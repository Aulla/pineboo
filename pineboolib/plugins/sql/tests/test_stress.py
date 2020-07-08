"""Test_Stress module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
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
        cursor.select()
        util = qsa.FLUtil()

        for number in range(100000):
            texto = util.enLetra(randint(0, 10000000))
            if randint(0, 8) > 7:
                texto += ' % :) :: " "'

            util.execSql(
                "INSERT INTO fltest(string_field, double_field, bool_field, uint_field, bloqueo) VALUES ('%s',%s,%s,%s, True)"
                % (texto, random(), True if randint(0, 10) > 4 else False, randint(0, 100000))
            )

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
        print(field_str)

    def test_basic_6(self) -> None:
        """Test basic 6."""
        return
        cursor = qsa.FLSqlCursor("fltest")
        metadata = cursor.metadata()
        field_mtd = metadata.field("string_field")
        self.assertNotEqual(field_mtd, None)
        # self.assertEqual(field_mtd.length(), 10)

        # def test_basic_3(self) -> None:
        #    """Test basic 3."""

        # cursor = qsa.FLSqlCursor("fltest")
        """metadata = cursor.metadata()

        from pineboolib.application.metadata import pnfieldmetadata

        field = pnfieldmetadata.PNFieldMetaData(
            "new_double",
            "Nuevo Double",
            False,
            False,
            "double",
            0,
            False,
            True,
            True,
            5,
            8,
            False,
            False,
            False,
            0.01,
            False,
            None,
            True,
            False,
            False,
        )"""

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
