"""FLDateEdit module."""

from PyQt6 import QtWidgets, QtCore  # type: ignore[import]

import unittest

from .. import fldateedit
from pineboolib.loader.main import init_testing, finish_testing


class TestFLDateEdit(unittest.TestCase):
    """Test FLDataTable class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self):
        """Test basic 1."""
        parent = QtWidgets.QWidget()

        control = fldateedit.FLDateEdit(parent, "nombre")
        self.assertTrue(control is not None)
        date = QtCore.QDate.fromString(str("01-01-2000"), control.DMY)
        self.assertTrue(date is not None)
        control.setDate(date)
        control.setOrder("dd.MM.yyyy")
        # self.assertTrue(len(str(control.getDate()).split(".")) == 3)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
