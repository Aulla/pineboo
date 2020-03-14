"""Flsqls module."""


from pineboolib.core import decorators

from pineboolib.application.metadata import pntablemetadata
from pineboolib import logging

from pineboolib.fllegacy import flutil
from . import pnsqlschema

from typing import Optional, Union, List, Any


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
        self._like_true = "1"
        self._like_false = "0"
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

    def nextSerialVal(self, table_name: str, field_name: str) -> int:
        """Return next serial value."""

        if self.isOpen():
            cur = self.execute_query("SELECT NEXT VALUE FOR %s_%s_seq" % (table_name, field_name))
            result = cur.fetchone()
            if not result:
                LOGGER.warning("not exec sequence")
            else:
                return result[0]

        return 0

    def releaseSavePoint(self, n: int) -> bool:
        """Set release savepoint."""

        return True

    def setType(self, type_: str, leng: int = 0) -> str:
        """Return type definition."""
        type_ = type_.lower()
        res_ = ""
        if type_ in ("int", "serial"):
            res_ = "INT"
        elif type_ == "uint":
            res_ = "BIGINT"
        elif type_ in ("bool", "unlock"):
            res_ = "BIT"
        elif type_ == "double":
            res_ = "DECIMAL"
        elif type_ == "time":
            res_ = "TIME"
        elif type_ == "date":
            res_ = "DATE"
        elif type_ in ("pixmap", "stringlist"):
            res_ = "TEXT"
        elif type_ == "string":
            res_ = "VARCHAR"
        elif type_ == "bytearray":
            res_ = "NVARCHAR"
        elif type_ == "timestamp":
            res_ = "DATETIME2"
        else:
            LOGGER.warning("seType: unknown type %s", type_)
            leng = 0

        return "%s(%s)" % (res_, leng) if leng else res_

    def existsTable(self, table_name: str) -> bool:
        """Return if exists a table specified by name."""

        cur = self.execute_query(
            "SELECT 1 FROM sys.Tables WHERE  Name = N'%s' AND Type = N'U'" % table_name
        )
        result = cur.fetchone()

        return True if result else False

    def sqlCreateTable(
        self, tmd: "pntablemetadata.PNTableMetaData", create_index: bool = True
    ) -> Optional[str]:
        """Return a create table query."""
        util = flutil.FLUtil()

        primary_key = ""
        sql = "CREATE TABLE %s (" % tmd.name()
        seq = None

        field_list = tmd.fieldList()

        unlocks = 0
        for number, field in enumerate(field_list):

            sql += field.name()
            type_ = field.type()
            if type_ == "serial":
                seq = "%s_%s_seq" % (tmd.name(), field.name())
                if self.isOpen() and create_index:
                    try:
                        self.execute_query("CREATE SEQUENCE %s START WITH 1 INCREMENT BY 1" % seq)
                    except Exception as error:
                        LOGGER.error("%s::sqlCreateTable:%s", __name__, str(error))

                    sql += " INT"

            elif type_ == "double":
                sql += " DECIMAL(%s,%s)" % (
                    int(field.partInteger()) + int(field.partDecimal()),
                    int(field.partDecimal()),
                )

            else:
                if type_ == "unlock":
                    unlocks += 1

                    if unlocks > 1:
                        LOGGER.warning(
                            u"FLManager : No se ha podido crear la tabla %s ", tmd.name()
                        )
                        LOGGER.warning(
                            u"FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno."
                        )
                        return None

                sql += " %s" % self.setType(type_, field.length())

            if field.isPrimaryKey():
                if not primary_key:
                    sql = sql + " PRIMARY KEY"
                    primary_key = field.name()
                else:
                    LOGGER.warning(
                        util.translate(
                            "application",
                            "FLManager : Tabla-> %s ." % tmd.name()
                            + "Se ha intentado poner una segunda clave primaria para el campo %s ,pero el campo %s ya es clave primaria."
                            % (primary_key, field.name())
                            + "Sólo puede existir una clave primaria en FLTableMetaData, use FLCompoundKey para crear claves compuestas.",
                        )
                    )
                    return None
            else:

                sql += " UNIQUE" if field.isUnique() else ""
                sql += " NULL" if field.allowNull() else " NOT NULL"

            if number != len(field_list) - 1:
                sql += ","

        sql += ")"

        return sql

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

    @decorators.not_implemented_warn
    def alterTable(self, new_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Modify a table structure."""

        return True
