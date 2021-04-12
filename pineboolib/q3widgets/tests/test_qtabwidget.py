"""Test_qtabwidget module."""
from PyQt6 import QtGui  # type: ignore[import]

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from .. import qtabwidget
from .. import qwidget


class TestQTabWidget(unittest.TestCase):
    """TestQTabWidget class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic 1."""

        qtab = qtabwidget.QTabWidget()
        self.assertTrue(qtab is not None)
        widget = qwidget.QWidget()
        widget.setObjectName("prueba")
        qtab.addTab(widget, QtGui.QIcon(), "prueba")
        qtab.setTabEnabled("prueba", False)
        qtab.setTabEnabled("prueba", True)
        qtab.showPage("prueba")
        self.assertEqual(qtab.count(), 1)
        self.assertEqual(qtab.indexByName("prueba"), 0)
        qtab.removePage(0)
        self.assertEqual(qtab.count(), 0)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
