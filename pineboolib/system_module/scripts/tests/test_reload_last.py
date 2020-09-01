"""Test reloadlast module."""


import unittest
from pineboolib.loader.main import init_testing, finish_testing

from pineboolib import application
from pineboolib.qsa import qsa
from pineboolib.core.utils import utils_base
from pineboolib.core import settings


class TestFLReloadLast(unittest.TestCase):
    """TestFlReloadLast class."""

    prev_main_window_name: str

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        settings.CONFIG.set_value("application/isDebuggerMode", True)
        settings.CONFIG.set_value("application/dbadmin_enabled", True)
        cls.prev_main_window_name = settings.CONFIG.value(
            "ebcomportamiento/main_form_name", "eneboo"
        )
        settings.CONFIG.set_value("ebcomportamiento/main_form_name", "eneboo")

        init_testing()

    def test_main(self) -> None:
        """Test main."""

        from pineboolib.plugins.mainform import eneboo

        application.PROJECT.main_window = eneboo.MainForm()
        application.PROJECT.main_window.initScript()

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

        settings.CONFIG.set_value("ebcomportamiento/main_form_name", cls.prev_main_window_name)
        finish_testing()
