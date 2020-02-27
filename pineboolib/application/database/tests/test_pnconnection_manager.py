"""Test_pnconnection module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.application.database import pnsqlcursor

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
