"""
Collect information from the query, such as field tables, lines, etc ...
"""

from pineboolib.core.utils import logging
from pineboolib import application

import datetime
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces.ifieldmetadata import IFieldMetaData  # noqa: F401

LOGGER = logging.get_logger(__name__)


class SqlInspector(object):
    """SqlInspector Class."""

    _sql_list: List[str]
    _sql: str
    _invalid_tables: List[str]
    _mtd_fields: Dict[int, "IFieldMetaData"]
    _field_list: Dict[str, int]
    _table_names: List[str]
    _alias: Dict[str, str]
    _posible_float: bool
    _list_sql: List[str]

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

    def mtd_fields(self) -> Dict[int, "IFieldMetaData"]:
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

    def field_names(self) -> List[str]:  # FIXME: This does NOT preserve order!
        """
        Return a list with the name of the fields.

        @return fields list.
        """

        return list(self._field_list.keys())

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

        raise Exception("No se encuentra el campo %s el la query:\n%s" % (name, self._sql))

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
            for field in list(fields_list):
                if field == "":
                    continue
                new_fields_list.append(field)

            tables_list: List[str] = []
            if "where" in list_sql:
                index_where = list_sql.index("where")
                tables_list = list_sql[index_from + 1 : index_where]
            elif "order" in list_sql:
                index_order_by = list_sql.index("order")
                tables_list = list_sql[index_from + 1 : index_order_by]
            else:
                tables_list = list_sql[index_from + 1 :]
            tablas: List[str] = []
            self._alias = {}
            jump = 0
            # next_is_alias = None
            prev_ = ""
            last_was_table = False
            for table in tables_list:
                if jump > 0:
                    jump -= 1
                    prev_ = table
                    last_was_table = False
                    continue

                # if next_is_alias:
                #    alias[t] = next_is_alias
                #    next_is_alias = None
                #    prev_ = t
                #    continue

                # elif t in ("inner", "on"):
                #    print("Comprobando")
                #    if prev_ not in tablas:
                #        alias[prev_] = tablas[:-1]

                elif table == "on":
                    jump = 3
                    prev_ = table
                    last_was_table = False

                elif table in ("left", "join", "right", "inner", "outer"):
                    prev_ = table
                    last_was_table = False
                    continue

                # elif t == "on":
                # jump = 3
                #    prev_ = t
                #    continue
                elif table == "as":
                    #    next_is_alias = True
                    last_was_table = True
                    continue
                elif table == "and":
                    jump = 3
                    last_was_table = False

                else:
                    if last_was_table:
                        self._alias[table] = prev_
                        last_was_table = False
                    else:
                        if table != "":
                            if table not in tablas:
                                tablas.append(table)
                            last_was_table = True
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

        return ret_

    def resolve_value(self, pos: int, value: Any, raw: bool = False) -> Any:
        """
        Return a data type according to field type.

        @param pos. index postion.
        """

        if not self.mtd_fields():
            if isinstance(value, datetime.time):
                value = str(value)[0:8]
            return value

        type_ = "double"
        if pos not in self._mtd_fields.keys():
            if pos not in self._field_list.values():
                LOGGER.warning("SQL_TOOLS : resolve_value : No se encuentra la posición %s", pos)
                return None
        else:
            mtd = self._mtd_fields[pos]
            if mtd is not None:
                type_ = mtd.type()

        ret_: Any = value
        if type_ in ("string", "stringlist", "timestamp"):
            pass
        elif type_ == "double":
            try:
                ret_ = float(ret_)
            except ValueError as error:
                LOGGER.warning(str(error))

        elif type_ in ("int", "uint", "serial"):
            ret_ = int(ret_)
        elif type_ == "pixmap":

            if application.PROJECT.conn_manager is None:
                raise Exception("Project is not connected yet")

            metadata = mtd.metadata()
            if metadata is None:
                raise Exception("Metadata not found")
            if raw or not application.PROJECT.conn_manager.manager().isSystemTable(metadata.name()):
                ret_ = application.PROJECT.conn_manager.manager().fetchLargeValue(ret_)
        elif type_ == "date":
            from pineboolib.application import types

            ret_ = types.Date(str(ret_))
        elif type_ == "time":
            ret_ = str(ret_)
            if ret_.find(".") > -1:
                ret_ = ret_[0 : ret_.find(".")]
            elif ret_.find("+") > -1:
                ret_ = ret_[0 : ret_.find("+")]

        elif type_ in ("unlock", "bool"):
            from pineboolib.application import types

            ret_ = types.boolean(ret_)
        elif type_ == "bytearray":
            ret_ = bytearray(ret_)
        else:
            ret_ = float(ret_)
            print("TIPO DESCONOCIDO", type_, ret_)

        return ret_

    def _create_mtd_fields(self, fields_list: list, tables_list: list) -> None:
        """
        Solve the fields that make up the query.

        @param fields_list. fields list.
        @param tables_list. tables list.
        """
        if application.PROJECT.conn_manager is None:
            raise Exception("Project is not connected yet")

        _filter = ["sum(", "max(", "distint("]

        self._mtd_fields = {}
        self._invalid_tables = []
        self._table_names = list(tables_list)
        # self._field_list = {k: n for n, k in enumerate(fields_list)}

        for number_, field_name_org in enumerate(list(fields_list)):
            self._field_list[field_name_org] = number_
            field_name = field_name_org
            for table_name in list(tables_list):
                mtd_table = application.PROJECT.conn_manager.manager().metadata(table_name)
                if mtd_table is not None:
                    for fil in _filter:
                        if field_name.startswith(fil):
                            field_name = field_name.replace(fil, "")
                            field_name = field_name[:-1]

                    if field_name.find(".") > -1:
                        if table_name != field_name[0 : field_name.find(".")]:
                            continue
                        else:
                            field_name = field_name[field_name.find(".") + 1 :]
                    mtd_field = mtd_table.field(field_name)
                    if mtd_field is not None:
                        self._mtd_fields[number_] = mtd_field
                    # fields_list.remove(field_name_org)
                else:
                    if table_name not in self._invalid_tables:
                        self._invalid_tables.append(table_name)
                    # tables_list.remove(table_name)

    # https://ruddra.com/posts/dynamically-constructing-filters-based-on-string-input-using-sqlalchemy/


