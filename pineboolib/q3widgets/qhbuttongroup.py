"""qhbuttongroup module."""

from PyQt6 import QtWidgets  # type: ignore[import]

from . import qbuttongroup


class QHButtonGroup(qbuttongroup.QButtonGroup):
    """QHButtonGroup class."""

    def __init__(self, *args):
        """Initialize."""

        super().__init__(*args)
        self.setLayout(QtWidgets.QHBoxLayout())
