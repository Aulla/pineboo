# -*- coding: utf-8 -*-
"""
Defines the IConnection class.
"""

from pineboolib.core.utils import logging


from typing import Any, List, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:

    from pineboolib.fllegacy import flmanager  # pragma: no cover
    from pineboolib.fllegacy import flmanagermodules  # pragma: no cover
    from pineboolib.application.metadata import pntablemetadata  # pragma: no cover
    from pineboolib.application.database import (
        pnsqldriversmanager,
        pnconnectionmanager,
    )  # pragma: no cover
    from pineboolib.interfaces import isession, isqldriver, isqlcursor  # pragma: no cover
    from sqlalchemy.engine import base, result

LOGGER = logging.get_logger(__name__)


class IConnection:
    """Interface for database cursors which are used to emulate FLSqlCursor."""

    _db_name: str
    _db_host: str
    _db_port: int
    _db_user_name: str
    _db_password: str = ""
    conn: Optional[Union["base.Connection", bool]]
    _interactive_gui: str
    _drivers_sql_manager: "pnsqldriversmanager.PNSqlDriversManager"
    _driver_name: str
    _name: str
    _is_open: bool
    _last_error: str
    _transaction_level: int
    _conn_manager: "pnconnectionmanager.PNConnectionManager"
    _driver: Optional["isqldriver.ISqlDriver"]
    _last_active_cursor: Optional["isqlcursor.ISqlCursor"]
    _session_legacy: Optional["isession.PinebooSession"]
    _session_atomic: Optional["isession.PinebooSession"]

    def connectionName(self) -> str:
        """Get the current connection name for this cursor."""
        return ""  # pragma: no cover

    def isOpen(self) -> bool:
        """Indicate if a connection is open."""
        return False  # pragma: no cover

    def tables(self, tables: Union[str, int] = "") -> List[str]:
        """Return a list of available tables in the database, according to a given filter."""
        return []  # pragma: no cover

    def DBName(self) -> str:
        """Return the database name."""
        return ""  # pragma: no cover

    def driver(self) -> "isqldriver.ISqlDriver":
        """Return the instance of the driver that is using the connection."""

        return None  # type: ignore [return-value] # pragma: no cover

    def database(self) -> "IConnection":
        """Return self."""

        return self  # pragma: no cover

    def session(self) -> "isession.PinebooSession":
        """
        Sqlalchemy session.

        When using the ORM option this function returns the session for sqlAlchemy.
        """

        return None  # type: ignore[return-value] # noqa: F821 # pragma: no cover

    def connManager(self) -> "pnconnectionmanager.PNConnectionManager":
        """Return connection manager."""

        return None  # type: ignore[return-value] # noqa: F821 # pragma: no cover

    def engine(self) -> "base.Engine":
        """Sqlalchemy connection."""

        return None  # type: ignore[return-value] # noqa: F821 # pragma: no cover

    def dictDatabases(self) -> Dict[str, "IConnection"]:
        """Return dict with own database connections."""

        return {}  # pragma: no cover

    # def cursor(self) -> IApiCursor:
    #    """Return a cursor to the database."""

    #    return IApiCursor()

    def connection(self) -> "base.Connection":
        """Return base connection."""

        pass  # pragma: no cover

    def lastActiveCursor(self) -> Optional["isqlcursor.ISqlCursor"]:  # returns FLSqlCuror
        """Return the last active cursor in the sql driver."""

        return None  # pragma: no cover

    def conectar(
        self, db_name, db_host, db_port, db_user_name, db_returnword
    ) -> Union["base.Connection", bool]:
        """Request a connection to the database."""

        return False  # pragma: no cover

    def driverName(self) -> str:
        """Return sql driver name."""

        return ""  # pragma: no cover

    def driverAlias(self) -> str:
        """Return sql driver alias."""

        return ""  # pragma: no cover

    def driverNameToDriverAlias(self, name) -> str:
        """Return the alias from the name of a sql driver."""

        return ""  # pragma: no cover

    def lastError(self) -> str:
        """Return the last error reported by the sql driver."""

        return ""  # pragma: no cover

    def host(self) -> str:
        """Return the name of the database host."""

        return ""  # pragma: no cover

    def port(self) -> int:
        """Return the port used by the database."""

        return 0  # pragma: no cover

    def user(self) -> str:
        """Return the user name used by the database."""

        return ""  # pragma: no cover

    def returnword(self) -> str:
        """Return ****word used by the database."""
        return ""  # pragma: no cover

    def md5TuplesStateTable(self, curname: str) -> bool:
        """
        Return the sum md5 with the total records inserted, deleted and modified in the database so far.

        Useful to know if the database has been modified from a given moment.
        """

        return True  # pragma: no cover

    def setInteractiveGUI(self, data) -> None:
        """Set if it is an interactive GUI."""

        return  # pragma: no cover

    def setQsaExceptions(self, data) -> None:
        """See properties of the qsa exceptions."""

        return  # pragma: no cover

    def formatValue(self, type_, value, upper) -> str:
        """Return a correctly formatted value to be assigned as a where filter."""

        return ""  # pragma: no cover

    def formatValueLike(self, type_, value, upper) -> str:
        """Return a correctly formatted value to be assigned as a WHERE LIKE filter."""

        return ""  # pragma: no cover

    def doTransaction(self, cursor) -> bool:
        """Make a transaction or savePoint according to transaction level."""

        return False  # pragma: no cover

    def transactionLevel(self) -> int:
        """Indicate the level of transaction."""

        return 0  # pragma: no cover

    def doRollback(self, cur) -> bool:
        """Drop a transaction or savepoint depending on the transaction level."""

        return False  # pragma: no cover

    def interactiveGUI(self) -> str:
        """Return if it is an interactive GUI."""

        return ""  # pragma: no cover

    def doCommit(self, cur, notify=True) -> bool:
        """Approve changes to a transaction or a save point based on your transaction level."""

        return False  # pragma: no cover

    def canDetectLocks(self) -> bool:
        """Indicate if the connection detects locks in the database."""

        return False  # pragma: no cover

    def commit(self) -> bool:
        """Send the commit order to the database."""

        return True  # pragma: no cover

    def canOverPartition(self) -> bool:
        """Return True if the database supports the OVER statement."""

        return True  # pragma: no cover

    def canRegenTables(self) -> bool:
        """Return True if the database can regenerate tables."""

        return True  # pragma: no cover

    def regenTable(self, table_name: str, mtd: "pntablemetadata.PNTableMetaData") -> bool:
        """Regenerate a table."""

        return True  # pragma: no cover

    def releaseSavePoint(self, save_point: int) -> bool:
        """Release a save point."""

        return True  # pragma: no cover

    def Mr_Proper(self) -> None:
        """Clean the database of unnecessary tables and records."""

        return  # pragma: no cover

    def transaction(self) -> bool:
        """Create a transaction/savePoint."""

        return True  # pragma: no cover

    def rollback(self) -> bool:
        """Roll back a transaction/savepoint."""

        return True  # pragma: no cover

    def nextSerialVal(self, table: str, field: str) -> int:
        """Indicate next available value of a serial type field."""

        return 0  # pragma: no cover

    def existsTable(self, name: str) -> bool:
        """Indicate the existence of a table in the database."""

        return False  # pragma: no cover

    def createTable(self, tmd: "pntablemetadata.PNTableMetaData") -> bool:
        """Create a table in the database, from a pntablemetadata.PNTableMetaData."""

        return False  # pragma: no cover

    def mismatchedTable(self, tablename: str, tmd: "pntablemetadata.PNTableMetaData") -> bool:
        """Compare an existing table with a pntablemetadata.PNTableMetaData and return if there are differences."""

        return False  # pragma: no cover

    def normalizeValue(self, text: str) -> Optional[str]:
        """Return the value of a correctly formatted string to the database type from a string."""

        return None  # pragma: no cover

    # def queryUpdate(self, name: str, update: str, filter: str) -> Optional[str]:
    #    """Return a correct UPDATE query for the database type."""

    #    return ""  # pragma: no cover

    def execute_query(self, query: str) -> Optional["result.ResultProxy"]:
        """Execute a query in a database cursor."""

        return None  # pragma: no cover

    def alterTable(self, table_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Modify the fields of a table in the database based on the differences of two pntablemetadata.PNTableMetaData."""

        return False  # pragma: no cover

    def getTimeStamp(self) -> str:
        """Return timestamp."""

        return ""  # pragma: no cover

    def manager(self) -> "flmanager.FLManager":
        """Return flmanager instance."""

        return self.connManager().manager()  # pragma: no cover

    def managerModules(self) -> "flmanagermodules.FLManagerModules":
        """Return flmanager instance."""

        return self.connManager().managerModules()  # pragma: no cover

    def singleConnection(self) -> bool:
        """Return if driver uses a single connection."""
        return False  # pragma: no cover

    def sqlLength(self, field_name: str, size: int) -> str:
        """Return length formated."""

        return ""  # pragma: no cover

    def insert_data(self, table_name: str, fields: List[str], values: List[str]) -> bool:
        """Insert data into table."""

        return True  # pragma: no cover

    def update_data(
        self, metadata: "pntablemetadata.PNTableMetaData", data: Dict[str, Any], pk_value: Any
    ) -> bool:
        """Update table data."""

        return True  # pragma: no cover

    def delete_data(self, metadata: "pntablemetadata.PNTableMetaData", pk_value: Any) -> bool:
        """Delete row from table."""

        return True  # pragma: no cover

    def close(self) -> None:
        """Close connection."""

        return  # pragma: no cover

    def resolve_dsn(self) -> str:
        """Return dsn data."""

        return ""
