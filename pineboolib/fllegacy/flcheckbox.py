"""Flcheckbox module."""
# -*- coding: utf-8 -*-

from pineboolib.q3widgets import qcheckbox
from PyQt5 import QtWidgets
from typing import Optional


class FLCheckBox(qcheckbox.QCheckBox):
    """FLCheckBox class."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, num_rows: int = None) -> None:
        """Inicialize."""
        super(FLCheckBox, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
