"""Fldateedit module."""

# -*- coding: utf-8 -*-
import datetime
from typing import Union, Optional

from PyQt6 import QtCore, QtWidgets  # type: ignore
from pineboolib.q3widgets import qdateedit
from pineboolib.application.utils.date_conversion import convert_to_qdate
from pineboolib.application.types import Date


class FLDateEdit(qdateedit.QDateEdit):
    """FLDateEdit class."""

    valueChanged: QtCore.pyqtSignal = QtCore.pyqtSignal()
    DMY: str = "dd-MM-yyyy"
    _parent: QtWidgets.QWidget

    def __init__(self, parent: "QtWidgets.QWidget", name: str) -> None:
        """Inicialize."""

        super().__init__(parent, name)
        self.DMY = "dd-MM-yyyy"  # pylint: disable=invalid-name
        self.setMinimumWidth(90)
        # self.setMaximumWidth(90)
        self._parent = parent

    def setOrder(self, order: str) -> None:
        """Set order."""
        self.setDisplayFormat(order)

    def getDate(self) -> str:
        """Return date."""
        return super().getDate()

    def setDate(  # type: ignore [override] # noqa F821
        self, date: Union[str, datetime.date, Date, QtCore.QDate] = ""
    ) -> None:
        """Set Date."""
        new_date: Union[str, datetime.date, Date, QtCore.QDate, None] = (
            None if isinstance(date, QtCore.QDate) and date.isNull() else date
        )

        super().setDate(
            QtCore.QDate.fromString(str("01-01-2000"), self.DMY)
            if new_date in (None, "NAN", "")
            else convert_to_qdate(date)
        )
        self.setStyleSheet("color: black")

    date: Optional[str] = property(getDate, setDate)  # type: ignore [assignment] # noqa F821
