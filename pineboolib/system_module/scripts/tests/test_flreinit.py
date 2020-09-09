"""Test reinit module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa
from pineboolib.plugins.mainform import eneboo
from pineboolib import application


class TestFLReinit(unittest.TestCase):
    """TestFLReinit class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        init_testing()

    def test_basic1(self) -> None:
        """Test reinit function."""

        application.PROJECT.main_window = eneboo.MainForm()
        application.PROJECT.main_window.initScript()

        reinit_func = qsa.from_project("formflreinit").main
        self.assertTrue(reinit_func)
        reinit_func()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
