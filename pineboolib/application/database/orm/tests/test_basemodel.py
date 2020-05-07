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

        instance = qsa.orm_("flareas")
        model_class = instance.__class__

        session = qsa.session()

        instance.session = session
        instance.bloqueo = True
        instance.idarea = "z"
        instance.descripcion = "Descripción M"

        self.assertTrue(instance.save())

    def test_basic_2(self) -> None:
        """Basic test 2."""

        instance = qsa.orm_("flareas")
        model_class = instance.__class__

        session = qsa.session()

        instance.session = session
        instance.bloqueo = True
        instance.idarea = "z"
        instance.descripcion = "Descripción M"

        self.assertFalse(instance.save())

    def test_basic_3(self) -> None:
        """Basic test 3."""

        model_class = qsa.orm_("flareas").__class__
        session = qsa.session()

        area_obj = session.query(model_class).filter(model_class.idarea == "z").first()
        self.assertEqual(area_obj.descripcion, "Descripción M")
        self.assertTrue(area_obj.delete())

    def test_default_value(self) -> None:
        """Test default values when new instances."""

        obj_ = qsa.orm_("flareas")
        self.assertEqual(obj_.bloqueo, True)

    def test_metadata(self) -> None:
        """Test table_metadata."""

        obj_ = qsa.orm_("fltest")
        meta = obj_.table_metadata()
        self.assertTrue(meta)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
