"""Flqpsql module."""

from pineboolib.application.metadata import pntablemetadata, pnfieldmetadata
from pineboolib import logging

from pineboolib.fllegacy import flutil

from pineboolib.interfaces import isqldriver

import sqlalchemy  # type: ignore [import] # noqa: F821, F401

from typing import Optional, Union, List, Dict, Any, Tuple

LOGGER = logging.get_logger(__name__)


class FLQPSQL(isqldriver.ISqlDriver):
    """FLQPSQL class."""

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.version_ = "0.9"
        self.name_ = "FLQPSQL"
        self.error_list = []
        self.alias_ = "PostgreSQL (PSYCOPG2)"
        self.default_port = 5432
        self._true = True
        self._false = False
        self._like_true = "'t'"
        self._like_false = "'f'"
        self._database_not_found_keywords = ["does not exist", "no existe"]
        self._sqlalchemy_name = "postgresql"
        self._type_array: Dict[int, str] = {
            16: "bool",
            23: "uint",
            25: "stringlist",
            701: "double",
            1082: "date",
            1043: "string",
            1184: "timestamp",
            114: "json",
        }

        self._legacy_migrate = False

    def getAlternativeConn(self, name: str, host: str, port: int, usern: str, passw_: str) -> Any:
        """Return connection."""
        # import psycopg2

        conn_ = self.getConn("postgres", host, port, usern, passw_)
        # if conn_ is not None:
        #    conn_.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        return conn_

    def nextSerialVal(self, table_name: str, field_name: str) -> int:
        """Return next serial value."""

        if self.is_open():
            seq_ = "%s_%s_seq" % (table_name, field_name)
            result_ = 0
            qry = self.execute_query("SELECT NEXTVAL('%s')" % seq_)
            if qry is not None:
                result_ = qry.fetchone()[0]  # type: ignore [index] # noqa: F821
            else:
                self.execute_query("CREATE SEQUENCE %s" % seq_)

        return result_

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
        elif type_ == "json":
            res_ = "JSON"
        else:
            LOGGER.warning("seType: unknown type %s", type_)
            leng = 0

        return "%s(%s)" % (res_, leng) if leng else res_

    def sqlCreateTable(
        self, tmd: "pntablemetadata.PNTableMetaData", create_index: bool = True
    ) -> Optional[str]:
        """Return a create table query."""

        if tmd.isQuery():
            return self.sqlCreateView(tmd)

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
                if self.is_open() and create_index:
                    cursor = self.execute_query(
                        "SELECT relname FROM pg_class WHERE relname='%s'" % seq
                    )

                    res_ = cursor.fetchone() if cursor else None
                    if not res_:
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
                    raise Exception(
                        "A primary key (%s) has been defined before the field %s.%s -> %s"
                        % (primary_key, tmd.name(), field.name(), sql)
                    )
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
            "pg_get_expr(pg_attrdef.adbin, pg_attrdef.adrelid) from pg_class, pg_attribute "
            "left join pg_attrdef on (pg_attrdef.adrelid = pg_attribute.attrelid and pg_attrdef.adnum = pg_attribute.attnum)"
            " where lower(pg_class.relname) = '%s' and pg_attribute.attnum > 0 and pg_attribute.attrelid = pg_class.oid "
            "and pg_attribute.attisdropped = false order by pg_attribute.attnum" % tablename.lower()
        )
        cursor = self.execute_query(sql)
        res = cursor.fetchall() if cursor else []
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
                    None,  # defualt_value
                    None,  # is_pk
                ]
            )
        return info

    def decodeSqlType(self, type_: Union[int, str]) -> str:
        """Return the specific field type."""

        return self._type_array[int(type_)] if int(type_) in self._type_array.keys() else str(type_)

    def tables(self, type_name: str = "", table_name: str = "") -> List[str]:
        """Return a tables list specified by type."""
        table_list: List[str] = []
        result_list: List[Any] = []

        if self.is_open():
            where: List[str] = []

            if type_name in ["Tables", ""]:
                where.append(
                    "(( relkind = 'r' ) AND ( relname !~ '^Inv' ) AND ( relname !~ '^pg_' ))"
                )
            if type_name in ["Views", ""]:
                where.append(
                    "(( relkind = 'v' ) AND ( relname !~ '^Inv' ) AND ( relname !~ '^pg_' ))"
                )
            if type_name in ["SystemTables", ""]:
                where.append("(( relkind = 'r' ) AND ( relname like 'pg_%%' ))")

            if where:
                and_name = " AND relname ='%s'" % (table_name) if table_name else ""

                cursor = self.execute_query(
                    "select relname from pg_class where %s%s ORDER BY relname ASC"
                    % (" OR ".join(where), and_name)
                )
                result_list += cursor.fetchall() if cursor else []

            table_list = [item[0] for item in result_list]

        return table_list

    def constraintExists(self, name: str) -> bool:
        """Return if constraint exists specified by name."""

        sql = (
            "SELECT constraint_name FROM information_schema.table_constraints where constraint_name='%s'"
            % name
        )
        cur = self.execute_query(sql)
        result_: Any = cur.fetchone() if cur else []
        return True if result_ else False

    def vacuum(self):
        """Vacuum tables."""
        table_names = self.db_.tables("Tables")
        self._connection.connection.set_isolation_level(0)
        for table_name in table_names:
            if self.db_.connManager().manager().metadata(table_name) is not None:
                self.execute_query("VACUUM ANALYZE %s" % table_name)
        self._connection.connection.set_isolation_level(1)

    # def fix_query(self, query: str) -> str:
    #    """Fix string."""
    #    # ret_ = query.replace(";", "")
    #    return query

    def checkSequences(self) -> None:
        """Check sequences."""
        util = flutil.FLUtil()
        conn_dbaux = self.db_.connManager().dbAux()
        sql = (
            "select relname from pg_class where ( relkind = 'r' ) " + "and ( relname !~ '^Inv' ) "
            "and ( relname !~ '^pg_' ) and ( relname !~ '^sql_' )"
        )
        cur_sequences = conn_dbaux.execute_query(sql)
        data_list = list(cur_sequences.fetchall() if cur_sequences else [])
        util.createProgressDialog(
            util.translate("application", "Comprobando indices"), len(data_list)
        )

        for number, data in enumerate(data_list):
            table_name = data[0]
            util.setLabelText(util.translate("application", "Creando índices para %s" % table_name))
            util.setProgress(number)
            metadata = self.db_.connManager().manager().metadata(table_name)
            if metadata is None:
                pass
            #    LOGGER.error("checkSequences: %s metadata not found!", table_name)

        util.destroyProgressDialog()
        return

    def create_migration_sql(
        self, metadata: "pntablemetadata.PNTableMetaData", old_table_name: str
    ) -> str:
        """Generate migration sql."""

        field_names: List[str] = []
        field_values: List[str] = []
        field_names, field_values = self.sql_cast(metadata, old_table_name)

        sql = ""
        if field_names:
            sql = """INSERT INTO %s (%s) SELECT %s from %s""" % (
                metadata.name(),
                ",".join(field_names),
                ",".join(field_values),
                old_table_name,
            )

        return sql

    def sql_cast(
        self, metadata: "pntablemetadata.PNTableMetaData", table_name: str
    ) -> Tuple[List[str], List[str]]:
        """Return field cast."""

        fields_db_data = self.recordInfo2(table_name)
        fields_meta_data = self.recordInfo(metadata)
        fields_data_names = [field[0] for field in fields_db_data]
        fields_meta_names = [field[0] for field in fields_meta_data]
        field_names: List[str] = []
        field_values: List[str] = []
        for field_meta_name in fields_meta_names:
            name = field_meta_name
            value = ""
            field_meta_data = fields_meta_data[fields_meta_names.index(field_meta_name)]
            if field_meta_name in fields_data_names:
                value = self.cast_field(
                    fields_db_data[fields_data_names.index(field_meta_name)], field_meta_data
                )

            if field_meta_data[2]:  # not allow_null
                default_value: Any = self.formatValue(field_meta_data[1], field_meta_data[5], False)
                value = "ISNULL(%s,%s)" % (value, default_value) if value else default_value

            field_names.append(name)
            field_values.append(value)

        return field_names, field_values

    def cast_field(self, data_field: List[Any], meta_field: List[Any]) -> str:
        """Cast a field."""

        # 1 name
        # 2 sql_type
        # 3 allow_null
        # 4 field_size
        # 5 field_precission

        value = data_field[0]
        if self.notEqualsFields(data_field, meta_field):
            value = "CAST ( %s AS %s )" % (value, self.setType(meta_field[1]))

        return value
