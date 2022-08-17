"""Qgroupbox module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtCore  # type: ignore[import]
from pineboolib.core import decorators

from pineboolib.core import settings

from pineboolib import logging
from . import qwidget
from typing import Any

logger = logging.get_logger(__name__)


class QGroupBox(QtWidgets.QGroupBox, qwidget.QWidget):  # type: ignore [misc] # noqa: F821
    """QGroupBox class."""

    # style_str: str
    # _line_width: int
    presset = QtCore.pyqtSignal(int)
    selectedId: int
    line_width: int = 1

    def __init__(self, *args, **kwargs) -> None:
        """Inicialize."""
        if len(args):
            name = None
            parent = None
            if isinstance(args[0], str):
                name = args[0]
            else:
                parent = args[0]

            if len(args) > 1:
                if isinstance(args[1], str):
                    name = args[1]
                else:
                    parent = args[1]

            if parent is not None:
                super().__init__(parent, **kwargs)
            else:
                super().__init__(**kwargs)

            if name is not None:
                self.setObjectName(name)

        else:
            super().__init__()

        if not settings.CONFIG.value("ebcomportamiento/spacerLegacy", False):
            self.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred
            )

        self.setContentsMargins(0, 2, 0, 2)

    def setLayout(self, layout: QtWidgets.QLayout) -> None:
        """Set layout to QGroupBox."""

        # layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(0)
        super().setLayout(layout)

    def setLineWidth(self, width: int) -> None:
        """Set line width."""

        style_ = "%s#%s {  border: %spx solid gray; margin-top: 20px; border-radius: 3px;}" % (
            type(self).__name__,
            self.objectName(),
            width,
        )
        self.line_width = width
        self.setStyleSheet(style_)

    def setTitle(self, title: str) -> None:
        """Set title."""
        if self.line_width == 0:
            title = ""
        if title == "":
            self.setLineWidth(0)
        super().setTitle(title)

    def get_enabled(self) -> bool:
        """Return if enabled."""
        return self.isEnabled()

    def set_enabled(self, value: bool) -> None:
        """Set enabled."""

        self.setDisabled(not value)

    @decorators.pyqt_slot(bool)
    def setShown(self, value: bool) -> None:
        """Set shown."""
        self.setVisible(value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute especified by name."""

        if name == "title":
            self.setTitle(str(value))
        else:
            super().__setattr__(name, value)

    @decorators.not_implemented_warn
    def setFrameShadow(self, frame_shadow: None) -> None:
        """Set frame shadow."""

    @decorators.not_implemented_warn
    def setFrameShape(self, frame_shape: None) -> None:
        """Set frame shape."""

        pass

    @decorators.not_implemented_warn
    def newColumn(self) -> None:
        """Create a new column."""

        pass

    enabled = property(get_enabled, set_enabled)
