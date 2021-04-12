"""Qhboxlayout module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]
from typing import Optional


class QHBoxLayout(QtWidgets.QHBoxLayout):
    """QHBoxLayout class."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Inicialize."""

        if isinstance(parent, QtWidgets.QWidget):
            super().__init__(parent)
        else:
            super().__init__()
            if parent:
                parent.addLayout(self)

        self.setContentsMargins(2, 0, 2, 0)
        self.setSpacing(1)
        self.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
