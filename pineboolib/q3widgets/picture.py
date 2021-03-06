"""Picture module."""
from PyQt5 import QtGui, Qt

from typing import Callable


class Picture(QtGui.QPicture):
    """Picture class."""

    def __getattr__(self, name: str) -> Callable:
        """Return painter attributes."""

        painter = Qt.QPainter(self)
        ret = getattr(painter, name, None)
        if ret is None:
            raise AttributeError("Attribute %s not found!" % name)

        return ret
