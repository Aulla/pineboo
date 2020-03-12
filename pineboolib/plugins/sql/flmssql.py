"""Flsqls module."""
from PyQt5 import QtCore, Qt, QtWidgets

from pineboolib.core import decorators


from pineboolib.application.database import pnsqlquery
from pineboolib.application.database import pnsqlcursor
from pineboolib.application.metadata import pnfieldmetadata
from pineboolib.application.metadata import pntablemetadata
from pineboolib import logging

from pineboolib.fllegacy import flutil
from . import pnsqlschema

from xml.etree import ElementTree
import traceback
from typing import Optional, Union, List, Dict, Any


LOGGER = logging.get_logger(__name__)


class FLMSSQL(pnsqlschema.PNSqlSchema):
    """FLQPSQL class."""

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.version_ = "0.6"
        self.name_ = "FLMSSQL"
        self.errorList = []
        self.alias_ = "SQL Server (PYMSSQL)"
        self.defaultPort_ = 1433
        self.savepoint_command = "SAVE TRANSACTION"
        self.rollback_savepoint_command = "ROLLBACK TRANSACTION"
        self.commit_transaction_command = "COMMIT"
        self._like_true = "'t'"
        self._like_false = "'f'"
        self._safe_load = {"pymssql": "pymssql", "sqlalchemy": "sqlAlchemy"}
        self._database_not_found_keywords = ["does not exist", "no existe"]

    def getEngine(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return sqlAlchemy connection."""
        from sqlalchemy import create_engine  # type: ignore

        return create_engine("mssql+pymssql://%s:%s@%s:%s/%s" % (usern, passw_, host, port, name))

    def loadSpecialConfig(self) -> None:
        """Set special config."""

        self.conn_.autocommit(True)

    def getConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import pymssql  # type: ignore

        conn_ = None

        try:
            conn_ = pymssql.connect(
                server=host, user=usern, password=passw_, database=name, port=port
            )
        except Exception as error:
            self.setLastError(str(error), "CONNECT")

        return conn_

    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import pymssql  # type: ignore

        conn_ = None

        try:
            conn_ = pymssql.connect(server=host, user="SA", password=passw_, port=port)
            conn_.autocommit(True)
        except Exception as error:
            self.setLastError(str(error), "CONNECT")

        return conn_

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Return next serial value."""
        # q = pnsqlquery.PNSqlQuery()
        # q.setSelect(u"nextval('" + table + "_" + field + "_seq')")
        # q.setFrom("")
        # q.setWhere("")
        # if not q.exec_():
        #    LOGGER.warning("not exec sequence")
        # elif q.first():
        #    return q.value(0)
        cursor = self.conn_.cursor()
        cursor.execute("SELECT NEXT VALUE FOR %s_%s_seq" % (table, field))
        result = cursor.fetchone()
        if result is not None:
            return result[0]

        return None

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
        if not self.isOpen():
            LOGGER.warning("PSQLDriver::existsTable: Database not open")
            return False

        cur_ = self.conn_.cursor()
        cur_.execute("SELECT 1 FROM sys.Tables WHERE  Name = N'%s' AND Type = N'U'" % name)
        result_ = cur_.fetchone()
        ok = False if result_ is None else True
        return ok

    def sqlCreateTable(self, tmd: "pntablemetadata.PNTableMetaData") -> Optional[str]:
        """Return a create table query."""
        util = flutil.FLUtil()
        if not tmd:
            return None

        primaryKey = None
        sql = "CREATE TABLE %s (" % tmd.name()
        seq = None

        fieldList = tmd.fieldList()

        unlocks = 0
        for field in fieldList:
            if field.type() == "unlock":
                unlocks = unlocks + 1

        if unlocks > 1:
            LOGGER.warning(u"FLManager : No se ha podido crear la tabla %S ", tmd.name())
            LOGGER.warning(u"FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno.")
            return None

        i = 1
        for field in fieldList:
            sql += field.name()
            type_ = field.type()
            if type_ == "int":
                sql += " INT"
            elif type_ == "uint":
                sql += " BIGINT"
            elif type_ in ("bool", "unlock"):
                sql += " BIT"
            elif type_ == "double":
                sql += " DECIMAL"
                sql += "(%s,%s)" % (
                    int(field.partInteger()) + int(field.partDecimal()),
                    int(field.partDecimal()),
                )
            elif type_ == "time":
                sql += " TIME"
            elif type_ == "date":
                sql += " DATE"
            elif type_ in ("pixmap", "stringlist"):
                sql += " TEXT"
            elif type_ == "string":
                sql += " VARCHAR"
            elif type_ == "bytearray":
                sql += " NVARCHAR"
            elif type_ == "timestamp":
                sql += " DATETIME2"
            elif type_ == "serial":
                seq = "%s_%s_seq" % (tmd.name(), field.name())
                cursor = self.conn_.cursor()
                # self.transaction()
                try:
                    cursor.execute("CREATE SEQUENCE %s START WITH 1 INCREMENT BY 1" % seq)
                except Exception:
                    print("FLQPSQL::sqlCreateTable:\n", traceback.format_exc())

                sql += " INT"

            longitud = field.length()
            if longitud > 0:
                sql = sql + "(%s)" % longitud

            if field.isPrimaryKey():
                if primaryKey is None:
                    sql = sql + " PRIMARY KEY"
                else:
                    LOGGER.warning(
                        util.translate(
                            "application",
                            "FLManager : Tabla-> %s . %s %s ,pero el campo %s ya es clave primaria. %s"
                            % (
                                tmd.name(),
                                "Se ha intentado poner una segunda clave primaria para el campo",
                                field.name(),
                                primaryKey,
                                "Sólo puede existir una clave primaria en FLTableMetaData, use FLCompoundKey para crear claves compuestas.",
                            ),
                        )
                    )
                    return None
            else:
                if field.isUnique():
                    sql = sql + " UNIQUE"
                if not field.allowNull():
                    sql = sql + " NOT NULL"
                else:
                    sql = sql + " NULL"

            if not i == len(fieldList):
                sql = sql + ","
                i = i + 1

        sql = sql + ")"

        return sql

    @decorators.not_implemented_warn
    def mismatchedTable(
        self,
        table1: str,
        tmd_or_table2: Union["pntablemetadata.PNTableMetaData", str],
        db_: Optional[Any] = None,
    ) -> bool:
        """Return if a table is mismatched."""

        if db_ is None:
            db_ = self.db_

        return False

    def decodeSqlType(self, type_: Union[int, str]) -> str:
        """Return the specific field type."""
        ret = str(type_)

        if type_ == 16:
            ret = "bool"
        elif type_ == 23:
            ret = "uint"
        elif type_ == 25:
            ret = "stringlist"
        elif type_ == 701:
            ret = "double"
        elif type_ == 1082:
            ret = "date"
        elif type_ == 1083:
            ret = "time"
        elif type_ == 1043:
            ret = "string"
        elif type_ == 1184:
            ret = "timestamp"

        return ret

    def tables(self, type_name: Optional[str] = "") -> List[str]:
        """Return a tables list specified by type."""
        table_list: List[str] = []
        result_list: List[Any] = []
        if self.isOpen():

            if type_name in ("Tables", ""):
                cursor = self.execute_query("SELECT * FROM SYSOBJECTS WHERE xtype ='U'")
                result_list += cursor.fetchall()

            if type_name in ("Views", ""):
                cursor = self.execute_query("SELECT * FROM SYSOBJECTS WHERE xtype ='V'")
                result_list += cursor.fetchall()

            if type_name in ("SystemTables", ""):
                cursor = self.execute_query("SELECT * FROM SYSOBJECTS WHERE xtype ='S'")
                result_list += cursor.fetchall()

        for item in result_list:
            table_list.append(item[0])

        return table_list

    def queryUpdate(self, name: str, update: str, filter: str) -> str:
        """Return a database friendly update query."""
        return """UPDATE %s SET %s WHERE %s""" % (name, update, filter)

    def declareCursor(
        self, curname: str, fields: str, table: str, where: str, cursor: Any, conn: Any
    ) -> None:
        """Set a refresh query for database."""

        if not self.isOpen():
            raise Exception("declareCursor: Database not open")

        sql = "DECLARE %s CURSOR STATIC FOR SELECT %s FROM %s WHERE %s " % (
            curname,
            fields,
            table,
            where,
        )
        try:
            cursor.execute(sql)
            cursor.execute("OPEN %s" % curname)
        except Exception as e:
            LOGGER.error("refreshQuery: %s", e)
            LOGGER.info("SQL: %s", sql)
            LOGGER.trace("Detalle:", stack_info=True)

    def getRow(self, number: int, curname: str, cursor: Any) -> List:
        """Return a data row."""

        if not self.isOpen():
            raise Exception("getRow: Database not open")

        ret_: List[Any] = []
        sql = "FETCH ABSOLUTE %s FROM %s" % (number + 1, curname)
        sql_exists = "SELECT CURSOR_STATUS('global','%s')" % curname
        cursor.execute(sql_exists)
        if cursor.fetchone()[0] < 1:
            return ret_

        try:
            cursor.execute(sql)
            ret_ = cursor.fetchone()
        except Exception as e:
            LOGGER.error("getRow: %s", e)
            LOGGER.trace("Detalle:", stack_info=True)

        return ret_

    def findRow(self, cursor: Any, curname: str, field_pos: int, value: Any) -> Optional[int]:
        """Return index row."""
        pos: Optional[int] = None

        if not self.isOpen():
            raise Exception("findRow: Database not open")

        try:
            n = 0
            while True:
                sql = "FETCH %s FROM %s" % ("FIRST" if not n else "NEXT", curname)
                cursor.execute(sql)
                data_ = cursor.fetchone()
                if not data_:
                    break
                if data_[field_pos] == value:
                    pos = n
                    break
                else:
                    n += 1

        except Exception as e:
            LOGGER.warning("finRow: %s", e)
            LOGGER.warning("Detalle:", stack_info=True)

        return pos

    def deleteCursor(self, cursor_name: str, cursor: Any) -> None:
        """Delete cursor."""

        if not self.isOpen():
            raise Exception("deleteCursor: Database not open")

        try:
            sql_exists = "SELECT CURSOR_STATUS('global','%s')" % cursor_name
            cursor.execute(sql_exists)

            if cursor.fetchone()[0] < 1:
                return

            cursor.execute("CLOSE %s" % cursor_name)
        except Exception as exception:
            LOGGER.error("finRow: %s", exception)
            LOGGER.warning("Detalle:", stack_info=True)

    def fix_query(self, query: str) -> str:
        """Fix string."""
        # ret_ = query.replace(";", "")
        return query

    # def isOpen(self):
    #    return self.conn_.closed == 0
