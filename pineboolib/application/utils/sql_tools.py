"""
Collect information from the query, such as field tables, lines, etc ...
"""


from pineboolib import application, logging
from pineboolib.application import types

import datetime
import re
from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import ifieldmetadata  # noqa: F401 # pragma: no cover

LOGGER = logging.get_logger(__name__)


class SqlInspector(object):
    """SqlInspector Class."""

    _sql_list: List[str]
    _sql: str
    _invalid_tables: List[str]
    _mtd_fields: Dict[int, "ifieldmetadata.IFieldMetaData"]
    _field_list: Dict[str, int]
    _table_names: List[str]
    _alias: Dict[str, str]
    _posible_float: bool
    _list_sql: List[str]

    _suspected_injection: Optional[str]
    _suspicious_keywords: List[str] = [
        "ASCII(",
        "SUBSTRING(",
        "SELECT",
        "COALESCE",
        "CAST",
        "CHARACTER",
        "/**/",
        "current_database()",
        "::text",
        "sleep",
        "waitfor",
        "benchmark",
        "selectchar",
    ]
    _suspicious_characters: List[str] = ["(", ")", "'", '"', " ", ",", "/*", "*/"]
    _suspicious_bypass_union_time: List[str] = [
        "adminor1=1",
        "convertintunionall",
        "unionallselect",
        "unionselect@",  # unionselect@@version
        "selectsleep",
        "selectbecnhmark",
        "orderby1sleep",
        ";waitfordelay",
        "orpg_sleep",
        "fromselectsleep",
        "selectsubsctring@",
    ]

    def __init__(self) -> None:
        """
        Initialize the class.
        """
        self._sql = ""
        self._list_sql = []
        self._field_list = {}
        self._table_names = []
        self._mtd_fields = {}
        self._invalid_tables = []
        self._suspected_injection = None
        # self.set_sql(sql_text)
        # self.resolve()

        # self.table_names()
        # self.field_names()

    def resolve(self) -> None:
        """Resolve query."""
        self._invalid_tables = []
        self._mtd_fields = {}
        self._field_list = {}
        self._table_names = []
        self._alias = {}
        self._list_sql = []
        self._posible_float = False
        if self._sql.startswith("show"):
            return

        self._resolve_fields()

    def mtd_fields(self) -> Dict[int, "ifieldmetadata.IFieldMetaData"]:
        """
        Return a dictionary with the fields of the query.

        @return fields dictionary.
        """

        return self._mtd_fields

    def get_from(self) -> str:
        """Return from clausule."""
        ret_ = ""
        if "from" in self._list_sql:
            index_from = self._list_sql.index("from")
            if "where" in self._list_sql:
                index_where = self._list_sql.index("where")
                ret_ = " ".join(self._list_sql[index_from + 1 : index_where])
            else:
                ret_ = " ".join(self._list_sql[index_from + 1 :])

        return ret_

    def get_where(self) -> str:
        """Return where clausule."""

        ret_ = ""
        if "where" in self._list_sql:
            index_where = self._list_sql.index("where")
            if "group" in self._list_sql:
                ret_ = " ".join(self._list_sql[index_where + 1 : self._list_sql.index("group")])
            elif "order" in self._list_sql:
                ret_ = " ".join(self._list_sql[index_where + 1 : self._list_sql.index("order")])
            else:
                ret_ = " ".join(self._list_sql[index_where + 1 :])

        return ret_

    def get_order_by(self) -> str:
        """Return order by clausule."""
        ret_ = ""
        if "order" in self._list_sql:
            index_order = self._list_sql.index("order")
            ret_ = " ".join(self._list_sql[index_order + 2 :])

        return ret_

    def table_names(self) -> List[str]:
        """
        Return a list with the tables of the query.

        @return tables list.
        """

        return self._table_names

    def set_table_names(self, table_names: List[str]) -> None:
        """
        Set a list with the tables of the query.

        @return tables list.
        """

        self._table_names = table_names

    def sql(self) -> str:
        """
        Return sql string.
        """

        return self._sql

    def set_sql(self, sql: str) -> None:
        """Set sql query."""
        sql = sql.lower()
        sql = sql.replace("\n", " ")
        sql = sql.replace("\t", " ")
        sql = sql.strip()

        self._sql = sql

    def field_names(self) -> List[str]:
        """
        Return a list with the name of the fields.

        @return fields list.
        """
        return [k for k, v in sorted(self._field_list.items(), key=lambda item: item[1])]

    def field_list(self) -> Dict[str, int]:
        """
        Return a Dict with name and position.

        @return fields list.
        """

        return self._field_list

    def fieldNameToPos(self, name: str) -> int:
        """
        Return the position of a field, from the name.

        @param name. field name.
        @return index position.
        """
        name = name.strip()
        if name in self._field_list.keys():
            return self._field_list[name]
        else:
            if name.find(".") > -1:
                table_name = name[0 : name.find(".")]
                field_name = name[name.find(".") + 1 :]
                if table_name in self._alias.keys():
                    table_name = self._alias[table_name]

                    field_name = "%s.%s" % (table_name, field_name)
                    if field_name in self._field_list.keys():
                        return self._field_list[field_name]
                else:
                    # probando a cambiar tabla por alias
                    for alias in self._alias.keys():
                        if self._alias[alias] == table_name:
                            field_name = "%s.%s" % (alias, field_name)
                            if field_name in self._field_list.keys():
                                return self._field_list[field_name]

            else:
                for table_name in self.table_names():
                    field_name = "%s.%s" % (table_name, name)
                    if field_name in self._field_list.keys():
                        return self._field_list[field_name]

                    for alias in self._alias.keys():
                        if self._alias[alias] == table_name:
                            field_name = "%s.%s" % (alias, name)
                            if field_name in self._field_list.keys():
                                return self._field_list[field_name]

        raise Exception(
            "No se encuentra el campo %s en la query:\n%s.\ncampos: %s"
            % (name, self._sql, self.field_list())
        )

    def posToFieldName(self, pos: int) -> str:
        """
        Return the name of a field, from the position.

        @param name. field name.
        @return field name.
        """
        for k in self._field_list.keys():
            if int(self._field_list[k]) == pos:
                return k
        raise Exception("fieldName not found! %s")

    def _resolve_fields(self) -> None:
        """
        Break the query into the different data.
        """
        self._sql = self._sql.replace(" cast(", " cast (")
        list_sql = self._sql.split(" ")
        self._list_sql = list_sql
        if list_sql[0] == "select":
            if "from" not in list_sql:
                return  # Se entiende que es una consulta especial

            index_from = list_sql.index("from")
            new_fields_list: List[str] = []
            fields_list = list_sql[1:index_from]
            for field in fields_list:
                field = field.replace(" ", "")
                if field.find(",") > -1:
                    extra_fields: List[str] = field.split(",")
                    new_fields_list = new_fields_list + extra_fields
                else:
                    new_fields_list.append(field)

            fields_list = new_fields_list
            new_fields_list = []
            inicio_parentesis: List[str] = []
            composed_field: Dict[str, List[str]] = {}
            for field in list(fields_list):

                # Comprueba si hay field_names compuestos
                if (field.find("(") > -1 and not field.find(")") > -1) or field in [
                    "case",
                    "cast",
                ]:  # si es multiple de verdad
                    # Contamos los parentesis
                    if field in ["case", "cast"]:
                        inicio_parentesis.append(str(len(inicio_parentesis) + 1))
                        composed_field[inicio_parentesis[-1]] = []

                    else:
                        segmento = field[field.find("(") :]
                        while segmento.find("(") > -1 and not segmento.find(")") > -1:
                            inicio_parentesis.append(str(len(inicio_parentesis) + 1))
                            composed_field[inicio_parentesis[-1]] = []
                            try:
                                segmento = segmento[segmento.find("(") + 1 :]
                            except Exception:
                                break

                    composed_field[inicio_parentesis[-1]].append(field)
                    continue
                elif field == "":
                    continue
                elif (
                    (field.find(")") > -1 and not field.find("(") > -1)
                    or field == "end"
                    and inicio_parentesis
                ):  # si es multiple de verdad

                    if field == "end":

                        composed_field[inicio_parentesis[-1]].append(field)
                        if len(inicio_parentesis) == 1:
                            new_fields_list.append(" ".join(composed_field[inicio_parentesis[-1]]))
                        else:
                            composed_field[inicio_parentesis[-2]] += composed_field[
                                inicio_parentesis[-1]
                            ]

                        composed_field[inicio_parentesis[-1]] = []
                        del composed_field[inicio_parentesis[-1]]
                        del inicio_parentesis[-1]

                    else:
                        segmento = field[field.find(")") :]
                        print("*", composed_field, field, inicio_parentesis)
                        composed_field[inicio_parentesis[-1]].append(field)
                        while segmento.find(")") > -1 and not field.find("(") > -1:
                            if len(inicio_parentesis) == 1:
                                new_fields_list.append(
                                    " ".join(composed_field[inicio_parentesis[-1]])
                                )
                            else:
                                composed_field[inicio_parentesis[-2]] += composed_field[
                                    inicio_parentesis[-1]
                                ]
                            composed_field[inicio_parentesis[-1]] = []
                            del composed_field[inicio_parentesis[-1]]
                            del inicio_parentesis[-1]
                            try:
                                segmento = segmento[segmento.find(")") + 1 :]
                            except Exception:
                                break

                elif inicio_parentesis:  # si estoy en medio de un multiple

                    composed_field[inicio_parentesis[-1]].append(field)
                else:
                    new_fields_list.append(field)

            # Repasa si hay alias en los fieldnames.
            old_list = list(new_fields_list)
            new_fields_list = []
            expect_alias = False
            for field_name in old_list:
                num = len(new_fields_list)
                if field_name == "as":
                    expect_alias = True
                    continue
                else:
                    if expect_alias:
                        expect_alias = False
                        del new_fields_list[num - 1]

                    new_fields_list.append(field_name)

            tables_list: List[str] = []
            if "where" in list_sql:
                index_where = list_sql.index("where")
                tables_list = list_sql[index_from + 1 : index_where]
            elif "order" in list_sql:
                index_order_by = list_sql.index("order")
                tables_list = list_sql[index_from + 1 : index_order_by]
            else:
                tables_list = list_sql[index_from + 1 :]

            if "group" in tables_list:
                index_group_by = tables_list.index("group")
                tables_list = tables_list[:index_group_by]

            tablas: List[str] = []
            self._alias = {}
            jump = 0
            # next_is_alias = None
            prev_ = ""
            last_was_table = False
            for table in tables_list:
                if table == "cast":
                    jump += 3
                    last_was_table = False

                if jump > 0:
                    jump -= 1
                    prev_ = table
                    last_was_table = False
                    continue

                if table.find(")") > -1:
                    last_was_table = False
                    continue

                elif table == "on":
                    jump = 3
                    prev_ = table
                    last_was_table = False
                    continue

                elif table in ("left", "join", "right", "inner", "outer"):
                    prev_ = table
                    last_was_table = False
                    continue

                elif table in ("-", "+"):
                    last_was_table = False
                    continue

                elif table == "interval":
                    jump = 1
                    last_was_table = False
                    continue

                elif table == "as":

                    last_was_table = True
                    continue

                elif table in ("and", "or"):
                    jump = 3
                    last_was_table = False

                else:
                    if last_was_table:
                        self._alias[table] = prev_
                        last_was_table = False
                    else:
                        if table != "":
                            last_was_table = True
                            if table.endswith(","):
                                table = table[:-1]
                                last_was_table = False
                            if table not in tablas:
                                tablas.append(table)

                    prev_ = table

            temp_tl: List[str] = []
            for item in tablas:
                temp_tl = temp_tl + item.split(",")
            tablas = temp_tl

            fl_finish = []
            for field_name in new_fields_list:
                if field_name.find(".") > -1:
                    table_ = field_name[0 : field_name.find(".")]
                    field_ = field_name[field_name.find(".") + 1 :]

                    if field_ == "*":
                        mtd_table = application.PROJECT.conn_manager.manager().metadata(table_)
                        if mtd_table is not None:
                            for item in mtd_table.fieldListArray():
                                fl_finish.append(item)

                            continue

                #    if a_.find("(") > -1:
                #        a = a_[a_.find("(") + 1 :]
                #    else:
                #        a = a_

                # if a in self._alias.keys():
                #    field_name = "%s.%s" % (a_.replace(a, self._alias[a]), f_)

                fl_finish.append(field_name)

            self._create_mtd_fields(fl_finish, tablas)
            self._check_sql_injection(list_sql)  # Pasamos el where

    def resolve_empty_value(self, pos: int) -> Any:
        """
        Return a data type according to field type and value None.

        @param pos. index postion.
        """

        if not self.mtd_fields():
            if self._sql.find("sum(") > -1:
                return 0
            return None

        type_ = "double"
        if pos not in self._mtd_fields.keys():
            if pos not in self._field_list.values():
                LOGGER.warning(
                    "SQL_TOOLS : resolve_empty_value : No se encuentra la posición %s", pos
                )
                return None
        else:
            mtd = self._mtd_fields[pos]
            if mtd is not None:
                type_ = mtd.type()

        ret_: Any = None
        if type_ in ("double", "int", "uint", "serial"):
            ret_ = 0
        elif type_ in ("string", "stringlist", "pixmap", "date", "timestamp"):
            ret_ = ""
        elif type_ in ("unlock", "bool"):
            ret_ = False
        elif type_ == "time":
            ret_ = "00:00:00"
        elif type_ == "bytearray":
            ret_ = bytearray()
        elif type_ == "json":
            ret_ = {}

        return ret_

    def resolve_value(self, pos: int, value: Any, raw: bool = False) -> Any:
        """
        Return a data type according to field type.

        @param pos. index postion.
        """

        if not self.mtd_fields():
            if isinstance(value, datetime.time):
                value = str(value)[0:8]
            elif isinstance(value, datetime.timedelta):
                days, seconds = value.days, value.seconds
                hours = days * 24 + seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                value = "%s:%s:%s" % (
                    hours,
                    minutes if len(str(minutes)) > 1 else "0%s" % minutes,
                    seconds if len(str(seconds)) > 1 else "0%s" % seconds,
                )

                value = str(value)
                if value.find(".") > -1:
                    value = value[0 : value.find(".")]
                elif value.find("+") > -1:
                    value = value[0 : value.find("+")]

            return value
        else:
            type_ = "double"
            field_metadata = None
            if pos not in self._mtd_fields.keys():
                if pos not in self._field_list.values():
                    LOGGER.warning(
                        "SQL_TOOLS : resolve_value : No se encuentra la posición %s", pos
                    )
                    return None
            else:
                field_metadata = self._mtd_fields[pos]
                if field_metadata is not None:
                    type_ = field_metadata.type()

        ret_: Any = value
        if type_ in ("string", "stringlist", "timestamp", "json"):
            pass
        elif type_ == "double":
            try:
                ret_ = float(ret_)
            except Exception as error:
                LOGGER.warning(str(error))

        elif type_ in ("int", "uint", "serial"):
            ret_ = int(ret_)
        elif type_ == "pixmap":

            if application.PROJECT.conn_manager is None:
                raise Exception("Project is not connected yet")

            if field_metadata is None:
                raise Exception("Field metadata not found")

            table_metadata = field_metadata.metadata()
            if table_metadata is None:
                raise Exception("Metadata not found")
            if raw or not application.PROJECT.conn_manager.manager().isSystemTable(
                table_metadata.name()
            ):
                ret_ = application.PROJECT.conn_manager.manager().fetchLargeValue(ret_)
        elif type_ == "date":

            ret_ = types.Date(str(ret_))
        elif type_ == "time":

            if isinstance(ret_, datetime.timedelta):
                days, seconds = ret_.days, ret_.seconds
                hours = days * 24 + seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                ret_ = "%s:%s:%s" % (
                    hours,
                    minutes if len(str(minutes)) > 1 else "0%s" % minutes,
                    seconds if len(str(seconds)) > 1 else "0%s" % seconds,
                )

            ret_ = str(ret_)
            if ret_.find(".") > -1:
                ret_ = ret_[0 : ret_.find(".")]
            elif ret_.find("+") > -1:
                ret_ = ret_[0 : ret_.find("+")]

        elif type_ in ("unlock", "bool"):
            ret_ = types.boolean(ret_)
        elif type_ == "bytearray":
            ret_ = bytearray(ret_)
        else:
            try:
                ret_ = float(ret_)
            except Exception:
                LOGGER.warning("Unknown type %s, value %s" % (type_, ret_))

        return ret_

    def _create_mtd_fields(self, fields_list: list, tables_list: list) -> None:
        """
        Solve the fields that make up the query.

        @param fields_list. fields list.
        @param tables_list. tables list.
        """
        if application.PROJECT.conn_manager is None:
            raise Exception("Project is not connected yet")

        db_admin = application.PROJECT._db_admin_mode

        _filter = ["sum(", "max(", "distint("]

        self._mtd_fields = {}
        self._invalid_tables = []
        self._table_names = list(tables_list)
        # self._field_list = {k: n for n, k in enumerate(fields_list)}

        for number_, field_name_org in enumerate(list(fields_list)):
            self._field_list[field_name_org] = number_
            field_name = field_name_org
            for table_name in list(tables_list):
                mtd_table = application.PROJECT.conn_manager.manager().metadata(
                    table_name, not db_admin
                )
                mtd_field = None
                if mtd_table is not None:
                    for fil in _filter:
                        if field_name.startswith(fil):
                            field_name = field_name.replace(fil, "")
                            field_name = field_name[:-1]

                    field_name_fixed = field_name
                    if field_name.find(".") > -1:
                        if table_name != field_name[0 : field_name.find(".")]:
                            continue
                        else:
                            field_name_fixed = field_name[field_name.find(".") + 1 :]
                    mtd_field = mtd_table.field(field_name_fixed)
                    if mtd_field is not None:
                        for existed_field in self._mtd_fields.values():
                            if existed_field.name() == mtd_field.name():
                                if (
                                    existed_field.metadata().name()  # type: ignore [union-attr]
                                    == mtd_field.metadata().name()  # type: ignore [union-attr]
                                ):
                                    LOGGER.info("%s already exists. Skipping" % mtd_field.name())
                                    continue
                        self._mtd_fields[number_] = mtd_field

                    # fields_list.remove(field_name_org)
                else:
                    if table_name not in self._invalid_tables:
                        self._invalid_tables.append(table_name)
                    # tables_list.remove(table_name)

    def suspected_injection(self) -> bool:
        """Return if the query contains suspicion of sql injection."""

        return False if self._suspected_injection is None else True

    def _check_sql_injection(self, where: List[str]) -> None:
        """Examine the query for suspected sql injection."""
        infected = ""

        # 1 concatenado.
        for word in where:
            if len(word) > 30:
                contador = [
                    suspicious_word
                    for suspicious_word in self._suspicious_keywords
                    if suspicious_word.lower() in word.lower()
                ]
                if len(contador) > 1:
                    infected = word
                    break

        # 2 bypass
        if not infected:
            rep = dict((re.escape(character), "") for character in self._suspicious_characters)
            pattern = re.compile("|".join(rep.keys()))
            split_where = str(
                pattern.sub(lambda m: rep[re.escape(m.group(0))], " ".join(where))
            ).lower()
            for bypass in self._suspicious_bypass_union_time:
                if bypass in split_where:
                    infected = "%s -> %s" % (bypass, " ".join(where))
                    break

        if infected:
            self._suspected_injection = infected
