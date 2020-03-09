"""Test_pnconnection module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.application.database import pnsqlcursor

from pineboolib.core.utils import logging
from threading import Thread
import time

LOGGER = logging.get_logger(__name__)

USER_ID: str


class TestPNConnectionManager(unittest.TestCase):
    """TestPNConnection Class."""

    @classmethod
    def setUp(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic1(self) -> None:
        """Basic test 1."""
        global USER_ID

        USER_ID = "usu0"

        application.PROJECT.set_session_function(self.user_id)
        conn_manager = application.PROJECT.conn_manager
        self.assertEqual(conn_manager.session_id(), USER_ID)
        cursor_1 = pnsqlcursor.PNSqlCursor("flfiles")  # noqa: F841
        self.assertEqual(conn_manager.session_id(), "usu0")
        self.assertEqual(conn_manager.active_pncursors(True), ["flfiles"])

    def test_basic2(self) -> None:
        """Basic test 2."""
        global USER_ID

        USER_ID = "usu1"
        conn_manager = application.PROJECT.conn_manager
        self.assertEqual(conn_manager.session_id(), "usu1")
        self.assertEqual(conn_manager.active_pncursors(True), [])
        cursor_1 = pnsqlcursor.PNSqlCursor("flfiles")  # noqa: F841
        self.assertEqual(conn_manager.active_pncursors(True), ["flfiles"])
        self.assertTrue("flfiles" in conn_manager.active_pncursors(True, True))
        USER_ID = "usu2"
        self.assertEqual(conn_manager.session_id(), "usu2")
        self.assertEqual(conn_manager.active_pncursors(True), [])
        cursor_2 = pnsqlcursor.PNSqlCursor("flfiles")  # noqa: F841
        cursor_3 = pnsqlcursor.PNSqlCursor("flareas")  # noqa: F841
        self.assertEqual(conn_manager.active_pncursors(True), ["flfiles", "flareas"])
        self.assertTrue(len(conn_manager.active_pncursors(True, True)) > 2)
        USER_ID = "usu1"
        self.assertEqual(conn_manager.active_pncursors(True), ["flfiles"])
        self.assertTrue(len(conn_manager.active_pncursors(True, True)) > 2)

    def test_basic3(self) -> None:
        """Basic test 3."""
        from PyQt5 import QtWidgets

        global USER_ID

        USER_ID = "test3"

        conn_manager = application.PROJECT.conn_manager
        self.assertEqual(application.PROJECT.conn_manager.session_id(), "test3")
        thread1 = Thread(target=self.threaded_function)
        thread2 = Thread(target=self.threaded_function)
        thread3 = Thread(target=self.threaded_function)
        thread4 = Thread(target=self.threaded_function)
        thread5 = Thread(target=self.threaded_function)
        thread6 = Thread(target=self.threaded_function)
        thread7 = Thread(target=self.threaded_function)
        thread8 = Thread(target=self.threaded_function)
        thread9 = Thread(target=self.threaded_function)

        thread1.start()
        while "flfiles" in conn_manager.active_pncursors(True):
            QtWidgets.QApplication.processEvents()
        thread2.start()
        while "flfiles" in conn_manager.active_pncursors(True):
            QtWidgets.QApplication.processEvents()
        thread3.start()
        while "flfiles" in conn_manager.active_pncursors(True):
            QtWidgets.QApplication.processEvents()
        thread4.start()
        thread5.start()
        thread6.start()
        thread7.start()
        thread8.start()
        thread9.start()
        while "flfiles" in conn_manager.active_pncursors(True):
            QtWidgets.QApplication.processEvents()

    def threaded_function(self) -> None:
        """Threaded function."""

        try:
            cur = pnsqlcursor.PNSqlCursor("flfiles")
            cur.select()
        except Exception:
            time.sleep(1)
            pnsqlcursor.CONNECTION_CURSORS[application.PROJECT.conn_manager.session_id()].pop()

    def user_id(self) -> str:
        """Return user id."""
        global USER_ID
        return USER_ID

    @classmethod
    def tearDown(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
