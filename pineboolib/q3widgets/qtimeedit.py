"""Qtimeedit module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtCore  # type: ignore[import]
from typing import Optional, Union


class QTimeEdit(QtWidgets.QTimeEdit):
    """QTimeEdit class."""

    def __init__(self, parent: Optional["QtWidgets.QWidget"] = None) -> None:
        """Inicialize."""
        super().__init__(parent)

        self.setDisplayFormat("hh:mm:ss A")

    def setTime(  # type: ignore [override] # noqa: F821
        self, time: Union["QtCore.QTime", str]
    ) -> None:
        """Set time."""
        if not isinstance(time, QtCore.QTime):
            t_list = time.split(":")
            time = QtCore.QTime(int(t_list[0]), int(t_list[1]), int(t_list[2]))
        super().setTime(time)

    def getTime(self) -> str:
        """Return time."""

        return super().time().toString("hh:mm:ss")

    time: str = property(getTime, setTime)  # type: ignore [assignment] # noqa F821
