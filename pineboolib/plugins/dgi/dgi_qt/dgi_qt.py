"""Dgi_qt module."""
# # -*- coding: utf-8 -*-
from importlib import import_module

import PyQt5
from PyQt5 import QtWidgets

from pineboolib import logging
from pineboolib.plugins.dgi import dgi_schema

from typing import Any, Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from .dgi_objects import splash_screen
    from .dgi_objects import progress_dialog_manager  # type: ignore [import] # noqa: F401

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

    def extraProjectInit(self):
        """Extra init."""
        from .dgi_objects import splash_screen, progress_dialog_manager, status_help_msg

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
            array_mod = [PyQt5.QtWidgets, PyQt5.QtXml, PyQt5.QtGui, PyQt5.QtCore]
            for mod in array_mod:
                cls = getattr(mod, name, None)
                if cls is not None:
                    break

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

        from .dgi_objects.dlg_about import about_pineboo

        about_ = about_pineboo.AboutPineboo()
        about_.show()
