"""Test_aqsbutton_group module."""

import unittest


class TestAQSButtonGroup(unittest.TestCase):
    """TestAQSButtonGroup Class."""

    def test_full(self) -> None:
        """Full test."""

        from pineboolib.fllegacy.aqsobjects import aqsbuttongroup
        from pineboolib.qsa import qsa

        button_group = aqsbuttongroup.AQSButtonGroup(None, "prueba")
        self.assertTrue(button_group.objectName(), "prueba")
        button_group2 = qsa.AQSButtonGroup(None, "prueba2")
        self.assertTrue(button_group2.objectName(), "prueba2")
