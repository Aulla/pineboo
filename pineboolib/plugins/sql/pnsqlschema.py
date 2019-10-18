"""PNSqlSchema module."""

from pineboolib import logging

import traceback
from typing import Iterable, Optional, Union, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401
    from pineboolib.application.database import pnsqlcursor  # noqa: F401


logger = logging.getLogger(__name__)


class PNSqlSchema(object):
    """PNSqlSchema class."""

    version_: str
    conn_: Any
    name_: str
    alias_: str
    errorList: List[str]
    lastError_: Optional[str]
    db_: Any
    _dbname: str
    mobile_: bool
    pure_python_: bool
    defaultPort_: int
    engine_: Any
    session_: Any
    declarative_base_: Any
    cursor_: Any

    def __init__(self):
        """Inicialize."""
        self.version_ = ""
        self.name_ = ""
        self.open_ = False
        self.errorList = []
        self.alias_ = ""
        self._dbname = ""
        self.mobile_ = False
        self.pure_python_ = False
        self.defaultPort_ = 0
        self.engine_ = None
        self.session_ = None
        self.declarative_base_ = None
        self.lastError_ = None
        self.cursor_ = None

    def useThreads(self) -> bool:
        """Return True if the driver use threads."""
        return False

    def useTimer(self) -> bool:
        """Return True if the driver use Timer."""
        return True

    def version(self) -> str:
        """Return version number."""
        return self.version_

    def driverName(self) -> str:
        """Return driver name."""
        return self.name_

    def isOpen(self) -> bool:
        """Return if the connection is open."""
        return self.open_

    def pure_python(self) -> bool:
        """Return if the driver is python only."""
        return self.pure_python_

    def safe_load(self) -> bool:
        """Return if the driver can loads dependencies safely."""
        return False

    def mobile(self) -> bool:
        """Return if the driver is mobile ready."""
        return self.mobile_

    def DBName(self) -> str:
        """Return database name."""
        return self._dbname

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_userName: str, db_password: str
    ) -> Any:
        """Connec to to database."""
        return None

    def engine(self) -> Any:
        """Return sqlAlchemy ORM engine."""
        return self.engine_

    def session(self) -> Any:
        """Create a sqlAlchemy session."""
        if self.session_ is None:
            from sqlalchemy.orm import sessionmaker  # type: ignore

            Session = sessionmaker(bind=self.engine())
            self.session_ = Session()

        return self.session_

    def declarative_base(self) -> Any:
        """Return sqlAlchemy declarative base."""
        if self.declarative_base_ is None:
            from sqlalchemy.ext.declarative import declarative_base  # type: ignore

            self.declarative_base_ = declarative_base()

        return self.declarative_base_

    def formatValueLike(self, type_: str, v: Any, upper: bool) -> str:
        """Return a string with the format value like."""

        return ""

    def formatValue(self, type_: str, v: Any, upper: bool) -> Optional[Union[int, str, bool]]:
        """Return a string with the format value."""

        return ""

    def canOverPartition(self) -> bool:
        """Return can override partition option ready."""
        return True

    def canRegenTables(self) -> bool:
        """Return if can regenerate tables."""
        return True

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Return next serial value."""

        return None

    def savePoint(self, n: int) -> bool:
        """Set a savepoint."""
        return True

    def canSavePoint(self) -> bool:
        """Return if can do save point."""
        return True

    def canTransaction(self) -> bool:
        """Return if can do transaction."""
        return True

    def rollbackSavePoint(self, n: int) -> bool:
        """Set rollback savepoint."""
        return True

    def set_last_error_null(self) -> None:
        """Set lastError flag Null."""
        self.lastError_ = None

    def setLastError(self, text: str, command: str) -> None:
        """Set last error."""
        self.lastError_ = "%s (%s)" % (text, command)

    def lastError(self) -> Optional[str]:
        """Return last error."""
        return self.lastError_

    def commitTransaction(self) -> bool:
        """Set commit transaction."""
        return True

    def rollbackTransaction(self) -> bool:
        """Set a rollback transaction."""
        return True

    def transaction(self) -> bool:
        """Set a new transaction."""
        return True

    def releaseSavePoint(self, n: int) -> bool:
        """Set release savepoint."""
        return True

    def setType(self, type_: str, leng: Optional[Union[str, int]] = None) -> str:
        """Return type definition."""
        if leng:
            return "::%s(%s)" % (type_, leng)
        else:
            return "::%s" % type_

    def refreshQuery(
        self, curname: str, fields: str, table: str, where: str, cursor: Any, conn: Any
    ) -> None:
        """Set a refresh query for database."""
        pass

    def refreshFetch(
        self, number: int, curname: str, table: str, cursor: Any, fields: str, where_filter: str
    ) -> None:
        """Return data fetched."""
        pass

    def fetchAll(
        self, cursor: Any, tablename: str, where_filter: str, fields: str, curname: str
    ) -> List:
        """Return all fetched data from a query."""
        ret_: List[str] = []
        return ret_

    def existsTable(self, name: str) -> bool:
        """Return if exists a table specified by name."""
        return True

    def sqlCreateTable(self, tmd: "pntablemetadata.PNTableMetaData") -> Optional[str]:
        """Return a create table query."""
        return ""

    def mismatchedTable(
        self,
        table1: str,
        tmd_or_table2: Union["pntablemetadata.PNTableMetaData", str],
        db_: Optional[Any] = None,
    ) -> bool:
        """Return if a table is mismatched."""
        return False

    def recordInfo2(self, tablename: str) -> List[List[Any]]:
        """Return info from a database table."""
        return []

    def decodeSqlType(self, type_: str) -> str:
        """Return the specific field type."""
        return ""

    def recordInfo(self, tablename_or_query: Any) -> List[list]:
        """Return info from  a record fields."""
        return []

    def notEqualsFields(self, field1: List[Any], field2: List[Any]) -> bool:
        """Return if a field has canged."""
        return False

    def tables(self, typeName: Optional[str] = None) -> List[str]:
        """Return a tables list specified by type."""
        return []

    def normalizeValue(self, text: str) -> str:
        """Return a database friendly text."""
        return text

    def hasCheckColumn(self, mtd: "pntablemetadata.PNTableMetaData") -> bool:
        """Retrieve if MTD has a check column."""
        field_list = mtd.fieldList()
        if not field_list:
            return False

        for field in field_list:
            if field.isCheck() or field.name().endswith("_check_column"):
                return True

        return False

    def constraintExists(self, name: str) -> bool:
        """Return if constraint exists specified by name."""
        return False

    def queryUpdate(self, name: str, update: str, filter: str) -> str:
        """Return a database friendly update query."""
        return ""

    def alterTable(
        self,
        mtd1: "pntablemetadata.PNTableMetaData",
        mtd2: Optional["pntablemetadata.PNTableMetaData"] = None,
        key: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Modify a table structure."""
        return False

    def insertMulti(self, table_name: str, records: Iterable) -> bool:
        """Insert multiple registers into a table."""
        return False

    def Mr_Proper(self) -> None:
        """Clear all garbage data."""
        pass

    def cascadeSupport(self) -> bool:
        """Return True if the driver support cascade."""
        return True

    def canDetectLocks(self) -> bool:
        """Return if can detect locks."""
        return True

    def fix_query(self, query: str) -> str:
        """Fix string."""
        # ret_ = query.replace(";", "")
        return query

    def desktopFile(self) -> bool:
        """Return if use a file like database."""
        return False

    def cursor(self) -> Any:
        """Return cursor to database."""
        return None

    def execute_query(self, q: str, cursor: Optional["pnsqlcursor.PNSqlCursor"] = None) -> Any:
        """Excecute a query and return result."""
        if not self.isOpen():
            logger.warning("%s::execute_query: Database not open", __name__)

        self.set_last_error_null()
        if cursor is None:
            cursor = self.cursor()
        try:
            q = self.fix_query(q)
            cursor.execute(q)
        except Exception:
            # self.logger.error("SQL3Driver:: No se pudo ejecutar la query %s" % q, q)
            self.setLastError(
                "%s::No se pudo ejecutar la query %s.\n%s" % (__name__, q, traceback.format_exc()),
                q,
            )

        return cursor
