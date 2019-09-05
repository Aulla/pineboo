"""Test_pnsqlquery module."""

import unittest
from pineboolib.loader.main import init_testing
from pineboolib.application.database import pnsqlquery


class TestPNSqlQuery(unittest.TestCase):
    """TestPNSqlDrivers Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic_1."""
        from pineboolib.application.database import pnparameterquery

        qry = pnsqlquery.PNSqlQuery("fltest2")

        from_param = pnparameterquery.PNParameterQuery("from", "from", 2)
        to_param = pnparameterquery.PNParameterQuery("to", "to", 2)
        from_param.setValue(0)
        to_param.setValue(1)
        qry.addParameter(from_param)
        qry.addParameter(to_param)
        self.assertEqual(qry.valueParam("to"), 1)
        self.assertEqual(
            qry.sql(),
            "SELECT id,string_field,date_field,time_field,double_field,bool_field,uint_field,bloqueo FROM fltest"
            + " WHERE id>='0' AND id<='1' ORDER BY fltest.id",
        )
        self.assertEqual(qry.name(), "fltest2")
        self.assertEqual(qry.where(), "id>=[from] AND id<=[to]")
        self.assertEqual(qry.orderBy(), "fltest.id")
        qry.setSelect(["id", "fltest.string_field"])
        self.assertEqual(len(qry.parameterDict()), 2)
        self.assertEqual(len(qry.groupDict()), 1)
        self.assertEqual(qry.fieldList(), ["id", "fltest.string_field"])
        self.assertEqual(qry.posToFieldName(0), "id")
        self.assertEqual(qry.posToFieldName(1), "fltest.string_field")
        self.assertEqual(qry.fieldNameToPos("fltest.string_field"), 1)
        self.assertEqual(qry.fieldNameToPos("string_field"), 1)
        qry.setName("fltest2_dos")

        self.assertEqual(qry.name(), "fltest2_dos")
        self.assertEqual(len(qry.fieldMetaDataList()), 2)

    def test_basic_2(self) -> None:
        """Test basic_2."""

        qry = pnsqlquery.PNSqlQuery("fake")
        qry.setTablesList("fake_table")
        qry.setSelect("field_01")
        qry.setFrom("fake_table")
        qry.setWhere("1=1")
        qry.setOrderBy("field_01 ASC")
        self.assertEqual(
            qry.sql(), "SELECT field_01 FROM fake_table WHERE 1=1 ORDER BY field_01 ASC"
        )
        self.assertFalse(qry.exec_())
        self.assertEqual(qry.fieldList(), ["field_01"])
        self.assertFalse(qry.isValid())
        self.assertTrue(qry.isNull("field_01"))
        self.assertEqual(qry.value("field_01"), None)

    def test_only_inspector(self) -> None:
        """Test basic_3."""

        qry = pnsqlquery.PNSqlQuery("fake")
        qry.exec_(
            "SELECT SUM(munitos), dia, noche FROM dias WHERE astro = 'sol' GROUP BY dias.minutos ORDER BY dia ASC, noche DESC"
        )
        self.assertEqual(qry.tablesList(), ["dias"])
        self.assertEqual(qry.from_(), "dias")
        self.assertEqual(qry.fieldList(), ["sum(munitos)", "dia", "noche"])
        self.assertEqual(qry.select(), "sum(munitos),dia,noche")
        self.assertEqual(qry.orderBy(), "dia asc, noche desc")
        self.assertEqual(qry.where(), "astro = 'sol'")

        qry_2 = pnsqlquery.PNSqlQuery("fake")
        qry_2.exec_(
            "SELECT SUM(munitos), dia, noche, p.nombre FROM dias INNER JOIN planetas AS "
            + "p ON p.id = dias.id WHERE astro = 'sol' GROUP BY dias.minutos ORDER BY dia ASC, noche DESC"
        )
        self.assertEqual(qry_2.tablesList(), ["dias", "planetas"])
        self.assertEqual(qry_2.fieldNameToPos("planetas.nombre"), 3)
        self.assertEqual(qry_2.fieldList(), ["sum(munitos)", "dia", "noche", "p.nombre"])
        self.assertEqual(qry_2.fieldNameToPos("nombre"), 3)
        self.assertEqual(qry_2.fieldNameToPos("p.nombre"), 3)
        self.assertEqual(qry_2.posToFieldName(3), "p.nombre")
        self.assertEqual(qry_2.posToFieldName(2), "noche")
