"""Test_flutil module."""

import unittest


class TestTranslations(unittest.TestCase):
    def test_full(self) -> None:
        from pineboolib.qsa import qsa

        qsa.aqApp.loadTranslationFromModule("sys", "es")

        util = qsa.FLUtil()
        self.assertEqual(util.translate("scripts", "single"), "simple!")
        self.assertEqual(util.translate("scripts", "variable %s") % "uno", "con variable uno!")
        self.assertEqual(
            util.translate("scripts", "multiple variable %s , %s") % ("uno", "dos"),
            "Test uno y dos",
        )
