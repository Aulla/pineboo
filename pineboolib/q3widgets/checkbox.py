"""Checkbox module."""

# -*- coding: utf-8 -*-

from PyQt6 import QtWidgets  # type: ignore[import]
from .qwidget import QWidget


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
            1, 1, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )
        _lay = QtWidgets.QHBoxLayout()
        _lay.addWidget(self._cb)
        _lay.addWidget(self._label)
        _lay.addSpacerItem(spacer)
        self.setLayout(_lay)

    # def __setattr__(self, name: str, value: Any) -> None:
    #    """Set an attribute."""

    #    if name == "text":
    #        self._label.setText(str(value))
    #    elif name == "checked":
    #        self._cb.setChecked(value)

    # def __getattr__(self, name: str) -> Any:
    #    """Return an attribute."""

    #    if name == "checked":
    #        return self._cb.isChecked()

    def getText(self) -> str:
        """Return text label."""

        return self._label.text()

    def setText(self, value: str) -> None:
        """Set text label."""

        self._label.setText(value)

    def getChecked(self) -> bool:
        """Return if checked."""

        return self._cb.isChecked()

    def setChecked(self, value: bool) -> None:
        """Set checked."""

        self._cb.setChecked(value)

    text: str = property(getText, setText)  # type: ignore [assignment] # noqa: F821
    checked: bool = property(getChecked, setChecked)  # type: ignore [assignment] # noqa: F821
