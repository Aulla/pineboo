"""Test_messagebox module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.q3widgets import messagebox


class TestMessageBox(unittest.TestCase):
    """TestMessageBox Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_buttons(self) -> None:
        """Test if the buttons exists"""
        msg_box = messagebox.MessageBox()
        self.assertTrue(hasattr(msg_box, "Yes"))
        self.assertTrue(hasattr(msg_box, "No"))
        self.assertTrue(hasattr(msg_box, "NoButton"))
        self.assertTrue(hasattr(msg_box, "Ok"))
        self.assertTrue(hasattr(msg_box, "Cancel"))
        self.assertTrue(hasattr(msg_box, "Ignore"))

    def test_types(self) -> None:
        """Test types."""

        msg_question = messagebox.MessageBox.question("pruebaq")
        self.assertTrue(msg_question is not None)
        msg_warning = messagebox.MessageBox.warning("pruebaw")
        self.assertTrue(msg_warning is not None)
        msg_info = messagebox.MessageBox.information("pruebai")
        self.assertTrue(msg_info is not None)
        msg_crit = messagebox.MessageBox.critical("pruebac")
        self.assertTrue(msg_crit is not None)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
