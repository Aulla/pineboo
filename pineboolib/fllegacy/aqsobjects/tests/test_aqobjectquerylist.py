"""Aqobjectquerylist module."""

import unittest
import importlib
from pineboolib.loader.main import init_testing, finish_testing


class TestAQObjectQueryList(unittest.TestCase):
    """TestAQObjectQueryList Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_aqobject_query_list(self) -> None:
        """Test AQObjectQueryList function."""
        from pineboolib import application
        from pineboolib.qsa import qsa

        application.project.main_form = importlib.import_module(
            "pineboolib.plugins.mainform.eneboo.eneboo"
        )
        application.project.main_window = getattr(application.project.main_form, "mainWindow", None)
        main_form_ = getattr(application.project.main_form, "MainForm", None)
        self.assertTrue(main_form_)
        main_w = main_form_()
        main_w.initScript()
        main_w.show()

        list_ = qsa.AQObjectQueryList(main_w, "QAction", None, False, True)
        self.assertTrue(len(list_) > 86)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
