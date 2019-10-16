"""Test_aqods module."""

import unittest


class TestAQOds(unittest.TestCase):
    """TestAQOds Class."""

    def test_aq_ods_color(self) -> None:

        from pineboolib.qsa import qsa

        val_1 = qsa.AQOdsColor(0xE7E7E7)
        val_2 = qsa.AQOdsColor(242, 150, 141)

        self.assertEqual(val_1, "e7e7e7")
        self.assertEqual(val_2, "f2968d")
