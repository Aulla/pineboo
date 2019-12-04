"""
Provide some functions based on data.
"""

from pineboolib.core.utils import logging
from pineboolib.application import types
from pineboolib import application

from . import pnsqlcursor, pnsqlquery

from typing import Any, Union, List, Optional, TYPE_CHECKING


if TYPE_CHECKING:

    from pineboolib.interfaces import iconnection, isqlcursor  # noqa : F401

logger = logging.getLogger("database.utils")


def nextCounter(
    name_or_series: str,
    cursor_or_name: Union[str, "isqlcursor.ISqlCursor"],
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

        if not isinstance(cursor_or_name, pnsqlcursor.PNSqlCursor):
            raise ValueError
        return _nextCounter_2(name_or_series, cursor_or_name)
    else:
        if not isinstance(cursor_or_name, str):
            raise ValueError
        return _nextCounter_3(name_or_series, cursor_or_name, cursor_)


def _nextCounter_2(name_: str, cursor_: "isqlcursor.ISqlCursor") -> Optional[Union[str, int]]:

    if not cursor_:
        return None

    tmd = cursor_.metadata()

    field = tmd.field(name_)
    if field is None:
        return None

    type_ = field.type()

    if type_ not in ["string", "double"]:
        return None

    _len = int(field.length())
    _cadena = None

    q = pnsqlquery.PNSqlQuery(None, cursor_.db().connectionName())
    q.setForwardOnly(True)
    q.setTablesList(tmd.name())
    q.setSelect(name_)
    q.setFrom(tmd.name())
    q.setWhere("LENGTH(%s)=%s" % (name_, _len))
    q.setOrderBy(name_ + " DESC")

    if not q.exec_():
        return None

    _max_range: int = 10 ** _len
    _numero: int = _max_range

    while _numero >= _max_range:
        if not q.next():
            _numero = 1
            break

        try:
            _numero = int(q.value(0))
            _numero = _numero + 1
        except Exception:
            pass

    if type_ == "string":
        _cadena = str(_numero)

        if len(_cadena) < _len:
            _cadena = _cadena.rjust(_len, "0")

        return _cadena

    elif type_ == "double":
        return _numero

    return None


def _nextCounter_3(serie_: str, name_: str, cursor_: "isqlcursor.ISqlCursor") -> Optional[str]:

    if not cursor_:
        return None

    tmd = cursor_.metadata()

    field = tmd.field(name_)
    if field is None:
        return None

    _type = field.type()
    if _type not in ["string", "double"]:
        return None

    _len: int = field.length() - len(serie_)
    _where: str = "length(%s)=%d AND %s" % (
        name_,
        field.length(),
        cursor_.db().connManager().manager().formatAssignValueLike(name_, "string", serie_, True),
    )

    q = pnsqlquery.PNSqlQuery(None, cursor_.db().connectionName())
    q.setForwardOnly(True)
    q.setTablesList(tmd.name())
    q.setSelect(name_)
    q.setFrom(tmd.name())
    q.setWhere(_where)
    q.setOrderBy(name_ + " DESC")

    if not q.exec_():
        return None

    _max_range: int = 10 ** _len
    _numero: int = _max_range

    while _numero >= _max_range:
        if not q.next():
            _numero = 1
            break

        _numero = int(q.value(0)[len(serie_) :])
        _numero = _numero + 1

    if _type in ["string", "double"]:
        _cadena: str = str(_numero)
        if len(_cadena) < _len:
            _cadena = _cadena.rjust(_len, "0")

        return _cadena

    return None


def sqlSelect(
    from_: str,
    select_: str,
    where_: Optional[str] = None,
    table_list_: Optional[Union[str, List, types.Array]] = None,
    size_: int = 0,
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
    # else:
    #    _qry.setTablesList(from_)

    _qry.setSelect(select_)
    _qry.setFrom(from_)
    _qry.setWhere(where_)
    # q.setForwardOnly(True)
    if not _qry.exec_():
        return False

    return _qry.value(0) if _qry.first() else False


def quickSqlSelect(
    from_: str,
    select_: str,
    where_: Optional[str] = None,
    conn_: Union[str, "iconnection.IConnection"] = "default",
) -> Any:
    """
    Quick version of sqlSelect. Run the query directly without checking.Use with caution.
    """

    if where_ is None:
        where_ = "1 = 1"

    _qry = pnsqlquery.PNSqlQuery(None, conn_)
    if not _qry.exec_("SELECT %s FROM %s WHERE %s " % (select_, from_, where_)):
        return False

    return _qry.value(0) if _qry.first() else False


def sqlInsert(
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
    _field_list: Union[List[Any], types.Array]
    _value_list: Union[List[Any], types.Array]

    if isinstance(field_list_, str):
        _field_list = field_list_.split(",")
    else:
        _field_list = field_list_

    if isinstance(value_list_, str):
        _value_list = value_list_.split(",")
    elif isinstance(value_list_, (List, types.Array)):
        _value_list = value_list_
    else:
        _value_list = [value_list_]

    if len(_field_list) != len(_value_list):
        return False

    _cursor = pnsqlcursor.PNSqlCursor(table_, True, conn_)
    _cursor.setModeAccess(_cursor.Insert)
    _cursor.refreshBuffer()

    for _pos in range(len(_field_list)):

        if _value_list[_pos] is None:
            _cursor.bufferSetNull(_field_list[_pos])
        else:
            _cursor.setValueBuffer(_field_list[_pos], _value_list[_pos])

    return _cursor.commitBuffer()


def sqlUpdate(
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


def sqlDelete(
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


def quickSqlDelete(
    table_: str, where_: str, conn_: Union[str, "iconnection.IConnection"] = "default"
) -> bool:
    """
    Quick version of sqlDelete. Execute the query directly without checking and without committing signals.Use with caution.
    """
    return execSql("DELETE FROM %s WHERE %s" % (table_, where_), conn_)


def execSql(sql_: str, conn_: Union[str, "iconnection.IConnection"] = "default") -> bool:
    """
    Run a query.
    """

    if application.project.conn_manager is None:
        raise Exception("Project is not connected yet")

    if isinstance(conn_, str):
        my_conn = application.project.conn_manager.useConn(conn_)
    else:
        my_conn = conn_

    _cur = my_conn.cursor()
    try:
        last = my_conn.lastError()
        logger.warning("execSql: Ejecutando la consulta : %s", sql_)
        # sql = conn_.db().driver().fix_query(sql)
        # cur.execute(sql)
        # conn_.conn.commit()
        my_conn.execute_query(sql_, _cur)
        if my_conn.lastError() != last:
            return False
        return True
    except Exception as exc:
        logger.exception("execSql: Error al ejecutar la consulta SQL: %s %s", sql_, exc)
        return False
