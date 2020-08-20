"""Qbuttongroup module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore  # type: ignore
from . import qgroupbox
from pineboolib.core import decorators


from typing import Callable


class QButtonGroup(qgroupbox.QGroupBox):
    """QButtonGroup class."""

    pressed = QtCore.pyqtSignal(int)
    clicked = QtCore.pyqtSignal(int)

    def __init__(self, *args) -> None:
        """Inicialize."""

        super().__init__(*args)
        self.bg_ = QtWidgets.QButtonGroup(self)
        self.selectedId = -1

    @decorators.not_implemented_warn
    def setLineWidth(self, w: int):
        """Set line width."""
        pass

    def setSelectedId(self, id: int) -> None:
        """Set selected id."""

        self.selectedId = id

    def __getattr__(self, name: str) -> Callable:
        """Return an attribute."""

        ret_ = getattr(self.bg_, name, None)
        return ret_
