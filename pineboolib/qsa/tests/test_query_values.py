"""Test query values module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestQueryValues(unittest.TestCase):
    """TestQueryValues class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_pnsqlcursor(self) -> None:
        """Test PNSqlCursor received values."""
        cur = qsa.FLSqlCursor("fltest")
        cur.setModeAccess(cur.Insert)
        cur.refreshBuffer()
        cur.setValueBuffer("date_field", "2000-01-01")
        self.assertTrue(cur.commitBuffer())
        self.assertTrue(isinstance(cur.valueBuffer("date_field"), qsa.Date))

    def test_pnsqlcursor_fake(self) -> None:
        """Test PNSqlCursor_fake received values."""
        class_fltest2 = qsa.orm.fltest
        self.assertTrue(class_fltest2)
        obj_ = class_fltest2()
        fake_cursor = obj_.cursor
        fake_cursor.setValueBuffer("date_field", "2001-02-01")
        self.assertTrue(isinstance(fake_cursor.valueBuffer("date_field"), qsa.Date))

    def test_pnsqlquery(self) -> None:
        """Test PNSqlQuery received values."""
        qry = qsa.FLSqlQuery()
        qry.setSelect("date_field")
        qry.setFrom("fltest")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        self.assertTrue(isinstance(qry.value("date_field"), qsa.Date))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
