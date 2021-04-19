"""Test_pnsqldrivers module."""

import unittest
from pineboolib import application

from pineboolib.loader.main import init_testing


class TestPNSqlDriversManager(unittest.TestCase):
    """TestPNSqlDriversManager Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_full(self) -> None:
        """Test full."""

        mng_ = application.PROJECT.conn_manager

        self.assertEqual(mng_._drivers_sql_manager.defaultDriverName(), "FLsqlite")
        self.assertEqual(mng_._drivers_sql_manager.driverName(), "FLsqlite")
        # self.assertTrue(
        #    conn_._driver_sql.isDesktopFile(
        #        conn_._driver_sql.nameToAlias(conn_._driver_sql.driverName())
        #    )
        # )
        self.assertEqual(
            mng_._drivers_sql_manager.port(
                mng_._drivers_sql_manager.nameToAlias(mng_._drivers_sql_manager.driverName())
            ),
            "0",
        )
        self.assertEqual(mng_._drivers_sql_manager.aliasToName(""), "FLsqlite")
        self.assertEqual(mng_._drivers_sql_manager.aliasToName(), "FLsqlite")
