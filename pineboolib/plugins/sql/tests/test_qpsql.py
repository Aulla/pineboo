"""Test_FLPGSql module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.database import pnsqlcursor
from pineboolib.application.metadata import pntablemetadata
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

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        sql = (
            "CREATE TABLE fltest (id INT4 DEFAULT NEXTVAL('fltest_id_seq') PRIMARY KEY,string_field VARCHAR NULL,"
            + "date_field DATE NULL,time_field TIME NULL,double_field FLOAT8 NULL,bool_field BOOLEAN NULL,"
            + "uint_field INT4 NULL,bloqueo BOOLEAN NOT NULL,empty_relation VARCHAR(15) NULL,int_field INT2 NULL)"
        )

        driver = flqpsql.FLQPSQL()
        self.assertEqual(sql, driver.sqlCreateTable(cursor.metadata(), False))

    def test_cast_1(self) -> None:
        """Cast test 1 (to string)."""

        metadata = pnsqlcursor.PNSqlCursor("fltest").metadata()
        driver = flqpsql.FLQPSQL()

        meta_data = driver.recordInfo(metadata)
        print("meta", meta_data)

        # str -> str
        meta_field = meta_data[1]
        self.assertEqual(
            "string_field",
            driver.cast_field(["string_field", "string", False, 0, 0, None, False], meta_field),
        )
        # int -> str
        self.assertEqual(
            "CAST ( string_field AS VARCHAR )",
            driver.cast_field(["string_field", "uint", False, 0, 0, None, False], meta_field),
        )

        # double -> str
        self.assertEqual(
            "CAST ( string_field AS VARCHAR )",
            driver.cast_field(["string_field", "double", False, 0, 0, None, False], meta_field),
        )

        print("**", driver.setType("date"))
        # date -> str
        self.assertEqual(
            "CAST ( string_field AS VARCHAR )",
            driver.cast_field(["string_field", "date", False, 0, 0, None, False], meta_field),
        )

        # json -> str
        self.assertEqual(
            "CAST ( string_field AS VARCHAR )",
            driver.cast_field(["string_field", "json", False, 0, 0, None, False], meta_field),
        )

        # timestamp -> str
        self.assertEqual(
            "CAST ( string_field AS VARCHAR )",
            driver.cast_field(["string_field", "timestamp", False, 0, 0, None, False], meta_field),
        )

        # stringlist -> str
        self.assertEqual(
            "CAST ( string_field AS VARCHAR )",
            driver.cast_field(["string_field", "stringlist", False, 0, 0, None, False], meta_field),
        )

    def test_cast_2(self) -> None:
        """Cast test 2 (to uint)."""

        metadata = pnsqlcursor.PNSqlCursor("fltest").metadata()
        driver = flqpsql.FLQPSQL()

        meta_data = driver.recordInfo(metadata)
        print("meta", meta_data)

        # str -> uint
        meta_field = meta_data[6]
        self.assertEqual(
            "CAST ( uint_field AS INT4 )",
            driver.cast_field(["uint_field", "string", False, 0, 0, None, False], meta_field),
        )
        # int -> uint
        self.assertEqual(
            "uint_field",
            driver.cast_field(["uint_field", "uint", False, 0, 0, None, False], meta_field),
        )

        # double -> uint
        self.assertEqual(
            "CAST ( uint_field AS INT4 )",
            driver.cast_field(["uint_field", "double", False, 0, 0, None, False], meta_field),
        )

    def test_cast_3(self) -> None:
        """Cast test 3 (to double)."""

        metadata = pnsqlcursor.PNSqlCursor("fltest").metadata()
        driver = flqpsql.FLQPSQL()

        meta_data = driver.recordInfo(metadata)
        print("meta", meta_data)

        # str -> double
        meta_field = meta_data[4]
        self.assertEqual(
            "CAST ( double_field AS FLOAT8 )",
            driver.cast_field(["double_field", "string", False, 0, 0, None, False], meta_field),
        )
        # int -> double
        self.assertEqual(
            "CAST ( double_field AS FLOAT8 )",
            driver.cast_field(["double_field", "uint", False, 0, 0, None, False], meta_field),
        )

        # double -> double
        self.assertEqual(
            "double_field",
            driver.cast_field(["double_field", "double", False, 0, 0, None, False], meta_field),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
