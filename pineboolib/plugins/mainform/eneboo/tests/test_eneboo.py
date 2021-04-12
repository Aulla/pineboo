"""Test Eneboo module."""

import unittest
from PyQt6 import QtWidgets, QtGui  # type: ignore[import]

from pineboolib.loader.main import init_testing, finish_testing

from pineboolib.core import settings
from pineboolib import application
from . import fixture_path
from pineboolib import logging

from typing import cast

LOGGER = logging.get_logger("eneboo_%s" % __name__)


class TestEnebooGUI(unittest.TestCase):
    """Tes EnebooGUI class."""

    prev_main_window_name: str

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        settings.CONFIG.set_value("application/isDebuggerMode", True)
        settings.CONFIG.set_value("application/dbadmin_enabled", True)
        cls.prev_main_window_name = settings.CONFIG.value(
            "ebcomportamiento/main_form_name", "eneboo"
        )
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", "eneboo")

        init_testing()

    def test_initialize(self) -> None:
        """Test GUI initialize."""

        from pineboolib.qsa import qsa

        from pineboolib.plugins.mainform.eneboo import eneboo
        import os

        if hasattr(application.PROJECT, "main_window"):
            del application.PROJECT.main_window
            application.PROJECT.main_window = None
        # application.PROJECT.main_form = eneboo
        # eneboo.mainWindow = eneboo.MainForm()
        # eneboo.mainWindow.initScript()
        application.PROJECT.main_window = eneboo.MainForm()
        application.PROJECT.main_window.initScript()
        application.PROJECT.main_window.reinitScript()
        # main_window = application.PROJECT.main_form.MainForm()  # type: ignore
        # main_window.initScript()
        self.assertTrue(application.PROJECT.main_window)
        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        application.PROJECT.main_window.triggerAction(
            "triggered():initModule():flfactppal_actiongroup_name"
        )

        self.assertTrue(qsa_sys.loadModules(path, False))

        # application.PROJECT.main_window = application.PROJECT.main_form.mainWindow  # type: ignore
        application.PROJECT.main_window.show()
        self.assertTrue(application.PROJECT.main_window)
        application.PROJECT.main_window.triggerAction(
            "triggered():initModule():sys_actiongroup_name"
        )

        application.PROJECT.main_window.triggerAction("triggered():openDefaultForm():clientes")
        application.PROJECT.main_window.triggerAction(
            "triggered():openDefaultForm():clientes"
        )  # Remove page and show again.

        action = cast(
            QtGui.QAction, application.PROJECT.main_window.findChild(QtGui.QAction, "clientes")
        )
        application.PROJECT.main_window.addMark(action)

        if application.PROJECT.main_window.ag_mar_:
            application.PROJECT.main_window.ag_mar_.removeAction(action)
        application.PROJECT.main_window.dck_mar_.update(application.PROJECT.main_window.ag_mar_)
        doc_widget = QtWidgets.QDockWidget()
        doc_widget.setWidget(QtWidgets.QTreeWidget())
        application.PROJECT.main_window.dck_mar_.initFromWidget(doc_widget)
        application.PROJECT.main_window.dck_mar_.change_state(False)

        application.PROJECT.main_window.removeCurrentPage(0)
        application.PROJECT.main_window.initModule("sys")

        application.PROJECT.main_window.initFromWidget(application.PROJECT.main_window)
        application.PROJECT.main_window.triggerAction("triggered():shConsole():clientes")

        self.assertFalse(
            application.PROJECT.aq_app.getTabWidgetPages("formRecordclientes", "prueba")
        )

        application.PROJECT.aq_app.checkAndFixTransactionLevel("prueba")
        application.PROJECT.aq_app.popupWarn("prueba")

    def test_load_tabs(self) -> None:
        """Ensure load only one tab."""

        main_window = application.PROJECT.main_window

        if main_window is not None:

            key = "MainWindow/%s/" % application.PROJECT.conn_manager.database()
            settings.SETTINGS.set_value(
                "%sopenActions" % key,
                [
                    "flmodules",
                    "flmodules",
                    "flareas",
                    "flmodules",
                    "flusers",
                    "flmodules",
                    "flareas",
                ],
            )
            main_window.loadTabs()
            self.assertEqual(main_window.tab_widget.count(), 3)  # flmodules, flareas, flusers

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure this class is finished correctly."""
        del application.PROJECT.main_window

        settings.CONFIG.set_value("application/isDebuggerMode", False)
        settings.CONFIG.set_value("application/dbadmin_enabled", False)
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", cls.prev_main_window_name)

        finish_testing()
