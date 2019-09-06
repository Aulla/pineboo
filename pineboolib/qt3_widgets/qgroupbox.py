"""Qgroupbox module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets  # type: ignore
from pineboolib.core import decorators
from PyQt5 import Qt  # type: ignore
from pineboolib import logging

from typing import Any

logger = logging.getLogger("QGroupBox")


class QGroupBox(QtWidgets.QGroupBox):
    """QGroupBox class."""

    style_str: str
    _line_width: int
    presset = Qt.pyqtSignal(int)
    selectedId: int

    def __init__(self, *args, **kwargs) -> None:
        """Inicialize."""

        super(QGroupBox, self).__init__(*args, **kwargs)
        from pineboolib.core.settings import config

        self.style_str = ""
        self._line_width = 0
        # self._do_style()
        # self.setFlat(True)
        if not config.value("ebcomportamiento/spacerLegacy", False):
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

    def setLineWidth(self, width: int) -> None:
        """Set line width."""

        self._line_width = width
        # self._do_style()

    def setTitle(self, t: str) -> None:
        """Set title."""

        super().setTitle(t)
        # self._do_style()

    # def _do_style(self) -> None:
    #    """Apply style."""

    #    self.style_str = "QGroupBox { font-weight: bold; background-color: transparent;"
    #    if self._line_width == 0 and not self.title():
    #        self.style_str += " border: none;"
    #    else:
    #        self.style_str += " border-width: %spx transarent" % self._line_width
    #    self.style_str += " }"
    #    self.setStyleSheet(self.style_str)

    def get_enabled(self) -> bool:
        """Return if enabled."""
        return self.isEnabled()

    def set_enabled(self, b: bool) -> None:
        """Set enabled."""

        self.setDisabled(not b)

    @decorators.pyqtSlot(bool)
    def setShown(self, b: bool) -> None:
        """Set shown."""
        self.setVisible(b)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute especified by name."""

        if name == "title":
            self.setTitle(str(value))
        else:
            super().__setattr__(name, value)

    @decorators.NotImplementedWarn
    def setFrameShadow(self, fs: None) -> None:
        """Set frame shadow."""

        pass

    @decorators.NotImplementedWarn
    def setFrameShape(self, fs: None) -> None:
        """Set frame shape."""

        pass

    @decorators.NotImplementedWarn
    def newColumn(self) -> None:
        """Create a new column."""

        pass

    enabled = property(get_enabled, set_enabled)
