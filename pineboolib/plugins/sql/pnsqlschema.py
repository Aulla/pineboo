"""PNSqlSchema module."""

from PyQt5 import QtCore, QtWidgets

from pineboolib import logging, application

from pineboolib.core.utils import utils_base
from pineboolib.application.utils import check_dependencies
from pineboolib.application.database import pnsqlquery

from pineboolib.application import qsadictmodules


from typing import Iterable, Optional, Union, List, Any, Dict, cast, Tuple, TYPE_CHECKING
from pineboolib.core import decorators

from pineboolib.fllegacy import flutil

from sqlalchemy.engine import base, create_engine  # type: ignore [import] # noqa: F821
from sqlalchemy.inspection import inspect  # type: ignore [import] # noqa: F821, F401
from sqlalchemy.orm import sessionmaker  # type: ignore [import] # noqa: F821

from sqlalchemy import event, pool, text
import sqlalchemy  # type: ignore [import] # noqa: F821, F401
import traceback


import re


if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401 # pragma: no cover
    from pineboolib.interfaces import iconnection  # noqa: F401 # pragma: no cover
    from sqlalchemy.engine import (  # type: ignore [import] # noqa: F821, F401
        result,  # noqa: F401
    )  # noqa: F401 # pragma: no cover
    from sqlalchemy.orm import (
        session as orm_session,
    )  # type: ignore [import] # noqa: F821, F401 # pragma: no cover


LOGGER = logging.get_logger(__name__)

ENGINES: Dict[str, "base.Engine"] = {}


