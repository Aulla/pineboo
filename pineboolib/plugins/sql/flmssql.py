"""Flsqls module."""
from PyQt5 import QtCore, Qt, QtWidgets

from pineboolib.core import decorators
from pineboolib.core import settings

from pineboolib.application.utils import check_dependencies
from pineboolib.application.database import pnsqlquery
from pineboolib.application.database import pnsqlcursor
from pineboolib.application.metadata import pnfieldmetadata
from pineboolib.application.metadata import pntablemetadata
from pineboolib import application, logging

from pineboolib.fllegacy import flutil
from . import pnsqlschema

from xml.etree import ElementTree
import traceback
from typing import Optional, Union, List, Dict, Any, cast


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

    def safe_load(self) -> bool:
        """Return if the driver can loads dependencies safely."""
        return check_dependencies.check_dependencies(
            {"pymssql": "pymssql", "sqlalchemy": "sqlAlchemy"}, False
        )

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_userName: str, db_password: str
    ) -> Any:
        """Connecto to database."""
        self._dbname = db_name
        check_dependencies.check_dependencies({"pymssql": "pymssql", "sqlalchemy": "sqlAlchemy"})
        import pymssql  # type: ignore

        # from psycopg2.extras import LoggingConnection  # type: ignore

        LOGGER.debug = LOGGER.trace  # type: ignore  # Send Debug output to Trace

        # conninfostr = (
        #    "DRIVER={ODBC Driver 17 for SQL Server};SERVER='%s,%s';DATABASE='%s':UID='%s';PWD='%s'"
        #    % (db_host, db_port, db_name, db_userName, db_password)
        # )

        try:
            self.conn_ = pymssql.connect(
                server=db_host,
                user=db_userName,
                password=db_password,
                database=db_name,
                port=db_port,
            )
            # self.conn_.initialize(LOGGER)

            if settings.CONFIG.value("ebcomportamiento/orm_enabled", False):
                from sqlalchemy import create_engine  # type: ignore

                self.engine_ = create_engine(
                    "mssql+pymssql://%s:%s@%s:%s/%s"
                    % (db_userName, db_password, db_host, db_port, db_name)
                )
        except Exception as e:
            LOGGER.warning(e)
            if application.PROJECT._splash:
                application.PROJECT._splash.hide()

            if not application.PROJECT.DGI.localDesktop():
                return False

            if "does not exist" in str(e) or "no existe" in str(e):
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
                        tmpConn = pymssql.connect(
                            server=db_host, port=db_port, user="SA", password=db_password
                        )

                        # tmpConn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                        tmpConn.autocommit(True)
                        cursor = tmpConn.cursor()
                        try:
                            cursor.execute("CREATE DATABASE %s" % db_name)
                            tmpConn.autocommit(False)
                        except Exception:
                            LOGGER.warning(traceback.format_exc())
                            cursor.execute("ROLLBACK")
                            cursor.close()
                            tmpConn.autocommit(False)
                            return False
                        cursor.close()

                        return self.connect(db_name, db_host, db_port, db_userName, db_password)
                    except Exception:
                        LOGGER.warning(traceback.format_exc())

                        QtWidgets.QMessageBox.information(
                            QtWidgets.QWidget(),
                            "Pineboo",
                            "ERROR: No se ha podido crear la Base de Datos %s" % db_name,
                            QtWidgets.QMessageBox.Ok,
                        )
                        print("ERROR: No se ha podido crear la Base de Datos %s" % db_name)
                        return False
            else:
                QtWidgets.QMessageBox.information(
                    QtWidgets.QWidget(),
                    "Pineboo",
                    "Error de conexión\n%s" % str(e),
                    QtWidgets.QMessageBox.Ok,
                )
                return False

        self.conn_.autocommit(True)  # Posiblemente tengamos que ponerlo a
        # false para que las transacciones funcionen
        # self.conn_.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        if self.conn_:
            self.open_ = True

        # try:
        #    self.conn_.set_client_encoding("UTF8")
        # except Exception:
        #    LOGGER.warning(traceback.format_exc())

        return self.conn_

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

    def tables(self, typeName: Optional[str] = None) -> List[str]:
        """Return a tables list specified by type."""
        tl: List[str] = []
        if not self.isOpen():
            return tl

        t = pnsqlquery.PNSqlQuery()
        t.setForwardOnly(True)

        if not typeName or typeName == "Tables":
            t.exec_("SELECT * FROM SYSOBJECTS WHERE xtype ='U'")
            while t.next():
                tl.append(str(t.value(0)))

        if not typeName or typeName == "Views":
            t.exec_("SELECT * FROM SYSOBJECTS WHERE xtype ='V'")
            while t.next():
                tl.append(str(t.value(0)))
        if not typeName or typeName == "SystemTables":
            t.exec_("SELECT * FROM SYSOBJECTS WHERE xtype ='S'")
            while t.next():
                tl.append(str(t.value(0)))

        del t
        return tl

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
            QtCore.QDateTime().currentDateTime().toString("ddhhssz"),
        )

        if self.db_ is None:
            raise Exception("alterTable3. self.db_ is None")

        self.db_.connManager().dbAux().transaction()

        q = pnsqlquery.PNSqlQuery(None, self.db_.connManager().dbAux())

        constraintName = "%s_key" % old_mtd.name()

        if not q.exec_(
            "ALTER TABLE %s DROP CONSTRAINT %s CASCADE" % (old_mtd.name(), constraintName)
        ):
            self.db_.connManager().dbAux().rollbackTransaction()
            return False

        for oldField in fieldList:
            if oldField.isCheck():
                return False
            if oldField.isUnique():
                constraintName = "%s_%s_key" % (old_mtd.name(), oldField.name())
                if not q.exec_(
                    "ALTER TABLE %s DROP CONSTRAINT %s CASCADE" % (old_mtd.name(), constraintName)
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
        progress = QtWidgets.QProgressDialog(
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
                            v = QtCore.QTime().currentTime()
                        elif oldField.type() == "date":
                            v = QtCore.QDate().currentDate()
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
        # LOGGER.warning("alterTable2 FIXME::Me quedo colgado al hacer createTable --> existTable")
        util = flutil.FLUtil()

        old_mtd = None
        new_mtd = None

        if not self.isOpen():
            raise Exception("alterTable2: Database not open")

        if self.db_ is None:
            raise Exception("alterTable2. self.db_ is None")

        if not mtd1:
            LOGGER.warning(
                "FLManager::alterTable : "
                + util.translate("application", "Error al cargar los metadatos.")
            )
        else:
            xml = ElementTree.fromstring(mtd1)
            old_mtd = self.db_.connManager().manager().metadata(xml, True)

        if old_mtd and old_mtd.isQuery():
            return True

        if not mtd2:
            LOGGER.warning(
                "FLManager::alterTable : "
                + util.translate("application", "Error al cargar los metadatos.")
            )
            return False
        else:
            xml = ElementTree.fromstring(mtd2)
            new_mtd = self.db_.connManager().manager().metadata(xml, True)

        if not old_mtd:
            old_mtd = new_mtd

        if not old_mtd.name() == new_mtd.name():
            LOGGER.warning(
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
            LOGGER.warning(
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
            LOGGER.warning(
                "FLManager::alterTable : "
                + util.translate(
                    "application",
                    "La tabla %s antigua de donde importar los registros no existe."
                    % (old_mtd.name()),
                )
            )
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        fieldList = old_mtd.fieldList()
        oldField = None

        if not fieldList:
            LOGGER.warning(
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
            QtCore.QDateTime().currentDateTime().toString("ddhhssz"),
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
                c2.execute(
                    "ALTER TABLE %s DROP CONSTRAINT %s CASCADE" % (old_mtd.name(), constraintName)
                )

        # if not q.exec_("ALTER TABLE %s RENAME TO %s" % (old_mtd.name(), renameOld)):
        #    LOGGER.warning(
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
                            v = QtCore.QTime.currentTime()
                        elif oldField.type() == "date":
                            v = QtCore.QDate.currentDate()
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

    def Mr_Proper(self) -> None:
        """Clear all garbage data."""
        util = flutil.FLUtil()

        if not self.isOpen():
            raise Exception("Mr_Proper: Database not open")

        if self.db_ is None:
            raise Exception("Mr_Proper. self.db_ is None")

        self.db_.connManager().dbAux().transaction()

        qry = pnsqlquery.PNSqlQuery(None, "dbAux")
        # qry2 = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry3 = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry4 = pnsqlquery.PNSqlQuery(None, "dbAux")
        # qry5 = pnsqlquery.PNSqlQuery(None, "dbAux")
        cur = self.db_.connManager().dbAux().cursor()
        steps = 0

        rx = Qt.QRegExp("^.*\\d{6,9}$")
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

                    LOGGER.warning(msg)
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
                # mtd = self.db_.connManager().manager().metadata(item, True)
                # if not mtd:
                #    continue

                # field_list = mtd.fieldList()

                # for it in field_list:
                #    if it.type() == "pixmap":
                #        cursor_ = pnsqlcursor.PNSqlCursor(item, True, "dbAux")
                #        cursor_.select(it.name() + " not like 'RK@%'")
                #        while cursor_.next():
                #            buf = cursor_.buffer()
                #            v = buf.value(it.name())
                #            if v is None:
                #                continue

                #            v = self.db_.connManager().manager().storeLargeValue(mtd, v)
                #            if v:
                #                buf = cursor_.primeUpdate()
                #                buf.setValue(it.name(), v)
                #                cursor_.update(False)

                # sqlCursor.setName(item, True)

        # self.db_.dbAux().driver().commit()
        self.db_.connManager().dbAux().commitTransaction()
        util.destroyProgressDialog()
        steps = 0
        qry4.exec_("select tablename from pg_tables where schemaname='public'")
        util.createProgressDialog(
            util.translate("application", "Analizando base de datos"), qry4.size()
        )
        while qry4.next():
            item = qry4.value(0)
            util.setLabelText(util.translate("application", "Analizando tabla %s" % item))
            cur.execute("vacuum analyze %s" % item)
            steps = steps + 1
            util.setProgress(steps)

        util.destroyProgressDialog()

    def fix_query(self, query: str) -> str:
        """Fix string."""
        # ret_ = query.replace(";", "")
        return query

    # def isOpen(self):
    #    return self.conn_.closed == 0
