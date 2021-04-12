"""Qmainwindow module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtCore  # type: ignore[import]
from typing import Optional, cast


class QMainWindow(QtWidgets.QMainWindow):
    """QMainWindow class."""

    def child(self, child_name: str, obj: QtCore.QObject) -> Optional[QtWidgets.QWidget]:
        """Return a child especified by name."""

        return cast(QtWidgets.QWidget, self.findChild(QtWidgets.QWidget, child_name))
