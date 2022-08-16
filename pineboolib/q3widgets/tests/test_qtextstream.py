"""Test_qtextstream module."""

import unittest
from . import fixture_path

import os


class TestQTextStream(unittest.TestCase):
    """TestQPushButton Class."""

    def test_enabled(self) -> None:
        """Test control."""

        from pineboolib.qsa.qsa import QTextStream, QFile, File

        file_path = fixture_path("test_qtextstream.txt")
        if os.path.exists(file_path):
            os.remove(file_path)

        file_ = QFile(file_path)
        self.assertTrue(file_.open(File.WriteOnly))

        control = QTextStream()
        control.setDevice(file_.ioDevice())
        control.opIn("hola")
        file_.close()

        file2_ = open(file_path, "r", encoding="UTF-8")
        data = file2_.read()
        file2_.close()
        self.assertEqual(data, "hola")

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        file_path = fixture_path("test_qtextstream.txt")
        if os.path.exists(file_path):
            os.remove(file_path)
