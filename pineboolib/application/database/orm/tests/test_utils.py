"""Test for basemodel module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa

from .. import utils as orm_utils


class TestUtils(unittest.TestCase):
    """Testutils Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic 1."""

        model_areas = qsa.orm_("flareas")
        model_areas_2 = qsa.orm.flareas
        self.assertEqual(model_areas, model_areas_2)

    def test_basic_2(self) -> None:
        """Test basic 2."""

        self.assertTrue(len(qsa.orm.models()) in [20, 17])

    def test_dynamic_filter(self) -> None:
        """Test dynamic filter."""

        session_ = qsa.session()
        self.assertTrue(session_)
        model_class = qsa.orm_("flareas")

        new_ = model_class()
        new_.idarea = "ir"
        new_.descripcion = "descripcion ir"
        self.assertTrue(new_.save())

        obj_ = model_class.get("ir")

        self.assertEqual(obj_, new_)
        query = orm_utils.DynamicFilter(query=session_.query(model_class), model_class=model_class)
        query.set_filter_condition_from_string(
            "%s = %s order by idarea desc" % ("idarea", "ir".replace(" ", "_|_space_|_"))
        )
        ret_ = query.return_query().first()
        self.assertEqual(query.order_by, [["idarea", "desc"]])
        self.assertEqual(ret_.idarea, "ir")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
