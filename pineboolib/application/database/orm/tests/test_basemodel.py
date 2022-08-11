"""Test for basemodel module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa

from sqlalchemy import orm


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

        self.assertTrue(obj_.get_session_from_connection())
        self.assertTrue(obj_.copy())

    def test_cursor_mode_access(self) -> None:
        """Test mode access."""

        obj_ = qsa.orm.flareas()
        self.assertTrue(obj_.module_iface)

        obj2_ = qsa.orm.flareas()
        self.assertTrue(obj2_.module_iface)

        cursor = obj_.cursor
        self.assertEqual(cursor.modeAccess(), cursor.Insert)
        obj_.idarea = "TT"
        self.assertEqual(cursor.modeAccess(), cursor.Insert)

        obj1_ = qsa.orm.flareas.get("O")
        self.assertTrue(obj1_.module_iface)
        self.assertFalse(obj1_.changes())
        self.assertEqual(obj1_.pk, "O")
        self.assertEqual(obj1_.cursor.modeAccess(), obj1_.cursor.Browse)
        obj1_.descripcion = "prueba nuevo"
        obj1_.pk = "O"
        self.assertTrue(obj1_.changes())
        self.assertEqual(obj1_.cursor.modeAccess(), obj1_.cursor.Edit)
        obj1_.allow_buffer_changed("idarea", False)
        self.assertTrue("idarea" in obj1_._deny_buffer_changed)
        obj1_.allow_buffer_changed("idarea", True)
        self.assertFalse("idarea" in obj1_._deny_buffer_changed)

    def test_2_metadata(self) -> None:
        """Test table_metadata."""
        session = qsa.session()
        obj_class = qsa.orm_("fltest")
        obj_ = obj_class(session=session)
        meta = obj_.table_metadata()
        self.assertTrue(meta)
        session.begin()
        self.assertTrue(obj_.save())
        obj_.session.commit()

    def test_serial(self) -> None:
        """Test serial field."""
        qsa.thread_session_new()
        class_fltest = qsa.orm_("fltest")
        obj_ = class_fltest()
        self.assertEqual(obj_.id, 2)

        obj2_ = class_fltest(serial=False)
        self.assertEqual(obj2_.id, None)

        class_fltest2 = qsa.orm_("fltest")
        obj3_ = class_fltest2()
        self.assertEqual(obj3_.id, 3)

    def test_3_get(self) -> None:
        """Test get classmethod."""

        class_fltest = qsa.orm_("fltest")
        session = qsa.session()
        obj_ = class_fltest.get(1, session)
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

        session = qsa.thread_session_current()
        qsa.thread_session_free()
        new_session = qsa.thread_session_new()
        self.assertNotEqual(session, new_session)
        obj_ = qsa.orm_("flmodules")()
        obj_.idmodulo = "mod2"
        obj_.idarea = "F"
        with self.assertRaises(Exception):
            obj_.save()

        obj_.descripcion = "PRUEBA"
        with self.assertRaises(Exception):
            obj_.save()

        obj_2 = qsa.orm_("flareas")()
        obj_2.idarea = "F"
        obj_2.descripcion = "Area"
        obj_2.session.begin()
        self.assertTrue(obj_2.save())
        obj_2.session.commit()

        self.assertTrue(obj_.relationM1("idarea"))
        self.assertEqual(obj_.get_transaction_level(), -1)

        self.assertTrue(obj_.save())
        self.assertEqual(qsa.FLUtil().sqlSelect("flmodules", "idmodulo", "idarea='F'"), "mod2")
        obj_3 = qsa.orm_("flmodules")()
        obj_3.idmodulo = "mod1"
        obj_3.idarea = "G"
        obj_3.descripcion = "PRUEBA"

        self.assertEqual(
            obj_3.changes(),
            {
                "bloqueo": True,
                "descripcion": "PRUEBA",
                "idarea": "G",
                "idmodulo": "mod1",
                "version": "0.0",
            },
        )

        self.assertFalse(obj_3.is_being_changed())
        self.assertTrue(obj_3.is_being_created())
        self.assertFalse(obj_3.is_being_deleted())

        obj_3.mode_access = 3
        self.assertEqual(obj_3.mode_access, 3)

    def test_integrity_2(self) -> None:
        """Test integrity"""

        orm = qsa.orm

        class_modulos = qsa.orm.flmodules
        self.assertTrue(class_modulos)
        mod_1 = class_modulos()
        mod_1.idmodulo = "prueba"
        mod_1.descripcion = "descripcion"
        mod_1.idarea = ""
        with self.assertRaises(Exception):
            mod_1._check_integrity()

        class_test4 = orm.fltest4
        self.assertTrue(class_test4)
        obj_ = class_test4()
        obj_.idarea = 22
        obj_.id_test = 0
        obj_.other_field = "NO"
        # with self.assertRaises(Exception):
        #    obj_._check_integrity()

        obj_.id_test = 1
        obj_._check_integrity()

    def test_relation_m1(self) -> None:
        """Test relationM1."""
        qsa.thread_session_free()
        qsa.session()
        current_session = qsa.thread_session_current()
        if current_session is not None:
            current_session.begin()
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
            self.assertEqual(obj_rel.idarea, obj_.idarea)

    def test_relation_1m(self) -> None:
        """Test realtion 1M."""

        obj_class = qsa.orm_("flareas")

        obj_2 = qsa.orm_("flmodules")()
        obj_2.idmodulo = "mod4"
        obj_2.idarea = "F"
        obj_2.descripcion = "relation_m1"
        self.assertTrue(obj_2.save())
        obj_ = obj_class.query(obj_2.session).get("F")
        self.assertTrue(obj_)
        # obj_2.session.commit()
        relations_dict = obj_.relation1M("idarea")
        modules_rel = relations_dict["flmodules_idarea"]
        self.assertTrue(obj_2)
        self.assertEqual(len(modules_rel), 2)
        self.assertEqual(modules_rel[1].idmodulo, obj_2.idmodulo, modules_rel)

    def test_(self) -> None:
        """Test."""
        session = qsa.session()
        session.begin()
        obj_class = qsa.orm_("flareas")
        obj_ = obj_class(session=session)
        self.assertEqual(obj_.mode_access, 0)  # Insert
        obj_.idarea = "O"
        obj_.descripcion = "Descripcion O"
        self.assertTrue(obj_.save())
        obj_.session.commit()

        session.begin()
        obj_new = obj_class.get("O", session)
        obj_new.descripcion = "Nueva descripción"
        self.assertTrue(obj_new.is_being_changed())
        self.assertFalse(obj_new.is_being_created())
        self.assertTrue(obj_new.save())
        session.commit()

    def test_cache_objects(self) -> None:
        """Test cache objects."""
        qsa.thread_session_new()
        obj_class = qsa.orm_("flareas")
        obj_ = obj_class()
        obj_.idarea = "R"
        obj_.descripcion = "Descripción de R"
        self.assertTrue(obj_.save())

        obj_2 = obj_class.query(obj_.session).all()[1]
        self.assertTrue(obj_2)
        self.assertEqual(obj_, obj_2, obj_class.query(obj_.session).all())
        obj_2.descripcion = "Descripción de P"
        self.assertEqual(obj_.descripcion, "Descripción de P")

    def test_counter(self) -> None:
        """Test counter."""
        qsa.thread_session_new()
        obj_class = qsa.orm_("fltest3")
        obj_ = obj_class(counter=True)
        self.assertEqual(obj_.counter_field, "000001")
        obj_class = qsa.orm_("fltest3")
        obj2_ = obj_class()
        self.assertEqual(obj2_.counter_field, None)

    def test_z_delete(self) -> None:
        """Test delete."""

        qsa.thread_session_free()
        self.assertFalse(qsa.thread_session_current())

        session = qsa.thread_session_new()
        obj_class = qsa.orm.flareas

        obj_ = obj_class.get("F")
        self.assertEqual(session, obj_.session)

        self.assertTrue(obj_)
        self.assertEqual(obj_class.query().all()[2].idarea, obj_.idarea)

        self.assertFalse(obj_.relation1M())

        obj_2_class = qsa.orm_("flmodules")
        obj2_ = obj_2_class()
        obj2_.idarea = "F"
        obj2_.descripcion = "Desc"
        obj2_.idmodulo = "mr1"
        self.assertTrue(obj2_.save())
        session.begin()

        obj2_.session.commit()
        session.begin()
        self.assertEqual(len(obj_.relation1M("idarea")["flmodules_idarea"]), 3)
        self.assertEqual(obj_.relation1M("idarea")["flmodules_idarea"][2].idmodulo, obj2_.idmodulo)
        self.assertTrue(obj_.delete())
        obj_.session.commit()
        # self.assertFalse(obj_.relation1M("idarea")["flmodules_idarea"])

    def test_z_real_relation(self) -> None:
        """Test real relation."""

        areas_class = qsa.orm_("flareas")
        modules_class = qsa.orm_("flmodules")

        # modules_class.parent = orm.relationship(
        #    areas_class,
        #    primaryjoin=(modules_class.idarea == areas_class.idarea),
        #    foreign_keys=[areas_class.idarea],
        # )

        areas_class.children = orm.relationship(
            modules_class,
            primaryjoin=(areas_class.idarea == modules_class.idarea),
            foreign_keys=[modules_class.idarea],
            cascade="delete,delete-orphan",  # "all, delete-orphan"
        )
        current_session = qsa.thread_session_current()
        if current_session:

            current_session.begin()

            obj_areas = areas_class()
            obj_areas.idarea = "I"
            obj_areas.descripcion = "Descripción I"
            self.assertTrue(obj_areas.save())
            obj_areas.session.commit()

            obj_modules_1 = modules_class()
            obj_modules_1.idarea = "I"
            obj_modules_1.descripcion = "modulo 1"
            obj_modules_1.idmodulo = "M1"

            obj_modules_2 = modules_class()
            obj_modules_2.idarea = "I"
            obj_modules_2.descripcion = "modulo 2"
            obj_modules_2.idmodulo = "M2"

            current_session.begin()

            self.assertTrue(obj_modules_1.save())
            self.assertTrue(obj_modules_2.save())

            obj_modules_1.session.commit()

            # self.assertEqual(obj_modules_1.parent[0], obj_areas)
            # self.assertEqual(obj_modules_2.parent[0], obj_areas)
            self.assertEqual(
                len(modules_class.query().filter(modules_class.idarea == "I").all()), 2
            )
            self.assertEqual(len(obj_areas.children), 2)

            # for child in obj_areas.children: #Modo correcto para lanzar eventos ... si no hay legacy_metadata.deleteCascade()
            #    self.assertTrue(child.delete())
            obj_areas.session.begin()
            self.assertTrue(obj_areas.delete())
            obj_areas.session.commit()
            self.assertEqual(
                len(modules_class.query().filter(modules_class.idarea == "I").all()), 0
            )

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
