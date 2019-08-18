"""Splash_screen module."""
from PyQt5 import QtGui, QtCore, QtWidgets  # type: ignore
from pineboolib.core.utils.utils_base import filedir
from pineboolib.core.settings import config


class splashscreen(object):
    """Show a splashscreen to inform keep the user busy while Pineboo is warming up."""

    _splash: QtWidgets.QSplashScreen

    def __init__(self):
        """Inicialize."""
        splash_path = filedir(
            "../share/splashscreen/%s240.png"
            % ("dbadmin" if config.value("application/dbadmin_enabled") else "quick")
        )

        splash_pix = QtGui.QPixmap(splash_path)
        self._splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        self._splash.setMask(splash_pix.mask())

        frameGm = self._splash.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(
            QtWidgets.QApplication.desktop().cursor().pos()
        )
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self._splash.move(frameGm.topLeft())

    def showMessage(self, text: str) -> None:
        """Show a message into spalsh screen."""
        self._splash.showMessage(text, QtCore.Qt.AlignLeft, QtCore.Qt.white)

    def hide(self) -> None:
        """Hide splash screen."""
        QtCore.QTimer.singleShot(1000, self._splash.hide)

    def show(self) -> None:
        """Show splash screen."""
        self._splash.show()
