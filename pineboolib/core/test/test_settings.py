"""Test_settings module."""

from PyQt5 import QtWidgets, QtCore

import unittest
from pineboolib.loader.main import init_testing, finish_testing

from .. import settings


class TestSettings(unittest.TestCase):
    """TestSettings Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_raises(self):
        """Test errors."""

        setting = settings.PinebooSettings("TEST")

        with self.assertRaises(Exception):
            sett = setting._value(QtWidgets.QWidget(), None)

        with self.assertRaises(TypeError):
            sett = setting.load_value(QtWidgets.QSizePolicy)

        with self.assertRaises(TypeError):
            sett = setting.load_value(QtWidgets.QLabel())

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
