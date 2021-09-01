"""Test Signals module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.qsa import qsa

VALUE_1: int = 0
VALUE_2: str = ""
VALUE_3: bool = False
VALUE_4: str = ""
VALUE_5 = None


def update_value(field_name: str) -> None:
    """Update test value 1."""

    global VALUE_1, VALUE_2

    VALUE_2 = field_name
    VALUE_1 += 1


def update_value_2() -> None:
    """Update test value 2."""

    global VALUE_1

    VALUE_1 += 1


def update_value_3(field_name: str = "", cursor=None) -> None:
    """Update test value 3."""

    global VALUE_3

    VALUE_3 = field_name != "" and cursor is not None


def update_value_4(field_name: str = "", cursor=None) -> None:
    """Update test value 4."""

    global VALUE_4, VALUE_5

    if cursor.valueBuffer("idarea") == "JUAS_3":
        return

    VALUE_4 = cursor.valueBuffer(field_name)
    cursor.setValueBuffer("idarea", "JUAS_3")
    VALUE_5 = cursor


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

    def test_basic_5(self) -> None:
        global VALUE_1, VALUE_2

        VALUE_1 = 0
        VALUE_2 = ""
        qsa.thread_session_new()
        obj_ = qsa.orm.fltest4()
        self.assertTrue(obj_)
        obj_.cursor.bufferChanged.connect(update_value)
        obj_.bufferChanged.connect(update_value_2)
        self.assertEqual(obj_.cursor.bufferChanged, obj_.bufferChanged)
        obj_.idarea = "juas"
        qsa.thread_session_free()
        self.assertEqual(VALUE_1, 2)
        self.assertEqual(VALUE_2, "idarea")

    def test_basic_6(self) -> None:

        global VALUE_3

        qsa.thread_session_new()
        obj_ = qsa.orm.fltest4()
        self.assertTrue(obj_)
        obj_.cursor.bufferChanged.connect(update_value_3)
        obj_.idarea = "juas"

        self.assertEqual(VALUE_3, True)

    def test_basic_7(self) -> None:

        global VALUE_4, VALUE_5

        qsa.thread_session_new()
        obj_ = qsa.orm.fltest4()
        self.assertTrue(obj_)
        obj_.cursor.bufferChanged.connect(update_value_4)
        obj_.idarea = "juas"
        self.assertEqual(VALUE_4, "juas")
        self.assertTrue(VALUE_5)
        if VALUE_5 is not None:
            VALUE_5.setValueBuffer("idarea", "JUAS_2")
            self.assertEqual(obj_.idarea, "JUAS_2")
            VALUE_5.setValueBuffer("idarea", "JUAS_4")
            VALUE_5.setValueBuffer("idarea", "JUAS_3")
        self.assertEqual(obj_.idarea, "JUAS_3")
        self.assertEqual(obj_.changes(), {"id": 7, "idarea": "JUAS_3"})
        qsa.thread_session_free()
        self.assertEqual(VALUE_4, "JUAS_4")
        self.assertEqual(obj_.cursor.valueBuffer("idarea"), "JUAS_3")
        qsa.thread_session_free()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
