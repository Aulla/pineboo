"""Test for basemodel module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa


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

        self.assertEqual(len(qsa.orm.models()), 17)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
