"""Qframe module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .qgroupbox import QGroupBox  # noqa: F401 # pragma: no cover
    from .qwidget import QWidget  # noqa: F401 # pragma: no cover


class QFrame(QtWidgets.QFrame):
    """QFrame class."""

    _line_width: int

    PopupPanel = 7
    MenuBarPanel = 8
    ToolBarPanel = 9
    LineEditPanel = 10
    TabWidgetPanel = 11
    GroupBoxPanel = 12
    MShape = 13

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
