"""
Provide some functions based on data.
"""

from pineboolib.core.utils import logging
from pineboolib.application import types, qsadictmodules, load_script
from pineboolib import application
from pineboolib.application.database.orm import dummy_cursor
from . import pnsqlcursor, pnsqlquery


from typing import Any, Union, List, Optional, TYPE_CHECKING


if TYPE_CHECKING:

    from pineboolib.interfaces import iconnection, isqlcursor  # noqa : F401 # pragma: no cover
    from pineboolib.application import file as file_app  # noqa : F401 # pragma: no cover

LOGGER = logging.get_logger(__name__)


def next_counter(
    name_or_series: str,
    cursor_or_name: Union[str, "isqlcursor.ISqlCursor", "dummy_cursor.DummyCursor"],
    cursor_: Optional["isqlcursor.ISqlCursor"] = None,
) -> Optional[Union[str, int]]:
    """
    Return the following value of a counter type field of a table.

    This method is very useful when inserting records in which
    the reference is sequential and we don't remember which one was the last
    number used The return value is a QVariant of the field type is
    the one that looks for the last reference. The most advisable thing is that the type
    of the field be 'String' because this way it can be formatted and be
    used to generate a barcode. The function anyway
    supports both that the field is of type 'String' and of type 'double'.

    @param name Field name
    @param cursor_ Cursor to the table where the field is located.
    @return Qvariant with the following number.
    @author Andrés Otón Urbano.
    """
    """
    dpinelo: This method is an extension of nextCounter but allowing the introduction of a first
    character sequence It is useful when we want to keep different counters within the same table.
    Example, Customer Group Table: We add a prefix field, which will be a letter: A, B, C, D.
    We want customer numbering to be of type A00001, or B000023. With this function, we can
    Keep using the counter methods when we add that letter.

    This method returns the following value of a counter type field of a table for a given series.

    This method is very useful when inserting records in which
    the reference is sequential according to a sequence and we don't remember which one was the last
    number used The return value is a QVariant of the field type is
    the one that looks for the last reference. The most advisable thing is that the type
    of the field be 'String' because this way it can be formatted and be
    used to generate a barcode. The function anyway
    supports both that the field is of type 'String' and of type 'double'.

    @param series series that differentiates counters
    @param name Field name
    @param cursor_ Cursor to the table where the field is located.
    @return Qvariant with the following number.
    @author Andrés Otón Urbano.
    """

    if cursor_ is None:

        if not isinstance(cursor_or_name, (pnsqlcursor.PNSqlCursor, dummy_cursor.DummyCursor)):
            raise ValueError
        return _next_counter2(name_or_series, cursor_or_name)
    else:
        if not isinstance(cursor_or_name, str):
            raise ValueError
        return _next_counter3(name_or_series, cursor_or_name, cursor_)


def _next_counter2(
    name_: str, cursor_: Union["isqlcursor.ISqlCursor", "dummy_cursor.DummyCursor"]
) -> Optional[Union[str, int]]:

    if not cursor_:
        return None

    tmd = cursor_.metadata()

    field = tmd.field(name_)
    if field is None:
        return None

    type_ = field.type()

    if type_ not in ("string", "double"):
        return None

    _len = int(field.length())
    _where: str = cursor_.db().sqlLength(name_, _len)

    qry = pnsqlquery.PNSqlQuery(None, cursor_.db())
    qry.setForwardOnly(True)
    qry.setTablesList(tmd.name())
    qry.setSelect(name_)
    qry.setFrom(tmd.name())
    qry.setWhere(_where)
    qry.setOrderBy(name_ + " ASC")

    if not qry.exec_():
        return None

    _numero: int = int(qry.value(0)) if qry.last() else 0

    _numero += 1

    if type_ == "string":
        _cadena = str(_numero)

        return _cadena.rjust(_len, "0") if len(_cadena) < _len else _cadena

    elif type_ == "double":
        return _numero

    return None


