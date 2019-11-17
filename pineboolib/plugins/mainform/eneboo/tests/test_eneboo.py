"""Test Eneboo module."""

import unittest
from PyQt5 import QtWidgets

from pineboolib.loader.main import init_testing, finish_testing

from pineboolib.core.settings import config
from pineboolib import application
from . import fixture_path
from pineboolib import logging

logger = logging.getLogger("eneboo_%s" % __name__)


class TestEnebooGUI(unittest.TestCase):
    """Tes EnebooGUI class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        config.set_value("application/isDebuggerMode", True)
        config.set_value("application/dbadmin_enabled", True)
        cls.prev_main_window_name = config.value("ebcomportamiento/main_form_name", "eneboo")
        config.set_value("ebcomportamiento/main_form_name", "eneboo")

        init_testing()

    def test_initialize(self) -> None:
        """Test GUI initialize."""

        from pineboolib.qsa import qsa

        from pineboolib.plugins.mainform.eneboo import eneboo
        import os

        application.project.main_form = eneboo
        eneboo.mainWindow = eneboo.MainForm()
        eneboo.mainWindow.initScript()
        application.project.main_window = eneboo.mainWindow

        # main_window = application.project.main_form.MainForm()  # type: ignore
        # main_window.initScript()

        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        application.project.main_window.triggerAction(
            "triggered():initModule():flfactppal_actiongroup_name"
        )
        qsa_sys.loadModules(path, False)

        application.project.main_window = application.project.main_form.mainWindow  # type: ignore
        application.project.main_window.show()
        self.assertTrue(application.project.main_window)
        application.project.main_window.triggerAction(
            "triggered():initModule():sys_actiongroup_name"
        )
        # self.assertTrue(False)
        application.project.main_window.triggerAction("triggered():openDefaultForm():clientes")
        application.project.main_window.triggerAction(
            "triggered():openDefaultForm():clientes"
        )  # Remove page and show again.
        ac = application.project.main_window.findChild(QtWidgets.QAction, "clientes")
        application.project.main_window.addMark(ac)

        application.project.main_window.ag_mar_.removeAction(ac)
        application.project.main_window.dck_mar_.update(application.project.main_window.ag_mar_)
        w = QtWidgets.QDockWidget()
        w.setWidget(QtWidgets.QTreeWidget())
        application.project.main_window.dck_mar_.initFromWidget(w)
        application.project.main_window.dck_mar_.change_state(False)

        application.project.main_window.removeCurrentPage(0)
        application.project.main_window.initModule("sys")

        application.project.main_window.initFromWidget(application.project.main_window)
        application.project.main_window.triggerAction("triggered():shConsole():clientes")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure this class is finished correctly."""
        del application.project.main_form
        del application.project.main_window

        config.set_value("application/isDebuggerMode", False)
        config.set_value("application/dbadmin_enabled", False)
        config.set_value("ebcomportamiento/main_form_name", cls.prev_main_window_name)

        finish_testing()
