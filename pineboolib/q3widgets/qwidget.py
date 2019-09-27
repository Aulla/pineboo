"""Qwidget module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore  # type: ignore


class QWidget(QtWidgets.QWidget):
    """QWidget class."""

    def child(self, child_name: str) -> QtWidgets.QWidget:
        """Return an QWidget especified by name."""

        ret = self.findChild(QtWidgets.QWidget, child_name, QtCore.Qt.FindChildrenRecursively)
        if ret is None:
            raise Exception("child %s not found!." % child_name)

        return ret

    def get_title(self) -> str:
        """Return widget title."""
        return self.windowTitle()

    def set_title(self, title: str) -> None:
        """Set title."""
        self.setWindowTitle(title)

    title = property(get_title, set_title)
