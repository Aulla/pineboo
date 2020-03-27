"""Test_messagebox module."""

import unittest
from pineboolib.q3widgets import messagebox


class TestMessageBox(unittest.TestCase):
    """TestMessageBox Class."""

    def test_buttons(self) -> None:
        """Test if the buttons exists"""
        msg_box = messagebox.MessageBox()
        self.assertTrue(hasattr(msg_box, "Yes"))
        self.assertTrue(hasattr(msg_box, "No"))
        self.assertTrue(hasattr(msg_box, "NoButton"))
        self.assertTrue(hasattr(msg_box, "Ok"))
        self.assertTrue(hasattr(msg_box, "Cancel"))
        self.assertTrue(hasattr(msg_box, "Ignore"))
