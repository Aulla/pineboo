"""
Module for MYISAM driver.
"""
from pineboolib import logging
from pineboolib.interfaces import isqldriver
from typing import Any, Optional, List, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401 # pragma: no cover
    from sqlalchemy.engine import base  # noqa: F401 # pragma: no cover

LOGGER = logging.get_logger(__name__)


class FLMYSQL_MYISAM(isqldriver.ISqlDriver):  # pylint: disable=invalid-name
    """MYISAM Driver class."""

    _default_charset: str

    def __init__(self):
        """Create empty driver."""
        super().__init__()
        self.version_ = "0.9"
        self.name_ = "FLMYSQL_MyISAM"
        self.alias_ = "MySQL MyISAM (MYSQLDB)"
        self._no_inno_db = True
        self.default_port = 3306
        self.active_create_index = True
        self.rollback_savepoint_command = "ROLLBACK TO SAVEPOINT"
        self.commit_transaction_command = "COMMIT"
        self.rollback_transaction_command = "ROLLBACK"
        self.transaction_command = "START TRANSACTION"
        self._true = True
        self._false = False
        self._like_true = "1"
        self._like_false = "0"
        self._text_like = " "
        self._create_isolation = False
        self._use_create_table_save_points = False
        self._database_not_found_keywords = ["Unknown database"]
        self._default_charset = "DEFAULT CHARACTER SET = utf8 COLLATE = utf8_bin"
        self._sqlalchemy_name = "mysql"

    def tables(self, type_name: str = "", table_name: str = "") -> List[str]:
        """Return a tables list specified by type."""
        table_list: List[str] = []
        result_list: List[Any] = []
        if self.is_open():
            where: List[str] = []
            if type_name in ("Tables", ""):
                where.append(
                    "TABLE_TYPE LIKE 'BASE TABLE' AND TABLE_SCHEMA LIKE '%s'" % self.DBName()
                )
            if type_name in ("Views", ""):
                where.append("TABLE_TYPE LIKE 'VIEW' AND TABLE_SCHEMA LIKE '%s'" % self.DBName())
            if type_name in ("SystemTables", ""):
                where.append("TABLE_TYPE LIKE 'SYSTEM VIEW'")

            if where:
                and_name = " AND TABLE_NAME ='%s'" % (table_name) if table_name else ""

                cursor = self.execute_query(
                    "SELECT TABLE_NAME,TABLE_TYPE,ENGINE FROM information_schema.tables where %s%s ORDER BY TABLE_NAME ASC"
                    % (" OR ".join(where), and_name)
                )
                result_list += cursor.fetchall() if cursor else []

            for item in result_list:
                table_name = item[0]
                table_list.append(table_name)
                if table_name not in self._tables_info.keys():
                    self._tables_info[table_name] = {
                        "type": item[1],
                        "engine": item[2],
                    }

            # table_list = [item[0] for item in result_list]

        return table_list

    def setType(self, type_: str, leng: int = 0) -> str:
        """Return type definition."""
        res_ = ""
        type_ = type_.lower()
        if type_ == "int":
            res_ = "INTEGER"
        elif type_ in ["uint", "serial"]:
            res_ = "INT UNSIGNED"
        elif type_ in ("bool", "unlock"):
            res_ = "BOOL"
        elif type_ == "double":
            res_ = "DECIMAL"
        elif type_ == "time":
            res_ = "TIME"
        elif type_ == "date":
            res_ = "DATE"
        elif type_ in ["pixmap", "stringlist"]:
            res_ = "MEDIUMTEXT"
        elif type_ == "string":
            if leng > 255:
                res_ = "VARCHAR"
            else:
                res_ = "CHAR"
        elif type_ == "bytearray":
            res_ = "LONGBLOB"
        elif type_ == "timestamp":
            res_ = "TIMESTAMP"
        elif type_ == "json":
            res_ = "JSON"
        else:
            LOGGER.warning("seType: unknown type %s", type_)
            leng = 0

        return "%s(%s)" % (res_, leng) if leng else res_

    def sqlCreateTable(
        self,
        tmd: "pntablemetadata.PNTableMetaData",
        create_index: bool = True,
        is_view: bool = False,
    ) -> Optional[str]:
        """Create a table from given MTD."""

        if tmd.isQuery():
            return self.sqlCreateView(tmd)

        from pineboolib.fllegacy import flutil

        util = flutil.FLUtil()
        primary_key = ""
        sql = "CREATE TABLE %s (" % tmd.name()
        # seq = None

        field_list = tmd.fieldList()

        unlocks = 0
        for number, field in enumerate(field_list):
            type_ = field.type()
            leng_ = field.length()
            if field.type() == "unlock":
                unlocks += 1

                if unlocks > 1:
                    LOGGER.debug("FLManager : No se ha podido crear la tabla " + tmd.name())
                    LOGGER.debug(
                        "FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno."
                    )
                    return None

            sql += field.name()
            if type_ == "double":
                sql += " DECIMAL(%s,%s)" % (
                    field.partInteger() + field.partDecimal() + 5,
                    field.partDecimal() + 5,
                )

            else:
                if type_ == "string" and leng_ == 0:
                    leng_ = 255

                sql += " %s" % self.setType(type_, leng_)

            if field.isPrimaryKey():
                if not primary_key:
                    sql += " PRIMARY KEY"
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

        engine = ") ENGINE=INNODB" if not self._no_inno_db else ") ENGINE=MyISAM"
        sql += engine

        sql += " %s" % self._default_charset

        return sql

    def dict_cursor(self) -> Any:
        """Return dict cursor."""

        from MySQLdb.cursors import DictCursor  # type: ignore

        return DictCursor

    def recordInfo2(self, table_name: str) -> Dict[str, List[Any]]:
        """Obtain current cursor information on columns."""

        info = {}

        sql = "SHOW FIELDS FROM %s" % table_name

        cursor = self.execute_query(sql)
        res = cursor.fetchall() if cursor else []

        for columns in res:
            field_name = columns[0]
            field_allow_null = columns[2] == "NO"
            field_size = "0"
            field_precision = 0
            field_default_value = columns[4]
            field_primary_key = columns[3] == "PRI"

            if columns[1].find("(") > -1:
                field_type = self.decodeSqlType(columns[1][: columns[1].find("(")])
                if field_type not in ["uint", "int", "double"]:
                    field_size = columns[1][columns[1].find("(") + 1 : columns[1].find(")")]
                else:
                    pos_comma = field_size.find(",")
                    if pos_comma > -1:
                        list_number = field_size.split(",")
                        field_precision = int(list_number[1])
                        field_size = list_number[0]

            else:
                field_type = self.decodeSqlType(columns[1])

            if field_type == "string" and field_size == "255":
                field_size = "0"

            info[field_name] = [
                field_name,
                field_type,
                field_allow_null,
                int(field_size),
                field_precision,
                field_default_value,
                field_primary_key,
            ]

        return info

    def decodeSqlType(self, t: str) -> str:
        """Translate types."""
        ret = t

        if t in ["char", "varchar", "text"]:
            ret = "string"
        elif t == "int unsigned":
            ret = "uint"
        elif t == "int":
            ret = "int"
        elif t == "date":
            ret = "date"
        elif t in ["mediumtext"]:
            ret = "stringlist"
        elif t == "tinyint":
            ret = "bool"
        elif t in ["decimal", "double"]:
            ret = "double"
        elif t == "longblob":
            ret = "bytearray"
        elif t == "time":
            ret = "time"
        elif t == "timestamp":
            ret = "timestamp"
        elif t in ["json", "longtext"]:
            ret = "json"

        else:
            LOGGER.warning("formato desconocido %s", ret)

        return ret

    def vacuum(self):
        """Vacuum tables."""
        table_names = self.db_.tables("Tables")
        # self._connection.connection.set_isolation_level(0)
        for table_name in table_names:
            if self.db_.connManager().manager().metadata(table_name) is not None:
                self.execute_query("ANALYZE TABLE %s" % table_name)
        # self._connection.connection.set_isolation_level(1)

    def getAlternativeConn(
        self, name: str, host: str, port: int, usern: str, passw_: str
    ) -> Optional["base.Connection"]:
        """Return alternative connection."""
        return self.getConn("", host, port, usern, passw_)

    def do_connect(self, dbapi_connection, connection_record):
        """Isolation Level fix."""

        dbapi_connection.isolation_level = "READ COMMITTED"

    def get_common_params(self) -> None:
        """Load common params."""

        super().get_common_params()
        self._queqe_params["isolation_level"] = "READ COMMITTED"

        if self.pool_enabled():
            self._queqe_params["pool_recycle"] = 1800
        else:
            if "connect_args" not in self._queqe_params.keys():
                self._queqe_params["connect_args"] = {}
            if "connect_timeout" not in self._queqe_params["connect_args"].keys():
                self._queqe_params["connect_args"]["connect_timeout"] = 28800  # 8 horas.

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_user_name: str, db_password: str
    ) -> Union["base.Connection", bool]:
        """Connect to database."""

        if self._no_inno_db:
            LOGGER.warning(
                "MyISAM engines doesn't support transactions. ROLLBACK statement doesn't produce any effect"
            )

        return super().connect(db_name, db_host, db_port, db_user_name, db_password)

    def mismatchedTable(self, table_name: str, metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Return if a table is mismatched."""

        if self.invalid_engine(table_name):
            return True

        return super().mismatchedTable(table_name, metadata)

    def invalid_engine(self, table_name: str, mute: bool = False) -> bool:
        """Return if table engine is valid."""

        engine_name = self._tables_info[table_name]["engine"]
        if not self._no_inno_db == (engine_name == "MyISAM"):
            if not mute:
                LOGGER.warning(
                    "The engine of the %s table is of type %s, but the driver uses the %s engine",
                    table_name,
                    engine_name,
                    "MyISAM" if self._no_inno_db else "InnoDB",
                )
            return True

        return False
