"""Flqpsql module."""

from pineboolib.application.metadata import pntablemetadata
from pineboolib.application.parsers.parser_mtd import pnmtdparser
from pineboolib import logging

from pineboolib.fllegacy import flutil
from pineboolib.interfaces import isqldriver

from typing import Optional, Union, List, Dict, Any, TYPE_CHECKING

LOGGER = logging.get_logger(__name__)

if TYPE_CHECKING:
    from pineboolib.application.metadata import pnfieldmetadata


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
            20: "uint",
            23: "uint",
            25: "stringlist",
            701: "double",
            1082: "date",
            1043: "string",
            1184: "timestamp",
            114: "json",
        }

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

        type_array = {
            "int": "INT2",
            "uint": "INT4",
            "bool": "BOOLEAN",
            "unlock": "BOOLEAN",
            "double": "FLOAT8",
            "time": "TIME",
            "date": "DATE",
            "pixmap": "TEXT",
            "stringlist": "TEXT",
            "string": "VARCHAR",
            "bytearray": "BYTEA",
            "timestamp": "TIMESTAMPTZ",
            "json": "JSON",
        }

        res_ = type_array[type_] if type_ in type_array.keys() else ""

        if not res_:
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

        field_list = tmd.fieldList()

        unlocks = 0
        sql_fields: List[str] = []
        for field in field_list:

            sql_field = field.name()
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

                sql_field += " INT4 DEFAULT NEXTVAL('%s')" % seq
            else:
                if type_ == "unlock":
                    unlocks += 1

                    if unlocks > 1:
                        LOGGER.warning("FLManager : No se ha podido crear la tabla %s ", tmd.name())
                        LOGGER.warning(
                            "FLManager : Hay mas de un campo tipo unlock. Solo puede haber uno."
                        )
                        return None

                sql_field += " %s" % self.setType(type_, field.length())

            if field.isPrimaryKey():
                if not primary_key:
                    sql_field += " PRIMARY KEY"
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
                        % (primary_key, tmd.name(), field.name(), sql_fields)
                    )
            else:

                sql_field += " UNIQUE" if field.isUnique() else ""
                sql_field += " NULL" if field.allowNull() else " NOT NULL"

            sql_fields.append(sql_field)

        return "CREATE TABLE %s (%s)" % (tmd.name(), ",".join(sql_fields))

    def recordInfo2(self, tablename: str) -> Dict[str, List[Any]]:
        """Return info from a database table."""
        info = {}
        sql = (
            "select pg_attribute.attname, pg_attribute.atttypid, pg_attribute.attnotnull, pg_attribute.attlen, pg_attribute.atttypmod, "
            "pg_get_expr(pg_attrdef.adbin, pg_attrdef.adrelid) from pg_class, pg_attribute "
            "left join pg_attrdef on (pg_attrdef.adrelid = pg_attribute.attrelid and pg_attrdef.adnum = pg_attribute.attnum)"
            " where lower(pg_class.relname) = '%s' and pg_attribute.attnum > 0 and pg_attribute.attrelid = pg_class.oid "
            "and pg_attribute.attisdropped = false order by pg_attribute.attnum" % tablename.lower()
        )
        cursor = self.execute_query(sql)
        # res = cursor.fetchall() if cursor else []
        # for columns in res:
        #    field_size = columns[3]
        #    field_precision = columns[4]
        #    field_name = columns[0]
        #    field_type = columns[1]
        #    field_allow_null = columns[2]
        #    field_default_value = columns[5]

        for (
            field_name,
            field_type,
            field_allow_null,
            field_size,
            field_precision,
            field_default_value,
        ) in list(cursor.fetchall() if cursor else []):

            if isinstance(field_default_value, str) and field_default_value:
                field_default_value = (
                    field_default_value[0 : field_default_value.find("::character varying")]
                    if field_default_value.find("::character varying") > -1
                    else field_default_value
                )

            if (
                field_size == -1  # type: ignore [comparison-overlap]
                and field_precision > -1  # type: ignore [operator]
            ):
                field_size = field_precision - 4  # type: ignore [operator, assignment]
                field_precision = -1  # type: ignore [assignment]

            if field_size < 0:  # type: ignore [operator]
                field_size = 0  # type: ignore [assignment]

            if field_precision < 0:  # type: ignore [operator]
                field_precision = 0  # type: ignore [assignment]

            field_default_value = (
                field_default_value[1 : len(field_default_value) - 2]
                if field_default_value and field_default_value[0] == "'"
                else field_default_value
            )

            info[field_name] = [
                field_name,
                self.decodeSqlType(field_type),
                field_allow_null,
                field_size,
                field_precision,
                None,  # defualt_value
                None,  # is_pk
            ]

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

    def resolveAlterColumn(
        self,
        table_name: str,
        field_meta: "pnfieldmetadata.PNFieldMetaData",
        db_value: List[Union[int, str]],
    ):
        """Return string alter column."""

        def_value: Optional[str] = field_meta.defaultValue()
        text_default_value = ""
        if not field_meta.allowNull():
            text_default_value = " ,server_default='%s'" % (
                def_value
                if def_value is not None
                else self.formatValue(field_meta.type(), None, False)
            )

        result = "op.alter_column('%s', '%s', %s)" % (
            table_name,
            field_meta.name(),
            "type_=%s, existing_type=%s, postgresql_using='%s', nullable=%s%s"
            % (
                pnmtdparser.generate_field(field_meta, "sa"),
                pnmtdparser.resolve_type(db_value[1], db_value[3], "sa"),  # type: ignore [arg-type]
                "%s::%s" % (field_meta.name(), self.setType(field_meta.type())),
                field_meta.allowNull(),
                text_default_value,
            ),
        )

        return result
