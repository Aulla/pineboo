"""Test_pnbuffer module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.database import pnsqlcursor


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

        if buffer_ is None:
            raise Exception("buffer is empty!.")

        buffer_.prime_update()

        # self.assertEqual(buffer_.value(2), "2019-01-01")
        self.assertEqual(buffer_.value("date_field"), "2019-01-01")
        # self.assertEqual(buffer_.count(), 8)
        # buffer_.clear_buffer()
        # buffer_.prime_update()
        # buffer_.prime_delete()
        # self.assertEqual(buffer_.value(1), None)
        # buffer_.prime_update()
        # buffer_.setRow(0)
        # self.assertEqual(buffer_.row(), 0)
        # self.assertEqual(buffer_.value(1), "Campo texto 1")
        # self.assertEqual(buffer_.setNull(1), True)
        # self.assertEqual(buffer_.value(1), None)
        # time_field_ = buffer_.field("time_field")

        # if time_field_ is None:
        #    raise Exception("time_field_ is empty!.")

        # self.assertEqual(time_field_.generated, True)
        # buffer_.setGenerated(3, False)

        # self.assertEqual(time_field_.generated, False)

        # mtd_field = cursor.metadata().field("time_field")

        # if mtd_field is None:
        #    raise Exception("mtd_field is empty!.")

    # buffer_.setGenerated(mtd_field, True)

    # self.assertEqual(time_field_.generated, True)

    def test_basic2(self) -> None:
        """Basic test 2."""

        # import datetime

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.select()
        cursor.first()

        buffer_ = cursor.buffer()

        if buffer_ is None:
            raise Exception("buffer is empty!.")

        # field_1 = buffer_.field(0)
        # field_2 = buffer_.field(2)

        # if field_1 is None:
        #    raise Exception("field_1 is empty!.")

        # if field_2 is None:
        #    raise Exception("field_2 is empty!.")

        # self.assertEqual(field_1.has_changed(buffer_.value(0)))
        # self.assertFalse(field_2.has_changed(datetime.date(2019, 1, 1)))

        self.assertEqual(buffer_.is_null("string_field"), False)
        self.assertEqual(buffer_.is_null("date_field"), False)
        self.assertEqual(buffer_.is_null("time_field"), False)
        self.assertEqual(buffer_.is_null("bool_field"), False)
        self.assertEqual(buffer_.is_null("double_field"), False)

        # self.assertEqual(buffer_.isEmpty(), False)
        # buffer_.clear_values()
        # self.assertEqual(buffer_.value("string_field"), None)
        # self.assertEqual(buffer_.value("date_field"), None)
        # self.assertEqual(buffer_.value("time_field"), None)
        # self.assertEqual(buffer_.value("bool_field"), None)
        # self.assertEqual(buffer_.value("double_field"), None)
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

        if buffer_ is None:
            raise Exception("buffer is empty!.")

        buffer_.setValue("string_field", "Campo texto 1 mod")
        # self.assertEqual(buffer_.modifiedFields(), ["string_field"])
        # buffer_.setNoModifiedFields()
        # self.assertEqual(buffer_.modifiedFields(), [])
        buffer_.setValue("double_field", 1.02)
        # self.assertEqual(buffer_.modifiedFields(), ["double_field"])
        self.assertEqual(buffer_.value("double_field"), 1.02)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
