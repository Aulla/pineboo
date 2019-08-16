"""Qmainwindow module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore  # type: ignore
from typing import Optional


class QMainWindow(QtWidgets.QMainWindow):
    """QMainWindow class."""

    def child(self, child_name: str, obj: QtWidgets.QWidget) -> Optional[QtWidgets.QWidget]:
        """Return a child especified by name."""

        return self.findChild(obj, child_name, QtCore.Qt.FindChildrenRecursively)
