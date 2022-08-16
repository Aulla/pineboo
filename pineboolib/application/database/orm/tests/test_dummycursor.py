"""Test dummycursor module."""

import datetime
import unittest

from pineboolib.loader.main import init_testing
from pineboolib.qsa import qsa


class TestDummyCursor(unittest.TestCase):
    """TestDummyCursor Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic."""

        qsa.thread_session_new()
        class_area = qsa.orm.flareas
        self.assertTrue(class_area)
        obj_ = class_area()
        fake_cursor_empty = obj_.get_cursor()
        obj_.idarea = "M"
        obj_.descripcion = "area M"
        obj_.save()

        self.assertFalse(fake_cursor_empty.isModifiedBuffer(), obj_.changes())

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

        self.assertTrue(fake_cursor.isModifiedBuffer())

    def test_basic_2(self) -> None:
        """Test basic 2."""

        class_area = qsa.orm.flareas
        self.assertTrue(class_area)
        obj_ = class_area()

        fake_cursor = obj_.cursor

        self.assertTrue(fake_cursor)
        self.assertEqual(fake_cursor.table(), "flareas")
        self.assertEqual(fake_cursor.primaryKey(), "idarea")
        self.assertTrue(fake_cursor.db())
        self.assertTrue(fake_cursor.metadata() is not None)

    def test_basic_3(self) -> None:
        """Test basic 3."""

        class_area = qsa.orm.flareas
        self.assertTrue(class_area)
        obj_ = class_area()

        fake_cursor = obj_.cursor

        self.assertTrue(fake_cursor)
        self.assertEqual(fake_cursor.action(), "flareas")
        self.assertTrue(fake_cursor.action() == "flareas")

    def test_basic_4(self) -> None:
        """Test basic 4."""

        class_fltest2 = qsa.orm.fltest2
        self.assertTrue(class_fltest2)

        obj_ = class_fltest2()

        fake_cursor = obj_.cursor
        fake_cursor.setValueBuffer("date_field", "2000-01-01")
        self.assertTrue(isinstance(fake_cursor.valueBuffer("date_field"), qsa.Date))
        fake_cursor.setValueBuffer("date_field", datetime.datetime.now())
        self.assertTrue(isinstance(fake_cursor.valueBuffer("date_field"), qsa.Date))
        fake_cursor.setValueBuffer("time_field", "08:00:01")
        self.assertTrue(isinstance(fake_cursor.valueBuffer("time_field"), str))
        now_qsa_date = qsa.Date()
        fake_cursor.setValueBuffer("date_field", now_qsa_date)
        self.assertEqual(str(now_qsa_date)[0:10], str(fake_cursor.valueBuffer("date_field"))[0:10])

        self.assertTrue(fake_cursor.isValid())
