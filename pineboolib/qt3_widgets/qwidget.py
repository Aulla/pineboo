"""Qwidget module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore  # type: ignore
from typing import Optional


class QWidget(QtWidgets.QWidget):
    """QWidget class."""

    def child(self, child_name: str) -> Optional[QtWidgets.QWidget]:
        """Return an QWidget especified by name."""

        return self.findChild(QtWidgets.QWidget, child_name, QtCore.Qt.FindChildrenRecursively)

    def get_title(self) -> str:
        """Return widget title."""
        return self.windowTitle()

    def set_title(self, title: str) -> None:
        """Set title."""
        self.setWindowTitle(title)

    title = property(get_title, set_title)
