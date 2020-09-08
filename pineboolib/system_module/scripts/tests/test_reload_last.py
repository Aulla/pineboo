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
        form_record = qsa.from_project("formRecordflmodules")
        form_record.child(u"lineas").cursor().first()
        form_record.exportarADisco(fixture_path("."))
        ruta = fixture_path("principal")
        self.assertTrue(os.path.exists(ruta))
        settings.CONFIG.set_value("scripts/sys/modLastModule_temp_db", ruta)

        mod_ = qsa.from_project("formflreloadlast")
        mod_.main()

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
