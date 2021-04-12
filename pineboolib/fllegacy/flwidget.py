"""Flwidget module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6 import QtGui  # type: ignore[import] # pragma: no cover


class FLWidget(QtWidgets.QWidget):
    """FLWidget class."""

    logo: "QtGui.QPixmap"
    f_color: "QtGui.QColor"
    p_color: "QtGui.QColor"

    def __init__(self, parent: "QtWidgets.QWidget", name: str) -> None:
        """Initialize."""

        super(FLWidget, self).__init__(parent)
        self.setObjectName(name)
