"""Test Eneboo module."""

from PyQt5 import QtWidgets

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application

from pineboolib.core.settings import config
from . import fixture_path


class TestEnebooGUI(unittest.TestCase):
    """Tes EnebooGUI class."""

    main_w: QtWidgets.QMainWindow

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        config.set_value("application/isDebuggerMode", True)
        config.set_value("application/dbadmin_enabled", True)

        init_testing()

    def test_initialize(self) -> None:
        """Test GUI initialize."""
        from pineboolib.qsa import qsa
        from pineboolib.plugins.mainform.eneboo_mdi import eneboo_mdi

        import os

        application.project.main_form = eneboo_mdi
        eneboo_mdi.mainWindow = eneboo_mdi.MainForm()
        eneboo_mdi.mainWindow.initScript()
        application.project.main_window = eneboo_mdi.mainWindow

        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        qsa_sys.loadModules(path, False)
        self.main_w = application.project.main_window
        self.assertTrue(self.main_w)

        self.main_w.initToolBar()
        self.main_w.windowMenuAboutToShow()
        self.main_w.activateModule("sys")
        self.assertFalse(self.main_w.existFormInMDI("flusers"))
        application.project.actions["flusers"].openDefaultForm()
        self.main_w.windowMenuAboutToShow()
        self.main_w.windowMenuActivated(0)
        self.assertTrue(self.main_w.existFormInMDI("flusers"))
        self.main_w.writeState()
        self.main_w.writeStateModule()
        self.main_w.toggleToolBar(True)
        self.main_w.toggleStatusBar(True)
        self.main_w.windowClose()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure this class is finished correctly."""
        del application.project.main_form
        del application.project.main_window

        config.set_value("application/isDebuggerMode", False)
        config.set_value("application/dbadmin_enabled", False)

        finish_testing()
