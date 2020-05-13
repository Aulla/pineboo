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

    def test_basic_1(self) -> None:
        """Basic test 1."""

        instance = qsa.orm_("flareas")()
        # model_class = instance.__class__

        session = qsa.session()

        instance.session = session
        instance.bloqueo = True
        instance.idarea = "z"
        instance.descripcion = "Descripción M"

        self.assertTrue(instance.save())

    def test_basic_2(self) -> None:
        """Basic test 2."""

        instance = qsa.orm_("flareas")()
        # model_class = instance.__class__

        session = qsa.session()

        instance.session = session
        instance.bloqueo = True
        instance.idarea = "z"
        instance.descripcion = "Descripción M"

        self.assertFalse(instance.save())

    def test_basic_3(self) -> None:
        """Basic test 3."""

        model_class = qsa.orm_("flareas")
        session = qsa.session()

        area_obj = session.query(model_class).filter(model_class.idarea == "z").first()
        self.assertEqual(area_obj.descripcion, "Descripción M")
        self.assertTrue(area_obj.delete())
        area_obj.session.commit()

    def test_default_value(self) -> None:
        """Test default values when new instances."""

        obj_ = qsa.orm_("flareas")()
        self.assertEqual(obj_.bloqueo, True)

    def test_metadata(self) -> None:
        """Test table_metadata."""

        obj_ = qsa.orm_("fltest")
        meta = obj_().table_metadata()
        self.assertTrue(meta)

    def test_serial(self) -> None:
        """Test serial field."""

        class_fltest = qsa.orm_("fltest")
        obj_ = class_fltest()
        self.assertEqual(obj_.id, 3)

    def test_get(self) -> None:
        """Test get classmethod."""

        class_fltest = qsa.orm_("fltest")
        obj_ = class_fltest()
        self.assertTrue(obj_.save())
        obj_.session.commit()

        self.assertTrue(obj_)
        obj_2 = class_fltest.get(1)
        self.assertTrue(obj_2)
        self.assertEqual(obj_, obj_2)
        obj_3 = class_fltest.query().get(1)
        self.assertEqual(obj_, obj_3)
        self.assertTrue(obj_3)
        obj_4 = class_fltest.query().get(2)
        self.assertFalse(obj_4)
        self.assertEqual(obj_3.id, 1)
        self.assertNotEqual(obj_, obj_4)

        obj_5 = class_fltest.get(1)
        self.assertTrue(obj_5.delete())
        obj_5.session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
