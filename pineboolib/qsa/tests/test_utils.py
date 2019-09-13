"""Test utils module."""

import unittest

from pineboolib.qsa import utils


class TestUtils(unittest.TestCase):
    """Test Utils module."""

    def test_parse_int(self) -> None:
        """Test parse_int function."""

        val_1 = utils.parseInt("123", 10)
        self.assertEqual(val_1, 123)
        val_2 = utils.parseInt("11", 2)
        self.assertEqual(val_2, 3)
        val_3 = utils.parseInt("123,99", 10)
        self.assertEqual(val_3, 123)
        val_4 = utils.parseInt("0xFE", 16)
        self.assertEqual(val_4, 254)
        val_5 = utils.parseInt(100.0023, 10)
        self.assertEqual(val_5, 100)
        val_6 = utils.parseInt(100, 2)
        self.assertEqual(val_6, 4)
        val_7 = utils.parseInt("99")
        self.assertEqual(val_7, 99)

    def test_parse_float(self) -> None:
        """Test parse_float function."""

        val_1 = utils.parseFloat(100)
        self.assertEqual(val_1, 100.0)
        val_2 = utils.parseFloat(100.01)
        self.assertEqual(val_2, 100.01)
        val_3 = utils.parseFloat("66000")
        self.assertEqual(val_3, 66000.0)
        val_4 = utils.parseFloat("66000.2122")
        self.assertEqual(val_4, 66000.2122)
        val_5 = utils.parseFloat("12:00:00")
        self.assertEqual(val_5, 12)
        val_6 = utils.parseFloat("12:59:00")
        self.assertTrue(val_6 > 12.98 and val_6 < 12.99)
