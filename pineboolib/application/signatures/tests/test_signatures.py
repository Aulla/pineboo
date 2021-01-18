"""Test_signatures module."""

import unittest
from pineboolib.qsa import qsa
from pineboolib.loader.main import init_testing, finish_testing
from . import fixture_path
import os


class TestSignatures(unittest.TestCase):
    """TestSignatures class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_qr(self) -> None:
        """test pdf_qr."""

        test_file = fixture_path("test.pdf")
        dest_file = fixture_path("test_result.pdf")

        self.assertTrue(os.path.exists(test_file))
        if os.path.exists(dest_file):
            os.remove(dest_file)

        obj_ = qsa.pdfQr(test_file)
        obj_.set_size(5)
        obj_.set_extension("PNG")
        obj_.set_dpi()
        obj_.set_text("textoa", "textob")
        obj_.set_font("Arial", 8)
        obj_.set_position(100, 100)
        self.assertTrue(obj_.sign(True))
        self.assertTrue(obj_.save_file(dest_file))
        self.assertTrue(obj_.get_qr())

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
