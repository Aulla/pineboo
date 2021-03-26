"""Test_flmssql module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from .. import flpymssql


class TestFLMSSql(unittest.TestCase):
    """TestFLSqlite Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Basics test 1."""

        driver = flpymssql.FLPYMSSQL()

        self.assertEqual(driver.formatValueLike("bool", "true", False), "=0")
        self.assertEqual(driver.formatValueLike("date", "27-01-2020", True), "LIKE '%%2020-01-27'")

        self.assertEqual(driver.formatValue("bool", "false", True), "0")
        self.assertEqual(driver.formatValue("time", "", True), "")

        self.assertEqual(driver.setType("String", 20), "VARCHAR(20)")
        self.assertEqual(driver.setType("sTring", 0), "VARCHAR")
        self.assertEqual(driver.setType("Double"), "DECIMAL")
        self.assertEqual(driver.setType("Bool"), "BIT")
        self.assertEqual(driver.setType("DATE"), "DATE")
        self.assertEqual(driver.setType("pixmap"), "TEXT")
        self.assertEqual(driver.setType("bytearray"), "NVARCHAR")
        self.assertEqual(driver.setType("timestamp"), "DATETIME2")

    def test_basic_2(self) -> None:
        """Basics test 1."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        sql = (
            "CREATE TABLE fltest (id PRIMARY KEY,string_field VARCHAR NULL,date_field DATE NULL,time_field TIME NULL,double_field"
            + " DECIMAL(8,2) NULL,bool_field BIT NULL,uint_field BIGINT NULL,"
            + "bloqueo BIT NOT NULL,empty_relation VARCHAR(15) NULL,int_field INT NULL)"
        )

        driver = flpymssql.FLPYMSSQL()
        print(driver.sqlCreateTable(cursor.metadata(), False))
        self.assertEqual(sql, driver.sqlCreateTable(cursor.metadata(), False))

    def test_basic_3(self) -> None:
        """Basic test 3."""

        driver = flpymssql.FLPYMSSQL()
        self.assertEqual(driver.decodeSqlType("varchar"), "string")
        self.assertEqual(driver.decodeSqlType("bigint"), "uint")
        self.assertEqual(driver.decodeSqlType("int"), "int")
        self.assertEqual(driver.decodeSqlType("date"), "date")
        self.assertEqual(driver.decodeSqlType("text"), "stringlist")
        self.assertEqual(driver.decodeSqlType("bit"), "bool")
        self.assertEqual(driver.decodeSqlType("decimal"), "double")
        self.assertEqual(driver.decodeSqlType("nvarchar"), "bytearray")
        self.assertEqual(driver.decodeSqlType("time"), "time")
        self.assertEqual(driver.decodeSqlType("datetime2"), "timestamp")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
