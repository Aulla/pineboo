"""Test_pnbuffer module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.database import pnsqlcursor, pnsqlquery


class TestPNBuffer(unittest.TestCase):
    """TestPNBuffer Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Basic test."""
        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("string_field", "Campo texto 1")
        cursor.setValueBuffer("date_field", "2019-01-01")
        cursor.setValueBuffer("time_field", "01:01:01")
        cursor.setValueBuffer("bool_field", False)
        cursor.setValueBuffer("double_field", 1.01)
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("string_field", "Campo texto 2")
        cursor.setValueBuffer("date_field", "2019-02-02T00:00:00")
        cursor.setValueBuffer("time_field", "02:02:02.1234")
        cursor.setValueBuffer("bool_field", "true")
        cursor.setValueBuffer("double_field", 2.02)
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("string_field", "Campo texto 3")
        cursor.setValueBuffer("date_field", "2019-03-03")
        cursor.setValueBuffer("time_field", "2019-03-03T03:03:03 +2")
        cursor.setValueBuffer("bool_field", "false")
        cursor.setValueBuffer("double_field", 3.03)
        self.assertTrue(cursor.commitBuffer())

    def test_basic1(self) -> None:
        """Basic test 1."""

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.select()
        self.assertEqual(cursor.size(), 3)
        self.assertTrue(cursor.first())

        buffer_ = cursor.buffer()
        self.assertTrue(buffer_ is not None)
        if buffer_ is not None:
            buffer_.prime_update()

            self.assertEqual(buffer_.value("date_field"), "2019-01-01")
            self.assertEqual(buffer_.value("time_field"), "01:01:01")

        self.assertEqual(cursor.valueBuffer("date_field"), "2019-01-01")

        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect("date_field, time_field")
        qry.setFrom("fltest")
        qry.setWhere("1 = 1")
        qry.setOrderBy("string_field ASC")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        self.assertEqual(qry.value(0), "2019-01-01T00:00:00")
        self.assertEqual(qry.value(1), "01:01:01")
        self.assertTrue(qry.next())
        self.assertEqual(qry.value(1), "02:02:02")
        self.assertTrue(qry.next())
        self.assertEqual(qry.value(1), "03:03:03")
        self.assertEqual(qry.value(0), "2019-03-03T00:00:00")

    def test_basic2(self) -> None:
        """Basic test 2."""

        # import datetime

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.select()
        cursor.first()

        buffer_ = cursor.buffer()
        self.assertTrue(buffer_ is not None)
        if buffer_ is not None:
            self.assertEqual(buffer_.is_null("string_field"), False)
            self.assertEqual(buffer_.is_null("date_field"), False)
            self.assertEqual(buffer_.is_null("time_field"), False)
            self.assertEqual(buffer_.is_null("bool_field"), False)
            self.assertEqual(buffer_.is_null("double_field"), False)

            buffer_.prime_update()

            self.assertEqual(buffer_.value("string_field"), "Campo texto 1")
            self.assertEqual(buffer_.value("double_field"), 1.01)
            self.assertEqual(buffer_.value("date_field"), "2019-01-01")
            self.assertEqual(buffer_.value("time_field"), "01:01:01")
            self.assertEqual(buffer_.value("bool_field"), False)

    def test_basic3(self) -> None:
        """Basic test 3."""

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.select()
        cursor.first()

        buffer_ = cursor.buffer()
        self.assertTrue(buffer_ is not None)

        if buffer_ is not None:

            buffer_.set_value("string_field", "Campo texto 1 mod")
            buffer_.set_value("double_field", 1.02)
            self.assertEqual(buffer_.value("double_field"), 1.02)

    def test_null(self) -> None:
        """Test null."""

        cursor_1 = pnsqlcursor.PNSqlCursor("fltest")
        cursor_1.setModeAccess(cursor_1.Insert)
        cursor_1.refreshBuffer()
        self.assertFalse(cursor_1.isNull("id"))
        self.assertEqual(cursor_1.buffer().value("uint_field"), None)
        self.assertTrue(cursor_1.isNull("string_field"))
        self.assertFalse(cursor_1.isNull("double_field"))  # default 0

        cursor_1.setNull("double_field")
        self.assertEqual(cursor_1.buffer().value("double_field"), None)
        self.assertTrue(cursor_1.isNull("double_field"))

        self.assertEqual(cursor_1.valueBuffer("uint_field"), 0)
        self.assertEqual(cursor_1.buffer().value("uint_field"), None)

        cursor_2 = pnsqlcursor.PNSqlCursor("fltest5")
        cursor_2.setModeAccess(cursor_2.Insert)
        cursor_2.refreshBuffer()
        self.assertTrue(cursor_2.isNull("unit_field"))
        self.assertTrue(cursor_2.isNull("uint_field"))
        self.assertEqual(cursor_2.valueBuffer("uint_field"), 0)
        self.assertEqual(cursor_2.buffer().value("uint_field"), None)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
