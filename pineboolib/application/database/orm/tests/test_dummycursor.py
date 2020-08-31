"""Test dummycursor module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestDummyCursor(unittest.TestCase):
    """TestDummyCursor Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic."""

        new_session = qsa.thread_session_new()
        class_area = qsa.orm.flareas
        self.assertTrue(class_area)
        obj_ = class_area()
        obj_.idarea = "M"
        obj_.descripcion = "area M"
        obj_.save()

        fake_cursor = obj_.get_cursor()
        self.assertTrue(fake_cursor)
        fake_cursor.setValueBuffer("descripcion", "area M2")
        self.assertEqual(fake_cursor.valueBuffer("descripcion"), "area M2")
        self.assertEqual(fake_cursor.modeAccess(), 1)
        # fake_cursor.setModeAccess(fake_cursor.Edit)
        # self.assertEqual(fake_cursor.modeAccess(), 1)

        self.assertEqual(fake_cursor.valueBufferCopy("descripcion"), "area M")
        fake_cursor.setValueBufferCopy("descripcion", "area M2")
        self.assertEqual(fake_cursor.valueBufferCopy("descripcion"), "area M2")
        self.assertFalse(fake_cursor.isNull("descripcion"))
        fake_cursor.setNull("descripcion")

    def test_basic_2(self) -> None:
        """Test basic."""

        class_area = qsa.orm.flareas
        self.assertTrue(class_area)
        obj_ = class_area()

        fake_cursor = obj_.cursor

        self.assertTrue(fake_cursor)
        self.assertEqual(fake_cursor.table(), "flareas")
        self.assertEqual(fake_cursor.primaryKey(), "idarea")
        self.assertTrue(fake_cursor.db())
        self.assertTrue(fake_cursor.metadata() is not None)
