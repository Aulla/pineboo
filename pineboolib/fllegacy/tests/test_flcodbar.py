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
        cod_bar.setMargin(10)
        self.assertEqual(cod_bar.margin(), 10)
        cod_bar.setScale(1.0)
        self.assertEqual(cod_bar.scale(), 1.0)
        cod_bar.setCut(2.0)
        self.assertEqual(cod_bar.cut(), 2.0)
        cod_bar.setText("TEXTO")
        self.assertEqual(cod_bar.text(), "TEXTO")
        cod_bar.setRotation(10)
        self.assertEqual(cod_bar.rotation(), 10)
        self.assertEqual(cod_bar.fg().value, 2)
        self.assertEqual(cod_bar.bg().value, 3)
        cod_bar.setCaption("9876543210")
        self.assertEqual(cod_bar.caption(), "9876543210")
        cod_bar.setValue("010101010101")
        self.assertEqual(cod_bar.value(), "010101010101")
        self.assertFalse(cod_bar.validBarcode())
        cod_bar._createBarcode()
        self.assertTrue(cod_bar.validBarcode())
        cod_bar.fillDefault()
        self.assertEqual(cod_bar.typeToName(cod_bar.type_()), "Code39")
        self.assertEqual(cod_bar.nameToType("Code39"), 12)
        bar2 = flcodbar.FLCodBar(cod_bar)
        self.assertEqual(cod_bar.typeToName(bar2.type_()), "Code39")
