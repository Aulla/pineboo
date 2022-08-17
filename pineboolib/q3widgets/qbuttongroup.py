"""Qbuttongroup module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtCore  # type: ignore[import]
from . import qgroupbox


from typing import Callable


class QButtonGroup(qgroupbox.QGroupBox):
    """QButtonGroup class."""

    pressed = QtCore.pyqtSignal(int)  # type: ignore [assignment] # noqa: F821
    clicked = QtCore.pyqtSignal(int)  # type: ignore [assignment] # noqa: F821

    def __init__(self, *args) -> None:
        """Inicialize."""

        super().__init__(*args)
        self.bg_ = QtWidgets.QButtonGroup(self)
        self.selectedId = -1  # pylint: disable=invalid-name

    def setSelectedId(self, id_: int) -> None:
        """Set selected id."""

        self.selectedId = id_

    def __getattr__(self, name: str) -> Callable:
        """Return an attribute."""

        ret_ = getattr(self.bg_, name, None)
        return ret_
