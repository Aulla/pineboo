"""Test_flcodbar module."""

import unittest
from pineboolib.fllegacy import flcodbar


class TestFLCodBar(unittest.TestCase):
    """TestFLCodBar Class."""

    def test_basic(self) -> None:
        """Test basic."""

        cod_bar = flcodbar.FLCodBar("12345678")

        self.assertEqual(cod_bar.value(), "12345678")
        self.assertEqual(cod_bar.type_(), 13)
