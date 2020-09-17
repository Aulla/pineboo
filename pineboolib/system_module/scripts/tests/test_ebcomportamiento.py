"""Test_ebcomportamiento module."""


import unittest
from pineboolib.loader.main import init_testing, finish_testing

from pineboolib.core.utils import utils_base
from pineboolib import application


class TestEBComportamiento(unittest.TestCase):
    """TestFLFormsearchDB Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        utils_base.FORCE_DESKTOP = True
        init_testing()

    def test_basic(self) -> None:
        """Test flformrecord cursor assignment"""

        from pineboolib.qsa import qsa
        from pineboolib.plugins.mainform import eneboo

        application.PROJECT.main_window = eneboo.MainForm()
        application.PROJECT.main_window.initScript()

        func_ = qsa.from_project("formebcomportamiento").main
        self.assertTrue(func_)
        func_()
        func2_ = qsa.from_project("formebcomportamiento").guardar_clicked
        self.assertTrue(func2_)
        func2_()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
