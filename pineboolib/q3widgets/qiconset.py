"""QIconSet module."""

from PyQt5 import QtGui


class QIconSet(QtGui.QIcon):
    """QIconSet class."""

    def __init__(self, icon: QtGui.QIcon):
        """Initialize."""

        super().__init__(icon)