class PNSqlSchema(object):
    """PNSqlSchema class."""

    version_: str
    name_: str
    alias_: str
    error_list: List[str]
    _last_error: str
    db_: Any
    _dbname: str
    mobile_: bool
    pure_python_: bool
    default_port: int
    cursor_proxy: Dict[str, "result.ResultProxy"]
    open_: bool
    desktop_file: bool
    _true: Any
    _false: Any
    _like_true: Any
    _like_false: Any
    _null: str
    _text_like: str
    _text_cascade: str
    _safe_load: Dict[str, str]
    _database_not_found_keywords: List[str]
    _parse_porc: bool
    _queqe_params: Dict[str, Any]
    _create_isolation: bool

    _sqlalchemy_name: str
    _connection: "base.Connection"
    _engine: "base.Engine"
    _session: "orm_session.Session"
    _extra_alternative: str
    _sp_level: int
    _use_altenative_isolation_level: bool

    def __init__(self):
        """Inicialize."""
        self.version_ = ""
        self.name_ = ""
        # self._connection = None
        self.error_list = []
        self.alias_ = ""
        self._dbname = ""
        self.mobile_ = False
        self.pure_python_ = False
        self.default_port = 0
        self._parse_porc = True

        self._last_error = ""
        self.db_ = None

        self._text_cascade = "CASCADE"
        self._true = "1"
        self._false = "0"
        self._like_true = "1"
        self._like_false = "0"
        self._null = "Null"
        self._text_like = "::text "
        self._safe_load = {"sqlalchemy": "sqlAlchemy"}
        self._database_not_found_keywords = ["does not exist", "no existe"]
        self._queqe_params = {}
        self._create_isolation = True
        self._extra_alternative = ""
        self._connection = None  # type: ignore [assignment] # noqa: F821
        self._sqlalchemy_name = ""
        self._sp_level = 0
        self._use_altenative_isolation_level = False

    def safe_load(self, exit: bool = False) -> bool:
        """Return if the driver can loads dependencies safely."""
        return check_dependencies.check_dependencies(self._safe_load, exit)

    def close(self):
        """Close driver connection."""

        self.open_ = False
        if self._connection is not None:
            self._connection.close()
            self._connection = None  # type: ignore [assignment] # noqa: F821

    # def singleConnection(self) -> bool:
    #    """Return if driver uses a single connection."""
    #    return self._single_conn

    def loadConnectionString(self, name: str, host: str, port: int, usern: str, passw_: str) -> str:
        """Set special config."""

        return "%s://%s:%s@%s:%s/%s" % (self._sqlalchemy_name, usern, passw_, host, port, name)

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_user_name: str, db_password: str
    ) -> Optional["base.Connection"]:
        """Connect to database."""

        self.setDBName(db_name)
        self.safe_load(True)

        LOGGER.debug = LOGGER.trace  # type: ignore  # Send Debug output to Trace
        conn_ = self.getConn(db_name, db_host, db_port, db_user_name, db_password)

        if (
            conn_ is None and self.db_._name == "main_conn"
        ):  # Si no existe la conexión y soy main_conn
            if application.PROJECT._splash:
                application.PROJECT._splash.hide()
            if not application.PROJECT.DGI.localDesktop():
                return None

            _last_error = self.last_error()
            found = False
            for key in self._database_not_found_keywords:
                if key in _last_error:
                    found = True
                    break

            if found:
                ret = QtWidgets.QMessageBox.warning(
                    QtWidgets.QWidget(),
                    "Pineboo",
                    "La base de datos %s no existe.\n¿Desea crearla?" % db_name,
                    cast(
                        QtWidgets.QMessageBox.StandardButtons,
                        QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No,
                    ),
                )
                if ret == QtWidgets.QMessageBox.No:
                    return None
                else:
                    try:
                        tmp_conn = self.getAlternativeConn(
                            db_name, db_host, db_port, db_user_name, db_password
                        )
                        if tmp_conn is not None:
                            self.set_last_error_null()
                            try:
                                if self._create_isolation:
                                    tmp_conn.connection.set_isolation_level(0)
                                tmp_conn.execute("CREATE DATABASE %s" % db_name)
                                if self._create_isolation:
                                    tmp_conn.connection.set_isolation_level(1)
                            except Exception as error:
                                self.set_last_error(str(error), "LOGGIN")

                                tmp_conn.execute("ROLLBACK")
                                tmp_conn.close()
                                return None

                            tmp_conn.close()
                            conn_ = self.getConn(
                                db_name, db_host, db_port, db_user_name, db_password
                            )

                    except Exception as error:
                        LOGGER.warning(error)
                        QtWidgets.QMessageBox.information(
                            QtWidgets.QWidget(),
                            "Pineboo",
                            "ERROR: No se ha podido crear la Base de Datos %s" % db_name,
                            QtWidgets.QMessageBox.Ok,
                        )
                        LOGGER.error("ERROR: No se ha podido crear la Base de Datos %s", db_name)
                        return None

        if conn_ is not None:
            # if settings.CONFIG.value("ebcomportamiento/orm_enabled", False):
            #    self._engine = self.getEngine(db_name, db_host, db_port, db_user_name, db_password)
            self._connection = conn_
            self.open_ = True
            # self.session()
        else:
            LOGGER.error("connect: %s", self.last_error())

        return conn_

    def setDBName(self, name: str) -> None:
        """Set DB Name."""

        self._dbname = name

    @decorators.not_implemented_warn
    def getAlternativeConn(
        self, name: str, host: str, port: int, usern: str, passw_: str
    ) -> Optional["base.Connection"]:
        """Return alternative connection."""

        return None  # pragma: no cover

    def getConn(
        self, name: str, host: str, port: int, usern: str, passw_: str, alternative=False
    ) -> Optional["base.Connection"]:
        """Return connection."""

        conn_ = None
        LOGGER.debug = LOGGER.trace  # type: ignore  # Send Debug output to Trace
        try:
            str_conn = self.loadConnectionString(name, host, port, usern, passw_)
            if str_conn in ENGINES.keys():
                LOGGER.info(
                    "Reusing engine %s:%s/%s to %s connection", host, port, name, self.db_._name
                )
                self._engine = ENGINES[str_conn]
            else:
                if alternative:
                    str_conn += self._extra_alternative

                self.get_common_params()
                self._engine = create_engine(str_conn, **self._queqe_params)
                if self._use_altenative_isolation_level:
                    event.listen(self._engine, "begin", self.do_begin)
                    event.listen(self._engine, "savepoint", self.do_savepoint)

                ENGINES[str_conn] = self._engine

            if application.SHOW_CONNECTION_EVENTS:
                self.listen_engine()

            conn_ = self.connection()

        except Exception as error:
            self.set_last_error(str(error), "CONNECT")
        return conn_

    def loadSpecialConfig(self) -> None:
        """Set special config."""

        pass  # pragma: no cover

    def version(self) -> str:
        """Return version number."""
        return self.version_

    def driverName(self) -> str:
        """Return driver name."""
        return self.name_

    def is_open(self) -> bool:
        """Return if the connection is open."""
        if hasattr(self, "_engine"):
            conn_ = self.connection()
            return not conn_.closed
        return False

    def pure_python(self) -> bool:
        """Return if the driver is python only."""
        return self.pure_python_

    def mobile(self) -> bool:
        """Return if the driver is mobile ready."""
        return self.mobile_

    def DBName(self) -> str:
        """Return database name."""
        return self._dbname

    def engine(self) -> Any:
        """Return sqlAlchemy ORM engine."""
        return self._engine

    def session(self) -> Tuple[str, "orm_session.Session"]:
        """Create a sqlAlchemy session."""
        while True:
            session_class = sessionmaker(
                bind=self.connection().execution_options(autocommit=True),
                autoflush=False,
                autocommit=True,
            )

            new_session = session_class()
            if new_session.connection().connection is not None:
                break
            else:
                LOGGER.warning("Conexión invalida capturada.Solicitando nueva")

        setattr(new_session, "_conn_name", self.db_._name)
        session_key = utils_base.session_id(self.db_._name, True)
        self.db_._conn_manager._thread_sessions[session_key] = new_session
        return (session_key, new_session)

    def connection(self) -> "base.Connection":
        """Return a cursor connection."""

        if self._connection is None or self._connection.closed:
            if getattr(self, "_engine", None):
                self._connection = self._engine.connect()
                if application.SHOW_CONNECTION_EVENTS:
                    event.listen(self._engine, "close", self.close_emited)
                    LOGGER.info("New connection created.\n%s", self._engine.pool.status())
            else:
                raise Exception("Engine is not loaded!")

        return self._connection

    def formatValueLike(self, type_: str, value: Any, upper: bool) -> str:
        """Return a string with the format value like."""

        util = flutil.FLUtil()
        res = "IS NULL"

        if type_ == "bool":
            value = str(value[0]).upper()
            if value == str(util.translate("application", "Sí")[0]).upper():
                res = "=%s" % self._like_true
            else:
                res = "=%s" % self._like_false

        elif type_ == "date":
            dateamd = util.dateDMAtoAMD(str(value))
            if dateamd is None:
                dateamd = ""
            res = self._text_like + "LIKE '%%" + dateamd + "'"

        elif type_ == "time":
            time_ = value.toTime()
            res = self._text_like + "LIKE '" + time_.toString(QtCore.Qt.ISODate) + "%%'"

        else:
            res = str(value)
            if upper:
                res = "%s" % res.upper()

            res = self._text_like + "LIKE '" + res + "%%'"

        return res

    def formatValue(self, type_: str, value: Any, upper: bool) -> Optional[Union[int, str, bool]]:
        """Return a string with the format value."""

        result_: Any = value

        if type_ in ("uint", "int", "double", "serial"):
            result_ = value or 0

        elif type_ in ("string", "stringlist", "timestamp"):
            if type_ == "string":
                value = utils_base.auto_qt_translate_text(value)
                if upper:
                    value = value.upper()

            result_ = "'%s'" % value or self._null

        elif type_ == "pixmap":
            result_ = "'%s'" % self.normalizeValue(value)

        elif type_ in ("bool", "unlock"):
            result_ = self._true if utils_base.text2bool(str(value)) else self._false

        elif type_ == "date":
            result_ = "'%s'" % str(flutil.FLUtil.dateDMAtoAMD(value))

        elif type_ == "time":
            if value:
                result_ = "'%s'" % value
            else:
                result_ = ""

        return str(result_)

    def canOverPartition(self) -> bool:
        """Return can override partition option ready."""
        return True

    def canRegenTables(self) -> bool:
        """Return if can regenerate tables."""
        return True

    def nextSerialVal(self, table_name: str, field_name: str) -> int:
        """Return next serial value."""

        table_max = 0
        flseq_max = 0
        res_ = 0
        sql = "SELECT MAX(%s) FROM %s WHERE 1=1" % (field_name, table_name)
        cur = self.execute_query(sql)
        if cur is not None:
            value = cur.fetchone()

            if value is not None:
                table_max = value[0] or 0

        sql = "SELECT seq FROM flseqs WHERE tabla = '%s' AND campo ='%s'" % (table_name, field_name)
        cur = self.execute_query(sql)
        if cur is not None:
            value = cur.fetchone()

            if value is not None:
                flseq_max = value[0] or 0

        res_ = flseq_max or table_max
        res_ += 1

        str_qry = ""
        if flseq_max:
            if res_ > flseq_max:
                str_qry = "UPDATE flseqs SET seq=%s WHERE tabla = '%s' AND campo = '%s'" % (
                    res_,
                    table_name,
                    field_name,
                )
        else:
            str_qry = "INSERT INTO flseqs (tabla,campo,seq) VALUES('%s','%s',%s)" % (
                table_name,
                field_name,
                res_,
            )

        if str_qry:
            try:
                self.execute_query(str_qry)
            except Exception as error:
                LOGGER.error("nextSerialVal: %s", str(error))
                self.session()[1].rollback()

        return res_

    def set_last_error_null(self) -> None:
        """Set lastError flag Null."""
        self._last_error = ""

    def set_last_error(self, text: str, command: str) -> None:
        """Set last error."""
        self._last_error = "%s (%s)" % (text, command)
        LOGGER.error(self._last_error)

    def last_error(self) -> str:
        """Return last error."""
        return self._last_error

    @decorators.not_implemented_warn
    def setType(self, type_: str, leng: int = 0) -> str:
        """Return type definition."""
        return ""  # pragma: no cover

    def existsTable(self, table_name: str) -> bool:
        """Return if exists a table specified by name."""

        if self._engine:
            self.set_last_error_null()
            table_list = self.tables("", table_name)
            if self.last_error():
                raise Exception("Error loading tables.")

            return table_name in table_list
        else:
            raise Exception("No engine or connection exists!")

    def is_valid_view(
        self, metadata: "pntablemetadata.PNTableMetaData", qry: "pnsqlquery.PNSqlQuery"
    ) -> bool:
        """Return if a view is valid."""

        valid = True
        if qry.select().find(".*") > -1:
            LOGGER.warning("the use of * is not allowed")
            valid = False
        else:
            meta_field_names = metadata.fieldNames()
            select_text = qry.select()
            for field_name in meta_field_names:
                if field_name not in select_text:
                    valid = False
                    LOGGER.warning(
                        "Field name %s not found on query select (%s)", field_name, select_text
                    )
                    break

        return valid

    def sqlCreateView(self, meta: "pntablemetadata.PNTableMetaData") -> str:
        """Return a sql create view."""

        sql = ""
        qry = pnsqlquery.PNSqlQuery(meta.name())
        if qry.select() and qry.from_():
            if self.is_valid_view(meta, qry):
                sql = "CREATE VIEW %s AS SELECT %s FROM %s" % (
                    meta.name(),
                    qry.select() or "*",
                    qry.from_(),
                )
        else:
            LOGGER.warning("sqlCreateView: %s.qry is empty or does not exists", meta.name())

        return sql

    @decorators.not_implemented_warn
    def sqlCreateTable(
        self, tmd: "pntablemetadata.PNTableMetaData", create_index: bool = True
    ) -> Optional[str]:
        """Return a create table query."""
        return ""  # pragma: no cover

    def mismatchedTable(self, table_name: str, metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Return if a table is mismatched."""

        ret = False

        dict_database: Dict[str, List[Any]] = dict(
            [
                [rec_d[0], rec_d]  # type: ignore [misc] # noqa: F821
                for rec_d in self.recordInfo2(table_name)
            ]
        )

        if metadata.isQuery():
            if application.USE_MISMATCHED_VIEWS:
                qry = pnsqlquery.PNSqlQuery(table_name)
                names = qry.select().split(",")
                if not len(metadata.fieldNames()):
                    return False

                for name in names:
                    field_name = name.split(".")[1] if name.find(".") > -1 else name
                    if field_name not in dict_database.keys():
                        return True
            else:
                return False

        else:
            dict_metadata: Dict[str, List[Any]] = dict(
                [
                    [rec_m[0], rec_m]  # type: ignore [misc] # noqa: F821
                    for rec_m in self.recordInfo(metadata)
                ]
            )

            if len(dict_metadata.keys()) != len(dict_database.keys()):
                ret = True
            else:
                for name, meta in dict_metadata.items():
                    if (
                        name in dict_database.keys()
                    ):  # si falla una key, los campos en el metadata y database no son los mismos.
                        if self.notEqualsFields(dict_database[name], meta, metadata.isQuery()):
                            LOGGER.warning(
                                "Mismatched field %s.%s:\nMetadata : %s.\nDataBase : %s\n",
                                table_name,
                                name,
                                meta,
                                dict_database[name],
                            )
                            ret = True
                            break
                        else:
                            del dict_database[
                                name
                            ]  # dict_database mas peuqeño cada vez, para comparar mas rápido
                    else:
                        LOGGER.warning("Field %s not found in database", name)
                        ret = True
                        break

                # if not ret and dict_database:
                #    LOGGER.warning("Fields %s not found in metadata", dict_database)
                #    ret = True

        return ret

    @decorators.not_implemented_warn
    def recordInfo2(self, tablename: str) -> List[List[Any]]:
        """Return info from a database table."""
        return []  # pragma: no cover

    def recordInfo(self, table_metadata: "pntablemetadata.PNTableMetaData") -> List[list]:
        """Obtain current cursor information on columns."""

        return [
            [
                field.name(),
                field.type(),
                not field.allowNull(),
                field.length(),
                field.partDecimal(),
                field.defaultValue(),
                field.isPrimaryKey(),
            ]
            for field in table_metadata.fieldList()
        ]

    @decorators.not_implemented_warn
    def decodeSqlType(self, type_: str) -> str:
        """Return the specific field type."""
        return ""  # pragma: no cover

    def notEqualsFields(self, field_db: List[Any], field_meta: List[Any], is_query=False) -> bool:
        """Return if a field has changed."""
        # 0 name,
        # 1 type,
        # 2 allow_null,
        # 3 length,
        # 4 part_decimal,
        # 5 default_value,
        # 6 is_primary_key

        ret = False
        try:
            if field_db[2] != field_meta[2] and not is_query:  # nulos
                if field_meta[1] == "serial":
                    pass

                else:
                    if (
                        not field_meta[2] and field_meta[6]
                    ):  # Si en meta , nulo false y pk , dejamos pasar
                        pass
                    else:
                        ret = True

            if not ret:
                db_type = field_db[1]
                meta_type = field_meta[1]

                if db_type == "string":
                    if meta_type == "string":
                        if field_db[3] not in [field_meta[3], 0, 255]:
                            ret = True
                    elif meta_type not in ("string", "time", "date"):
                        ret = True

                elif db_type == "uint" and meta_type not in ("int", "uint", "serial"):
                    ret = True
                elif db_type == "bool" and meta_type not in ("bool", "unlock"):
                    ret = True
                elif db_type == "double" and meta_type != "double":
                    ret = True
                elif db_type == "stringlist" and meta_type not in (
                    "stringlist",
                    "pixmap",
                    "string",
                ):
                    ret = True
                elif db_type == "timestamp" and meta_type != "timestamp":
                    ret = True

        except Exception as error:
            LOGGER.error("notEqualsFields %s %s (%s)", field_db, field_meta, str(error))

        # if ret:
        #    LOGGER.warning("Falla database: %s, metadata: %s", field_db, field_meta)

        return ret

    @decorators.not_implemented_warn
    def tables(self, type_name: str = "", table_name: str = "") -> List[str]:
        """Return a tables list specified by type."""
        return []  # pragma: no cover

    def normalizeValue(self, text: str) -> str:
        """Return a database friendly text."""

        res = str(text).replace("'", "''")
        if self._parse_porc:
            res = res.replace("%", "%%")
        # res = res.replace(":", "\\:")
        return res

    def hasCheckColumn(self, metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Retrieve if MTD has a check column."""

        for field in metadata.fieldList():
            if field.isCheck() or field.name().endswith("_check_column"):
                return True

        return False

    @decorators.not_implemented_warn
    def constraintExists(self, name: str) -> bool:
        """Return if constraint exists specified by name."""
        return False  # pragma: no cover

    def remove_index(self, metadata: "pntablemetadata.PNTableMetaData", cursor: Any) -> bool:
        """Remove olds index."""

        return True

    def alterTable(self, new_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Modify a table structure."""

        if self.hasCheckColumn(new_metadata):
            return False

        field_list = new_metadata.fieldList()
        if not field_list:
            return False

        util = flutil.FLUtil()
        table_name = new_metadata.name()

        old_columns_info = self.recordInfo2(table_name)
        old_field_names: List[str] = [old_column[0] for old_column in old_columns_info]

        renamed_table = "%salteredtable%s" % (
            table_name,
            QtCore.QDateTime().currentDateTime().toString("ddhhssz"),
        )

        query = pnsqlquery.PNSqlQuery(None, "dbAux")

        session_ = query.db().session()
        query.db().transaction()

        if new_metadata.isQuery():
            if table_name in self.tables("Views"):
                query.exec_("DROP VIEW %s %s" % (table_name, self._text_cascade))
            elif table_name in self.tables("Tables"):
                query.exec_("DROP TABLE %s %s" % (table_name, self._text_cascade))

        else:
            if table_name not in self.tables("Tables"):
                LOGGER.warning(
                    "El metadata indica erroneamente, que %s es una tabla. Proceso cancelado.",
                    table_name,
                )
                session_.rollback()
                return False

            if not self.remove_index(new_metadata, query):
                session_.rollback()
                return False

            if not query.exec_("ALTER TABLE %s RENAME TO %s" % (table_name, renamed_table)):
                session_.rollback()
                return False

        if not self.db_.createTable(new_metadata):
            session_.rollback()
            return False

        if new_metadata.isQuery():
            session_.commit()
            return True

        cur = query.db().execute_query(
            "SELECT %s FROM %s WHERE 1=1" % (", ".join(old_field_names), renamed_table)
        )
        old_data_list = cur.fetchall() if cur else []
        # old_cursor = pnsqlcursor.PNSqlCursor(renamed_table, True, "dbAux")
        # old_cursor.setModeAccess(old_cursor.Browse)
        # old_cursor.select()
        util.createProgressDialog(
            util.translate("application", "Reestructurando registros para %s...")
            % new_metadata.alias(),
            len(old_data_list),
        )

        util.setLabelText(util.translate("application", "Tabla modificada"))

        new_field_names: List[str] = new_metadata.fieldNames()

        list_records = []
        for number_progress, old_data in enumerate(old_data_list):
            new_buffer = []

            for new_idx, new_name in enumerate(new_field_names):
                new_field = new_metadata.field(new_name)
                if new_field is None:
                    LOGGER.warning(
                        "Field %s not found un metadata %s" % (new_name, new_metadata.name())
                    )
                    session_.rollback()

                    return False
                value = None
                if new_name in old_field_names:
                    value = old_data[old_field_names.index(new_name)]
                    if value is None:
                        continue
                elif not new_field.allowNull():
                    value = new_field.defaultValue()
                    if value is None:
                        if new_field.type() == "timestamp":
                            value = self.getTimeStamp()
                        else:
                            continue
                else:
                    continue
                new_buffer.append([new_field, value])

            list_records.append(new_buffer)

            util.setProgress(number_progress)

        util.destroyProgressDialog()
        if not self.insertMulti(table_name, list_records):
            session_.rollback()
            return False
        else:

            session_.commit()

        if new_metadata.name() not in self.tables("Views"):
            query.exec_("DROP TABLE %s %s" % (renamed_table, self._text_cascade))

        return True

    def cascadeSupport(self) -> bool:
        """Return True if the driver support cascade."""
        return True

    def canDetectLocks(self) -> bool:
        """Return if can detect locks."""
        return True

    # def fix_query(self, val: str) -> str:
    #    """Fix values on SQL."""
    #    ret_ = val.replace("'true'", "1")
    #    ret_ = ret_.replace("'false'", "0")
    #    ret_ = ret_.replace("'0'", "0")
    #    ret_ = ret_.replace("'1'", "1")
    #    return ret_

    # def desktopFile(self) -> bool:
    #    """Return if use a file like database."""
    #    return self.desktop_file

    def execute_query(self, query: str) -> Optional["result.ResultProxy"]:
        """Excecute a query and return result."""

        if not self.is_open():
            raise Exception("execute_query: Database not open %s", self)

        self.set_last_error_null()
        session_ = self.db_.session()
        result_ = None
        try:
            try:
                if query.find("::bytea") > -1:
                    result_ = (  # Esto es necesario para no obtener error en la consulta con los bytearray
                        session_.connection()
                        .execution_options(autocommit=True)
                        .execute("""%s""" % query)
                    )
                else:
                    result_ = session_.execute(text("""%s""" % query))
            except sqlalchemy.exc.DBAPIError as error:
                LOGGER.warning(
                    "Se ha producido un error DBAPI con la consulta %s. Ejecutando rollback necesario",
                    query,
                    stack_info=True,
                )
                session_.rollback()
                self.set_last_error(
                    "No se pudo ejecutar la query %s.\n%s" % (query, str(error)), query
                )

        except Exception as error:
            LOGGER.warning(
                "Se ha producido un error al ejecutar la consulta %s.\n%s\nSTACK APP: %s\nSTACK ERROR: %s",
                query,
                str(error),
                "".join(traceback.format_exc(limit=None)),
                "".join(traceback.format_stack(limit=None)),
            )
            self.set_last_error("No se pudo ejecutar la query %s.\n%s" % (query, str(error)), query)

        return result_

    def getTimeStamp(self) -> str:
        """Return TimeStamp."""

        sql = "SELECT CURRENT_TIMESTAMP"

        cur = self.execute_query(sql)

        time_stamp_: Any = cur.fetchone() if cur else None

        if time_stamp_ is None:
            raise Exception("timestamp is empty!")

        return time_stamp_[0]

    def close_emited(self, *args):
        """."""
        pass
        # LOGGER.warning("** %s, %s", self, args)

    def insertMulti(
        self, table_name: str, list_records: Iterable = []
    ) -> bool:  # FIXME SQLITE NO PUEDE TODAS DE GOLPE
        """Insert several rows at once."""

        model_ = qsadictmodules.QSADictModules.from_project("%s_orm" % table_name)
        session_ = self.db_.connManager().dbAux().session()
        if not model_:
            return False

        for number, line in enumerate(list_records):
            # model_obj = model_()
            field_names = []
            field_values = []
            for field, value in line:
                if field.generated():

                    if field.type() in ("string", "stringlist", "bytearray"):
                        value = self.normalizeValue(value)

                        if value in ["Null", "NULL"]:
                            value = "''"
                        else:
                            value = self.formatValue(field.type(), value, False)
                    else:
                        value = self.formatValue(field.type(), value, False)

                # setattr(model_obj, field.name(), value)
                field_names.append(field.name())
                field_values.append(value)

            sql = None
            if field_names:
                sql = """INSERT INTO %s(%s) values (%s)""" % (
                    table_name,
                    ", ".join(field_names),
                    ", ".join(map(str, field_values)),
                )

            if sql:
                try:
                    session_.connection().execute(sql)
                except Exception as error:
                    LOGGER.error("insertMulti: %s", str(error))
                    return False
        session_.flush()
        return True

    def Mr_Proper(self) -> None:
        """Clear all garbage data."""

        util = flutil.FLUtil()
        conn_dbaux = self.db_.connManager().dbAux()

        multi_fllarge = False
        fllarge_tables_list: List[str] = []
        fllarge_to_delete: Dict[str, List[str]] = {}
        sql = "SELECT valor FROM flsettings WHERE flkey=%s" % self.formatValue(
            "string", "FLLargeMode", False
        )
        cursor = conn_dbaux.execute_query(sql)
        try:
            result_ = cursor.fetchone()
            if result_:
                multi_fllarge = utils_base.text2bool(str(result_[0]))
        except Exception as error:
            LOGGER.warning("Mr_Proper: %s" % str(error))

        if not multi_fllarge:
            fllarge_tables_list.append("fllarge")

        tables = self.db_.tables("Tables")
        altered_tables = []
        for table_name in tables:
            if table_name.find("alteredtable") > -1:
                altered_tables.append(table_name)
            elif multi_fllarge and table_name.startswith("fllarge_"):
                fllarge_tables_list.append(table_name)

        LOGGER.debug(
            "Tablas fllarge. Modo multiple: %s Lista : %s sql : %s",
            multi_fllarge,
            fllarge_tables_list,
            sql,
        )

        util.createProgressDialog(
            util.translate("application", "Revisando tablas fllarge"), len(fllarge_tables_list)
        )

        for number, table_fllarge in enumerate(fllarge_tables_list):
            util.setLabelText(util.translate("application", "Revisando tabla %s" % table_fllarge))

            sql = "SELECT refkey FROM %s WHERE 1 = 1" % table_fllarge
            cursor = conn_dbaux.execute_query(sql)
            old_target = ""
            metadata_target = None

            for line in list(cursor):

                target = line[0].split("@")[1]
                found = False
                if target != old_target:
                    metadata_target = self.db_.connManager().manager().metadata(target)
                    old_target = target

                if metadata_target is None:
                    LOGGER.warning("Error limpiando fllarge: %s no tiene un metdata válido", target)
                    return
                else:
                    for field in metadata_target.fieldList():
                        if found:
                            break
                        if field.type() == "pixmap":
                            sql = "SELECT %s FROM %s WHERE 1 = 1" % (
                                field.name(),
                                target,
                            )  # 1 a 1 , si busco especifico me da problemas mssql

                            cursor_finder = conn_dbaux.execute_query(sql)
                            for result_finder in list(cursor_finder):
                                if result_finder[0] == line[0]:
                                    found = True
                                    break

                    if not found:
                        if table_fllarge not in fllarge_to_delete.keys():
                            fllarge_to_delete[table_fllarge] = []
                        fllarge_to_delete[table_fllarge].append(line[0])

            util.setProgress(number)

        util.destroyProgressDialog()

        util.createProgressDialog(
            util.translate("application", "Limpiando tablas fllarge"), len(fllarge_to_delete)
        )
        for number, key in enumerate(fllarge_to_delete.keys()):
            for ref_key in fllarge_to_delete[key]:
                LOGGER.debug("Eliminado %s.%s", key, ref_key)
                util.setLabelText(util.translate("application", "Limpiando tabla fllarge %s" % key))
                sql = "DELETE FROM %s WHERE refkey = %s" % (
                    key,
                    self.formatValue("string", ref_key, False),
                )
                conn_dbaux.execute_query(sql)

            util.setProgress(number)

        util.destroyProgressDialog()

        conn_dbaux.transaction()

        # query = pnsqlquery.PNSqlQuery(None,conn_dbaux)
        cursor = conn_dbaux.execute_query(
            "SELECT nombre FROM flfiles WHERE nombre "
            + self.formatValueLike("string", "%%.mtd", False)
        )
        list_mtds = []
        try:
            for data in list(cursor):
                list_mtds.append(data[0])
        except Exception as error:
            LOGGER.error("Mr_Proper: %s", error)

        reg_exp = re.compile("^.*\\d{6,9}$")
        bad_list_mtds = list(filter(reg_exp.match, list_mtds))

        util.createProgressDialog(
            util.translate("application", "Borrando backups"), len(bad_list_mtds)
        )

        for number, mtd_name in enumerate(bad_list_mtds):
            util.setLabelText(util.translate("application", "Borrando registro %s" % mtd_name))
            conn_dbaux.execute_query("DELETE FROM flfiles WHERE nombre ='%s'" % mtd_name)
            util.setProgress(number)

        util.setTotalSteps(len(altered_tables))

        for number, altered_table_name in enumerate(altered_tables):
            util.setLabelText(
                util.translate("application", "Borrando registro %s" % altered_table_name)
            )
            if self.existsTable(altered_table_name):
                util.setLabelText(
                    util.translate("application", "Borrando tabla %s" % altered_table_name)
                )
                conn_dbaux.execute_query(
                    "DROP TABLE %s %s" % (altered_table_name, self._text_cascade)
                )

            util.setProgress(number)

        util.destroyProgressDialog()

        tables = self.db_.tables("Tables")

        util.createProgressDialog(
            util.translate("application", "Comprobando base de datos"), len(tables) + 2
        )
        for number, table_name in enumerate(tables):
            util.setLabelText(util.translate("application", "Comprobando tabla %s" % table_name))
            metadata = conn_dbaux.connManager().manager().metadata(table_name)
            if metadata is not None:
                if self.mismatchedTable(table_name, metadata):
                    if metadata:
                        msg = util.translate(
                            "application",
                            "La estructura de los metadatos de la tabla '%s' y su "
                            "estructura interna en la base de datos no coinciden. "
                            "Intentando regenerarla." % table_name,
                        )

                        LOGGER.warning(msg)
                        self.alterTable(metadata)

            util.setProgress(number)

        util.destroyProgressDialog()
        self.checkSequences()

        util.createProgressDialog(util.translate("application", "Comprobando base de datos"), 4)
        util.setLabelText(util.translate("application", "Borrando flmetadata"))
        util.setProgress(1)
        conn_dbaux.execute_query("DELETE FROM flmetadata")
        util.setLabelText(util.translate("application", "Borrando flvar"))
        util.setProgress(2)
        conn_dbaux.execute_query("DELETE FROM flvar")
        conn_dbaux.connManager().manager().cleanupMetaData()
        conn_dbaux.commit()

        util.setLabelText(util.translate("application", "Vacunando base de datos"))
        util.setProgress(3)
        self.vacuum()

        util.setProgress(4)
        util.destroyProgressDialog()

    def vacuum(self):
        """Vacuum tables."""

        # self._connection.connection.set_isolation_level(0)
        self.execute_query("vacuum")
        # self._connection.connection.set_isolation_level(1)

    def sqlLength(self, field_name: str, size: int) -> str:
        """Return length formated."""

        return "LENGTH(%s)=%s" % (field_name, size)

    def checkSequences(self) -> None:
        """Check sequences."""

        return

    def regenTable(self, table_name: str, new_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Regenerate tables."""

        must_alter = self.mismatchedTable(table_name, new_metadata)

        if must_alter:
            must_alter = self.alterTable(new_metadata)

            if must_alter:
                conn_dbaux = self.db_.connManager().dbAux()
                reg_exp = re.compile("^.*\\d{6,9}$")
                bad_list_tables = list(filter(reg_exp.match, self.db_.tables("Tables")))

                sql = "SELECT nombre FROM flfiles WHERE nombre%s" % self.formatValueLike(
                    "string", "%%alteredtable", False
                )
                cursor = conn_dbaux.execute_query(sql)
                for name in cursor:
                    sql = "DELETE FROM flfiles WHERE nombre ='%s'" % name
                    conn_dbaux.execute_query(sql)
                    if name.find("alteredtable") > -1 and self.existsTable(
                        name.replace(".mtd", "")
                    ):
                        conn_dbaux.execute_query(
                            "DROP TABLE %s %s" % (name.replace(".mtd", ""), self._text_cascade)
                        )

                for bad_table in bad_list_tables:
                    if self.existsTable(bad_table):
                        conn_dbaux.execute_query(
                            "DROP TABLE %s %s" % (bad_table, self._text_cascade)
                        )

                conn_dbaux.commit()

        return must_alter

    @classmethod
    def close_connection_warning(cls, dbapi_connection, connection_record=None) -> None:
        """Show connection closed message."""
        if application.SHOW_CONNECTION_EVENTS:
            LOGGER.warning(
                "The connection was closed: connection: %s, record : %s !!",
                dbapi_connection,
                connection_record,
            )

    def get_common_params(self) -> None:
        """Load common params."""

        self._queqe_params["encoding"] = "UTF-8"
        mng_ = self.db_.connManager()
        limit_conn = mng_.limit_connections
        if limit_conn > 0:
            LOGGER.info("SqlAlchemy pool enabled")
            self._queqe_params["poolclass"] = pool.QueuePool
            self._queqe_params["pool_size"] = limit_conn
            self._queqe_params["max_overflow"] = int(limit_conn + 10)
            if mng_.safe_mode_level in [4, 5]:
                self._queqe_params["pool_pre_ping"] = True
            if mng_.connections_time_out:
                self._queqe_params["pool_timeout"] = int(mng_.connections_time_out)

        else:
            LOGGER.info("SqlAlchemy pool disabled")
            self._queqe_params["poolclass"] = pool.NullPool

        if application.LOG_SQL:
            self._queqe_params["echo"] = True
            if limit_conn > 0:
                self._queqe_params["echo_pool"] = True

        for key, value in self._queqe_params.items():
            LOGGER.info("    * %s = %s", key, value)

    def listen_engine(self) -> None:
        """Listen engine events."""

        event.listen(self._engine, "close_detached", self.close_connection_warning)
        event.listen(self._engine, "close", self.close_connection_warning)

    def do_begin(self, conn):
        """Begin event."""

        conn.exec_driver_sql("BEGIN")

    def do_savepoint(self, conn, name):
        """Save point event."""

        self._sp_level += 1
        name = "sp_%s" % self._sp_level
        conn.exec_driver_sql("SAVEPOINT %s" % name)
