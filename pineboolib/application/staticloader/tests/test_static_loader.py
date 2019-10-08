"""Test_static_loader module."""

import unittest
from pineboolib.core.settings import config
from pineboolib.loader.main import init_testing, finish_testing


class TestStaticLoader(unittest.TestCase):
    """TestStaticLoader Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        from pineboolib.core.utils.utils_base import filedir

        db_name = "temp_db"
        dirs = [True, filedir("./application/staticloader/tests/fixtures")]
        config.set_value("StaticLoader/%s/enabled" % (db_name), True)  # Para activar carga estática
        config.set_value("StaticLoader/%s/dirs" % db_name, dirs)
        init_testing()

    def test_script_overload(self) -> None:
        """Test script overload loader."""
        from pineboolib import application

        action = application.project.actions["sys"]
        script = application.load_script.load_script("sys.qs", action)
        self.assertEqual(script.FormInternalObj().saluda(), "Hola!")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
        db_name = "temp_db"
        config.set_value(
            "StaticLoader/%s/enabled" % (db_name), False
        )  # Para activar carga estática
        config.set_value("StaticLoader/%s/dirs" % db_name, [])
