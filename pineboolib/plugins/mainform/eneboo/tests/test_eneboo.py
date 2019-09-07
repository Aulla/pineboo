"""Test Eneboo module."""

import unittest
import importlib
from pineboolib.loader.main import init_testing
from pineboolib import application


class TestEnebooGUI(unittest.TestCase):
    """Tes EnebooGUI class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_initialize(self) -> None:
        """Test GUI initialize."""

        project = application.project
        project.main_form = importlib.import_module("pineboolib.plugins.mainform.eneboo.eneboo")
        project.main_window = getattr(project.main_form, "mainWindow", None)
        main_form_ = getattr(project.main_form, "MainForm", None)
        self.assertTrue(main_form_)
        main_w = main_form_()
        main_w.initScript()
        main_w.show()
        self.assertTrue(main_w)
