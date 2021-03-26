"""Test_FLPGSql module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from .. import flqpsql


class TestFLPGSql(unittest.TestCase):
    """TestFLSqlite Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Basics test 1."""

        driver = flqpsql.FLQPSQL()

        self.assertEqual(driver.formatValueLike("bool", "true", False), "='f'")
        self.assertEqual(
            driver.formatValueLike("date", "27-01-2020", True), "::text LIKE '%%2020-01-27'"
        )

        self.assertEqual(driver.formatValue("bool", "false", True), "False")
        self.assertEqual(driver.formatValue("time", "", True), "")

        self.assertEqual(driver.setType("String", 20), "VARCHAR(20)")
        self.assertEqual(driver.setType("sTring", 0), "VARCHAR")
        self.assertEqual(driver.setType("Double"), "FLOAT8")
        self.assertEqual(driver.setType("Bool"), "BOOLEAN")
        self.assertEqual(driver.setType("DATE"), "DATE")
        self.assertEqual(driver.setType("pixmap"), "TEXT")
        self.assertEqual(driver.setType("bytearray"), "BYTEA")
        self.assertEqual(driver.setType("timestamp"), "TIMESTAMPTZ")

    def test_basic_2(self) -> None:
        """Basics test 1."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        sql = (
            "CREATE TABLE fltest (id INT4 DEFAULT NEXTVAL('fltest_id_seq') PRIMARY KEY,string_field VARCHAR NULL,"
            + "date_field DATE NULL,time_field TIME NULL,double_field FLOAT8 NULL,bool_field BOOLEAN NULL,"
            + "uint_field INT4 NULL,bloqueo BOOLEAN NOT NULL,empty_relation VARCHAR(15) NULL,int_field INT2 NULL)"
        )

        driver = flqpsql.FLQPSQL()
        self.assertEqual(sql, driver.sqlCreateTable(cursor.metadata(), False))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
