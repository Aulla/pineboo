"""Test Signals module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.qsa import qsa

VALUE_1 = 0
VALUE_2 = ""


def update_value(field_name: str) -> None:
    """Update test value."""

    global VALUE_1, VALUE_2

    VALUE_2 = field_name
    VALUE_1 += 1


def update_value_2() -> None:
    """Update test value"""

    global VALUE_1

    VALUE_1 += 1


class TestSignals(unittest.TestCase):
    """TestQueryOrm Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        application.PROJECT.conn_manager.manager().createTable("fltest4")
        application.PROJECT.conn_manager.manager().createTable("fltest5")

    def test_basic_1(self) -> None:
        global VALUE_1

        VALUE_1 = 0
        qsa.thread_session_new()
        obj_ = qsa.orm.fltest4()
        self.assertTrue(obj_)
        obj_.bufferChanged.connect(update_value)
        obj_.idarea = "juas"
        qsa.thread_session_free()
        self.assertEqual(VALUE_1, 1)

    def test_basic_2(self) -> None:
        global VALUE_1

        VALUE_1 = 0
        qsa.thread_session_new()
        obj_ = qsa.orm.fltest4()
        self.assertTrue(obj_)
        obj_.bufferChanged.connect(update_value)
        obj_.idarea = "juas"
        obj_.other_field = "dos"

        self.assertEqual(VALUE_1, 2)
        obj_.bufferChanged.disconnect(update_value)
        obj_.idarea = "juas2"
        self.assertEqual(VALUE_1, 2)
        qsa.thread_session_free()

    def test_basic_3(self) -> None:
        global VALUE_2

        VALUE_2 = ""
        qsa.thread_session_new()
        obj_ = qsa.orm.fltest4()
        self.assertTrue(obj_)
        obj_.bufferChanged.connect(update_value)
        obj_.idarea = "juas"
        qsa.thread_session_free()
        self.assertEqual(VALUE_2, "idarea")

    def test_basic_4(self) -> None:
        global VALUE_1, VALUE_2

        VALUE_1 = 0
        VALUE_2 = ""
        qsa.thread_session_new()
        obj_ = qsa.orm.fltest4()
        self.assertTrue(obj_)
        obj_.bufferChanged.connect(update_value)
        obj_.bufferChanged.connect(update_value_2)
        obj_.idarea = "juas"
        qsa.thread_session_free()
        self.assertEqual(VALUE_1, 2)
        self.assertEqual(VALUE_2, "idarea")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
