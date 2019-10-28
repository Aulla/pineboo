"""Test_flfieldDB module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestFLFieldDBString(unittest.TestCase):
    """TestFLFieldDBString Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test string FLFieldDB mode."""

        from pineboolib.qsa import dictmodules
        from pineboolib.application.database import pnsqlcursor

        cursor_1 = pnsqlcursor.PNSqlCursor("flmodules")
        cursor_1.select()
        cursor_1.setModeAccess(cursor_1.Insert)
        cursor_1.refreshBuffer()
        cursor_1.insertRecord(False)

        module_ = dictmodules.from_project("formRecordflmodules")
        self.assertTrue(module_)

        cursor_2 = module_.cursor()
        field = module_.child("flfielddb_5")
        self.assertNotEqual(field, None)
        field.setValue("hola")

        self.assertEqual(cursor_1.valueBuffer("descripcion"), "hola")
        cursor_2.setValueBuffer("descripcion", "nueva hola.")
        self.assertEqual(field.value(), "nueva hola.")

        # module_.form.close()

    def test_button_in_empty_buffer(self) -> None:
        """Check that the button is displayed on a control that points to a non-existent field."""
        from pineboolib.fllegacy import flfielddb
        from pineboolib.qsa import dictmodules

        module_ = dictmodules.from_project("formRecordflmodules")
        parent = module_.widget.parentWidget()
        new_field = flfielddb.FLFieldDB(parent)
        new_field.setObjectName("fake_control")
        new_field.setFieldName("tes_field")
        new_field.load()
        lay = parent.layout()
        lay.addWidget(new_field)

        field = module_.child("fake_control")
        self.assertTrue(field)
        field.showWidget()
        self.assertEqual(field.pushButtonDB.isHidden(), False)

    def test_fldateedit_empty_value(self) -> None:
        """Check if the empty value is 00-00-0000."""
        from pineboolib.fllegacy import flfielddb
        from pineboolib.application.metadata import pnfieldmetadata
        from pineboolib.qsa import dictmodules
        from pineboolib import application

        module_ = dictmodules.from_project("formRecordflmodules")
        parent = module_.widget.parentWidget()
        table_mtd = application.project.conn.useConn("default").manager().metadata("flmodules")
        if table_mtd is None:
            raise Exception("table_mtd is empty!.")
        field_mtd = pnfieldmetadata.PNFieldMetaData(
            "date_control",
            "Date",
            True,
            False,
            "date",
            0,
            False,
            True,
            False,
            0,
            0,
            False,
            False,
            False,
            None,
            False,
            None,
            True,
            False,
            False,
        )
        table_mtd.addFieldMD(field_mtd)
        new_field = flfielddb.FLFieldDB(parent)
        new_field.setObjectName("date_control")
        new_field.setFieldName(field_mtd.name())
        new_field.load()
        cursor = new_field.cursor()
        self.assertEqual(module_.cursor(), cursor)
        field_mtd_2 = cursor.metadata().field("date_control")
        if field_mtd_2 is None:
            raise Exception("field_mtd_2 is empty!")

        self.assertEqual(field_mtd, field_mtd_2)
        self.assertEqual(field_mtd_2.type(), "date")
        self.assertTrue(new_field.editor_)
        self.assertEqual(new_field.editor_.DMY, "dd-MM-yyyy")
        new_field.editor_.date = "01-02-2001"
        self.assertEqual(new_field.editor_.date, "2001-02-01")
        new_field.editor_.date = None
        self.assertEqual(new_field.editor_.date, None)
        table_mtd.removeFieldMD(field_mtd.name())
        # lay = parent.layout()
        # lay.addWidget(new_field)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
