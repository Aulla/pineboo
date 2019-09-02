"""Qframe module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets  # type: ignore
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .qgroupbox import QGroupBox  # noqa: F401
    from .qwidget import QWidget  # noqa: F401


class QFrame(QtWidgets.QFrame):
    """QFrame class."""

    _line_width: int

    def __init__(self, parent: Union["QGroupBox", "QWidget"]) -> None:
        """Initialize."""

        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        # self.setStyleSheet("QFrame{background-color: transparent}")
        self.setLineWidth(1)
        # self._do_style()

    # def _do_style(self) -> None:
    #    """Set style."""

    #    self.style_str = "QFrame{ background-color: transparent;"
    #    self.style_str += " border-width: %spx;" % self._line_width
    #    self.style_str += " }"
    #    self.setStyleSheet(self.style_str)
