"""Flcheckbox module."""
# -*- coding: utf-8 -*-

from pineboolib.q3widgets import qcheckbox
from PyQt6 import QtWidgets  # type: ignore[import]
from typing import Optional


class FLCheckBox(qcheckbox.QCheckBox):
    """FLCheckBox class."""

    def __init__(self, parent: Optional["QtWidgets.QWidget"] = None, num_rows: int = None) -> None:
        """Inicialize."""
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
