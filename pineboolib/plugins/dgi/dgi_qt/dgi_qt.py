"""Dgi_qt module."""
# # -*- coding: utf-8 -*-
from importlib import import_module

from PyQt6 import QtWidgets, QtXml, QtGui, QtCore  # type: ignore[import]

from pineboolib import logging
from pineboolib.plugins.dgi import dgi_schema

from typing import Any, Optional, cast, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .dgi_objects import (  # noqa : F401 # pragma: no cover
        splash_screen,
        progress_dialog_manager,
    )

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
            array_mod = [QtWidgets, QtXml, QtGui, QtCore]
            for mod in array_mod:
                cls = getattr(mod, name, None)
                if cls is not None:
                    break

        return cls

    def msgBoxWarning(
        self,
        text: str,
        parent: Optional["QtWidgets.QWidget"] = None,
        title: str = "Pineboo",
        buttons: List["QtWidgets.QMessageBox.StandardButton"] = [
            QtWidgets.QMessageBox.StandardButton.Ok
        ],
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Show a message box warning."""

        LOGGER.warning("%s", text)

        if QtWidgets.QApplication.platformName() not in ["offscreen", ""]:
            if parent is None:
                parent = QtWidgets.QApplication.activeWindow()

            return QtWidgets.QMessageBox.warning(parent, title, text, *buttons)

        return None

    def msgBoxQuestion(
        self, text: str, parent: Optional["QtWidgets.QWidget"] = None, title: str = "Pineboo"
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Show a message box warning."""

        if QtWidgets.QApplication.platformName() not in ["offscreen", ""]:
            if parent is None:
                parent = QtWidgets.QApplication.activeWindow()
            return QtWidgets.QMessageBox.question(
                parent,
                title,
                text,
                cast(
                    QtWidgets.QMessageBox.StandardButton,
                    QtWidgets.QMessageBox.StandardButton.Yes
                    | QtWidgets.QMessageBox.StandardButton.No
                    | QtWidgets.QMessageBox.StandardButton.Yes,
                ),
            )

        return None

    def msgBoxError(
        self, text: str, parent: Optional["QtWidgets.QWidget"] = None, title: str = "Pineboo"
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Show a message box warning."""

        LOGGER.warning("%s", text)

        if QtWidgets.QApplication.platformName() not in ["offscreen", ""]:
            if parent is None:
                parent = QtWidgets.QApplication.activeWindow()

            return QtWidgets.QMessageBox.critical(
                parent, title, text, QtWidgets.QMessageBox.StandardButton.Ok
            )

        return None

    def msgBoxInfo(
        self, text: str, parent: Optional["QtWidgets.QWidget"] = None, title: str = "Pineboo"
    ) -> Optional["QtWidgets.QMessageBox.StandardButton"]:
        """Show a message box warning."""

        LOGGER.warning("%s", text)

        if QtWidgets.QApplication.platformName() not in ["offscreen", ""]:
            if parent is None:
                parent = QtWidgets.QApplication.activeWindow()

            return QtWidgets.QMessageBox.information(parent, title, text)

        return None

    def about_pineboo(self) -> None:
        """Show about pineboo dialog."""

        from .dgi_objects.dlg_about import about_pineboo

        about_ = about_pineboo.AboutPineboo()
        about_.show()
