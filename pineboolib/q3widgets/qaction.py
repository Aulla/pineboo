"""Qaction module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtGui  # type: ignore[import]
from typing import Optional


class QAction(QtGui.QAction):
    """QAction class."""

    activated = QtCore.pyqtSignal()
    _menu_text: str

    def __init__(self, *args) -> None:
        """Inicialize."""

        super().__init__(*args)
        self.triggered.connect(self.send_activated)  # type: ignore [attr-defined] # noqa: F821
        self._menu_text = ""

    def send_activated(self, value: Optional[bool] = None) -> None:
        """Send activated signal."""

        self.activated.emit()

    def getName(self) -> str:
        """Return widget name."""

        return self.objectName()

    def setName(self, name: str) -> None:
        """Set widget name."""

        self.setObjectName(name)

    def getMenuText(self) -> str:
        """Return menu text."""

        return self._menu_text

    def setMenuText(self, text: str) -> None:
        """Set menu text."""

        self._menu_text = text

    name = property(getName, setName)
    menuText = property(getMenuText, setMenuText)
