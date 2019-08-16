"""Qlistview module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui  # type: ignore
from pineboolib.core import decorators

from typing import Any, List, Optional, Union, cast


class QListView(QtWidgets.QWidget):
    """QListView class."""

    _resizeable: bool
    _clickable: bool
    _root_is_decorated: bool
    _default_rename_action: bool
    _tree: QtWidgets.QTreeView
    _cols_labels: List[str]
    _key: str
    _root_item: Any
    _current_row: int

    doubleClicked = QtCore.pyqtSignal(object)
    selectionChanged = QtCore.pyqtSignal(object)
    expanded = QtCore.pyqtSignal(object)
    collapsed = QtCore.pyqtSignal(object)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Inicialize."""

        super().__init__(parent=None)
        lay = QtWidgets.QVBoxLayout(self)
        self._tree = QtWidgets.QTreeView(self)
        lay.addWidget(self._tree)
        self._tree.setModel(QtGui.QStandardItemModel())
        self._cols_labels = []
        self._resizeable = True
        self._clickable = True
        self._default_rename_action = False
        self._root_is_decorated = False
        self._key = ""
        self._root_item = None
        self._current_row = -1
        cast(QtCore.pyqtSignal, self._tree.doubleClicked).connect(self.doubleClickedEmit)
        cast(QtCore.pyqtSignal, self._tree.clicked).connect(self.singleClickedEmit)
        cast(QtCore.pyqtSignal, self._tree.activated).connect(self.singleClickedEmit)

    def singleClickedEmit(self, index: Any) -> None:
        """Emit single clicked signal."""

        if index.column() != 0:
            index = index.sibling(index.row(), 0)
        else:
            index = index.sibling(index.row(), index.column())
        item = index.model().itemFromIndex(index)

        self.selectionChanged.emit(item)

    def doubleClickedEmit(self, index: Any) -> None:
        """Emit double clicked signal."""

        item = index.model().itemFromIndex(index)
        self.doubleClicked.emit(item)

    def addItem(self, t: str) -> None:
        """Add a new item."""

        from pineboolib.fllegacy.fllistviewitem import FLListViewItem

        self._current_row = self._current_row + 1
        item = FLListViewItem()
        item.setEditable(False)
        item.setText(t)
        if self._tree is not None:
            self._tree.model().setItem(self._current_row, 0, item)

    @decorators.NotImplementedWarn
    def setItemMargin(self, m: int):
        """Set items margin."""

        self.setContentsMargins(m, m, m, m)

    def setHeaderLabel(self, labels: Union[str, List[str]]) -> None:
        """Set header labels from a stringlist."""
        if isinstance(labels, str):
            labels = [labels]

        if self._tree is not None:
            self._tree.model().setHorizontalHeaderLabels(labels)
        self._cols_labels = labels

    def setColumnText(self, col: int, new_value: str) -> None:
        """Set Column text."""

        i = 0
        new_list = []
        for old_value in self._cols_labels:
            value = new_value if i == col else old_value
            new_list.append(value)

        self._cols_labels = new_list

    def addColumn(self, text: str) -> None:
        """Add a new column."""

        self._cols_labels.append(text)

        self.setHeaderLabel(self._cols_labels)

    @decorators.NotImplementedWarn
    def setClickable(self, c: bool) -> None:
        """Set clickable."""
        self._clickable = True if c else False

    @decorators.NotImplementedWarn
    def setResizable(self, r: bool) -> None:
        """Set resizeable."""

        self._resizeable = True if r else False

    @decorators.NotImplementedWarn
    def resizeEvent(self, e: QtCore.QEvent) -> None:
        """Process resize event."""
        if self._resizeable:
            super().resizeEvent(e)

    def clear(self) -> None:
        """Clear all data."""

        self._cols_labels = []

    @decorators.NotImplementedWarn
    def defaultRenameAction(self) -> bool:
        """Return default_rename_action enabled."""
        return self._default_rename_action

    @decorators.NotImplementedWarn
    def setDefaultRenameAction(self, b: bool) -> None:
        """Set default_rename_action enabled."""
        self._default_rename_action = b

    def model(self) -> QtGui.QStandardItemModel:
        """Return model index."""

        if self._tree is not None:
            return self._tree.model()
        else:
            raise Exception("No hay _tree")
