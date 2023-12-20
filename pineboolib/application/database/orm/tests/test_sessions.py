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

    def test_relation_session_flush(self):
        class_area = qsa.orm_("flareas", False)
        class_modulo = qsa.orm_("flmodules", False)

        self.assertFalse(class_area is None)
        self.assertFalse(class_modulo is None)

        obj_area = class_area()
        obj_area.bloqueo = False
        obj_area.idarea = "TS"
        obj_area.descripcion = "Area de pruebas de pendingRelationships"
        obj_area.save()

        session = obj_area._session

        obj_modulo_1 = class_modulo()
        obj_modulo_1.bloqueo = False
        obj_modulo_1.idmodulo = "M1"
        obj_modulo_1.idarea = obj_area.idarea
        obj_modulo_1.descripcion = "Modulo de pruebas 1 de pendingrelationships"
        obj_modulo_1.version = "0.1"
        obj_modulo_1.save()

        obj_modulo_2 = class_modulo()
        obj_modulo_2.bloqueo = False
        obj_modulo_2.idmodulo = "M2"
        obj_modulo_2.idarea = obj_area.idarea
        obj_modulo_2.descripcion = "Modulo de pruebas 2 de pendingrelationships"
        obj_modulo_2.version = "0.1"
        session.add(obj_modulo_2)

        self.assertTrue(obj_modulo_2 in session.new)
        self.assertTrue(len(session.dirty) == 0)

        obj_area.descripcion = "Area altered!"
        self.assertTrue(len(session.dirty) == 1)

        obj_modulo_1.descripcion = "."
        self.assertTrue(len(session.dirty) == 2)

        obj_modulo_2.save()

        self.assertTrue(len(session.dirty) == 2)

    def test_session_flush(self):
        class_area = qsa.orm_("flareas", False)

        self.assertFalse(class_area is None)

        obj_area_1 = class_area()
        session = obj_area_1._session
        obj_area_1.bloqueo = False
        obj_area_1.idarea = "TS11"
        obj_area_1.descripcion = "."
        obj_area_1.save()
        self.assertFalse(obj_area_1 in session.dirty)
        obj_area_1.descripcion = "1"
        self.assertTrue(obj_area_1 in session.dirty)
        obj_area_1.save()

        obj_area_2 = class_area()
        obj_area_2.bloqueo = False
        obj_area_2.idarea = "TS12"
        obj_area_2.descripcion = "."
        session.add(obj_area_2)
        self.assertTrue(obj_area_2 in session.new)
        obj_area_2.save()

        obj_area_3 = class_area()
        obj_area_3.bloqueo = False
        obj_area_3.idarea = "TS13"
        obj_area_3.descripcion = "."
        session.add(obj_area_3)

        obj_area_4 = class_area()
        obj_area_4.bloqueo = False
        obj_area_4.idarea = "TS14"
        obj_area_4.descripcion = "."
        session.add(obj_area_4)

        self.assertTrue(obj_area_3 in session.new)
        obj_area_1.descripcion = ".."
        obj_area_2.descripcion = ".."

        self.assertTrue(obj_area_1 in session.dirty)
        self.assertTrue(obj_area_2 in session.dirty)

        obj_area_3.save()
        self.assertTrue(obj_area_1 in session.dirty)
        self.assertTrue(obj_area_2 in session.dirty)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
