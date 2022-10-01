"""Flsqlite module."""


from pineboolib.application.utils import path

from pineboolib import logging, application

from pineboolib.fllegacy import flutil

from pineboolib.interfaces import isqldriver

import os


from typing import Optional, Any, List, Dict, TYPE_CHECKING
from sqlalchemy import create_engine, event  # type: ignore [import] # noqa: F821, F401


if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata
    from sqlalchemy.engine import (
        base,
    )  # type: ignore [import] # noqa: F401, F821 # pragma: no cover
    from sqlalchemy.orm import (  # type: ignore [import] # noqa: F821, F401
        session,
    )  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class FLSQLITE(isqldriver.ISqlDriver):
    """FLSQLITE class."""

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.version_ = "0.9"
        self.name_ = "FLsqlite"
        self.error_list = []
        self.alias_ = "SQLite3 (SQLITE3)"
        self.db_filename = ""
        self.mobile_ = True
        self.desktop_file = True
        self._null = ""
        self._text_like = ""
        self._text_cascade = ""
        self._parse_porc = False
        self._can_use_preping = False

        self._sqlalchemy_name = "sqlite"

    def getConn(
        self, name: str, host: str, port: int, usern: str, passw_: str, alternative: bool = False
    ) -> "base.Connection":
        """Return connection."""

        conn_ = None
        main_conn = None
        if "main_conn" in application.PROJECT.conn_manager.connections_dict.keys():
            main_conn = application.PROJECT.conn_manager.mainConn()
            conn_driver = main_conn.driver()
            if self.db_filename == conn_driver.db_filename:
                self._engine = conn_driver._engine
                self._connection = conn_driver._connection
                return self._connection

        if conn_ is None:
            if (
                not os.path.exists("%s/sqlite_databases/" % application.PROJECT.tmpdir)
                and not self.db_filename == ":memory:"
            ):
                os.mkdir("%s/sqlite_databases/" % application.PROJECT.tmpdir)

            self.get_common_params()
            self._engine = create_engine(
                self.loadConnectionString(name, host, port, usern, passw_), **self._queqe_params
            )

            event.listen(self._engine, "connect", self.do_connect)
            event.listen(self._engine, "begin", self.do_begin)
            event.listen(self._engine, "savepoint", self.do_savepoint)

            if application.SHOW_CONNECTION_EVENTS:
                self.listen_engine()

            conn_ = self.connection()

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

        type_ = type_.lower()
        type_array = {
            "int": "INTEGER",
            "uint": "INTEGER",
            "bool": "BOOLEAN",
            "unlock": "BOOLEAN",
            "double": "FLOAT",
            "time": "VARCHAR(20)",
            "date": "VARCHAR(20)",
            "pixmap": "TEXT",
            "stringlist": "TEXT",
            "string": "VARCHAR",
            "bytearray": "CLOB",
            "timestamp": "DATETIME",
            "json": "JSON",
        }

        res_ = type_array[type_] if type_ in type_array.keys() else ""

        if not res_:
            LOGGER.warning("seType: unknown type %s", type_)
            leng = 0

        return "%s(%s)" % (res_, leng) if leng else res_

    # def process_booleans(self, where: str) -> str:
    #    """Process booleans fields."""

    #    return where.replace("'true'", "1").replace("'false'", "0")

    def sqlCreateTable(
        self, tmd: "pntablemetadata.PNTableMetaData", create_index: bool = True
    ) -> Optional[str]:
        """Return a create table query."""

        if tmd.isQuery():
            return self.sqlCreateView(tmd)

        util = flutil.FLUtil()
        primary_key = ""

        unlocks = 0
        sql_fields: List[str] = []
        for field in tmd.fieldList():

            type_ = field.type()

            sql_field = field.name()

            if type_ == "serial":
                sql_field += " INTEGER"
                if not field.isPrimaryKey():
                    sql_field += " PRIMARY KEY"
            else:
                if type_ == "unlock":
                    unlocks += 1

                    if unlocks > 1:
                        LOGGER.debug("FLManager : No se ha podido crear la tabla " + tmd.name())
                        LOGGER.debug(
                            "FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno."
                        )
                        return None

                sql_field += " %s" % self.setType(type_, field.length())

            if field.isPrimaryKey():
                if not primary_key:
                    sql_field += " PRIMARY KEY"
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
                        % (primary_key, tmd.name(), field.name(), sql_fields)
                    )
            else:

                sql_field += " UNIQUE" if field.isUnique() else ""
                sql_field += " NULL" if field.allowNull() else " NOT NULL"

            sql_fields.append(sql_field)

        sql = "CREATE TABLE %s (%s);" % (tmd.name(), ",".join(sql_fields))

        if tmd.primaryKey() and create_index:
            sql += "CREATE INDEX %s_pkey ON %s (%s)" % (tmd.name(), tmd.name(), tmd.primaryKey())

        return sql

    def recordInfo2(self, table_name: str) -> Dict[str, List[Any]]:
        """Return info from a database table."""

        info = {}
        sql = "PRAGMA table_info('%s')" % table_name

        cursor = self.execute_query(sql)

        for col0, field_name, field_type, allow_null, col4, is_pk in list(
            cursor.fetchall() if cursor else []
        ):

            field_allow_null = allow_null == 0 and is_pk == 0  # type: ignore [comparison-overlap]
            field_primary_key = is_pk == 1  # type: ignore [comparison-overlap]
            field_size = (
                int(field_type[field_type.find("(") + 1 : len(field_type) - 1])
                if field_type.find("VARCHAR(") > -1
                else 0
            )

            info[field_name] = [
                field_name,
                self.decodeSqlType(field_type),
                not field_allow_null,
                int(field_size),
                None,  # field_precision
                None,  # default value
                field_primary_key,
            ]

        return info

    def decodeSqlType(self, type_: str) -> str:
        """Return the specific field type."""

        key = type_
        key = "VARCHAR" if key.find("VARCHAR") > -1 else key

        array_types = {
            "VARCHAR": "string",  # Aqui también puede ser time y date
            "FLOAT": "double",
            "INTEGER": "uint",  # serial
            "BOOLEAN": "bool",  # y unlock
            "TEXT": "stringlist",  # Aquí también puede ser pixmap
            "DATETIME": "timestamp",
            "JSON": "json",
        }

        return array_types[key] if key in array_types else str(type_)

    def tables(self, type_name: str = "", table_name: str = "") -> List[str]:
        """Return a tables list specified by type."""

        table_list: List[str] = []
        result_list: List[Any] = []
        if self.is_open():
            where: List[str] = []
            if type_name in ("Tables", ""):
                where.append("type='table'")
            if type_name in ("Views", ""):
                where.append("type='view'")
            if type_name in ("SystemTables", ""):
                table_list.append("sqlite_master")

            if where:
                and_name = " AND name ='%s'" % (table_name) if table_name else ""

                cursor = self.execute_query(
                    "SELECT name FROM sqlite_master WHERE %s%s ORDER BY name ASC"
                    % (" OR ".join(where), and_name)
                )
                result_list = cursor.fetchall() if cursor else []

            table_list += [item[0] for item in result_list]

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
                self._connection = self._engine.connect().execution_options(autocommit=True)
                self._connection.execute("PRAGMA journal_mode=WAL")
                self._connection.execute("PRAGMA synchronous=NORMAL")

                event.listen(self._engine, "close", self.close_emited)
            else:
                raise Exception("Engine is not loaded!")
        return self._connection

    def get_common_params(self) -> None:
        """Load common params."""

        super().get_common_params()

        self._queqe_params["isolation_level"] = None

    def do_connect(self, dbapi_connection, connection_record):
        """Isolation Level fix."""

        dbapi_connection.isolation_level = None
