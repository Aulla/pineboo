"""PNCore class is used for receive signal from mainforms."""
from PyQt6 import QtCore, QtWidgets  # type: ignore[import]


class PNCore(QtWidgets.QWidget):
    """PNCore class."""

    @QtCore.pyqtSlot()
    def execDefaultScript(self):
        """Execdefaultscript class."""
        pass

    @QtCore.pyqtSlot()
    def openDefaultForm(self):
        """Opendefaultform class."""
        pass
