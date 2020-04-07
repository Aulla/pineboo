"""Test_xmlaction module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from . import fixture_path


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

    def test_basic_2(self) -> None:
        """Test class."""

        from pineboolib.qsa import qsa
        import os

        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        qsa_sys.loadModules(path, False)

        class_usuarios = qsa.class_("usuarios")
        self.assertTrue(class_usuarios)
        self.assertNotEqual(class_usuarios(), class_usuarios())

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
