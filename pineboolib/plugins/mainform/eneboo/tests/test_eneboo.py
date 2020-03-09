"""Test Eneboo module."""

import unittest
from PyQt5 import QtWidgets

from pineboolib.loader.main import init_testing, finish_testing

from pineboolib.core import settings
from pineboolib import application
from . import fixture_path
from pineboolib import logging

logger = logging.getLogger("eneboo_%s" % __name__)


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

        application.PROJECT.main_form = eneboo
        eneboo.mainWindow = eneboo.MainForm()
        eneboo.mainWindow.initScript()
        application.PROJECT.main_window = eneboo.mainWindow

        # main_window = application.PROJECT.main_form.MainForm()  # type: ignore
        # main_window.initScript()

        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        application.PROJECT.main_window.triggerAction(
            "triggered():initModule():flfactppal_actiongroup_name"
        )
        qsa_sys.loadModules(path, False)

        application.PROJECT.main_window = application.PROJECT.main_form.mainWindow  # type: ignore
        application.PROJECT.main_window.show()
        self.assertTrue(application.PROJECT.main_window)
        application.PROJECT.main_window.triggerAction(
            "triggered():initModule():sys_actiongroup_name"
        )
        # self.assertTrue(False)
        application.PROJECT.main_window.triggerAction("triggered():openDefaultForm():clientes")
        application.PROJECT.main_window.triggerAction(
            "triggered():openDefaultForm():clientes"
        )  # Remove page and show again.
        ac = application.PROJECT.main_window.findChild(QtWidgets.QAction, "clientes")
        application.PROJECT.main_window.addMark(ac)

        application.PROJECT.main_window.ag_mar_.removeAction(ac)
        application.PROJECT.main_window.dck_mar_.update(application.PROJECT.main_window.ag_mar_)
        w = QtWidgets.QDockWidget()
        w.setWidget(QtWidgets.QTreeWidget())
        application.PROJECT.main_window.dck_mar_.initFromWidget(w)
        application.PROJECT.main_window.dck_mar_.change_state(False)

        application.PROJECT.main_window.removeCurrentPage(0)
        application.PROJECT.main_window.initModule("sys")

        application.PROJECT.main_window.initFromWidget(application.PROJECT.main_window)
        application.PROJECT.main_window.triggerAction("triggered():shConsole():clientes")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure this class is finished correctly."""
        del application.PROJECT.main_form
        del application.PROJECT.main_window

        settings.CONFIG.set_value("application/isDebuggerMode", False)
        settings.CONFIG.set_value("application/dbadmin_enabled", False)
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", cls.prev_main_window_name)

        finish_testing()
