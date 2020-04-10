# -*- coding: utf-8 -*-
"""
Defines PNCursorTableModel class.
"""


from PyQt5 import QtCore, QtGui, Qt, QtWidgets

from pineboolib.core.utils import logging, utils_base


from pineboolib.application.utils import date_conversion, xpm
from pineboolib.application import qsadictmodules

import itertools
import locale
import os
import datetime


from typing import Any, Iterable, Optional, List, Dict, Tuple, cast, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.application.metadata import pnfieldmetadata  # noqa: F401
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401
    from pineboolib.interfaces import iconnection, isqlcursor
    from pineboolib.fllegacy import fldatatable
    from pineboolib.plugins.sql import pnsqlschema

DEBUG = False
CURSOR_COUNT = itertools.count()
LOGGER = logging.get_logger("CursorTableModel")


class PNCursorTableModel(QtCore.QAbstractTableModel):
    """
    Link between FLSqlCursor and database.
    """

    rows: int
    cols: int
    _use_timer = True
    _rows_loaded: int
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
    _curname: str
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
    _current_row_data: List
    _current_row_index: int
    _tablename: str
    _order: str
    grid_row_tmp: Dict[int, List[Any]]

    def __init__(self, conn: "iconnection.IConnection", parent: "isqlcursor.ISqlCursor") -> None:
        """
        Constructor.

        @param conn. PNConnection Object
        @param parent. related FLSqlCursor
        """

        super(PNCursorTableModel, self).__init__()
        self._parent = parent
        self.parent_view = None

        metadata = self._parent.private_cursor.metadata_

        self._rows_loaded = 0
        self.rows = 0
        self.cols = 0
        self._metadata = None

        if not metadata:
            return

        self._metadata = metadata

        self._driver_sql = self.db().driver()
        # self._use_timer = self.driver_sql().useTimer()

        # if not self._use_timer:
        #    self._use_timer = True
        #    LOGGER.warning("SQL Driver supports neither Timer, defaulting to Timer")
        # self._use_timer = True

        self._rows_loaded = 0
        self.rows = 0
        self.cols = 0

        self.sql_fields = []
        self.sql_fields_omited = []
        self.sql_fields_without_check = []
        # self.field_aliases = []
        # self.field_type = []
        # self.field_metaData = []
        self.col_aliases: List[str] = []
        self._current_row_data = []
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

        # self._rows_loaded = 0
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
        self._curname = ""

        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.updateRows)
        # self.timer.start(1000)

        # self._can_fetch_more_rows = True
        self._disable_refresh = False
        self._initialized = None
        self.grid_row_tmp = {}

        # self.refresh()

        if self.metadata().isQuery():
            query = self.db().connManager().manager().query(self.metadata().query())
            if query is None:
                raise Exception("query is empty!")
            self._tablename = query.from_()
        else:
            self._tablename = self.metadata().name()

    def disable_refresh(self, disable: bool) -> None:
        """
        Disable refresh.

        e.g. FLSqlQuery.setForwardOnly(True).
        @param disable. True or False
        """
        self._disable_refresh = disable

    def sort(self, column: int, order: QtCore.Qt.SortOrder = QtCore.Qt.AscendingOrder) -> None:
        """
        Change order by used ASC/DESC and column.

        @param col. Column to sort by
        @param order. 0 ASC, 1 DESC
        """
        col = column
        # order 0 ascendente , 1 descendente
        ord = "ASC"
        if order == 1:
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
        self._sort_order = ""
        # if isinstance(sort_order, list):
        #    self._sort_order = ",".join(sort_order)

        # else:
        self._sort_order = sort_order

    # def setColorFunction(self, f):
    #    self.color_function_ = f

    # def dict_color_function(self):
    #    return self.color_function_

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
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
        if _type != "check":

            # r = [x for x in self._data[row]]
            # self._data[row] = r
            # d = r[col]
            # self.seekRow(row)
            # d = self._current_row_data[col]
            # d = self._data[row][col]
            result: Any = None
            if row not in self.grid_row_tmp.keys():
                self.grid_row_tmp = {}
                self.grid_row_tmp[row] = self.driver_sql().row_get(row, self._curname)
                if not self.grid_row_tmp[row]:  # refresh grid if cursor is deleted.
                    self.refresh()
                    return

            tuple = self.grid_row_tmp[row]
            if tuple:
                result = tuple[col]

        else:
            primary_key = str(self.value(row, self.metadata().primaryKey()))
            if primary_key not in self._check_column.keys():
                result = QtWidgets.QCheckBox()
                self._check_column[primary_key] = result

        if self.parent_view and role in [QtCore.Qt.BackgroundRole, QtCore.Qt.ForegroundRole]:
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

        if role == QtCore.Qt.CheckStateRole and _type == "check":
            if primary_key in self._check_column.keys():
                if self._check_column[primary_key].isChecked():
                    return QtCore.Qt.Checked

            return QtCore.Qt.Unchecked

        elif role == QtCore.Qt.TextAlignmentRole:
            result = QtCore.Qt.AlignVCenter
            if _type in ("int", "double", "uint"):
                result = result | QtCore.Qt.AlignRight
            elif _type in ("bool", "date", "time"):
                result = result | QtCore.Qt.AlignCenter
            elif _type in ("unlock", "pixmap"):
                result = result | QtCore.Qt.AlignHCenter

            return result

        elif role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
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

            elif _type in ("string", "stringlist", "timestamp"):
                if not result:
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

        elif role == QtCore.Qt.DecorationRole:
            pixmap = None
            if _type in ("unlock", "pixmap") and self.parent_view:
                row_height = self.parent_view.rowHeight(row)  # Altura row
                row_width = self.parent_view.columnWidth(col)

                if _type == "unlock":
                    if result in (True, "1"):
                        pixmap = QtGui.QPixmap(
                            utils_base.filedir("./core/images/icons", "unlock.png")
                        )
                    else:
                        pixmap = QtGui.QPixmap(
                            utils_base.filedir("./core/images/icons", "lock.png")
                        )
                else:
                    if not self._parent.private_cursor._is_system_table:
                        data = self.db().connManager().manager().fetchLargeValue(result)
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
                        new_pixmap.fill(QtCore.Qt.transparent)
                        painter = Qt.QPainter(new_pixmap)
                        painter.drawPixmap(
                            center_width, center_height, pixmap.width(), pixmap.height(), pixmap
                        )

                        pixmap = new_pixmap

            return pixmap

        elif role == QtCore.Qt.BackgroundRole:
            if _type == "bool":
                if result in (True, "1"):
                    result = QtGui.QBrush(QtCore.Qt.green)
                else:
                    result = QtGui.QBrush(QtCore.Qt.red)

            elif _type == "check":
                obj_ = self._check_column[primary_key]
                result = (
                    QtGui.QBrush(QtCore.Qt.green)
                    if obj_.isChecked()
                    else QtGui.QBrush(QtCore.Qt.white)
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

        elif role == QtCore.Qt.ForegroundRole:
            if _type == "bool":
                if result in (True, "1"):
                    result = QtGui.QBrush(QtCore.Qt.black)
                else:
                    result = QtGui.QBrush(QtCore.Qt.white)
            else:
                if res_color_function and len(res_color_function) and res_color_function[1] != "":
                    color_ = QtGui.QColor(res_color_function[1])
                    style_ = getattr(QtCore.Qt, res_color_function[2], None)
                    result = QtGui.QBrush(color_)
                    result.setStyle(style_)
                else:
                    result = None

            return result

        # else:
        #    print("role desconocido", role)

        return None

    def updateRows(self) -> None:
        """
        Update virtual records managed by its model.
        """
        parent = QtCore.QModelIndex()
        torow = self.rows - 1
        self._rows_loaded = torow + 1
        self.beginInsertRows(parent, 0, torow)
        self.endInsertRows()
        top_left = self.index(0, 0)
        bottom_right = self.index(torow, self.cols - 1)
        self.dataChanged.emit(top_left, bottom_right)
        self.indexes_valid = True

    def _refresh_field_info(self) -> None:
        """
        Check if query fields do exist.

        If any field does not exist it gets marked as ommitted.
        """
        is_query = self.metadata().isQuery()
        qry_file = self.metadata().query()
        qry_tables = []
        qry = None
        # if qry is None:
        #    return
        if is_query:
            qry = self.db().connManager().manager().query(qry_file)
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

            for table in qry.tablesList():
                mtd = self.db().connManager().manager().metadata(table, True)
                if mtd:
                    qry_tables.append((table, mtd))

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
                    for table, mtd in qry_tables:
                        if field.name() in mtd.fieldNames():
                            self.sql_fields.append("%s.%s" % (table, field.name()))
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

    def refresh(self) -> None:
        """
        Refresh information mananged by this class.
        """
        print("REFESCANDO", self._tablename)
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

        # if self._disable_refresh and self.rows > 0:
        #    return

        if not self.metadata():
            LOGGER.warning("ERROR: CursorTableModel :: No hay tabla %s", self.metadata().name())
            return

        """ FILTRO WHERE """
        where_filter = ""
        for k, wfilter in sorted(self.where_filters.items()):
            # if wfilter is None:
            #     continue
            wfilter = wfilter.strip()

            if not wfilter:
                continue
            if not where_filter:
                where_filter = wfilter
            elif wfilter not in where_filter:
                if where_filter not in wfilter:
                    where_filter += " AND " + wfilter
        if not where_filter:
            where_filter = "1 = 1"

        self.where_filter = where_filter
        self._order = self.getSortOrder()
        # Si no existe un orderBy y se ha definido uno desde FLTableDB ...
        if self.where_filter.find("ORDER BY") == -1 and self.getSortOrder():
            if self.where_filter.find(";") > -1:  # Si el where termina en ; ...
                self.where_filter = self.where_filter.replace(";", " ORDER BY %s;" % self._order)
            else:
                self.where_filter = "%s ORDER BY %s" % (self.where_filter, self._order)
        """ FIN """

        parent = QtCore.QModelIndex()

        self.beginRemoveRows(parent, 0, self.rows)
        self.endRemoveRows()
        if self.rows > 0:
            cast(QtCore.pyqtSignal, self.rowsRemoved).emit(parent, 0, self.rows - 1)

        self.rows = 0
        self._rows_loaded = 0
        self._fetched_rows = 0
        self.sql_fields = []
        self.sql_fields_without_check = []

        self._refresh_field_info()

        if self.sql_fields_without_check:
            self.sql_str = ", ".join(self.sql_fields_without_check)
        else:
            self.sql_str = ", ".join(self.sql_fields)

        self._current_row_data = []
        self._current_row_index = -1

        if self._curname:
            self.driver_sql().delete_declared_cursor(self._curname)

        self._curname = "cur_%s_%08d" % (self.metadata().name(), next(CURSOR_COUNT))

        self.driver_sql().declare_cursor(
            self._curname, self.sql_str, self._tablename, self.where_filter
        )

        self.rows = self.size()
        if not self.rows:  # Si no hay tamaño, no declara/crea el cursor/consulta
            return

        self.grid_row_tmp = {}

        self.need_update = False
        self._column_hints = [120] * len(self.sql_fields)
        self.updateRows()

    def value(self, row: Optional[int], field_name: str) -> Any:
        """
        Retrieve column value for a row.

        @param row. Row number to retrieve
        @param field_name. Field name.
        @return Value
        """
        if row is None or row < 0:
            return None
        col = None
        if not self.metadata().isQuery():
            col = self.metadata().indexPos(field_name)
        else:
            # Comparo con los campos de la qry, por si hay algun hueco que no se detectaria con indexPos
            for number, field in enumerate(self.sql_fields):
                if field_name == field[field.find(".") + 1 :]:
                    col = number
                    break

            if not col:
                return None

        mtdfield = self.metadata().field(field_name)
        if mtdfield is None:
            raise Exception("field_name: %s not found" % field_name)
        type_ = mtdfield.type()

        if type_ == "check":
            return None

        if self._current_row_index != row:
            if not self.seekRow(row):
                return None

        campo: Any = None
        if self._current_row_data:
            campo = self._current_row_data[col]

        if type_ in ("serial", "uint", "int"):
            if campo not in (None, "None"):
                campo = int(campo)
            elif campo == "None":
                LOGGER.warning("Campo no deberia ser un string 'None'")

        return campo

    def seekRow(self, row: int) -> bool:
        """Seek to a row possition."""
        if not self.rows:
            return False

        if row != self._current_row_index:
            result = self.driver_sql().row_get(row, self._curname)
            if not result:
                return False

            self._current_row_index = row
            self._current_row_data = list(result)
        return True

    def setValuesDict(self, row: int, update_dict: Dict[str, Any]) -> None:
        """
        Set value to a row using a Dict.

        @param row. Row to update
        @param update_dict. Key-Value where key is the fieldname and value is the value to update
        """

        if DEBUG:
            LOGGER.info("CursorTableModel.setValuesDict(row %s) = %r", row, update_dict)

        try:
            self.seekRow(row)
            self._current_row_data = list(self._current_row_data)

            colsnotfound = []
            for fieldname, value in update_dict.items():
                # col = self.metadata().indexPos(fieldname)
                try:
                    col = self.sql_fields.index(fieldname)
                    # self._data[row][col] = value
                    self._current_row_data[col] = value
                    # r[col] = value
                except ValueError:
                    colsnotfound.append(fieldname)
            if colsnotfound:
                LOGGER.warning(
                    "CursorTableModel.setValuesDict:: columns not found: %r", colsnotfound
                )
            # self.indexUpdateRow(row)

        except Exception:
            LOGGER.exception(
                "CursorTableModel.setValuesDict(row %s) = %r :: ERROR:", row, update_dict
            )

        self._current_row_index = -1

    def setValue(self, row: int, fieldname: str, value: Any) -> None:
        """
        Set value to a cell.

        @param row. related row
        @param fieldname. name of the field to update.
        @param value. Value to write. Text, Pixmap, etc.
        """
        # Reimplementación para que todo pase por el método genérico.
        self.setValuesDict(row, {fieldname: value})

    def insert(self, pn_cursor: "isqlcursor.ISqlCursor") -> bool:
        """
        Create new row in TableModel.

        @param buffer . PNBuffer to be added.
        """

        data: Dict[str, Any] = {}
        buffer = pn_cursor.buffer()
        if buffer is None:
            raise Exception("Cursor has no buffer")

        for buffer_field in buffer.fieldsList():
            value: Any = None
            if buffer.value(buffer_field.name) is None:
                mtdfield = pn_cursor.metadata().field(buffer_field.name)
                if mtdfield is None:
                    raise Exception("field %s not found" % buffer_field.name)
                value = mtdfield.defaultValue()
            else:
                value = buffer.value(buffer_field.name)

            if value is not None:  # si el campo se rellena o hay valor default
                if buffer_field.type_ in ("string", "stringlist") and isinstance(value, str):
                    value = self.db().normalizeValue(value)

                data[buffer_field.name] = value

        if data:
            try:
                model = qsadictmodules.QSADictModules.from_project(
                    "%s_orm" % pn_cursor.action().name()
                )

                if self.db().driver().insert_model(model, data):
                    self.need_update = True

            except Exception as error:
                LOGGER("INSERT : %s", str(error))
                return False

        return True

    def update(self, pk_value: Any, dict_update: Dict[str, Any]) -> bool:
        """
        Update record data from tableModel into DB.

        @param pk_value. Pirmary Key of the record to be updated
        @param dict_update. Fields to be updated
        """
        row = self.findPKRow([pk_value])
        if row is None:
            return False

        if self.value(row, self.pK()) != pk_value:
            raise AssertionError(
                "Los indices del CursorTableModel devolvieron un registro erroneo: %r != %r"
                % (self.value(row, self.pK()), pk_value)
            )

        model = qsadictmodules.QSADictModules.from_project("%s_orm" % self.metadata().name())
        if not self.driver_sql().update_model(model, dict_update, pk_value):
            return False

        self.setValuesDict(row, dict_update)

        self.need_update = True
        return True

    def delete(self, cursor: "isqlcursor.ISqlCursor") -> bool:
        """
        Delete a row from tableModel.

        @param cursor . FLSqlCursor object
        """
        pk_value = cursor.valueBuffer(self.pK())

        model = qsadictmodules.QSADictModules.from_project("%s_orm" % self.metadata().name())
        result_ = self.driver_sql().delete_model(model, pk_value)
        if result_:
            self.need_update = True
        return result_

    def findPKRow(self, pklist: Iterable[Any]) -> Optional[int]:
        """
        Retrieve row index of a record given a primary key.

        @param pklist. Primary Key list to find. Use a List [] even for a single record.
        @return row index.
        """
        if not isinstance(pklist, (tuple, list)):
            raise ValueError(
                "findPKRow expects a list as first argument. Enclose PK inside brackets [self.pkvalue]"
            )

        pklist = tuple(pklist)
        if not pklist or pklist[0] is None:
            raise ValueError("Primary Key can't be null")

        ret = None
        if self.pK():
            ret = self.driver_sql().row_find(
                self._curname, self.sql_fields.index(self.pK()), pklist[0]
            )

        return ret

    def pK(self) -> str:
        """
        Get field name of the primary key.

        @return field name
        """
        return self.metadata().primaryKey()

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
        return self._rows_loaded

    def size(self) -> int:
        """
        Get amount of data selected on the cursor.

        @return number of retrieved rows.
        """
        size = 0
        mtd = self.metadata()
        if mtd and self.db().isOpen():
            where_ = self.where_filter
            # from_ = self.metadata().name()

            # if mtd.isQuery():
            #    qry = self.db().connManager().manager().query(self.metadata().query())
            #    if qry is None:
            #        raise Exception("Query not found")
            #    from_ = qry.from_()

            if self.where_filter.find("ORDER BY") > -1:
                where_ = self.where_filter[: self.where_filter.find("ORDER BY")]

            where_ = self.driver_sql().fix_query(where_)
            # q = pnsqlquery.PNSqlQuery(None, self.db())
            sql = "SELECT COUNT(%s) FROM %s WHERE %s" % (self.pK(), self._tablename, where_)
            cursor = self.driver_sql().execute_query(sql)
            result = cursor.fetchone() if cursor else None
            if result is not None:
                size = result[0]
            # q.exec_(sql)
            # if q.first():
            #    size = q.value(0)
        return size

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole
    ) -> Any:
        """
        Retrieve header data.

        @param section. Column
        @param orientation. Horizontal, Vertical
        @param role. QtCore.Qt.DisplayRole only. Every other option is ommitted.
        @return info for section, orientation and role.
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if not self.col_aliases:
                    self.loadColAliases()
                return self.col_aliases[section]
            elif orientation == QtCore.Qt.Vertical:
                return section + 1
        return None

    def loadColAliases(self) -> None:
        """
        Load column alias for every column.
        """
        self.col_aliases = [
            str(self.metadata().indexFieldObject(i).alias()) for i in range(self.cols)
        ]

    def field_metadata(self, field_name: str) -> "pnfieldmetadata.PNFieldMetaData":
        """
        Retrieve FLFieldMetadata for given field name.

        @param field_name. field name.
        @return FLFieldMetadata
        """
        field = self.metadata().field(field_name)
        if field is None:
            raise Exception("field_name %s not found" % field_name)
        return field

    def metadata(self) -> "pntablemetadata.PNTableMetaData":
        """
        Retrieve FLTableMetaData for this tableModel.

        @return Objeto FLTableMetaData
        """
        if self._metadata is None:
            raise Exception("metadata is empty!")

        return self._metadata

    def db(self) -> "iconnection.IConnection":
        """Get current connection."""

        return self._parent.db()

    def driver_sql(self) -> "pnsqlschema.PNSqlSchema":
        """Return driver sql."""

        return self._parent.db().driver()

    def set_parent_view(self, parent_view: "fldatatable.FLDataTable") -> None:
        """Set the parent view."""
        self.parent_view = parent_view
