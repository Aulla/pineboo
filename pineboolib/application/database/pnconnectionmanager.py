"""PNConnection_manager module."""
from PyQt6 import QtCore, QtWidgets  # type: ignore[import]

from pineboolib.core.utils import logging, utils_base

from pineboolib.core import garbage_collector, decorators
from pineboolib import application
from pineboolib.interfaces import iconnection
from . import pnconnection
from . import pnsqlcursor
from . import pnsqldriversmanager

from sqlalchemy import exc
import threading

from typing import Dict, Union, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.fllegacy import flmanager  # pragma: no cover
    from pineboolib.fllegacy import flmanagermodules  # pragma: no cover
    from pineboolib.interfaces import isession  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class PNConnectionManager(QtCore.QObject):
    """PNConnectionManager Class."""

    _drivers_sql_manager: "pnsqldriversmanager.PNSqlDriversManager"
    _manager: Optional["flmanager.FLManager"]
    _manager_modules: Optional["flmanagermodules.FLManagerModules"]
    connections_dict: Dict[str, "pnconnection.PNConnection"] = {}
    limit_connections: int = 0  # Limit of connections to use.
    connections_time_out: int = 0  # Seconds to wait to eliminate the inactive connections.

    REMOVE_CONNECTIONS_AFTER_ATOMIC: bool = False
    SAFE_TIME_SLEEP: float
    safe_mode_level: int

    def __init__(self):
        """Initialize."""

        super().__init__()
        self.connections_dict = {}
        self._manager = None
        self._manager_modules = None
        self.REMOVE_CONNECTIONS_AFTER_ATOMIC = False  # pylint: disable=invalid-name
        self.SAFE_TIME_SLEEP = 0.01  # pylint: disable=invalid-name
        self.safe_mode_level = 0
        self._drivers_sql_manager = pnsqldriversmanager.PNSqlDriversManager()

        LOGGER.debug("Initializing PNConnection Manager:")
        LOGGER.debug(
            "Limit : %s, Time out: %s. (0 disabled)",
            self.limit_connections,
            self.connections_time_out,
        )

    def setMainConn(self, main_conn: "pnconnection.PNConnection") -> bool:
        """Set main connection."""
        if "main_conn" in self.connections_dict:
            if main_conn.conn is not self.connections_dict["main_conn"].conn:
                self.connections_dict["main_conn"].close()
                del self.connections_dict["main_conn"]

        pnsqlcursor.CONNECTION_CURSORS.clear()

        main_conn._name = "main_conn"
        if self._drivers_sql_manager.loadDriver(main_conn._driver_name):
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

        if "main_conn" in self.connections_dict.keys():
            return self.connections_dict["main_conn"]
        else:
            raise Exception("main_conn is empty!")

    def remove_session(self, session: "isession.PinebooSession") -> bool:
        """Remove session."""

        try:
            session.close()
            obj_ = session
            del session
            garbage_collector.check_delete(obj_, str(obj_))
        except Exception as error:
            LOGGER.warning("Error removing session:%s", error)
            return False

        return True

    def finish(self) -> None:
        """Set the connection as terminated."""

        for key in list(self.connections_dict.keys()):
            if self.connections_dict[key] is None:
                continue

            self.connections_dict[key].close()
            del self.connections_dict[key]

        self.connections_dict.clear()
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

        name: str = (
            name_or_conn.connectionName()
            if isinstance(name_or_conn, iconnection.IConnection)
            else name_or_conn
        )

        name_conn_: str = utils_base.session_id(name)
        self.check_alive_connections()

        if name_conn_ in self.connections_dict.keys() and not db_name:
            return self.connections_dict[name_conn_]
        else:
            main_conn = self.mainConn()
            if main_conn is None:
                raise Exception("main_conn is empty!!")

            if name == "main_conn":
                return main_conn
            else:

                if db_name:
                    if not self.removeConn(name):
                        raise Exception("a problem existes deleting older connection")

                new_conn: "pnconnection.PNConnection" = pnconnection.PNConnection(
                    db_name or main_conn._db_name
                )
                new_conn._name = name

                if name.lower() in ["default", "dbaux", "aux"]:  # Las abrimos automáticamene!
                    if self._drivers_sql_manager.loadDriver(new_conn._driver_name):
                        new_conn.conn = new_conn.conectar(
                            new_conn._db_name,
                            new_conn._db_host,
                            new_conn._db_port,
                            new_conn._db_user_name,
                            new_conn._db_password,
                        )
                        new_conn._is_open = True

                self.connections_dict[name_conn_] = new_conn

                return new_conn

    def enumerate(self) -> Dict[str, "pnconnection.PNConnection"]:
        """Return dict with own database connections."""

        dict_ = {}
        id_thread = threading.current_thread().ident
        for key, value in self.connections_dict.items():
            connection_data = key.split("|")
            if connection_data[0] == str(id_thread):
                dict_[connection_data[1]] = value

        return dict_

    def removeConn(self, name="default") -> bool:
        """Delete a connection specified by name."""

        name_conn_: str = utils_base.session_id(name) if name.find("|") == -1 else name

        result = True

        if name_conn_ in self.connections_dict.keys():

            self.connections_dict[name_conn_]._is_open = False

            if self.connections_dict[name_conn_].conn not in [None, self.mainConn().conn]:
                try:
                    if application.SHOW_CONNECTION_EVENTS:
                        LOGGER.info("Closing connection %s", name_conn_)
                    self.connections_dict[name_conn_].close()
                    self.connections_dict[
                        name_conn_
                    ].driver().db_ = None  # type: ignore [assignment]
                    self.connections_dict[name_conn_]._driver = None

                    obj_ = self.connections_dict[name_conn_]
                    garbage_collector.check_delete(obj_, name_conn_)

                except Exception:
                    LOGGER.warning("Connection %s failed when close", name_conn_.split("|")[1])
                    result = False

            self.connections_dict[name_conn_] = None  # type: ignore [assignment] # noqa: F821
            del self.connections_dict[name_conn_]

        return result

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

    def test_session(
        self, conn_or_session: Union["iconnection.IConnection", "isession.PinebooSession"]
    ) -> bool:
        """Test a specific connection."""

        result = True
        session: "isession.PinebooSession" = (
            conn_or_session.session(False)  # type: ignore [assignment]
            if isinstance(conn_or_session, pnconnection.PNConnection)
            else conn_or_session
        )
        try:
            session.execute("SELECT 1").fetchone()
            result = hasattr(session, "commit")
        except Exception as error:
            session_name = session._conn_name  # type: ignore [attr-defined] # noqa: F821
            LOGGER.info("Connection %s is bad. error: %s", session_name, str(error))
            result = False

        return result

    def check_connections(self) -> bool:
        """Check connections."""
        self.default()
        self.dbAux()
        for conn_name in list(self.enumerate().keys()):  # Comprobamos conexiones una a una
            conn_identifier = utils_base.session_id(conn_name)
            if conn_identifier in self.connections_dict.keys():
                conn_ = self.connections_dict[conn_identifier]
                LOGGER.debug("Checking connection %s", conn_identifier)
                valid = True
                if not conn_.isOpen():
                    LOGGER.debug("Connection %s is closed.", conn_identifier)
                    valid = False
                else:
                    if not self.test_session(conn_):
                        valid = False

                if not valid:
                    if not self.removeConn(conn_identifier):
                        LOGGER.debug("Connection %s removing failed!", conn_identifier)
                        return False

        return True

    def reinit_user_connections(self) -> None:
        """Reinit users connection."""

        for conn_name in self.enumerate().keys():
            if self.removeConn(conn_name):
                self.useConn(conn_name)

    def check_alive_connections(self):
        """Check alive connections."""

        alived_threads: List[str] = [str(thread.ident) for thread in threading.enumerate()]

        for conn_ident in list(self.connections_dict.keys()):
            if conn_ident.find("|") > -1:
                thread_id = conn_ident.split("|")[0]
                if (
                    thread_id not in alived_threads  # si no es un hilo existente
                    or not self.connections_dict[conn_ident]._is_open  # si esta cerrada
                    and self.connections_dict[conn_ident].conn is not None  # si no esta incializada
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

    def is_valid_session(
        self,
        session_or_id: Optional[Union[str, "isession.PinebooSession"]],
        raise_error: bool = True,
    ) -> bool:
        """Return if a session id is valid."""
        is_valid = False
        if application.AUTO_RELOAD_BAD_CONNECTIONS:
            raise_error = False

        session = None

        if session_or_id is not None:
            session = (
                self.useConn(session_or_id).session()
                if isinstance(session_or_id, str)
                else session_or_id
            )

        if session is not None:
            try:
                try:
                    if not session.connection().closed:
                        is_valid = True
                except exc.InvalidRequestError:
                    if session.transaction is None:
                        is_valid = True
                except AttributeError:
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

    def pool_status(self, conn_name: str = "main_conn") -> str:
        """Return pool status used for the conn_name."""

        return self.useConn(conn_name).driver()._engine.pool.status()

    @decorators.deprecated
    def set_safe_mode(self, level: int) -> None:
        """
        Set safe mode level.

        > 0 ) Engine events activated.
        1) Increase time before SERIALIZED calls.
        2) Increase time after SERIALIZED calls.
        3) 1 + 2.
        4) Pool pre pings activated.
        5) 1 + 2 + 4.
        """

        """         self.safe_mode_level = level
        LOGGER.info("CONNECTION MANAGER: Safe mode level set to %s", level)

        if level > 0:
            application.SHOW_CONNECTION_EVENTS = True
            LOGGER.info("CONNECTION MANAGER (%s): Engine events activated.", level)
            LOGGER.info(
                "CONNECTION MANAGER (%s): Pool status when new connection activated.", level
            )

        if level in [1, 3, 5]:
            LOGGER.info(
                "CONNECTION MANAGER (%s): Time before SERIALIZED calls increase %s sec.",
                level,
                self.SAFE_TIME_SLEEP,
            )
        if level in [2, 3, 5]:
            LOGGER.info(
                "CONNECTION MANAGER (%s): Time after SERIALIZED calls increase %s sec.",
                level,
                self.SAFE_TIME_SLEEP,
            )
        if level in [4, 5]:
            LOGGER.info("CONNECTION MANAGER (%s): Pre ping activated.", level) """

    def __getattr__(self, name):
        """Return attributer from main_conn pnconnection."""

        if "main_conn" in self.connections_dict.keys():
            return getattr(self.mainConn(), name, None)

        return None

    database = useConn
