"""Test_static_loader module."""

import unittest
from pineboolib.core import settings
from pineboolib.loader.main import init_testing, finish_testing
from PyQt5 import QtWidgets


class TestStaticLoader(unittest.TestCase):
    """TestStaticLoader Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        from pineboolib.core.utils.utils_base import filedir

        db_name = "temp_db"
        dirs = [True, filedir("./application/staticloader/tests/fixtures")]
        settings.CONFIG.set_value(
            "StaticLoader/%s/enabled" % (db_name), True
        )  # Para activar carga estática
        settings.CONFIG.set_value("StaticLoader/%s/dirs" % db_name, dirs)
        init_testing()

    def test_script_overload(self) -> None:
        """Test script overload loader."""
        from pineboolib.qsa import qsa
        from pineboolib import application

        self.assertEqual(qsa.from_project("sys").saluda(), "Hola!")
        self.assertTrue(
            "sys" in application.PROJECT.actions.keys(),
            "Los actions disponibles son %s" % application.PROJECT.actions.keys(),
        )

        while qsa.aqApp._inicializing:
            QtWidgets.QApplication.processEvents()

        action = application.PROJECT.actions["sys"]
        script = application.load_script.load_script("sys.qs", action)
        self.assertEqual(script.form.saluda(), "Hola!")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
        db_name = "temp_db"
        settings.CONFIG.set_value(
            "StaticLoader/%s/enabled" % (db_name), False
        )  # Para activar carga estática
        settings.CONFIG.set_value("StaticLoader/%s/dirs" % db_name, [])
