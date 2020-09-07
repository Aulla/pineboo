"""Test_xmlaction module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application


class TestXMLAction(unittest.TestCase):
    """TestXMLAction Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic."""

        action = application.PROJECT.actions["flareas"]
        self.assertEqual(action._name, "flareas")
        self.assertEqual(action._table, "flareas")
        self.assertEqual(action._master_form, "master")
        self.assertEqual(action._record_form, "flareas")
        self.assertEqual(action._master_script, "flmasterareas")
        self.assertEqual(action._record_script, "")

        action2 = application.PROJECT.actions["flmodules"]
        self.assertEqual(action2._name, "flmodules")
        self.assertEqual(action2._table, "flmodules")
        self.assertEqual(action2._master_form, "master")
        self.assertEqual(action2._record_form, "flmodulos")
        self.assertEqual(action2._master_script, "")
        self.assertEqual(action2._record_script, "flmodules")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