class DynamicFilter(object):
    def __init__(self, query=None, model_class=None, filter_condition=None):
        self.query = query
        self.model_class = model_class
        self.filter_condition = filter_condition

    def get_query(self):
        """
        Returns query with all the objects
        :return:
        """
        if not self.query:
            self.query = self.session.query(self.model_class)
        return self.query

    def filter_query(self, query, filter_condition):
        """
        Return filtered queryset based on condition.
        :param query: takes query
        :param filter_condition: Its a list, ie: [(key,operator,value)]
        operator list:
            eq for ==
            lt for <
            ge for >=
            in for in_
            like for like
            value could be list or a string
        :return: queryset

        """

        if query is None:
            query = self.get_query()
        # model_class = self.get_model_class()  # returns the query's Model
        model_class = self.model_class
        for raw in filter_condition:
            try:
                key, op, value = raw
            except ValueError:
                raise Exception("Invalid filter: %s" % raw)
            column = getattr(model_class, key, None)
            if not column:
                raise Exception("Invalid filter column: %s" % key)
            if op == "in":
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(","))
            else:
                try:
                    attr = (
                        list(filter(lambda e: hasattr(column, e % op), ["%s", "%s_", "__%s__"]))[0]
                        % op
                    )
                except IndexError:
                    raise Exception("Invalid filter operator: %s" % op)
                if value == "null":
                    value = None
                filt = getattr(column, attr)(value)
            query = query.filter(filt)
        return query

    def return_query(self, delete_later: bool = False):
        if delete_later:
            return self.filter_query(self.get_query(), self.filter_condition).delete(
                synchronize_session=False
            )

        return self.filter_query(self.get_query(), self.filter_condition)
