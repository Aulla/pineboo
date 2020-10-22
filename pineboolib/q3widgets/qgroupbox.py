"""Qgroupbox module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore  # type: ignore
from pineboolib.core import decorators

from pineboolib.core import settings

from pineboolib import logging
from . import qwidget
from typing import Any

logger = logging.get_logger(__name__)


class QGroupBox(QtWidgets.QGroupBox, qwidget.QWidget):
    """QGroupBox class."""

    # style_str: str
    # _line_width: int
    presset = QtCore.pyqtSignal(int)
    selectedId: int
    line_width: int = 1

    def __init__(self, *args, **kwargs) -> None:
        """Inicialize."""

        super().__init__(*args, **kwargs)

        if not settings.CONFIG.value("ebcomportamiento/spacerLegacy", False):
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self.setContentsMargins(0, 2, 0, 2)

    def setLayout(self, layout: QtWidgets.QLayout) -> None:
        """Set layout to QGroupBox."""

        # layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(0)
        super().setLayout(layout)

    def setLineWidth(self, s: int) -> None:
        """Set line width."""

        style_ = (
            "QGroupBox#%s {  border: %spx solid gray; margin-top: 20px; border-radius: 3px;}"
            % (self.objectName(), s)
        )
        self.line_width = s
        self.setStyleSheet(style_)

    def setTitle(self, t: str) -> None:
        """Set title."""
        if self.line_width == 0:
            t = ""
        if t == "":
            self.setLineWidth(0)
        super().setTitle(t)

    def get_enabled(self) -> bool:
        """Return if enabled."""
        return self.isEnabled()

    def set_enabled(self, b: bool) -> None:
        """Set enabled."""

        self.setDisabled(not b)

    @decorators.pyqt_slot(bool)
    def setShown(self, b: bool) -> None:
        """Set shown."""
        self.setVisible(b)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute especified by name."""

        if name == "title":
            self.setTitle(str(value))
        else:
            super().__setattr__(name, value)

    @decorators.not_implemented_warn
    def setFrameShadow(self, fs: None) -> None:
        """Set frame shadow."""

        pass

    @decorators.not_implemented_warn
    def setFrameShape(self, fs: None) -> None:
        """Set frame shape."""

        pass

    @decorators.not_implemented_warn
    def newColumn(self) -> None:
        """Create a new column."""

        pass

    enabled = property(get_enabled, set_enabled)
