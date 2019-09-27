"""Test classes module."""

import unittest
import os


class TestClasses(unittest.TestCase):
    """Test classes."""

    def test_qdir(self) -> None:
        """Test qdir class."""

        from pineboolib.qsa import qsa

        dir_ = qsa.QDir(".", "*.py *.pyo")
        path_ = os.path.abspath(dir_.path())
        self.assertTrue(dir_.exists())
        self.assertTrue(dir_.isReadable())
        self.assertEqual(dir_.absPath(), qsa.QDir(path_))
