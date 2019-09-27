"""Dgi_qt module."""
# # -*- coding: utf-8 -*-
from importlib import import_module

from PyQt5 import QtWidgets, QtCore, QtGui, Qt, QtXml  # type: ignore

from pineboolib import logging
from pineboolib.plugins.dgi.dgi_schema import dgi_schema
from pineboolib.application.parsers.qt3uiparser import dgi_qt3ui
from .dgi_objects.splash_screen import splashscreen
from .dgi_objects.progress_dialog_manager import ProgressDialogManager
from .dgi_objects.status_help_msg import StatusHelpMsg
from typing import Any, Optional

logger = logging.getLogger(__name__)


class dgi_qt(dgi_schema):
    """dgi_qt class."""

    pnqt3ui: Any
    splash: Any
    progress_dialog_manager: Any

    def __init__(self):
        """Inicialize."""
        super(dgi_qt, self).__init__()  # desktopEnabled y mlDefault a True
        self._name = "qt"
        self._alias = "Qt5"

        self.pnqt3ui = dgi_qt3ui
        self.splash = splashscreen()
        self.progress_dialog_manager = ProgressDialogManager()
        self.status_help_msg = StatusHelpMsg()

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

    def msgBoxWarning(self, t: str, parent: Optional[Any] = None) -> None:
        """Show a message box warning."""
        from PyQt5.QtWidgets import qApp  # type: ignore
        from pineboolib.q3widgets.messagebox import MessageBox

        if parent is None:
            parent = (
                qApp.focusWidget().parent()
                if hasattr(qApp.focusWidget(), "parent")
                else qApp.activeWindow()
            )

        logger.warning("%s", t)

        if parent is not None:
            MessageBox.warning(
                t, MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton, "Pineboo", parent
            )

    def about_pineboo(self) -> None:
        """Show about pineboo dialog."""
        from .dgi_objects.dlg_about.about_pineboo import AboutPineboo

        about_ = AboutPineboo()
        about_.show()
