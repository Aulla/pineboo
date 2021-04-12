"""Qtoolbar module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]


class QToolBar(QtWidgets.QToolBar):
    """QToolBar class."""

    _label: str

    def setLabel(self, label: str) -> None:
        """Set label."""
        self._label = label

    def getLabel(self) -> str:
        """Get label."""
        return self._label

    label = property(getLabel, setLabel)
