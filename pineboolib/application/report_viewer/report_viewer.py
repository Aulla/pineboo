"""Report viewer module."""

from PyQt5 import QtWidgets, QtCore, QtGui
from pineboolib.core.utils import utils_base

from typing import Optional


class ReportViewer(QtWidgets.QWidget):
    """ReportViewer class."""

    _interface: Optional["QtWidgets.QWidget"]

    def __init__(self, parent: Optional["QtWidgets.QWidget"] = None) -> None:
        """Initialize."""

        super().__init__(parent)

        from pineboolib.fllegacy import flmanagermodules

        dlg_ = utils_base.filedir("application/report_viewer/report_viewer.ui")
        self._interface = flmanagermodules.FLManagerModules.createUI(dlg_, None, self)

        if not self._interface:
            raise Exception("Error creating dlgConnect")
        # Centrado en pantalla
        frame_geo = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(
            QtWidgets.QApplication.desktop().cursor().pos()  # type: ignore [misc] # noqa: F821
        )
        center_point = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())
        self._interface.installEventFilter(self)
        self._interface.show()

    def eventFilter(self, object: "QtCore.QObject", event: "QtCore.QEvent") -> bool:
        """Event Filter."""

        if isinstance(event, QtGui.QKeyEvent):

            if event.key() == QtCore.Qt.Key_Escape:
                self.close()
                return True

        return super().eventFilter(object, event)
