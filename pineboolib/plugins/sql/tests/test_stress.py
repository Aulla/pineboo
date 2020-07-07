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

        return
        cursor = qsa.FLSqlCursor("fltest")
        util = qsa.FLUtil()

        for number in range(10000):
            cursor.setModeAccess(cursor.Insert)
            cursor.refreshBuffer()
            texto = util.enLetra(randint(0, 10000000))
            if randint(0, 8) > 7:
                texto += ' % :) :: " "'
            cursor.setValueBuffer("string_field", texto)

            cursor.setValueBuffer("double_field", random())
            cursor.setValueBuffer("bool_field", True if randint(0, 10) > 4 else False)
            cursor.setValueBuffer("uint_field", randint(0, 100000))
            cursor.commitBuffer()

    def test_basic_2(self) -> None:
        """Test basic 2."""
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
