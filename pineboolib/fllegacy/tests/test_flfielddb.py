"""Test_flfieldDB module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.fllegacy import fldateedit
from datetime import datetime


class TestFLFieldDBString(unittest.TestCase):
    """TestFLFieldDBString Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test string FLFieldDB mode."""

        from pineboolib.application import qsadictmodules
        from pineboolib.application.database import pnsqlcursor
        from pineboolib.core.utils import utils_base
        from PyQt6 import QtWidgets  # type: ignore[import]

        cursor_1 = pnsqlcursor.PNSqlCursor("flmodules")
        cursor_1.select()
        cursor_1.setModeAccess(cursor_1.Insert)
        cursor_1.refreshBuffer()
        cursor_1.insertRecord(False)

        module_ = qsadictmodules.QSADictModules.from_project("formRecordflmodules")
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
        from pineboolib.application import qsadictmodules

        module_ = qsadictmodules.QSADictModules.from_project("formRecordflmodules")
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
        from pineboolib.application import qsadictmodules
        from pineboolib import application

        module_ = qsadictmodules.QSADictModules.from_project("formRecordflmodules")
        parent = module_.parent()
        table_mtd = application.PROJECT.conn_manager.manager().metadata("flmodules")
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
        if table_mtd is not None:
            table_mtd.addFieldMD(field_mtd)
        new_field = flfielddb.FLFieldDB(parent)
        new_field.setName("date_control")
        self.assertEqual(new_field.objectName(), "date_control")
        new_field.setFieldName(field_mtd.name())
        new_field.load()
        cursor = new_field.cursor()
        self.assertEqual(module_.cursor(), cursor)
        field_mtd_2 = cursor.metadata().field("date_control")
        if field_mtd_2 is not None:
            self.assertEqual(field_mtd, field_mtd_2)
            self.assertEqual(field_mtd_2.type(), "date")
        editor = new_field.editor_
        if isinstance(editor, fldateedit.FLDateEdit):
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
            if table_mtd is not None:
                table_mtd.removeFieldMD(field_mtd.name())

                self.assertFalse(
                    application.PROJECT.conn_manager.useConn("default").regenTable(
                        "flmodules", table_mtd
                    )
                )

    def test_basic_2(self) -> None:
        """Test basics 2."""
        from pineboolib.application import qsadictmodules
        from pineboolib.fllegacy import fllineedit

        module_ = qsadictmodules.QSADictModules.from_project("formRecordflmodules")
        field = module_.child("flfielddb_2")
        self.assertTrue(field)
        self.assertEqual(field._text_label_db.text(), "Versión")
        field.setFieldAlias("Versión 2")
        self.assertEqual(field._text_label_db.text(), "Versión 2")

        self.assertTrue(
            isinstance(field.editor_, fllineedit.FLLineEdit),
            "El tipo de campo es %s y se espera qlineedit.QLineEdit" % type(field.editor_),
        )

        self.assertEqual(field.echoMode(), fllineedit.FLLineEdit.EchoMode.Normal)
        field.setEchoMode(fllineedit.FLLineEdit.EchoMode.Password)
        self.assertEqual(field.echoMode(), fllineedit.FLLineEdit.EchoMode.Password)

        self.assertTrue(field.cursor_)

    def test_basic_3(self) -> None:
        """Test basics 3."""
        from pineboolib.qsa import qsa

        cur_test = qsa.FLSqlCursor("fltest")
        cur_test.openFormInMode(cur_test.Insert, False)
        form_ = qsa.from_project("formRecordfltest").form
        self.assertEqual(form_.child("fdb_double").value(), 0.0)
        self.assertEqual(form_.child("fdb_double").editor_.text(), "0.0")
        self.assertEqual(form_.child("fdb_id").value(), None)
        self.assertEqual(form_.child("fdb_date").value(), "")
        self.assertEqual(form_.child("fdb_time").value(), "00:00:00")
        self.assertEqual(form_.child("fdb_uint").value(), 0)
        cursor = form_.cursor()

        self.assertFalse(form_.child("fdb_bool").value())
        cursor.setValueBuffer("bool_field", True)
        self.assertTrue(form_.child("fdb_bool").value())
        cursor.setValueBuffer("uint_field", 10)
        self.assertEqual(form_.child("fdb_uint").value(), 10)
        cursor.setValueBuffer("uint_field", 11.01)
        self.assertEqual(form_.child("fdb_uint").value(), 11)
        cursor.setValueBuffer("uint_field", 12.99)
        self.assertEqual(form_.child("fdb_uint").value(), 12)
        cursor.setValueBuffer("double_field", 6.99)
        self.assertEqual(form_.child("fdb_double").value(), 6.99)
        today = qsa.Date()
        time_now = datetime.now().time()
        cursor.setValueBuffer("date_field", today)
        self.assertEqual(str(form_.child("fdb_date").value())[:10], str(today)[:10])
        cursor.setValueBuffer("time_field", time_now)
        self.assertEqual(form_.child("fdb_time").value(), str(time_now)[:8])

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
