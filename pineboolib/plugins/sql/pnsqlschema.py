"""PNSqlSchema module."""

from pineboolib import logging

import traceback
from typing import Iterable, Optional, Union, List, Any, Dict, TYPE_CHECKING
from pineboolib.core import settings

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401


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
    rows_cached: Dict[str, List[Any]]
    init_cached: int = 200

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
        self.db_ = None
        self.rows_cached = {}
        # self.sql_query = {}
        # self.cursors_dict = {}

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
        if settings.config.value("ebcomportamiento/orm_enabled", False) and self.session_ is None:
            from sqlalchemy.orm import sessionmaker  # type: ignore

            Session = sessionmaker(bind=self.engine())
            self.session_ = Session()

        return self.session_

    def declarative_base(self) -> Any:
        """Return sqlAlchemy declarative base."""
        if (
            settings.config.value("ebcomportamiento/orm_enabled", False)
            and self.declarative_base_ is None
        ):
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

    def alterTable(
        self,
        mtd1: Union[str, "pntablemetadata.PNTableMetaData"],
        mtd2: Optional[str] = None,
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

    def execute_query(self, q: str, cursor: Any = None) -> Any:
        """Excecute a query and return result."""
        if not self.isOpen():
            logger.warning("%s::execute_query: Database not open", __name__)

        self.set_last_error_null()
        if cursor is None:
            cursor = self.cursor()
        try:
            # q = self.fix_query(q)
            cursor.execute(q)
        except Exception:
            logger.error("SQL3Driver:: No se pudo ejecutar la query %s" % q, q)
            self.setLastError(
                "%s::No se pudo ejecutar la query %s.\n%s" % (__name__, q, traceback.format_exc()),
                q,
            )

        return cursor

    def getTimeStamp(self) -> str:
        """Return TimeStamp."""

        sql = "SELECT CURRENT_TIMESTAMP"

        cur = self.execute_query(sql)
        time_stamp_: str
        for line in cur:
            time_stamp_ = line[0]
            break

        if time_stamp_ is None:
            raise Exception("timestamp is empty!")

        return time_stamp_

    def declareCursor(
        self, curname: str, fields: str, table: str, where: str, cursor: Any, conn: Any
    ) -> None:
        """Set a refresh query for database."""
        sql = "SELECT %s FROM %s WHERE %s " % (fields, table, where)
        sql = self.fix_query(sql)
        self.rows_cached[curname] = []
        try:
            cursor.execute(sql)
            data_list = cursor.fetchmany(self.init_cached)
            for data in data_list:
                self.rows_cached[curname].append(data)

        except Exception as e:
            logger.error("declareCursor: %s", e)
            logger.trace("Detalle:", stack_info=True)
        # self.sql_query[curname] = sql

    def getRow(self, number: int, curname: str, cursor: Any) -> List:
        """Return a data row."""
        try:
            cached_count = len(self.rows_cached[curname])
            if number >= cached_count:

                data_list = cursor.fetchmany(number - cached_count + 1)
                for row in data_list:
                    self.rows_cached[curname].append(row)

                cached_count = len(self.rows_cached[curname])

        except Exception as e:
            logger.error("getRow: %s", e)
            logger.trace("Detalle:", stack_info=True)

        return self.rows_cached[curname][number] if number < cached_count else []

    def findRow(self, cursor: Any, curname: str, field_pos: int, value: Any) -> Optional[int]:
        """Return index row."""
        ret_ = None
        try:
            for n, row in enumerate(self.rows_cached[curname]):
                if row[field_pos] == value:
                    return n

            cached_count = len(self.rows_cached[curname])

            while True:
                data = cursor.fetchone()
                if not data:
                    break

                self.rows_cached[curname].append(data)
                if data[field_pos] == value:
                    ret_ = cached_count
                    break

                cached_count += 1

        except Exception as e:
            logger.error("finRow: %s", e)
            logger.warning("%s %s Detalle:", curname, field_pos, stack_info=True)

        return ret_

    def deleteCursor(self, cursor_name: str, cursor: Any) -> None:
        """Delete cursor."""
        try:
            del cursor
            self.rows_cached[cursor_name] = []
            self.rows_cached.pop(cursor_name)
        except Exception as exception:
            logger.error("finRow: %s", exception)
            logger.warning("Detalle:", stack_info=True)

    def queryUpdate(self, name: str, update: str, filter: str) -> str:
        """Return a database friendly update query."""
        sql = "UPDATE %s SET %s WHERE %s" % (name, update, filter)
        return sql

    def cursor(self) -> Any:
        """Return a cursor connection."""

        if self.cursor_ is None:
            if self.conn_ is None:
                raise Exception("cursor. self.conn_ is None")
            self.cursor_ = self.conn_.cursor()
        return self.cursor_
