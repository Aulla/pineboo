"""Test_pncursortablemodel module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
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
        cursor.setValueBuffer("date_field", "2019-01-01")
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
        cursor.select()
        cursor.setSort("string_field ASC")
        cursor.last()
        self.assertEqual(cursor.currentRegister(), 2)
        cursor.select()
        self.assertTrue(cursor.last())
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

        self.assertEqual(model.find_pk_row(cursor.valueBuffer("id")), cursor.size() - 1)
        self.assertEqual(model.metadata().primaryKey(), "id")
        self.assertEqual(model.fieldType("string_field"), "string")
        self.assertEqual(model.alias("string_field"), "String field")
        self.assertEqual(
            model.metadata().field("string_field"), cursor.metadata().field("string_field")
        )

    def test_basic_3(self) -> None:
        from PyQt6 import QtCore  # type: ignore[import]
        import locale
        import os
        from datetime import date

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.setSort("string_field DESC")

        cursor.select()
        model = cursor.model()

        self.assertEqual(model.data(model.index(0, 1)), "zzz")
        self.assertEqual(model.data(model.index(0, 0)), 4)
        self.assertEqual(model.data(model.index(0, 2)), None)
        self.assertEqual(
            model.data(model.index(0, 4)), QtCore.QLocale.system().toString(float(0.01), "f", 2)
        )
        self.assertEqual(model.data(model.index(0, 5)), "No")
        self.assertEqual(model.data(model.index(1, 1)), "yyy")
        self.assertEqual(model.data(model.index(1, 0)), 6)

        cursor.setSort("string_field DESC, double_field DESC")
        model.sort(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.assertEqual(
            model.data(model.index(0, 5), QtCore.Qt.ItemDataRole.TextAlignmentRole),
            QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignCenter,
        )
        self.assertEqual(
            model.data(model.index(1, 1), QtCore.Qt.ItemDataRole.TextAlignmentRole),
            QtCore.Qt.AlignmentFlag.AlignVCenter,
        )
        system_date = date(2019, 1, 1)
        locale.setlocale(locale.LC_TIME, "")
        date_format = "%%d/%%m/%%y" if os.name == "nt" else locale.nl_langinfo(locale.D_FMT)

        date_format = date_format.replace("y", "Y")  # Año con 4 dígitos
        date_format = date_format.replace("/", "-")  # Separadores
        date_ = system_date.strftime(date_format)

        self.assertEqual(model.data(model.index(0, 2), QtCore.Qt.ItemDataRole.DisplayRole), date_)
        self.assertEqual(
            model.data(model.index(1, 4), QtCore.Qt.ItemDataRole.DisplayRole),
            QtCore.QLocale.system().toString(float(0.01), "f", 2),
        )

    def test_basic_4(self) -> None:
        """Test basic 4."""
        from PyQt6 import QtCore, QtGui

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.setSort("string_field DESC")
        cursor.select()

        model = cursor.model()
        self.assertTrue(
            isinstance(
                model.data(model.index(0, 5), QtCore.Qt.ItemDataRole.BackgroundRole), QtGui.QBrush
            )
        )
        self.assertTrue(
            isinstance(
                model.data(model.index(0, 5), QtCore.Qt.ItemDataRole.ForegroundRole), QtGui.QBrush
            )
        )

        model.update_rows()
        # self.assertFalse(model.findCKRow([]))
        # self.assertFalse(model.findCKRow([2, 2]))
        self.assertEqual(model.find_pk_row(21), -1)
        self.assertEqual(model.find_pk_row(4), 0)

    def test_basic_5(self) -> None:
        """Test basic 5."""
        from PyQt6 import QtCore

        cursor = pnsqlcursor.PNSqlCursor("fltest2")

        model = cursor.model()
        model.disable_refresh(True)
        model.sort(1, QtCore.Qt.SortOrder.DescendingOrder)
        self.assertTrue(model._disable_refresh)
        model.disable_refresh(False)
        model.update_rows()
        cursor.select()
        model.updateColumnsCount()
        self.assertEqual(model.rowCount(), 3)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


class TestFetchMore(unittest.TestCase):
    """Test Acos class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test fetchmoderows 1."""

        from pineboolib.application.database import pnsqlcursor

        cur_test = pnsqlcursor.PNSqlCursor("fltest")
        size = 2102
        for i in range(size):
            cur_test.setModeAccess(cur_test.Insert)
            self.assertTrue(cur_test.refreshBuffer())
            cur_test.setValueBuffer("string_field", "Registro %s" % i)
            self.assertTrue(cur_test.commitBuffer())

        cur_test.select()
        self.assertEqual(cur_test.size(), size)

    def test_basic_2(self) -> None:
        """Test fetchmoderows 2."""

        from pineboolib.application.database import pnsqlcursor

        cur_test = pnsqlcursor.PNSqlCursor("fltest")
        cur_test.select()
        self.assertTrue(cur_test.first())
        self.assertEqual(cur_test.valueBuffer("string_field"), "Registro 0")
        self.assertTrue(cur_test.next())
        self.assertEqual(cur_test.valueBuffer("string_field"), "Registro 1")
        self.assertTrue(cur_test.last())
        self.assertEqual(cur_test.valueBuffer("string_field"), "Registro 2101")
        self.assertTrue(cur_test.prev())
        self.assertEqual(cur_test.valueBuffer("string_field"), "Registro 2100")

    def test_basic_3(self) -> None:
        """Test fetchmoderows 3."""

        from pineboolib.application.database import pnsqlquery

        qry_test = pnsqlquery.PNSqlQuery()
        qry_test.setTablesList("fltest")
        qry_test.setFrom("fltest")
        qry_test.setWhere("1=1")
        qry_test.setSelect("string_field")
        qry_test.setOrderBy("id")
        self.assertTrue(qry_test.exec_())
        self.assertEqual(qry_test.size(), 2102)
        self.assertTrue(qry_test.first())
        self.assertEqual(qry_test.value(0), "Registro 0")
        self.assertTrue(qry_test.last())
        self.assertEqual(qry_test.value(0), "Registro 2101")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
