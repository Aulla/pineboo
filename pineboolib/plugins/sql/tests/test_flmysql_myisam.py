"""Test_flsqlite module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from .. import flmysql_myisam


class TestFLSqlite(unittest.TestCase):
    """TestFLSqlite Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Basics test 1."""

        driver = flmysql_myisam.FLMYSQL_MYISAM()

        self.assertEqual(driver.formatValueLike("bool", "true", False), "=0")
        self.assertEqual(driver.formatValueLike("date", "27-01-2020", True), " LIKE '%%2020-01-27'")

        self.assertEqual(driver.formatValue("bool", "false", True), "False")
        self.assertEqual(driver.formatValue("time", "", True), "")

        self.assertEqual(driver.setType("String", 20), "CHAR(20)")
        self.assertEqual(driver.setType("sTring", 0), "CHAR")
        self.assertEqual(driver.setType("Double"), "DECIMAL")
        self.assertEqual(driver.setType("Bool"), "BOOL")
        self.assertEqual(driver.setType("DATE"), "DATE")
        self.assertEqual(driver.setType("pixmap"), "MEDIUMTEXT")
        self.assertEqual(driver.setType("bytearray"), "LONGBLOB")
        self.assertEqual(driver.setType("timestamp"), "TIMESTAMP")

    def test_basic_2(self) -> None:
        """Basics test 2."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        sql = (
            "CREATE TABLE fltest (id INT UNSIGNED PRIMARY KEY,string_field CHAR(255) NULL,date_field DATE NULL,time_field TIME NULL,"
            + "double_field DECIMAL(13,7) NULL,bool_field BOOL NULL,uint_field INT UNSIGNED NULL,bloqueo BOOL NOT NULL"
            + ",empty_relation CHAR(15) NULL,int_field INTEGER NULL)"
            + " ENGINE=MyISAM DEFAULT CHARACTER SET = utf8 COLLATE = utf8_bin"
        )

        driver = flmysql_myisam.FLMYSQL_MYISAM()
        self.assertEqual(sql, driver.sqlCreateTable(cursor.metadata(), False))

    def test_basic_3(self) -> None:
        """Basic test 3."""

        driver = flmysql_myisam.FLMYSQL_MYISAM()
        self.assertEqual(driver.decodeSqlType("char"), "string")
        self.assertEqual(driver.decodeSqlType("int unsigned"), "uint")
        self.assertEqual(driver.decodeSqlType("int"), "int")
        self.assertEqual(driver.decodeSqlType("date"), "date")
        self.assertEqual(driver.decodeSqlType("mediumtext"), "stringlist")
        self.assertEqual(driver.decodeSqlType("tinyint"), "bool")
        self.assertEqual(driver.decodeSqlType("decimal"), "double")
        self.assertEqual(driver.decodeSqlType("longblob"), "bytearray")
        self.assertEqual(driver.decodeSqlType("time"), "time")
        self.assertEqual(driver.decodeSqlType("timestamp"), "timestamp")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
