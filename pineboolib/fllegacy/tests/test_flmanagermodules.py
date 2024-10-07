"""Test_flmanager module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing

from pineboolib import application


class TestFLManagerModules(unittest.TestCase):
    """TestFLManager Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic1(self) -> None:
        """Basic test."""

        manager_modules_ = application.PROJECT.conn_manager.managerModules()
        self.assertEqual(manager_modules_.listAllIdModules(), ["sys"])

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
