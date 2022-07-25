"""Test_flutil module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestFLUtil(unittest.TestCase):
    """Test FLUtil class."""

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
        cx_ = cursor_areas.db()

        util = qsa.FLUtil()
        self.assertEqual(util.sqlSelect("flareas", "descripcion", "idarea='Y'"), "123oX")
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"]), "123oX"
        )
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], 0), "123oX"
        )
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], cx_), "123oX"
        )
        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], 0, "default"),
            "123oX",
        )

        self.assertEqual(
            util.sqlSelect("flareas", "descripcion", "idarea='Y'", ["flareas"], 0, cx_), "123oX"
        )

    def test_basic_1(self) -> None:
        """ "Test basic 1."""

        from pineboolib.qsa import qsa

        util = qsa.FLUtil()

        self.assertEqual(util.partDecimal(1.21), 21)
        self.assertEqual(util.partInteger(12.345), 12)
        result = "CIENTO VEINTITRES MILLONES CUATROCIENTOS CINCUENTA Y SEIS MIL SETECIENTOS OCHENTA"
        result += " Y NUEVE EUROS CON VEINTIUN CÉNTIMOS"
        self.assertEqual(util.enLetraMonedaEuro(123456789.21), result)
        self.assertEqual(util.enLetraMonedaEuro(100), "CIEN EUROS")
        self.assertEqual(util.enLetraMonedaEuro(5000), "CINCO MIL EUROS")
        self.assertEqual(util.enLetraMonedaEuro(6002), "SEIS MIL DOS EUROS")
        self.assertEqual(util.enLetraMonedaEuro(13), "TRECE EUROS")
        self.assertEqual(util.enLetraMonedaEuro(-10), "MENOS DIEZ EUROS")
        self.assertEqual(util.enLetraMonedaEuro(5125), "CINCO MIL CIENTO VEINTICINCO EUROS")
        self.assertEqual(util.letraDni(12345678), "Z")
        self.assertEqual(util.nombreCampos("flareas"), ["3", "bloqueo", "idarea", "descripcion"])
        self.assertEqual(util.calcularDC(30660001), "2")
        self.assertEqual(util.formatoMiles("12345"), "12.345")
        self.assertEqual(util.formatoMiles("-12.05"), "-12,05")
        self.assertFalse(util.numCreditCard("5539110012141618"))
        self.assertTrue(util.numCreditCard("3716820019271998"))

    def test_dates(self) -> None:
        """Test dates functions."""
        from pineboolib.qsa import qsa

        util = qsa.FLUtil()

        self.assertEqual(str(util.addDays("30-11-2020", 2)), "2020-12-02T00:00:00")
        self.assertEqual(str(util.addDays("2021-12-31", 2)), "2022-01-02T00:00:00")
        self.assertEqual(str(util.addDays("2021-12-31T00:01:00", 2)), "2022-01-02T00:00:00")
        self.assertEqual(str(util.addMonths("2021-12-31", 12)), "2022-12-31T00:00:00")
        self.assertEqual(str(util.addMonths("01-10-2021", 12)), "2022-10-01T00:00:00")
        self.assertEqual(str(util.addYears("01-10-2021", 12)), "2033-10-01T00:00:00")
        self.assertEqual(str(util.addYears("2021-10-01", 12)), "2033-10-01T00:00:00")
        self.assertEqual(util.daysTo(qsa.Date("2019-07-12"), qsa.Date("2019-07-15")), 3)
        self.assertEqual(util.daysTo(qsa.Date("2019-07-01"), qsa.Date("2019-11-15")), 137)
        self.assertEqual(util.daysTo(qsa.Date("2019-07-01"), qsa.Date("2019-03-15")), -108)
        self.assertEqual(util.dateAMDtoDMA("2019-12-01"), "01-12-2019")
        self.assertEqual(util.dateAMDtoDMA("20"), "")
        self.assertEqual(util.dateDMAtoAMD("20"), "")

    def test_basic_2(self) -> None:
        """Test basic 2."""
        from PyQt6 import QtCore  # type: ignore[import]

        from pineboolib.fllegacy import flutil

        util = flutil.FLUtil()

        self.assertEqual(util.buildNumber("123.4533", "", 2), "123.45")
        self.assertEqual(util.buildNumber("123.451000", "", 3), "123.451")
        self.assertEqual(util.buildNumber("123.451000", "", 1), "123.5")
        self.assertEqual(util.buildNumber("123.451000", "", 2), "123.45")
        self.assertEqual(util.buildNumber("-123.451000", "", 2), "-123.45")
        self.assertEqual(util.buildNumber("-123.4", "", 2), "-123.40")

        self.assertEqual(util.nameBD(), "temp_db")
        self.assertEqual(util.nameUser(), "memory_user")
        self.assertEqual(util.getIdioma(), QtCore.QLocale().name()[:2])

    def test_basic_3(self) -> None:
        """Test basic 3."""
        from pineboolib.fllegacy import flutil

        util = flutil.FLUtil()
        self.assertEqual(util.roundFieldValue("100.0193", "fltest", "double_field"), "100.02")
        self.assertEqual(util.sha1("123456"), "7C4A8D09CA3762AF61E59520943DC26494F8941B")

    def test_sql(self) -> None:
        """Test sql functions."""
        from pineboolib.fllegacy import flutil, flsqlcursor
        from pineboolib.qsa import qsa

        ar_1 = qsa.Array("idarea", "descripcion")
        ar_2 = qsa.Array("G", "area test 2")

        util = flutil.FLUtil()
        self.assertTrue(util.sqlInsert("flareas", ["idarea", "descripcion"], ["T", "area test 1"]))
        self.assertTrue(util.sqlInsert("flareas", ar_1, ar_2))
        cur = flsqlcursor.FLSqlCursor("flareas")
        cur.select()
        self.assertEqual(cur.size(), 2)

        res_1 = util.sqlSelect("flareas", "COUNT(idarea)", "1=1")
        self.assertEqual(res_1, 2)

        res_2 = util.quickSqlSelect("flareas", "COUNT(idarea)", "1=1")
        self.assertEqual(res_2, 2)

        self.assertTrue(
            util.sqlUpdate("flareas", "descripcion", "area test modificado", "idarea ='T'")
        )
        self.assertEqual(
            util.quickSqlSelect("flareas", "descripcion", "idarea ='T'"), "area test modificado"
        )

        self.assertTrue(util.execSql("SELECT COUNT(*) FROM flareas WHERE 1=1", "default"))
        self.assertFalse(util.execSql("SELECT COUNT(*) FROG flareas WHERE 1=1", "default"))

        self.assertTrue(util.sqlDelete("flareas", "idarea ='T'", "default"))
        cur.refresh()
        self.assertEqual(cur.size(), 1)
        self.assertTrue(util.quickSqlDelete("flareas", "idarea ='G'", "default"))
        cur.refresh()
        self.assertEqual(cur.size(), 0)

    def test_field_functions(self) -> None:
        """Test field functions."""
        from pineboolib.fllegacy import flutil

        util = flutil.FLUtil()

        self.assertEqual(util.formatValue("string", "uno", True), "'UNO'")
        self.assertEqual(util.formatValue("uint", 1233, False), "1233")
        self.assertEqual(util.formatValue("double", 1233, False), "1233")
        self.assertEqual(util.formatValue("bool", True, False), "1")

        self.assertTrue(util.fieldDefaultValue("bloqueo", "flareas"))
        self.assertFalse(util.fieldIsCompoundKey("idarea", "flareas"))
        self.assertTrue(util.fieldIsPrimaryKey("idarea", "flareas"))
        self.assertTrue(util.fieldAllowNull("icono", "flmodules"))
        self.assertFalse(util.fieldAllowNull("idarea", "flareas"))
        self.assertEqual(util.fieldAliasToName("Icono", "flmodules"), "icono")
        self.assertEqual(util.fieldNameToAlias("icono", "flmodules"), "Icono")
        self.assertEqual(util.fieldType("icono", "flmodules"), 6)
        self.assertEqual(util.fieldLength("descripcion", "flareas"), 100)
        self.assertEqual(util.fieldLength("idarea", "flareas"), 15)
        self.assertEqual(util.fieldLength("bloqueo", "flareas"), 0)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
