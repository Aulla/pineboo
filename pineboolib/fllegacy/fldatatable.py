"""Fldatatable module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, Qt, QtGui

from pineboolib.core import decorators, settings
from pineboolib.core.utils import utils_base

from pineboolib import logging

from typing import Any, Optional, List, Dict, Tuple, cast, TYPE_CHECKING

from pineboolib.application.database import pnsqlcursor, pncursortablemodel


if TYPE_CHECKING:
    from pineboolib.application.metadata import pnfieldmetadata
    from pineboolib.application.metadata import pntablemetadata
    from pineboolib.interfaces import isqlcursor

logger = logging.getLogger(__name__)


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
    rowSelected: int

    """
    Numero de la columna (campo) seleccionada actualmente
    """
    colSelected: int

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
    pixOk_: Qt.QPixmap
    pixNo_: Qt.QPixmap

    """
    Lista con las claves primarias de los registros seleccionados por chequeo
    """
    primarysKeysChecked_: List[object]

    """
    Filtro persistente para el cursor
    """
    persistentFilter_: str

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
    widthCols_: Dict[str, int]

    """
    Indica si se deben mostrar los campos tipo pixmap en todas las filas
    """
    showAllPixmaps_: bool

    """
    Nombre de la función de script a invocar para obtener el color de las filas y celdas
    """
    function_get_color: Optional[str]

    """
    Indica que no se realicen operaciones con la base de datos (abrir formularios). Modo "sólo tabla".
    """
    onlyTable_: bool
    changingNumRows_: bool
    paintFieldName_: Optional[str]
    paintFieldMtd_: Optional["pnfieldmetadata.PNFieldMetaData"]

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
        self.refreshing_ = False
        self.filter_ = ""
        self.sort_ = ""
        self.rowSelected = -1
        self.colSelected = -1
        self.primarysKeysChecked_ = []
        self.persistentFilter_ = ""
        self.widthCols_ = {}

        self.pixOk_ = utils_base.filedir("./core/images/icons", "unlock.png")
        self.pixNo_ = utils_base.filedir("./core/images/icons", "lock.png")
        self.paintFieldMtd_ = None
        self.refreshing_ = False
        self.popup_ = False
        self.showAllPixmaps_ = False
        self.onlyTable_ = False
        self.function_get_color = None
        self.changingNumRows_ = False
        self.cursor_ = None

        self._v_header = self.verticalHeader()
        self._v_header.setDefaultSectionSize(22)
        self._h_header = self.horizontalHeader()
        self._h_header.setDefaultSectionSize(120)
        self._h_header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
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
                cast(QtCore.pyqtSignal, self.cursor_.cursorUpdated).disconnect(self.refresh)

                cur_chg = True

            if not self.cursor_ or cur_chg:
                self.cursor_ = cursor
                if not self.cursor_:
                    raise Exception("cursor_ is empty!")

                self.setFLReadOnly(self.readonly_)
                self.setEditOnly(self.editonly_)
                self.setInsertOnly(self.insertonly_)
                self.setOnlyTable(self.onlyTable_)

                cast(QtCore.pyqtSignal, self.cursor_.cursorUpdated).connect(self.refresh)

                self.setModel(self.cursor_.model())
                self.setSelectionModel(self.cursor_.selection())
                # self.model().sort(self.header().logicalIndex(0), 0)
                self.installEventFilter(self)
                self.model().set_parent_view(self)
            # if self.cursor_.at() >= 0:
            #    QtCore.QTimer.singleShot(2000, self.marcaRow) #Por ahora es 3000 para que de tiempo a mostrarse FIXME

    def marcaRow(self, id_pk: Optional[Any]) -> None:
        """
        Set a persistent filter that always applies to the cursor before to refresh.
        """
        if id_pk is not None and self.numRows():
            pos = self.model().findPKRow((id_pk,))
            if pos is not None and pos != self.cur.currentRegister():
                self.cur.move(pos)
            # self.ensureRowSelectedVisible()

    def setPersistentFilter(self, p_filter: Optional[str] = None) -> None:
        """Set the persistent filter for this control."""

        if p_filter is None:
            raise Exception("Invalid use of setPersistentFilter with None")
        self.persistentFilter_ = p_filter

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

        return self.primarysKeysChecked_

    def clearChecked(self) -> None:
        """
        Clear the list with the primary keys of the records selected by check.
        """

        self.primarysKeysChecked_.clear()
        model = self.cur.model()
        for r in model._check_column.keys():
            model._checkColumn[r].setChecked(False)

    def setPrimaryKeyChecked(self, primaryKeyValue: str, on: bool) -> None:
        """
        Set the status selected by check for a record, indicating the value of its primary key.
        """

        model = self.cur.model()
        if on:
            if primaryKeyValue not in self.primarysKeysChecked_:
                self.primarysKeysChecked_.append(primaryKeyValue)
                self.primaryKeyToggled.emit(primaryKeyValue, False)
        else:
            if primaryKeyValue in self.primarysKeysChecked_:
                self.primarysKeysChecked_.remove(primaryKeyValue)
                self.primaryKeyToggled.emit(primaryKeyValue, False)

        if primaryKeyValue not in model._check_column.keys():
            model._check_column[primaryKeyValue] = QtWidgets.QCheckBox()

        model._check_column[primaryKeyValue].setChecked(on)

    def setShowAllPixmaps(self, s: bool) -> None:
        """
        Set if the pixmaps of unselected lines are displayed.
        """

        self.showAllPixmaps_ = s

    def showAllPixmap(self) -> bool:
        """
        Return if pixmaps of unselected lines are displayed.
        """

        return self.showAllPixmaps_

    def setFunctionGetColor(self, f: Optional[str], iface: Optional[Any] = None) -> None:
        """
        Set the function to use to calculate the color of the cell.
        """

        self.fltable_iface = iface
        self.function_get_color = f

    def functionGetColor(self) -> Tuple[Optional[str], Any]:
        """
        Return the function to use to calculate the color of the cell.
        """

        return (self.function_get_color, self.fltable_iface)

    def setOnlyTable(self, on: bool = True) -> None:
        """
        Set if the control is only Table mode.
        """

        if not self.cursor_ or self.cursor_.aqWasDeleted():
            return

        self.cursor_.setEdition(not on, self.objectName())
        self.cursor_.setBrowse(not on, self.objectName())
        self.onlyTable_ = on

    def onlyTable(self) -> bool:
        """
        Return if the control is only Table mode.
        """

        return self.onlyTable_

    def indexOf(self, i: int) -> str:
        """
        Return the visual index of a position.
        """

        return self.header().visualIndex(i)

    def fieldName(self, col: int) -> str:
        """
        Return the name of the field according to a position.
        """

        field = self.cur.metadata().indexFieldObject(self.indexOf(col))
        if field is None:
            raise Exception("Field not found")
        return field.name()

    def eventFilter(self, o: Any, e: Any) -> bool:
        """
        Event Filtering.
        """

        r = self.currentRow()
        c = self.currentColumn()
        nr = self.numRows()
        nc = self.numCols()
        if e.type() == QtCore.QEvent.KeyPress:
            key_event = e

            if key_event.key() == QtCore.Qt.Key_Escape and self.popup_ and self.parentWidget():
                self.parentWidget().hide()
                return True

            if key_event.key() == QtCore.Qt.Key_Insert:
                return True

            if key_event.key() == QtCore.Qt.Key_F2:
                return True

            if key_event.key() == QtCore.Qt.Key_Up and r == 0:
                return True

            if key_event.key() == QtCore.Qt.Key_Left and c == 0:
                return True

            if key_event.key() == QtCore.Qt.Key_Down and r == nr - 1:
                return True

            if key_event.key() == QtCore.Qt.Key_Right and c == nc - 1:
                return True

            if key_event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return) and r > -1:
                self.recordChoosed.emit()
                return True

            if key_event.key() == QtCore.Qt.Key_Space:
                self.setChecked(self.model().index(r, c))

            if not settings.config.value("ebcomportamiento/FLTableShortCut", False):
                if key_event.key() == QtCore.Qt.Key_A and not self.popup_:
                    if (
                        self.cursor_
                        and not self.readonly_
                        and not self.editonly_
                        and not self.onlyTable_
                    ):

                        self.cursor_.insertRecord()
                        return True
                    else:
                        return False

                if key_event.key() == QtCore.Qt.Key_C and not self.popup_:
                    if (
                        self.cursor_
                        and not self.readonly_
                        and not self.editonly_
                        and not self.onlyTable_
                    ):
                        self.cursor_.copyRecord()
                        return True
                    else:
                        return False

                if key_event.key() == QtCore.Qt.Key_M and not self.popup_:
                    if self.cursor_ and not self.readonly_ and not self.onlyTable_:
                        self.cursor_.editRecord()
                        return True
                    else:
                        return False

                if key_event.key() == QtCore.Qt.Key_Delete and not self.popup_:
                    if (
                        self.cursor_
                        and not self.readonly_
                        and not self.editonly_
                        and not self.onlyTable_
                    ):
                        self.cursor_.deleteRecord()
                        return True
                    else:
                        return False

                if key_event.key() == QtCore.Qt.Key_V and not self.popup_:
                    if self.cursor_ and not self.onlyTable_:
                        self.cursor_.browseRecord()
                        return True

            return False

        return super(FLDataTable, self).eventFilter(o, e)

    @decorators.not_implemented_warn
    def paintCell(self, p: Any, row: int, col: int, cr: Any, selected: bool, cg: Any) -> None:
        """Paint the cell."""

        pass

    @decorators.not_implemented_warn
    def paintField(self, p: Any, field: str, cr: Any, selected: bool) -> None:
        """Paint the field."""
        pass

    def contextMenuEvent(self, e: Any) -> None:
        """
        To prevent the context menu from appearing with the options to edit records.
        """

        super().contextMenuEvent(e)

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

        db = self.cursor_.db()
        pri_key_val = self.cursor_.valueBuffer(pri_key)

        from pineboolib.q3widgets.qmenu import QMenu
        from pineboolib.q3widgets.qwidget import QWidget
        from pineboolib.q3widgets.qvboxlayout import QVBoxLayout

        from .fldatatable import FLDataTable

        popup = QMenu(self)

        menu_frame = QWidget(self, QtCore.Qt.Popup)

        lay = QVBoxLayout()
        menu_frame.setLayout(lay)

        tmp_pos = e.globalPos()

        for rel in rel_list:
            cur = pnsqlcursor.PNSqlCursor(
                rel.foreignTable(), True, db.connectionName(), None, None, popup
            )

            if cur.private_cursor.metadata_:
                mtd = cur.metadata()
                field = mtd.field(rel.foreignField())
                if field is None:
                    continue

                sub_popup = QMenu(self)
                sub_popup.setTitle(mtd.alias())
                sub_popup_frame = QWidget(sub_popup, QtCore.Qt.Popup)
                lay_popup = QVBoxLayout(sub_popup)
                sub_popup_frame.setLayout(lay_popup)

                dt = FLDataTable(None, "FLDataTable", True)
                lay_popup.addWidget(dt)

                dt.setFLSqlCursor(cur)
                filter = db.connManager().manager().formatAssignValue(field, pri_key_val, False)
                cur.setFilter(filter)
                dt.setFilter(filter)
                dt.refresh()

                # horiz_header = dt.header()
                for i in range(dt.numCols()):
                    field = mtd.indexFieldObject(i)
                    if not field:
                        continue

                    if not field.visibleGrid():
                        dt.setColumnHidden(i, True)

                sub_menu = popup.addMenu(sub_popup)
                sub_menu.hovered.connect(sub_popup_frame.show)
                sub_popup_frame.move(
                    tmp_pos.x() + 200, tmp_pos.y()
                )  # FIXME: Hay que mejorar esto ...

        popup.move(tmp_pos.x(), tmp_pos.y())

        popup.exec_(e.globalPos())
        del popup
        e.accept()

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
        pK = str(model.value(row, self.cur.metadata().primaryKey()))
        model._checkColumn[pK].setChecked(not model._checkColumn[pK].isChecked())
        self.setPrimaryKeyChecked(str(pK), model._checkColumn[pK].isChecked())
        # print("FIXME: falta un repaint para ver el color!!")

    # def focusOutEvent(self, e: QtCore.QEvent) -> None:
    #    """
    #    Losing focus event.
    #    """
    # setPaletteBackgroundColor(qApp->palette().color(QPalette::Active, QColorGroup::Background)) FIXME
    #    pass

    # def syncNumRows(self) -> None:
    #    """
    #    Synchronize the number of lines.
    #    """

    # print("syncNumRows")
    #    if not self.cursor_:
    #        return

    #    if self.changingNumRows_:
    #        return
    # if self.numRows() != self.cursor_.size():
    #    self.changingNumRows_ = True
    #    self.setNumRows(self.cursor_.size())
    #    self.changingNumRows_ = False

    def paintFieldMtd(
        self, f: str, t: "pntablemetadata.PNTableMetaData"
    ) -> "pnfieldmetadata.PNFieldMetaData":
        """
        Return the metadata of a field.
        """

        if self.paintFieldMtd_ and self.paintFieldName_ == f:
            return self.paintFieldMtd_

        self.paintFieldName_ = f
        self.paintFieldMtd_ = t.field(f)

        if self.paintFieldMtd_ is None:
            raise Exception("paintFieldMtd_ is empty!.")

        return self.paintFieldMtd_

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

            # if self.function_get_color and self.cur.model():
            #    if self.cur.model().color_function_ != self.function_get_color:
            #        self.cur.model().setColorFunction(self.function_get_color)

            self.refreshing_ = True
            self.hide()
            filter: str = self.persistentFilter_
            if self.filter_:
                if self.filter_ not in self.persistentFilter_:
                    if self.persistentFilter_:
                        filter = "%s AND %s" % (filter, self.filter_)
                    else:
                        filter = self.filter_

            self.cur.setFilter(filter)
            if self.sort_:
                self.cur.setSort(self.sort_)

            last_pk = None
            buffer = self.cur.buffer()
            if buffer:
                pk_name = buffer.pK()
                if pk_name is not None:
                    last_pk = buffer.value(pk_name)

            self.cur.refresh()

            self.marcaRow(last_pk)
            self.cur.refreshBuffer()
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
    #    print("****", position, self.cur.at(), self.cur.isValid())

    #    if position is None:
    #        if self.cursor():
    #            position = self.cur.at()
    #        else:
    #            return

    # index = self.cur.model().index(position, 0)
    # if index is not None:
    #    self.scrollTo(index)

    def setQuickFocus(self) -> None:
        """
        Fast focus without refreshments to optimize.
        """

        # setPaletteBackgroundColor(qApp->palette().color(QPalette::Active, QColorGroup::Base)); FIXME
        super(FLDataTable, self).setFocus()

    def setColWidth(self, field: str, w: int) -> None:
        """
        Set the width of a column.

        @param field Name of the database field corresponding to the column.
        @param w Column width.
        """

        self.widthCols_[field] = w

    def resize_column(self, col: int, str_text: Optional[str]) -> None:
        """
        Resize a column.
        """

        if str_text is None:
            return

        str_text = str(str_text)

        field = self.model().metadata().indexFieldObject(col)
        if field.name() in self.widthCols_.keys():
            if self.columnWidth(col) < self.widthCols_[field.name()]:
                self.header().resizeSection(col, self.widthCols_[field.name()])
        else:
            wC = self.header().sectionSize(col)

            fm = Qt.QFontMetrics(self.header().font())
            wH = fm.horizontalAdvance(field.alias() + "W")
            if wH < wC:
                wH = wC

            wC = fm.horizontalAdvance(str_text) + fm.maxWidth()
            if wC > wH:
                self.header().resizeSection(col, wC)
                if col == 0 and self.popup_:
                    pw = self.parentWidget()
                    if pw and pw.width() < wC:
                        self.resize(wC, pw.height())
                        pw.resize(wC, pw.height())

    # def delayedViewportRepaint(self) -> None:
    #    if not self.timerViewRepaint_:
    #        self.timerViewRepaint_ = QtCore.QTimer(self)
    #        self.timerViewRepaint_.timeout.connect(self.repaintViewportSlot)

    #    if not self.timerViewRepaint_.isActive():
    #        self.setUpdatesEnabled(False)
    #        self.timerViewRepaint_.start(50)

    # @decorators.pyqtSlot()
    # def repaintViewportSlot(self) -> None:

    #    vw = self.viewport()
    #    self.setUpdatesEnabled(True)
    #    if vw:
    #        vw.repaint(False)

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

        return self.cursor_.model().rows

    def column_name_to_column_index(self, name: str) -> int:
        """
        Return the real index (incusive hidden columns) from a field name.

        @param name The name of the field to look for in the table.
        @return column position in the table.
        """

        if not self.cursor_:
            return -1

        return self.cursor_.model().metadata().fieldIsIndex(name)

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
        """Double click event."""
        if cast(QtGui.QMouseEvent, e).button() != QtCore.Qt.LeftButton:
            return

        self.recordChoosed.emit()

    def visual_index_to_column_index(self, c: int) -> Optional[int]:
        """
        Return the column index from an index of visible columns.

        @param c visible column position.
        @return index column of the column.
        """

        if not self.cursor_:
            return None

        visible_id = -1
        ret_ = None
        for column in range(self.model().columnCount()):
            if not self.isColumnHidden(self.logical_index_to_visual_index(column)):
                visible_id += 1

                if visible_id == c:
                    ret_ = column
                    break

        return ret_

    def visual_index_to_logical_index(self, c: int) -> int:
        """
        Visual to logical index.
        """
        return self.header().logicalIndex(c)

    def logical_index_to_visual_index(self, c: int) -> int:
        """
        Logical Index to Visual Index.
        """
        return self.header().visualIndex(c)

    def visual_index_to_field(self, pos_: int) -> Optional["pnfieldmetadata.PNFieldMetaData"]:
        """
        Return the metadata of a field according to visual position.
        """

        # if pos_ is None:
        #     logger.warning("visual_index_to_field: pos is None")
        #     return None
        colIdx = self.visual_index_to_column_index(pos_)
        if colIdx is None:
            logger.warning("visual_index_to_field: colIdx is None")
            return None

        logIdx = self.logical_index_to_visual_index(colIdx)
        # if logIdx is None:
        #     logger.warning("visual_index_to_field: logIdx is None")
        #     return None
        model: pncursortablemodel.PNCursorTableModel = self.model()
        mtd = model.metadata()
        mtdfield = mtd.indexFieldObject(logIdx)
        if not mtdfield.visibleGrid():
            raise ValueError(
                "Se ha devuelto el field %s.%s que no es visible en el grid"
                % (mtd.name(), mtdfield.name())
            )

        return mtdfield

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
