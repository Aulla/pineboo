"""Fltimeedit module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtCore  # type: ignore
from typing import Union, List


class FLTimeEdit(QtWidgets.QTimeEdit):
    """FLTimeEdit class."""

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """Inicialize."""

        super().__init__(parent)
        self.setDisplayFormat("hh:mm:ss")
        self.setMinimumWidth(90)
        self.setTime(
            "00:00:00"
        )  # Normalmente deberia inicar a 00:00:00, pero inicia a 23:00:00 BUG??
        # self.setMaximumWidth(90)

    def setTime(self, value: Union[str, QtCore.QTime]) -> None:  # type: ignore
        """Set the time in the control."""

        if isinstance(value, str):
            list_: List[str] = value.split(":")
            value = QtCore.QTime(int(list_[0]), int(list_[1]), int(list_[2]))

        super().setTime(value)
