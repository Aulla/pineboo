"""Fltimeedit module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore  # type: ignore
from typing import Union, List


class FLTimeEdit(QtWidgets.QTimeEdit):
    """FLTimeEdit class."""

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """Inicialize."""

        super(FLTimeEdit, self).__init__(parent)
        self.setDisplayFormat("hh:mm:ss")
        self.setMinimumWidth(90)
        self.setMaximumWidth(90)

    def setTime(self, v: Union[str, QtCore.QTime]) -> None:  # type: ignore
        """Set the time in the control."""

        if isinstance(v, str):
            list_v: List[str] = v.split(":")
            time = QtCore.QTime(int(list_v[0]), int(list_v[1]), int(list_v[2]))
        else:
            time = v

        super().setTime(time)
