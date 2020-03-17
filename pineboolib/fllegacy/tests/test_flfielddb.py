"""Test_flfieldDB module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.fllegacy import fldateedit


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
        from pineboolib.core.utils import utils_base
        from PyQt5 import QtWidgets

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
        field.status()
        field.selectAll()
        field.setShowAlias(True)
        self.assertTrue(field.showAlias())
        self.assertTrue(field.showEditor())
        field.setKeepDisabled(False)

        comp_mode = field.autoCompletionMode()
        self.assertTrue(comp_mode)
        field.setAutoCompletionMode(comp_mode)
        field.refresh()
        field.refreshQuick()

        del field.editor_
        field.initFakeEditor()
        field.field_map_value_ = field
        field.setMapValue()

        field.setNoShowed()
        field.autoCompletionUpdateValue()
        field.searchValue()

        field_icono = module_.child("flfielddb_3")
        icono_file = utils_base.filedir("./core/images/icons", "flfielddb.png")
        field_icono.setPixmap(icono_file)
        pix = field_icono.pixmap()
        field_icono.setPixmapFromPixmap(pix)

        clb = QtWidgets.QApplication.clipboard()
        clb.setPixmap(pix)
        field_icono.setPixmapFromClipboard()

        # module_.form.close()

    def test_button_in_empty_buffer(self) -> None:
        """Check that the button is displayed on a control that points to a non-existent field."""
        from pineboolib.fllegacy import flfielddb
        from pineboolib.qsa import dictmodules

        module_ = dictmodules.from_project("formRecordflmodules")
        parent = module_.parent()
        new_field = flfielddb.FLFieldDB(parent)
        new_field.setObjectName("fake_control")
        new_field.setFieldName("tes_field")
        new_field.load()
        lay = parent.layout()
        lay.addWidget(new_field)

        field = module_.child("fake_control")
        self.assertTrue(field)
        field.showWidget()
        self.assertEqual(field._push_button_db.isHidden(), False)

    def test_fldateedit_empty_value(self) -> None:
        """Check if the empty value is 00-00-0000."""
        from pineboolib.fllegacy import flfielddb
        from pineboolib.application.metadata import pnfieldmetadata
        from pineboolib.qsa import dictmodules
        from pineboolib import application

        module_ = dictmodules.from_project("formRecordflmodules")
        parent = module_.parent()
        table_mtd = application.PROJECT.conn_manager.manager().metadata("flmodules")
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
        new_field.setName("date_control")
        self.assertEqual(new_field.objectName(), "date_control")
        new_field.setFieldName(field_mtd.name())
        new_field.load()
        cursor = new_field.cursor()
        self.assertEqual(module_.cursor(), cursor)
        field_mtd_2 = cursor.metadata().field("date_control")
        if field_mtd_2 is None:
            raise Exception("field_mtd_2 is empty!")

        self.assertEqual(field_mtd, field_mtd_2)
        self.assertEqual(field_mtd_2.type(), "date")
        editor = new_field.editor_
        if not isinstance(editor, fldateedit.FLDateEdit):
            raise Exception("wrong control!")
        self.assertEqual(editor.DMY, "dd-MM-yyyy")
        editor.date = "01-02-2001"
        self.assertEqual(editor.date, "2001-02-01")
        editor.date = None
        self.assertEqual(editor.date, "")

        new_field.setValue("2011-03-02")
        self.assertEqual(str(new_field.value())[:10], "2011-03-02")

        new_field.refresh()
        new_field.refreshQuick()
        new_field.setActionName("nueva_action")
        self.assertEqual(new_field.actionName(), "nueva_action")

        new_field.setFilter("nuevo_filtro")
        self.assertEqual(new_field.filter(), "nuevo_filtro")

        new_field.setForeignField("foreignfield")
        self.assertEqual(new_field.foreignField(), "foreignfield")

        new_field.setFieldRelation("fieldrelation")
        self.assertEqual(new_field.fieldRelation(), "fieldrelation")

        new_field.toggleAutoCompletion()

        table_mtd.removeFieldMD(field_mtd.name())
        # lay = parent.layout()
        # lay.addWidget(new_field)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
