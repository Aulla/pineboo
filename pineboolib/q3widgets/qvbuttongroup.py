"""qhbuttongroup module."""

from PyQt5 import QtWidgets

from . import qbuttongroup


class QVButtonGroup(qbuttongroup.QButtonGroup):
    """QHButtonGroup class."""

    def __init__(self, *args):
        """Initialize."""

        super().__init__(*args)
        self.setLayout(QtWidgets.QVBoxLayout())
