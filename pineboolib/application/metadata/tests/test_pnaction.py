"""Test_pnaction module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.metadata import pnaction
from pineboolib import application
from pineboolib.qsa import qsa


class TestPNAction(unittest.TestCase):
    """TestPNAction class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic1(self) -> None:
        """Test basic 1."""

        qsa.sys.reinit()
        act_struct = application.PROJECT.actions["flareas"]
        self.assertTrue(act_struct is not None)
        act_ = pnaction.PNAction(act_struct)
        self.assertEqual(act_.scriptFormRecord(), "")
        self.assertEqual(act_.scriptForm(), "flmasterareas.qs")
        self.assertEqual(act_.table(), "flareas")
        self.assertEqual(act_.formRecord(), "flareas.ui")
        self.assertEqual(act_.form(), "master.ui")
        act2_ = act_
        self.assertTrue(act2_ == act_)
        self.assertTrue(str(act_) is not None)
        self.assertFalse(act_.class_())

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
