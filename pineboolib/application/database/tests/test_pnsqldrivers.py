"""Test_pnsqldrivers module."""

import unittest
from pineboolib.loader.main import init_testing


class TestPNSqlDrivers(unittest.TestCase):
    """TestPNSqlDrivers Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_full(self) -> None:
        """Test full."""
        from pineboolib import application

        conn_ = application.PROJECT.conn_manager.mainConn()

        self.assertEqual(conn_._driver_sql.defaultDriverName(), "FLsqlite")
        self.assertEqual(conn_._driver_sql.driverName(), "FLsqlite")
        # self.assertTrue(
        #    conn_._driver_sql.isDesktopFile(
        #        conn_._driver_sql.nameToAlias(conn_._driver_sql.driverName())
        #    )
        # )
        self.assertEqual(
            conn_._driver_sql.port(conn_._driver_sql.nameToAlias(conn_._driver_sql.driverName())),
            "0",
        )
        self.assertEqual(conn_._driver_sql.aliasToName(""), "FLsqlite")
        self.assertEqual(conn_._driver_sql.aliasToName(), "FLsqlite")
