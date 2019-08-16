"""Fldateedit module."""

# -*- coding: utf-8 -*-
import datetime
from typing import Union, Optional

from PyQt5 import QtCore, QtWidgets  # type: ignore
from pineboolib.qt3_widgets import qdateedit
from pineboolib.application.utils.date_conversion import convert_to_qdate
from pineboolib.application.types import Date


class FLDateEdit(qdateedit.QDateEdit):
    """FLDateEdit class."""

    valueChanged: QtCore.pyqtSignal = QtCore.pyqtSignal()
    DMY: str
    _parent: QtWidgets.QWidget

    def __init__(self, parent: QtWidgets.QWidget, name: str) -> None:
        """Inicialize."""

        super().__init__(parent, name)
        self.DMY = "dd-MM-yyyy"
        self.setMinimumWidth(90)
        self.setMaximumWidth(90)
        self._parent = parent

    def setOrder(self, order: str) -> None:
        """Set order."""
        self.setDisplayFormat(order)

    def getDate(self) -> Optional[str]:
        """Return date."""
        return super().getDate()

    def setDate(self, date: Union[str, datetime.date, Date] = None) -> None:  # type: ignore
        """Set Date."""

        if date in (None, "NAN", ""):
            date = QtCore.QDate.fromString(str("01-01-2000"), self.DMY)
        else:
            date = convert_to_qdate(date)

        super().setDate(date)
        self.setStyleSheet("color: black")

    date = property(getDate, setDate)  # type: ignore
