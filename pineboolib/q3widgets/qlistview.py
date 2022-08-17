"""Qlistview module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets, QtGui  # type: ignore[import]

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
        cast(
            QtCore.pyqtSignal, self._tree.doubleClicked
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self.doubleClickedEmit
        )
        cast(
            QtCore.pyqtSignal, self._tree.clicked
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self.singleClickedEmit
        )
        cast(
            QtCore.pyqtSignal, self._tree.activated
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self.singleClickedEmit
        )

    def singleClickedEmit(self, index: Any) -> None:
        """Emit single clicked signal."""
        if not self._clickable:
            return

        if index.column() != 0:
            index = index.sibling(index.row(), 0)
        else:
            index = index.sibling(index.row(), index.column())
        item = index.model().itemFromIndex(index)

        self.selectionChanged.emit(item)

    def doubleClickedEmit(self, index: Any) -> None:
        """Emit double clicked signal."""
        if not self._clickable:
            return

        item = index.model().itemFromIndex(index)
        self.doubleClicked.emit(item)

    def addItem(self, item_text: str) -> None:
        """Add a new item."""

        from pineboolib.fllegacy.fllistviewitem import FLListViewItem

        self._current_row = self._current_row + 1
        item = FLListViewItem()
        item.setEditable(False)
        item.setText(item_text)
        if self._tree is not None:
            cast(QtGui.QStandardItemModel, self._tree.model()).setItem(self._current_row, 0, item)

    def setHeaderLabel(self, labels: Union[str, List[str]]) -> None:
        """Set header labels from a stringlist."""
        if isinstance(labels, str):
            labels = [labels]

        if self._tree is not None:
            cast(QtGui.QStandardItemModel, self._tree.model()).setHorizontalHeaderLabels(labels)
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

    def setClickable(self, clickable: bool) -> None:
        """Set clickable."""
        self._clickable = clickable

    def setResizable(self, resizeable: bool) -> None:
        """Set resizeable."""
        self._resizeable = resizeable

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Event filter."""

        if isinstance(event, QtGui.QResizeEvent):
            if not self._resizeable:
                return False

        return super().eventFilter(obj, event)

    def setItemMargin(self, item_margin: int) -> None:
        """Set items margin."""

        style_ = "QTreeView::item#%s { border: 0px; padding: %spx; }" % (
            self.objectName(),
            item_margin,
        )
        self._tree.setStyleSheet(style_)

    # @decorators.not_implemented_warn
    # def resizeEvent(self, e: QtCore.QEvent) -> None:
    #    """Process resize event."""
    #    if self._resizeable:
    #        super().resizeEvent(e)

    def clear(self) -> None:
        """Clear all data."""

        self._cols_labels = []

    def getDefaultRenameAction(self) -> bool:
        """Return default_rename_action enabled."""
        return self._default_rename_action

    def setDefaultRenameAction(self, default: bool) -> None:
        """Set default_rename_action enabled."""
        self._default_rename_action = default

    def model(self) -> QtGui.QStandardItemModel:
        """Return model index."""

        if self._tree is not None:
            return cast(QtGui.QStandardItemModel, self._tree.model())
        else:
            raise Exception("No hay _tree")

    def setRootIsDecorated(self, show: bool) -> None:
        """Set tree root decorated."""

        self._tree.setRootIsDecorated(show)

    def getRootIsDecorated(self) -> bool:
        """Return if tree is root decorated."""

        return self._tree.rootIsDecorated()

    rootIsDecorated = property(getRootIsDecorated, setRootIsDecorated)
    defaultRenameAction = property(getDefaultRenameAction, setDefaultRenameAction)
