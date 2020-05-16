"""Test for basemodel module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


class TestBaseModel(unittest.TestCase):
    """TestBaseModel Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_default_value(self) -> None:
        """Test default values when new instances."""

        obj_ = qsa.orm_("flareas")()
        self.assertEqual(obj_.bloqueo, True)

    def test_2_metadata(self) -> None:
        """Test table_metadata."""

        obj_class = qsa.orm_("fltest")
        obj_ = obj_class()
        meta = obj_.table_metadata()
        self.assertTrue(meta)
        self.assertTrue(obj_.save())
        obj_.session.commit()

    def test_serial(self) -> None:
        """Test serial field."""

        class_fltest = qsa.orm_("fltest")
        obj_ = class_fltest()
        self.assertEqual(obj_.id, 2)

    def test_3_get(self) -> None:
        """Test get classmethod."""

        class_fltest = qsa.orm_("fltest")
        obj_ = class_fltest.get(1)
        self.assertTrue(obj_)

    #
    #         self.assertTrue(obj_)
    #         obj_2 = class_fltest.get(1)
    #         self.assertTrue(obj_2)
    #         self.assertEqual(obj_, obj_2)
    #         obj_3 = class_fltest.query().get(1)
    #         self.assertEqual(obj_, obj_3)
    #         self.assertTrue(obj_3)
    #         obj_4 = class_fltest.query().get(2)
    #         self.assertFalse(obj_4)
    #         self.assertEqual(obj_3.id, 1)
    #         self.assertNotEqual(obj_, obj_4)
    #
    #         obj_5 = class_fltest.get(1)
    #         self.assertTrue(obj_5.delete())
    #         obj_5.session.commit()
    # ===============================================================================

    def test_integrity(self) -> None:
        """test _check_integrity."""

        obj_ = qsa.orm_("flmodules")()
        obj_.idmodulo = "mod2"
        obj_.idarea = "F"

        self.assertFalse(obj_.save())
        obj_.descripcion = "PRUEBA"
        self.assertFalse(obj_.save())
        obj_2 = qsa.orm_("flareas")()
        obj_2.idarea = "F"
        obj_2.descripcion = "Area"
        self.assertTrue(obj_2.save())
        obj_2.session.commit()

        self.assertTrue(obj_.save())
        obj_3 = qsa.orm_("flmodules")()
        obj_3.idmodulo = "mod1"
        obj_3.idarea = "G"
        obj_3.descripcion = "PRUEBA"
        self.assertTrue(obj_3.save(False))

    def test_relation_m1(self) -> None:
        """Test relationM1."""

        obj_ = qsa.orm_("flareas")()
        obj_.idarea = "T"
        obj_.descripcion = "Area"
        self.assertTrue(obj_.save())
        obj_.session.commit()

        obj_2 = qsa.orm_("flmodules")()
        obj_2.idmodulo = "mod1"
        obj_2.idarea = "T"
        obj_2.descripcion = "PRUEBA relation M1"

        obj_rel = obj_2.relationM1("idarea")
        obj_rel_1 = obj_2.relationM1("idmodulo")
        self.assertFalse(obj_rel_1)
        self.assertTrue(obj_rel)
        self.assertEqual(obj_rel, obj_)

    def test_relation_1m(self) -> None:
        """Test realtion 1M."""

        obj_class = qsa.orm_("flareas")

        obj_ = obj_class.query().get("F")

        obj_2 = qsa.orm_("flmodules")()
        obj_2.idmodulo = "mod4"
        obj_2.idarea = "F"
        obj_2.descripcion = "relation_m1"
        self.assertTrue(obj_2.save())
        # obj_2.session.commit()
        relations_dict = obj_.relation1M("idarea")
        modules_rel = relations_dict["flmodules_idarea"]
        self.assertTrue(obj_2)
        self.assertEqual(len(modules_rel), 2)
        self.assertEqual(modules_rel[1], obj_2)

    def test_(self) -> None:
        """Test."""

        obj_class = qsa.orm_("flareas")
        obj_ = obj_class()
        self.assertEqual(obj_.mode_access, 1)
        obj_.idarea = "O"
        obj_.descripcion = "Descripcion O"
        self.assertTrue(obj_.save())

        obj_new = obj_class.query().get("O")
        obj_new.descripcion = "Nueva descripción"
        self.assertTrue(obj_new.save())

    def test_cache_objects(self) -> None:
        """Test cache objects."""

        obj_class = qsa.orm_("flareas")
        obj_ = obj_class()
        obj_.idarea = "R"
        obj_.descripcion = "Descripción de R"
        self.assertTrue(obj_.save())

        obj_2 = obj_class.query().all()[1]
        self.assertTrue(obj_2)
        self.assertEqual(obj_, obj_2)
        obj_2.descripcion = "Descripción de P"
        self.assertEqual(obj_.descripcion, "Descripción de P")

    def test_z_delete(self) -> None:
        """Test delete."""

        obj_class = qsa.orm_("flareas")
        obj_ = obj_class.get("F")
        self.assertTrue(obj_)
        self.assertEqual(obj_class.query().all()[2], obj_)

        self.assertFalse(obj_.relation1M())

        obj_2_class = qsa.orm_("flmodules")
        obj2_ = obj_2_class()
        obj2_.idarea = "F"
        obj2_.descripcion = "Desc"
        obj2_.idmodulo = "mr1"
        self.assertTrue(obj2_.save())
        obj2_.session.commit()

        self.assertTrue(obj_.relation1M("idarea"))
        self.assertTrue(obj_.delete())
        obj_.session.commit()
        # self.assertFalse(obj_.relation1M("idarea")["flmodules_idarea"])

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
