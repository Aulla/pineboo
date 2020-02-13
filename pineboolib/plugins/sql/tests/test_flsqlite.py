"""Test_flsqlite module."""
import unittest
from pineboolib.plugins.sql import flsqlite


class TestFLSqlite(unittest.TestCase):
    """TestFLSqlite Class."""

    def test_basic(self) -> None:
        """Basics test."""

        driver = flsqlite.FLSQLITE()

        self.assertEqual(driver.formatValueLike("bool", "true", False), "=0")
        self.assertEqual(driver.formatValueLike("date", "2020-01-27", True), "LIKE '%%27-01-2020'")

        self.assertEqual(driver.formatValue("bool", "false", True), 0)
        self.assertEqual(driver.formatValue("time", "", True), "")

        self.assertFalse(driver.rollbackTransaction())
        self.assertFalse(driver.savePoint(0))
        self.assertFalse(driver.commitTransaction())
        self.assertFalse(driver.transaction())
        self.assertFalse(driver.releaseSavePoint(0))

        self.assertEqual(driver.setType("String", 20), " STRING(20)")
        self.assertEqual(driver.setType("Double"), " DOUBLE")
        self.assertEqual(
            driver.process_booleans("'true' AND false AND 'false'"), "1 AND false AND 0"
        )
