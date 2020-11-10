"""Test_static_loader module."""

import unittest
import os
from pineboolib.core import settings
from pineboolib.loader.main import init_testing, finish_testing
from . import fixture_path


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

        action = application.PROJECT.actions["sys"]
        script = application.load_script.load_script("sys.qs", action)
        self.assertEqual(script.saluda(), "Hola!")  # type: ignore [operator] # noqa: F821

    def test_static_loader(self) -> None:
        """Test script overloaded again."""
        from pineboolib.qsa import qsa

        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa.sys.loadModules(path, False))
        cursor = qsa.FLSqlCursor("flfiles")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("nombre", "clientes_model.py")
        cursor.setValueBuffer("idmodulo", "flfactppal")
        cursor.setValueBuffer("contenido", " ")
        cursor.setValueBuffer("sha", qsa.util.sha1(" "))
        self.assertTrue(cursor.commitBuffer())
        qsa.sys.reinit()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
        db_name = "temp_db"
        settings.CONFIG.set_value(
            "StaticLoader/%s/enabled" % (db_name), False
        )  # Para activar carga estática
        settings.CONFIG.set_value("StaticLoader/%s/dirs" % db_name, [])