def _next_counter3(
    serie_: str, name_: str, cursor_: Union["isqlcursor.ISqlCursor", "dummy_cursor.DummyCursor"]
) -> Optional[Union[str, int]]:

    if not cursor_:
        return None

    tmd = cursor_.metadata()

    field = tmd.field(name_)

    if field is None:
        return None

    _type = field.type()

    _len: int = field.length() - len(serie_)
    _where: str = "length(%s)=%d AND %s" % (
        name_,
        field.length(),
        cursor_.db().connManager().manager().formatAssignValueLike(name_, "string", serie_, True),
    )

    qry = pnsqlquery.PNSqlQuery(None, cursor_.db())
    qry.setForwardOnly(True)
    qry.setTablesList(tmd.name())
    qry.setSelect(name_)
    qry.setFrom(tmd.name())
    qry.setWhere(_where)
    qry.setOrderBy(name_ + " ASC")

    if not qry.exec_():
        return None

    _numero: int = int(qry.value(0)[len(serie_) :]) if qry.last() else 0
    _numero += 1

    if _type == "string":
        _cadena: str = str(_numero)
        return _cadena.rjust(_len, "0") if len(_cadena) < _len else _cadena
    elif _type == "double":
        return _numero

    return None


def sql_select(
    from_: str,
    select_: str,
    where_: Optional[str] = None,
    table_list_: Optional[Union[str, List, types.Array]] = None,
    size_: int = 0,  # pylint: disable=unused-argument
    conn_: Union[str, "iconnection.IConnection"] = "default",
) -> Any:
    """
    Execute a query of type select, returning the results of the first record found.

    @param from_: from the query statement.
    @param select_: Select statement of the query, which will be the name of the field to return.
    @param where_: Where statement of the query.
    @param table_list_: Tableslist statement of the query. Required when more than one table is included in the from statement.
    @param size_: Number of lines found. (-1 if there is error).
    @param conn_name_ Connection name.
    @return Value resulting from the query or false if it finds nothing.
    """

    if where_ is None:
        where_ = "1 = 1"

    _qry = pnsqlquery.PNSqlQuery(None, conn_)

    if table_list_:
        _qry.setTablesList(table_list_)

    _qry.setSelect(select_)
    _qry.setFrom(from_)
    _qry.setWhere(where_)

    return False if not _qry.exec_() or not _qry.first() else _qry.value(0)


def quick_sql_select(
    from_: str,
    select_: str,
    where_: Optional[str] = "1 = 1",
    conn_: Union[str, "iconnection.IConnection"] = "default",
) -> Any:
    """
    Quick version of sqlSelect. Run the query directly without checking.Use with caution.
    """

    _qry = pnsqlquery.PNSqlQuery(None, conn_)
    return (
        _qry.value(0)
        if _qry.exec_("SELECT %s FROM %s WHERE %s " % (select_, from_, where_)) and _qry.first()
        else False
    )


def sql_insert(
    table_: str,
    field_list_: Union[str, List[str], types.Array],
    value_list_: Union[str, List, bool, int, float, types.Array],
    conn_: Union[str, "iconnection.IConnection"] = "default",
) -> bool:
    """
    Perform the insertion of a record in a table using an FLSqlCursor object.

    @param table_ Table name.
    @param field_list_ Comma separated list of field names.
    @param value_list_ Comma separated list of corresponding values.
    @param conn_name_ Connection name.
    @return True in case of successful insertion, False in any other case.
    """
    _value_list: Union[List[Any], types.Array] = (
        value_list_.split(",")
        if isinstance(value_list_, str)
        else value_list_
        if isinstance(value_list_, (List, types.Array))
        else [value_list_]  # type: ignore [list-item]
    )

    _field_list: Union[List[Any], types.Array] = (
        field_list_.split(",") if isinstance(field_list_, str) else field_list_
    )

    len_field_list = len(_field_list)

    if len_field_list != len(_value_list):
        return False

    _cursor = pnsqlcursor.PNSqlCursor(table_, True, conn_)
    _cursor.setModeAccess(_cursor.Insert)
    _cursor.refreshBuffer()

    for _pos in range(len_field_list):

        if _value_list[_pos] is None:
            _cursor.setNull(_field_list[_pos])
        else:
            _cursor.setValueBuffer(_field_list[_pos], _value_list[_pos])

    return _cursor.commitBuffer()


