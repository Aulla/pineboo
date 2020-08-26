"""Test ThreadSession module."""

import unittest
import threading
import time

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.qsa import qsa

SESSION_LIST = []


class TestThreadSession(unittest.TestCase):
    """TestQueryOrm Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        application.PROJECT.conn_manager.manager().createTable("fltest4")
        application.PROJECT.conn_manager.manager().createTable("fltest5")

    def test_basic_1(self) -> None:
        """Test basic 1."""
        id_thread = threading.current_thread().ident
        key = "%s_%s" % (id_thread, "default")
        self.assertFalse(key in application.PROJECT.conn_manager.thread_atomic_sessions.keys())
        self.assertTrue(prueba(1))
        self.assertFalse(key in application.PROJECT.conn_manager.thread_atomic_sessions.keys())

    def test_basic_2(self) -> None:
        """Test basic 2."""
        id_thread = threading.current_thread().ident
        key = "%s_dbaux" % id_thread
        self.assertTrue(prueba2())
        self.assertFalse(key in application.PROJECT.conn_manager.thread_atomic_sessions.keys())

    def test_basic_3(self) -> None:
        """Test basic 3."""
        with self.assertRaises(Exception):
            prueba3()

    def test_basic_4(self) -> None:
        """Test basic 4."""

        for num in range(50):
            thr = threading.Thread(target=massive, args=(num,))
            thr.start()

        while len(SESSION_LIST) < 50:
            time.sleep(0.1)

        for session in SESSION_LIST:
            self.assertFalse(session.transaction)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()


@qsa.atomic()  # type: ignore [misc] # noqa: F821
def massive(value: int):
    """Massive test."""
    print("____inicio", value, qsa.session_atomic(), qsa.session_atomic().transaction)
    if not qsa.session_atomic().transaction:
        raise Exception("Transaction is empty!")

    SESSION_LIST.append(qsa.session_atomic())


@qsa.atomic()  # type: ignore [misc] # noqa: F821
def prueba(value: int):
    id_thread = threading.current_thread().ident
    key = "%s_%s" % (id_thread, "default")
    result = key in application.PROJECT.conn_manager.thread_atomic_sessions.keys()

    if application.PROJECT.conn_manager.thread_atomic_sessions[key] != qsa.session_atomic():
        result = False

    if value != 1:
        result = False
    return result


@qsa.atomic("dbaux")  # type: ignore [misc] # noqa: F821
def prueba2():
    id_thread = threading.current_thread().ident
    key = "%s_%s" % (id_thread, "dbaux")
    result = key in application.PROJECT.conn_manager.thread_atomic_sessions.keys()
    if application.PROJECT.conn_manager.thread_atomic_sessions[key] != qsa.session_atomic("dbaux"):
        result = False

    return result


@qsa.atomic("dbaux")  # type: ignore [misc] # noqa: F821
def prueba3():

    obj_ = qsa.orm.fltest4()
    return not obj_.session == qsa.session_atomic("dbaux")

