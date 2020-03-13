"""Test_flsqlite module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.plugins.sql import flsqlite


class TestFLSqlite(unittest.TestCase):
    """TestFLSqlite Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Basics test 1."""

        driver = flsqlite.FLSQLITE()

        self.assertEqual(driver.formatValueLike("bool", "true", False), "=0")
        self.assertEqual(driver.formatValueLike("date", "2020-01-27", True), "LIKE '%%27-01-2020'")

        self.assertEqual(driver.formatValue("bool", "false", True), "0")
        self.assertEqual(driver.formatValue("time", "", True), "")

        self.assertFalse(driver.rollbackTransaction())
        self.assertFalse(driver.savePoint(0))
        self.assertFalse(driver.commitTransaction())
        self.assertFalse(driver.transaction())
        self.assertFalse(driver.releaseSavePoint(0))

        self.assertEqual(driver.setType("String", 20), "VARCHAR(20)")
        self.assertEqual(driver.setType("sTring", 0), "VARCHAR")
        self.assertEqual(driver.setType("Double"), "FLOAT")
        self.assertEqual(driver.setType("Bool"), "BOOLEAN")
        self.assertEqual(driver.setType("DATE"), "VARCHAR(20)")
        self.assertEqual(driver.setType("pixmap"), "TEXT")
        self.assertEqual(driver.setType("bytearray"), "CLOB")
        self.assertEqual(driver.setType("timestamp"), "DATETIME")
        self.assertEqual(
            driver.process_booleans("'true' AND false AND 'false'"), "1 AND false AND 0"
        )

    def test_basic_2(self) -> None:
        """Basics test 1."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        sql = (
            "CREATE TABLE fltest (id INTEGER PRIMARY KEY,string_field VARCHAR NULL,date_field VARCHAR(20)"
            + " NULL,time_field VARCHAR(20) NULL,double_field FLOAT NULL,bool_field BOOLEAN NULL"
            + ",uint_field INTEGER NULL,bloqueo BOOLEAN NOT NULL);CREATE INDEX fltest_pkey ON fltest (id)"
        )
        sql2 = (
            "CREATE TABLE fltest (id INTEGER PRIMARY KEY,string_field VARCHAR NULL,date_field VARCHAR(20)"
            + " NULL,time_field VARCHAR(20) NULL,double_field FLOAT NULL,bool_field BOOLEAN NULL"
            + ",uint_field INTEGER NULL,bloqueo BOOLEAN NOT NULL);"
        )
        driver = flsqlite.FLSQLITE()

        self.assertEqual(sql, driver.sqlCreateTable(cursor.metadata()))
        self.assertEqual(sql2, driver.sqlCreateTable(cursor.metadata(), False))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
