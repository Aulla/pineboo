"""PNConnection_manager module."""
from PyQt5 import QtCore, QtWidgets

from pineboolib.core.utils import logging, utils_base
from pineboolib import application
from pineboolib.interfaces import iconnection
from . import pnconnection
from . import pnsqlcursor

import threading

from typing import Dict, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.fllegacy import flmanager
    from pineboolib.fllegacy import flmanagermodules
    from sqlalchemy import orm as orm_session  # noqa: F401

LOGGER = logging.get_logger(__name__)


class PNConnectionManager(QtCore.QObject):
    """PNConnectionManager Class."""

    _manager: "flmanager.FLManager"
    _manager_modules: "flmanagermodules.FLManagerModules"
    connections_dict: Dict[str, "pnconnection.PNConnection"] = {}
    limit_connections: int = 50  # Limit of connections to use.
    connections_time_out: int = 0  # Seconds to wait to eliminate the inactive connections.

    current_atomic_sessions: Dict[str, str]
    current_thread_sessions: Dict[str, str]
    current_conn_sessions: Dict[str, str]
    _thread_sessions: Dict[str, "orm_session.Session"]

    def __init__(self):
        """Initialize."""

        super().__init__()
        self.connections_dict = {}
        self.current_atomic_sessions = {}
        self.current_thread_sessions = {}
        self.current_conn_sessions = {}
        self._thread_sessions = {}

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

        name_conn_: str = "%s|%s" % (application.PROJECT.session_id(), name)
        # if name in ("default", None):
        #    return self
        self.check_alive_connections()

        if name_conn_ in self.connections_dict.keys() and not db_name:
            connection_ = self.connections_dict[name_conn_]
        else:
            if db_name:
                if not self.removeConn(name):
                    raise Exception("a problem existes deleting older connection")

            if len(self.connections_dict.keys()) > self.limit_connections:
                raise Exception("Connections limit reached!")
            # if self._driver_sql is None:
            #    raise Exception("No driver selected")

            main_conn = self.mainConn()
            if main_conn is None:
                raise Exception("main_conn is empty!!")
            connection_ = pnconnection.PNConnection(main_conn._db_name if not db_name else db_name)
            connection_._name = name

            if name in ["default", "dbAux", "Aux"]:  # Las abrimos automáticamene!
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

    def dictDatabases(self) -> Dict[str, "pnconnection.PNConnection"]:
        """Return dict with own database connections."""

        dict_ = {}
        session_name = application.PROJECT.session_id()
        for key in self.connections_dict.keys():
            if key.find("|") > -1:
                connection_data = key.split("|")
                if connection_data[0] == session_name:
                    dict_[connection_data[1]] = self.connections_dict[key]

        return dict_

    def removeConn(self, name="default") -> bool:
        """Delete a connection specified by name."""
        name_conn_: str = name
        if name.find("|") == -1:
            name_conn_ = "%s|%s" % (application.PROJECT.session_id(), name)

        if name_conn_ in self.connections_dict.keys():

            self.connections_dict[name_conn_]._is_open = False
            if self.connections_dict[name_conn_].conn not in [None, self.mainConn().conn]:
                self.connections_dict[name_conn_].close()

            self.connections_dict[name_conn_] = None  # type: ignore [assignment] # noqa: F821
            del self.connections_dict[name_conn_]

        return True

    def manager(self) -> "flmanager.FLManager":
        """
        Flmanager instance that manages the connection.

        Flmanager manages metadata of fields, tables, queries, etc .. to then be managed this data by the controls of the application.
        """

        if not getattr(self, "_manager", None):
            # FIXME: Should not load from FL*
            from pineboolib.fllegacy import flmanager

            self._manager = flmanager.FLManager(self.mainConn())

        return self._manager

    def managerModules(self) -> "flmanagermodules.FLManagerModules":
        """
        Instance of the FLManagerModules class.

        Contains functions to control the state, health, etc ... of the database tables.
        """

        if not getattr(self, "_manager_modules", None):
            from pineboolib.fllegacy.flmanagermodules import FLManagerModules

            # FIXME: Should not load from FL*
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

    def reinit_user_connections(self) -> None:
        """Reinit users connection."""

        connections = self.dictDatabases()
        for conn_name in connections.keys():
            LOGGER.warning("Reinit connection %s forced!", conn_name)
            self.removeConn(conn_name)
            self.useConn(conn_name)

    def check_alive_connections(self):
        """Check alive connections."""

        for conn_name in list(self.connections_dict.keys()):
            if conn_name.find("|") > -1:
                if (
                    not self.connections_dict[conn_name]._is_open  # Closed connections
                    and self.connections_dict[conn_name].conn
                    is not None  # Only initialized connections.
                ) or (
                    self.connections_time_out
                    and self.connections_dict[conn_name].idle_time() > self.connections_time_out
                ):
                    self.removeConn(conn_name)

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

    def status(self, all_users: bool = False) -> str:
        """Return connections status."""

        conns = []
        user_id = self.session_id()
        for conn_name in list(self.connections_dict.keys()):
            # print("*", conn_name)
            if conn_name.find("|") > -1:
                if not all_users:
                    if user_id == conn_name.split("|")[0]:
                        conns.append(conn_name)
                else:
                    conns.append(conn_name)
            else:
                conns.append(conn_name)

        result = "CONNECTIONS (%s):" % ("All users" if all_users else "User: %s" % user_id)
        for conn_name in conns:
            conn_ = ""
            if conn_name.find("|") > -1:
                conn_ = conn_name.split("|")[1]
                result += "\n    - User: %s, Connection name: %s:" % (
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
                    valid_session = self.mainConn().driver().is_valid_session(key, False)
                    session_result += "* id: %s,  thread_id: %s" % (key, key.split("_")[0])
                    session_result += ", is_valid: %s" % ("True" if valid_session else "False")
                    if valid_session:
                        session_result += ", in_transaction: %s" % (
                            "False" if session.transaction is None else "True"
                        )

                    if session_id in self.current_atomic_sessions.keys():
                        # print("****", session_id)
                        if key == self.current_atomic_sessions[session_id]:
                            session_result += ", type: Atomic"
                    if session_id in self.current_conn_sessions.keys():
                        # print("***", session_id)
                        if key == self.current_conn_sessions[session_id]:
                            session_result += ", type: Legacy"
                    if session_id in self.current_thread_sessions.keys():
                        # print("*****", session_id)
                        if key == self.current_thread_sessions[session_id]:
                            session_result += ", type: Thread"

                if session_result:
                    result += "\n        " + session_result
                else:
                    # print("***", conn_, key)
                    continue

        return result

    def get_current_thread_sessions(self) -> List["orm_session.session.Session"]:
        """Return thread sessions openend."""

        id_thread = threading.current_thread().ident
        result: List["orm_session.session.Session"] = []
        conn_sessions = []
        for id_session in self.current_conn_sessions.keys():
            conn_sessions.append(id_session)

        for key in self._thread_sessions.keys():
            if str(id_thread) in key and key not in conn_sessions:  # todas menos las _conn_sessions
                result.append(self._thread_sessions[key])

        return result

    def __getattr__(self, name):
        """Return attributer from main_conn pnconnection."""

        if "main_conn" in self.connections_dict.keys():
            return getattr(self.mainConn(), name, None)

        return None

    database = useConn
