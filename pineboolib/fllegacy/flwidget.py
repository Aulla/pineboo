"""Flwidget module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6 import Qt  # pragma: no cover


class FLWidget(QtWidgets.QWidget):
    """FLWidget class."""

    logo: "Qt.QPixmap"
    f_color: "Qt.QColor"
    p_color: "Qt.QColor"

    def __init__(self, parent: QtWidgets.QWidget, name: str) -> None:
        """Initialize."""

        super(FLWidget, self).__init__(parent)
        self.setObjectName(name)
