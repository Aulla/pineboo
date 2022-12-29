"""Test pending-replationships module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestPendingRelationships(unittest.TestCase):
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

        obj_area = class_area()
        obj_area.bloqueo = False
        obj_area.idarea = "T"
        obj_area.descripcion = "Area de pruebas de pendingRelationships"
        obj_area.save()

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

        self.assertTrue(hasattr(obj_area, "children"))

        self.assertEqual(len(obj_area.children), 2, "no son dos => %s" % obj_area.children)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
