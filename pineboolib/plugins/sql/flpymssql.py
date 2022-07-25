"""Flsqls module."""


from pineboolib.core import decorators
from pineboolib.core.utils import utils_base

from pineboolib.application.metadata import pntablemetadata
from pineboolib import logging

from pineboolib.fllegacy import flutil
from pineboolib.interfaces import isqldriver

from sqlalchemy.orm import sessionmaker  # type: ignore [import] # noqa: F821

from typing import Optional, Union, List, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.engine import (  # type: ignore [import] # noqa: F401, F821
        base,  # noqa: F401
        result,  # noqa: F401
    )  # noqa: F401 # pragma: no cover

    from pineboolib.interfaces import isession


LOGGER = logging.get_logger(__name__)


class FLPYMSSQL(isqldriver.ISqlDriver):
    """FLPYMSSQL class."""

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.version_ = "0.9"
        self.name_ = "FLPYMSSQL"
        self.error_list = []
        self.alias_ = "SQL Server (PYMSSQL)"
        self.default_port = 1433
        self.savepoint_command = "SAVE TRANSACTION"
        self.rollback_savepoint_command = "ROLLBACK TRANSACTION"
        self.commit_transaction_command = "COMMIT"
        self._like_true = "1"
        self._like_false = "0"
        self._safe_load = {"pymssql": "pymssql", "sqlalchemy": "sqlAlchemy"}
        self._database_not_found_keywords = ["20018"]
        self._text_like = ""
        self._sqlalchemy_name = "mssql+pymssql"
        self._create_isolation = False

    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""
        self._queqe_params["connect_args"] = {"autocommit": True}
        conn_ = self.getConn("master", host, port, usern, passw_)
        del self._queqe_params["connect_args"]
        # conn_.execute("set transaction isolation level read uncommitted;")
        return conn_

    def session(self) -> "isession.PinebooSession":
        """Create a sqlAlchemy session."""
        while True:
            session_class = sessionmaker(bind=self.connection(), autoflush=False, autocommit=True)

            new_session = session_class()
            if new_session.connection().connection is not None:
                break
            else:
                LOGGER.warning("Conexión invalida capturada.Solicitando nueva")

        setattr(new_session, "_conn_name", self.db_._name)
        session_key = utils_base.session_id(self.db_._name, True)
        self.db_._conn_manager._thread_sessions[session_key] = new_session
        return new_session

    def existsTable(self, table_name: str) -> bool:
        """Return if exists a table specified by name."""

        sql = (
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE "
            + "TABLE_NAME = N'%s' AND TABLE_CATALOG = '%s'" % (table_name, self._dbname)
        )
        cur = self.execute_query(sql)
        return True if cur and cur.fetchone() else False

    def nextSerialVal(self, table_name: str, field_name: str) -> int:
        """Return next serial value."""

        if self.is_open():
            cur = self.execute_query("SELECT NEXT VALUE FOR %s_%s_seq" % (table_name, field_name))

            if cur and cur.returns_rows:
                return cur.fetchone()[0]  # type: ignore [index] # noqa: F821

            LOGGER.warning("not exec sequence")

        return 0

    def releaseSavePoint(self, num: int) -> bool:
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
        elif type_ == "json":
            res_ = "NVARCHAR"
        else:
            LOGGER.warning("seType: unknown type %s", type_)
            leng = 0

        return "%s(%s)" % (res_, leng) if leng else res_

    def sqlCreateTable(
        self, tmd: "pntablemetadata.PNTableMetaData", create_index: bool = True
    ) -> Optional[str]:
        """Return a create table query."""

        if tmd.isQuery():
            return self.sqlCreateView(tmd)

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
                if self.is_open() and create_index:
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
                        LOGGER.warning("FLManager : No se ha podido crear la tabla %s ", tmd.name())
                        LOGGER.warning(
                            "FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno."
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
                    raise Exception(
                        "A primary key (%s) has been defined before the field %s.%s -> %s"
                        % (primary_key, tmd.name(), field.name(), sql)
                    )
            else:

                sql += " UNIQUE" if field.isUnique() else ""
                sql += " NULL" if field.allowNull() else " NOT NULL"

            if number != len(field_list) - 1:
                sql += ","

        sql += ")"

        return sql

    def decodeSqlType(self, type_: Union[int, str]) -> str:
        """Return the specific field type."""
        ret = str(type_).lower()

        if type_ == "bit":
            ret = "bool"
        elif type_ == "bigint":
            ret = "uint"
        elif type_ == "decimal":
            ret = "double"
        elif type_ == "date":
            ret = "date"
        elif type_ == "time":
            ret = "time"
        elif type_ == "varchar":
            ret = "string"
        elif type_ == "nvarchar":
            ret = "bytearray"
        elif type_ == "text":
            ret = "stringlist"
        elif type_ == "datetime2":
            ret = "timestamp"
        elif type_ == "json":
            ret = "json"

        return ret

    def tables(self, type_name: str = "", table_name: str = "") -> List[str]:
        """Return a tables list specified by type."""
        table_list: List[str] = []
        result_list: List[Any] = []
        if self.is_open():

            where: List[str] = []
            if type_name in ("Tables", ""):
                where.append("xtype ='U'")
            if type_name in ("Views", ""):
                where.append("xtype ='V'")
            if type_name in ("SystemTables", ""):
                where.append("xtype ='S'")

            if where:
                and_name = " AND name ='%s'" % (table_name) if table_name else ""

                cursor = self.execute_query(
                    "SELECT name FROM SYSOBJECTS where %s%s ORDER BY name ASC"
                    % (" OR ".join(where), and_name)
                )
                result_list += cursor.fetchall() if cursor else []

        table_list = [item[0] for item in result_list]

        return table_list

    def declareCursor(
        self, curname: str, fields: str, table: str, where: str, conn_db: "base.Connection"
    ) -> Optional["result.ResultProxy"]:
        """Set a refresh query for database."""

        if not self.is_open():
            raise Exception("declareCursor: Database not open")

        sql = "DECLARE %s CURSOR STATIC FOR SELECT %s FROM %s WHERE %s " % (
            curname,
            fields,
            table,
            where,
        )
        try:
            conn_db.execute(sql)
            conn_db.execute("OPEN %s" % curname)
        except Exception as error:
            LOGGER.error("refreshQuery: %s", error)
            LOGGER.info("SQL: %s", sql)
            LOGGER.trace("Detalle:", stack_info=True)

        return None

    def deleteCursor(self, cursor_name: str, cursor: Any) -> None:
        """Delete cursor."""

        if not self.is_open():
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

    # def fix_query(self, query: str) -> str:
    #    """Fix string."""
    #    # ret_ = query.replace(";", "")
    #    return query

    @decorators.not_implemented_warn
    def alterTable(self, new_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Modify a table structure."""

        return True

    def recordInfo2(self, tablename: str) -> Dict[str, List[Any]]:
        """Return info from a database table."""
        info = {}
        sql = (
            "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, NUMERIC_PRECISION_RADIX,"
            + " CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s'"
            % tablename.lower()
        )

        data = self.execute_query(sql)
        res = data.fetchall() if data else []
        for columns in res:
            field_size = int(columns[5]) if columns[5] else 0
            # field_precision = columns[4] or 0
            field_name = columns[0]
            field_type = self.decodeSqlType(columns[1])
            field_allow_null = columns[2] == "YES"
            field_default_value = columns[3]

            info[field_name] = [
                field_name,
                field_type,
                not field_allow_null,
                field_size,
                None,
                field_default_value,
                None,  # field_pk
            ]

        return info

    def vacuum(self) -> None:
        """Vacuum tables."""

        return

    def sqlLength(self, field_name: str, size: int) -> str:
        """Return length formated."""

        return "LEN(%s)=%s" % (field_name, size)
