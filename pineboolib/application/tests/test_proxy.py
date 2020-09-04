"""Test_proxy module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing

from pineboolib.qsa import qsa


class TestProxy(unittest.TestCase):
    """TestProcess Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_duplicate(self) -> None:
        """Test Duplicate."""

        module_1 = qsa.from_project("formflareas")
        module_2 = qsa.from_project("formflareas")
        self.assertEqual(module_1.iface, module_2.iface)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
