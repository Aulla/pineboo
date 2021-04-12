"""Test_aqs module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from typing import cast

from pineboolib.qsa import qsa


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

        cursor = flsqlcursor.FLSqlCursor("flareas")
        action = application.PROJECT.conn_manager.manager().action("flareas")
        form = flformdb.FLFormDB(action, None)
        self.assertTrue(form)
        form.load()
        form.setCursor(cursor)
        child = cast(fltabledb.FLTableDB, form.child("tableDBRecords"))
        self.assertTrue(isinstance(child, fltabledb.FLTableDB))
        child.refresh(qsa.AQS.RefreshData)
        # FIXME : saber que ha funcionado

    def test_qevents(self) -> None:
        """Test QEvent class."""

        ev_1 = qsa.AQS.FocusIn
        ev_2 = qsa.AQS.KeyRelease

        self.assertEqual(ev_1, 8)
        self.assertEqual(ev_2, 7)

    def test_aqs_attributes(self) -> None:
        """Test AQS Attributes."""
        from PyQt6 import QtCore, QtGui  # type: ignore[import]

        at_1 = qsa.AQS.WaitCursor
        at_2 = qsa.AQS.ContextMenu
        self.assertEqual(at_1, QtCore.Qt.CursorShape.WaitCursor)
        self.assertEqual(at_2, QtGui.QContextMenuEvent)

    def test_others(self) -> None:
        """Test others."""

        sha = qsa.AQS.sha1(b"12345")
        self.assertEqual(sha, "8CB2237D0679CA88DB6464EAC60DA96345513964")
        self.assertEqual(qsa.AQS.WordBreak, 4096)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
