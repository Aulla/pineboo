"""Fllistview module."""
# -*- coding: utf-8 -*-

from PyQt6 import QtGui  # type: ignore
from pineboolib.core import decorators
from pineboolib import logging
from pineboolib.q3widgets import qlistview
from typing import Any, Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6 import QtWidgets  # noqa: F401 # pragma: no cover

LOGGER = logging.get_logger("FLListViewItem")


class FLListViewItem(QtGui.QStandardItem):
    """FLListView class."""

    _expandable: bool
    _key: str
    _open: bool
    _root: bool
    _index_child: int

    def __init__(self, parent: Optional["QtWidgets.QWidget"] = None) -> None:
        """Inicialize."""

        super().__init__()
        self._root = False
        self.setOpen(False)
        self.setExpandable(False)
        self._parent = None
        self.setKey("")
        self.setEditable(False)
        self._index_child = 0
        if parent:
            # Comprueba que tipo de parent es
            if isinstance(parent, qlistview.QListView):
                # self._root = True
                parent.model().setItem(0, 0, self)
            else:
                if isinstance(parent, self):  # type: ignore [arg-type] # noqa: F821
                    # print("Añadiendo nueva linea a", parent.text(0))
                    cast(FLListViewItem, parent).appendRow(self)

        # if parent:
        #    self._parent = parent
        #    self._row = self._parent.model().rowCount()
        #    if self._parent.model().item(0,0) is not None:
        #        self._parent.model().item(0,0).setChild(self._row,0, self)
        #        self._parent.model().item(0,0)._rowcount += 1
        #    else:
        #        self._parent.model().setItem(self._row,0,self)

        #    self._rows = self._parent.model().item(0,0)._rowcount - 1

    def firstChild(self) -> Any:
        """Return first child."""

        self._index_child = 0
        item = self.child(self._index_child)
        return item

    def nextSibling(self) -> Any:
        """Return next child."""

        self._index_child += 1
        item = self.child(self._index_child)
        return item

    def isExpandable(self) -> bool:
        """Return if is expandable."""

        return self._expandable
        # return True if self.child(0) is not None or not self.parent() else False

    def setText(self, *args) -> None:
        """Set text."""

        # print("Seteando", args, self.parent())
        # LOGGER.warning("Seteo texto %s" , args, stack_info = True )
        col = 0
        if len(args) == 1:
            value = args[0]
        else:
            col = args[0]
            value = str(args[1])

        if col == 0:
            # if self._root:
            # print("Inicializando con %s a %s" % ( value, self.parent()))
            super().setText(value)
        else:
            item = self.parent().child(self.row(), col)
            if item is None:
                item = FLListViewItem()
                self.parent().setChild(self.row(), col, item)

            item.setText(value)

    def text(self, col: int = 0) -> str:
        """Return text from a column."""

        ret = ""
        if col == 0:
            ret = super().text()

        return str(ret)

    @decorators.not_implemented_warn
    def setPixmap(self, *args):
        """Set pixmap."""
        pass

    def setExpandable(self, val: bool) -> None:
        """Set expandable."""

        self._expandable = val

    def setKey(self, key: str) -> None:
        """Set key."""
        self._key = key

    def key(self) -> str:
        """Return key."""

        if self.parent() and self.column() > 0:
            return (
                self.parent().child(self.row(), 0).key()  # type: ignore [attr-defined] # noqa: F821
            )
        return self._key

    def setOpen(self, open: bool) -> None:
        """Set Open."""
        self._open = open
