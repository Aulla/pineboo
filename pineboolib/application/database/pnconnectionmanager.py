"""PNConnection_manager module."""
from PyQt5 import QtCore, QtWidgets

from pineboolib.core.utils import logging, utils_base
from pineboolib import application
from pineboolib.interfaces import iconnection
from . import pnconnection
from . import pnsqlcursor

from sqlalchemy import exc
import threading

from typing import Dict, Union, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.fllegacy import flmanager  # pragma: no cover
    from pineboolib.fllegacy import flmanagermodules  # pragma: no cover
    from sqlalchemy import orm as orm_session  # noqa: F401 # pragma: no cover

LOGGER = logging.get_logger(__name__)


class PNConnectionManager(QtCore.QObject):
    """PNConnectionManager Class."""

    _manager: Optional["flmanager.FLManager"]
    _manager_modules: Optional["flmanagermodules.FLManagerModules"]
    connections_dict: Dict[str, "pnconnection.PNConnection"] = {}
    limit_connections: int = 50  # Limit of connections to use.
    connections_time_out: int = 0  # Seconds to wait to eliminate the inactive connections.

    current_atomic_sessions: Dict[str, str]
    current_thread_sessions: Dict[str, str]
    # current_conn_sessions: Dict[str, str]
    _thread_sessions: Dict[str, "orm_session.Session"]

    def __init__(self):
        """Initialize."""

        super().__init__()
        self.connections_dict = {}
        self.current_atomic_sessions = {}
        self.current_thread_sessions = {}
        # self.current_conn_sessions = {}
        self._thread_sessions = {}
        self._manager = None
        self._manager_modules = None

        LOGGER.info("Initializing PNConnection Manager:")
        LOGGER.info("LIMIT CONNECTIONS = %s.", self.limit_connections)
        LOGGER.info("CONNECTIONS TIME OUT = %s. (0 disabled)", self.connections_time_out)

    def setMainConn(self, main_conn: "pnconnection.PNConnection") -> bool:
        """Set main connection."""
        if "main_conn" in self.connections_dict:
            conn_ = self.connections_dict["main_conn"]
            if main_conn.conn is not conn_.conn:
                conn_.close()
                del conn_
                del self.connections_dict["main_conn"]

        del pnsqlcursor.CONNECTION_CURSORS
        pnsqlcursor.CONNECTION_CURSORS = {}

        main_conn._name = "main_conn"
        if main_conn._driver_name and main_conn._driver_sql.loadDriver(main_conn._driver_name):
            main_conn.conn = main_conn.conectar(
                main_conn._db_name,
                main_conn._db_host,
                main_conn._db_port,
                main_conn._db_user_name,
                main_conn._db_password,
            )
            if isinstance(main_conn.conn, bool):
                return False

            main_conn._is_open = True

        self.connections_dict["main_conn"] = main_conn
        return True

    def mainConn(self) -> "pnconnection.PNConnection":
        """Return main conn."""
        ret_: "pnconnection.PNConnection"

        if "main_conn" in self.connections_dict.keys():
            ret_ = self.connections_dict["main_conn"]
        else:
            raise Exception("main_conn is empty!")

        return ret_

    def finish(self) -> None:
        """Set the connection as terminated."""

        for key in list(self.connections_dict.keys()):
            if self.connections_dict[key] is None:
                continue

            # if "main_conn" in self.connections_dict.keys():
            #    if self.connections_dict["main_conn"].conn is conn_:
            #        continue
            self.connections_dict[key].close()
            del self.connections_dict[key]

        self.connections_dict = {}
        del self._manager
        del self._manager_modules
        del self

    def useConn(
        self, name_or_conn: Union[str, "iconnection.IConnection"] = "default", db_name: str = ""
    ) -> "iconnection.IConnection":
        """
        Select another connection which can be not the default one.

        Allow you to select a connection.
        """

        name: str
        if isinstance(name_or_conn, iconnection.IConnection):
            name = name_or_conn.connectionName()
        else:
            name = name_or_conn

        name_conn_: str = utils_base.session_id(name)
        # if name in ("default", None):
        #    return self
        self.check_alive_connections()

        if name_conn_ in self.connections_dict.keys() and not db_name:
            connection_ = self.connections_dict[name_conn_]
        else:
            if db_name:
                if not self.removeConn(name):
                    raise Exception("a problem existes deleting older connection")

            # if len(self.connections_dict.keys()) > self.limit_connections:
            #    raise Exception("Connections limit reached!")
            # if self._driver_sql is None:
            #    raise Exception("No driver selected")

            main_conn = self.mainConn()
            if main_conn is None:
                raise Exception("main_conn is empty!!")
            connection_ = pnconnection.PNConnection(main_conn._db_name if not db_name else db_name)
            connection_._name = name

            if name.lower() in ["default", "dbaux", "aux"]:  # Las abrimos automáticamene!
                if connection_._driver_name and connection_._driver_sql.loadDriver(
                    connection_._driver_name
                ):
                    connection_.conn = connection_.conectar(
                        connection_._db_name,
                        connection_._db_host,
                        connection_._db_port,
                        connection_._db_user_name,
                        connection_._db_password,
                        self.limit_connections,
                    )
                    connection_._is_open = True

            # if connection_.conn is None:
            # LOGGER.warning("Connection %s is closed!", name, stack_info=True)

            self.connections_dict[name_conn_] = connection_

        return connection_

    def enumerate(self) -> Dict[str, "pnconnection.PNConnection"]:
        """Return dict with own database connections."""

        dict_ = {}
        id_thread = threading.current_thread().ident
        for key in self.connections_dict.keys():
            if key.find("|") > -1:
                connection_data = key.split("|")
                if connection_data[0] == str(id_thread):
                    dict_[connection_data[1]] = self.connections_dict[key]

        return dict_

    def removeConn(self, name="default") -> bool:
        """Delete a connection specified by name."""
        name_conn_: str = name
        if name.find("|") == -1:
            name_conn_ = utils_base.session_id(name)

        result = True

        if name_conn_ in self.connections_dict.keys():

            self.connections_dict[name_conn_]._is_open = False
            if self.connections_dict[name_conn_].conn not in [None, self.mainConn().conn]:
                try:
                    self.connections_dict[name_conn_].close()
                except Exception:
                    LOGGER.warning("Connection %s failed when close", name_conn_.split("|")[1])
                    result = False

            if not result:
                self.delete_from_sessions_dict(name_conn_)

            self.connections_dict[name_conn_] = None  # type: ignore [assignment] # noqa: F821
            del self.connections_dict[name_conn_]

        return result

    def delete_from_sessions_dict(self, conn_name: str) -> None:
        """Search and delete sessions_identifiers from sessions dicts."""

        if conn_name in self.current_atomic_sessions.keys():
            del self.current_atomic_sessions[conn_name]

        if conn_name in self.current_thread_sessions.keys():
            del self.current_thread_sessions[conn_name]

        for thread_session_identifier in list(self._thread_sessions.keys()):
            if thread_session_identifier.startswith(conn_name):
                self.delete_session(thread_session_identifier)

    def delete_session(self, session_id: str) -> None:
        """Delete a session."""

        if session_id and session_id in self._thread_sessions:
            session = self._thread_sessions[session_id]
            try:
                session.close()
            except Exception:
                pass

            del self._thread_sessions[session_id]

    def manager(self) -> "flmanager.FLManager":
        """
        Flmanager instance that manages the connection.

        Flmanager manages metadata of fields, tables, queries, etc .. to then be managed this data by the controls of the application.
        """

        if self._manager is None:
            from pineboolib.fllegacy import flmanager

            self._manager = flmanager.FLManager(self.mainConn())

        return self._manager

    def managerModules(self) -> "flmanagermodules.FLManagerModules":
        """
        Instance of the FLManagerModules class.

        Contains functions to control the state, health, etc ... of the database tables.
        """

        if self._manager_modules is None:
            from pineboolib.fllegacy.flmanagermodules import FLManagerModules

            self._manager_modules = FLManagerModules(self.mainConn())

        return self._manager_modules

    def db(self) -> "iconnection.IConnection":
        """Return the connection itself."""

        return self.useConn("default")

    def dbAux(self) -> "iconnection.IConnection":
        """
        Return the auxiliary connection to the database.

        This connection is useful for out of transaction operations.
        """
        return self.useConn("dbAux")

    def default(self) -> "iconnection.IConnection":
        """
        Return the default connection to the database.
        """
        return self.useConn("default")

    def test_session(self, conn_or_session) -> bool:
        """Test a specific connection."""

        result = True
        if isinstance(conn_or_session, pnconnection.PNConnection):
            session = conn_or_session.session(False)
        else:
            session = conn_or_session

        try:
            session.execute("SELECT 1").fetchone()
        except Exception as error:
            session_name = session._conn_name  # type: ignore [attr-defined] # noqa: F821
            LOGGER.info("Connection %s is bad. error: %s", session_name, str(error))
            result = False

        return result

    def check_connections(self, serialize: bool = True) -> None:
        """Check connections."""

        for conn_name in list(self.enumerate().keys()):  # Comprobamos conexiones una a una
            conn_identifier = utils_base.session_id(conn_name)

            if serialize:
                if conn_identifier not in application.GET_LIST:
                    application.GET_LIST.append(conn_identifier)
                else:
                    while conn_identifier in application.GET_LIST:
                        QtWidgets.QApplication.processEvents()

            if conn_identifier not in application.GET_LIST:
                application.GET_LIST.append(conn_identifier)

            if conn_identifier in self.connections_dict.keys():
                conn_ = self.connections_dict[conn_identifier]
                LOGGER.info("Checking connection %s", conn_identifier)
                valid = True
                if not conn_.isOpen():
                    LOGGER.info("Connection %s is closed.", conn_identifier)
                    valid = False
                else:
                    if not self.test_session(conn_):
                        valid = False

                if not valid:
                    if not self.removeConn(conn_identifier):
                        LOGGER.info("Connection %s removing failed!", conn_identifier)
            if serialize:
                application.GET_LIST.remove(conn_identifier)

    def reinit_user_connections(self) -> None:
        """Reinit users connection."""

        connections = self.enumerate()
        for conn_name in connections.keys():
            if self.removeConn(conn_name):
                self.useConn(conn_name)

    def check_alive_connections(self):
        """Check alive connections."""

        alived_threads: List[str] = []

        for thread in threading.enumerate():
            alived_threads.append(str(thread.ident))

        for conn_ident in list(self.connections_dict.keys()):
            if conn_ident.find("|") > -1:
                thread_id = conn_ident.split("|")[0]
                if thread_id not in alived_threads:
                    self.removeConn(conn_ident)

        for conn_ident in list(self.enumerate().keys()):
            if conn_ident.find("|") > -1:
                if (
                    not self.connections_dict[conn_ident]._is_open  # Closed connections
                    and self.connections_dict[conn_ident].conn
                    is not None  # Only initialized connections.
                ) or (
                    self.connections_time_out
                    and self.connections_dict[conn_ident].idle_time() > self.connections_time_out
                ):
                    self.removeConn(conn_ident)

    def set_max_connections_limit(self, limit: int) -> None:
        """Set maximum connections limit."""
        LOGGER.info("New max connections limit %s.", limit)
        self.limit_connections = limit  # noqa: F841

    def set_max_idle_connections(self, limit: int) -> None:
        """Set maximum connections time idle."""
        LOGGER.info("New max connections idle time %s.", limit)
        self.connections_time_out = limit  # noqa: F841

    def active_pncursors(self, only_name: bool = False, all_sessions: bool = False) -> List[str]:
        """Return a user cursor opened list."""

        QtWidgets.QApplication.processEvents()

        identifier = self.session_id()

        result = []

        for key in pnsqlcursor.CONNECTION_CURSORS.keys():
            if key == identifier or all_sessions:
                for cursor_name in pnsqlcursor.CONNECTION_CURSORS[key]:
                    result.append(cursor_name.split("@")[0] if only_name else cursor_name)

        return result

    def session_id(self) -> str:
        """Return session identifier."""

        return application.PROJECT.session_id()

    def _get_session_id(self, conn_name: str) -> Optional[str]:
        """Return correct session."""

        session_key = utils_base.session_id(conn_name)
        use_key = None
        if session_key in self.current_atomic_sessions.keys():
            atomic_key = self.current_atomic_sessions[session_key]
            if atomic_key in self._thread_sessions.keys():
                use_key = atomic_key

        if not use_key:
            if session_key in self.current_thread_sessions.keys():
                use_key = self.current_thread_sessions[session_key]

        return use_key

    def status(self, all_threads: bool = False) -> str:
        """Return connections status."""

        conns = []
        id_thread = threading.current_thread().ident

        for conn_name in list(self.enumerate().keys()):
            if conn_name.find("|") > -1:
                if not all_threads:
                    if str(id_thread) != conn_name.split("|")[0]:
                        continue

            conns.append(conn_name)

        result = "CONNECTIONS (%s):" % ("All threads" if all_threads else "Thread: %s" % id_thread)
        for conn_name in conns:
            conn_ = ""
            if conn_name.find("|") > -1:
                conn_ = conn_name.split("|")[1]
                result += "\n    - Thread: %s, Connection name: %s:" % (
                    conn_name.split("|")[0],
                    conn_,
                )

            else:
                conn_ = conn_name
                result += "\n    - Main connection: %s:" % conn_

            for key, session in self._thread_sessions.items():
                session_id = utils_base.session_id(conn_)

                session_result = ""
                if conn_ in key:
                    valid_session = self.is_valid_session(key, False)
                    session_result += "* id: %s,  thread_id: %s" % (key, key.split("|")[0])
                    session_result += ", is_valid: %s" % ("True" if valid_session else "False")
                    if valid_session:
                        session_result += ", in_transaction: %s" % (
                            "False" if session.transaction is None else "True"
                        )

                    if session_id in self.current_atomic_sessions.keys():
                        if key == self.current_atomic_sessions[session_id]:
                            session_result += ", type: Atomic"
                    if session_id in self.current_thread_sessions.keys():
                        if key == self.current_thread_sessions[session_id]:
                            session_result += ", type: Thread"

                if session_result:
                    result += "\n        " + session_result
                else:
                    continue

        return result

    def get_current_thread_sessions(self) -> List["orm_session.session.Session"]:
        """Return thread sessions openend."""

        id_thread = threading.current_thread().ident
        result: List["orm_session.session.Session"] = []
        # conn_sessions = []
        # for id_session in self.current_conn_sessions.keys():
        #    conn_sessions.append(id_session)

        for key in self._thread_sessions.keys():
            if str(id_thread) in key and key:  # todas menos las _conn_sessions
                result.append(self._thread_sessions[key])

        return result

    def is_valid_session(
        self, session_or_id: Union[str, "orm_session.Session"], raise_error: bool = True
    ) -> bool:
        """Return if a session id is valid."""
        is_valid = False
        if application.AUTO_RELOAD_BAD_CONNECTIONS:
            raise_error = False

        session = None

        if session_or_id is not None:
            if not isinstance(session_or_id, str):
                session = session_or_id
            elif session_or_id in self._thread_sessions:
                session = self._thread_sessions[session_or_id]

        if session is not None:
            try:
                try:
                    if not session.connection().closed:
                        is_valid = True
                except exc.InvalidRequestError:
                    if session.transaction is None:
                        is_valid = True

            except Exception as error:
                if raise_error:
                    LOGGER.warning(
                        "AttributeError:: Quite possibly, you are trying to use a session in which"
                        " a previous error has occurred and has not"
                        " been recovered with a rollback. Current session is discarded."
                    )
                    raise error

            if application.AUTO_RELOAD_BAD_CONNECTIONS:
                need_reload = False
                if is_valid:
                    if not self.test_session(session):
                        need_reload = True
                        is_valid = False

                if need_reload:
                    LOGGER.warning(
                        "AUTO RELOAD: bad connection detected. Reloading users connections"
                    )
                    if session.transaction is not None:
                        LOGGER.warning(
                            "AUTO RELOAD: bad session %s is currently in transacction. Aborted",
                            session.transaction,
                        )

                    self.reinit_user_connections()

        return is_valid

    def __getattr__(self, name):
        """Return attributer from main_conn pnconnection."""

        if "main_conn" in self.connections_dict.keys():
            return getattr(self.mainConn(), name, None)

        return None

    database = useConn
