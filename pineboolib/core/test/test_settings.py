"""Test_settings module."""

from PyQt6 import QtWidgets  # type: ignore[import]

import unittest
from pineboolib.loader.main import init_testing, finish_testing

from .. import settings


class TestSettings(unittest.TestCase):
    """TestSettings Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_raises(self) -> None:
        """Test errors."""

        setting = settings.PinebooSettings("TEST")

        with self.assertRaises(Exception):
            sett = setting._value(  # type: ignore [arg-type] # noqa : F821
                QtWidgets.QWidget(), None  # type: ignore [arg-type] # noqa : F821
            )

        with self.assertRaises(TypeError):
            sett = setting.load_value(  # type: ignore [arg-type] # noqa : F821
                QtWidgets.QSizePolicy  # type: ignore [arg-type] # noqa : F821
            )

        with self.assertRaises(TypeError):
            sett = setting.load_value(QtWidgets.QLabel())  # type: ignore [arg-type] # noqa : F821

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
