"""Test mrproper module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa
from pineboolib.plugins.mainform import eneboo
from pineboolib import application


class TestFLMrProper(unittest.TestCase):
    """TestFLMrProper class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        init_testing()

    def test_basic1(self) -> None:
        """Test mrproper function."""

        application.PROJECT.main_window = eneboo.MainForm()
        application.PROJECT.main_window.initScript()

        _func = qsa.from_project("formflmrproper").main
        self.assertTrue(_func)
        _func()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
