"""
Tests for Class on qsa.
"""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestClass(unittest.TestCase):
    """Test Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test basic."""

        class_ = qsa.class_.Prueba
        self.assertEqual(qsa.class_.classes(), ["Prueba"])
        self.assertTrue(class_)
        self.assertEqual(class_.__name__, "Prueba")
        self.assertNotEqual(class_(), class_())

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