def sql_update(
    table_: str,
    field_list_: Union[str, List[str], types.Array],
    value_list_: Union[str, List, bool, int, float, types.Array],
    where_: str,
    conn_: Union[str, "iconnection.IConnection"] = "default",
) -> bool:
    """
    Modify one or more records in a table using an FLSqlCursor object.

    @param table_ Table name.
    @param field_list_ Comma separated list of field names.
    @param value_list_ Comma separated list of corresponding values.
    @param where_ Where statement to identify the records to be edited.
    @param conn_name_ Connection name.
    @return True in case of successful insertion, false in any other case.
    """

    _cursor = pnsqlcursor.PNSqlCursor(table_, True, conn_)
    _cursor.select(where_)
    _cursor.setForwardOnly(True)
    while _cursor.next():

        _cursor.setModeAccess(_cursor.Edit)
        _cursor.refreshBuffer()

        if isinstance(field_list_, (List, types.Array)):
            for _pos in range(len(field_list_)):
                _cursor.setValueBuffer(
                    field_list_[_pos],
                    value_list_[_pos]
                    if isinstance(value_list_, (List, types.Array))
                    else value_list_,
                )
        else:
            _cursor.setValueBuffer(field_list_, value_list_)

        if not _cursor.commitBuffer():
            return False

    return True


def sql_delete(
    table_: str, where_: str, conn_: Union[str, "iconnection.IConnection"] = "default"
) -> bool:
    """
    Delete one or more records in a table using an FLSqlCursor object.

    @param table_ Table name.
    @param where_ Where statement to identify the records to be deleted.
    @param conn_name_ Connection name.
    @return True in case of successful insertion, false in any other case.
    """

    _cursor = pnsqlcursor.PNSqlCursor(table_, True, conn_)

    # if not c.select(w):
    #     return False

    _cursor.select(where_)
    _cursor.setForwardOnly(True)

    while _cursor.next():
        _cursor.setModeAccess(_cursor.Del)
        _cursor.refreshBuffer()
        if not _cursor.commitBuffer():
            return False

    return True


def quick_sql_delete(
    table_: str, where_: str, conn_: Union[str, "iconnection.IConnection"] = "default"
) -> bool:
    """
    Quick version of sqlDelete. Execute the query directly without checking and without committing signals.Use with caution.
    """
    return exec_sql("DELETE FROM %s WHERE %s" % (table_, where_), conn_)


def exec_sql(sql_: str, conn_: Union[str, "iconnection.IConnection"] = "default") -> bool:
    """
    Run a query.
    """

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    my_conn = application.PROJECT.conn_manager.useConn(conn_) if isinstance(conn_, str) else conn_

    try:
        last = my_conn.lastError()
        LOGGER.info("execSql: Ejecutando la consulta : %s", sql_)
        sql_ = sql_.replace("%", "%%") if my_conn.driver()._parse_porc else sql_

        my_conn.execute_query(sql_)  # noqa: F841
        return my_conn.lastError() == last
    except Exception as exc:
        LOGGER.exception("execSql: Error al ejecutar la consulta SQL: %s %s", sql_, exc)
        return False


def process_file_class(file_obj: "file_app.File") -> None:
    """Process file class."""
    file_ = open(file_obj.path(), "r", encoding="UTF-8", errors="replace")
    text_ = file_.read()
    class_name = ""
    if text_.find("public_class =") > -1:
        class_name = text_[text_.find("public_class =") + 15 :].split(" ")[0][1:-1]
        if class_name.find('"') > -1:
            class_name = class_name[0 : class_name.find('"')]
        if class_name.find("'") > -1:
            class_name = class_name[0 : class_name.find("'")]

    if class_name:
        application.FILE_CLASSES[class_name] = file_obj.filename


class ClassManager(object):
    """ClassManager class."""

    def __getattr__(self, name: str) -> Any:
        """Return class."""

        class_ = None
        if name in application.FILE_CLASSES.keys():
            class_ = getattr(
                qsadictmodules.QSADictModules.qsa_dict_modules(), "%s_class" % name, None
            )
            if class_ is None:
                module_ = load_script.load_module(application.FILE_CLASSES[name])
                main_class = getattr(module_, name, None)
                qsadictmodules.QSADictModules.set_qsa_tree("%s_class" % name, main_class)
                class_ = main_class
        return class_

    def classes(self) -> List[str]:
        """Return available models list."""
        return list(application.FILE_CLASSES.keys())
