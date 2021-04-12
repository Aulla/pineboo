"""Test_flformsearchdb module."""

from . import fixture_path

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa
from pineboolib.core.utils import utils_base

from PyQt6 import QtWidgets  # type: ignore[import]


class TestFLFormsearchDB(unittest.TestCase):
    """TestFLFormsearchDB Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_initialization(self) -> None:
        """Test flformrecord cursor assignment"""

        import os

        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa.sys.loadModules(path, False))

        form_search_1 = qsa.FLFormSearchDB("bancos")
        self.assertEqual(form_search_1.cursor().metadata().name(), "bancos")
        self.assertEqual(form_search_1.action().name(), "bancos")
        self.assertEqual(form_search_1.parent(), QtWidgets.QApplication.activeModalWidget())

        parent_2 = QtWidgets.QWidget()

        form_search_2 = qsa.FLFormSearchDB("clientes", parent_2)
        self.assertEqual(form_search_2.cursor().metadata().name(), "clientes")
        self.assertEqual(form_search_2.action().name(), "clientes")
        self.assertEqual(form_search_2.parent(), parent_2)

        parent_3 = QtWidgets.QWidget()
        cur_3 = qsa.FLSqlCursor("proveedores")
        print(1, cur_3)
        form_search_3 = qsa.FLFormSearchDB(cur_3, "proveedores", parent_3)
        print(2, cur_3)
        self.assertEqual(form_search_3.cursor().metadata().name(), "proveedores")
        self.assertEqual(form_search_3.action().name(), "proveedores")
        self.assertEqual(form_search_3.parent(), parent_3)
        self.assertEqual(form_search_3.cursor(), cur_3)

        parent_4 = None
        cur_4 = qsa.FLSqlCursor("proveedores")
        form_search_4 = qsa.FLFormSearchDB(cur_4, "proveedores", parent_4)
        self.assertEqual(form_search_4.cursor().metadata().name(), "proveedores")
        self.assertEqual(form_search_4.action().name(), "proveedores")
        self.assertEqual(form_search_4.parent(), QtWidgets.QApplication.activeModalWidget())
        self.assertEqual(form_search_4.cursor(), cur_4)

        self.assertEqual(qsa.sys.interactiveGUI(), "Pineboo")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()


class TestNoFLFormsearchDB(unittest.TestCase):
    """TestNoFLFormsearchDB Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        utils_base.FORCE_DESKTOP = False
        init_testing()

    def test_no_gui(self) -> None:
        """Test FlformSearch call with no GUI"""

        self.assertEqual(qsa.sys.interactiveGUI(), "Pinebooapi")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        utils_base.FORCE_DESKTOP = True
        finish_testing()
