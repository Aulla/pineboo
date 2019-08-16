"""Qradiobutton module."""
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore  # type: ignore
from pineboolib import logging

from .qbuttongroup import QButtonGroup

from typing import Optional, cast
from PyQt5.QtCore import pyqtSignal

logger = logging.getLogger(__name__)


class QRadioButton(QtWidgets.QRadioButton):
    """QRadioButton class."""

    dg_id: Optional[int]

    def __init__(self, parent: Optional[QButtonGroup] = None) -> None:
        """Inicialize."""

        super().__init__(parent)
        self.setChecked(False)
        self.dg_id = None

        cast(pyqtSignal, self.clicked).connect(self.send_clicked)

    def setButtonGroupId(self, id: int) -> None:
        """Set button group id."""

        self.dg_id = id
        if self.parent() and hasattr(self.parent(), "selectedId"):
            if self.dg_id == self.parent().selectedId:
                self.setChecked(True)

    def send_clicked(self) -> None:
        """Send clicked to parent."""

        if self.parent() and hasattr(self.parent(), "selectedId"):
            self.parent().presset.emit(self.dg_id)

    @QtCore.pyqtProperty(bool)  # type: ignore
    def checked(self) -> bool:
        """Return is checked."""

        return super().isChecked()

    @checked.setter  # type: ignore
    def setChecked(self, b: bool) -> None:
        """Set checked."""

        super().setChecked(b)

    @QtCore.pyqtProperty(str)  # type: ignore
    def text(self) -> str:
        """Return text."""

        return super().getText()

    @text.setter  # type: ignore
    def setText(self, t: str) -> None:
        """Set text."""

        super().setText(t)
