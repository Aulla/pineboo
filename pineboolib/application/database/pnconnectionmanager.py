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

logger = logging.getLogger(__name__)

LIMIT_CONNECTIONS = 10  # Limit of connections to use.
CONNECTIONS_TIME_OUT = 0  # Seconds to wait to eliminate the inactive connections.


class PNConnectionManager(QtCore.QObject):
    """PNConnectionManager Class."""

    _manager: "flmanager.FLManager"
    _manager_modules: "flmanagermodules.FLManagerModules"
    conn_dict: Dict[str, "pnconnection.PNConnection"] = {}

    def __init__(self):
        """Initialize."""

        super().__init__()
        self.conn_dict = {}

        logger.info("Initializing PNConnection Manager:")
        logger.info("LIMIT CONNECTIONS = %s.", LIMIT_CONNECTIONS)
        logger.info("CONNECTIONS TIME OUT = %s. (0 disabled)", CONNECTIONS_TIME_OUT)

    # def __init__(
    #    self,
    #    db_name: str,
    #    db_host: Optional[str],
    #    db_port: Optional[int],
    #    db_user_name: Optional[str],
    #    db_password: Optional[str],
    #    driver_alias: str,
    # ):
    #    """Initialize."""

    #    super().__init__()
    #    self.conn_dict["main_conn"] = pnconnection.PNConnection(self, db_name, db_host, db_port, db_user_name, db_password, driver_alias)

    def setMainConn(self, main_conn: "pnconnection.PNConnection") -> bool:
        """Set main connection."""
        if "main_conn" in self.conn_dict:
            conn_ = self.conn_dict["main_conn"]
            if main_conn.conn is not conn_.conn:
                conn_.conn.close()
                del conn_
                del self.conn_dict["main_conn"]

        if main_conn.driver_name_ and main_conn.driverSql.loadDriver(main_conn.driver_name_):
            main_conn.conn = main_conn.conectar(
                main_conn.db_name_,
                main_conn.db_host_,
                main_conn.db_port_,
                main_conn.db_user_name_,
                main_conn.db_password_,
            )
            main_conn._isOpen = True

        main_conn.name = "main_conn"
        self.conn_dict["main_conn"] = main_conn
        return True

    def mainConn(self) -> "pnconnection.PNConnection":
        """Return main conn."""
        ret_: "pnconnection.PNConnection"

        if "main_conn" in self.conn_dict.keys():
            ret_ = self.conn_dict["main_conn"]
        else:
            raise Exception("main_conn is empty!")

        return ret_

    def finish(self) -> None:
        """Set the connection as terminated."""

        for n in list(self.conn_dict.keys()):
            conn_ = self.conn_dict[n].conn
            if conn_ is None:
                continue

            # if "main_conn" in self.conn_dict.keys():
            #    if self.conn_dict["main_conn"].conn is conn_:
            #        continue
            self.conn_dict[n]._isOpen = False
            conn_.close()
            del self.conn_dict[n]

        self.conn_dict = {}
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

        name_conn_: str = "%s|%s" % (application.project.session_id(), name)
        # if name in ("default", None):
        #    return self
        self.check_alive_connections()

        if name_conn_ in self.conn_dict.keys():
            connection_ = self.conn_dict[name_conn_]
        else:
            if len(self.conn_dict.keys()) > LIMIT_CONNECTIONS:
                raise Exception("Connections limit reached!")
            # if self.driverSql is None:
            #    raise Exception("No driver selected")

            main_conn = self.mainConn()
            if main_conn is None:
                raise Exception("main_conn is empty!!")
            connection_ = pnconnection.PNConnection(main_conn.db_name_)
            connection_.name = name

            if name in ["default", "dbAux"]:  # Las abrimos automáticamene!
                if connection_.driver_name_ and connection_.driverSql.loadDriver(
                    connection_.driver_name_
                ):
                    connection_.conn = connection_.conectar(
                        connection_.db_name_,
                        connection_.db_host_,
                        connection_.db_port_,
                        connection_.db_user_name_,
                        connection_.db_password_,
                    )
                    connection_._isOpen = True

            if connection_.conn is None:
                logger.warning("Connection %s is closed!", name)

            self.conn_dict[name_conn_] = connection_

        return connection_

    def dictDatabases(self) -> Dict[str, "pnconnection.PNConnection"]:
        """Return dict with own database connections."""

        dict_ = {}
        session_name = application.project.session_id()
        for n in self.conn_dict.keys():
            if n.find("|") > -1:
                connection_data = n.split("|")
                if connection_data[0] == session_name:
                    dict_[connection_data[1]] = self.conn_dict[n]

            # if session_name:
            #    if n.startswith(session_name):
            #        dict_[n.replace("%s|" % session_name, "")] = self.conn_dict[n]
            # else:
            #    if n[0] == "|":
            #        dict_[n[1:]] = self.conn_dict[n]
            #    else:
            #        dict_[n] = self.conn_dict[n]

        return dict_

    def removeConn(self, name="default") -> bool:
        """Delete a connection specified by name."""
        name_conn_ = name
        if name.find("|") == -1:
            name_conn_: str = "%s|%s" % (application.project.session_id(), name)

        self.conn_dict[name_conn_]._isOpen = False
        conn_ = self.conn_dict[name_conn_].conn
        if conn_ not in [None, self.mainConn().conn]:
            conn_.close()

        del self.conn_dict[name_conn_]
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

    def check_alive_connections(self):
        """Check alive connections."""

        for conn_name in list(self.conn_dict.keys()):
            if conn_name.find("|") > -1:
                connection_data = conn_name.split("|")
                if (
                    not self.conn_dict[conn_name]._isOpen  # Closed connections
                    and self.conn_dict[conn_name].conn is not None  # Only initialized connections.
                ) or (
                    CONNECTIONS_TIME_OUT
                    and self.conn_dict[conn_name].idle_time() > CONNECTIONS_TIME_OUT
                ):
                    self.removeConn(conn_name)

    def set_max_connections_limit(self, n: int) -> None:
        """Set maximum connections limit."""
        logger.info("New max connections limit %s.", n)
        LIMIT_CONNECTIONS = n  # noqa: F841

    def set_max_idle_connections(self, s: int) -> None:
        """Set maximum connections time idle."""
        logger.info("New max connections idle time %s.", s)
        CONNECTIONS_TIME_OUT = s  # noqa: F841

    def __getattr__(self, name):
        """Return attributer from main_conn pnconnection."""
        return getattr(self.mainConn(), name, None)

    database = useConn
