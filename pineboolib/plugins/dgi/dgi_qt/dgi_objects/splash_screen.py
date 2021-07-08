"""Splash_screen module."""
from PyQt6 import QtGui, QtCore, QtWidgets  # type: ignore
from pineboolib.core.utils.utils_base import filedir
from pineboolib.core import settings


class SplashScreen(object):
    """Show a splashscreen to inform keep the user busy while Pineboo is warming up."""

    _splash: "QtWidgets.QSplashScreen"

    def __init__(self):
        """Inicialize."""
        splash_path = filedir(
            "./core/images/splashscreen/%s240.png"
            % ("dbadmin" if settings.CONFIG.value("application/dbadmin_enabled") else "quick")
        )

        splash_pix = QtGui.QPixmap(splash_path)
        self._splash = QtWidgets.QSplashScreen(
            splash_pix, QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self._splash.setMask(splash_pix.mask())

        frame_geo = self._splash.frameGeometry()
        primary_screen = QtGui.QGuiApplication.primaryScreen()
        frame_geo.moveCenter(primary_screen.geometry().center())
        self._splash.move(frame_geo.topLeft())

    def showMessage(self, text: str) -> None:
        """Show a message into spalsh screen."""
        self._splash.showMessage(
            text, QtCore.Qt.AlignmentFlag.AlignLeft, QtCore.Qt.GlobalColor.white
        )

    def hide(self) -> None:
        """Hide splash screen."""
        QtCore.QTimer.singleShot(1000, self._splash.hide)

    def show(self) -> None:
        """Show splash screen."""
        self._splash.show()
