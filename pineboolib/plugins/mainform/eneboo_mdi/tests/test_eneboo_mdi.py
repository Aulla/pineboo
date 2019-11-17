"""Test Eneboo module."""

from PyQt5 import QtWidgets

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application

from pineboolib.core.settings import config
from . import fixture_path


class TestEnebooGUI(unittest.TestCase):
    """Tes EnebooGUI class."""

    prev_main_window_name: str

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        config.set_value("application/isDebuggerMode", True)
        config.set_value("application/dbadmin_enabled", True)
        cls.prev_main_window_name = config.value("ebcomportamiento/main_form_name", "eneboo")
        config.set_value("ebcomportamiento/main_form_name", "eneboo_mdi")

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
        application.project.main_window = application.project.main_form.mainWindow
        self.assertTrue(application.project.main_window)

        application.project.main_window.initToolBar()
        application.project.main_window.windowMenuAboutToShow()
        application.project.main_window.show()
        application.project.main_window.activateModule("sys")
        for window in application.project.main_window._p_work_space.subWindowList():
            window.close()

        self.assertFalse(application.project.main_window.existFormInMDI("flusers"))
        application.project.actions["flusers"].openDefaultForm()
        application.project.main_window.windowMenuAboutToShow()
        application.project.main_window.windowMenuActivated(0)
        self.assertTrue(application.project.main_window.existFormInMDI("flusers"))
        application.project.main_window.writeState()
        application.project.main_window.writeStateModule()
        application.project.main_window.toggleToolBar(True)
        application.project.main_window.toggleStatusBar(True)
        application.project.main_window.windowClose()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure this class is finished correctly."""
        del application.project.main_form
        del application.project.main_window

        config.set_value("application/isDebuggerMode", False)
        config.set_value("application/dbadmin_enabled", False)
        config.set_value("ebcomportamiento/main_form_name", cls.prev_main_window_name)

        finish_testing()
