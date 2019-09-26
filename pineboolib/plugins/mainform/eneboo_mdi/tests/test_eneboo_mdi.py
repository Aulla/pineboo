"""Test Eneboo module."""

import unittest
import importlib
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from PyQt5 import QtWidgets


class TestEnebooGUI(unittest.TestCase):
    """Tes EnebooGUI class."""

    main_w: QtWidgets.QMainWindow

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_initialize(self) -> None:
        """Test GUI initialize."""
        from pineboolib.fllegacy import flapplication

        project = application.project
        project.main_form = importlib.import_module(
            "pineboolib.plugins.mainform.eneboo_mdi.eneboo_mdi"
        )
        project.main_window = getattr(project.main_form, "mainWindow", None)
        main_form_ = getattr(project.main_form, "MainForm", None)
        self.assertTrue(main_form_)
        self.main_w = main_form_()
        self.main_w.initScript()
        self.main_w.show()
        self.assertTrue(self.main_w)
        flapplication.aqApp.stopTimerIdle()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure this class is finished correctly."""
        del application.project.main_form
        del application.project.main_window
        finish_testing()
