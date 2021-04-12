"""Dateedit module."""

from PyQt6 import QtWidgets  # type: ignore[import]

from . import qdateedit
from pineboolib.application.qsatypes import date as datelib
from typing import Optional


class DateEdit(QtWidgets.QWidget):
    """DateEdit class."""

    label_control: QtWidgets.QLabel
    date_control: qdateedit.QDateEdit

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize."""

        super().__init__(parent)
        layout_ = QtWidgets.QHBoxLayout()
        self.label_control = QtWidgets.QLabel()
        self.date_control = qdateedit.QDateEdit()
        layout_.addWidget(self.label_control)
        layout_.addWidget(self.date_control)
        self.setLayout(layout_)

    def getDate(self) -> datelib.Date:
        """Return Date."""

        return datelib.Date(self.date_control.getDate())

    def setDate(self, date_: datelib.Date) -> None:
        """Set Date."""

        self.date_control.setDate(date_)

    def getLabel(self) -> str:
        """Return Label text."""

        return self.label_control.text()

    def setLabel(self, text_: str) -> None:
        """Set Label text."""

        self.label_control.setText(text_)

    date: datelib.Date = property(getDate, setDate)  # type: ignore [assignment] # noqa: F821
    label: str = property(getLabel, setLabel)  # type: ignore [assignment] # noqa: F821
