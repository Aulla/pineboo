"""Flqpsql module."""
from PyQt5.QtCore import QTime, QDate, QDateTime, Qt  # type: ignore
from PyQt5.Qt import qWarning, QDomDocument, QRegExp  # type: ignore
from PyQt5.QtWidgets import QMessageBox, QProgressDialog, QWidget  # type: ignore

from pineboolib.core.utils.utils_base import text2bool, auto_qt_translate_text

from pineboolib.application.utils.check_dependencies import check_dependencies
from pineboolib.application.database import pnsqlquery
from pineboolib.application.database import pnsqlcursor
from pineboolib.application.metadata import pnfieldmetadata
from pineboolib.application.metadata import pntablemetadata
from pineboolib import application

from pineboolib.fllegacy import flutil
from . import pnsqlschema
from pineboolib import logging

from sqlalchemy import create_engine  # type: ignore
import traceback
from typing import Iterable, Optional, Union, List, Dict, Any, cast


logger = logging.getLogger(__name__)


class FLQPSQL(pnsqlschema.PNSqlSchema):
    """FLQPSQL class."""

    def __init__(self):
        """Inicialize."""
        self.version_ = "0.8"
        self.name_ = "FLQPSQL"
        self.open_ = False
        self.errorList = []
        self.alias_ = "PostgreSQL (PSYCOPG2)"
        self.mobile_ = False
        self.pure_python_ = False
        self.defaultPort_ = 5432
        self.engine_ = None
        self.session_ = None
        self.declarative_base_ = None
        self.lastError_ = None

    def safe_load(self) -> bool:
        """Return if the driver can loads dependencies safely."""
        return check_dependencies(
            {"psycopg2": "python3-psycopg2", "sqlalchemy": "sqlAlchemy"}, False
        )

    def cursor(self):
        """Get current cursor for db."""
        return self.conn_.cursor()

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_userName: str, db_password: str
    ) -> Any:
        """Connecto to database."""
        self._dbname = db_name
        check_dependencies({"psycopg2": "python3-psycopg2", "sqlalchemy": "sqlAlchemy"})
        import psycopg2  # type: ignore
        from psycopg2.extras import LoggingConnection  # type: ignore

        logger = logging.getLogger(self.alias_)
        logger.debug = logger.trace  # type: ignore  # Send Debug output to Trace

        conninfostr = "dbname=%s host=%s port=%s user=%s password=%s connect_timeout=5" % (
            db_name,
            db_host,
            db_port,
            db_userName,
            db_password,
        )

        try:
            self.conn_ = psycopg2.connect(conninfostr, connection_factory=LoggingConnection)
            self.conn_.initialize(logger)
            self.engine_ = create_engine(
                "postgresql+psycopg2://%s:%s@%s:%s/%s"
                % (db_userName, db_password, db_host, db_port, db_name)
            )
        except psycopg2.OperationalError as e:
            if application.project._splash:
                application.project._splash.hide()

            if application.project._DGI and not application.project.DGI.localDesktop():
                return False

            if "does not exist" in str(e) or "no existe" in str(e):
                ret = QMessageBox.warning(
                    QWidget(),
                    "Pineboo",
                    "La base de datos %s no existe.\n¿Desea crearla?" % db_name,
                    cast(QMessageBox.StandardButtons, QMessageBox.Ok | QMessageBox.No),
                )
                if ret == QMessageBox.No:
                    return False
                else:
                    conninfostr2 = (
                        "dbname=postgres host=%s port=%s user=%s password=%s connect_timeout=5"
                        % (db_host, db_port, db_userName, db_password)
                    )
                    try:
                        tmpConn = psycopg2.connect(conninfostr2)

                        tmpConn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

                        cursor = tmpConn.cursor()
                        try:
                            cursor.execute("CREATE DATABASE %s" % db_name)
                        except Exception:
                            print("ERROR: FLPSQL.connect", traceback.format_exc())
                            cursor.execute("ROLLBACK")
                            cursor.close()
                            return False
                        cursor.close()
                        return self.connect(db_name, db_host, db_port, db_userName, db_password)
                    except Exception:
                        qWarning(traceback.format_exc())
                        QMessageBox.information(
                            QWidget(),
                            "Pineboo",
                            "ERROR: No se ha podido crear la Base de Datos %s" % db_name,
                            QMessageBox.Ok,
                        )
                        print("ERROR: No se ha podido crear la Base de Datos %s" % db_name)
                        return False
            else:
                QMessageBox.information(
                    QWidget(), "Pineboo", "Error de conexión\n%s" % str(e), QMessageBox.Ok
                )
                return False

        # self.conn_.autocommit = True #Posiblemente tengamos que ponerlo a
        # false para que las transacciones funcionen
        self.conn_.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        if self.conn_:
            self.open_ = True

        try:
            self.conn_.set_client_encoding("UTF8")
        except Exception:
            qWarning(traceback.format_exc())

        return self.conn_

    def formatValueLike(self, type_: str, v: Any, upper: bool) -> str:
        """Return a string with the format value like."""
        util = flutil.FLUtil()
        res = "IS NULL"

        if type_ == "bool":
            s = str(v[0]).upper()
            if s == str(util.translate("application", "Sí")[0]).upper():
                res = "='t'"
            elif str(util.translate("application", "No")[0]).upper():
                res = "='f'"

        elif type_ == "date":
            dateamd = util.dateDMAtoAMD(str(v))
            if dateamd is None:
                dateamd = ""
            res = "::text LIKE '%%" + dateamd + "'"

        elif type_ == "time":
            t = v.toTime()
            res = "::text LIKE '" + t.toString(Qt.ISODate) + "%%'"

        else:
            res = str(v)
            if upper:
                res = "%s" % res.upper()

            res = "::text LIKE '" + res + "%%'"

        return res

    def formatValue(self, type_: str, v: Any, upper: bool) -> Optional[Union[int, str, bool]]:
        """Return a string with the format value."""

        util = flutil.FLUtil()

        s: Any = None

        # if v == None:
        #    v = ""
        # TODO: psycopg2.mogrify ???

        if v is None:
            return "NULL"

        if type_ == "bool" or type_ == "unlock":
            s = text2bool(v)

        elif type_ == "date":
            if s != "Null":
                if len(str(v).split("-")[0]) < 3:
                    val = util.dateDMAtoAMD(v)
                else:
                    val = v

                s = "'%s'" % val

        elif type_ == "time":
            s = "'%s'" % v

        elif type_ in ("uint", "int", "double", "serial"):
            if s == "Null":
                s = "0"
            else:
                s = v

        elif type_ in ("string", "stringlist"):
            if v == "":
                s = "Null"
            else:
                if type_ == "string":
                    v = auto_qt_translate_text(v)
                if upper and type_ == "string":
                    v = v.upper()

                s = "'%s'" % v

        elif type_ == "pixmap":
            if v.find("'") > -1:
                v = self.normalizeValue(v)
            s = "'%s'" % v

        else:
            s = v
        # print ("PNSqlDriver(%s).formatValue(%s, %s) = %s" % (self.name_, type_, v, s))
        return s

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Return next serial value."""
        q = pnsqlquery.PNSqlQuery()
        q.setSelect(u"nextval('" + table + "_" + field + "_seq')")
        q.setFrom("")
        q.setWhere("")
        if not q.exec_():
            qWarning("not exec sequence")
        elif q.first():
            return q.value(0)

        return None

    def savePoint(self, n: int) -> bool:
        """Set a savepoint."""
        if not self.isOpen():
            qWarning("PSQLDriver::savePoint: Database not open")
            return False
        self.set_last_error_null()
        cursor = self.conn_.cursor()
        try:
            cursor.execute("SAVEPOINT sv_%s" % n)
        except Exception:
            self.setLastError("No se pudo crear punto de salvaguarda", "SAVEPOINT sv_%s" % n)
            qWarning(
                "PSQLDriver:: No se pudo crear punto de salvaguarda SAVEPOINT sv_%s \n %s "
                % (n, traceback.format_exc())
            )
            return False

        return True

    def rollbackSavePoint(self, n: int) -> bool:
        """Set rollback savepoint."""
        if not self.isOpen():
            qWarning("PSQLDriver::rollbackSavePoint: Database not open")
            return False
        self.set_last_error_null()
        cursor = self.conn_.cursor()
        try:
            cursor.execute("ROLLBACK TO SAVEPOINT sv_%s" % n)
        except Exception:
            self.setLastError(
                "No se pudo rollback a punto de salvaguarda", "ROLLBACK TO SAVEPOINTt sv_%s" % n
            )
            qWarning(
                "PSQLDriver:: No se pudo rollback a punto de salvaguarda ROLLBACK TO SAVEPOINT sv_%s\n %s"
                % (n, traceback.format_exc())
            )
            return False

        return True

    def commitTransaction(self) -> bool:
        """Set commit transaction."""
        if not self.isOpen():
            qWarning("PSQLDriver::commitTransaction: Database not open")
        self.set_last_error_null()
        cursor = self.conn_.cursor()
        try:
            cursor.execute("COMMIT TRANSACTION")
        except Exception:
            self.setLastError("No se pudo aceptar la transacción", "COMMIT")
            qWarning(
                "PSQLDriver:: No se pudo aceptar la transacción COMMIT\n %s"
                % traceback.format_exc()
            )
            return False

        return True

    def rollbackTransaction(self) -> bool:
        """Set a rollback transaction."""
        if not self.isOpen():
            qWarning("PSQLDriver::rollbackTransaction: Database not open")
        self.set_last_error_null()
        cursor = self.conn_.cursor()
        try:
            cursor.execute("ROLLBACK TRANSACTION")
        except Exception:
            self.setLastError("No se pudo deshacer la transacción", "ROLLBACK")
            qWarning(
                "PSQLDriver:: No se pudo deshacer la transacción ROLLBACK\n %s"
                % traceback.format_exc()
            )
            return False

        return True

    def transaction(self) -> bool:
        """Set a new transaction."""
        if not self.isOpen():
            qWarning("PSQLDriver::transaction: Database not open")
        self.set_last_error_null()
        cursor = self.conn_.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
        except Exception:
            self.setLastError("No se pudo crear la transacción", "BEGIN")
            qWarning(
                "PSQLDriver:: No se pudo crear la transacción BEGIN\n %s" % traceback.format_exc()
            )
            return False

        return True

    def releaseSavePoint(self, n: int) -> bool:
        """Set release savepoint."""

        if not self.isOpen():
            qWarning("PSQLDriver::releaseSavePoint: Database not open")
            return False
        self.set_last_error_null()
        cursor = self.conn_.cursor()
        try:
            cursor.execute("RELEASE SAVEPOINT sv_%s" % n)
        except Exception:
            self.setLastError(
                "No se pudo release a punto de salvaguarda", "RELEASE SAVEPOINT sv_%s" % n
            )
            qWarning(
                "PSQLDriver:: No se pudo release a punto de salvaguarda RELEASE SAVEPOINT sv_%s\n %s"
                % (n, traceback.format_exc())
            )

            return False

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
        sql = "DECLARE %s NO SCROLL CURSOR WITH HOLD FOR SELECT %s FROM %s WHERE %s " % (
            curname,
            fields,
            table,
            where,
        )
        try:
            cursor.execute(sql)
        except Exception as e:
            logger.error("refreshQuery: %s", e)
            logger.info("SQL: %s", sql)
            logger.trace("Detalle:", stack_info=True)

    def refreshFetch(
        self, number: int, curname: str, table: str, cursor: Any, fields: str, where_filter: str
    ) -> None:
        """Return data fetched."""
        sql = "FETCH %d FROM %s" % (number, curname)

        sql_exists = "SELECT name FROM pg_cursors WHERE name = '%s'" % curname
        cursor.execute(sql_exists)
        if cursor.fetchone() is None:
            return

        try:
            cursor.execute(sql)
        except Exception as e:
            logger.error("refreshFetch: %s", e)
            logger.info("SQL: %s", sql)
            logger.trace("Detalle:", stack_info=True)

    def fetchAll(
        self, cursor: Any, tablename: str, where_filter: str, fields: str, curname: str
    ) -> List:
        """Return all fetched data from a query."""
        ret_: List[str] = []
        try:
            ret_ = cursor.fetchall()
        except Exception as e:
            logger.error("fetchAll: %s", e)
            logger.info("where_filter: %s", where_filter)
            logger.trace("Detalle:", stack_info=True)

        return ret_

    def existsTable(self, name: str) -> bool:
        """Return if exists a table specified by name."""
        if not self.isOpen():
            return False

        cur_ = self.conn_.cursor()
        cur_.execute("select relname from pg_class where relname = '%s'" % name)
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
            qWarning(u"FLManager : No se ha podido crear la tabla " + tmd.name())
            qWarning(u"FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno.")
            return None

        i = 1
        for field in fieldList:
            sql = sql + field.name()
            if field.type() == "int":
                sql = sql + " INT2"
            elif field.type() == "uint":
                sql = sql + " INT4"
            elif field.type() in ("bool", "unlock"):
                sql = sql + " BOOLEAN"
            elif field.type() == "double":
                sql = sql + " FLOAT8"
            elif field.type() == "time":
                sql = sql + " TIME"
            elif field.type() == "date":
                sql = sql + " DATE"
            elif field.type() == "pixmap":
                sql = sql + " TEXT"
            elif field.type() == "string":
                sql = sql + " VARCHAR"
            elif field.type() == "stringlist":
                sql = sql + " TEXT"
            elif field.type() == "bytearray":
                sql = sql + " BYTEA"
            elif field.type() == "serial":
                seq = "%s_%s_seq" % (tmd.name(), field.name())
                q = pnsqlquery.PNSqlQuery()
                q.setForwardOnly(True)
                q.exec_("SELECT relname FROM pg_class WHERE relname='%s'" % seq)
                if not q.next():
                    cursor = self.conn_.cursor()
                    # self.transaction()
                    try:
                        cursor.execute("CREATE SEQUENCE %s" % seq)
                    except Exception:
                        print("FLQPSQL::sqlCreateTable:\n", traceback.format_exc())
                    # self.commitTransaction()

                sql = sql + " INT4 DEFAULT NEXTVAL('%s')" % seq
                del q

            longitud = field.length()
            if longitud > 0:
                sql = sql + "(%s)" % longitud

            if field.isPrimaryKey():
                if primaryKey is None:
                    sql = sql + " PRIMARY KEY"
                else:
                    qWarning(
                        util.translate("application", "FLManager : Tabla-> ")
                        + tmd.name()
                        + util.translate(
                            "application",
                            " . Se ha intentado poner una segunda clave primaria para el campo ",
                        )
                        + field.name()
                        + util.translate("application", " , pero el campo ")
                        + primaryKey
                        + util.translate(
                            "application",
                            " ya es clave primaria. Sólo puede existir una clave primaria en FLTableMetaData, "
                            "use FLCompoundKey para crear claves compuestas.",
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
                print(traceback.format_exc())

            return mismatch

        else:
            return self.mismatchedTable(table1, tmd_or_table2.name(), db_)

    def recordInfo2(self, tablename: str) -> List[List[Any]]:
        """Return info from a database table."""
        if not self.isOpen():
            raise Exception("PSQL is not open")
        info = []
        stmt = (
            "select pg_attribute.attname, pg_attribute.atttypid, pg_attribute.attnotnull, pg_attribute.attlen, pg_attribute.atttypmod, "
            "pg_attrdef.adsrc from pg_class, pg_attribute "
            "left join pg_attrdef on (pg_attrdef.adrelid = pg_attribute.attrelid and pg_attrdef.adnum = pg_attribute.attnum)"
            " where lower(pg_class.relname) = '%s' and pg_attribute.attnum > 0 and pg_attribute.attrelid = pg_class.oid "
            "and pg_attribute.attisdropped = false order by pg_attribute.attnum" % tablename.lower()
        )
        cursor = self.conn_.cursor()
        cursor.execute(stmt)
        rows = cursor.fetchall()
        for row in rows:
            len_ = row[3]
            precision = row[4]
            name = row[0]
            type_ = row[1]
            allowNull = row[2]
            defVal = row[5]

            if isinstance(defVal, str) and defVal is not None:
                if defVal.find("::character varying") > -1:
                    defVal = defVal[0 : defVal.find("::character varying")]

            if len_ == -1 and precision and precision > -1:
                len_ = precision - 4
                precision = -1

            if len_ == -1:
                len_ = 0

            if precision == -1:
                precision = 0

            if defVal and defVal[0] == "'":
                defVal = defVal[1 : len(defVal) - 2]

            info.append(
                [name, self.decodeSqlType(type_), allowNull, len_, precision, defVal, int(type_)]
            )

        return info

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

        return ret

    def recordInfo(self, tablename_or_query: Any) -> List[list]:
        """Return info from  a record fields."""
        info: List[list] = []
        if not self.isOpen():
            return info

        if isinstance(tablename_or_query, str):
            tablename = tablename_or_query

            doc = QDomDocument(tablename)
            if self.db_ is None:
                raise Exception("recordInfo. self.db_ es Nulo")

            stream = self.db_.connManager().managerModules().contentCached("%s.mtd" % tablename)
            util = flutil.FLUtil()
            if not util.domDocumentSetContent(doc, stream):
                print(
                    "FLManager : "
                    + util.translate("application", "Error al cargar los metadatos para la tabla")
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
        """Return if a field has canged."""
        ret = False
        try:
            if not field1[2] == field2[2] and not field2[6]:
                ret = True

            if field1[1] == "stringlist" and not field2[1] in ("stringlist", "pixmap"):
                ret = True

            elif field1[1] == "string" and (
                not field2[1] in ("string", "time", "date") or not field1[3] == field2[3]
            ):
                if field1[1] == "string" and field2[3] != 0:
                    ret = True
            elif field1[1] == "uint" and not field2[1] in ("int", "uint", "serial"):
                ret = True
            elif field1[1] == "bool" and not field2[1] in ("bool", "unlock"):
                ret = True
            elif field1[1] == "double" and not field2[1] == "double":
                ret = True

        except Exception:
            print(traceback.format_exc())

        return ret

    def tables(self, typeName: Optional[str] = None) -> List[str]:
        """Return a tables list specified by type."""
        tl: List[str] = []
        if not self.isOpen():
            return tl

        t = pnsqlquery.PNSqlQuery()
        t.setForwardOnly(True)

        if not typeName or typeName == "Tables":
            t.exec_(
                "select relname from pg_class where ( relkind = 'r' ) AND ( relname !~ '^Inv' ) AND ( relname !~ '^pg_' ) "
            )
            while t.next():
                tl.append(str(t.value(0)))

        if not typeName or typeName == "Views":
            t.exec_(
                "select relname from pg_class where ( relkind = 'v' ) AND ( relname !~ '^Inv' ) AND ( relname !~ '^pg_' ) "
            )
            while t.next():
                tl.append(str(t.value(0)))
        if not typeName or typeName == "SystemTables":
            t.exec_(
                "select relname from pg_class where ( relkind = 'r' ) AND ( relname like 'pg_%' ) "
            )
            while t.next():
                tl.append(str(t.value(0)))

        del t
        return tl

    def normalizeValue(self, text: str) -> str:
        """Return a database friendly text."""
        return str(text).replace("'", "''")

    def constraintExists(self, name: str) -> bool:
        """Return if constraint exists specified by name."""

        sql = (
            "SELECT constraint_name FROM information_schema.table_constraints where constraint_name='%s'"
            % name
        )

        if self.db_ is None:
            raise Exception("constraintExists. self.db_ is None")

        q = pnsqlquery.PNSqlQuery(None, "dbAux")

        return q.exec_(sql) and q.size() > 0

    def queryUpdate(self, name: str, update: str, filter: str) -> str:
        """Return a database friendly update query."""
        return """UPDATE %s SET %s WHERE %s RETURNING *""" % (name, update, filter)

    def alterTable(
        self,
        mtd1: Union[str, "pntablemetadata.PNTableMetaData"],
        mtd2: Optional[str] = None,
        key: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Modify a table structure."""

        if isinstance(mtd1, pntablemetadata.PNTableMetaData):
            return self.alterTable3(mtd1)
        else:
            return self.alterTable2(mtd1, mtd2, key, force)

    def alterTable3(self, new_mtd: "pntablemetadata.PNTableMetaData") -> bool:
        """Modify a table structure."""
        if self.hasCheckColumn(new_mtd):
            return False

        util = flutil.FLUtil()

        old_mtd = new_mtd
        fieldList = old_mtd.fieldList()

        renameOld = "%salteredtable%s" % (
            old_mtd.name()[0:5],
            QDateTime().currentDateTime().toString("ddhhssz"),
        )

        if self.db_ is None:
            raise Exception("alterTable3. self.db_ is None")

        self.db_.connManager().dbAux().transaction()

        q = pnsqlquery.PNSqlQuery(None, self.db_.connManager().dbAux())

        constraintName = "%s_key" % old_mtd.name()

        if self.constraintExists(constraintName) and not q.exec_(
            "ALTER TABLE %s DROP CONSTRAINT %s" % (old_mtd.name(), constraintName)
        ):
            self.db_.connManager().dbAux().rollbackTransaction()
            return False

        for oldField in fieldList:
            if oldField.isCheck():
                return False
            if oldField.isUnique():
                constraintName = "%s_%s_key" % (old_mtd.name(), oldField.name())
                if self.constraintExists(constraintName) and not q.exec_(
                    "ALTER TABLE %s DROP CONSTRAINT %s" % (old_mtd.name(), constraintName)
                ):
                    self.db_.connManager().dbAux().rollbackTransaction()
                    return False

        if not q.exec_("ALTER TABLE %s RENAME TO %s" % (old_mtd.name(), renameOld)):
            self.db_.connManager().dbAux().rollbackTransaction()
            return False

        if not self.db_.connManager().manager().createTable(new_mtd):
            self.db_.connManager().dbAux().rollbackTransaction()
            return False

        oldCursor = pnsqlcursor.PNSqlCursor(renameOld, True, "dbAux")
        oldCursor.setModeAccess(oldCursor.Browse)
        oldCursor.select()

        fieldList = new_mtd.fieldList()

        if not fieldList:
            self.db_.connManager().dbAux().rollbackTransaction()
            return False

        oldCursor.select()
        totalSteps = oldCursor.size()
        progress = QProgressDialog(
            util.translate("application", "Reestructurando registros para %s...")
            % (new_mtd.alias()),
            util.translate("application", "Cancelar"),
            0,
            totalSteps,
        )
        progress.setLabelText(util.translate("application", "Tabla modificada"))

        step = 0
        newBuffer = None
        newField = None
        listRecords = []
        newBufferInfo = self.recordInfo2(new_mtd.name())
        oldFieldsList = {}
        newFieldsList = {}
        defValues: Dict[str, Any] = {}
        v = None

        for newField in fieldList:
            old_field: Optional["pnfieldmetadata.PNFieldMetaData"] = old_mtd.field(newField.name())

            defValues[str(step)] = None
            if not old_field or not oldCursor.field(old_field.name()):
                if not old_field:
                    old_field = newField
                if not newField.type() == "serial":
                    v = newField.defaultValue()
                    defValues[str(step)] = v

            newFieldsList[str(step)] = newField
            oldFieldsList[str(step)] = old_field
            step = step + 1

        ok = True
        while oldCursor.next():
            newBuffer = newBufferInfo

            for reg in defValues.keys():
                newField = newFieldsList[reg]
                oldField = oldFieldsList[reg]
                if defValues[reg]:
                    v = defValues[reg]
                else:
                    v = oldCursor.valueBuffer(newField.name())
                    if (
                        (not oldField.allowNull or not newField.allowNull())
                        and not v
                        and not newField.type() == "serial"
                    ):
                        defVal = newField.defaultValue()
                        if defVal is not None:
                            v = defVal

                    # FIXME: newBuffer is an array from recordInfo2()
                    """if v is not None and not newBuffer.field(newField.name()).type() == newField.type():
                        print(
                            "FLManager::alterTable : "
                            + util.translate("application", "Los tipos del campo %1 no son compatibles. Se introducirá un valor nulo.").arg(
                                newField.name()
                            )
                        )

                    if v is not None and newField.type() == "string" and newField.length() > 0:
                        v = str(v)[0 : newField.length()]

                    if (not oldField.allowNull() or not newField.allowNull()) and v is None:
                        if oldField.type() == "serial":
                            v = int(self.nextSerialVal(new_mtd.name(), newField.name()))
                        elif oldField.type() in ("int", "uint", "bool", "unlock"):
                            v = 0
                        elif oldField.type() == "double":
                            v = 0.0
                        elif oldField.type() == "time":
                            v = QTime().currentTime()
                        elif oldField.type() == "date":
                            v = QDate().currentDate()
                        else:
                            v = "NULL"[0 : newField.length()]

                    # FIXME: newBuffer is an array from recordInfo2()
                    newBuffer.setValue(newField.name(), v)
                    """

                listRecords.append(newBuffer)

            # if not self.insertMulti(new_mtd.name(), listRecords):
            #    ok = False
            #    listRecords.clear()
            #    break

            # listRecords.clear()

        if len(listRecords) > 0:
            if not self.insertMulti(new_mtd.name(), listRecords):
                ok = False
            listRecords.clear()

        if ok:
            self.db_.connManager().dbAux().commit()
        else:
            self.db_.connManager().dbAux().rollbackTransaction()
            return False

        force = False  # FIXME
        if force and ok:
            q.exec_("DROP TABLE %s CASCADE" % renameOld)
        return True

    def alterTable2(
        self, mtd1: str, mtd2: Optional[str] = None, key: Optional[str] = None, force: bool = False
    ) -> bool:
        """Modify a table structure."""
        # logger.warning("alterTable2 FIXME::Me quedo colgado al hacer createTable --> existTable")
        util = flutil.FLUtil()

        old_mtd = None
        new_mtd = None
        doc = QDomDocument("doc")
        docElem = None

        if self.db_ is None:
            raise Exception("alterTable2. self.db_ is None")

        if not util.domDocumentSetContent(doc, mtd1):
            logger.warning(
                "FLManager::alterTable : "
                + util.translate("application", "Error al cargar los metadatos.")
            )
        else:
            docElem = doc.documentElement()

            old_mtd = self.db_.connManager().manager().metadata(docElem, True)

        if old_mtd and old_mtd.isQuery():
            return True

        if not util.domDocumentSetContent(doc, mtd2):
            logger.warning(
                "FLManager::alterTable : "
                + util.translate("application", "Error al cargar los metadatos.")
            )
            return False
        else:
            docElem = doc.documentElement()
            new_mtd = self.db_.connManager().manager().metadata(docElem, True)

        if not old_mtd:
            old_mtd = new_mtd

        if not old_mtd.name() == new_mtd.name():
            logger.warning(
                "FLManager::alterTable : "
                + util.translate("application", "Los nombres de las tablas nueva y vieja difieren.")
            )
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        oldPK = old_mtd.primaryKey()
        newPK = new_mtd.primaryKey()

        if not oldPK == newPK:
            logger.warning(
                "FLManager::alterTable : "
                + util.translate("application", "Los nombres de las claves primarias difieren.")
            )
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        if not self.db_.connManager().manager().checkMetaData(old_mtd, new_mtd):
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return True

        if not self.db_.connManager().manager().existsTable(old_mtd.name()):
            logger.warning(
                "FLManager::alterTable : "
                + util.translate(
                    "application", "La tabla %s antigua de donde importar los registros no existe."
                )
                % (old_mtd.name())
            )
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        fieldList = old_mtd.fieldList()
        oldField = None

        if not fieldList:
            logger.warning(
                "FLManager::alterTable : "
                + util.translate("application", "Los antiguos metadatos no tienen campos.")
            )
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        renameOld = "%salteredtable%s" % (
            old_mtd.name()[0:5],
            QDateTime().currentDateTime().toString("ddhhssz"),
        )

        if not self.db_.connManager().dbAux():
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        self.db_.connManager().dbAux().transaction()

        if key and len(key) == 40:
            c = pnsqlcursor.PNSqlCursor("flfiles", True, "dbAux")
            c.setForwardOnly(True)
            c.setFilter("nombre = '%s.mtd'" % renameOld)
            c.select()
            if not c.next():
                c.setModeAccess(c.Insert)
                c.refreshBuffer()
                c.setValueBuffer("nombre", "%s.mtd" % renameOld)
                c.setValueBuffer("contenido", mtd1)
                c.setValueBuffer("sha", key)
                c.commitBuffer()
                # c.primeInsert()
                # buffer = c.buffer()
                # if buffer is not None:
                #    buffer.setValue("nombre", "%s.mtd" % renameOld)
                #    buffer.setValue("contenido", mtd1)
                #    buffer.setValue("sha", key)
                #    c.insert()

        # q = pnsqlquery.PNSqlQuery(None, self.db_.dbAux())
        constraintName = "%s_pkey" % old_mtd.name()
        c1 = self.db_.connManager().dbAux().cursor()
        c1.execute(
            "ALTER TABLE %s DROP CONSTRAINT %s CASCADE" % (old_mtd.name(), constraintName)
        )  # FIXME CASCADE is correct?

        if self.constraintExists(constraintName):

            logger.warning(
                "FLManager : "
                + util.translate(
                    "application",
                    "En método alterTable, no se ha podido borrar el índice %s_pkey de la tabla antigua."
                    % old_mtd.name(),
                )
            )
            self.db_.connManager().dbAux().rollbackTransaction()
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        fieldNamesOld = []
        record_info = self.recordInfo2(old_mtd.name())
        for f in record_info:
            fieldNamesOld.append(f[0])

        for it in fieldList:
            # if new_mtd.field(it.name()) is not None:
            #    fieldNamesOld.append(it.name())

            if it.isUnique():
                constraintName = "%s_%s_key" % (old_mtd.name(), it.name())
                c2 = self.db_.connManager().dbAux().cursor()
                c2.execute("ALTER TABLE %s DROP CONSTRAINT %s" % (old_mtd.name(), constraintName))

                if self.constraintExists(constraintName):
                    logger.warning(
                        "FLManager : "
                        + util.translate(
                            "application",
                            "En método alterTable, no se ha podido borrar el índice %s_%s_key de la tabla antigua.",
                        )
                        % (old_mtd.name(), oldField)
                    )
                    self.db_.connManager().dbAux().rollbackTransaction()
                    if old_mtd and not old_mtd == new_mtd:
                        del old_mtd
                    if new_mtd:
                        del new_mtd

                    return False

        # if not q.exec_("ALTER TABLE %s RENAME TO %s" % (old_mtd.name(), renameOld)):
        #    logger.warning(
        #        "FLManager::alterTable : "
        #        + util.translate("application", "No se ha podido renombrar la tabla antigua.")
        #    )

        #    self.db_.dbAux().rollbackTransaction()
        #    if old_mtd and not old_mtd == new_mtd:
        #        del old_mtd
        #    if new_mtd:
        #        del new_mtd

        #    return False
        c3 = self.db_.connManager().dbAux().cursor()
        c3.execute("ALTER TABLE %s RENAME TO %s" % (old_mtd.name(), renameOld))
        if not self.db_.connManager().manager().createTable(new_mtd):
            self.db_.connManager().dbAux().rollbackTransaction()
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        v = None
        ok = False

        if not force and not fieldNamesOld:
            self.db_.connManager().dbAux().rollbackTransaction()
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return self.alterTable2(mtd1, mtd2, key, True)

        if not ok:
            old_cursor = self.db_.connManager().dbAux().cursor()
            old_cursor.execute(
                "SELECT %s FROM %s WHERE 1 = 1" % (", ".join(fieldNamesOld), renameOld)
            )
            result_set = old_cursor.fetchall()
            totalSteps = len(result_set)
            util.createProgressDialog(
                util.translate(
                    "application", "Reestructurando registros para %s..." % new_mtd.alias()
                ),
                totalSteps,
            )
            util.setLabelText(util.translate("application", "Tabla modificada"))

            step = 0
            newBuffer = None
            newField = None
            listRecords = []
            newBufferInfo = self.recordInfo2(new_mtd.name())
            vector_fields = {}
            default_values = {}
            v = None

            for it2 in fieldList:
                oldField = old_mtd.field(it2.name())

                if oldField is None or not result_set:
                    if oldField is None:
                        oldField = it2
                    if it2.type() != pnfieldmetadata.PNFieldMetaData.Serial:
                        v = it2.defaultValue()
                        step += 1
                        default_values[str(step)] = v

                step += 1
                vector_fields[str(step)] = it2
                step += 1
                vector_fields[str(step)] = oldField

            # step2 = 0
            ok = True
            x = 0
            for row in result_set:
                x += 1
                newBuffer = newBufferInfo

                i = 0

                while i < step:
                    v = None
                    if str(i + 1) in default_values.keys():
                        i += 1
                        v = default_values[str(i)]
                        i += 1
                        newField = vector_fields[str(i)]
                        i += 1
                        oldField = vector_fields[str(i)]

                    else:
                        i += 1
                        newField = vector_fields[str(i)]
                        i += 1
                        oldField = vector_fields[str(i)]
                        pos = 0
                        for field_name in fieldNamesOld:
                            if newField.name() == field_name:
                                v = row[pos]
                                break
                            pos += 1

                        if (
                            (not oldField.allowNull() or not newField.allowNull())
                            and (v is None)
                            and newField.type() != pnfieldmetadata.PNFieldMetaData.Serial
                        ):
                            defVal = newField.defaultValue()
                            if defVal is not None:
                                v = defVal

                    if v is not None and newField.type() == "string" and newField.length() > 0:
                        v = str(v)[: newField.length()]

                    if (not oldField.allowNull() or not newField.allowNull()) and v in (
                        None,
                        "None",
                    ):
                        if oldField.type() == pnfieldmetadata.PNFieldMetaData.Serial:
                            v = int(self.nextSerialVal(new_mtd.name(), newField.name()))
                        elif oldField.type() in ["int", "uint"]:
                            v = 0
                        elif oldField.type() in ["bool", "unlock"]:
                            v = False
                        elif oldField.type() == "double":
                            v = 0.0
                        elif oldField.type() == "time":
                            v = QTime.currentTime()
                        elif oldField.type() == "date":
                            v = QDate.currentDate()
                        else:
                            v = "NULL"[: newField.length()]

                    # new_b = []
                    for buffer_ in newBuffer:
                        if buffer_[0] == newField.name():
                            new_buffer = []
                            new_buffer.append(buffer_[0])
                            new_buffer.append(buffer_[1])
                            new_buffer.append(newField.allowNull())
                            new_buffer.append(buffer_[3])
                            new_buffer.append(buffer_[4])
                            new_buffer.append(v)
                            new_buffer.append(buffer_[6])
                            listRecords.append(new_buffer)
                            break
                    # newBuffer.setValue(newField.name(), v)

                if listRecords:
                    if not self.insertMulti(new_mtd.name(), listRecords):
                        ok = False
                    listRecords = []

            util.setProgress(totalSteps)

        util.destroyProgressDialog()
        c_drop = self.db_.connManager().dbAux().cursor()
        if ok:
            self.db_.connManager().dbAux().commit()

            if force:
                c_drop.execute("DROP TABLE %s CASCADE" % renameOld)
        else:
            self.db_.connManager().dbAux().rollbackTransaction()

            c_drop.execute("DROP TABLE %s CASCADE" % old_mtd.name())
            c_drop.execute("ALTER TABLE %s RENAME TO %s" % (renameOld, old_mtd.name()))

            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd
            return False

        if old_mtd and old_mtd != new_mtd:
            del old_mtd
        if new_mtd:
            del new_mtd

        return True

    def insertMulti(self, table_name: str, records: Iterable) -> bool:
        """Insert multiple registers into a table."""

        if not records:
            return False

        if self.db_ is None:
            raise Exception("insertMulti. self.db_ is None")

        mtd = self.db_.connManager().manager().metadata(table_name)
        fList = []
        vList = []
        cursor_ = self.conn_.cursor()
        for f in records:
            field = mtd.field(f[0])
            if field.generated():

                value = f[5]
                if field.type() in ("string", "stringlist") and value:
                    value = self.normalizeValue(value)
                value = self.formatValue(field.type(), value, False)
                if field.type() in ("string", "stringlist") and value in ["Null", "NULL"]:
                    value = "''"
                #    value = self.db_.normalizeValue(value)
                # if value is None and field.allowNull():
                #    continue
                fList.append(field.name())
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
        except Exception as exc:
            print(sql[:200], "\n", exc)
            raise Exception("EOo!")
            return False

        return True

    def Mr_Proper(self) -> None:
        """Clear all garbage data."""
        util = flutil.FLUtil()

        if self.db_ is None:
            raise Exception("Mr_Proper. self.db_ is None")

        self.db_.connManager().dbAux().transaction()

        qry = pnsqlquery.PNSqlQuery(None, "dbAux")
        # qry2 = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry3 = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry4 = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry5 = pnsqlquery.PNSqlQuery(None, "dbAux")
        cur = self.db_.connManager().dbAux().cursor()
        steps = 0

        rx = QRegExp("^.*\\d{6,9}$")
        if rx in self.tables():
            listOldBks = self.tables()[rx]
        else:
            listOldBks = []

        qry.exec_(
            "select nombre from flfiles where nombre similar to"
            "'%[[:digit:]][[:digit:]][[:digit:]][[:digit:]]-[[:digit:]][[:digit:]]%:[[:digit:]][[:digit:]]%' or nombre similar to"
            "'%alteredtable[[:digit:]][[:digit:]][[:digit:]][[:digit:]]%' or (bloqueo='f' and nombre like '%.mtd')"
        )

        util.createProgressDialog(
            util.translate("application", "Borrando backups"), len(listOldBks) + qry.size() + 2
        )

        while qry.next():
            item = qry.value(0)
            util.setLabelText(util.translate("application", "Borrando registro %s") % item)

            cur.execute("DELETE FROM flfiles WHERE nombre ='%s'" % item)
            if item.find("alteredtable") > -1:
                if self.existsTable(item.replace(".mtd", "")):
                    util.setLabelText(util.translate("application", "Borrando tabla %s" % item))
                    cur.execute("DROP TABLE %s CASCADE" % item.replace(".mtd", ""))

            steps = steps + 1
            util.setProgress(steps)

        for item in listOldBks:
            if self.existsTable(item):
                util.setLabelText(util.translate("application", "Borrando tabla %s" % item))
                cur.execute("DROP TABLE %s CASCADE" % item)

            steps = steps + 1
            util.setProgress(steps)

        util.setLabelText(util.translate("application", "Inicializando cachés"))
        steps = steps + 1
        util.setProgress(steps)
        cur.execute("DELETE FROM flmetadata")
        cur.execute("DELETE FROM flvar")
        self.db_.connManager().manager().cleanupMetaData()
        # self.db_.driver().commit()
        util.destroyProgressDialog()

        steps = 0
        qry3.exec_("select tablename from pg_tables where schemaname='public'")
        util.createProgressDialog(
            util.translate("application", "Comprobando base de datos"), qry3.size()
        )
        while qry3.next():
            item = qry3.value(0)
            util.setLabelText(util.translate("application", "Comprobando tabla %s" % item))
            mustAlter = self.mismatchedTable(item, item)
            if mustAlter:
                conte = self.db_.connManager().managerModules().content("%s.mtd" % item)
                if conte:
                    msg = util.translate(
                        "application",
                        "La estructura de los metadatos de la tabla '%s' y su "
                        "estructura interna en la base de datos no coinciden. "
                        "Intentando regenerarla." % item,
                    )

                    logger.warning(msg)
                    self.alterTable2(conte, conte, None, True)

            steps = steps + 1
            util.setProgress(steps)

        self.db_.connManager().dbAux().driver().transaction()
        steps = 0
        # sqlCursor = pnsqlcursor.PNSqlCursor(None, True, self.db_.dbAux())
        sqlQuery = pnsqlquery.PNSqlQuery(None, "dbAux")
        if sqlQuery.exec_(
            "select relname from pg_class where ( relkind = 'r' ) "
            "and ( relname !~ '^Inv' ) "
            "and ( relname !~ '^pg_' ) and ( relname !~ '^sql_' )"
        ):

            util.setTotalSteps(sqlQuery.size())
            while sqlQuery.next():
                item = sqlQuery.value(0)
                steps = steps + 1
                util.setProgress(steps)
                util.setLabelText(util.translate("application", "Creando índices para %s" % item))
                mtd = self.db_.connManager().manager().metadata(item, True)
                if not mtd:
                    continue
                fL = mtd.fieldList()
                if not fL:
                    continue
                for it in fL:
                    if not it or not it.type() == "pixmap":
                        continue
                    cur = pnsqlcursor.PNSqlCursor(item, True, self.db_.connManager().dbAux())
                    cur.select(it.name() + " not like 'RK@%'")
                    while cur.next():
                        v = cur.value(it.name())
                        if v is None:
                            continue

                        v = self.db_.connManager().manager().storeLargeValue(mtd, v)
                        if v:
                            buf = cur.primeUpdate()
                            buf.setValue(it.name(), v)
                            cur.update(False)

                # sqlCursor.setName(item, True)

        # self.db_.dbAux().driver().commit()
        util.destroyProgressDialog()
        steps = 0
        qry4.exec_("select tablename from pg_tables where schemaname='public'")
        util.createProgressDialog(
            util.translate("application", "Analizando base de datos"), qry4.size()
        )
        while qry4.next():
            item = qry4.value(0)
            util.setLabelText(util.translate("application", "Analizando tabla %s" % item))
            qry5.exec_("vacuum analyze %s" % item)
            steps = steps + 1
            util.setProgress(steps)

        util.destroyProgressDialog()

    def fix_query(self, query: str) -> str:
        """Fix string."""
        # ret_ = query.replace(";", "")
        return query
