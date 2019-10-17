"""Test_aqs module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestAQS(unittest.TestCase):
    """TestAQS Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_refreshData(self) -> None:
        """RefreshData test."""

        from pineboolib.fllegacy import flformdb, fltabledb, flsqlcursor
        from pineboolib import application
        from pineboolib.qsa import qsa

        cursor = flsqlcursor.FLSqlCursor("flareas")
        action = application.project.conn.manager().action("flareas")
        form = flformdb.FLFormDB(None, action)
        self.assertTrue(form)
        form.load()
        form.setCursor(cursor)
        child = form.child("tableDBRecords")
        self.assertTrue(isinstance(child, fltabledb.FLTableDB))
        child.refresh(qsa.AQS.RefreshData)
        # FIXME : saber que ha funcionado

    def test_qevents(self) -> None:
        """Test QEvent class."""
        from pineboolib.qsa import qsa

        ev_1 = qsa.AQS.FocusIn
        ev_2 = qsa.AQS.KeyRelease

        self.assertEqual(ev_1, 8)
        self.assertEqual(ev_2, 7)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
