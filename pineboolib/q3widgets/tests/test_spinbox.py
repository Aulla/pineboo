"""Test spinbox module."""
import unittest


class TestSpinBox(unittest.TestCase):
    """TestSpinBox class."""

    def test_basic(self) -> None:
        """Test basic."""

        from pineboolib.q3widgets import spinbox

        sb_ = spinbox.SpinBox()
        sb_.maximum = 100
        sb_.minimum = 50
        sb_.value = 75

        self.assertEqual(sb_.maximum, 100)
        self.assertEqual(sb_.minimum, 50)
        self.assertEqual(sb_.value, 75)

        sb_.label = "Prueba"
        self.assertEqual(sb_.label, "Prueba")
