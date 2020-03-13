"""
Module for MYISAM driver.
"""

import traceback

from PyQt5 import Qt, QtCore, QtWidgets

from pineboolib.application.database import pnsqlcursor, pnsqlquery
from pineboolib.application.metadata import pnfieldmetadata

from pineboolib.fllegacy import flutil
from pineboolib import logging
from . import pnsqlschema

from xml.etree import ElementTree

from typing import Any, Optional, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401

LOGGER = logging.get_logger(__name__)


class FLMYSQL_MYISAM(pnsqlschema.PNSqlSchema):
    """MYISAM Driver class."""

    _default_charset: str

    def __init__(self):
        """Create empty driver."""
        super().__init__()
        self.version_ = "0.9"
        self.name_ = "FLMYSQL_MyISAM"
        self.alias_ = "MySQL MyISAM (MYSQLDB)"
        self.noInnoDB = True
        self.defaultPort_ = 3306
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
        self._safe_load = {"MySQLdb": "mysqlclient", "sqlalchemy": "sqlAlchemy"}
        self._database_not_found_keywords = ["Unknown database"]
        self._default_charset = "DEFAULT CHARACTER SET = utf8 COLLATE = utf8_bin"

    def getEngine(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return sqlAlchemy connection."""
        from sqlalchemy import create_engine  # type: ignore

        return create_engine("mysql+mysqldb://%s:%s@%s:%s/%s" % (usern, passw_, host, port, name))

    def getConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import MySQLdb  # type: ignore

        conn_ = None
        try:
            conn_ = MySQLdb.connect(host, usern, passw_, name)
        except MySQLdb.OperationalError as error:
            self.setLastError(str(error), "CONNECT")

        return conn_

    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import MySQLdb  # type: ignore

        conn_ = None
        try:
            conn_ = MySQLdb.connect(host, usern, passw_)
        except MySQLdb.OperationalError as error:
            self.setLastError(str(error), "CONNECT")

        return conn_

    def loadSpecialConfig(self) -> None:
        """Set special config."""

        self.conn_.autocommit(True)
        self.conn_.set_character_set("utf8")

    def tables(self, type_name: Optional[str] = "") -> List[str]:
        """Return a tables list specified by type."""
        table_list: List[str] = []
        result_list: List[Any] = []
        if self.isOpen():

            if type_name in ("Tables", ""):
                cursor = self.execute_query(
                    "SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_TYPE LIKE 'BASE TABLE' AND TABLE_SCHEMA LIKE '%s'"
                    % self.DBName()
                )
                result_list += cursor.fetchall()

            if type_name in ("Views", ""):
                cursor = self.execute_query(
                    "SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_TYPE LIKE 'VIEW' AND TABLE_SCHEMA LIKE '%s'"
                    % self.DBName()
                )
                result_list += cursor.fetchall()

            if type_name in ("SystemTables", ""):
                cursor = self.execute_query(
                    "SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_TYPE LIKE 'SYSTEM VIEW'"
                )
                result_list += cursor.fetchall()

        for item in result_list:
            table_list.append(item[0])

        return table_list

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Get next serial value for given table and field."""
        if not self.isOpen():
            raise Exception("beginTransaction: Database not open")

        # if not self.transaction():
        #    self.setLastError("No se puede iniciar la transacción", "BEGIN WORK")
        #    return None

        max = 0
        cur_max = 0
        updateQry = False
        ret = None

        q = pnsqlquery.PNSqlQuery()
        q.setSelect("max(%s)" % field)
        q.setFrom(table)
        q.setWhere("1 = 1")
        if not q.exec_():
            LOGGER.warning("not exec sequence")
            return None
        elif q.first():
            v = q.value(0)
            if v is not None:
                max = v

        if not self.conn_:
            raise Exception("must be connected")
        cursor = self.conn_.cursor()

        strQry: Optional[str] = "SELECT seq FROM flseqs WHERE tabla = '%s' AND campo ='%s'" % (
            table,
            field,
        )
        try:
            cur_max = 0
            cursor.execute(strQry)
            line = cursor.fetchone()
            if line:
                cur_max = line[0]
        except Exception:
            LOGGER.warning(
                "%s:: La consulta a la base de datos ha fallado", self.name_, traceback.format_exc()
            )
            self.rollbackTransaction()
            return

        if cur_max > 0:
            updateQry = True
            ret = cur_max
        else:
            ret = max

        ret += 1
        strQry = None
        if updateQry:
            if ret > cur_max:
                strQry = "UPDATE flseqs SET seq=%s WHERE tabla = '%s' AND campo = '%s'" % (
                    ret,
                    table,
                    field,
                )
        else:
            strQry = "INSERT INTO flseqs (tabla,campo,seq) VALUES('%s','%s',%s)" % (
                table,
                field,
                ret,
            )

        if strQry is not None:
            try:
                cursor.execute(strQry)
            except Exception:
                LOGGER.warning(
                    "%s:: La consulta a la base de datos ha fallado\n %s",
                    self.name_,
                    traceback.format_exc(),
                )
                self.rollbackTransaction()

                return

        # if not self.commitTransaction():
        #    LOGGER.warning("%s:: No se puede aceptar la transacción" % self.name_)
        #    return None

        return ret

    def existsTable(self, name: str) -> bool:
        """Return if exists a table specified by name."""
        if not self.isOpen():
            LOGGER.warning("existsTable: Database not open")
            return False

        cursor = self.cursor()

        cursor.execute("SHOW TABLES LIKE '%s'" % name)

        result = cursor.fetchall()

        return True if result else False

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
        else:
            LOGGER.warning("seType: unknown type %s", type_)
            leng = 0

        return "%s(%s)" % (res_, leng) if leng else res_

    def sqlCreateTable(
        self, tmd: "pntablemetadata.PNTableMetaData", create_index: bool = True
    ) -> Optional[str]:
        """Create a table from given MTD."""

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
                    LOGGER.debug(u"FLManager : No se ha podido crear la tabla " + tmd.name())
                    LOGGER.debug(
                        u"FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno."
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
                    return None
            else:

                sql += " UNIQUE" if field.isUnique() else ""
                sql += " NULL" if field.allowNull() else " NOT NULL"

            if number != len(field_list) - 1:
                sql += ","

        engine = ") ENGINE=INNODB" if not self.noInnoDB else ") ENGINE=MyISAM"
        sql += engine

        sql += " %s" % self._default_charset

        return sql

    def Mr_Proper(self) -> None:
        """Cleanup database like mr.proper."""
        if not self.isOpen():
            raise Exception("Mr_Proper: Database not open")

        util = flutil.FLUtil()
        if not self.db_:
            raise Exception("must be connected")
        self.db_.connManager().dbAux().transaction()

        qry = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry2 = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry3 = pnsqlquery.PNSqlQuery(None, "dbAux")
        # qry4 = pnsqlquery.PNSqlQuery(None, "dbAux")
        # qry5 = pnsqlquery.PNSqlQuery(None, "dbAux")
        steps = 0
        self.active_create_index = False

        rx = Qt.QRegExp("^.*\\d{6,9}$")
        if rx in self.tables():
            listOldBks = self.tables()[rx]
        else:
            listOldBks = []

        qry.exec_(
            "select nombre from flfiles where nombre regexp"
            "'.*[[:digit:]][[:digit:]][[:digit:]][[:digit:]]-[[:digit:]][[:digit:]].*:[[:digit:]][[:digit:]]$' or nombre regexp"
            "'.*alteredtable[[:digit:]][[:digit:]][[:digit:]][[:digit:]].*' or (bloqueo=0 and nombre like '%.mtd')"
        )

        util.createProgressDialog(
            util.translate("SqlDriver", "Borrando backups"), len(listOldBks) + qry.size() + 2
        )

        while qry.next():
            item = qry.value(0)
            util.setLabelText(util.translate("SqlDriver", "Borrando registro %s") % item)
            qry2.exec_("DELETE FROM flfiles WHERE nombre ='%s'" % item)
            if item.find("alteredtable") > -1:
                if self.existsTable(item.replace(".mtd", "")):
                    util.setLabelText(util.translate("SqlDriver", "Borrando tabla %s" % item))
                    qry2.exec_("DROP TABLE %s CASCADE" % item.replace(".mtd", ""))

            steps = steps + 1
            util.setProgress(steps)

        for item in listOldBks:
            if self.existsTable(item):
                util.setLabelText(util.translate("SqlDriver", "Borrando tabla %s" % item))
                qry2.exec_("DROP TABLE %s CASCADE" % item)

            steps = steps + 1
            util.setProgress(steps)

        util.setLabelText(util.translate("SqlDriver", "Inicializando cachés"))
        steps = steps + 1
        util.setProgress(steps)
        qry.exec_("DELETE FROM flmetadata")
        qry.exec_("DELETE FROM flvar")
        self.db_.connManager().manager().cleanupMetaData()
        # self.db_.connManager().driver().commit()
        util.destroyProgressDialog()

        steps = 0
        qry3.exec_("SHOW TABLES")

        util.createProgressDialog(
            util.translate("SqlDriver", "Comprobando base de datos"), qry3.size()
        )
        while qry3.next():
            item = qry3.value(0)
            # print("Comprobando", item)
            # qry2.exec_("alter table %s convert to character set utf8 collate utf8_bin" % item)
            mustAlter = self.mismatchedTable(item, item)
            if mustAlter:
                conte = self.db_.connManager().managerModules().content("%s.mtd" % item)
                if conte:
                    msg = util.translate(
                        "SqlDriver",
                        "La estructura de los metadatos de la tabla '%s' y su "
                        "estructura interna en la base de datos no coinciden. "
                        "Intentando regenerarla." % item,
                    )

                    LOGGER.warning("%s", msg)
                    self.alterTable2(conte, conte, None, True)

            steps = steps + 1
            util.setProgress(steps)

        self.db_.connManager().dbAux().driver().transaction()
        self.active_create_index = True
        steps = 0
        # sqlCursor = pnsqlcursor.PNSqlCursor(None, True, self.db_.connManager().dbAux())
        engine = "MyISAM" if self.noInnoDB else "INNODB"
        convert_engine = False
        do_ques = True

        sqlQuery = pnsqlquery.PNSqlQuery(None, self.db_.connManager().dbAux())
        sql_query2 = pnsqlquery.PNSqlQuery(None, self.db_.connManager().dbAux())
        if sqlQuery.exec_("SHOW TABLES"):
            util.setTotalSteps(sqlQuery.size())
            while sqlQuery.next():
                item = sqlQuery.value(0)
                steps = steps + 1
                util.setProgress(steps)
                util.setLabelText(util.translate("SqlDriver", "Creando índices para %s" % item))
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
                        v = cur.valueBuffer(it.name())
                        if v is None:
                            continue

                        v = self.db_.connManager().manager().storeLargeValue(mtd, v)
                        if v:
                            buf = cur.primeUpdate()
                            buf.setValue(it.name(), v)
                            cur.update(False)

                # sqlCursor.setName(item, True)

                # self.db_.connManager().dbAux().driver().commit()
                sql_query2.exec_(
                    "show table status where Engine='%s' and Name='%s'" % (engine, item)
                )
                if not sql_query2.next():
                    if do_ques:
                        res = QtWidgets.QMessageBox.question(
                            QtWidgets.QWidget(),
                            util.translate("SqlDriver", "Mr. Proper"),
                            util.translate(
                                "SqlDriver",
                                "Existen tablas que no son del tipo %s utilizado por el driver de la conexión actual.\n"
                                "Ahora es posible convertirlas, pero asegurése de tener una COPIA DE SEGURIDAD,\n"
                                "se pueden peder datos en la conversión de forma definitiva.\n\n"
                                "¿ Quiere convertirlas ?" % (engine),
                            ),
                            QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No,
                        )
                        if res == QtWidgets.QMessageBox.Yes:
                            convert_engine = True

                    do_ques = False
                    if convert_engine:
                        conte = self.db_.connManager().managerModules().content("%s.mtd" % item)
                        self.alterTable2(conte, conte, None, True)

        self.active_create_index = False
        util.destroyProgressDialog()

    def alterTable(
        self,
        mtd1: Union[str, "pntablemetadata.PNTableMetaData"],
        mtd2: Optional[str] = None,
        key: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Alter a table following mtd instructions."""
        if not isinstance(mtd1, str):
            raise Exception("unexpected PNTableMetaData")
        else:
            if mtd2 is None:
                raise Exception("mtd2 is empty!")

            return self.alterTable2(mtd1, mtd2, key, force)

    def dict_cursor(self) -> Any:
        """Return dict cursor."""

        from MySQLdb.cursors import DictCursor  # type: ignore

        return DictCursor

    def alterTable2(self, mtd1: str, mtd2: str, key: Optional[str], force: bool = False) -> bool:
        """Alter a table following mtd instructions."""
        if not self.isOpen():
            raise Exception("alterTable2: Database not open")
            return False

        if not self.db_:
            raise Exception("must be connected")

        util = flutil.FLUtil()

        old_mtd = None
        new_mtd = None

        if not mtd1:
            print(
                "FLManager::alterTable : "
                + util.translate("SqlDriver", "Error al cargar los metadatos.")
            )
        else:
            xml = ElementTree.fromstring(mtd1)
            old_mtd = self.db_.connManager().manager().metadata(xml, True)

        if old_mtd and old_mtd.isQuery():
            return True

        if old_mtd and self.hasCheckColumn(old_mtd):
            return False

        if not mtd2:
            print(
                "FLManager::alterTable : "
                + util.translate("SqlDriver", "Error al cargar los metadatos.")
            )
            return False
        else:
            xml = ElementTree.fromstring(mtd2)
            new_mtd = self.db_.connManager().manager().metadata(xml, True)

        if not old_mtd:
            old_mtd = new_mtd

        if not old_mtd.name() == new_mtd.name():
            print(
                "FLManager::alterTable : "
                + util.translate("SqlDriver", "Los nombres de las tablas nueva y vieja difieren.")
            )
            if old_mtd and not old_mtd == new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        oldPK = old_mtd.primaryKey()
        newPK = new_mtd.primaryKey()

        if not oldPK == newPK:
            print(
                "FLManager::alterTable : "
                + util.translate("SqlDriver", "Los nombres de las claves primarias difieren.")
            )
            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        if not force and self.db_.connManager().manager().checkMetaData(old_mtd, new_mtd):
            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return True

        if not self.db_.connManager().manager().existsTable(old_mtd.name()):
            print(
                "FLManager::alterTable : "
                + util.translate(
                    "SqlDriver",
                    "La tabla %s antigua de donde importar los registros no existe."
                    % old_mtd.name(),
                )
            )
            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        fieldList = old_mtd.fieldList()
        # oldField = None

        if not fieldList:
            print(
                "FLManager::alterTable : "
                + util.translate("SqlDriver", "Los antiguos metadatos no tienen campos.")
            )
            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        fieldNamesOld = []
        if not force:
            for it in fieldList:
                if new_mtd.field(it.name()) is not None:
                    fieldNamesOld.append(it.name())

        renameOld = "%salteredtable%s" % (
            old_mtd.name()[0:5],
            QtCore.QDateTime().currentDateTime().toString("ddhhssz"),
        )

        if not self.db_.connManager().dbAux():
            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        # self.db_.connManager().dbAux().transaction()
        fieldList = new_mtd.fieldList()

        if not fieldList:
            LOGGER.warning(
                "FLManager::alterTable : "
                + util.translate("SqlDriver", "Los nuevos metadatos no tienen campos")
            )

            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        q = pnsqlquery.PNSqlQuery(None, "dbAux")
        in_sql = "ALTER TABLE %s RENAME TO %s" % (old_mtd.name(), renameOld)
        LOGGER.warning(in_sql)
        if not q.exec_(in_sql):
            LOGGER.warning(
                "FLManager::alterTable : "
                + util.translate("SqlDriver", "No se ha podido renombrar la tabla antigua.")
            )

            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        if not self.db_.connManager().manager().createTable(new_mtd):
            self.db_.connManager().dbAux().rollbackTransaction()
            if old_mtd and old_mtd != new_mtd:
                del old_mtd
            if new_mtd:
                del new_mtd

            return False

        self.db_.connManager().dbAux().transaction()

        if not force and key and len(key) == 40:
            c = pnsqlcursor.PNSqlCursor("flfiles", True, self.db_.connManager().dbAux())
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
                        self.db_.connManager()
                        .managerModules()
                        .idModuleOfFile("%s.mtd" % old_mtd.name()),
                        key,
                    )
                )
                LOGGER.warning(in_sql)
                q.exec_(in_sql)

        ok = False
        if force and fieldNamesOld:
            # sel = fieldNamesOld.join(",")
            # in_sql = "INSERT INTO %s(%s) SELECT %s FROM %s" % (new_mtd.name(), sel, sel, renameOld)
            # LOGGER.warning(in_sql)
            # ok = q.exec_(in_sql)
            if not ok:
                self.db_.connManager().dbAux().rollbackTransaction()
                if old_mtd and old_mtd != new_mtd:
                    del old_mtd
                if new_mtd:
                    del new_mtd

            return self.alterTable2(mtd1, mtd2, key, True)

        if not ok:

            oldCursor = self.conn_.cursor(self.dict_cursor())
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
                util.translate("SqlDriver", "Reestructurando registros para %s...")
                % new_mtd.alias(),
                totalSteps,
            )
            util.setLabelText(util.translate("SqlDriver", "Tabla modificada"))

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
                if (
                    oldField is None
                    or not result_set
                    or oldField.name() not in result_set[0].keys()
                ):
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
                        v = row[newField.name()]
                        if (
                            (not oldField.allowNull() or not newField.allowNull())
                            and (v is None)
                            and newField.type() != pnfieldmetadata.PNFieldMetaData.Serial
                        ):
                            defVal = newField.defaultValue()
                            if defVal is not None:
                                v = defVal

                    if v is not None and newField.type() == "string" and newField.length() > 0:
                        v = v[: newField.length()]

                    if (not oldField.allowNull() or not newField.allowNull()) and v is None:
                        if oldField.type() == pnfieldmetadata.PNFieldMetaData.Serial:
                            v = int(self.nextSerialVal(new_mtd.name(), newField.name()))
                        elif oldField.type() in ["int", "uint", "bool", "unlock"]:
                            v = 0
                        elif oldField.type() == "double":
                            v = 0.0
                        elif oldField.type() == "time":
                            v = QtCore.QTime.currentTime()
                        elif oldField.type() == "date":
                            v = QtCore.QDate.currentDate()
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
                    if not self.insertMulti(new_mtd.name(), listRecords):
                        ok = False
                    listRecords = []

            util.setProgress(totalSteps)

        util.destroyProgressDialog()
        if ok:
            self.db_.connManager().dbAux().commit()

            if force:
                q.exec_("DROP TABLE %s CASCADE" % renameOld)
        else:
            self.db_.connManager().dbAux().rollbackTransaction()

            q.exec_("DROP TABLE %s CASCADE" % old_mtd.name())
            q.exec_("ALTER TABLE %s RENAME TO %s" % (renameOld, old_mtd.name()))

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

    def recordInfo2(self, tablename: str) -> List[list]:
        """Obtain current cursor information on columns."""
        if not self.isOpen():
            raise Exception("recordInfo2: conn not opened")
        if not self.conn_:
            raise Exception("must be connected")
        info = []
        cursor = self.conn_.cursor()

        cursor.execute("SHOW FIELDS FROM %s" % tablename)
        # print("Campos", tablename)
        for field in cursor.fetchall():
            col_name = field[0]
            allow_null = True if field[2] == "NO" else False
            tipo_ = field[1]
            if field[1].find("(") > -1:
                tipo_ = field[1][: field[1].find("(")]

            # len_
            len_ = "0"
            if field[1].find("(") > -1:
                len_ = field[1][field[1].find("(") + 1 : field[1].find(")")]

            precision_ = 0

            tipo_ = self.decodeSqlType(tipo_)

            if tipo_ in ["uint", "int", "double"]:
                len_ = "0"
                # print("****", tipo_, field)
            else:
                if len_.find(",") > -1:
                    precision_ = int(len_[len_.find(",") :])
                    len_ = len_[: len_.find(",")]

            len_n = int(len_)

            if len_n == 255 and tipo_ == "string":
                len_n = 0

            default_value_ = field[4]
            primary_key_ = True if field[3] == "PRI" else False
            # print("***", field)
            # print("Nombre:", col_name)
            # print("Tipo:", tipo_)
            # print("Nulo:", allow_null)
            # print("longitud:", len_)
            # print("Precision:", precision_)
            # print("Defecto:", default_value_)
            info.append(
                [col_name, tipo_, allow_null, len_n, precision_, default_value_, primary_key_]
            )
            # info.append(desc[0], desc[1], not desc[6], , part_decimal, default_value, is_primary_key)

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
        elif t == "mediumtext":
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

        else:
            LOGGER.warning("formato desconocido %s", ret)

        return ret

    def normalizeValue(self, text: str) -> str:
        """Escape values, suitable to prevent sql injection."""

        import MySQLdb

        return MySQLdb.escape_string(text).decode("utf-8")
