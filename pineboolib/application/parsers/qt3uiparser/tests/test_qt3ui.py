"""Test_pnsqlquery module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application


class TestQT3UIParser(unittest.TestCase):
    """TestQT3UIParser Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_mainForm(self) -> None:
        """Test mainForm widget."""
        act_sys = application.project.actions["sys"]
        self.assertTrue(act_sys)
        act_sys.load()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
