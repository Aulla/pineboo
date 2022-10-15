# -*- coding: utf-8 -*-
"""
Defines PNCursorTableModel class.
"""


from PyQt6 import QtCore, QtGui, QtWidgets  # type: ignore[import]

from pineboolib.core.utils import logging, utils_base

from sqlalchemy import exc, orm, inspect
from pineboolib.application.utils import date_conversion, xpm

from .orm import utils as orm_utils
from . import pnsqlquery


import itertools
import locale
import os
import datetime


from typing import Any, Optional, List, Dict, Tuple, cast, Callable, Union, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401 # pragma: no cover
    from pineboolib.interfaces import (
        iconnection,
        isqlcursor,
        isqldriver,
        itablemetadata,
    )  # pragma: no cover
    from pineboolib.fllegacy import fldatatable  # pragma: no cover
    from . import pnconnectionmanager  # pragma: no cover
    from . import pnbuffer  # pragma: no cover

DEBUG = False
CURSOR_COUNT = itertools.count()
LOGGER = logging.get_logger(__name__)


class PNCursorTableModel(QtCore.QAbstractTableModel):
    """
    Link between FLSqlCursor and database.
    """

    # rows: int
    cols: int
    _use_timer = True
    where_filter: str
    where_filters: Dict[str, str] = {}
    _metadata: Optional["pntablemetadata.PNTableMetaData"]
    _sort_order = ""
    _disable_refresh: bool
    color_function_ = None
    need_update = False
    _driver_sql = None
    _show_pixmap: bool
    _size = None
    parent_view: Optional["fldatatable.FLDataTable"]
    sql_str = ""
    _can_fetch_more_rows: bool

    _parent: "isqlcursor.ISqlCursor"
    _initialized: Optional[
        bool
    ] = None  # Usa 3 estado None, True y False para hacer un primer refresh retardado si pertenece a un fldatatable
    _check_column: Dict[str, QtWidgets.QCheckBox]

    _data: List[List[Any]]
    _vdata: List[Optional[List[Any]]]

    sql_fields: List[str]
    sql_fields_omited: List[str]
    sql_fields_without_check: List[str]
    pkpos: List[int]
    ckpos: List[int]
    pkidx: Dict[Tuple, int]
    ckidx: Dict[Tuple, int]
    _column_hints: List[int]
    _current_row_data: Any
    _current_row_index: int
    _tablename: str
    _order: str

    # _data_proxy: List[Callable]
    _data_proxy: Optional["ProxyIndex"]

    _grid_obj: Dict[int, Any]

    def __init__(self, conn: "iconnection.IConnection", parent: "isqlcursor.ISqlCursor") -> None:
        """
        Initialize.

        @param conn. PNConnection Object
        @param parent. related FLSqlCursor
        """

        super(PNCursorTableModel, self).__init__()
        self._parent = parent
        self.parent_view = None

        metadata = self._parent.private_cursor.metadata_

        self.cols = 0
        self._metadata = None

        if not metadata:
            return

        self._metadata = metadata

        self._driver_sql = self._parent.db().driver()

        self.sql_fields = []
        self.sql_fields_omited = []
        self.sql_fields_without_check = []
        self.col_aliases: List[str] = []
        self._current_row_data = None
        self._current_row_index = -1

        # Indices de busqueda segun PK y CK. Los array "pos" guardan las posiciones
        # de las columnas afectadas. PK normalmente valdrá [0,].
        # CK puede ser [] o [2,3,4] por ejemplo.
        # En los IDX tendremos como clave el valor compuesto, en array, de la clave.
        # Como valor del IDX tenemos la posicion de la fila.
        # Si se hace alguna operación en _data como borrar filas intermedias hay
        # que invalidar los indices. Opcionalmente, regenerarlos.
        self.pkpos = []
        self.ckpos = []
        self.pkidx = {}
        self.ckidx = {}
        self._check_column = {}
        # Establecer a False otra vez si el contenido de los indices es erróneo.
        self.indexes_valid = False
        # self._data = []
        self._vdata = []
        self._column_hints = []
        self.updateColumnsCount()

        # self.pendingRows = 0
        # self.lastFetch = 0.0
        # self._fetched_rows = 0
        self._show_pixmap = True
        self.color_function_ = None
        # self.color_dict_ = {}

        self.where_filter = "1=1"
        self.where_filters = {}
        self.where_filters["main-filter"] = ""
        self.where_filters["filter"] = ""
        self.sql_str = ""
        self._tablename = ""
        self._order = ""

        self._disable_refresh = False
        self._initialized = None

        self._data_proxy = None

        if self.metadata().isQuery():
            query = self.conn_manager.manager().query(self.metadata().query())
            if query is None:
                raise Exception("query is empty!")
            self._tablename = query.from_()
        else:
            self._tablename = self.metadata().name()

        self._grid_obj = {}

    def disable_refresh(self, disable: bool) -> None:
        """
        Disable refresh.

        e.g. FLSqlQuery.setForwardOnly(True).
        @param disable. True or False
        """

        self._disable_refresh = disable

    def sort(
        self, column: int, order: QtCore.Qt.SortOrder = QtCore.Qt.SortOrder.AscendingOrder
    ) -> None:
        """
        Change order by used ASC/DESC and column.

        @param col. Column to sort by
        @param order. 0 ASC, 1 DESC
        """
        col = column
        # order 0 ascendente , 1 descendente
        ord = "ASC"
        if order == QtCore.Qt.SortOrder.DescendingOrder:
            ord = "DESC"

        field_mtd = self.metadata().indexFieldObject(col)
        if field_mtd.type() == "check":
            return

        col_name = field_mtd.name()

        order_list: List[str] = []
        found_ = False
        if self._sort_order:
            for column_name in self._sort_order.split(","):
                if col_name in column_name and ord in column_name:
                    found_ = True
                    order_list.append("%s %s" % (col_name, ord))
                else:
                    order_list.append(column_name)

            if not found_:
                LOGGER.debug(
                    "%s. Se intenta ordernar por una columna (%s) que no está definida en el order by previo (%s). "
                    "El order by previo se perderá" % (__name__, col_name, self._sort_order)
                )
            else:
                self._sort_order = ",".join(order_list)

        if not found_:
            self._sort_order = "%s %s" % (col_name, ord)
            self.refresh()

    def getSortOrder(self) -> str:
        """
        Get current sort order.

        Returns string  with sortOrder value.
        @return string  with info about column and order
        """
        return self._sort_order

    def setSortOrder(self, sort_order: str) -> None:
        """
        Set current ORDER BY.
        """
        # self._sort_order = ""
        self._sort_order = sort_order

    def data(
        self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole
    ) -> Any:
        """
        Retrieve information about a record.

        (overload of QAbstractTableModel)
        Could return alignment, backgroun color, value... depending on role.

        @param index. Register position
        @param role. information type required
        @return solicited data
        """

        row = index.row()
        col = index.column()
        field = self.metadata().indexFieldObject(col)
        _type = field.type()
        res_color_function: List[str] = []

        obj_ = self.get_obj_from_row(row)

        result = getattr(obj_, field.name(), None)

        if _type == "check":
            primary_key = getattr(obj_, self.metadata().primaryKey())
            if primary_key not in self._check_column.keys():
                result = QtWidgets.QCheckBox()
                self._check_column[primary_key] = result

        if self.parent_view and role in [
            QtCore.Qt.ItemDataRole.BackgroundRole,
            QtCore.Qt.ItemDataRole.ForegroundRole,
        ]:
            fun_get_color, iface = self.parent_view.functionGetColor()
            if fun_get_color is not None:
                context_ = None
                fun_name_ = None
                if fun_get_color.find(".") > -1:
                    list_ = fun_get_color.split(".")
                    from pineboolib.application.safeqsa import SafeQSA

                    qsa_widget = SafeQSA.get_any(list_[0])
                    fun_name_ = list_[1]
                    if qsa_widget:
                        context_ = qsa_widget.iface
                else:
                    context_ = iface
                    fun_name_ = fun_get_color

                function_color = getattr(context_, fun_name_, None)
                if function_color is not None:
                    field_name = field.name()
                    field_value = result
                    cursor = self._parent
                    selected = False
                    res_color_function = function_color(
                        field_name, field_value, cursor, selected, _type
                    )
                else:
                    raise Exception(
                        "No se ha resuelto functionGetColor %s desde %s" % (fun_get_color, context_)
                    )
        # print("Data ", index, role)
        # print("Registros", self.rowCount())
        # roles
        # 0 QtCore.Qt.DisplayRole
        # 1 QtCore.Qt.DecorationRole
        # 2 QtCore.Qt.EditRole
        # 3 QtCore.Qt.ToolTipRole
        # 4 QtCore.Qt.StatusTipRole
        # 5 QtCore.Qt.WhatThisRole
        # 6 QtCore.Qt.FontRole
        # 7 QtCore.Qt.TextAlignmentRole
        # 8 QtCore.Qt.BackgroundRole
        # 9 QtCore.Qt.ForegroundRole

        if role == QtCore.Qt.ItemDataRole.CheckStateRole and _type == "check":
            if primary_key in self._check_column.keys():
                if self._check_column[primary_key].isChecked():
                    return QtCore.Qt.CheckState.Checked

            return QtCore.Qt.CheckState.Unchecked

        elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            result = QtCore.Qt.AlignmentFlag.AlignVCenter
            if _type in ("int", "double", "uint"):
                result = result | QtCore.Qt.AlignmentFlag.AlignRight
            elif _type in ("bool", "date", "time"):
                result = result | QtCore.Qt.AlignmentFlag.AlignCenter
            elif _type in ("unlock", "pixmap"):
                result = result | QtCore.Qt.AlignmentFlag.AlignHCenter

            return result

        elif role in (QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole):
            if not field.visible():
                result = None
            # r = self._vdata[row]
            elif _type == "bool":
                if result in (True, "1"):
                    result = "Sí"
                else:
                    result = "No"

            elif _type in ("unlock", "pixmap"):

                result = None

            elif _type in ("string", "stringlist", "timestamp", "json"):
                if not result:
                    if _type == "stringlist":
                        result = "..."
                    else:
                        result = ""
                else:
                    result = str(result)

            elif _type == "time" and result:
                result = str(result)

            elif _type == "date":
                # Si es str lo paso a datetime.date
                if isinstance(result, str):
                    if len(result.split("-")[0]) == 4:
                        result = date_conversion.date_amd_to_dma(result)

                    if result:
                        list_ = result.split("-")
                        result = datetime.date(int(list_[2]), int(list_[1]), int(list_[0]))

                if isinstance(result, datetime.date):
                    # Cogemos el locale para presentar lo mejor posible la fecha
                    try:
                        locale.setlocale(locale.LC_TIME, "")
                        if os.name == "nt":
                            date_format = "%%d/%%m/%%y"
                        else:
                            date_format = locale.nl_langinfo(locale.D_FMT)
                        date_format = date_format.replace("y", "Y")  # Año con 4 dígitos
                        date_format = date_format.replace("/", "-")  # Separadores
                        result = result.strftime(date_format)
                    except AttributeError:
                        import platform

                        LOGGER.warning(
                            "locale specific date format is not yet implemented for %s",
                            platform.system(),
                        )

            elif _type == "check":
                return

            elif _type == "double":
                if result is not None:
                    # d = QtCore.QLocale.system().toString(float(d), "f", field.partDecimal())
                    result = utils_base.format_double(
                        result, field.partInteger(), field.partDecimal()
                    )
            elif _type in ("int", "uint"):
                if result is not None:
                    result = QtCore.QLocale.system().toString(int(result))
            if self.parent_view is not None:
                self.parent_view.resize_column(col, result)

            return result

        elif role == QtCore.Qt.ItemDataRole.DecorationRole:
            pixmap = None
            if _type in ("unlock", "pixmap") and self.parent_view:
                row_height = self.parent_view.rowHeight(row)  # Altura row
                row_width = self.parent_view.columnWidth(col)

                if _type == "unlock":
                    if result in (True, "1"):
                        pixmap = QtGui.QPixmap(
                            utils_base.filedir("./core/images/icons", "unlock.png")
                        )
                    elif result in (False, "0"):

                        pixmap = QtGui.QPixmap(
                            utils_base.filedir("./core/images/icons", "lock.png")
                        )
                else:
                    if not self._parent.private_cursor._is_system_table:
                        data = self.conn_manager.manager().fetchLargeValue(result)
                    else:
                        data = xpm.cache_xpm(result)

                    pixmap = QtGui.QPixmap(data)
                    if not pixmap.isNull():
                        new_size = row_height - 1
                        if new_size > row_width:
                            new_size = row_width

                        pixmap = pixmap.scaled(new_size, new_size)

                if self.parent_view.showAllPixmap() or row == self.parent_view.cur.at():
                    if pixmap and not pixmap.isNull() and self.parent_view:
                        new_pixmap = QtGui.QPixmap(row_width, row_height)  # w , h
                        center_width = (row_width - pixmap.width()) / 2
                        center_height = (row_height - pixmap.height()) / 2
                        new_pixmap.fill(QtCore.Qt.GlobalColor.transparent)
                        painter = QtGui.QPainter(new_pixmap)
                        painter.drawPixmap(
                            int(center_width),
                            int(center_height),
                            pixmap.width(),
                            pixmap.height(),
                            pixmap,
                        )

                        pixmap = new_pixmap

            return pixmap

        elif role == QtCore.Qt.ItemDataRole.BackgroundRole:
            if _type == "bool":
                if result in (True, "1"):
                    result = QtGui.QBrush(QtCore.Qt.GlobalColor.green)
                else:
                    result = QtGui.QBrush(QtCore.Qt.GlobalColor.red)

            elif _type == "check":
                obj_ = self._check_column[primary_key]  # type: ignore [assignment]
                result = (
                    QtGui.QBrush(QtCore.Qt.GlobalColor.green)
                    if obj_.isChecked()  # type: ignore [union-attr]
                    else QtGui.QBrush(QtCore.Qt.GlobalColor.white)
                )

            else:
                if res_color_function and len(res_color_function) and res_color_function[0] != "":
                    color_ = QtGui.QColor(res_color_function[0])
                    style_ = getattr(QtCore.Qt, res_color_function[2], None)
                    result = QtGui.QBrush(color_)
                    result.setStyle(style_)
                else:
                    result = None

            return result

        elif role == QtCore.Qt.ItemDataRole.ForegroundRole:
            if _type == "bool":
                if result in (True, "1"):
                    result = QtGui.QBrush(QtCore.Qt.GlobalColor.black)
                else:
                    result = QtGui.QBrush(QtCore.Qt.GlobalColor.white)
            else:
                if res_color_function and len(res_color_function) and res_color_function[1] != "":
                    color_ = QtGui.QColor(res_color_function[1])
                    style_ = getattr(QtCore.Qt, res_color_function[2], None)
                    result = QtGui.QBrush(color_)
                    result.setStyle(style_)
                else:
                    result = None

            return result

        return None

    def update_rows(self) -> None:
        """Update virtual records managed by its model."""

        parent = QtCore.QModelIndex()
        to_row = self.rowCount() - 1

        self.beginInsertRows(parent, 0, to_row)
        self.endInsertRows()
        top_left = self.index(0, 0)
        botom_rigth = self.index(to_row, self.cols - 1)
        self.dataChanged.emit(top_left, botom_rigth)  # type: ignore [attr-defined] # noqa: F821
        self.indexes_valid = True

    def _refresh_field_info(self) -> None:
        """
        Check if query fields do exist.

        If any field does not exist it gets marked as ommitted.
        """
        is_query = self.metadata().isQuery()
        qry_tables: List[
            Tuple[
                str,
                Optional[Union["itablemetadata.ITableMetaData", "pntablemetadata.PNTableMetaData"]],
            ]
        ] = []
        qry = None

        if is_query:
            qry_file = self.metadata().query()
            qry = self.conn_manager.manager().query(qry_file)
            if qry is None:
                LOGGER.error(
                    "Could not load the file %s.qry for an unknown reason. This table is a view",
                    qry_file,
                )
                raise Exception(
                    "Could not load the file %s.qry for an unknown reason. This table is a view"
                    % qry_file
                )
            qry_select = [x.strip() for x in (qry.select()).split(",")]
            qry_fields: Dict[str, str] = {
                fieldname.split(".")[-1]: fieldname for fieldname in qry_select
            }

            # for table in qry.tablesList():
            #    mtd = self.conn_manager.manager().metadata(table, True)
            #    if mtd:
            #        qry_tables.append((table, mtd))

            qry_tables = [
                (table, self.conn_manager.manager().metadata(table, True))
                for table in qry.tablesList()
            ]

        for number, field in enumerate(self.metadata().fieldList()):
            # if field.visibleGrid():
            #    sql_fields.append(field.name())
            if field.isPrimaryKey():
                self.pkpos.append(number)
            if field.isCompoundKey():
                self.ckpos.append(number)

            if is_query:
                if field.name() in qry_fields:
                    self.sql_fields.append(qry_fields[field.name()])
                else:
                    found = False
                    for table_name, table_meta in qry_tables:
                        if table_meta and field.name() in table_meta.fieldNames():
                            self.sql_fields.append("%s.%s" % (table_name, field.name()))
                            found = True
                            break
                    # Omito los campos que aparentemente no existen
                    if not found and not field.name() in self.sql_fields_omited:

                        if qry is None:
                            raise Exception("The qry is empty!")

                        # NOTE: Esto podría ser por ejemplo porque no entendemos los campos computados.
                        LOGGER.error(
                            "CursorTableModel.refresh(): Omitiendo campo '%s' referenciado en query %s. El campo no existe en %s ",
                            field.name(),
                            self.metadata().name(),
                            qry.tablesList(),
                        )
                        self.sql_fields_omited.append(field.name())

            else:
                if field.type() != field.Check:
                    self.sql_fields_without_check.append(field.name())

                self.sql_fields.append(field.name())

    def insert_current_buffer(self) -> bool:
        """Insert data from current buffer."""
        try:
            obj_ = self.buffer.current_object()
            self.session.add(obj_)
            self.session.flush()
            return True
        except Exception as error:
            LOGGER.warning("insert_current_buffer : %s" % error, stack_info=True)

        return False

    # def edit_current_buffer(self):
    #    """Update data from current buffer."""

    def delete_current_buffer(self) -> bool:
        """Delete data from current buffer."""

        try:
            obj_ = self.buffer.current_object()
            self.session.delete(obj_)
            self.session.flush()
            return True
        except Exception as error:
            LOGGER.warning("delete_current_buffer : %s" % error, stack_info=True)

        return False

    def refresh(self) -> None:
        """
        Refresh information mananged by this class.
        """

        if utils_base.is_library():
            self._initialized = False

        if (
            self._initialized is None and self.parent_view
        ):  # Si es el primer refresh y estoy conectado a un FLDatatable()
            self._initialized = True
            QtCore.QTimer.singleShot(1, self.refresh)
            return

        if (
            self._initialized
        ):  # Si estoy inicializando y no me ha enviado un sender, cancelo el refesh
            if not self.sender():
                return

        self._initialized = False

        if (
            self._disable_refresh or self._parent.modeAccess() == self._parent.Del
        ) and self.rowCount():
            return

        self._grid_obj = {}
        self._parent.clear_buffer()

        where_filter = self.buildWhere()

        # """ FIN """

        parent = QtCore.QModelIndex()

        rows = self.rowCount()
        self.beginRemoveRows(parent, 0, rows)
        self.endRemoveRows()
        if rows > 0:
            cast(
                QtCore.pyqtSignal, self.rowsRemoved
            ).emit(  # type: ignore [attr-defined] # noqa: F821
                parent, 0, rows - 1
            )

        self._refresh_field_info()

        # if self.metadata().isQuery():
        #    print("FIXME!! query!!")

        # dynamic_filter_class = sql_tools.DynamicFilter(
        #    query=session_.query(self._parent._cursor_model), model_class=self._parent._cursor_model
        # )

        # dynamic_filter_class.set_filter_condition_from_string(where_filter)

        # self._data_proxy = dynamic_filter_class.return_query()
        if self.metadata().isQuery():

            meta_qry = pnsqlquery.PNSqlQuery(self.metadata().query())
            if where_filter.strip().lower().startswith("order"):
                order_by = where_filter.lower().replace("order by", "")
                if order_by:
                    meta_qry.setOrderBy(order_by)
                where_filter = "1 = 1"

            meta_qry.setWhere(where_filter.replace("WHERE ", ""))
            sql_query = meta_qry.sql()
        else:
            sql_query = "SELECT %s FROM %s %s" % (
                self.metadata().primaryKey(),
                self.metadata().name(),
                where_filter,
            )

        self._data_proxy = None
        # print("COUNT", sql_count)

        # print("QUERY", sql_query)
        result_query = self.session.execute(sql_query)
        rows_loaded = result_query.rowcount

        if rows_loaded == -1:
            sql_count = (
                "SELECT COUNT(%s) FROM " % self.metadata().primaryKey()
                + sql_query[sql_query.find(" FROM ") + 6 :]
            )

            if sql_count.find("ORDER BY") > 1:
                if sql_count.find("WHERE") == -1:
                    sql_count += " WHERE 1 = 1"
                sql_count = sql_count[: sql_count.find("ORDER BY")]

            result_count = self.session.execute(sql_count)
            rows_loaded = result_count.fetchone()[0]

        if rows_loaded > 0:

            self._data_proxy = ProxyIndex(result_query, rows_loaded)

            self.need_update = False
            self._column_hints = [120] * len(self.sql_fields)

        if self.parent_view:
            self.update_rows()

    def buildWhere(self) -> str:
        """Return valid where."""

        where_filter = " AND ".join(
            [value.strip() for key, value in sorted(self.where_filters.items()) if value]
        )

        if self._sort_order:
            if where_filter.find("ORDER BY") == -1:
                order_by = " ORDER BY %s" % self._sort_order
                if where_filter.find(";") > -1:
                    where_filter = where_filter.replace(";", "%s;" % order_by)
                else:
                    where_filter += order_by

        return (
            where_filter
            if where_filter.strip().startswith("ORDER")
            else "WHERE %s" % where_filter
            if where_filter
            else ""
        )

    def updateCacheData(self, mode: int) -> bool:
        """Update cache data without refresh."""
        # print("* updateCacheData", mode)
        # mode 1- Insert, 2 - Edit, 3 - Del

        if self._disable_refresh:
            return True

        pk_name = self._parent.primaryKey()
        pk_value = self._parent.buffer().value(pk_name)
        where_filter = self.buildWhere()

        sql_query = "SELECT %s FROM %s %s" % (
            self.metadata().primaryKey(),
            self.metadata().name(),
            where_filter,
        )
        order_by = ""
        if sql_query.find("ORDER BY") > 1:
            sql_query = sql_query[: sql_query.find("ORDER BY")]
            order_by = sql_query[sql_query.find("ORDER BY") :]

        extra_where = " %s" % (
            self.conn_manager.manager().formatAssignValue(self.metadata().field(pk_name), pk_value)
        )
        if extra_where not in sql_query:
            sql_query += " AND" if sql_query.find("WHERE") > -1 else " WHERE"
            sql_query += extra_where

        result = self.session.execute(sql_query)
        new_data = result.fetchone()

        if new_data is None and mode in [1, 2]:  # mode 3 allways returns None
            LOGGER.debug("no valid data to update cache!")
            return True

        if self._data_proxy is None:
            LOGGER.debug("data_proxy is empty!")
            return True
        elif (
            mode == 1 and new_data[0] in self._data_proxy._cached_data
        ):  # if exists dont need Insert.
            return True

        if mode == 1:  # Insert.

            if order_by:
                LOGGER.warning("FIXME! update chache whit alternative order_by")
                return False
            else:

                current_pos = None
                min_val = 0
                max_val = self._data_proxy._total_rows

                while True:
                    upper = None

                    if self.rowCount():

                        if current_pos is None:
                            current_pos = max_val // 2

                        # while current_pos > self._data_proxy._last_current_size:
                        #    if not self._data_proxy.fetch_more():
                        #        break

                        # if current_pos < self._data_proxy._last_current_size:
                        #    data = self._data_proxy[current_pos]
                        data = self._data_proxy[current_pos]

                        if self._data_proxy._last_current_size < current_pos:
                            LOGGER.warning(
                                "Error seek possition %s over %s (len %s). Total: %s"
                                % (
                                    current_pos,
                                    self._data_proxy._qry_rows_loaded,
                                    self._data_proxy._last_current_size,
                                    self._data_proxy._total_rows,
                                )
                            )
                            return False

                        if pk_value > data:
                            if current_pos in (max_val, 0):
                                upper = True
                            else:

                                min_val = current_pos
                                current_pos += (max_val - min_val) // 2
                        else:
                            if current_pos in (min_val, 0):
                                upper = False
                            else:

                                max_val = current_pos
                                current_pos -= (max_val - min_val) // 2

                        if (max_val - min_val) // 2 == 0:
                            upper = True
                    elif self._data_proxy is not None:
                        upper = False
                        current_pos = 0

                    if upper is not None:

                        if upper:
                            current_pos += 1

                        self._data_proxy.insert(
                            new_data,
                            current_pos
                            if current_pos < self._data_proxy._last_current_size
                            else -1,
                        )

                        break
            return True

        elif mode == 2:  # Edit.
            self._data_proxy.update_pk(pk_value, new_data[0])

            return True

        elif mode == 3:  # Delete.
            self._data_proxy.delete_pk(pk_value)

            return True

        LOGGER.warning("%s.model.updateCacheData(%s) returns False" % (self._parent._name, mode))
        return False

    def get_obj_from_row(self, row: int) -> Optional[Callable]:
        """Return row object from proxy."""

        if row > -1 and row < self.rowCount() and self._data_proxy:
            pk_value = self._data_proxy[row]
            session_ = self.session

            if (
                row not in self._grid_obj.keys()
                or self._grid_obj[row] is not None
                and inspect(self._grid_obj[row]).expired
            ):

                query = orm_utils.DynamicFilter(
                    query=session_.query(self._parent._cursor_model),
                    model_class=self._parent._cursor_model,
                )
                query.set_filter_condition_from_string(
                    "%s = %s"
                    % (self.metadata().primaryKey(), str(pk_value).replace(" ", "_|_space_|_"))
                )
                try:
                    self._grid_obj[row] = query.return_query().first()
                except Exception as error:
                    raise Exception("get_object_from_row %s (%s) : %s" % (row, pk_value, error))

            return self._grid_obj[row]

        return None

    def seek_row(self, row: int) -> bool:
        """Seek row selected."""

        if not hasattr(self, "_current_row_index") or row != self._current_row_index:
            if row > -1 and row < self.rowCount():
                object_ = self.get_obj_from_row(row)
                if object_ is None:
                    return False
                self._current_row_index = row
                self._current_row_data = object_

            else:
                return False

        return True

    def value(self, row: int, field_name: str) -> Any:
        """Return colum value from a row."""

        return (
            getattr(self.get_obj_from_row(row), field_name, None)
            if row > -1 and row < self.rowCount()
            else None
        )

    def find_pk_row(self, pk_value: Any) -> int:
        """Retrieve row index of a record given a primary key."""

        try:
            return self._data_proxy.index(pk_value) if self._data_proxy else -1
        except ValueError:
            return -1

    def fieldType(self, field_name: str) -> str:
        """
        Retrieve field type for a given field name.

        @param field_name. required field name.
        @return field type.
        """
        field = self.metadata().field(field_name)
        if field is None:
            raise Exception("field %s not found" % field_name)
        return field.type()

    def alias(self, field_name: str) -> str:
        """
        Retrieve alias name for a field name.

        @param field_name. field name requested.
        @return alias for the field.
        """
        field = self.metadata().field(field_name)
        if field is None:
            raise Exception("field %s not found" % field_name)
        return field.alias()

    def columnCount(self, *args: List[Any]) -> int:  # type: ignore [override] # noqa F821
        """
        Get current column count.

        @return Number of columns present.
        """
        # if args:
        #    LOGGER.warning("columnCount%r: wrong arg count", args, stack_info=True)
        return self.cols

    def updateColumnsCount(self) -> None:
        """
        Set number of columns in tableModel.
        """
        self.cols = len(self.metadata().fieldList())
        self.loadColAliases()
        if self.metadata().isQuery():
            self._refresh_field_info()

    def rowCount(self, parent: QtCore.QModelIndex = None) -> int:
        """
        Get current row count.

        @return Row number present in table.
        """
        return (
            self._data_proxy._total_rows  # type: ignore [union-attr] # noqa: F821
            if getattr(self, "_data_proxy", None)
            else 0
        )

    def headerData(
        self,
        section: int,
        orientation: "QtCore.Qt.Orientation",
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """
        Retrieve header data.

        @param section. Column
        @param orientation. Horizontal, Vertical
        @param role. QtCore.Qt.ItemDataRole.DisplayRole only. Every other option is ommitted.
        @return info for section, orientation and role.
        """
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                if not self.col_aliases:
                    self.loadColAliases()
                return self.col_aliases[section]
            elif orientation == QtCore.Qt.Orientation.Vertical:
                return section + 1
        return None

    def loadColAliases(self) -> None:
        """
        Load column alias for every column.
        """
        self.col_aliases = [
            str(self.metadata().indexFieldObject(i).alias()) for i in range(self.cols)
        ]

    def metadata(self) -> "pntablemetadata.PNTableMetaData":
        """
        Retrieve FLTableMetaData for this tableModel.

        @return Objeto FLTableMetaData
        """
        if self._metadata is None:
            raise Exception("metadata is empty!")

        return self._metadata

    @property
    def db(self) -> "iconnection.IConnection":
        """Get current connection."""

        return self._parent.db()

    @property
    def buffer(self) -> "pnbuffer.PNBuffer":
        """Get buffer."""

        return self._parent.buffer()

    @property
    def driver_sql(self) -> "isqldriver.ISqlDriver":
        """Return driver sql."""

        return self.db.driver()

    @property
    def session(self) -> "orm.Session":
        """Return pnsqlcursor session."""

        return self.db.session()

    @property
    def conn_manager(self) -> "pnconnectionmanager.PNConnectionManager":
        """Return connection manager."""

        return self.db.connManager()

    def set_parent_view(self, parent_view: "fldatatable.FLDataTable") -> None:
        """Set the parent view."""
        self.parent_view = parent_view


class ProxyIndex:
    """ProxyIndex class."""

    _query = None
    _cached_data: List[Any] = []
    _index: int
    _total_rows: int
    _qry_rows_total: int
    _qry_rows_loaded: int
    _last_current_size: int

    def __init__(self, result_query: Any, rows: int) -> None:
        """Initialize."""

        self._query = result_query
        self._qry_rows_total = self._total_rows = int(rows)

        self._qry_rows_loaded = 0
        self._last_current_size = 0
        self._cached_data = []

        self.fetch_more(2000 if rows > 2000 else rows)

    def __getitem__(self, index: int) -> Any:
        """Return item value."""

        if self._last_current_size <= index:
            self.fetch_more(index - self._last_current_size + 1)

        return self._cached_data[index] if self._last_current_size > index else None

    def index(self, value: Any) -> int:
        """Return data position."""

        while value not in self._cached_data:
            if not self.fetch_more():
                return -1

        return self._cached_data.index(value)

    def fetch_more(self, fetch_size: int = 2000) -> bool:
        """Fetch more data to cached data."""

        if self._qry_rows_loaded < self._qry_rows_total and self._query:
            to_fetch = self._qry_rows_loaded + fetch_size
            fetch_size = (
                (self._qry_rows_total - self._qry_rows_loaded)
                if to_fetch > 0 and to_fetch >= self._qry_rows_total
                else fetch_size
            )

            try:
                self._cached_data += [data[0] for data in self._query.fetchmany(fetch_size)]
                self._qry_rows_loaded += fetch_size
                self._last_current_size += fetch_size
                return True
            except exc.InterfaceError:
                LOGGER.warning(
                    "Se ha producido un problema al recoger %s primary keys del caché. cacheadas: %s, totales: %s",
                    fetch_size,
                    self._qry_rows_loaded,
                    self._qry_rows_total,
                )

        return False

    def insert(self, value: Any, position: int = -1) -> bool:
        """Insert a value to cache."""

        if position == -1:
            self._cached_data.append(value)
        else:
            self._cached_data.insert(position, value)

        self._last_current_size += 1
        self._total_rows += 1

        return True

    def update_pk(self, pk_value: Any, value: Any) -> bool:
        """Update a cached value."""

        self._cached_data[self.index(pk_value)] = value

        return True

    def delete_pk(self, pk_value: Any) -> bool:
        """Delete a cached value."""

        index = self.index(pk_value)
        if index > -1:
            del self._cached_data[index]
            self._total_rows -= 1
            self._last_current_size -= 1

            return True

        return False
