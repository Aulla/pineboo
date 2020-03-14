"""Flqpsql module."""
from PyQt5 import QtCore

from pineboolib.application.database import pnsqlquery

from pineboolib.application.metadata import pntablemetadata
from pineboolib import logging

from pineboolib.fllegacy import flutil

from . import pnsqlschema

import traceback
from typing import Optional, Union, List, Any


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

    def nextSerialVal(self, table_name: str, field_name: str) -> int:
        """Return next serial value."""

        if self.isOpen():
            cur = self.execute_query("SELECT nextval('%s_%s_seq')" % (table_name, field_name))
            result = cur.fetchone()
            if not result:
                LOGGER.warning("not exec sequence")
            else:
                return result[0]

        return 0

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

    def existsTable(self, table_name: str) -> bool:
        """Return if exists a table specified by name."""

        cur = self.execute_query("SELECT relname FROM pg_class WHERE relname = '%s'" % table_name)
        result = cur.fetchone()

        return True if result else False

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
                if self.isOpen() and create_index:
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
        info = []
        sql = (
            "select pg_attribute.attname, pg_attribute.atttypid, pg_attribute.attnotnull, pg_attribute.attlen, pg_attribute.atttypmod, "
            "pg_attrdef.adsrc from pg_class, pg_attribute "
            "left join pg_attrdef on (pg_attrdef.adrelid = pg_attribute.attrelid and pg_attrdef.adnum = pg_attribute.attnum)"
            " where lower(pg_class.relname) = '%s' and pg_attribute.attnum > 0 and pg_attribute.attrelid = pg_class.oid "
            "and pg_attribute.attisdropped = false order by pg_attribute.attnum" % tablename.lower()
        )
        cursor = self.execute_query(sql)
        res = cursor.fetchall()
        for columns in res:
            field_size = columns[3]
            field_precision = columns[4]
            field_name = columns[0]
            field_type = columns[1]
            field_allow_null = columns[2]
            field_default_value = columns[5]

            if isinstance(field_default_value, str) and field_default_value:
                if field_default_value.find("::character varying") > -1:
                    field_default_value = field_default_value[
                        0 : field_default_value.find("::character varying")
                    ]

            if field_size == -1 and field_precision > -1:
                field_size = field_precision - 4
                field_precision = -1

            if field_size < 0:
                field_size = 0

            if field_precision < 0:
                field_precision = 0

            if field_default_value and field_default_value[0] == "'":
                field_default_value = field_default_value[1 : len(field_default_value) - 2]

            info.append(
                [
                    field_name,
                    self.decodeSqlType(field_type),
                    field_allow_null,
                    field_size,
                    field_precision,
                    field_default_value,
                    int(field_type),
                ]
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
        cur = self.execute_query(sql)
        result = cur.fetchone()
        return True if result else False

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

    def alterTable(self, new_metadata: "pntablemetadata.PNTableMetaData") -> bool:
        """Modify a table structure."""

        if self.hasCheckColumn(new_metadata):
            return False

        field_list = new_metadata.fieldList()
        if not field_list:
            return False

        util = flutil.FLUtil()
        table_name = new_metadata.name()

        renamed_table = "%salteredtable%s" % (
            table_name,
            QtCore.QDateTime().currentDateTime().toString("ddhhssz"),
        )

        constraint_name = "%s_key" % table_name

        query = pnsqlquery.PNSqlQuery(None, "dbAux")
        query.db().transaction()

        if self.constraintExists(constraint_name):
            sql = "ALTER TABLE %s DROP CONSTRAINT %s CASCADE" % (table_name, constraint_name)
            if not query.exec_(sql):
                query.db().rollbackTransaction()
                return False

        for field in field_list:
            if field.isUnique():
                constraint_name = "%s_%s_key" % (table_name, field.name())
                if self.constraintExists(constraint_name):
                    sql = "ALTER TABLE %s DROP CONSTRAINT %s CASCADE" % (
                        table_name,
                        constraint_name,
                    )
                    if not query.exec_(sql):
                        query.db().rollbackTransaction()
                        return False

        if not query.exec_("ALTER TABLE %s RENAME TO %s" % (table_name, renamed_table)):
            query.db().rollbackTransaction()
            return False

        if not self.db_.connManager().manager().createTable(new_metadata):
            query.db().rollbackTransaction()
            return False

        cur = self.execute_query("SELECT * FROM %s WHERE 1=1" % renamed_table)
        old_data_list = cur.fetchall()
        # old_cursor = pnsqlcursor.PNSqlCursor(renamed_table, True, "dbAux")
        # old_cursor.setModeAccess(old_cursor.Browse)
        # old_cursor.select()
        util.createProgressDialog(
            util.translate("application", "Reestructurando registros para %s...")
            % new_metadata.alias(),
            len(old_data_list),
        )

        util.setLabelText(util.translate("application", "Tabla modificada"))

        old_columns_info = self.recordInfo2(table_name)
        new_field_names = new_metadata.fieldNames()
        list_records = []
        for number_progress, old_data in enumerate(old_data_list):
            new_buffer = []
            for number, column in enumerate(old_columns_info):
                new_field = new_metadata.field(column[0])
                if new_field:
                    value = (
                        old_data[number]
                        if column[0] in new_field_names
                        else new_field.defaultValue()
                    )
                    new_buffer.append([new_field, value])

            list_records.append(new_buffer)
            util.setProgress(number_progress)

        util.destroyProgressDialog()
        if not self.insertMulti(table_name, list_records):
            self.db_.connManager().dbAux().rollbackTransaction()
            return False
        else:
            self.db_.connManager().dbAux().commit()

        query.exec_("DROP TABLE %s CASCADE" % renamed_table)
        return True

    """
    def Mr_Proper(self) -> None:
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
                # conte = self.db_.connManager().managerModules().content("%s.mtd" % item)
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
    """

    def vacuum(self):
        """Vacuum tables."""
        table_names = self.tables("Tables")
        for table_name in table_names:
            self.execute_query("VACUUM ANALYZE %s" % table_name)

    def fix_query(self, query: str) -> str:
        """Fix string."""
        # ret_ = query.replace(";", "")
        return query

    # def isOpen(self):
    #    return self.conn_.closed == 0
