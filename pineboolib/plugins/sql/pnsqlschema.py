"""PNSqlSchema module."""

from PyQt5 import QtCore, QtWidgets

from pineboolib import logging, application

from pineboolib.core.utils import utils_base
from pineboolib.application.utils import check_dependencies

import traceback
from typing import Iterable, Optional, Union, List, Any, Dict, cast, TYPE_CHECKING
from pineboolib.core import settings, decorators

from pineboolib.fllegacy import flutil

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401


LOGGER = logging.get_logger(__name__)


class PNSqlSchema(object):
    """PNSqlSchema class."""

    version_: str
    conn_: Any
    name_: str
    alias_: str
    errorList: List[str]
    lastError_: str
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
    open_: bool
    desktop_file: bool
    savepoint_command: str
    rollback_savepoint_command: str
    rollback_transaction_command: str
    commit_transaction_command: str
    transaction_command: str
    release_savepoint_command: str
    _true: Any
    _false: Any
    _like_true: Any
    _like_false: Any
    _null: str
    _text_like: str
    _safe_load: Dict[str, str]
    _database_not_found_keywords: List[str]

    def __init__(self):
        """Inicialize."""
        self.version_ = ""
        self.name_ = ""
        self.conn_ = None
        self.errorList = []
        self.alias_ = ""
        self._dbname = ""
        self.mobile_ = False
        self.pure_python_ = False
        self.defaultPort_ = 0
        self.engine_ = None
        self.session_ = None
        self.declarative_base_ = None
        self.lastError_ = ""
        self.db_ = None
        self.rows_cached = {}
        self.open_ = False
        self.desktop_file = False
        self.savepoint_command = "SAVEPOINT"
        self.rollback_savepoint_command = "ROLLBACK TRANSACTION TO SAVEPOINT"
        self.commit_transaction_command = "END TRANSACTION"
        self.rollback_transaction_command = "ROLLBACK TRANSACTION"
        self.transaction_command = "BEGIN TRANSACTION"
        self.release_savepoint_command = "RELEASE SAVEPOINT"
        self._true = "1"
        self._false = "0"
        self._like_true = "1"
        self._like_false = "0"
        self._null = "Null"
        self._text_like = "::text "
        self._safe_load = {}
        self._database_not_found_keywords = ["does not exist", "no existe"]
        # self.sql_query = {}
        # self.cursors_dict = {}

    def safe_load(self, exit: bool = False) -> bool:
        """Return if the driver can loads dependencies safely."""
        return check_dependencies.check_dependencies(self._safe_load, exit)

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_user_name: str, db_password: str
    ) -> Any:
        """Connect to database."""

        self.setDBName(db_name)
        self.safe_load(True)
        LOGGER.debug = LOGGER.trace  # type: ignore  # Send Debug output to Trace
        self.conn_ = self.getConn(db_name, db_host, db_port, db_user_name, db_password)
        print("*", self.conn_)
        if self.conn_ is None:  # Si no existe la conexión
            if application.PROJECT._splash:
                application.PROJECT._splash.hide()
            if not application.PROJECT.DGI.localDesktop():
                return False

            last_error = self.lastError()
            found = False
            for key in self._database_not_found_keywords:
                if key in last_error:
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
                    return False
                else:
                    try:
                        tmp_conn = self.getAlternativeConn(
                            db_name, db_host, db_port, db_user_name, db_password
                        )
                        if tmp_conn is not None:
                            tmp_cursor = tmp_conn.cursor()
                            try:
                                tmp_cursor.execute("CREATE DATABASE %s" % db_name)
                            except Exception as error:
                                self.setLastError(str(error), "LOGGIN")
                                tmp_cursor.execute("ROLLBACK")
                                tmp_cursor.close()
                                return False

                            tmp_cursor.close()
                            self.conn_ = self.getConn(
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
                        return False

        if self.conn_ is not None:
            if settings.CONFIG.value("ebcomportamiento/orm_enabled", False):
                self.engine_ = self.getEngine(db_name, db_host, db_port, db_user_name, db_password)

            self.open_ = True
            self.loadSpecialConfig()

        return self.conn_

    def setDBName(self, name: str) -> None:
        """Set DB Name."""

        self._dbname = name

    @decorators.not_implemented_warn
    def getConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        return None

    @decorators.not_implemented_warn
    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        return None

    @decorators.not_implemented_warn
    def getEngine(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        return ""

    @decorators.not_implemented_warn
    def loadSpecialConfig(self) -> None:
        """Set special config."""

        pass

    def version(self) -> str:
        """Return version number."""
        return self.version_

    def driverName(self) -> str:
        """Return driver name."""
        return self.name_

    def isOpen(self) -> bool:
        """Return if the connection is open."""
        try:
            cur = self.conn_.cursor()
            cur.execute("select 1")
        except Exception as exc_:
            LOGGER.error("raise an exception %s", exc_)
            return False

        return True

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
        return self.engine_

    def session(self) -> Any:
        """Create a sqlAlchemy session."""
        if settings.CONFIG.value("ebcomportamiento/orm_enabled", False) and self.session_ is None:
            from sqlalchemy.orm import sessionmaker  # type: ignore

            Session = sessionmaker(bind=self.engine())
            self.session_ = Session()

        return self.session_

    def declarative_base(self) -> Any:
        """Return sqlAlchemy declarative base."""
        if (
            settings.CONFIG.value("ebcomportamiento/orm_enabled", False)
            and self.declarative_base_ is None
        ):
            from sqlalchemy.ext.declarative import declarative_base  # type: ignore

            self.declarative_base_ = declarative_base()

        return self.declarative_base_

    def formatValueLike(self, type_: str, v: Any, upper: bool) -> str:
        """Return a string with the format value like."""
        util = flutil.FLUtil()
        res = "IS NULL"

        if type_ == "bool":
            s = str(v[0]).upper()
            if s == str(util.translate("application", "Sí")[0]).upper():
                res = "=%s" % self._like_true
            else:
                res = "=%s" % self._like_false

        elif type_ == "date":
            dateamd = util.dateDMAtoAMD(str(v))
            if dateamd is None:
                dateamd = ""
            res = self._text_like + "LIKE '%%" + dateamd + "'"

        elif type_ == "time":
            t = v.toTime()
            res = self._text_like + "LIKE '" + t.toString(QtCore.Qt.ISODate) + "%%'"

        else:
            res = str(v)
            if upper:
                res = "%s" % res.upper()

            res = self._text_like + "LIKE '" + res + "%%'"

        return res

    def formatValue(self, type_: str, v: Any, upper: bool) -> Optional[Union[int, str, bool]]:
        """Return a string with the format value."""
        util = flutil.FLUtil()

        s: Any = None

        # if v is None:
        #    return "NULL"

        if type_ == "pixmap":
            if v.find("'") > -1:
                s = "'%s'" % self.normalizeValue(v)
            else:
                s = "'%s'" % v

        elif type_ in ("bool", "unlock"):
            if isinstance(v, bool):
                s = self._true if v else self._false
            else:
                s = self._true if utils_base.text2bool(v) else self._false

        elif type_ == "date":
            if len(str(v).split("-")[0]) < 3:
                date_ = str(util.dateDMAtoAMD(v))
            else:
                date_ = "%s" % v

            s = "'%s'" % date_

        elif type_ == "time":
            s = "'%s'" % v if v else ""

        elif type_ in ("uint", "int", "double", "serial"):
            s = v or 0

        elif type_ in ("string", "stringlist", "timestamp"):
            if not v:
                s = self._null
            else:
                if type_ == "string":
                    v = utils_base.auto_qt_translate_text(v)
                    if upper:
                        v = v.upper()

            s = "'%s'" % v
        else:
            s = v

        return str(s)

    def canOverPartition(self) -> bool:
        """Return can override partition option ready."""
        return True

    def canRegenTables(self) -> bool:
        """Return if can regenerate tables."""
        return True

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Return next serial value."""

        return None

    def savePoint(self, number: int) -> bool:
        """Set a savepoint."""
        if not self.isOpen():
            LOGGER.warning("savePoint: Database not open")
            return False

        if not number:
            return True

        self.set_last_error_null()

        cursor = self.cursor()
        try:
            LOGGER.debug("Creando savepoint sv_%s" % number)
            cursor.execute("%s sv_%s" % (self.savepoint_command, number))
        except Exception:
            self.setLastError("No se pudo crear punto de salvaguarda", "SAVEPOINT sv_%s" % number)
            LOGGER.error(
                "%s:: No se pudo crear punto de salvaguarda SAVEPOINT sv_%s", __name__, number
            )
            return False

        return True

    def canSavePoint(self) -> bool:
        """Return if can do save point."""
        return True

    def canTransaction(self) -> bool:
        """Return if can do transaction."""
        return True

    def rollbackSavePoint(self, number: int) -> bool:
        """Set rollback savepoint."""
        if not number:
            return True

        if not self.isOpen():
            LOGGER.warning("rollbackSavePoint: Database not open")
            return False

        self.set_last_error_null()

        cursor = self.cursor()
        try:
            cursor.execute("%s sv_%s" % (self.rollback_savepoint_command, number))
        except Exception:
            self.setLastError(
                "No se pudo rollback a punto de salvaguarda",
                "ROLLBACK TO SAVEPOINTt sv_%s" % number,
            )
            LOGGER.error(
                "%s:: No se pudo rollback a punto de salvaguarda ROLLBACK TO SAVEPOINT sv_%s",
                __name__,
                number,
            )
            return False

        return True

    def set_last_error_null(self) -> None:
        """Set lastError flag Null."""
        self.lastError_ = ""

    def setLastError(self, text: str, command: str) -> None:
        """Set last error."""
        self.lastError_ = "%s (%s)" % (text, command)

    def lastError(self) -> str:
        """Return last error."""
        return self.lastError_

    def commitTransaction(self) -> bool:
        """Set commit transaction."""
        if not self.isOpen():
            LOGGER.warning("%s::commitTransaction: Database not open", __name__)
            return False

        self.set_last_error_null()
        cursor = self.cursor()
        try:
            cursor.execute("%s" % self.commit_transaction_command)
        except Exception:
            self.setLastError("No se pudo aceptar la transacción", "COMMIT")
            LOGGER.error("%s:: No se pudo aceptar la transacción COMMIT.", __name__)
            return False

        return True

    def rollbackTransaction(self) -> bool:
        """Set a rollback transaction."""

        # if not self.isOpen():
        #    LOGGER.warning("%s::rollbackTransaction: Database not open", __name__)
        #    return False

        self.set_last_error_null()
        cursor = self.cursor()
        try:
            cursor.execute("%s" % self.rollback_transaction_command)
        except Exception:
            self.setLastError("No se pudo deshacer la transacción", "ROLLBACK")
            LOGGER.error("%s:: No se pudo deshacer la transacción ROLLBACK", __name__)
            return False

        return True

    def transaction(self) -> bool:
        """Set a new transaction."""
        if not self.isOpen():
            LOGGER.warning("%s::transaction: Database not open", __name__)
            return False

        cursor = self.cursor()
        self.set_last_error_null()

        try:
            cursor.execute("%s" % self.transaction_command)
        except Exception:
            self.setLastError("No se pudo crear la transacción", "BEGIN")
            LOGGER.error("%s:: No se pudo crear la transacción BEGIN", __name__)
            return False

        return True

    def releaseSavePoint(self, number: int) -> bool:
        """Set release savepoint."""

        if not self.isOpen():
            LOGGER.warning("%s::releaseSavePoint: Database not open", __name__)
            return False

        if not number:
            return True

        self.set_last_error_null()

        cursor = self.cursor()
        try:
            cursor.execute("%s sv_%s" % (self.release_savepoint_command, number))
        except Exception:
            self.setLastError(
                "No se pudo release a punto de salvaguarda", "RELEASE SAVEPOINT sv_%s" % number
            )
            LOGGER.error(
                "%s:: No se pudo release a punto de salvaguarda RELEASE SAVEPOINT sv_%s",
                __name__,
                number,
            )
            return False

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

        if db_ is None:
            db_ = self.db_

        if isinstance(tmd_or_table2, str):
            mtd = db_.connManager().manager().metadata(tmd_or_table2, True)
            if not mtd:
                return False

            mismatch = False
            processed_fields = []
            try:
                rec_mtd = self.recordInfo(tmd_or_table2)
                rec_db = self.recordInfo2(table1)
                # fieldBd = None
                if rec_mtd is None:
                    raise ValueError("recordInfo no ha retornado valor")

                for field_mtd in rec_mtd:
                    # fieldBd = None
                    found = False
                    for field_db in rec_db:
                        if field_db[0] == field_mtd[0]:
                            processed_fields.append(field_db[0])
                            found = True
                            if self.notEqualsFields(field_db, field_mtd):

                                mismatch = True

                            rec_db.remove(field_db)
                            break

                    if not found:
                        if field_mtd[0] not in processed_fields:
                            mismatch = True
                            break

                if len(rec_db) > 0:
                    mismatch = True

            except Exception:
                LOGGER.error(traceback.format_exc())

            return mismatch

        else:
            return self.mismatchedTable(table1, tmd_or_table2.name(), db_)

    def recordInfo2(self, tablename: str) -> List[List[Any]]:
        """Return info from a database table."""
        return []

    def decodeSqlType(self, type_: str) -> str:
        """Return the specific field type."""
        return ""

    def recordInfo(self, tablename_or_query: str) -> List[list]:
        """Obtain current cursor information on columns."""
        if not self.isOpen():
            raise Exception("recordInfo: conn not opened")
        if not self.db_:
            raise Exception("recordInfo: Must be connected")
        info = []
        util = flutil.FLUtil()

        if isinstance(tablename_or_query, str):
            tablename = tablename_or_query

            stream = self.db_.connManager().managerModules().contentCached("%s.mtd" % tablename)
            if not stream:
                LOGGER.warning(
                    "FLManager : "
                    + util.translate("FLMySQL", "Error al cargar los metadatos para la tabla")
                    + tablename
                )

                return self.recordInfo2(tablename)

            # docElem = doc.documentElement()
            mtd = self.db_.connManager().manager().metadata(tablename, True)
            if not mtd:
                return self.recordInfo2(tablename)
            fL = mtd.fieldList()
            if not fL:
                del mtd
                return self.recordInfo2(tablename)

            for f in mtd.fieldNames():
                field = mtd.field(f)
                info.append(
                    [
                        field.name(),
                        field.type(),
                        not field.allowNull(),
                        field.length(),
                        field.partDecimal(),
                        field.defaultValue(),
                        field.isPrimaryKey(),
                    ]
                )

            del mtd

        return info

    def notEqualsFields(self, field1: List[Any], field2: List[Any]) -> bool:
        """Return if a field has changed."""
        ret = False
        try:
            if not field1[2] == field2[2] and not field2[6]:
                ret = True

            if field1[1] == "stringlist" and not field2[1] in ("stringlist", "pixmap"):
                ret = True

            elif field1[1] == "string" and (
                field2[1] not in ("string", "time", "date") or field1[3] != field2[3]
            ):
                if field2[1] in ("time", "date") and field1[3] == 20:
                    ret = False
                elif field1[1] == "string" and field2[3] != 0:
                    ret = True
                else:
                    ret = True
            elif field1[1] == "uint" and not field2[1] in ("int", "uint", "serial"):
                ret = True
            elif field1[1] == "bool" and not field2[1] in ("bool", "unlock"):
                ret = True
            elif field1[1] == "double" and not field2[1] == "double":
                ret = True
            elif field1[1] == "timestamp" and not field2[1] == "timestamp":
                ret = True

        except Exception:
            LOGGER.error("notEqualsFields %s %s", field1, field2)

        return ret

    def tables(self, typeName: Optional[str] = None) -> List[str]:
        """Return a tables list specified by type."""
        return []

    def normalizeValue(self, text: str) -> str:
        """Return a database friendly text."""

        return str(text).replace("'", "''")

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

    def Mr_Proper(self) -> None:
        """Clear all garbage data."""
        pass

    def cascadeSupport(self) -> bool:
        """Return True if the driver support cascade."""
        return True

    def canDetectLocks(self) -> bool:
        """Return if can detect locks."""
        return True

    def fix_query(self, val: str) -> str:
        """Fix values on SQL."""
        ret_ = val.replace("'true'", "1")
        ret_ = ret_.replace("'false'", "0")
        ret_ = ret_.replace("'0'", "0")
        ret_ = ret_.replace("'1'", "1")
        return ret_

    def desktopFile(self) -> bool:
        """Return if use a file like database."""
        return self.desktop_file

    def execute_query(self, query: str, cursor: Any = None) -> Any:
        """Excecute a query and return result."""

        if not self.isOpen():
            raise Exception("execute_query: Database not open")

        self.set_last_error_null()
        if cursor is None:
            cursor = self.cursor()
        try:
            # q = self.fix_query(q)
            cursor.execute(query)
        except Exception:
            self.rollbackTransaction()
            self.setLastError(
                "No se pudo ejecutar la query %s.\n%s" % (query, traceback.format_exc()), query
            )

        return cursor

    def getTimeStamp(self) -> str:
        """Return TimeStamp."""

        if not self.isOpen():
            raise Exception("getTimeStamp: Database not open")

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

        if not self.isOpen():
            raise Exception("declareCursor: Database not open")

        sql = "SELECT %s FROM %s WHERE %s " % (fields, table, where)
        sql = self.fix_query(sql)
        self.rows_cached[curname] = []
        try:
            cursor.execute(sql)
            data_list = cursor.fetchmany(self.init_cached)
            for data in data_list:
                self.rows_cached[curname].append(data)

        except Exception as e:
            LOGGER.error("declareCursor: %s", e)
            LOGGER.trace("Detalle:", stack_info=True)
        # self.sql_query[curname] = sql

    def getRow(self, number: int, curname: str, cursor: Any) -> List:
        """Return a data row."""

        if not self.isOpen():
            raise Exception("getRow: Database not open")

        try:
            cached_count = len(self.rows_cached[curname])
            if number >= cached_count:

                data_list = cursor.fetchmany(number - cached_count + 1)
                for row in data_list:
                    self.rows_cached[curname].append(row)

                cached_count = len(self.rows_cached[curname])

        except Exception as e:
            LOGGER.error("getRow: %s", e)
            LOGGER.trace("Detalle:", stack_info=True)

        return self.rows_cached[curname][number] if number < cached_count else []

    def findRow(self, cursor: Any, curname: str, field_pos: int, value: Any) -> Optional[int]:
        """Return index row."""

        if not self.isOpen():
            raise Exception("findRow: Database not open")

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
            LOGGER.error("finRow: %s", e)
            LOGGER.warning("%s Detalle:", field_pos, stack_info=True)

        return ret_

    def deleteCursor(self, cursor_name: str, cursor: Any) -> None:
        """Delete cursor."""
        if not self.isOpen():
            raise Exception("deleteCursor: Database not open")

        try:
            del cursor
            self.rows_cached[cursor_name] = []
            self.rows_cached.pop(cursor_name)
        except Exception as exception:
            LOGGER.error("finRow: %s", exception)
            LOGGER.warning("Detalle:", stack_info=True)

    def queryUpdate(self, name: str, update: str, filter: str) -> str:
        """Return a database friendly update query."""
        sql = "UPDATE %s SET %s WHERE %s" % (name, update, filter)
        return sql

    def cursor(self) -> Any:
        """Return a cursor connection."""

        # if not self.isOpen():
        #    raise Exception("cursor: Database not open")

        return self.conn_.cursor() if self.conn_ is not None else False

    def insertMulti(self, table_name: str, records: Iterable) -> bool:
        """Insert several rows at once."""

        if not records:
            return False

        if not self.isOpen():
            raise Exception("insertMulti: Database not open")

        if not self.db_:
            raise Exception("must be connected")

        mtd = self.db_.connManager().manager().metadata(table_name)
        fList = []
        vList = []
        cursor_ = self.cursor()
        for f in records:
            field = mtd.field(f[0])
            if field.generated():
                fList.append(field.name())
                value = f[5]
                if field.type() in ("string", "stringlist"):
                    value = self.normalizeValue(value)
                value = self.formatValue(field.type(), value, False)
                if field.type() in ("string", "stringlist") and value in ["Null", "NULL"]:
                    value = "''"
                vList.append(value)

        sql = """INSERT INTO %s(%s) values (%s)""" % (
            table_name,
            ", ".join(fList),
            ", ".join(map(str, vList)),
        )

        if not fList:
            return False

        try:
            cursor_.execute(sql)
        except Exception:
            LOGGER.error("%s\n", sql)
            return False

        return True
