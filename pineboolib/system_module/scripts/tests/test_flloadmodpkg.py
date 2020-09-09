"""Test loadmodpkg module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestFLLoadModPkg(unittest.TestCase):
    """TestFLLoadModPkg class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        init_testing()

    def test_basic1(self) -> None:
        """Test loadmodpkg main function."""

        _func = qsa.from_project("formflloadmodpkg").main
        self.assertTrue(_func)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
