"""Test pending-replationships module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestRelationships(unittest.TestCase):
    """TestByteArray Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_list(self):
        """Test list"""

        class_area = qsa.orm_("flareas", False)
        class_modulo = qsa.orm_("flmodules", False)

        self.assertFalse(class_area is None)
        self.assertFalse(class_modulo is None)

        qsa.thread_session_free()
        session = qsa.thread_session_new()

        # nest = session.begin_nested()

        obj_area = class_area()
        obj_area.bloqueo = False
        obj_area.idarea = "T"
        obj_area.descripcion = "Area de pruebas de pendingRelationships"
        obj_area.save()
        self.assertEqual(obj_area.transaction_level, 0)
        # self.assertEqual(len(obj_area.children), 0, "no son cero => %s" % obj_area.children)

        obj_modulo_1 = class_modulo()
        obj_modulo_1.bloqueo = False
        obj_modulo_1.idmodulo = "M1"
        obj_modulo_1.idarea = obj_area.idarea
        obj_modulo_1.descripcion = "Modulo de pruebas 1 de pendingrelationships"
        obj_modulo_1.version = "0.1"
        obj_modulo_1.save()

        obj_modulo_1 = class_modulo()
        obj_modulo_1.bloqueo = False
        obj_modulo_1.idmodulo = "M2"
        obj_modulo_1.idarea = obj_area.idarea
        obj_modulo_1.descripcion = "Modulo de pruebas 2 de pendingrelationships"
        obj_modulo_1.version = "0.1"
        obj_modulo_1.save()

        obj_area = class_area.get("T")

        self.assertTrue(hasattr(obj_area, "children"))
        self.assertEqual(obj_area.transaction_level, 0)
        self.assertEqual(len(obj_area.children), 2, "no son dos => %s" % obj_area.children)

        session.commit()

    def test_children_before_after_commit(self):

        class_area = qsa.orm_("flareas", False)
        class_modulo = qsa.orm_("flmodules", False)

        self.assertFalse(class_area is None)
        self.assertFalse(class_modulo is None)

        qsa.thread_session_free()
        session = qsa.thread_session_new()

        # session.begin()

        obj_area = class_area()
        obj_area.bloqueo = False
        obj_area.idarea = "T1"
        obj_area.descripcion = "Area de pruebas de pendingRelationships"
        self.assertTrue(obj_area.save())

        self.assertEqual(obj_area.transaction_level, 0)

        # self.assertTrue(not obj_area.children)

        obj_modulo_1 = class_modulo()
        self.assertEqual(obj_modulo_1.transaction_level, 0)
        self.assertEqual(obj_modulo_1.session, obj_area.session)

        obj_modulo_1.bloqueo = False
        obj_modulo_1.idmodulo = "T2M1"
        obj_modulo_1.idarea = obj_area.idarea
        obj_modulo_1.descripcion = "Modulo de pruebas 1 de T1"
        obj_modulo_1.version = "0.1"
        self.assertTrue(obj_modulo_1.save())

        obj_modulo_1 = class_modulo()
        obj_modulo_1.bloqueo = False
        obj_modulo_1.idmodulo = "T2M2"
        obj_modulo_1.idarea = obj_area.idarea
        obj_modulo_1.descripcion = "Modulo de pruebas 2 de T1"
        obj_modulo_1.version = "0.1"
        self.assertTrue(obj_modulo_1.save())
        # obj_area.save()

        # current_session = qsa.thread_session_current()
        # self.asserTrue(session.get_transaction())
        # self.assertEqual(current_session.get_transaction(), session.get_transaction())

        self.assertTrue(obj_modulo_1 in obj_area.children, "hijos: %s" % obj_area.children)

        obj_modulo_1.idmodulo = "T2M1_1"
        with self.assertRaises(Exception):
            obj_area.save(relations=["children"])

        obj_modulo_1.idmodulo = "T2M1_2"
        obj_area.save(relations=["children"])  # Guardamos!

        self.assertTrue(obj_modulo_1.idmodulo == "T2M1_2", "idmodulo es %s" % obj_modulo_1.idmodulo)
        self.assertTrue(len(obj_area._session.dirty) == 0)
        self.assertEqual(
            obj_modulo_1.idmodulo, qsa.util.sqlSelect("flmodules", "idmodulo", "idmodulo='T2M1_2'")
        )

        session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
