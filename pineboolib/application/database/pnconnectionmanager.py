"""PNConnection_manager module."""
from PyQt5 import QtCore

from pineboolib.core.utils import logging
from pineboolib import application
from pineboolib.interfaces import iconnection
from . import pnconnection

from typing import Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.fllegacy import flmanager
    from pineboolib.fllegacy import flmanagermodules

LOGGER = logging.getLogger(__name__)

LIMIT_CONNECTIONS: int = 10  # Limit of connections to use.
CONNECTIONS_TIME_OUT: int = 0  # Seconds to wait to eliminate the inactive connections.


class PNConnectionManager(QtCore.QObject):
    """PNConnectionManager Class."""

    _manager: "flmanager.FLManager"
    _manager_modules: "flmanagermodules.FLManagerModules"
    connections_dict: Dict[str, "pnconnection.PNConnection"] = {}

    def __init__(self):
        """Initialize."""

        super().__init__()
        self.connections_dict = {}

        LOGGER.info("Initializing PNConnection Manager:")
        LOGGER.info("LIMIT CONNECTIONS = %s.", LIMIT_CONNECTIONS)
        LOGGER.info("CONNECTIONS TIME OUT = %s. (0 disabled)", CONNECTIONS_TIME_OUT)

    def setMainConn(self, main_conn: "pnconnection.PNConnection") -> bool:
        """Set main connection."""
        if "main_conn" in self.connections_dict:
            conn_ = self.connections_dict["main_conn"]
            if main_conn.conn is not conn_.conn:
                conn_.conn.close()
                del conn_
                del self.connections_dict["main_conn"]

        if main_conn._driver_name and main_conn._driver_sql.loadDriver(main_conn._driver_name):
            main_conn.conn = main_conn.conectar(
                main_conn._db_name,
                main_conn._db_host,
                main_conn._db_port,
                main_conn._db_user_name,
                main_conn._db_password,
            )
            main_conn._is_open = True

        main_conn._name = "main_conn"
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
            conn_ = self.connections_dict[key].conn
            if conn_ is None:
                continue

            # if "main_conn" in self.connections_dict.keys():
            #    if self.connections_dict["main_conn"].conn is conn_:
            #        continue
            self.connections_dict[key]._is_open = False
            conn_.close()
            del self.connections_dict[key]

        self.connections_dict = {}
        del self._manager
        del self._manager_modules
        del self

    def useConn(
        self, name_or_conn: Union[str, "iconnection.IConnection"] = "default"
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

        if name_conn_ in self.connections_dict.keys():
            connection_ = self.connections_dict[name_conn_]
        else:
            if len(self.connections_dict.keys()) > LIMIT_CONNECTIONS:
                raise Exception("Connections limit reached!")
            # if self._driver_sql is None:
            #    raise Exception("No driver selected")

            main_conn = self.mainConn()
            if main_conn is None:
                raise Exception("main_conn is empty!!")
            connection_ = pnconnection.PNConnection(main_conn._db_name)
            connection_._name = name

            if name in ["default", "dbAux"]:  # Las abrimos automáticamene!
                if connection_._driver_name and connection_._driver_sql.loadDriver(
                    connection_._driver_name
                ):
                    connection_.conn = connection_.conectar(
                        connection_._db_name,
                        connection_._db_host,
                        connection_._db_port,
                        connection_._db_user_name,
                        connection_._db_password,
                    )
                    connection_._is_open = True

            if connection_.conn is None:
                LOGGER.warning("Connection %s is closed!", name)

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
            conn_ = self.connections_dict[name_conn_].conn
            if conn_ not in [None, self.mainConn().conn]:
                conn_.close()

            del self.connections_dict[name_conn_]
            return True
        else:
            LOGGER.warning("An attempt was made to delete an invalid connection named %s" % name)
            return False

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

    def check_alive_connections(self):
        """Check alive connections."""

        for conn_name in list(self.connections_dict.keys()):
            if conn_name.find("|") > -1:
                if (
                    not self.connections_dict[conn_name]._is_open  # Closed connections
                    and self.connections_dict[conn_name].conn
                    is not None  # Only initialized connections.
                ) or (
                    CONNECTIONS_TIME_OUT
                    and self.connections_dict[conn_name].idle_time() > CONNECTIONS_TIME_OUT
                ):
                    self.removeConn(conn_name)

    def set_max_connections_limit(self, limit: int) -> None:
        """Set maximum connections limit."""
        LOGGER.info("New max connections limit %s.", limit)
        LIMIT_CONNECTIONS = limit  # noqa: F841

    def set_max_idle_connections(self, limit: int) -> None:
        """Set maximum connections time idle."""
        LOGGER.info("New max connections idle time %s.", limit)
        CONNECTIONS_TIME_OUT = limit  # noqa: F841

    def __getattr__(self, name):
        """Return attributer from main_conn pnconnection."""

        if "main_conn" in self.connections_dict.keys():
            return getattr(self.mainConn(), name, None)

        return None

    database = useConn
