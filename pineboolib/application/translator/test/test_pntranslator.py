"""PNTranslator module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.utils import path
from .. import pntranslator


class TestPNTranslator(unittest.TestCase):
    """TestPNTranslator Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic 1."""

        tor = pntranslator.PNTranslator(None, "esp")
        self.assertTrue(tor.load_ts(str(path._path("sys.es.ts"))))
        self.assertEqual(tor.translate("scripts", "single"), "simple!")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
