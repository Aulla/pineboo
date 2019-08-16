"""Qmdiarea module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

from pineboolib.fllegacy.aqsobjects.aqs import AQS


class QMdiArea(QtWidgets.QMdiArea):
    """QMdiArea class."""

    logo: QtGui.QPixmap

    def __init__(self, *args) -> None:
        """Inicialize."""
        super().__init__(*args)

        self.setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.logo = AQS.pixmap_fromMimeSource("pineboo-logo.png")
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.logo = self.logo.scaled(self.size(), QtCore.Qt.IgnoreAspectRatio)

    def paintEvent(self, e: QtCore.QEvent) -> None:
        """Paint event."""

        super().paintEvent(e)

        # painter = super().viewport()

        # x = self.width() - self.logo.width()
        # y = self.height() - self.logo.height()
        # painter.drawPixmap(x, y, self.logo)
