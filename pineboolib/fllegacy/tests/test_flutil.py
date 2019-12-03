"""Test_flutil module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing


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
        """Test sqlSelect."""

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
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], 0, "default"),
            "123oX",
        )

        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], 0, cx), "123oX"
        )

    def test_basic_1(self) -> None:
        """"Test basic 1."""

        from pineboolib.qsa import qsa

        util = qsa.FLUtil()

        self.assertEqual(util.partDecimal(1.21), 21)
        self.assertEqual(util.partInteger(12.345), 12)
        result = "CIENTO VEINTITRES MILLONES CUATROCIENTOS CINCUENTA Y SEIS MIL SETECIENTOS OCHENTA"
        result += " Y NUEVE EUROS CON VEINTIUN CÉNTIMOS"
        self.assertEqual(util.enLetraMonedaEuro(123456789.21), result)

        self.assertEqual(util.letraDni(12345678), "Z")
        self.assertEqual(util.nombreCampos("flareas"), [3, "bloqueo", "idarea", "descripcion"])
        self.assertEqual(util.calcularDC(30660001), "2")
        self.assertEqual(util.formatoMiles("12345"), "12.345")
        self.assertFalse(util.numCreditCard("5539110012141618"))
        self.assertTrue(util.numCreditCard("3716820019271998"))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
