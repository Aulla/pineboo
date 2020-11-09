"""Test Eneboo module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application

from pineboolib.core import settings

# from . import fixture_path


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
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", "eneboo_mdi")

        init_testing()

    def test_initialize(self) -> None:
        """Test GUI initialize."""
        # from pineboolib.qsa import qsa
        from pineboolib.plugins.mainform.eneboo_mdi import eneboo_mdi

        # import os

        # application.PROJECT.main_form = eneboo_mdi
        # eneboo_mdi.mainWindow = eneboo_mdi.MainForm()
        # eneboo_mdi.mainWindow.initScript()

        application.PROJECT.main_window = eneboo_mdi.MainForm()
        self.assertTrue(application.PROJECT.main_window)
        application.PROJECT.main_window.initScript()

        # qsa_sys = qsa.sys
        # path = fixture_path("principal.eneboopkg")
        # self.assertTrue(os.path.exists(path))
        # qsa_sys.loadModules(path, False)
        # application.PROJECT.main_window = application.PROJECT.main_form.mainWindow  # type: ignore
        self.assertTrue(application.PROJECT.main_window)
        if application.PROJECT.main_window:
            application.PROJECT.main_window.initToolBar()
            application.PROJECT.main_window.windowMenuAboutToShow()
            application.PROJECT.main_window.show()
            application.PROJECT.main_window.activateModule("sys")
            # if application.PROJECT.main_window._p_work_space is not None:
            #    for window in application.PROJECT.main_window._p_work_space.subWindowList():

            self.assertFalse(application.PROJECT.main_window.existFormInMDI("flusers"))
            application.PROJECT.actions["flusers"].openDefaultForm()
            application.PROJECT.main_window.windowMenuAboutToShow()
            application.PROJECT.main_window.windowMenuActivated(0)
            self.assertTrue(application.PROJECT.main_window.existFormInMDI("flusers"))
            application.PROJECT.main_window.writeState()
            application.PROJECT.main_window.writeStateModule()
            application.PROJECT.main_window.toggleToolBar(True)
            application.PROJECT.main_window.toggleStatusBar(True)
            application.PROJECT.main_window.windowClose()

            application.PROJECT.main_window.generalExit(False)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure this class is finished correctly."""

        del application.PROJECT.main_window

        settings.CONFIG.set_value("application/isDebuggerMode", False)
        settings.CONFIG.set_value("application/dbadmin_enabled", False)
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", cls.prev_main_window_name)

        finish_testing()
