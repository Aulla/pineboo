"""Flqpsql module."""
from PyQt5 import QtCore, Qt, QtWidgets

from pineboolib.application.database import pnsqlquery
from pineboolib.application.database import pnsqlcursor
from pineboolib.application.metadata import pnfieldmetadata
from pineboolib.application.metadata import pntablemetadata
from pineboolib import logging

from pineboolib.fllegacy import flutil
from . import pnsqlschema

from xml.etree import ElementTree
import traceback
from typing import Optional, Union, List, Dict, Any


LOGGER = logging.get_logger(__name__)


class FLQPSQL(pnsqlschema.PNSqlSchema):
    """FLQPSQL class."""

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.version_ = "0.9"
        self.name_ = "FLQPSQL"
        self.errorList = []
        self.alias_ = "PostgreSQL (PSYCOPG2)"
        self.defaultPort_ = 5432
        self.rollback_savepoint_command = "ROLLBACK TO SAVEPOINT"
        self.commit_transaction_command = "COMMIT TRANSACTION"
        self._true = True
        self._false = False
        self._like_true = "'t'"
        self._like_false = "'f'"
        self._safe_load = {"psycopg2": "python3-psycopg2", "sqlalchemy": "sqlAlchemy"}
        self._database_not_found_keywords = ["does not exist", "no existe"]

    def getConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import psycopg2  # type: ignore
        from psycopg2.extras import LoggingConnection  # type: ignore

        conn_ = None
        conn_info_str = "dbname=%s host=%s port=%s user=%s password=%s connect_timeout=5" % (
            name,
            host,
            port,
            usern,
            passw_,
        )

        LOGGER.debug = LOGGER.trace  # type: ignore  # Send Debug output to Trace

        try:
            conn_ = psycopg2.connect(conn_info_str, connection_factory=LoggingConnection)
            conn_.initialize(LOGGER)
        except psycopg2.OperationalError as error:
            self.setLastError(str(error), "CONNECT")

        return conn_

    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""
        import psycopg2

        conn_ = self.getConn("postgres", host, port, usern, passw_)
        if conn_ is not None:
            conn_.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        return conn_

    def getEngine(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return sqlAlchemy connection."""
        from sqlalchemy import create_engine  # type: ignore

        return create_engine(
            "postgresql+psycopg2://%s:%s@%s:%s/%s" % (usern, passw_, host, port, name)
        )

    def loadSpecialConfig(self) -> None:
        """Set special config."""
        import psycopg2

        self.conn_.initialize(LOGGER)
        self.conn_.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            self.conn_.set_client_encoding("UTF8")
        except Exception:
            LOGGER.warning(traceback.format_exc())

    def nextSerialVal(self, table: str, field: str) -> Any:
        """Return next serial value."""
        q = pnsqlquery.PNSqlQuery()
        q.setSelect(u"nextval('" + table + "_" + field + "_seq')")
        q.setFrom("")
        q.setWhere("")
        if not q.exec_():
            LOGGER.warning("not exec sequence")
        elif q.first():
            return q.value(0)

        return None

    def setType(self, type_: str, leng: int = 0) -> str:
        """Return type definition."""
        type_ = type_.lower()
        res_ = ""
        if type_ == "int":
            res_ = "INT2"
        elif type_ == "uint":
            res_ = "INT4"
        elif type_ in ("bool", "unlock"):
            res_ = "BOOLEAN"
        elif type_ == "double":
            res_ = "FLOAT8"
        elif type_ == "time":
            res_ = "TIME"
        elif type_ == "date":
            res_ = "DATE"
        elif type_ in ("pixmap", "stringlist"):
            res_ = "TEXT"
        elif type_ == "string":
            res_ = "VARCHAR"
        elif type_ == "bytearray":
            res_ = "BYTEA"
        elif type_ == "timestamp":
            res_ = "TIMESTAMPTZ"
        else:
            LOGGER.warning("seType: unknown type %s", type_)
            leng = 0

        return "%s(%s)" % (res_, leng) if leng else res_

    def existsTable(self, name: str) -> bool:
        """Return if exists a table specified by name."""
        if not self.isOpen():
            LOGGER.warning("PSQLDriver::existsTable: Database not open")
            return False

        cur_ = self.conn_.cursor()
        cur_.execute("select relname from pg_class where relname = '%s'" % name)
        result_ = cur_.fetchone()
        ok = False if result_ is None else True
        return ok

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

            sql += field.name()
            type_ = field.type()
            if type_ == "serial":
                seq = "%s_%s_seq" % (tmd.name(), field.name())
                if self.isOpen() and create_table:
                    cursor = self.execute_query(
                        "SELECT relname FROM pg_class WHERE relname='%s'" % seq
                    )
                    if not cursor.fetchone():
                        try:
                            self.execute_query("CREATE SEQUENCE %s" % seq)
                        except Exception as error:
                            LOGGER.error("%s::sqlCreateTable:%s", __name__, str(error))

                sql += " INT4 DEFAULT NEXTVAL('%s')" % seq
            else:
                if type_ == "unlock":
                    unlocks += 1

                    if unlocks > 1:
                        LOGGER.warning(
                            u"FLManager : No se ha podido crear la tabla %s ", tmd.name()
                        )
                        LOGGER.warning(
                            u"FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno."
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
                    return None
            else:

                sql += " UNIQUE" if field.isUnique() else ""
                sql += " NULL" if field.allowNull() else " NOT NULL"

            if number != len(field_list) - 1:
                sql += ","

        sql += ")"

        return sql

    def recordInfo2(self, tablename: str) -> List[List[Any]]:
        """Return info from a database table."""
        if not self.isOpen():
            raise Exception("recordInfo2: Database not open")

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
        elif type_ == 1184:
            ret = "timestamp"

        return ret

    def tables(self, type_name: Optional[str] = "") -> List[str]:
        """Return a tables list specified by type."""
        table_list: List[str] = []
        result_list: List[Any] = []
        if self.isOpen():

            if type_name in ("Tables", ""):
                cursor = self.execute_query(
                    "select relname from pg_class where ( relkind = 'r' ) AND ( relname !~ '^Inv' ) AND ( relname !~ '^pg_' ) "
                )
                result_list += cursor.fetchall()

            if type_name in ("Views", ""):
                cursor = self.execute_query(
                    "select relname from pg_class where ( relkind = 'v' ) AND ( relname !~ '^Inv' ) AND ( relname !~ '^pg_' ) "
                )
                result_list += cursor.fetchall()
            if type_name in ("SystemTables", ""):
                cursor = self.execute_query(
                    "select relname from pg_class where ( relkind = 'r' ) AND ( relname like 'pg_%' ) "
                )
                result_list += cursor.fetchall()

        for item in result_list:
            table_list.append(item[0])

        return table_list

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

    def declareCursor(
        self, curname: str, fields: str, table: str, where: str, cursor: Any, conn: Any
    ) -> None:
        """Set a refresh query for database."""

        if not self.isOpen():
            raise Exception("declareCursor: Database not open")

        sql = "DECLARE %s CURSOR WITH HOLD FOR SELECT %s FROM %s WHERE %s " % (
            curname,
            fields,
            table,
            where,
        )
        try:
            cursor.execute(sql)
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
        sql_exists = "SELECT name FROM pg_cursors WHERE name = '%s'" % curname
        cursor.execute(sql_exists)
        if cursor.fetchone() is None:
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
        limit = 0
        pos: Optional[int] = None

        if not self.isOpen():
            raise Exception("findRow: Database not open")

        try:
            while True:
                sql = "FETCH %s FROM %s" % ("FIRST" if not limit else limit + 10000, curname)
                cursor.execute(sql)
                data_ = cursor.fetchall()
                if not data_:
                    break
                for n, line in enumerate(data_):
                    if line[field_pos] == value:
                        return limit + n

                limit += len(data_)

        except Exception as e:
            LOGGER.error("finRow: %s", e)
            LOGGER.warning("Detalle:", stack_info=True)

        return pos

    def deleteCursor(self, cursor_name: str, cursor: Any) -> None:
        """Delete cursor."""

        if not self.isOpen():
            raise Exception("deleteCursor: Database not open")

        try:
            sql_exists = "SELECT name FROM pg_cursors WHERE name = '%s'" % cursor_name
            cursor.execute(sql_exists)
            if cursor.fetchone() is None:
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

        if self.constraintExists(constraintName) and not q.exec_(
            "ALTER TABLE %s DROP CONSTRAINT %s CASCADE" % (old_mtd.name(), constraintName)
        ):
            self.db_.connManager().dbAux().rollbackTransaction()
            return False

        for oldField in fieldList:
            if oldField.isCheck():
                return False
            if oldField.isUnique():
                constraintName = "%s_%s_key" % (old_mtd.name(), oldField.name())
                if self.constraintExists(constraintName) and not q.exec_(
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

        if self.constraintExists(constraintName):

            LOGGER.warning(
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
                c2.execute(
                    "ALTER TABLE %s DROP CONSTRAINT %s CASCADE" % (old_mtd.name(), constraintName)
                )

                if self.constraintExists(constraintName):
                    LOGGER.warning(
                        "FLManager : "
                        + util.translate(
                            "application",
                            "En método alterTable, no se ha podido borrar el índice %s_%s_key de la tabla antigua."
                            % (old_mtd.name(), oldField),
                        )
                    )
                    self.db_.connManager().dbAux().rollbackTransaction()
                    if old_mtd and not old_mtd == new_mtd:
                        del old_mtd
                    if new_mtd:
                        del new_mtd

                    return False

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
