"""Qradiobutton module."""
# -*- coding: utf-8 -*-

from PyQt6 import QtWidgets, QtCore  # type: ignore[import]
from pineboolib import logging

from . import qbuttongroup

from typing import Optional, cast

LOGGER = logging.get_logger(__name__)


class QRadioButton(QtWidgets.QRadioButton):
    """QRadioButton class."""

    dg_id: Optional[int]

    def __init__(self, parent: Optional["qbuttongroup.QButtonGroup"] = None) -> None:
        """Inicialize."""

        super().__init__(parent)
        super().setChecked(False)
        self.dg_id = None

        cast(QtCore.pyqtSignal, self.clicked).connect(  # type: ignore [attr-defined] # noqa: F821
            self.send_clicked
        )

    def setButtonGroupId(self, id_: int) -> None:
        """Set button group id."""

        self.dg_id = id_
        if self.parent() and hasattr(self.parent(), "selectedId"):
            if self.dg_id == cast(qbuttongroup.QButtonGroup, self.parent()).selectedId:
                self.setChecked(True)

    def send_clicked(self) -> None:
        """Send clicked to parent."""

        if self.parent() and hasattr(self.parent(), "selectedId"):
            cast(qbuttongroup.QButtonGroup, self.parent()).presset.emit(self.dg_id)
            cast(
                qbuttongroup.QButtonGroup, self.parent()
            ).clicked.emit(  # type: ignore [has-type] # noqa: F821
                self.dg_id
            )

    def get_checked(self) -> bool:
        """Return is checked."""

        return super().isChecked()

    def set_checked(self, checked: bool) -> None:
        """Set checked."""

        super().setChecked(checked)

    def get_text(self) -> str:
        """Return text."""

        return super().text()

    def set_text(self, text: str) -> None:
        """Set text."""

        super().setText(text)

    checked = property(get_checked, set_checked)
    text: str = property(get_text, set_text)  # type: ignore[assignment] # noqa : F821
