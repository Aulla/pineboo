"""Test_actions_slots module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.application import actions_slots


class TestActionsSlots(unittest.TestCase):
    """TestActionsSlots Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test basic."""

        actions_slots.exec_main_script("formareas")
        actions_slots.exec_default_script(application.PROJECT.actions["flreinit"])
        widget = actions_slots.form_record_widget(application.PROJECT.actions["flareas"])
        if widget is not None:
            self.assertTrue(widget._loaded)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
