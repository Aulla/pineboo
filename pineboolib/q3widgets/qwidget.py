"""Qwidget module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtCore  # type: ignore[import]
from typing import cast, Any
from pineboolib.core import decorators


class QWidget(QtWidgets.QWidget):
    """QWidget class."""

    def child(self, child_name: str) -> QtWidgets.QWidget:
        """Return an QWidget especified by name."""

        ret = cast(QtWidgets.QWidget, self.findChild(QtWidgets.QWidget, child_name))

        return ret or QWidget()

    def get_title(self) -> str:
        """Return widget title."""
        return self.windowTitle()

    def set_title(self, title: str) -> None:
        """Set title."""
        self.setWindowTitle(title)

    @decorators.not_implemented_warn
    def setInsideMargin(self, value):
        """Set inside margin."""
        pass

    @decorators.not_implemented_warn
    def setInsideSpacing(self, value):
        """Set inside margin."""
        pass

    def getattr(self, name: str) -> Any:
        """Return an attribute specified by name."""

        if name == "name":
            return self.objectName()
        else:
            print("FIXME:Q3Widget:", name)
            return getattr(QtCore.Qt, name, None)

    title = property(get_title, set_title)
