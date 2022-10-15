"""Fldatatable module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets, QtGui  # type: ignore[import]

from pineboolib.core import decorators, settings
from pineboolib.core.utils import utils_base

from pineboolib import logging

from typing import Any, Optional, List, Dict, Tuple, cast, TYPE_CHECKING

from pineboolib.application.database import pnsqlcursor, pncursortablemodel


if TYPE_CHECKING:
    from pineboolib.application.metadata import pnfieldmetadata  # pragma: no cover
    from pineboolib.application.metadata import pntablemetadata  # pragma: no cover
    from pineboolib.interfaces import isqlcursor  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class FLDataTable(QtWidgets.QTableView):
    """
    Class that is a redefinition of the QDataTable class.

    Specifies for the needs of AbanQ.
    """

    _parent: Optional[Any]
    filter_: str
    sort_: str
    fltable_iface: Any

    """
    Numero de la fila (registro) seleccionada actualmente
    """
    row_selected: int

    """
    Numero de la columna (campo) seleccionada actualmente
    """
    col_selected: int

    """
    Cursor, con los registros
    """
    cursor_: Optional["isqlcursor.ISqlCursor"]

    """
    Almacena la tabla está en modo sólo lectura
    """
    readonly_: bool

    """
    Almacena la tabla está en modo sólo edición
    """
    editonly_: bool

    """
    Indica si la tabla está en modo sólo inserción
    """
    insertonly_: bool

    """
    Texto del último campo dibujado en la tabla
    """
    lastTextPainted_: Optional[str]

    """
    Pixmap precargados
    """
    pix_ok_: str
    pix_no_: str

    """
    Lista con las claves primarias de los registros seleccionados por chequeo
    """
    pk_checked: List[object]

    """
    Filtro persistente para el cursor
    """
    persistent_filter_: str

    """
    Indicador para evitar refrescos anidados
    """
    refreshing_: bool

    """
    Indica si el componente es emergente ( su padre es un widget del tipo Popup )
    """
    popup_: bool

    """
    Indica el ancho de las columnas establecidas explícitamente con FLDataTable::setColumnWidth
    """
    width_cols_: Dict[str, int]

    """
    Indica si se deben mostrar los campos tipo pixmap en todas las filas
    """
    show_all_pixmaps_: bool

    """
    Nombre de la función de script a invocar para obtener el color de las filas y celdas
    """
    function_get_color: Optional[str]

    """
    Indica que no se realicen operaciones con la base de datos (abrir formularios). Modo "sólo tabla".
    """
    only_table_: bool
    changing_num_rows_: bool
    _paint_field_name: Optional[str]
    paint_field_mtd_: Optional["pnfieldmetadata.PNFieldMetaData"]

    def __init__(
        self, parent: Optional[Any] = None, name: str = "FLDataTable", popup: bool = False
    ):
        """Inicialize."""

        super().__init__(parent)

        if parent:
            self._parent = parent

        self.setObjectName(name)

        self.readonly_ = False
        self.editonly_ = False
        self.insertonly_ = False
        # self.refreshing_ = False
        self.filter_ = ""
        self.sort_ = ""
        self.row_selected = -1
        self.col_selected = -1
        self.pk_checked = []
        self.persistent_filter_ = ""
        self.width_cols_ = {}

        self.pix_ok_ = utils_base.filedir("./core/images/icons", "unlock.png")
        self.pix_no_ = utils_base.filedir("./core/images/icons", "lock.png")
        self.paint_field_mtd_ = None
        self.refreshing_ = False
        self.popup_ = False
        self.show_all_pixmaps_ = False
        self.only_table_ = False
        self.function_get_color = None
        self.changing_num_rows_ = False
        self.cursor_ = None

        self._v_header = self.verticalHeader()
        self._v_header.setDefaultSectionSize(22)
        self._h_header = self.horizontalHeader()
        self._h_header.setDefaultSectionSize(120)
        self._h_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.fltable_iface = None
        self.popup_ = popup

    # def __del__(self) -> None:
    #    """Destroyer."""

    # if self.timerViewRepaint_:
    #    self.timerViewRepaint_.stop()

    #    if self.cursor_:
    #        self.cursor_.restoreEditionFlag(self.objectName())
    #        self.cursor_.restoreBrowseFlag(self.objectName())

    def header(self) -> Any:
        """Return the FLDatatable header."""

        return self._h_header

    def model(self) -> pncursortablemodel.PNCursorTableModel:
        """Return cursor table model."""
        return cast(pncursortablemodel.PNCursorTableModel, super().model())

    def setFLSqlCursor(self, cursor: "isqlcursor.ISqlCursor") -> None:
        """Set the cursor."""

        if cursor and cursor.metadata():
            cur_chg = False
            if self.cursor_ and not self.cursor_ == cursor:
                self.cursor_.restoreEditionFlag(self.objectName())
                self.cursor_.restoreBrowseFlag(self.objectName())
                cast(
                    QtCore.pyqtSignal, self.cursor_.commited
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.refresh
                )

                cur_chg = True

            if not self.cursor_ or cur_chg:
                self.cursor_ = cursor
                if not self.cursor_:
                    raise Exception("cursor_ is empty!")

                self.setFLReadOnly(self.readonly_)
                self.setEditOnly(self.editonly_)
                self.setInsertOnly(self.insertonly_)
                self.setOnlyTable(self.only_table_)

                cast(
                    QtCore.pyqtSignal, self.cursor_.commited
                ).connect(  # type: ignore [attr-defined] # noqa: F821
                    self.refresh
                )

                self.setModel(self.cursor_.model())
                selection_model = self.cursor_.selection()
                if selection_model is not None:
                    self.setSelectionModel(selection_model)
                else:
                    LOGGER.warning("Invalid selection model in %s" % self.cursor_.curName())
                # self.model().sort(self.header().logicalIndex(0), 0)
                self.installEventFilter(self)
                self.model().set_parent_view(self)

    def setPersistentFilter(self, p_filter: Optional[str] = None) -> None:
        """Set the persistent filter for this control."""

        if p_filter is None:
            raise Exception("Invalid use of setPersistentFilter with None")
        self.persistent_filter_ = p_filter

    def setFilter(self, filter: str) -> None:
        """Set the filter for this control."""
        self.filter_ = filter

    def numCols(self) -> int:
        """
        Return the number of columns.
        """

        return self.horizontalHeader().count()

    def setSort(self, sort: str) -> None:
        """Return the ascending / descending order of the first columns."""

        self.sort_ = sort

    # def cursor(self) -> Optional["isqlcursor.ISqlCursor"]:
    #    """
    #    Devuelve el cursor
    #    """
    #    return self.cursor_

    @property
    def cur(self) -> "isqlcursor.ISqlCursor":
        """
        Return the cursor used by the control.
        """

        if self.cursor_ is None:
            raise Exception("Cursor not set yet")
        if self.cursor_.aqWasDeleted():
            raise Exception("Cursor was deleted")
        return self.cursor_

    def setFLReadOnly(self, mode: bool) -> None:
        """
        Set the table to read only or not.
        """

        if not self.cursor_ or self.cursor_.aqWasDeleted():
            return

        self.cursor_.setEdition(not mode, self.objectName())
        self.readonly_ = mode

    def flReadOnly(self) -> bool:
        """
        Return if the table is in read-only mode.
        """

        return self.readonly_

    def setEditOnly(self, mode: bool) -> None:
        """
        Set the table to edit only or not.
        """

        if not self.cursor_ or self.cursor_.aqWasDeleted():
            return

        self.editonly_ = mode

    def editOnly(self) -> bool:
        """
        Return if the table is in edit-only mode.
        """

        return self.editonly_

    def setInsertOnly(self, mode: bool) -> None:
        """
        Set the table to insert only or not.
        """

        if not self.cursor_ or self.cursor_.aqWasDeleted():
            return

        self.cursor_.setEdition(not mode, self.objectName())
        self.insertonly_ = mode

    def insertOnly(self) -> bool:
        """
        Return if the table is in insert-only mode.
        """
        return self.insertonly_

    def primarysKeysChecked(self) -> list:
        """
        Get the list with the primary keys of the records selected by check.
        """

        return self.pk_checked

    def clearChecked(self) -> None:
        """
        Clear the list with the primary keys of the records selected by check.
        """
        self.pk_checked.clear()
        model = self.cur.model()
        for idx in model._check_column.keys():
            model._check_column[idx].setChecked(False)

    def setPrimaryKeyChecked(self, pk_value: str, on_: bool) -> None:
        """
        Set the status selected by check for a record, indicating the value of its primary key.
        """

        model = self.cur.model()
        if on_:
            if pk_value not in self.pk_checked:
                self.pk_checked.append(pk_value)
                self.primaryKeyToggled.emit(pk_value, False)
        else:
            if pk_value in self.pk_checked:
                self.pk_checked.remove(pk_value)
                self.primaryKeyToggled.emit(pk_value, False)

        if pk_value not in model._check_column.keys():
            model._check_column[pk_value] = QtWidgets.QCheckBox()

        model._check_column[pk_value].setChecked(on_)

    def setShowAllPixmaps(self, value: bool) -> None:
        """
        Set if the pixmaps of unselected lines are displayed.
        """

        self.show_all_pixmaps_ = value

    def showAllPixmap(self) -> bool:
        """
        Return if pixmaps of unselected lines are displayed.
        """

        return self.show_all_pixmaps_

    def setFunctionGetColor(self, func_name: Optional[str], iface: Optional[Any] = None) -> None:
        """
        Set the function to use to calculate the color of the cell.
        """

        self.fltable_iface = iface
        self.function_get_color = func_name

    def functionGetColor(self) -> Tuple[Optional[str], Any]:
        """
        Return the function to use to calculate the color of the cell.
        """

        return (self.function_get_color, self.fltable_iface)

    def setOnlyTable(self, on_: bool = True) -> None:
        """
        Set if the control is only Table mode.
        """
        if not self.cursor_ or self.cursor_.aqWasDeleted():
            return

        self.cursor_.setEdition(not on_, self.objectName())
        self.cursor_.setBrowse(not on_, self.objectName())
        self.only_table_ = on_

    def onlyTable(self) -> bool:
        """
        Return if the control is only Table mode.
        """

        return self.only_table_

    def indexOf(self, idx: int) -> int:
        """
        Return the visual index of a position.
        """

        return self.header().visualIndex(idx)

    def fieldName(self, col: int) -> str:
        """
        Return the name of the field according to a position.
        """

        field = self.cur.metadata().indexFieldObject(self.indexOf(col))
        if field is None:
            raise Exception("Field not found")
        return field.name()

    def eventFilter(self, obj: Any, event: QtCore.QEvent) -> bool:
        """
        Event Filtering.
        """

        row = self.currentRow()
        col = self.currentColumn()
        num_rows = self.numRows()
        num_cols = self.numCols()
        if event.type() == QtCore.QEvent.Type.KeyPress:
            key_event = cast(QtGui.QKeyEvent, event)

            if (
                key_event.key() == cast(int, QtCore.Qt.Key.Key_Escape)
                and self.popup_
                and self.parentWidget()
            ):
                self.parentWidget().hide()
                return True

            if key_event.key() == cast(int, QtCore.Qt.Key.Key_Insert):
                return True

            if key_event.key() == cast(int, QtCore.Qt.Key.Key_F2):
                return True

            if key_event.key() == cast(int, QtCore.Qt.Key.Key_Up) and row == 0:
                return True

            if key_event.key() == cast(int, QtCore.Qt.Key.Key_Left) and col == 0:
                return True

            if key_event.key() == cast(int, QtCore.Qt.Key.Key_Down) and row == num_rows - 1:
                return True

            if key_event.key() == cast(int, QtCore.Qt.Key.Key_Right) and col == num_cols - 1:
                return True

            if (
                key_event.key()
                in (cast(int, QtCore.Qt.Key.Key_Enter), cast(int, QtCore.Qt.Key.Key_Return))
                and row > -1
            ):
                self.recordChoosed.emit()
                return True

            if key_event.key() == cast(int, QtCore.Qt.Key.Key_Space):
                self.setChecked(self.model().index(row, col))

            if not settings.CONFIG.value("ebcomportamiento/FLTableShortCut", False):
                if key_event.key() == cast(int, QtCore.Qt.Key.Key_A) and not self.popup_:
                    if (
                        self.cursor_
                        and not self.readonly_
                        and not self.editonly_
                        and not self.only_table_
                    ):

                        self.cursor_.insertRecord()
                        return True
                    else:
                        return False

                if key_event.key() == cast(int, QtCore.Qt.Key.Key_C) and not self.popup_:
                    if (
                        self.cursor_
                        and not self.readonly_
                        and not self.editonly_
                        and not self.only_table_
                    ):
                        self.cursor_.copyRecord()
                        return True
                    else:
                        return False

                if key_event.key() == cast(int, QtCore.Qt.Key.Key_M) and not self.popup_:
                    if self.cursor_ and not self.readonly_ and not self.only_table_:
                        self.cursor_.editRecord()
                        return True
                    else:
                        return False

                if key_event.key() == cast(int, QtCore.Qt.Key.Key_Delete) and not self.popup_:
                    if (
                        self.cursor_
                        and not self.readonly_
                        and not self.editonly_
                        and not self.only_table_
                    ):
                        self.cursor_.deleteRecord()
                        return True
                    else:
                        return False

                if key_event.key() == cast(int, QtCore.Qt.Key.Key_V) and not self.popup_:
                    if self.cursor_ and not self.only_table_:
                        self.cursor_.browseRecord()
                        return True

            return False

        return super().eventFilter(obj, event)

    def contextMenuEvent(self, event: Any) -> None:
        """
        To prevent the context menu from appearing with the options to edit records.
        """

        super().contextMenuEvent(event)

        if not self.cursor_ or not self.cursor_.isValid() or not self.cursor_.metadata():
            return

        mtd = self.cursor_.metadata()
        pri_key = mtd.primaryKey()

        field = mtd.field(pri_key)
        if field is None:
            return

        rel_list = field.relationList()
        if not rel_list:
            return

        conn_db = self.cursor_.db()
        pri_key_val = self.cursor_.valueBuffer(pri_key)

        from pineboolib.q3widgets.qmenu import QMenu
        from pineboolib.q3widgets.qwidget import QWidget
        from pineboolib.q3widgets.qvboxlayout import QVBoxLayout

        from .fldatatable import FLDataTable

        popup = QMenu(self)

        menu_frame = QWidget(self, QtCore.Qt.WindowType.Popup)

        lay = QVBoxLayout()
        menu_frame.setLayout(lay)

        tmp_pos = event.globalPos()

        for rel in rel_list:
            cur = pnsqlcursor.PNSqlCursor(
                rel.foreignTable(), True, conn_db.connectionName(), None, None, popup
            )

            if cur.private_cursor.metadata_:
                mtd = cur.metadata()
                field = mtd.field(rel.foreignField())
                if field is None:
                    continue

                sub_popup = QMenu(self)
                sub_popup.setTitle(mtd.alias())
                sub_popup_frame = QWidget(sub_popup, QtCore.Qt.WindowType.Popup)
                lay_popup = QVBoxLayout(sub_popup)
                sub_popup_frame.setLayout(lay_popup)

                data_table = FLDataTable(None, "FLDataTable", True)
                lay_popup.addWidget(data_table)

                data_table.setFLSqlCursor(cur)
                filter = (
                    conn_db.connManager().manager().formatAssignValue(field, pri_key_val, False)
                )
                cur.setFilter(filter)
                data_table.setFilter(filter)
                data_table.refresh()

                # horiz_header = dt.header()
                for i in range(data_table.numCols()):
                    field = mtd.indexFieldObject(i)
                    if not field:
                        continue

                    if not field.visibleGrid():
                        data_table.setColumnHidden(i, True)

                sub_menu = popup.addMenu(sub_popup)
                sub_menu.hovered.connect(  # type: ignore [attr-defined] # noqa: F821
                    sub_popup_frame.show
                )
                sub_popup_frame.move(
                    tmp_pos.x() + 200, tmp_pos.y()
                )  # FIXME: Hay que mejorar esto ...

        popup.move(tmp_pos.x(), tmp_pos.y())

        popup.exec(event.globalPos())
        del popup
        event.accept()

    def setChecked(self, index: Any) -> None:
        """
        Behavior when clicking on a cell.
        """

        row = index.row()
        col = index.column()
        field = self.cur.metadata().indexFieldObject(col)
        _type = field.type()
        if _type != "check":
            return
        model = self.cur.model()
        primary_key = model.value(row, self.cur.metadata().primaryKey())
        model._check_column[primary_key].setChecked(
            not model._check_column[primary_key].isChecked()
        )
        self.setPrimaryKeyChecked(str(primary_key), model._check_column[primary_key].isChecked())
        # print("FIXME: falta un repaint para ver el color!!")

    def paintFieldMtd(
        self, field_name: str, table_metadata: "pntablemetadata.PNTableMetaData"
    ) -> "pnfieldmetadata.PNFieldMetaData":
        """
        Return the metadata of a field.
        """

        if self.paint_field_mtd_ and self._paint_field_name == field_name:
            return self.paint_field_mtd_

        self._paint_field_name = field_name
        self.paint_field_mtd_ = table_metadata.field(field_name)

        if self.paint_field_mtd_ is None:
            raise Exception("paint_field_mtd_ is empty!.")

        return self.paint_field_mtd_

    timerViewRepaint_ = None

    # def focusInEvent(self, e: QtGui.QFocusEvent) -> None:
    #    """
    #    Focus pickup event.
    #    """

    #    obj = self
    #    # refresh = True
    #    while obj.parent():
    #        if getattr(obj, "inExec_", False):
    #            # refresh = False
    #            break
    #        else:
    #            obj = obj.parent()

    #    # if refresh:
    #    #    self.refresh()
    #    super().focusInEvent(e)

    def sortByColumn(self, column, order) -> None:
        """Overload Sort by column."""

        fix_column = 0

        if self.cursor_ is not None:
            fix_column = self.visual_index_to_metadata_index(column)
            mtdfield = self.model().metadata().indexFieldObject(fix_column)
            if mtdfield is not None:
                self.sort_ = "%s %s" % (mtdfield.name(), "ASC" if not order else "DESC")

        super().sortByColumn(fix_column, order)

    def refresh(self, refresh_option: Any = None) -> None:
        """
        Refresh the cursor.
        """
        if not self.cursor_:
            return

        if self.popup_:
            self.cursor_.refresh()
        # if not self.refreshing_ and self.cursor_ and not self.cursor_.aqWasDeleted() and self.cursor_.metadata():
        if not self.refreshing_:

            # if self.function_get_color and self.cursor_.model:
            #    if self.cursor_.model.color_function_ != self.function_get_color:
            #        self.cursor_.model.setColorFunction(self.function_get_color)

            self.refreshing_ = True
            self.hide()
            filter_: str = self.persistent_filter_
            if self.filter_:
                if self.filter_ not in self.persistent_filter_:
                    if self.persistent_filter_:
                        filter_ = "%s AND %s" % (filter_, self.filter_)
                    else:
                        filter_ = self.filter_

            self.cursor_.setFilter(filter_)

            if self.sort_:
                self.cursor_.setSort(self.sort_)

            last_pk = None
            buffer = self.cursor_.private_cursor.buffer_
            if buffer:
                last_pk = buffer.value(self.cursor_.primaryKey())

            self.cursor_.refresh()
            if last_pk is not None:
                self.selectRow(self.cur.at())
                self.cursor_.refreshBuffer()
            self.show()
            self.refreshing_ = False

    # @decorators.pyqtSlot()
    # @decorators.pyqtSlot(int)
    @decorators.not_implemented_warn
    def ensureRowSelectedVisible(self, position: Optional[int] = None) -> None:
        """Ensure row selected visible."""

        pass

    #    """
    #    Make the selected row visible.
    #    """
    #    print("****", position, self.cursor_.at(), self.cursor_.isValid())

    #    if position is None:
    #        if self.cursor():
    #            position = self.cursor_.at()
    #        else:
    #            return

    # index = self.cursor_.model.index(position, 0)
    # if index is not None:
    #    self.scrollTo(index)

    def setQuickFocus(self) -> None:
        """
        Fast focus without refreshments to optimize.
        """

        # setPaletteBackgroundColor(qApp->palette().color(QPalette::Active, QColorGroup::Base)); FIXME
        super(FLDataTable, self).setFocus()

    def setColWidth(self, field: str, width: int) -> None:
        """
        Set the width of a column.

        @param field Name of the database field corresponding to the column.
        @param width Column width.
        """

        self.width_cols_[field] = width

    def resize_column(self, col: int, str_text: Optional[str]) -> None:
        """
        Resize a column.
        """

        if str_text is None:
            return

        str_text = str(str_text)

        field = self.model().metadata().indexFieldObject(col)
        if field.name() in self.width_cols_.keys():
            if self.columnWidth(col) < self.width_cols_[field.name()]:
                self.header().resizeSection(col, self.width_cols_[field.name()])
        else:
            wc_ = self.header().sectionSize(col)

            font_metrics = QtGui.QFontMetrics(self.header().font())
            wh_ = font_metrics.horizontalAdvance(field.alias() + "W")
            if wh_ < wc_:
                wh_ = wc_

            wc_ = font_metrics.horizontalAdvance(str_text) + font_metrics.maxWidth()
            if wc_ > wh_:
                self.header().resizeSection(col, wc_)
                if col == 0 and self.popup_:
                    parent_widget = self.parentWidget()
                    if parent_widget and parent_widget.width() < wc_:
                        self.resize(wc_, parent_widget.height())
                        parent_widget.resize(wc_, parent_widget.height())

    def cursorDestroyed(self, obj: Optional[Any] = None) -> None:
        """
        Unlink a cursor to this control.
        """

        if not obj or not isinstance(obj, pnsqlcursor.PNSqlCursor):
            return

        self.cursor_ = None

    """
    Indicate that a record has been chosen
    """
    recordChoosed = QtCore.pyqtSignal()
    """
    Indicate that the status of the record selection field has changed.

    That is to say your primary key has been included or removed from the list of selected primary keys.
    This signal is emitted when the user clicks on the check control and when it is changed
    Programmatically check using the FLDataTable :: setPrimaryKeyChecked method.

    @param primaryKeyValue The value of the primary key of the corresponding record.
    @param on The new state; TRUE check activated, FALSE check disabled.
    """
    primaryKeyToggled = QtCore.pyqtSignal(str, bool)

    def numRows(self) -> int:
        """
        Return number of records offered by the cursor.
        """

        if not self.cursor_:
            return -1

        return self.cursor_.model().rowCount()

    def column_name_to_column_index(self, name: str) -> int:
        """
        Return the real index (incusive hidden columns) from a field name.

        @param name The name of the field to look for in the table.
        @return column position in the table.
        """

        if not self.cursor_:
            return -1

        return self.cursor_.model().metadata().fieldIsIndex(name)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        """Double click event."""
        if cast(QtGui.QMouseEvent, event).button() != QtCore.Qt.MouseButton.LeftButton:
            return

        self.recordChoosed.emit()

    def visual_index_to_column_index(self, col_pos: int) -> int:
        """
        Return the column index from an index of visible columns.

        @param col_pos visible column position.
        @return index column of the column.
        """

        if not self.cursor_:
            return -2

        visible_id = -1
        ret_ = -1
        for column in range(self.model().columnCount()):
            if not self.isColumnHidden(self.logical_index_to_visual_index(column)):
                visible_id += 1

                if visible_id == col_pos:
                    ret_ = column
                    break

        return ret_

    def visual_index_to_metadata_index(self, col_pos: int) -> int:
        """
        Visual to logical index.
        """
        return self.header().logicalIndex(col_pos)

    def logical_index_to_visual_index(self, col_pos: int) -> int:
        """
        Logical Index to Visual Index.
        """
        return self.header().visualIndex(col_pos)

    def visual_index_to_field(self, pos_: int) -> Optional["pnfieldmetadata.PNFieldMetaData"]:
        """
        Return the metadata of a field according to visual position.
        """
        valid_idx = self.visual_index_to_column_index(pos_)  # corrige posición con ocultos.
        logical_idx = self.visual_index_to_metadata_index(valid_idx)  # posicion en metadata.
        if logical_idx == -1:
            return None

        table_metadata = self.model().metadata()
        field_metadata = table_metadata.indexFieldObject(logical_idx)

        if not field_metadata.visibleGrid():
            raise ValueError(
                "Se ha devuelto el field %s.%s que no es visible en el grid"
                % (table_metadata.name(), field_metadata.name())
            )
        # print("POS", pos_, field_metadata.name())
        return field_metadata

    def currentRow(self) -> int:
        """
        Return the current row.
        """
        return self.currentIndex().row()

    def currentColumn(self) -> int:
        """
        Return the current column.
        """
        return self.currentIndex().column()
