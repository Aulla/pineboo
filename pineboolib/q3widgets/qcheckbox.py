"""Qcheckbox module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]


class QCheckBox(QtWidgets.QCheckBox):
    """QCheckBox class."""

    _parent: QtWidgets.QWidget

    def __init__(self, *args) -> None:
        """Inicialize."""

        if len(args) == 1:
            parent = args[0]
        else:
            self.setObjectName(args[0])
            parent = args[1]

        super().__init__(parent)

    def get_checked(self) -> bool:
        """Return if checked."""

        return self.isChecked()

    def set_checked(self, value: bool) -> None:
        """Set checked."""

        if isinstance(value, str):
            value = value == "true"

        super().setChecked(value)

    checked = property(get_checked, set_checked)
