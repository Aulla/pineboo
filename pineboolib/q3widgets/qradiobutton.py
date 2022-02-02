"""Qradiobutton module."""
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets  # type: ignore
from pineboolib import logging

from .qbuttongroup import QButtonGroup

from typing import Optional, cast
from PyQt5.QtCore import pyqtSignal

LOGGER = logging.get_logger(__name__)


class QRadioButton(QtWidgets.QRadioButton):
    """QRadioButton class."""

    dg_id: Optional[int]

    def __init__(self, parent: Optional[QButtonGroup] = None) -> None:
        """Inicialize."""

        super().__init__(parent)
        super().setChecked(False)
        self.dg_id = None

        cast(pyqtSignal, self.clicked).connect(self.send_clicked)  # type: ignore [attr-defined]

    def setButtonGroupId(self, id: int) -> None:
        """Set button group id."""

        self.dg_id = id
        if self.parent() and hasattr(self.parent(), "selectedId"):
            if self.dg_id == cast(QButtonGroup, self.parent()).selectedId:
                self.setChecked(True)

    def send_clicked(self) -> None:
        """Send clicked to parent."""

        if self.parent() and hasattr(self.parent(), "selectedId"):
            cast(QButtonGroup, self.parent()).presset.emit(self.dg_id)
            cast(QButtonGroup, self.parent()).clicked.emit(self.dg_id)

    def get_checked(self) -> bool:
        """Return is checked."""

        return super().isChecked()

    def set_checked(self, b: bool) -> None:
        """Set checked."""

        super().setChecked(b)

    def get_text(self) -> str:
        """Return text."""

        return super().text()

    def set_text(self, t: str) -> None:
        """Set text."""

        super().setText(t)

    checked = property(get_checked, set_checked)
    text: str = property(get_text, set_text)  # type: ignore[assignment] # noqa : F821
