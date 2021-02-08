"""Test_pntablemetadata module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing

from pineboolib.application.metadata import pntablemetadata
from pineboolib import application


class TestCreatePNTableMetaData(unittest.TestCase):
    """TestCreatePNTableMetaData Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test create a PNTableMetaData."""

        from pineboolib.application.metadata import pntablemetadata

        mtd = pntablemetadata.PNTableMetaData("prueba_1", "Alias de prueba_1", "qry_prueba_1")
        mtd_2 = pntablemetadata.PNTableMetaData("prueba_2")

        self.assertEqual(mtd.name(), "prueba_1")
        self.assertEqual(mtd_2.name(), "prueba_2")
        self.assertEqual(mtd.alias(), "Alias de prueba_1")
        self.assertEqual(mtd.isQuery(), True)

        mtd.setName("prueba_2")
        mtd.setAlias("Alias de prueba_2")
        mtd.setQuery("qry_prueba_2")

        self.assertEqual(mtd.query(), "qry_prueba_2")

    def test_basic_2(self) -> None:
        """Test functions."""

        from pineboolib.application.database import pnsqlcursor

        cur = pnsqlcursor.PNSqlCursor("fltest2")
        mtd = cur.metadata()

        self.assertEqual(mtd.fieldType("string_field"), 3)
        self.assertEqual(mtd.fieldType("time_field"), 27)
        self.assertEqual(mtd.fieldType("date_field"), 26)
        self.assertEqual(mtd.fieldType("double_field"), 19)
        self.assertEqual(mtd.fieldType("bool_field"), 18)
        self.assertEqual(mtd.fieldType("uint_field"), 17)
        self.assertEqual(mtd.fieldType("bloqueo"), 200)

        self.assertFalse(mtd.fieldIsCounter("string_field"))
        self.assertTrue(mtd.fieldAllowNull("string_field"))
        self.assertFalse(mtd.fieldAllowNull("bloqueo"))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


class TestCopyPNTableMetaData(unittest.TestCase):
    """TestCopyPNTableMetaData Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test copy a PNTableMetaData from other."""

        mtd_1 = application.PROJECT.conn_manager.manager().metadata("flgroups")
        if mtd_1:
            self.assertEqual(mtd_1.alias(), "Grupos de Usuarios")
        mtd_2 = pntablemetadata.PNTableMetaData(mtd_1 or "")

        self.assertEqual(mtd_2.name(), "flgroups")
        self.assertEqual(mtd_2.alias(), "Grupos de Usuarios")
        self.assertEqual(mtd_2.fieldNameToAlias("idgroup"), "Nombre")
        self.assertEqual(mtd_2.primaryKey(), "idgroup")
        self.assertEqual(mtd_2.fieldAliasToName("Nombre"), "idgroup")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


class TestPNTableMetaData(unittest.TestCase):
    """TestPNTableMetaData Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test manage a PNTableMetaData."""

        mtd = application.PROJECT.conn_manager.manager().metadata("flgroups")
        mtd_2 = application.PROJECT.conn_manager.manager().metadata("flareas")
        self.assertTrue(mtd is not None)
        self.assertTrue(mtd_2 is not None)
        if mtd is not None and mtd_2 is not None:
            self.assertEqual(mtd.fieldType("descripcion"), 3)
            self.assertEqual(mtd.fieldIsPrimaryKey("descripcion"), False)
            self.assertEqual(mtd.fieldIsPrimaryKey("idgroup"), True)
            self.assertEqual(mtd.fieldIsIndex("descripcion"), 1)
            self.assertEqual(mtd.fieldLength("descripcion"), 100)
            self.assertEqual(mtd.fieldPartInteger("descripcion"), 0)
            self.assertEqual(mtd.fieldPartDecimal("descripcion"), 0)
            self.assertEqual(mtd.fieldCalculated("descripcion"), False)
            self.assertEqual(mtd.fieldVisible("descripcion"), True)

            field = mtd.field("descripcion")
            self.assertTrue(field is not None)
            if field is not None:
                self.assertEqual(field.name(), "descripcion")

                field_list = mtd.fieldList()
                self.assertEqual(len(field_list), 2)

                field_list_2 = mtd.fieldListArray(False)
                self.assertEqual(field_list_2, ["idgroup", "descripcion"])

                field_list_3 = mtd.fieldListArray(True)
                self.assertEqual(field_list_3, ["flgroups.idgroup", "flgroups.descripcion"])

            mtd.removeFieldMD("descripcion")
            self.assertEqual(mtd.fieldIsIndex("descripcion"), -1)
            self.assertEqual(mtd.fieldIsUnique("idgroup"), False)

            self.assertEqual(mtd.indexPos("idgroup"), 0)
            self.assertEqual(mtd.fieldNames(), ["idgroup"])
            self.assertEqual(mtd_2.fieldNamesUnlock(), ["bloqueo"])

            self.assertEqual(mtd.concurWarn(), False)
            mtd.setConcurWarn(True)
            self.assertEqual(mtd.concurWarn(), True)

            self.assertEqual(mtd.detectLocks(), False)
            mtd.setDetectLocks(True)
            self.assertEqual(mtd.detectLocks(), True)

            self.assertEqual(mtd.FTSFunction(), "")
            mtd.setFTSFunction("1234_5678")
            self.assertEqual(mtd.FTSFunction(), "1234_5678")

            self.assertEqual(mtd.inCache(), False)
            mtd.setInCache(True)
            self.assertEqual(mtd.inCache(), True)

            field_pos_0 = mtd.indexFieldObject(0)
            self.assertEqual(field_pos_0.name(), "idgroup")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


class TestRelationsPNTableMetaData(unittest.TestCase):
    """TestRelationsPNTableMetaData Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test Relations M1 and 1M."""

        mtd_1 = application.PROJECT.conn_manager.manager().metadata("flusers")
        self.assertTrue(mtd_1)
        if mtd_1 is not None:
            self.assertEqual(mtd_1.fieldTableM1("idgroup"), "flgroups")
            self.assertEqual(mtd_1.fieldForeignFieldM1("idgroup"), "idgroup")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


class TestCompoundKeyPNTableMetaData(unittest.TestCase):
    """TestCompoundKeyPNTableMetaData Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test CompoundKey."""

        mtd = application.PROJECT.conn_manager.manager().metadata("flseqs")
        self.assertTrue(mtd is not None)
        if mtd is not None:
            field_list = mtd.fieldListOfCompoundKey("campo")
            self.assertTrue(field_list)
            if field_list:
                self.assertEqual(field_list[0].name(), "campo")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
