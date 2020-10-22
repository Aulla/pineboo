"""Qwidget module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from typing import cast, Optional, Any


class QWidget(QtWidgets.QWidget):
    """QWidget class."""

    def child(self, child_name: str) -> Optional[QtWidgets.QWidget]:
        """Return an QWidget especified by name."""

        ret = cast(QtWidgets.QWidget, self.findChild(QtWidgets.QWidget, child_name))

        return ret

    def get_title(self) -> str:
        """Return widget title."""
        return self.windowTitle()

    def set_title(self, title: str) -> None:
        """Set title."""
        self.setWindowTitle(title)

    def getattr(self, name: str) -> Any:
        if name == "name":
            return self.objectName()
        else:
            print("FIXME:Q3Widget:", name)
            return getattr(QtCore.Qt, name, None)

    title = property(get_title, set_title)
