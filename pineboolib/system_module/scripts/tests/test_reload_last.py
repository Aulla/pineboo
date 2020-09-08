"""Test reloadlast module."""


import unittest
import os
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.qsa import qsa
from pineboolib.core.utils import utils_base
from pineboolib.core import settings

from . import fixture_path


class TestFLReloadLast(unittest.TestCase):
    """TestFlReloadLast class."""

    prev_main_window_name: str
    prev_reload_last: str

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        settings.CONFIG.set_value("application/isDebuggerMode", True)
        settings.CONFIG.set_value("application/dbadmin_enabled", True)
        cls.prev_main_window_name = settings.CONFIG.value(
            "ebcomportamiento/main_form_name", "eneboo"
        )
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", "eneboo")
        cls.prev_reload_last = settings.CONFIG.value("scripts/sys/modLastModule_temp_db", False)

        init_testing()

    def test_main(self) -> None:
        """Test main."""

        from pineboolib.plugins.mainform import eneboo
        from pineboolib.qsa import qsa

        application.PROJECT.main_window = eneboo.MainForm()
        application.PROJECT.main_window.initScript()

        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa.sys.loadModules(path, False))
        cursor = qsa.FLSqlCursor("flmodules")
        cursor.select("idmodulo = 'flfactppal'")
        self.assertTrue(cursor.first())
        cursor.editRecord(False)
        self.assertEqual(cursor.size(), 1)
        form = qsa.from_project("formRecordflmodules").formRecordWidget()
        self.assertTrue(form)
        form.child("lineas").cursor().select()
        self.assertTrue(fixture_path("."))
        self.assertTrue(form.exportarADisco)
        form.exportarADisco(fixture_path("."))
        for root, dirs, files in os.walk(fixture_path("."), topdown=False):
            print("*", root, dirs, files)

        # ruta = fixture_path("principal")
        # self.assertTrue(os.path.exists(ruta))
        # qsa.from_project("formRecordflmodules").iface.exportarADisco(fixture_path("."))
        # ruta = fixture_path("principal")
        # self.assertTrue(os.path.exists(ruta))
        # settings.CONFIG.set_value("scripts/sys/modLastModule_temp_db", ruta)

        # mod_ = qsa.from_project("formflreloadlast")
        # mod_.main()

    def test_comparar_versiones(self) -> None:
        """Test comparar_versiones."""

        mod_ = qsa.from_project("formflreloadlast")
        self.assertTrue(mod_)
        self.assertEqual(mod_.compararVersiones("1.0", "1.1"), 2)
        self.assertEqual(mod_.compararVersiones("1.0", "0.1"), 1)
        self.assertEqual(mod_.compararVersiones("2.1", "2.1"), 0)

    def test_traducir_cadena(self) -> None:
        """Test traducir cadena."""

        mod_ = qsa.from_project("formflreloadlast")
        tr_dir = utils_base.filedir(utils_base.get_base_dir(), "system_module")
        self.assertEqual(mod_.traducirCadena("unodostres", tr_dir, "sys"), "unodostres")
        self.assertEqual(
            mod_.traducirCadena(
                "QT_TRANSLATE_NOOP('FLWidgetApplication','undostres')", tr_dir, "sys"
            ),
            "undostres",
        )

    def test_dame_valor(self) -> None:
        """Test dame valor."""

        mod_ = qsa.from_project("formflreloadlast")
        self.assertEqual(mod_.dameValor("unodostres"), "unodostres")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        settings.CONFIG.set_value("scripts/sys/modLastModule_temp_db", cls.prev_reload_last)
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", cls.prev_main_window_name)
        finish_testing()
