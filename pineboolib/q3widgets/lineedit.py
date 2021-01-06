"""Lineedit module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore
from . import qwidget
from typing import Any


class LineEdit(qwidget.QWidget):
    """LineEdit class."""

    _label: QtWidgets.QLabel
    _line: QtWidgets.QLineEdit

    def __init__(self) -> None:
        """Inicialize."""

        super(LineEdit, self).__init__()

        self._label = QtWidgets.QLabel(self)
        self._line = QtWidgets.QLineEdit(self)
        _lay = QtWidgets.QHBoxLayout()
        _lay.addWidget(self._label)
        _lay.addWidget(self._line)
        self.setLayout(_lay)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attributes."""

        if name == "label":
            self._label.setText(str(value))
        elif name == "text":
            self._line.setText(str(value))
        else:
            super(LineEdit, self).__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        """Return attribute."""

        if name == "text":
            return self._line.text()
