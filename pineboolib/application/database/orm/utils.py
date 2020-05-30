"""Utils module."""

from typing import List, Any, TYPE_CHECKING


from pineboolib.application import qsadictmodules
import sqlalchemy

if TYPE_CHECKING:
    from sqlalchemy.orm import query


class OrmManager(object):
    """OrmManager class."""

    def __getattr__(self, name: str) -> Any:
        """Return model."""

        return qsadictmodules.QSADictModules.orm_(name)

    def models(self) -> List[str]:
        """Return available models list."""
        result_list: List[str] = []
        for name in list(qsadictmodules.QSADictModules.qsa_dict_modules()):
            if str(name).endswith("_model"):
                result_list.append(name[:-6])

        return result_list


class DynamicFilter(object):
    """DynamicFilter class."""

    def __init__(self, query=None, model_class=None, filter_condition=None):
        """Initialize."""

        self.query = query
        self.model_class = model_class
        self.filter_condition = filter_condition
        self.order_by: List[List[str]] = []

    # def get_query(self):
    #    """
    #    Returns query with all the objects
    #    :return:
    #    """
    # if not self.query:
    #    self.query = self.session.query(self.model_class)
    #    return self.query

    def set_filter_condition_from_string(self, filter_str: str) -> None:
        """Set filter condition from string."""
        filter_list = []
        order_by_list = []
        order_by_str: str = ""

        pos_order = filter_str.lower().find("order by")
        if pos_order > -1:
            order_by_str = filter_str[pos_order + 9 :].lower()
            filter_str = filter_str[:pos_order]

            for order in order_by_str.split(","):
                order = order.strip()
                order_by_list.append(order.split(" "))

        if filter_str:
            filter_str = filter_str.replace("<=", " le ")
            filter_str = filter_str.replace(">=", " ge ")
            filter_str = filter_str.replace("=", " eq ")
            filter_str = filter_str.replace("<", " lt ")
            filter_str = filter_str.replace(">", " gt ")
            filter_str = filter_str.replace(" in ", " in_ ")

            item = []
            pasa = 0

            list_ = filter_str.split(" ")

            for number, part in enumerate(list_):

                if pasa:
                    pasa -= 1
                    continue

                if not part:
                    continue
                if part.startswith("upper("):
                    item.append("upper")
                    part = part[6:-1]
                elif part.find("'") > -1:
                    pos_ini = part.find("'")
                    while part[pos_ini + 1 :].find("'") == -1:
                        part = "%s %s" % (part, list_[number + 1])
                        pasa += 1

                    part = part.replace("'", "")

                elif part.lower() in ["and", "or"]:
                    filter_list.append(item)
                    item = []
                    part = part.lower()

                item.append(part)

            if item and item != ["1", "eq", "1"]:
                filter_list.append(item)

        # =======================================================================
        # print(
        #     "\nConvirtiendo:",
        #     filter_str,
        #     "\nOrder by:",
        #     order_by_list,
        #     "\nActual:",
        #     filter_list,
        #     "\nORDER:",
        #     order_by_list,
        # )
        # =======================================================================

        self.order_by = order_by_list
        self.filter_condition = filter_list

        # ===============================================================================
        #         filter_list = []
        #         try:
        #             for key, filter in self.where_filters.items():
        #                 if not filter:
        #                     continue
        #                 # filter = filter.lower()
        #                 filter = filter.replace("=", "eq")
        #                 filter = filter.replace("<=", "le")
        #                 filter = filter.replace(">=", "ge")
        #                 filter = filter.replace("<", "lt")
        #                 filter = filter.replace(">", "gt")
        #                 filter = filter.replace(" in ", " in_ ")
        #
        #                 item = filter.split(" ")
        #                 for number, part in enumerate(item):
        #                     if part.startswith("upper("):
        #                         item[number] = part[6:-1]
        #
        #                     if part.startswith("'"):
        #                         item[number] = part[1:-1]
        #                 filter_list.append(item)
        #         except Exception as error:
        #             LOGGER.warning(
        #                 "creando filtro %s : %s", self.where_filters, str(error), stack_info=True
        #             )
        #
        #         print("**", filter_list)
        # ===============================================================================
        # print("Filtro final", self.filter_condition)

    def filter_query(self, query, filter_condition) -> "query.Query":
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

        # if query is None:
        #    query = self.get_query()
        # model_class = self.get_model_class()  # returns the query's Model
        model_class = self.model_class
        for raw in filter_condition:
            try:
                func_ = ""
                func_class = None
                extra_filter = ""

                if len(raw) == 3:
                    key, option, value = raw
                elif len(raw) == 4:
                    func_or_extra, key, option, value = raw

                    if func_or_extra in ["and", "or"]:
                        extra_filter = func_or_extra
                    else:
                        func_ = func_or_extra

                elif len(raw) == 5:
                    extra_filter, func_, key, option, value = raw
                else:
                    raise Exception("arguments length error", raw)

            except ValueError:
                raise Exception("Invalid filter: %s" % raw)
            column = getattr(model_class, key, None)
            try:
                if func_:
                    func_class = getattr(sqlalchemy.func, func_)
            except Exception:
                raise Exception("Error parsing func_")

            if not column:
                raise Exception("Invalid filter column: %s" % key, raw)
            if option == "in":
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(","))
            else:
                try:
                    attr = (
                        list(
                            filter(lambda e: hasattr(column, e % option), ["%s", "%s_", "__%s__"])
                        )[0]
                        % option
                    )
                except IndexError:
                    raise Exception("Invalid filter operator: %s" % option)
                if value == "null":
                    value = None

                filt = getattr(column if not func_class else func_class(column), attr)(value)

            if extra_filter not in ["and", ""]:
                if extra_filter == "or":
                    filt = sqlalchemy.or_(filt)
                else:
                    raise Exception("Unknown extra filter", extra_filter)

            query = query.filter(filt)

        for name, ord in self.order_by:
            column_order = getattr(model_class, name, None)
            query = query.order_by(column_order.desc() if ord == "desc" else column_order.asc())

        return query

    def return_query(self) -> "query.Query":
        """Return query object."""

        return self.filter_query(self.query, self.filter_condition)
