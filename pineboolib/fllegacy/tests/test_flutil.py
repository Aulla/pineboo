"""Test_flutil module."""

import unittest


class TestTranslations(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_translate(self) -> None:
        """Test Translations."""

        from pineboolib.qsa import qsa

        qsa.aqApp.loadTranslationFromModule("sys", "es")

        util = qsa.FLUtil()
        self.assertEqual(util.translate("scripts", "single"), "simple!")
        self.assertEqual(util.translate("scripts", "variable %s") % "uno", "con variable uno!")
        self.assertEqual(
            util.translate("scripts", "multiple variable %s , %s") % ("uno", "dos"),
            "Test uno y dos",
        )

    def test_sqlSelect(self) -> None:

        from pineboolib.qsa import qsa

        cursor_areas = qsa.FLSqlCursor("flareas")
        cursor_areas.setModeAccess(cursor_areas.Insert)
        cursor_areas.refreshBuffer()
        cursor_areas.setValueBuffer("idarea", "Y")
        cursor_areas.setValueBuffer("descripcion", "123oX")
        self.assertTrue(cursor_areas.commitBuffer())
        cx = cursor_areas.db()

        util = qsa.FLUtil()
        self.assertEqual(util.sqlSelect("flareas", "descripcion", "idarea='Y'"), "123oX")
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"]), "123oX"
        )
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], 0), "123oX"
        )
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], cx), "123oX"
        )
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], 0, cx), "123oX"
        )
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], 0, "default"),
            "123oX",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
