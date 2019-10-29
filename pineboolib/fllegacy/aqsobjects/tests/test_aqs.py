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
        action = application.project.conn_manager.manager().action("flareas")
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

    def test_aqs_attributes(self) -> None:
        """Test AQS Attributes."""
        from PyQt5 import QtCore, QtGui
        from pineboolib.qsa import qsa

        at_1 = qsa.AQS.WaitCursor
        at_2 = qsa.AQS.ContextMenu
        self.assertEqual(at_1, QtCore.Qt.WaitCursor)
        self.assertEqual(at_2, QtGui.QContextMenuEvent)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
