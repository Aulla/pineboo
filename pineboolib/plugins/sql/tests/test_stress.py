"""Test_Stress module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.metadata import pnfieldmetadata
from pineboolib.qsa import qsa


class TestStress(unittest.TestCase):
    """TestFLSqlite Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic 1."""

        from random import randint, random

        cursor = qsa.FLSqlCursor("fltest")
        registers = 25000
        util = qsa.FLUtil()

        for number in range(registers):
            texto = util.enLetra(randint(0, 10000000))
            if randint(0, 8) > 7:
                texto += ' % :) :: " "'

            util.execSql(
                "INSERT INTO fltest(string_field, double_field, bool_field, uint_field, bloqueo) VALUES ('%s',%s,%s,%s, True)"
                % (texto, random(), True if randint(0, 10) > 4 else False, randint(0, 100000))
            )
        cursor.select()
        self.assertEqual(cursor.size(), registers)

    def test_basic_2(self) -> None:
        """Test basic 2."""

        cursor = qsa.FLSqlCursor("fltest")
        cursor.select()
        cursor.first()
        steps = 0
        while cursor.next():
            steps += 1

        self.assertEqual(steps, cursor.at())

        while cursor.prev():
            steps -= 1

        self.assertEqual(steps, cursor.at())

    def test_basic_21(self) -> None:
        """Test basic 21."""

        from random import randint, random

        util = qsa.FLUtil()
        cursor = qsa.FLSqlCursor("fltest")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("new_string", util.enLetra(randint(0, 10000000)))
        cursor.setValueBuffer("double_field", random())
        cursor.setValueBuffer("bool_field", False)
        cursor.setValueBuffer("uint_field", randint(0, 100000))
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("new_string", util.enLetra(randint(0, 10000000)))
        cursor.setValueBuffer("double_field", random())
        cursor.setValueBuffer("bool_field", False)
        cursor.setValueBuffer("uint_field", randint(0, 100000))
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("new_string", util.enLetra(randint(0, 10000000)))
        cursor.setValueBuffer("double_field", random())
        cursor.setValueBuffer("bool_field", False)
        cursor.setValueBuffer("uint_field", randint(0, 100000))
        self.assertTrue(cursor.commitBuffer())

    def test_basic_3(self) -> None:
        """Test basic 3."""

        cursor = qsa.FLSqlCursor("fltest")
        metadata = cursor.metadata()

        field_str = metadata.field("string_field")
        self.assertTrue(field_str is not None)
        if field_str is not None:
            self.assertEqual(field_str.length(), 0)
            before_change_structure = cursor.db().driver().recordInfo2("fltest")
            field_str.private.length_ = 180

        self.assertTrue(cursor.db().alterTable(metadata))
        after_change_structure = cursor.db().driver().recordInfo2("fltest")

        self.assertEqual(before_change_structure[list(before_change_structure.keys())[1]][3], 0)
        self.assertEqual(after_change_structure[list(after_change_structure.keys())[1]][3], 180)

    def test_basic_4(self) -> None:
        """Test basic 4."""

        cursor = qsa.FLSqlCursor("fltest")
        metadata = cursor.metadata()

        field = pnfieldmetadata.PNFieldMetaData(
            "new_string",
            "Nuevo String",
            False,
            False,
            "string",
            50,
            False,
            True,
            True,
            5,
            8,
            False,
            False,
            False,
            "nada",
            False,
            None,
            True,
            True,
            False,
        )

        metadata.addFieldMD(field)
        before_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertTrue(cursor.db().alterTable(metadata))
        after_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertEqual(len(before_change_structure), 10)
        self.assertEqual(len(after_change_structure), 11)

        total = qsa.FLUtil().quickSqlSelect("fltest", "new_string", "id = 9")
        self.assertEqual(total, "nada")

    def test_basic_5(self) -> None:
        """Test basic 5."""

        cursor = qsa.FLSqlCursor("fltest")
        metadata = cursor.metadata()

        field = pnfieldmetadata.PNFieldMetaData(
            "new_bool",
            "Nuevo Bool",
            False,
            False,
            "bool",
            50,
            False,
            True,
            True,
            5,
            8,
            False,
            False,
            False,
            False,  # default value
            False,
            None,
            True,
            True,
            False,
        )

        metadata.addFieldMD(field)
        before_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertTrue(cursor.db().alterTable(metadata))
        after_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertEqual(len(before_change_structure), 11)
        self.assertEqual(len(after_change_structure), 12)

        total = qsa.FLUtil().quickSqlSelect("fltest", "new_bool", "id = 100")
        self.assertEqual(total, False)

    def test_basic_6(self) -> None:
        """Test basic 6."""

        cursor = qsa.FLSqlCursor("fltest")
        metadata = cursor.metadata()

        field = pnfieldmetadata.PNFieldMetaData(
            "new_bool2",
            "Nuevo Bool 2",
            True,  # allow null.
            False,
            "bool",
            50,
            False,
            True,
            True,
            5,
            8,
            False,
            False,
            False,
            None,  # default value
            False,
            None,
            True,
            True,
            False,
        )

        metadata.addFieldMD(field)
        before_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertTrue(cursor.db().alterTable(metadata))
        after_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertEqual(len(before_change_structure), 12)
        self.assertEqual(len(after_change_structure), 12 + 1)
        # cursor.select()
        # self.assertTrue(cursor.size())

        total = qsa.FLUtil().quickSqlSelect("fltest", "new_bool2", "id = 100")
        self.assertEqual(total, False)

    def test_basic_7(self) -> None:
        """Test basic 7."""

        cursor = qsa.FLSqlCursor("fltest")
        metadata = cursor.metadata()

        field = pnfieldmetadata.PNFieldMetaData(
            "new_bool3",
            "Nuevo Bool 3",
            False,
            False,
            "bool",
            50,
            False,
            True,
            True,
            5,
            8,
            False,
            False,
            False,
            True,  # default value
            False,
            None,
            True,
            True,
            False,
        )

        metadata.addFieldMD(field)
        before_change_structure = cursor.db().driver().recordInfo2("fltest")
        cursor.db().alterTable(metadata)
        after_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertEqual(len(before_change_structure), 12 + 1)
        self.assertEqual(len(after_change_structure), 14)

        total = qsa.FLUtil().quickSqlSelect("fltest", "new_bool3", "id = 666")
        self.assertEqual(total, True)

    def test_basic_8(self) -> None:
        """Test basic 8."""

        cursor = qsa.FLSqlCursor("fltest")
        metadata = cursor.metadata()

        field = pnfieldmetadata.PNFieldMetaData(
            "new_date",
            "Nuevo Date",
            True,
            False,
            "date",
            0,
            False,
            True,
            True,
            5,
            8,
            False,
            False,
            False,
            None,  # default value
            False,
            None,
            True,
            True,
            False,
        )

        metadata.addFieldMD(field)
        before_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertTrue(cursor.db().alterTable(metadata))
        after_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertEqual(len(before_change_structure), 14)
        self.assertEqual(len(after_change_structure), 15)

        total = qsa.FLUtil().quickSqlSelect("fltest", "new_date", "id = 731")
        self.assertEqual(total, "")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
