"""Flsqlite module."""


from pineboolib.application.utils import path

from pineboolib import logging, application

from pineboolib.fllegacy import flutil
from sqlalchemy import event

from . import pnsqlschema


import os


from typing import Optional, Any, List, Dict, Union, TYPE_CHECKING
from sqlalchemy import create_engine  # type: ignore [import] # noqa: F821, F401
from sqlalchemy.orm import sessionmaker  # type: ignore [import] # noqa: F821
import sqlalchemy

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata
    from sqlalchemy.engine import base  # type: ignore [import] # noqa: F401, F821
    from sqlalchemy.orm import session  # type: ignore [import] # noqa: F821, F401

LOGGER = logging.get_logger(__name__)


class FLSQLITE(pnsqlschema.PNSqlSchema):
    """FLSQLITE class."""

    db_filename: Optional[str]

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.version_ = "0.9"
        self.name_ = "FLsqlite"
        self.errorList = []
        self.alias_ = "SQLite3 (SQLITE3)"
        self.db_filename = None
        self.db_ = None
        self.mobile_ = True
        self.desktop_file = True
        self._null = ""
        self._text_like = ""
        self._text_cascade = ""

        self._sqlalchemy_name = "sqlite"

    def getConn(
        self, name: str, host: str, port: int, usern: str, passw_: str, limit_conn=0
    ) -> "base.Connection":
        """Return connection."""

        conn_ = None

        main_conn = None
        if "main_conn" in application.PROJECT.conn_manager.connections_dict.keys():
            main_conn = application.PROJECT.conn_manager.mainConn()
            if self.db_filename == main_conn.driver().db_filename:
                self._engine = main_conn.driver()._engine
                self._connection = main_conn.driver()._connection
                return self._connection
                # self._session = main_conn.driver()._session
                # return self._connection

        # if self.db_._name == "main_conn":

        #    if hasattr(self, "_connection") and self._connection:
        #        self._connection.close()
        #        del self._connection

        queqe_params: Dict[str, Union[int, bool, str, Dict[str, int]]] = {}
        # queqe_params["connect_args"] = {"timeout": 5}
        queqe_params["encoding"] = "UTF-8"
        queqe_params["isolation_level"] = "AUTOCOMMIT"
        if application.LOG_SQL:
            queqe_params["echo"] = True

        # if limit_conn > 0:
        #    queqe_params["pool_size"] = limit_conn
        # queqe_params["max_overflow"] = int(limit_conn * 2)

        if conn_ is None:
            if not os.path.exists("%s/sqlite_databases/" % application.PROJECT.tmpdir):
                os.mkdir("%s/sqlite_databases/" % application.PROJECT.tmpdir)

            self._engine = create_engine(
                self.loadConnectionString(name, host, port, usern, passw_), **queqe_params
            )
            conn_ = self._engine.connect()

            if not os.path.exists("%s" % self.db_filename) and self.db_filename not in [
                ":memory:",
                "temp_db",
            ]:
                LOGGER.warning("La base de datos %s no existe", self.db_filename)

            if conn_ is not None:
                # self.session()
                self._connection = conn_

        return conn_

    def loadConnectionString(self, name: str, host: str, port: int, usern: str, passw_: str) -> str:
        """Set special config."""

        return "%s:///%s" % (self._sqlalchemy_name, self.db_filename)
        # return "%s:///%s?timeout=10&nolock=1" % (self._sqlalchemy_name, self.db_filename)

    def setDBName(self, name: str):
        """Set DB Name."""

        self._dbname = "temp_db" if name == ":memory:" else name

        self.db_filename = path._dir("sqlite_databases/%s.sqlite3" % self._dbname)

        if name == ":memory:":
            if application.PROJECT._splash:
                application.PROJECT._splash.hide()

            if application.VIRTUAL_DB:
                self.db_filename = name

    def setType(self, type_: str, leng: int = 0) -> str:
        """Return type definition."""
        res_ = ""
        type_ = type_.lower()
        if type_ == "int":
            res_ = "INTEGER"
        elif type_ == "uint":
            res_ = "INTEGER"
        elif type_ in ("bool", "unlock"):
            res_ = "BOOLEAN"
        elif type_ == "double":
            res_ = "FLOAT"
        elif type_ == "time":
            res_ = "VARCHAR(20)"
        elif type_ == "date":
            res_ = "VARCHAR(20)"
        elif type_ == "pixmap":
            res_ = "TEXT"
        elif type_ == "string":
            res_ = "VARCHAR"
        elif type_ == "stringlist":
            res_ = "TEXT"
        elif type_ == "bytearray":
            res_ = "CLOB"
        elif type_ == "timestamp":
            res_ = "DATETIME"
        else:
            LOGGER.warning("seType: unknown type %s", type_)
            leng = 0

        return "%s(%s)" % (res_, leng) if leng else res_

    def process_booleans(self, where: str) -> str:
        """Process booleans fields."""
        where = where.replace("'true'", "1")
        return where.replace("'false'", "0")

    def sqlCreateTable(
        self, tmd: "pntablemetadata.PNTableMetaData", create_index: bool = True
    ) -> Optional[str]:
        """Return a create table query."""

        util = flutil.FLUtil()
        primary_key = ""
        sql = "CREATE TABLE %s (" % tmd.name()

        field_list = tmd.fieldList()

        unlocks = 0
        for number, field in enumerate(field_list):
            type_ = field.type()

            sql += field.name()

            if type_ == "serial":
                sql += " INTEGER"
                if not field.isPrimaryKey():
                    sql += " PRIMARY KEY"
            else:
                if type_ == "unlock":
                    unlocks = unlocks + 1

                    if unlocks > 1:
                        LOGGER.debug(u"FLManager : No se ha podido crear la tabla " + tmd.name())
                        LOGGER.debug(
                            u"FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno."
                        )
                        return None

                sql += " %s" % self.setType(type_, field.length())

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

        sql += ");"

        if tmd.primaryKey() and create_index:
            sql += "CREATE INDEX %s_pkey ON %s (%s)" % (tmd.name(), tmd.name(), tmd.primaryKey())

        return sql

    def recordInfo2(self, table_name: str) -> List[List]:
        """Return info from a database table."""

        info = []
        sql = "PRAGMA table_info('%s')" % table_name

        cursor = self.execute_query(sql)
        res = cursor.fetchall() if cursor else []

        for columns in res:
            field_name = columns[1]
            field_type = columns[2]
            field_size = 0
            field_allow_null = columns[3] == 0
            field_primary_key = columns[5] == 1
            if field_type.find("VARCHAR(") > -1:
                field_size = field_type[field_type.find("(") + 1 : len(field_type) - 1]

            info.append(
                [
                    field_name,
                    self.decodeSqlType(field_type),
                    not field_allow_null,
                    int(field_size),
                    None,  # field_precision
                    None,  # default value
                    field_primary_key,
                ]
            )

        return info

    def decodeSqlType(self, type_: str) -> str:
        """Return the specific field type."""

        ret = str(type_)
        if type_ == "BOOLEAN":  # y unlock
            ret = "bool"
        elif type_ == "FLOAT":
            ret = "double"
        elif type_.find("VARCHAR") > -1:  # Aqui también puede ser time y date
            ret = "string"
        elif type_ == "TEXT":  # Aquí también puede ser pixmap
            ret = "stringlist"
        elif type_ == "INTEGER":  # serial
            ret = "uint"
        elif type_ == "DATETIME":
            ret = "timestamp"

        return ret

    def tables(self, type_name: Optional[str] = "All") -> List[str]:
        """Return a tables list specified by type."""

        table_list: List[str] = []
        result_list: List[Any] = []
        if self.is_open():

            if type_name in ("Tables", ""):
                cursor = self.execute_query(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name ASC"
                )
                result_list += cursor.fetchall() if cursor else []

            if type_name in ("Views", ""):
                cursor = self.execute_query(
                    "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name ASC"
                )
                result_list += cursor.fetchall() if cursor else []

            if type_name in ("SystemTables", ""):
                table_list.append("sqlite_master")

        for item in result_list:
            table_list.append(item[0])

        return table_list

    def remove_index(self, metadata: "pntablemetadata.PNTableMetaData", query: Any) -> bool:
        """Remove olds index."""

        if not query.exec_("DROP INDEX IF EXISTS %s_pkey" % metadata.name()):
            return False

        return True

    def connection(self) -> "base.Connection":
        """Retrun connection."""

        if not getattr(self, "_connection", None) or self._connection.closed:
            if getattr(self, "_engine", None):
                self._connection = self._engine.connect()
                self._connection.execute("PRAGMA journal_mode=WAL")
                self._connection.execute("PRAGMA synchronous=NORMAL")

                event.listen(self._engine, "close", self.close_emited)
            else:
                raise Exception("Engine is not loaded!")
        return self._connection
