"""Test_pnsqlquery module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.database import pnsqlquery, pnsqlcursor
from . import fixture_path


class TestPNSqlQuery_1(unittest.TestCase):
    """TestPNSqlDrivers Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic_1."""
        from pineboolib.application.database import pnparameterquery
        from pineboolib.application.database import pngroupbyquery

        qry = pnsqlquery.PNSqlQuery("fltest2")

        from_param = pnparameterquery.PNParameterQuery("from", "from", 2)
        to_param = pnparameterquery.PNParameterQuery("to", "to", 2)
        from_param.setValue(0)
        to_param.setValue(1)
        qry.addParameter(from_param)
        qry.addParameter(to_param)
        d_ = {}
        d_[from_param.name()] = from_param.value()
        d_[to_param.name()] = to_param.value()
        qry.setParameterDict(d_)

        self.assertEqual(qry.valueParam("to"), 1)
        qry.setValueParam("to", 2)
        self.assertEqual(qry.valueParam("to"), 2)
        self.assertEqual(
            qry.sql(),
            "SELECT id,string_field,date_field,time_field,double_field,bool_field,uint_field,bloqueo FROM fltest"
            + " WHERE id>='0' AND id<='2' ORDER BY fltest.id",
        )

        gr_01 = pngroupbyquery.PNGroupByQuery(0, "string_field")

        qry.addGroup(gr_01)
        g_ = {}
        g_[gr_01.level()] = gr_01.field()

        qry2 = pnsqlquery.PNSqlQuery("fltest")
        qry2.setSelect(
            "id,string_field,date_field,time_field,double_field,bool_field,uint_field,bloqueo"
        )
        qry2.setFrom("fltest")
        qry2.setWhere("id>='0' AND id<='1'")
        qry2.setGroupDict(g_)

        self.assertEqual(
            qry2.sql(),
            "SELECT id,string_field,date_field,time_field,double_field,bool_field,uint_field,bloqueo FROM fltest"
            + " WHERE id>='0' AND id<='1' ORDER BY string_field",
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
        self.assertEqual(qry.tablesList(), ["fake_table"])
        qry.setTablesList(["fake_table_1", "fake_table_2"])
        self.assertEqual(qry.tablesList(), ["fake_table_1", "fake_table_2"])
        qry.setSelect("field_01")
        qry.setFrom("fake_table")
        qry.setWhere("1=1")
        qry.setOrderBy("field_01 ASC")
        self.assertEqual(
            qry.sql(), "SELECT field_01 FROM fake_table WHERE 1=1 ORDER BY field_01 ASC"
        )

        self.assertEqual(qry.fieldNameToPos("field_01"), 0)

        self.assertFalse(qry.exec_())
        self.assertEqual(qry.fieldList(), ["field_01"])
        self.assertFalse(qry.isValid())
        self.assertTrue(qry.isNull("field_01"))
        self.assertEqual(qry.value("field_01"), None)

    def test_basic_3(self) -> None:
        """Test basic_3."""

        qry = pnsqlquery.PNSqlQuery("fake")
        qry.setTablesList("fake_table")
        qry.setSelect("field_01")
        qry.setFrom("fake_table")
        qry.setWhere("1=1")
        qry.setOrderBy("field_01 ASC")
        self.assertEqual(
            qry.sql(), "SELECT field_01 FROM fake_table WHERE 1=1 ORDER BY field_01 ASC"
        )
        self.assertFalse(qry.isForwardOnly())
        qry.setForwardOnly(True)
        self.assertTrue(qry.isForwardOnly())
        qry.setForwardOnly(False)
        self.assertFalse(qry.isForwardOnly())
        self.assertFalse(qry.lastError())
        qry2 = pnsqlquery.PNSqlQuery("fake")
        self.assertFalse(qry2.exec_("SELEFT * FROM DDD"))
        self.assertTrue(qry.lastError())
        self.assertEqual(qry2.driver(), qry2.db().driver())
        self.assertEqual(qry2.numRowsAffected(), 0)
        self.assertTrue(qry2.lastQuery(), "SELEFT * FROM DDD")
        self.assertFalse(qry2.isValid())
        self.assertFalse(qry2.isActive())

    def test_move(self) -> None:
        """Test move functions."""

        cursor_6 = pnsqlcursor.PNSqlCursor("flareas")
        cursor_6.setModeAccess(cursor_6.Insert)
        cursor_6.refreshBuffer()
        cursor_6.setValueBuffer("bloqueo", True)
        cursor_6.setValueBuffer("idarea", "O")
        cursor_6.setValueBuffer("descripcion", "Área de prueba T")
        self.assertTrue(cursor_6.commitBuffer())
        cursor_6.setModeAccess(cursor_6.Insert)
        cursor_6.refreshBuffer()
        cursor_6.setValueBuffer("bloqueo", True)
        cursor_6.setValueBuffer("idarea", "P")
        cursor_6.setValueBuffer("descripcion", "Área de prueba T")
        self.assertTrue(cursor_6.commitBuffer())
        cursor_6.commit()

        qry = pnsqlquery.PNSqlQuery("")
        qry.setTablesList("flareas")
        qry.setSelect("idarea")
        qry.setFrom("flareas")
        qry.setWhere("1=1")
        qry.setOrderBy("idarea ASC")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        val_first = qry.value(0)
        size_ = qry.size()
        self.assertTrue(qry.last())
        val_last = qry.value(0)
        self.assertNotEqual(qry.value("idarea"), val_first)
        self.assertEqual(qry.value("idarea"), qry.value(0))
        self.assertTrue(qry.prev())
        self.assertTrue(qry.seek(0))
        self.assertFalse(qry.isNull("idarea"))
        self.assertEqual(qry.value(0), val_first)
        self.assertFalse(qry.seek(1000))
        self.assertFalse(qry.seek(1000, True))
        self.assertTrue(qry.seek(size_ - 1, True))  # last
        self.assertEqual(qry.value(0), val_last)

    def test_only_inspector(self) -> None:
        """Test only inspector."""

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
        self.assertEqual(qry_2.where(), "astro = 'sol'")
        self.assertEqual(qry_2.from_(), "dias inner join planetas as p on p.id = dias.id")

    def test_date_result(self) -> None:
        """Test date values."""
        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("date_field", "2020-01-01")
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())
        cursor.commit()

        q = pnsqlquery.PNSqlQuery()
        q.setSelect("date_field")
        q.setFrom("fltest")
        q.setWhere("1=1")
        self.assertTrue(q.exec_())
        self.assertTrue(q.next())
        self.assertTrue(q.isNull("date_field"))
        self.assertEqual(q.value(0), "")
        self.assertEqual(q.value("date_field"), "")
        self.assertTrue(q.next())
        self.assertFalse(q.isNull("date_field"))
        self.assertEqual(str(q.value(0)), "2020-01-01T00:00:00")
        self.assertEqual(str(q.value("date_field")), "2020-01-01T00:00:00")
        self.assertTrue(q.next())
        self.assertTrue(q.isNull("date_field"))
        self.assertEqual(q.value(0), "")
        self.assertEqual(q.value("date_field"), "")

    def test_limit_offset(self) -> None:
        """Test limit and offset clausules from a query."""

        cursor = pnsqlcursor.PNSqlCursor("fltest")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertTrue(cursor.commitBuffer())  # 9 rows total!
        cursor.commit()

        q1 = pnsqlquery.PNSqlQuery()
        q1.setSelect("date_field")
        q1.setFrom("fltest")
        q1.setWhere("1 = 1")
        q1.setLimit(4)
        self.assertTrue(q1.exec_())
        self.assertTrue(q1.sql().lower().find("limit") > -1)
        self.assertEqual(q1.size(), 4)

        q2 = pnsqlquery.PNSqlQuery()
        q2.setSelect("date_field")
        q2.setFrom("fltest")
        q2.setWhere("1 = 1")
        q2.setLimit(100)
        q2.setOffset(7)
        self.assertTrue(q2.exec_())
        self.assertTrue(q2.sql().lower().find("offset") > -1)
        self.assertEqual(q2.size(), 2)  # 7 + 2 = 9 rows

        q3 = pnsqlquery.PNSqlQuery()
        q3.setSelect("date_field")
        q3.setFrom("fltest")
        q3.setWhere("1 = 1")
        q3.setOrderBy("date_field")
        q3.setOffset(5)
        self.assertTrue(q3.exec_())
        sql = q3.sql()
        self.assertTrue(sql.lower().find("offset") > -1)
        self.assertTrue(sql.lower().find("order by") > -1)
        self.assertEqual(q3.size(), 4)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


class TestPNSqlQuery_2(unittest.TestCase):
    """TestPNSqlDrivers Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_4(self) -> None:
        """Test basic test 4."""
        from pineboolib.qsa import qsa
        from pineboolib import application
        from pineboolib.application.metadata import pntablemetadata, pnfieldmetadata
        import os

        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        qsa_sys.loadModules(path, False)
        widget = qsa.from_project("flfactppal")
        widget.iface.valoresIniciales()
        cur_clientes = qsa.FLSqlCursor("clientes")
        cur_clientes.setModeAccess(cur_clientes.Insert)
        cur_clientes.refreshBuffer()
        # cur_clientes.setValueBuffer("codigo", "000001")
        cur_clientes.setValueBuffer("nombre", "cliente de prueba")
        cur_clientes.setValueBuffer("cifnif", "01234567H")
        cur_clientes.setValueBuffer("codserie", "A")
        self.assertTrue(cur_clientes.commitBuffer())
        cur_clientes.commit()
        cur_clientes.conn().doTransaction(cur_clientes)

        mtd_tareas = pntablemetadata.PNTableMetaData("tareas")
        field_01 = pnfieldmetadata.PNFieldMetaData(
            "idtarea",
            "Id",
            False,
            True,
            "serial",
            0,
            True,
            True,
            True,
            0,
            0,
            True,
            True,
            False,
            None,
            False,
            False,
            False,
            True,
            False,
        )
        field_02 = pnfieldmetadata.PNFieldMetaData(
            "nombre",
            "Nombre",
            False,
            False,
            "string",
            10,
            False,
            True,
            True,
            0,
            0,
            False,
            False,
            False,
            None,
            False,
            False,
            True,
            False,
            False,
        )
        field_03 = pnfieldmetadata.PNFieldMetaData(
            "fechaini",
            "Fecha Inicial",
            True,
            False,
            "date",
            0,
            False,
            True,
            True,
            0,
            0,
            False,
            False,
            False,
            None,
            False,
            False,
            True,
            False,
            False,
        )
        field_04 = pnfieldmetadata.PNFieldMetaData(
            "fechafinal",
            "Fecha Final",
            True,
            False,
            "date",
            0,
            False,
            True,
            True,
            0,
            0,
            False,
            False,
            False,
            None,
            False,
            False,
            True,
            False,
            False,
        )
        mtd_tareas.addFieldMD(field_01)
        mtd_tareas.addFieldMD(field_02)
        mtd_tareas.addFieldMD(field_03)
        mtd_tareas.addFieldMD(field_04)
        self.assertEqual(
            mtd_tareas.fieldListArray(False), ["idtarea", "nombre", "fechaini", "fechafinal"]
        )
        application.project.conn_manager.manager().cache_metadata_["tareas"] = mtd_tareas
        application.project.conn_manager.manager().createTable("tareas")
        self.assertTrue(application.project.conn_manager.manager().existsTable("tareas"))

        cur_tareas = qsa.FLSqlCursor("tareas")
        self.assertEqual(
            cur_tareas.metadata().fieldListArray(False),
            ["idtarea", "nombre", "fechaini", "fechafinal"],
        )

        cur_tareas.setModeAccess(cur_tareas.Insert)
        cur_tareas.refreshBuffer()
        # cur_tareas.setValueBuffer("idtarea", 1)
        cur_tareas.setValueBuffer("nombre", "prueba1")
        self.assertTrue(cur_tareas.commitBuffer())
        cur_tareas.setModeAccess(cur_tareas.Insert)
        cur_tareas.refreshBuffer()
        # cur_tareas.setValueBuffer("idtarea", 2)
        cur_tareas.setValueBuffer("nombre", "prueba2")
        cur_tareas.setValueBuffer("fechaini", str(qsa.Date()))
        cur_tareas.setValueBuffer("fechafinal", str(qsa.Date()))
        self.assertTrue(cur_tareas.commitBuffer())
        cur_tareas.setModeAccess(cur_tareas.Insert)
        cur_tareas.refreshBuffer()
        # cur_tareas.setValueBuffer("idtarea", 3)
        cur_tareas.setValueBuffer("nombre", "prueba3")
        cur_tareas.setValueBuffer("fechaini", str(qsa.Date()))
        cur_tareas.setValueBuffer("fechafinal", str(qsa.Date()))
        self.assertTrue(cur_tareas.commitBuffer())
        cur_tareas.setModeAccess(cur_tareas.Insert)
        cur_tareas.refreshBuffer()
        cur_tareas.setValueBuffer("nombre", "prueba4")
        cur_tareas.setValueBuffer("fechaini", str(qsa.Date()))
        self.assertTrue(cur_tareas.commitBuffer())
        cur_tareas.setModeAccess(cur_tareas.Insert)
        cur_tareas.refreshBuffer()
        # cur_tareas.setValueBuffer("idtarea", 3)
        cur_tareas.setValueBuffer("nombre", "prueba5")
        cur_tareas.setValueBuffer("fechafinal", str(qsa.Date()))
        self.assertTrue(cur_tareas.commitBuffer())
        cur_tareas.commit()

        qry = qsa.FLSqlQuery()
        qry.setSelect("idtarea,nombre,fechaini,fechafinal")
        qry.setFrom("tareas")
        qry.setWhere("1=1")
        qry.setOrderBy("idtarea")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        self.assertEqual(qry.value("fechaini"), "")
        self.assertEqual(qry.value("fechafinal"), "")
        self.assertTrue(qry.next())
        self.assertNotEqual(qry.value("fechaini"), "")
        self.assertNotEqual(qry.value("fechafinal"), "")
        self.assertTrue(qry.next())
        self.assertNotEqual(qry.value("fechaini"), "")
        self.assertNotEqual(qry.value("fechafinal"), "")
        self.assertTrue(qry.next())
        self.assertNotEqual(qry.value("fechaini"), "")
        self.assertEqual(qry.value("fechafinal"), "")
        self.assertTrue(qry.next())
        self.assertEqual(qry.value("fechaini"), "")
        self.assertNotEqual(qry.value("fechafinal"), "")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
