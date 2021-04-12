"""Groupbox module."""

# -*- coding: utf-8 -*-

from PyQt6 import QtWidgets  # type: ignore[import]
from . import qgroupbox


class GroupBox(qgroupbox.QGroupBox):
    """GroupBox class."""

    def __init__(self, *args) -> None:
        """Inicialize."""

        super().__init__(*args)
        self.setLayout(QtWidgets.QVBoxLayout())

    def add(self, widget: QtWidgets.QWidget) -> None:
        """Add new widget."""

        self.layout().addWidget(widget)
