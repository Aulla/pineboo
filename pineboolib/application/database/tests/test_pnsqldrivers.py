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

        conn_ = application.project.conn_manager.mainConn()

        self.assertEqual(conn_.driverSql.defaultDriverName(), "FLsqlite")
        self.assertEqual(conn_.driverSql.driverName(), "FLsqlite")
        self.assertTrue(
            conn_.driverSql.isDesktopFile(conn_.driverSql.nameToAlias(conn_.driverSql.driverName()))
        )
        self.assertEqual(
            conn_.driverSql.port(conn_.driverSql.nameToAlias(conn_.driverSql.driverName())), "0"
        )
        self.assertEqual(conn_.driverSql.aliasToName(""), "FLsqlite")
        self.assertEqual(conn_.driverSql.aliasToName(), "FLsqlite")
