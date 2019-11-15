"""Qmainwindow module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from typing import Optional, cast


class QMainWindow(QtWidgets.QMainWindow):
    """QMainWindow class."""

    def child(self, child_name: str, obj: QtCore.QObject) -> Optional[QtWidgets.QWidget]:
        """Return a child especified by name."""

        return cast(QtWidgets.QWidget, self.findChild(QtWidgets.QWidget, child_name))
