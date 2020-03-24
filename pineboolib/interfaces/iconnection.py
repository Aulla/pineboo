# -*- coding: utf-8 -*-
"""
Defines the IConnection class.
"""

from pineboolib.core.utils import logging

from .iapicursor import IApiCursor


from typing import Any, List, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata.pntablemetadata import PNTableMetaData
    from pineboolib.fllegacy import flmanager
    from pineboolib.fllegacy import flmanagermodules

LOGGER = logging.get_logger(__name__)


class IConnection:
    """Interface for database cursors which are used to emulate FLSqlCursor."""

    _db_name: str
    _db_host: Optional[str]
    _db_port: Optional[int]
    _db_user_name: Optional[str]
    _db_password: str = ""
    conn: Any  # connection from the actual driver
    _conn_aux: Dict[str, "IConnection"]
    _driver_sql: Any
    _current_save_point: Optional[Any]  # Optional["PNSqlSavePoint"]
    _stack_save_points: List[Any]  # List["PNSqlSavePoint"]
    _queue_save_points: List[Any]  # List["PNSqlSavePoint"]
    _interactive_gui: bool
    _driver_name: str
    _name: str
    _is_open: bool
    _driver = None

    def connectionName(self) -> str:
        """Get the current connection name for this cursor."""
        return ""

    def isOpen(self) -> bool:
        """Indicate if a connection is open."""
        return False

    def tables(self, tables: Optional[Union[str, int]] = None) -> List[str]:
        """Return a list of available tables in the database, according to a given filter."""
        return []

    def DBName(self) -> str:
        """Return the database name."""
        return ""

    def driver(self) -> Any:
        """Return the instance of the driver that is using the connection."""

        return None

    def database(self) -> Any:
        """Return self."""

        return None

    def session(self) -> Any:
        """
        Sqlalchemy session.

        When using the ORM option this function returns the session for sqlAlchemy.
        """

        return None

    def connManager(self) -> Any:
        """Return connection manager."""

        return

    def engine(self) -> Any:
        """Sqlalchemy connection."""

        return None

    def declarative_base(self) -> Any:
        """Contain the declared models for Sqlalchemy."""

        return None

    def dictDatabases(self) -> Dict[str, "IConnection"]:
        """Return dict with own database connections."""

        return {}

    def cursor(self) -> IApiCursor:
        """Return a cursor to the database."""

        return IApiCursor()

    def lastActiveCursor(self) -> Optional[Any]:  # returns FLSqlCuror
        """Return the last active cursor in the sql driver."""

        return None

    def conectar(self, db_name, db_host, db_port, db_user_name, db_returnword) -> Any:
        """Request a connection to the database."""

        return

    def driverName(self) -> str:
        """Return sql driver name."""

        return ""

    def driverAlias(self) -> str:
        """Return sql driver alias."""

        return ""

    def driverNameToDriverAlias(self, name) -> str:
        """Return the alias from the name of a sql driver."""

        return ""

    def lastError(self) -> str:
        """Return the last error reported by the sql driver."""

        return ""

    def host(self) -> Optional[str]:
        """Return the name of the database host."""

        return ""

    def port(self) -> Optional[int]:
        """Return the port used by the database."""

        return 0

    def user(self) -> Optional[str]:
        """Return the user name used by the database."""

        return ""

    def returnword(self) -> str:
        """Return ****word used by the database."""
        return ""

    def seek(self, offs, whence=0) -> None:
        """Position the cursor at a position in the database."""

        return

    def md5TuplesStateTable(self, curname: str) -> bool:
        """
        Return the sum md5 with the total records inserted, deleted and modified in the database so far.

        Useful to know if the database has been modified from a given moment.
        """

        return True

    def setInteractiveGUI(self, data) -> None:
        """Set if it is an interactive GUI."""

        return

    def setQsaExceptions(self, data) -> None:
        """See properties of the qsa exceptions."""

        return

    def formatValue(self, type_, value, upper) -> str:
        """Return a correctly formatted value to be assigned as a where filter."""

        return ""

    def formatValueLike(self, type_, value, upper) -> str:
        """Return a correctly formatted value to be assigned as a WHERE LIKE filter."""

        return ""

    def canSavePoint(self) -> bool:
        """Inform if the sql driver can manage savepoints."""

        return True

    def canTransaction(self) -> bool:
        """Inform if the sql driver can manage transactions."""

        return True

    def doTransaction(self, cursor) -> bool:
        """Make a transaction or savePoint according to transaction level."""

        return False

    def transactionLevel(self) -> int:
        """Indicate the level of transaction."""

        return 0

    def doRollback(self, cur) -> bool:
        """Drop a transaction or savepoint depending on the transaction level."""

        return False

    def interactiveGUI(self) -> bool:
        """Return if it is an interactive GUI."""

        return False

    def doCommit(self, cur, notify=True) -> bool:
        """Approve changes to a transaction or a save point based on your transaction level."""

        return False

    def canDetectLocks(self) -> bool:
        """Indicate if the connection detects locks in the database."""

        return False

    def commit(self) -> bool:
        """Send the commit order to the database."""

        return True

    def canOverPartition(self) -> bool:
        """Return True if the database supports the OVER statement."""

        return True

    def canRegenTables(self) -> bool:
        """Return True if the database can regenerate tables."""

        return True

    def regenTable(self, table_name: str, mtd: "PNTableMetaData") -> None:
        """Regenerate a table."""

        return None

    def savePoint(self, save_point: int) -> bool:
        """Create a save point."""

        return True

    def releaseSavePoint(self, save_point: int) -> bool:
        """Release a save point."""

        return True

    def Mr_Proper(self) -> None:
        """Clean the database of unnecessary tables and records."""

        return

    def rollbackSavePoint(self, save_point: int) -> bool:
        """Roll back a save point."""

        return True

    def transaction(self) -> bool:
        """Create a transaction."""

        return True

    def commitTransaction(self) -> bool:
        """Release a transaction."""

        return True

    def rollbackTransaction(self) -> bool:
        """Roll back a transaction."""

        return True

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Indicate next available value of a serial type field."""

        return

    def existsTable(self, name: str) -> bool:
        """Indicate the existence of a table in the database."""

        return False

    def createTable(self, tmd: "PNTableMetaData") -> bool:
        """Create a table in the database, from a PNTableMetaData."""

        return False

    def mismatchedTable(self, tablename: str, tmd: "PNTableMetaData") -> bool:
        """Compare an existing table with a PNTableMetaData and return if there are differences."""

        return False

    def normalizeValue(self, text: str) -> Optional[str]:
        """Return the value of a correctly formatted string to the database type from a string."""

        return None

    def queryUpdate(self, name: str, update: str, filter: str) -> Optional[str]:
        """Return a correct UPDATE query for the database type."""

        return ""

    def execute_query(self, query: str, cursor: Any = None) -> Any:
        """Execute a query in a database cursor."""

        return ""

    def alterTable(self, table_metadata: "PNTableMetaData") -> bool:
        """Modify the fields of a table in the database based on the differences of two PNTableMetaData."""

        return False

    def getTimeStamp(self) -> str:
        """Return timestamp."""

        return ""

    def manager(self) -> "flmanager.FLManager":
        """Return flmanager instance."""

        return self.connManager().manager()

    def managerModules(self) -> "flmanagermodules.FLManagerModules":
        """Return flmanager instance."""

        return self.connManager().managerModules()

    def singleConnection(self) -> bool:
        """Return if driver uses a single connection."""
        return False

    def sqlLength(self, field_name: str, size: int) -> str:
        """Return length formated."""

        return ""
