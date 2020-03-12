"""Flsqlite module."""

from PyQt5 import QtWidgets, Qt
from pineboolib.core import decorators

from pineboolib.application.utils import path
from pineboolib.application.database import pnsqlquery

from pineboolib import logging, application

from pineboolib.fllegacy import flutil

from . import pnsqlschema

from xml.etree import ElementTree
import os


from typing import Optional, Union, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata

LOGGER = logging.get_logger(__name__)


class FLSQLITE(pnsqlschema.PNSqlSchema):
    """FLSQLITE class."""

    db_filename: Optional[str]
    db_name: str

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.version_ = "0.7"
        self.name_ = "FLsqlite"
        self.errorList = []
        self.alias_ = "SQLite3 (SQLITE3)"
        self.db_filename = None
        self.db_ = None
        self.parseFromLatin = False
        self.mobile_ = True
        self.desktop_file = True
        self._null = ""
        self._text_like = ""
        self._safe_load = {"sqlite3": "sqlite3", "sqlalchemy": "sqlAlchemy"}

    def setDBName(self, name: str):
        """Set DB Name."""

        self.db_name = name
        if name == ":memory:":
            self.db_name = "temp_db"
            self.db_filename = name
            if application.PROJECT._splash:
                application.PROJECT._splash.hide()
        else:
            self.db_filename = path._dir("%s.sqlite3" % self.db_name)

    def loadSpecialConfig(self) -> None:
        """Set special config."""

        self.conn_.isolation_level = None
        if self.parseFromLatin:
            self.conn_.text_factory = lambda x: str(x, "latin1")

    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        return None

    def getConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""

        import sqlite3

        conn_ = None
        main_conn = None
        if "main_conn" in application.PROJECT.conn_manager.connections_dict.keys():
            main_conn = application.PROJECT.conn_manager.mainConn()
        if main_conn is not None:
            if self.db_filename == main_conn.driver().db_filename and main_conn.conn:

                conn_ = main_conn.conn

        if conn_ is None:
            conn_ = sqlite3.connect("%s" % self.db_filename)

            if not os.path.exists("%s" % self.db_filename) and self.db_filename not in [
                ":memory:",
                "temp_db",
            ]:
                LOGGER.warning("La base de datos %s no existe", self.db_filename)

        return conn_

    def getEngine(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return sqlAlchemy connection."""
        from sqlalchemy import create_engine  # type: ignore

        sqlalchemy_uri = "sqlite:///%s" % self.db_filename
        if self.db_filename == ":memory:":
            sqlalchemy_uri = "sqlite://"

        return create_engine(sqlalchemy_uri)

    def DBName(self) -> str:
        """Return database name."""
        return self.db_name or ""

    def nextSerialVal(self, table: str, field: str) -> Optional[int]:
        """Return next serial value."""
        q = pnsqlquery.PNSqlQuery()
        q.setSelect("max(%s)" % field)
        q.setFrom(table)
        q.setWhere("1 = 1")
        if not q.exec_():  # FIXME: exec es palabra reservada
            LOGGER.warning("not exec sequence")
        elif q.first():
            old_value = q.value(0)
            if old_value is not None:
                return int(old_value) + 1

        return None

    # def inTransaction(self) -> bool:
    #    """Return if the conn is on transaction."""
    #    if self.conn_ is None:
    #        raise Exception("inTransaction. self.conn_ is None")
    #    return self.conn_.in_transaction

    def setType(self, type_: str, leng: Optional[Union[str, int]] = None) -> str:
        """Return type definition."""

        return " %s(%s)" % (type_.upper(), leng) if leng else " %s" % type_.upper()

    def process_booleans(self, where: str) -> str:
        """Process booleans fields."""
        where = where.replace("'true'", "1")
        return where.replace("'false'", "0")

    def existsTable(self, name: str) -> bool:
        """Return if exists a table specified by name."""
        if not self.isOpen():
            LOGGER.warning("existsTable: Database not open")
            return False

        cursor = self.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % name)

        result = cursor.fetchall()

        return True if result else False

    def sqlCreateTable(self, tmd: "pntablemetadata.PNTableMetaData") -> Optional[str]:
        """Return a create table query."""

        if not tmd:
            return None

        primaryKey = None
        sql = "CREATE TABLE %s (" % tmd.name()

        fieldList = tmd.fieldList()

        unlocks = 0
        for field in fieldList:
            if field.type() == "unlock":
                unlocks = unlocks + 1

        if unlocks > 1:
            LOGGER.debug(u"FLManager : No se ha podido crear la tabla " + tmd.name())
            LOGGER.debug(u"FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno.")
            return None

        i = 1
        for field in fieldList:
            sql += field.name()
            if field.type() == "int":
                sql += " INTEGER"
            elif field.type() == "uint":
                sql += " INTEGER"
            elif field.type() in ("bool", "unlock"):
                sql += " BOOLEAN"
            elif field.type() == "double":
                sql += " FLOAT"
            elif field.type() == "time":
                sql += " VARCHAR(20)"
            elif field.type() == "date":
                sql += " VARCHAR(20)"
            elif field.type() == "pixmap":
                sql += " TEXT"
            elif field.type() == "string":
                sql += " VARCHAR"
            elif field.type() == "stringlist":
                sql += " TEXT"
            elif field.type() == "bytearray":
                sql += " CLOB"
            elif field.type() == "timestamp":
                sql += " DATETIME"
            elif field.type() == "serial":
                sql += " INTEGER"
                if not field.isPrimaryKey():
                    sql += " PRIMARY KEY"

            longitud = field.length()
            if longitud > 0:
                sql = sql + "(%s)" % longitud

            if field.isPrimaryKey():
                if primaryKey is None:
                    sql += " PRIMARY KEY"
                else:
                    LOGGER.debug(
                        QtWidgets.QApplication.tr("FLManager : Tabla-> ")
                        + tmd.name()
                        + QtWidgets.QApplication.tr(
                            " . Se ha intentado poner una segunda clave primaria para el campo "
                        )
                        + field.name()
                        + QtWidgets.QApplication.tr(" , pero el campo ")
                        + primaryKey
                        + QtWidgets.QApplication.tr(
                            " ya es clave primaria. Sólo puede existir una clave primaria en FLTableMetaData, "
                            "use FLCompoundKey para crear claves compuestas."
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

        sql = sql + ");"
        create_index = ""
        if tmd.primaryKey():
            create_index = "CREATE INDEX %s_pkey ON %s (%s)" % (
                tmd.name(),
                tmd.name(),
                tmd.primaryKey(),
            )

        # q = pnsqlquery.PNSqlQuery()
        # q.setForwardOnly(True)
        # q.exec_(createIndex)
        sql += create_index

        return sql

    def recordInfo2(self, tablename: str) -> List[List[Any]]:
        """Return info from a database table."""
        if not self.isOpen():
            raise Exception("recordInfo2: Cannot proceed: SQLLITE not open")

        if self.conn_ is None:
            raise Exception("recordInfo2. self.conn_ is None")

        sql = "PRAGMA table_info('%s')" % tablename
        conn = self.conn_
        cursor = conn.execute(sql)
        res = cursor.fetchall()
        return self.recordInfo(res)

    def recordInfo(self, tablename_or_query: Any) -> List[list]:
        """Return info from  a record fields."""
        if not self.isOpen():
            return []

        info: List[Any] = []

        if self.db_ is None:
            raise Exception("recordInfo. self.db_ is None")

        if isinstance(tablename_or_query, str):
            tablename = tablename_or_query

            stream = self.db_.connManager().managerModules().contentCached("%s.mtd" % tablename)
            if not stream:
                LOGGER.warning(
                    "FLManager : "
                    + QtWidgets.QApplication.translate(
                        "FLSQLite", "Error al cargar los metadatos para la tabla %s" % tablename
                    )
                )

                return self.recordInfo2(tablename)

            tree = ElementTree.fromstring(stream)
            mtd = self.db_.connManager().manager().metadata(tree, True)
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

        else:
            for columns in tablename_or_query:
                fName = columns[1]
                fType = columns[2]
                fSize = 0
                fAllowNull = columns[3] == 0
                if fType.find("VARCHAR(") > -1:
                    fSize = int(fType[fType.find("(") + 1 : len(fType) - 1])

                info.append([fName, self.decodeSqlType(fType), not fAllowNull, fSize])

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

    @decorators.not_implemented_warn
    def alterTable(
        self,
        mtd1: Union[str, "pntablemetadata.PNTableMetaData"],
        mtd2: Optional[str] = None,
        key: Optional[str] = None,
        force: bool = False,
    ) -> bool:
        """Modify a table structure."""
        raise Exception("not implemented")

    def tables(self, type_name: Optional[str] = "All") -> List[str]:
        """Return a tables list specified by type."""

        table_list: List[str] = []
        result_list: List[Any] = []
        if self.isOpen():

            if type_name in ("Tables", ""):
                cursor = self.execute_query(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name ASC"
                )
                result_list += cursor.fetchall()

            if type_name in ("Views", ""):
                cursor = self.execute_query(
                    "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name ASC"
                )
                result_list += cursor.fetchall()

            if type_name in ("SystemTables", ""):
                table_list.append("sqlite_master")

        for item in result_list:
            table_list.append(item[0])

        return table_list

    def Mr_Proper(self) -> None:
        """Clear all garbage data."""

        LOGGER.warning("FLSQLITE: FIXME: Mr_Proper no regenera tablas")
        util = flutil.FLUtil()
        if self.db_ is None:
            raise Exception("MR_Proper: self.db_ is None")

        if not self.isOpen():
            raise Exception("MR_Proper: Cannot proceed: SQLLITE not open")

        self.db_.connManager().dbAux().transaction()
        rx = Qt.QRegExp("^.*[\\d][\\d][\\d][\\d].[\\d][\\d].*[\\d][\\d]$")
        rx2 = Qt.QRegExp("^.*alteredtable[\\d][\\d][\\d][\\d].*$")
        qry = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry2 = pnsqlquery.PNSqlQuery(None, "dbAux")
        qry3 = pnsqlquery.PNSqlQuery(None, "dbAux")
        steps = 0
        item = ""

        rx3 = Qt.QRegExp("^.*\\d{6,9}$")
        # listOldBks = self.tables("").grep(rx3)
        listOldBks_prev = self.tables("Tables")

        listOldBks = []

        for l in listOldBks_prev:
            if rx3.indexIn(l) > -1:
                listOldBks.append(l)

        qry.exec_("select nombre from flfiles")
        util.createProgressDialog(
            util.translate("SqlDriver", "Borrando backups"), len(listOldBks) + qry.size() + 5
        )
        while qry.next():
            item = qry.value(0)
            if rx.indexIn(item) > -1 or rx2.indexIn(item) > -1:
                util.setLabelText(util.translate("SqlDriver", "Borrando regisro %s" % item))
                qry2.exec_("delete from flfiles where nombre = '%s'" % item)
                if item.find("alteredtable") > -1:
                    if item.replace(".mtd", "") in self.tables(""):
                        util.setLabelText(util.translate("SqlDriver", "Borrando tabla %s" % item))
                        qry2.exec_("drop table %s" % item.replace(".mtd", ""))

            steps = steps + 1
            util.setProgress(steps)

        for item in listOldBks:
            if item in self.tables(""):
                util.translate("SqlDriver", "Borrando tabla %s" % item)
                util.setLabelText(util.translate("SqlDriver", "Borrando tabla %s" % item))
                qry2.exec_("drop table %s" % item)

            steps = steps + 1
            util.setProgress(steps)

        util.setLabelText(util.translate("SqlDriver", "Inicializando cachés"))
        steps = steps + 1
        util.setProgress(steps)

        qry.exec_("delete from flmetadata")
        qry.exec_("delete from flvar")
        self.db_.connManager().manager().cleanupMetaData()
        self.db_.connManager().dbAux().commit()

        util.setLabelText(util.translate("SqlDriver", "Vacunando base de datos"))
        steps = steps + 1
        util.setProgress(steps)
        qry3.exec_("vacuum")
        steps = steps + 1
        util.setProgress(steps)
        util.destroyProgressDialog()
