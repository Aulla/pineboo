"""Test sessions module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestSessions(unittest.TestCase):
    """TestSessions Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_selective_dirty(self) -> None:
        """Test basic."""

        cursor = qsa.FLSqlCursor("fltest")
        cursor.db().transaction()
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("double_field", 0.1)
        cursor.setValueBuffer("string_field", "a")
        cursor.setValueBuffer("int_field", 1)
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("double_field", 0.2)
        cursor.setValueBuffer("string_field", "b")
        cursor.setValueBuffer("int_field", 2)
        self.assertTrue(cursor.commitBuffer())
        class_ = qsa.orm_("fltest")
        numero = qsa.util.sqlSelect("fltest", "min(id)", "1=1")

        obj1 = class_.get(numero)
        self.assertTrue(obj1)
        setattr(obj1, "_new_object", False)
        obj1._common_init()
        curobj = obj1.get_cursor()

        curobj.setValueBuffer("bool_field", True)
        self.assertEqual(curobj.valueBuffer("id"), numero)
        self.assertTrue(len(curobj._parent.changes()) > 0)

        self.assertTrue(
            len(curobj._parent.session.dirty) > 0,
            "dirty está vacio , y se esperaban datos (%s)" % (curobj._parent.session.dirty),
        )

        cursor2 = qsa.FLSqlCursor("fltest")
        numero = qsa.util.sqlSelect("fltest", "max(id)", "1=1")
        cursor2.select("id=%s" % (numero))
        self.assertTrue(cursor2.first())
        self.assertEqual(cursor2.valueBuffer("id"), numero)
        cursor2.setModeAccess(cursor2.Edit)
        cursor2.refreshBuffer()
        cursor2.setValueBuffer("bool_field", False)
        self.assertTrue(cursor2.commitBuffer())
        self.assertTrue(len(curobj._parent.session.dirty) == 1, curobj._parent.session.dirty)
        cursor3 = qsa.FLSqlCursor("fltest")
        cursor3.select("id=%s" % (numero))
        cursor3.first()
        cursor3.refreshBuffer()
        self.assertTrue(cursor3.valueBuffer("bool_field") is False)
        cursor.db().commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
