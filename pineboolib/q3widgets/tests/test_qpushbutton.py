"""Test_qpushbutton module."""

import unittest


class TestQPushButton(unittest.TestCase):
    """TestQPushButton Class."""

    def test_enabled(self) -> None:
        """Test if the control enabled/disabled."""

        from pineboolib.q3widgets import qpushbutton

        button = qpushbutton.QPushButton()
        self.assertTrue(button.enabled)
        button.enabled = False
        self.assertFalse(button.enabled)

    def test_label(self) -> None:
        """Test label."""

        from pineboolib.q3widgets import qpushbutton

        button = qpushbutton.QPushButton()
        button.setTextLabel("etiqueta")
        text: str = str(button.text)  # type: ignore
        self.assertEqual(text, "etiqueta")
