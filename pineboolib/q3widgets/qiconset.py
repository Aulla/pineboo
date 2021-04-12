"""QIconSet module."""

from PyQt6 import QtGui  # type: ignore[import]


class QIconSet(QtGui.QIcon):
    """QIconSet class."""

    def __init__(self, icon: QtGui.QIcon):
        """Initialize."""

        super().__init__(icon)
