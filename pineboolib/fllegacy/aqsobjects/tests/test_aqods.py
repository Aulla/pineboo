"""Test_aqods module."""

import unittest
from pineboolib.qsa import qsa


class TestAQOds(unittest.TestCase):
    """TestAQOds Class."""

    def test_aq_ods_color(self) -> None:
        """Test AQOdsColor."""

        val_1 = qsa.AQOdsColor(0xE7E7E7)
        val_2 = qsa.AQOdsColor(242, 150, 141)

        self.assertEqual(val_1, "e7e7e7")
        self.assertEqual(val_2, "f2968d")

    def test_aq_ods_row(self) -> None:
        """Test AQOdsRow."""

        generator = qsa.AQOdsGenerator()
        hojas = qsa.AQOdsSpreadSheet(generator)
        hoja = qsa.AQOdsSheet(hojas, "hoja_1")
        row_1 = qsa.AQOdsRow(hoja)
        self.assertTrue(row_1)
        row_1.setFixedPrecision(1)
        row_1.opIn(0.21)
        row_2 = qsa.AQOdsRow(hoja)
        self.assertTrue(row_2)
        style_obj = qsa.AQOdsStyle(19)

        style_obj.alignCenter()
        style_obj.alignLeft()
        style_obj.alignRight()
        style_obj.textBold()
        style_obj.textItalic()
        style_obj.textUnderline()
        style_obj.borderBottom()
        style_obj.borderLeft()
        style_obj.borderRight()
        style_obj.borderTop()

        self.assertTrue(style_obj)
        row_2.opIn(style_obj)
