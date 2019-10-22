"""
Module for MYISAM2 driver.
"""
from PyQt5.Qt import qWarning  # type: ignore
from PyQt5.QtWidgets import QMessageBox, QWidget  # type: ignore
from pineboolib.application.utils.check_dependencies import check_dependencies
from pineboolib.application import project
import traceback

from . import flmysql_myisam

from pineboolib import logging

from typing import Any, Dict, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401
    from pineboolib.application.database import pnsqlcursor  # noqa: F401

logger = logging.getLogger(__name__)


class FLMYSQL_MYISAM2(flmysql_myisam.FLMYSQL_MYISAM):
    """MYISAM2 Driver class."""

    cursorsArray_: Dict[str, Any]  # IApiCursor

    def __init__(self):
        """Create empty driver."""
        super().__init__()
        self.version_ = "0.8"
        self.conn_ = None
        self.name_ = "FLMYSQL_MyISAM2"
        self.open_ = False
        self.alias_ = "MySQL MyISAM (PyMySQL)"
        self.cursorsArray_ = {}
        self.noInnoDB = True
        self.mobile_ = True
        self.pure_python_ = True
        self.defaultPort_ = 3306
        self.rowsFetched: Dict[str, int] = {}
        self.active_create_index = True
        self.db_ = None
        self.engine_ = None
        self.session_ = None
        self.declarative_base_ = None
        self.lastError_ = None

    def safe_load(self) -> bool:
        """Return if the driver can loads dependencies safely."""
        return check_dependencies({"pymysql": "PyMySQL", "sqlalchemy": "sqlAlchemy"}, False)

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_userName: str, db_password: str
    ) -> Any:
        """Connect to a database."""
        self._dbname = db_name
        check_dependencies({"pymysql": "PyMySQL", "sqlalchemy": "sqlAlchemy"})
        from sqlalchemy import create_engine  # type: ignore
        import pymysql

        try:
            self.conn_ = pymysql.connect(
                host=db_host,
                user=db_userName,
                password=db_password,
                db=db_name,
                charset="utf8",
                autocommit=True,
            )
            self.engine_ = create_engine(
                "mysql+pymysql://%s:%s@%s:%s/%s"
                % (db_userName, db_password, db_host, db_port, db_name)
            )
        except pymysql.Error as e:
            if project._splash:
                project._splash.hide()
            if "Unknown database" in str(e):
                if project._DGI and not project.DGI.localDesktop():
                    return False

                ret = QMessageBox.warning(
                    QWidget(),
                    "Pineboo",
                    "La base de datos %s no existe.\n¿Desea crearla?" % db_name,
                    cast(QMessageBox, QMessageBox.Ok | QMessageBox.No),
                )
                if ret == QMessageBox.No:
                    return False
                else:
                    try:
                        tmpConn = pymysql.connect(
                            host=db_host,
                            user=db_userName,
                            password=db_password,
                            charset="utf8",
                            autocommit=True,
                        )
                        cursor = tmpConn.cursor()
                        try:
                            cursor.execute("CREATE DATABASE %s" % db_name)
                        except Exception:
                            print("ERROR: FLMYSQL2.connect", traceback.format_exc())
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

        if self.conn_:
            self.open_ = True
            # self.conn_.autocommit(True)
            # self.conn_.set_character_set('utf8')

        return self.conn_

    def alterTable2(self, mtd1, mtd2, key: Optional[str], force: bool = False) -> bool:
        """Alter a table following mtd instructions."""
        if not self.db_:
            raise Exception("must be connected")

        util = FLUtil()

        oldMTD = None
        newMTD = None
        doc = QDomDocument("doc")
        docElem = None
        if not util.domDocumentSetContent(doc, mtd1):
            print("FLManager::alterTable : " + util.tr("Error al cargar los metadatos."))
        else:
            docElem = doc.documentElement()
            oldMTD = self.db_.manager().metadata(docElem, True)

        if oldMTD and oldMTD.isQuery():
            return True

        if oldMTD and self.hasCheckColumn(oldMTD):
            return False

        if not util.domDocumentSetContent(doc, mtd2):
            print("FLManager::alterTable : " + util.tr("Error al cargar los metadatos."))
            return False
        else:
            docElem = doc.documentElement()
            newMTD = self.db_.manager().metadata(docElem, True)

        if not oldMTD:
            oldMTD = newMTD

        if not oldMTD.name() == newMTD.name():
            print(
                "FLManager::alterTable : "
                + util.tr("Los nombres de las tablas nueva y vieja difieren.")
            )
            if oldMTD and not oldMTD == newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return False

        oldPK = oldMTD.primaryKey()
        newPK = newMTD.primaryKey()

        if not oldPK == newPK:
            print(
                "FLManager::alterTable : "
                + util.tr("Los nombres de las claves primarias difieren.")
            )
            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return False

        if not force and self.db_.manager().checkMetaData(oldMTD, newMTD):
            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return True

        if not self.db_.manager().existsTable(oldMTD.name()):
            print(
                "FLManager::alterTable : "
                + util.tr(
                    "La tabla %s antigua de donde importar los registros no existe." % oldMTD.name()
                )
            )
            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return False

        fieldList = oldMTD.fieldList()
        # oldField = None

        if not fieldList:
            print("FLManager::alterTable : " + util.tr("Los antiguos metadatos no tienen campos."))
            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return False

        fieldNamesOld = []
        if not force:
            for it in fieldList:
                if newMTD.field(it.name()) is not None:
                    fieldNamesOld.append(it.name())

        renameOld = "%salteredtable%s" % (
            oldMTD.name()[0:5],
            QDateTime().currentDateTime().toString("ddhhssz"),
        )

        if not self.db_.dbAux():
            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return False

        # self.db_.dbAux().transaction()
        fieldList = newMTD.fieldList()

        if not fieldList:
            qWarning("FLManager::alterTable : " + util.tr("Los nuevos metadatos no tienen campos"))

            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return False

        q = pnsqlquery.PNSqlQuery(None, "dbAux")
        in_sql = "ALTER TABLE %s RENAME TO %s" % (oldMTD.name(), renameOld)
        logger.warning(in_sql)
        if not q.exec_(in_sql):
            qWarning(
                "FLManager::alterTable : " + util.tr("No se ha podido renombrar la tabla antigua.")
            )

            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return False

        if not self.db_.manager().createTable(newMTD):
            self.db_.dbAux().rollbackTransaction()
            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD

            return False

        self.db_.dbAux().transaction()

        if not force and key and len(key) == 40:
            c = pnsqlcursor.PNSqlCursor("flfiles", True, self.db_.dbAux())
            # oldCursor.setModeAccess(oldCursor.Browse)
            c.setForwardOnly(True)
            c.setFilter("nombre='%s.mtd'" % renameOld)
            c.select()
            if not c.next():
                # c.setModeAccess(c.Insert)
                # c.refreshBuffer()
                # c.setValueBuffer("nombre","%s.mtd" % renameOld)
                # c.setValueBuffer("contenido", mtd1)
                # c.setValueBuffer("sha", key)
                # c.commitBuffer()

                in_sql = (
                    "INSERT INTO flfiles(nombre,contenido,idmodulo,sha) VALUES ('%s.mtd','%s','%s','%s')"
                    % (
                        renameOld,
                        mtd1,
                        self.db_.managerModules().idModuleOfFile("%s.mtd" % oldMTD.name()),
                        key,
                    )
                )
                logger.warning(in_sql)
                q.exec_(in_sql)

        ok = False
        if force and fieldNamesOld:
            # sel = fieldNamesOld.join(",")
            # in_sql = "INSERT INTO %s(%s) SELECT %s FROM %s" % (newMTD.name(), sel, sel, renameOld)
            # logger.warning(in_sql)
            # ok = q.exec_(in_sql)
            if not ok:
                self.db_.dbAux().rollbackTransaction()
                if oldMTD and oldMTD != newMTD:
                    del oldMTD
                if newMTD:
                    del newMTD

            return self.alterTable2(mtd1, mtd2, key, True)

        if not ok:

            from pymysql.cursors import DictCursor  # type: ignore

            oldCursor = self.conn_.cursor(DictCursor)
            # print("Lanzando!!", "SELECT * FROM %s WHERE 1 = 1" % (renameOld))
            oldCursor.execute("SELECT * FROM %s WHERE 1 = 1" % (renameOld))
            result_set = oldCursor.fetchall()
            totalSteps = len(result_set)
            # oldCursor = pnsqlcursor.PNSqlCursor(renameOld, True, "dbAux")
            # oldCursor.setModeAccess(oldCursor.Browse)
            # oldCursor.setForwardOnly(True)
            # oldCursor.select()
            # totalSteps = oldCursor.size()

            util.createProgressDialog(
                util.tr("Reestructurando registros para %s...") % newMTD.alias(), totalSteps
            )
            util.setLabelText(util.tr("Tabla modificada"))

            step = 0
            newBuffer = None
            newField = None
            listRecords = []
            newBufferInfo = self.recordInfo2(newMTD.name())
            vector_fields = {}
            default_values = {}
            v = None

            for it2 in fieldList:
                oldField = oldMTD.field(it2.name())
                if (
                    oldField is None
                    or not result_set
                    or oldField.name() not in result_set[0].keys()
                ):
                    if oldField is None:
                        oldField = it2
                    if it2.type() != PNFieldMetaData.Serial:
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
                        v = row[newField.name()]
                        if (
                            (not oldField.allowNull() or not newField.allowNull())
                            and (v is None)
                            and newField.type() != PNFieldMetaData.Serial
                        ):
                            defVal = newField.defaultValue()
                            if defVal is not None:
                                v = defVal

                    if v is not None and newField.type() == "string" and newField.length() > 0:
                        v = v[: newField.length()]

                    if (not oldField.allowNull() or not newField.allowNull()) and v is None:
                        if oldField.type() == PNFieldMetaData.Serial:
                            v = int(self.nextSerialVal(newMTD.name(), newField.name()))
                        elif oldField.type() in ["int", "uint", "bool", "unlock"]:
                            v = 0
                        elif oldField.type() == "double":
                            v = 0.0
                        elif oldField.type() == "time":
                            v = QTime.currentTime()
                        elif oldField.type() == "date":
                            v = QDate.currentDate()
                        else:
                            v = "NULL"[: newField.length()]

                    # new_b = []
                    for buffer in newBuffer:
                        if buffer[0] == newField.name():
                            new_buffer = []
                            new_buffer.append(buffer[0])
                            new_buffer.append(buffer[1])
                            new_buffer.append(newField.allowNull())
                            new_buffer.append(buffer[3])
                            new_buffer.append(buffer[4])
                            new_buffer.append(v)
                            new_buffer.append(buffer[6])
                            listRecords.append(new_buffer)
                            break
                    # newBuffer.setValue(newField.name(), v)

                if listRecords:
                    if not self.insertMulti(newMTD.name(), listRecords):
                        ok = False
                    listRecords = []

            util.setProgress(totalSteps)

        util.destroyProgressDialog()
        if ok:
            self.db_.dbAux().commit()

            if force:
                q.exec_("DROP TABLE %s CASCADE" % renameOld)
        else:
            self.db_.dbAux().rollbackTransaction()

            q.exec_("DROP TABLE %s CASCADE" % oldMTD.name())
            q.exec_("ALTER TABLE %s RENAME TO %s" % (renameOld, oldMTD.name()))

            if oldMTD and oldMTD != newMTD:
                del oldMTD
            if newMTD:
                del newMTD
            return False

        if oldMTD and oldMTD != newMTD:
            del oldMTD
        if newMTD:
            del newMTD

        return True

    def normalizeValue(self, text: str) -> str:
        """Escape values, suitable to prevent sql injection."""
        import pymysql

        return pymysql.escape_string(text)
