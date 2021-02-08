"""Test_load_script module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application import load_script
from . import fixture_path

import os


class TestLoadScript(unittest.TestCase):
    """TestVirtualExists Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic1(self) -> None:
        """Test basic 1."""

        db_path = fixture_path(".")
        static_path = fixture_path(".")

        file_name = "test_file.txt"

        with open(os.path.join(db_path, file_name), "w"):
            pass

        file_path = fixture_path(file_name)
        load_script._build_static_flag(file_path, db_path, static_path)

        f1_ = open(file_path, "rb")
        data = f1_.read()
        self.assertNotEqual(data.decode(), "")

    def test_basic2(self) -> None:
        """Test basic 2."""

        file_name = "test_file.txt"
        file_path = fixture_path(file_name)
        load_script._resolve_flag(file_path, "uno", "dos")

        load_script._remove(file_path)
        self.assertFalse(os.path.exists(file_path))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
