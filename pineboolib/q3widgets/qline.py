"""QLine module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]
from typing import Optional


class QLine(QtWidgets.QFrame):
    """QLine class."""

    _object_name: Optional[str]
    _orientation: int

    def __init__(self, parent) -> None:
        """Inicialize."""

        super().__init__()
        self._object_name = None
        self._orientation = 0

    def getObjectName(self) -> Optional[str]:
        """Return object name."""

        return self._object_name

    def setObjectName(self, name: str) -> None:
        """Set object name."""

        self._object_name = name

    def setOrientation(self, ori_: int = 0) -> None:
        """Set orientation."""

        self._orientation = ori_
        self.setFrameShape(self.Shape.HLine if ori_ == 1 else self.Shape.VLine)

    def getOrientation(self) -> int:
        """Return orientation."""

        return self._orientation

    orientation = property(getOrientation, setOrientation)
    objectName = property(getObjectName, setObjectName)  # type: ignore [assignment]
