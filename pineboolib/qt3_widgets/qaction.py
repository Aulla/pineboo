"""Qaction module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets  # type: ignore
from typing import Optional


class QAction(QtWidgets.QAction):
    """QAction class."""

    activated = QtCore.pyqtSignal()
    _menuText: str

    def __init__(self, *args) -> None:
        """Inicialize."""

        super().__init__(*args)
        self.triggered.connect(self.send_activated)
        self._menuText = ""

    def send_activated(self, b: Optional[bool] = None) -> None:
        """Send activated signal."""

        self.activated.emit()

    def getName(self) -> str:
        """Return widget name."""

        return self.objectName()

    def setName(self, n: str) -> None:
        """Set widget name."""

        self.setObjectName(n)

    def getMenuText(self) -> str:
        """Return menu text."""

        return self._menuText

    def setMenuText(self, t: str) -> None:
        """Set menu text."""

        self._menuText = t

    name = property(getName, setName)
    menuText = property(getMenuText, setMenuText)
