"""Qpushbutton module."""
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore  # type: ignore
from pineboolib.core import decorators

from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5 import QtGui


class QPushButton(QtWidgets.QPushButton):
    """QPushButton class."""

    def __init__(self, *args, **kwargs) -> None:
        """Inicialize."""

        super(QPushButton, self).__init__(*args, **kwargs)
        self.setTextLabel = self.setText

    @decorators.NotImplementedWarn
    def setTextPosition(self, pos: int) -> None:
        """Set text position."""
        pass

    @decorators.NotImplementedWarn
    def setUsesBigPixmap(self, b: bool) -> None:
        """Set use big pixmap."""

        pass

    @decorators.NotImplementedWarn
    def setUsesTextLabel(self, b: bool) -> None:
        """Set use text label."""
        pass

    @property
    def pixmap(self) -> "QtGui.QIcon":
        """Return pixmap."""

        return self.icon()

    @pixmap.setter
    def pixmap(self, value: "QtGui.QIcon") -> None:
        """Set pixmap."""
        return self.setIcon(value)

    def setPixmap(self, value: "QtGui.QIcon") -> None:
        """Set pixmap."""
        return self.setIcon(value)

    def getToggleButton(self) -> bool:
        """Return if is checkable."""

        return self.isCheckable()

    def setToggleButton(self, v: bool) -> None:
        """Set if is checkable."""

        self.setCheckable(v)

    def getOn(self) -> bool:
        """Return if is checked."""
        return self.isChecked()

    def setOn(self, value: bool) -> None:
        """Set if is checked."""

        self.setChecked(value)

    def getText(self) -> str:
        """Return text."""

        return super().text()

    def setText(self, val: str) -> None:
        """Set text."""

        if self.maximumWidth() < 33 and len(val) > 4:
            val = ""
        super().setText(val)

    def setMaximumSize(self, w: Union[int, QtCore.QSize] = 30, h: Optional[int] = None) -> None:
        """Set Maximun size."""

        if isinstance(w, int):
            if h is None:
                h = w

            super().setMaximumSize(w, h)
        else:
            super().setMaximumSize(w)

    toggleButton = property(getToggleButton, setToggleButton)
    on = property(getOn, setOn)
    text = property(getText, setText)  # type: ignore

    @decorators.NotImplementedWarn
    def __getattr__(self, name: str):
        """Return a attribute specified by name."""
        pass
