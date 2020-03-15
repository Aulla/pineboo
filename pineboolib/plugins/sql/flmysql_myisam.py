"""
Module for MYISAM driver.
"""

from pineboolib.fllegacy import flutil
from pineboolib import logging
from . import pnsqlschema

from typing import Any, Optional, List, TYPE_CHECKING

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

    def existsTable(self, table_name: str) -> bool:
        """Return if exists a table specified by name."""

        cur = self.execute_query("SHOW TABLES LIKE '%s'" % table_name)
        result = cur.fetchone()

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

    """
    def Mr_Proper(self) -> None:
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
                metadata = self.db_.connManager().manager().metadata(item)

                if metadata:
                    msg = util.translate(
                        "application",
                        "La estructura de los metadatos de la tabla '%s' y su "
                        "estructura interna en la base de datos no coinciden. "
                        "Intentando regenerarla." % item,
                    )

                    LOGGER.warning(msg)
                    self.alterTable(metadata)

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
                        metadata = self.db_.connManager().manager().metadata(item)
                        if metadata:
                            self.alterTable(metadata)

        self.active_create_index = False
        util.destroyProgressDialog()
    """

    def dict_cursor(self) -> Any:
        """Return dict cursor."""

        from MySQLdb.cursors import DictCursor  # type: ignore

        return DictCursor

    def recordInfo2(self, table_name: str) -> List[list]:
        """Obtain current cursor information on columns."""

        info = []
        sql = "SHOW FIELDS FROM %s" % table_name

        cursor = self.execute_query(sql)
        res = cursor.fetchall()

        for columns in res:
            field_name = columns[0]
            field_allow_null = columns[2] == "NO"
            field_size = "0"
            field_precision = 0
            field_default_value = columns[4]
            field_primary_key = columns[3] == "PRI"

            if columns[1].find("(") > -1:
                field_type = self.decodeSqlType(columns[1][: columns[1].find("(")])
                if field_type not in ["uint", "int", "double"]:
                    field_size = columns[1][columns[1].find("(") + 1 : columns[1].find(")")]
                else:
                    pos_comma = field_size.find(",")
                    if pos_comma > -1:
                        list_number = field_size.split(",")
                        field_precision = int(list_number[1])
                        field_size = list_number[0]

            else:
                field_type = self.decodeSqlType(columns[1])

            if field_type == "string" and field_size == "255":
                field_size = "0"

            info.append(
                [
                    field_name,
                    field_type,
                    field_allow_null,
                    int(field_size),
                    field_precision,
                    field_default_value,
                    field_primary_key,
                ]
            )

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

    def vacuum(self):
        """Vacuum tables."""
        table_names = self.tables("Tables")

        for table_name in table_names:
            if self.db_.connManager().manager().metadata(table_name) is not None:
                self.execute_query("ANALYZE TABLE %s" % table_name)
