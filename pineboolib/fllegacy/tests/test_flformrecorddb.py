"""Test_flformrecorddb module."""

import unittest
from pineboolib.loader.main import init_testing


class TestFLFormrecordCursor(unittest.TestCase):
    """TestFLFormrecordCursor Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_cursor_asignment(self) -> None:
        """Test flformrecord cursor assignment"""

        from pineboolib.qsa import dictmodules
        from pineboolib.application.database import pnsqlcursor

        cursor_1 = pnsqlcursor.PNSqlCursor("flareas")
        cursor_1.select()
        cursor_1.setModeAccess(cursor_1.Insert)
        cursor_1.refreshBuffer()
        cursor_1.insertRecord(False)

        cursor_3 = pnsqlcursor.PNSqlCursor("flareas")

        module_ = dictmodules.from_project("formRecordflareas")
        self.assertTrue(module_)
        cursor_2 = module_.cursor()

        self.assertNotEqual(cursor_1, cursor_3)
        self.assertEqual(cursor_1, cursor_2)

    def test_flformrecord_show_again(self) -> None:
        """Check if a FLformRecordDB is shown again"""
        from pineboolib.qsa import dictmodules

        module_ = dictmodules.from_project("formRecordflusers")
        cursor = module_.widget.cursor()
        self.assertFalse(module_.form.showed)
        cursor.insertRecord(False)
        self.assertTrue(module_.form.showed)
        module_.form.close()
        self.assertFalse(module_.form.showed)


if __name__ == "__main__":
    unittest.main()
