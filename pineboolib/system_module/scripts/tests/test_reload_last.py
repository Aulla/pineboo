"""Test reloadlast module."""


import unittest
from pineboolib.loader.main import init_testing, finish_testing

from pineboolib.qsa import qsa
from pineboolib import application
from pineboolib.core.utils import utils_base


class TestFlModules(unittest.TestCase):
    """TestFlModules class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

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
        print("**", tr_dir)
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
        finish_testing()
