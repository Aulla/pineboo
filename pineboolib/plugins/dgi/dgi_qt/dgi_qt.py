# # -*- coding: utf-8 -*-
from importlib import import_module

from PyQt5 import QtWidgets, QtCore, QtGui, Qt, QtXml  # type: ignore

from pineboolib import logging
from pineboolib.plugins.dgi.dgi_schema import dgi_schema


logger = logging.getLogger(__name__)


class dgi_qt(dgi_schema):

    pnqt3ui = None
    splash = None
    progress_dialog_mng = None

    def __init__(self):
        super(dgi_qt, self).__init__()  # desktopEnabled y mlDefault a True
        self._name = "qt"
        self._alias = "Qt5"

        from pineboolib.application.parsers.qt3uiparser import dgi_qt3ui
        from .dgi_objects.splash_screen import splashscreen
        from .dgi_objects.progress_dialog_manager import ProgressDialogManager
        from .dgi_objects.status_help_msg import StatusHelpMsg

        self.pnqt3ui = dgi_qt3ui
        self.splash = splashscreen()
        self.progress_dialog_manager = ProgressDialogManager()
        self.status_help_msg = StatusHelpMsg()

    def __getattr__(self, name):

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

    def msgBoxWarning(self, t):
        from PyQt5.QtWidgets import qApp  # type: ignore
        from pineboolib.qt3_widgets.messagebox import MessageBox

        parent = (
            qApp.focusWidget().parent()
            if hasattr(qApp.focusWidget(), "parent")
            else qApp.focusWidget()
        )
        MessageBox.warning(
            t, MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton, "Pineboo", parent
        )

    def about_pineboo(self):
        from .dgi_objects.dlg_about.about_pineboo import AboutPineboo

        about_ = AboutPineboo()
        about_.show()
