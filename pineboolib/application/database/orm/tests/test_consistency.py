"""Test query_orm module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.qsa import qsa


class TestConsistency(unittest.TestCase):
    """TestQueryOrm Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        application.PROJECT.conn_manager.manager().createTable("fltest4")
        application.PROJECT.conn_manager.manager().createTable("fltest5")

    def test_isolation(self) -> None:
        """Create multiples diferents sessions."""

        conn_name = "default"

        single_session = qsa.session(conn_name)
        legacy_session = qsa.session(conn_name, True)
        thread_session = qsa.thread_session_new(conn_name)

        self.assertTrue(single_session is not legacy_session)
        self.assertTrue(thread_session is not single_session)
        self.assertTrue(
            single_session in application.PROJECT.conn_manager._thread_sessions.values()
        )
        self.assertTrue(
            legacy_session in application.PROJECT.conn_manager._thread_sessions.values()
        )
        self.assertTrue(
            thread_session in application.PROJECT.conn_manager._thread_sessions.values()
        )

    def test_transaction(self) -> None:
        """Create a new record and query it from a query in the same transaction."""

        # thread_session.begin()
        # class_test4 = qsa.orm.fltest4
        # obj1 = class_test4()

        pass

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
