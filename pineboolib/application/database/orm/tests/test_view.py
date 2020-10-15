"""Test view module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestView(unittest.TestCase):
    """TestView Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic1(self) -> None:
        """Test  basic view function."""

        cursor_view = qsa.FLSqlCursor("fltest2")
        cursor_view.select()
        self.assertEqual(cursor_view.size(), 0)

        cursor = qsa.FLSqlCursor("fltest")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("string_field", "prueba1")
        self.assertTrue(cursor.commitBuffer())

        cursor_view.select()
        self.assertEqual(cursor_view.size(), 1)
        self.assertTrue(cursor_view.first())
        self.assertEqual(cursor_view.valueBuffer("string_field"), "prueba1")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
