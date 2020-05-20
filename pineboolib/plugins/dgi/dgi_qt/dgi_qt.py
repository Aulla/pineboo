"""Dgi_qt module."""
# # -*- coding: utf-8 -*-
from importlib import import_module

from PyQt5 import QtWidgets, QtCore, QtGui, Qt, QtXml  # type: ignore

from pineboolib import logging
from pineboolib.plugins.dgi import dgi_schema

from .dgi_objects.dlg_about import about_pineboo

from .dgi_objects import splash_screen, progress_dialog_manager, status_help_msg
from typing import Any, Optional

LOGGER = logging.get_logger(__name__)


class DgiQt(dgi_schema.DgiSchema):
    """dgi_qt class."""

    pnqt3ui: Any
    splash: "splash_screen.SplashScreen"
    progress_dialog_manager: "progress_dialog_manager.ProgressDialogManager"

    def __init__(self):
        """Inicialize."""
        super().__init__()  # desktopEnabled y mlDefault a True
        self._name = "qt"
        self._alias = "Qt5"

        self.splash = splash_screen.SplashScreen()
        self.progress_dialog_manager = progress_dialog_manager.ProgressDialogManager()
        self.status_help_msg = status_help_msg.StatusHelpMsg()

    def __getattr__(self, name):
        """Return a specific DGI object."""
        cls = self.resolveObject(self._name, name)
        if cls is None:
            mod_ = import_module(__name__)
            cls = getattr(mod_, name, None)

        if cls is None:
            cls = (
                getattr(QtWidgets, name, None)
                or getattr(QtXml, name, None)
                or getattr(QtGui, name, None)
                or getattr(Qt, name, None)
                or getattr(QtCore, name, None)
            )

        return cls

    def msgBoxWarning(
        self, text: str, parent: Optional["QtWidgets.QWidget"] = None, title: str = "Pineboo"
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Show a message box warning."""

        if parent is None:
            parent = QtWidgets.qApp.activeWindow()

        LOGGER.warning("%s", text)

        if QtWidgets.QApplication.platformName() not in ["offscreen", ""]:
            return QtWidgets.QMessageBox.warning(parent, title, text, QtWidgets.QMessageBox.Ok)

        return None

    def msgBoxQuestion(
        self, text: str, parent: Optional["QtWidgets.QWidget"] = None, title: str = "Pineboo"
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Show a message box warning."""

        if parent is None:
            parent = QtWidgets.qApp.activeWindow()

        # LOGGER.warning("%s", text)

        if QtWidgets.QApplication.platformName() not in ["offscreen", ""]:
            return QtWidgets.QMessageBox.warning(
                parent,
                title,
                text,
                cast(
                    QtWidgets.QMessageBox.StandardButton,
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                ),
            )

        return None

    def msgBoxError(
        self, text: str, parent: Optional["QtWidgets.QWidget"] = None, title: str = "Pineboo"
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Show a message box warning."""

        if parent is None:
            parent = QtWidgets.qApp.activeWindow()

        LOGGER.warning("%s", text)

        if QtWidgets.QApplication.platformName() not in ["offscreen", ""]:

            if parent is not None:
                return QtWidgets.QMessageBox.critical(parent, title, text, QtWidgets.QMessageBox.Ok)

        return None

    def msgBoxInfo(
        self, text: str, parent: Optional["QtWidgets.QWidget"] = None, title: str = "Pineboo"
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Show a message box warning."""

        if parent is None:
            parent = QtWidgets.qApp.activeWindow()

        LOGGER.warning("%s", text)

        if QtWidgets.QApplication.platformName() not in ["offscreen", ""]:

            if parent is not None:
                return QtWidgets.QMessageBox.information(parent, title, text)

        return None

    def about_pineboo(self) -> None:
        """Show about pineboo dialog."""

        about_ = about_pineboo.AboutPineboo()
        about_.show()
