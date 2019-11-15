"""Checkbox module."""

# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets  # type: ignore
from .qwidget import QWidget
from typing import Any


class CheckBox(QWidget):
    """CheckBox class."""

    _label: QtWidgets.QLabel
    _cb: QtWidgets.QCheckBox

    def __init__(self) -> None:
        """Inicialize."""

        super().__init__()

        self._label = QtWidgets.QLabel(self)
        self._cb = QtWidgets.QCheckBox(self)
        spacer = QtWidgets.QSpacerItem(
            1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        _lay = QtWidgets.QHBoxLayout()
        _lay.addWidget(self._cb)
        _lay.addWidget(self._label)
        _lay.addSpacerItem(spacer)
        self.setLayout(_lay)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute."""

        if name == "text":
            self._label.setText(str(value))
        elif name == "checked":
            self._cb.setChecked(value)

    def __getattr__(self, name: str) -> Any:
        """Return an attribute."""

        if name == "checked":
            return self._cb.isChecked()
