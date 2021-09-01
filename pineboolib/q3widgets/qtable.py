"""Qtable module."""

# -*- coding: utf-8 -*-
from typing import Optional, Any, List, Union, cast
from PyQt6 import QtWidgets, QtCore, QtGui  # type: ignore[import]
from pineboolib.core import decorators
from pineboolib.core.utils.utils_base import format_double
from . import qwidget


# FIXMEQT6 class Q3TableWidget(QtWidgets.QTableWidget, qwidget.QWidget):
class Q3TableWidget(QtWidgets.QTableWidget, qwidget.QWidget):
    """
    Remove problematic properties from PyQt6-Stubs that we need to redefine.
    """

    currentChanged: Any


class QTable(Q3TableWidget):
    """QTable class."""

    linea_actuall = None
    currentChanged = QtCore.pyqtSignal(
        int, int
    )  # need overload (in Qt5, this signal is dataChanged)
    doubleClicked = QtCore.pyqtSignal(int, int)  # type: ignore [assignment] # noqa: F821
    clicked = QtCore.pyqtSignal(int, int)  # type: ignore [assignment] # noqa: F821
    valueChanged = QtCore.pyqtSignal(int, int)
    read_only_cols: List[int]
    read_only_rows: List[int]
    cols_list: List[str]
    resize_policy: QtWidgets.QSizePolicy

    Default = 0
    Manual = 1
    AutoOne = 2
    AutoOneFit = 3
    sort_column_: int

    def __init__(self, parent: Optional["QtWidgets.QGroupBox"] = None, name: str = None) -> None:
        """Inicialize."""
        super(QTable, self).__init__(parent)
        if not parent:
            self.setParent(self.parentWidget())

        if name:
            self.setObjectName(name)

        self.cols_list = []
        self.linea_actuall = -1
        cast(
            QtCore.pyqtSignal, self.currentCellChanged
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self.currentChanged_
        )
        cast(
            QtCore.pyqtSignal, self.cellDoubleClicked
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self.doubleClicked_
        )
        cast(
            QtCore.pyqtSignal, self.cellClicked
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self.simpleClicked_
        )
        cast(
            QtCore.pyqtSignal, self.itemChanged
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self.valueChanged_
        )
        self.read_only_cols = []
        self.read_only_rows = []
        self.resize_policy = cast(QtWidgets.QSizePolicy, 0)  # Default
        self.sort_column_ = -1

    def currentChanged_(
        self, current_row: int, current_column: int, previous_row: int, previous_column: int
    ) -> None:
        """Emit current changed signal."""
        if current_row > -1 and current_column > -1:
            cast(
                QtCore.pyqtSignal, self.currentChanged
            ).emit(  # type: ignore [attr-defined] # noqa: F821
                current_row, current_column
            )

    def doubleClicked_(self, field, col) -> None:
        """Emit double clicked signal."""
        cast(
            QtCore.pyqtSignal, self.cellDoubleClicked
        ).emit(  # type: ignore [attr-defined] # noqa: F821
            field, col
        )

    def simpleClicked_(self, field, col) -> None:
        """Emit simple clicked signal."""
        cast(QtCore.pyqtSignal, self.cellClicked).emit(  # type: ignore [attr-defined] # noqa: F821
            field, col
        )

    @decorators.not_implemented_warn
    def setResizePolicy(self, pol: QtWidgets.QSizePolicy) -> None:
        """Set resize polizy."""
        self.resize_policy = pol

    def __getattr__(self, name: str) -> Any:
        """Return an attribute specified by name."""
        if name == "Multi":
            return self.MultiSelection
        elif name == "SpreadSheet":
            return 999
        else:
            return getattr(super(), name, None)

    def valueChanged_(self, item=None) -> None:
        """Emit valueChanged signal."""

        if item and self.text(item.row(), item.column()) != "":
            cast(
                QtCore.pyqtSignal, self.valueChanged
            ).emit(  # type: ignore [attr-defined] # noqa: F821
                item.row(), item.column()
            )

    def numRows(self) -> int:
        """Return num rows."""

        return self.rowCount()

    def numCols(self) -> int:
        """Return num cols."""
        return self.columnCount()

    def setCellAlignment(self, row: int, col: int, alig_: int) -> None:
        """Set cell alignment."""
        self.item(row, col).setTextAlignment(alig_)

    def setNumCols(self, num: int) -> None:
        """Set num cols."""
        self.setColumnCount(num)
        self.setColumnLabels(",", ",".join(self.cols_list))

    def setNumRows(self, num: int) -> None:
        """Set num rows."""
        self.setRowCount(num)

    def setReadOnly(self, read_only: bool) -> None:
        """Set read only."""

        self.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
            if read_only
            else QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers
        )

    def selectionMode(self) -> "QtWidgets.QAbstractItemView.SelectionMode":
        """Return selection mode."""
        return super(QTable, self).selectionMode()

    def setFocusStyle(self, style: Union[str, int]) -> None:
        """Set focus style."""

        if isinstance(style, int):
            return
        else:
            self.setStyleSheet(style)

    def setColumnLabels(self, separador: str, lista: str) -> None:
        """Set column labels."""
        array_ = lista.split(separador)
        if array_:
            self.setHorizontalHeaderLabels(array_[0 : self.columnCount()])

    def setRowLabels(self, separator: str, lista: str) -> None:
        """Set row labels."""
        array_ = lista.split(separator)
        if array_:
            self.setVerticalHeaderLabels(array_[0 : self.rowCount()])

    def clear(self) -> None:
        """Clear values."""

        super().clear()
        for i in range(self.rowCount()):
            self.removeRow(i)
        self.setHorizontalHeaderLabels(self.cols_list)
        self.setRowCount(0)

    def setSelectionMode(self, mode: "QtWidgets.QAbstractItemView.SelectionMode") -> None:
        """Set selection mode."""
        if mode.value == 999:
            self.setAlternatingRowColors(True)
        else:
            super().setSelectionMode(mode)

    def setColumnStrechable(self, col: int, value: bool) -> None:
        """Set column strechable."""
        if value:
            self.horizontalHeader().setSectionResizeMode(
                col, QtWidgets.QHeaderView.ResizeMode.Stretch
            )
        else:
            self.horizontalHeader().setSectionResizeMode(
                col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )

    def setHeaderLabel(self, label: str) -> None:
        """Set header label."""

        self.cols_list.append(label)
        self.setColumnLabels(",", ",".join(self.cols_list))

    def insertRows(self, numero, number: int = 1) -> None:
        """Insert Rows."""
        for rep in range(number):
            self.insertRow(numero)

    def text(self, row: int, col: int) -> str:
        """Return text from a index."""
        if row is None:
            return
        return self.item(row, col).text() if self.item(row, col) else ""

    def setText(self, row: int, col: int, value: Any) -> None:
        """Set text to a index."""

        prev_item = self.item(row, col)
        if prev_item:
            bg_color = prev_item.background()

        right = True if isinstance(value, (int, float)) else False

        if right:
            value = value if isinstance(value, int) else format_double(value, len("%s" % value), 2)

        item = QtWidgets.QTableWidgetItem(str(value))

        if right:
            item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignVCenter + QtCore.Qt.AlignmentFlag.AlignRight
            )

        self.setItem(row, col, item)

        if prev_item:
            self.setCellBackgroundColor(row, col, bg_color)

        new_item = self.item(row, col)

        if new_item is not None:
            if row in self.read_only_rows or col in self.read_only_cols:
                new_item.setFlags(
                    cast(
                        QtCore.Qt.ItemFlag,
                        QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled,
                    )
                )
            else:
                new_item.setFlags(
                    cast(
                        QtCore.Qt.ItemFlag,
                        QtCore.Qt.ItemFlag.ItemIsSelectable
                        | QtCore.Qt.ItemFlag.ItemIsEnabled
                        | QtCore.Qt.ItemFlag.ItemIsEditable,
                    )
                )

    def setCellWidget(self, row: int, col: int, obj: "QtWidgets.QWidget") -> None:
        """Set cell widget."""

        super().setCellWidget(row, col, obj)

        widget = self.cellWidget(row, col)
        if widget is not None:
            if row in self.read_only_rows or col in self.read_only_cols:
                widget.setEnabled(False)

    def adjustColumn(self, k: int) -> None:
        """Adjust a column specified by name."""

        self.horizontalHeader().setSectionResizeMode(
            k, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )

    def setRowReadOnly(self, row: int, value: bool) -> None:
        """Set row read only specified by a number."""

        if value:
            if row in self.read_only_rows:
                return
            else:
                self.read_only_rows.append(row)
        else:
            if row in self.read_only_rows:
                self.read_only_rows.remove(row)
            else:
                return  # Ya esta en False la row

        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                if value:
                    item.setFlags(
                        cast(
                            QtCore.Qt.ItemFlag,
                            QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled,
                        )
                    )
                else:
                    item.setFlags(
                        cast(
                            QtCore.Qt.ItemFlag,
                            QtCore.Qt.ItemFlag.ItemIsSelectable
                            | QtCore.Qt.ItemFlag.ItemIsEnabled
                            | QtCore.Qt.ItemFlag.ItemIsEditable,
                        )
                    )

    def setColumnReadOnly(self, col: int, value: bool) -> None:
        """Set column read only."""

        if value:
            if col in self.read_only_cols:
                return
            else:
                self.read_only_cols.append(col)
        else:
            if col in self.read_only_cols:
                self.read_only_cols.remove(col)
            else:
                return

        for row in range(self.rowCount()):
            item = self.item(row, col)
            if item:
                if value:
                    item.setFlags(
                        cast(
                            QtCore.Qt.ItemFlag,
                            QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled,
                        )
                    )
                else:
                    item.setFlags(
                        cast(
                            QtCore.Qt.ItemFlag,
                            QtCore.Qt.ItemFlag.ItemIsSelectable
                            | QtCore.Qt.ItemFlag.ItemIsEnabled
                            | QtCore.Qt.ItemFlag.ItemIsEditable,
                        )
                    )

    @decorators.not_implemented_warn
    def setLeftMargin(self, margin: int):
        """Set left margin."""
        pass

    def setCellBackgroundColor(self, row: int, col: int, color: "QtGui.QBrush") -> None:
        """Set cell backgroun color."""
        item = self.item(row, col)

        if item is not None and color:
            item.setBackground(color)

    def getSorting(self) -> int:
        """Return sorting column."""

        return self.sort_column_

    def setSorting(self, col: int) -> None:
        """Set sorting column."""

        if not super().isSortingEnabled():
            super().setSortingEnabled(True)
        super().sortByColumn(col, QtCore.Qt.SortOrder.AscendingOrder)
        self.sort_column_ = col

    sorting = property(getSorting, setSorting)

    def editCell(self, row: int, col: int) -> None:
        """Edit a cell."""
        self.editItem(self.item(row, col))
