"""Test_pncursortablemodel module."""

import unittest
from pineboolib.loader.main import init_testing
from pineboolib.application.database import pnsqlcursor


class TestPNCursorTableModel(unittest.TestCase):
    """TestPNCursorTableModel Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Basic test 1."""

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("string_field", "xxx")
        cursor.setValueBuffer("double_field", 0.02)
        cursor.commitBuffer()
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("string_field", "zzz")
        cursor.setValueBuffer("double_field", 0.01)
        cursor.commitBuffer()
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("string_field", "yyy")
        cursor.setValueBuffer("double_field", 0.03)
        # cursor.setValueBuffer("check_field", True)
        cursor.commitBuffer()

        cursor.setSort("string_field ASC")
        cursor.refresh()
        cursor.last()
        self.assertEqual(cursor.valueBuffer("string_field"), "zzz")
        self.assertEqual(cursor.valueBuffer("double_field"), 0.01)
        cursor.prev()
        self.assertEqual(cursor.valueBuffer("string_field"), "yyy")

    def test_basic_2(self) -> None:
        """Basic test 2."""

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.select()
        cursor.last()
        cursor.refreshBuffer()
        self.assertEqual(cursor.valueBuffer("string_field"), "yyy")

        model = cursor.model()

        self.assertEqual(model.findPKRow([cursor.valueBuffer("id")]), cursor.size() - 1)
        self.assertEqual(model.pK(), "id")
        self.assertEqual(model.fieldType("string_field"), "string")
        self.assertEqual(model.alias("string_field"), "String field")
        self.assertEqual(
            model.field_metadata("string_field"), cursor.metadata().field("string_field")
        )

    def test_basic_3(self) -> None:
        from PyQt5 import QtCore, QtGui
        import locale
        from datetime import date

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.setSort("string_field DESC")
        cursor.select()

        model = cursor.model()

        self.assertEqual(model.data(model.index(0, 1)), "zzz")
        self.assertEqual(model.data(model.index(0, 0)), 5)
        self.assertEqual(model.data(model.index(0, 2)), None)
        self.assertEqual(
            model.data(model.index(0, 4)), QtCore.QLocale.system().toString(float(0.01), "f", 2)
        )
        self.assertEqual(model.data(model.index(0, 5)), "No")
        self.assertEqual(model.data(model.index(1, 1)), "yyy")
        self.assertEqual(model.data(model.index(1, 0)), 6)

        cursor.setSort("string_field DESC, double_field DESC")
        model.sort(0, QtCore.Qt.AscendingOrder)
        self.assertEqual(
            model.data(model.index(0, 5), QtCore.Qt.TextAlignmentRole),
            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter,
        )
        self.assertEqual(
            model.data(model.index(1, 1), QtCore.Qt.TextAlignmentRole), QtCore.Qt.AlignVCenter
        )
        d = date(2019, 1, 1)
        locale.setlocale(locale.LC_TIME, "")
        date_format = locale.nl_langinfo(locale.D_FMT)
        date_format = date_format.replace("y", "Y")  # Año con 4 dígitos
        date_format = date_format.replace("/", "-")  # Separadores
        date_ = d.strftime(date_format)

        self.assertEqual(model.data(model.index(0, 2), QtCore.Qt.DisplayRole), date_)
        self.assertEqual(
            model.data(model.index(0, 4), QtCore.Qt.DisplayRole),
            QtCore.QLocale.system().toString(float(1.01), "f", 2),
        )

        self.assertTrue(
            isinstance(model.data(model.index(0, 7), QtCore.Qt.DecorationRole), QtGui.QPixmap)
        )

    def test_basic_4(self) -> None:
        """Test basic 4."""
        from PyQt5 import QtCore, QtGui

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.setSort("string_field DESC")
        cursor.select()

        model = cursor.model()
        self.assertTrue(
            isinstance(model.data(model.index(0, 5), QtCore.Qt.BackgroundRole), QtGui.QBrush)
        )
        self.assertTrue(
            isinstance(model.data(model.index(0, 5), QtCore.Qt.ForegroundRole), QtGui.QBrush)
        )

        model.updateRows()
        self.assertFalse(model.findCKRow([]))
        self.assertFalse(model.findCKRow([2, 2]))
        self.assertFalse(model.findPKRow([21]))
        self.assertEqual(model.findPKRow([3]), 3)
