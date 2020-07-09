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

        util = qsa.FLUtil()

        for number in range(100000):
            texto = util.enLetra(randint(0, 10000000))
            if randint(0, 8) > 7:
                texto += ' % :) :: " "'

            util.execSql(
                "INSERT INTO fltest(string_field, double_field, bool_field, uint_field, bloqueo) VALUES ('%s',%s,%s,%s, True)"
                % (texto, random(), True if randint(0, 10) > 4 else False, randint(0, 100000))
            )
        cursor.select()
        self.assertEqual(cursor.size(), 100000)

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

    def test_basic_3(self) -> None:
        """Test basic 3."""

        cursor = qsa.FLSqlCursor("fltest")
        metadata = cursor.metadata()

        field_str = metadata.field("string_field")
        self.assertEqual(field_str.length(), 0)
        before_change_structure = cursor.db().driver().recordInfo2("fltest")
        field_str.private.length_ = 180

        cursor.db().alterTable(metadata)
        after_change_structure = cursor.db().driver().recordInfo2("fltest")

        self.assertEqual(before_change_structure[1][3], 0)
        self.assertEqual(after_change_structure[1][3], 180)

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
        cursor.db().alterTable(metadata)
        after_change_structure = cursor.db().driver().recordInfo2("fltest")
        self.assertEqual(len(before_change_structure), 8)
        self.assertEqual(len(after_change_structure), 9)

        new_cursor = qsa.FLSqlCursor("fltest")
        new_cursor.select()
        self.assertTrue(new_cursor.first())
        self.assertEqual(new_cursor.at(), 0)
        self.assertEqual(new_cursor.valueBuffer("new_string"), "nada")
        new_cursor.last()
        self.assertEqual(new_cursor.at(), 99999)
        self.assertEqual(new_cursor.valueBuffer("new_string"), "nada")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
