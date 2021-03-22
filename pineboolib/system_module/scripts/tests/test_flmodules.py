"""Test flmodules module."""


import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import logging, application
from . import fixture_path
from pineboolib.core.utils import utils_base
import codecs

LOGGER = logging.get_logger("eneboo_%s" % __name__)


class TestFlModules(unittest.TestCase):
    """TestFlModules class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        utils_base.FORCE_DESKTOP = True
        init_testing()

    def test_cargar_ficheros(self) -> None:
        """Test load files into Database."""
        from pineboolib.qsa import qsa
        from pineboolib.plugins.mainform import eneboo

        application.PROJECT.main_window = eneboo.MainForm()

        cur_area = qsa.FLSqlCursor("flareas")
        cur_area.select()
        cur_area.setModeAccess(cur_area.Insert)
        cur_area.refreshBuffer()
        cur_area.setValueBuffer("idarea", "sysco")
        cur_area.setValueBuffer("descripcion", "area sysco")
        self.assertTrue(cur_area.commitBuffer())

        cur_mod = qsa.FLSqlCursor("flmodules")
        cur_mod.select()
        cur_mod.setModeAccess(cur_mod.Insert)
        cur_mod.refreshBuffer()
        cur_mod.setValueBuffer("idarea", "sysco")
        cur_mod.setValueBuffer("idmodulo", "mod_sysco")
        cur_mod.setValueBuffer("version", "1")
        cur_mod.setValueBuffer("descripcion", "modulo mod_sysco")
        self.assertTrue(cur_mod.commitBuffer())

        # qsa.from_project("formRecordflmodules").cargarFicheros(fixture_path("scripts"), "*.py")
        cursor = qsa.FLSqlCursor("flmodules")
        cursor.insertRecord(False)
        form = qsa.from_project("formRecordflmodules").form
        cursor_form = form.cursor()
        self.assertEqual(cursor, cursor_form)
        cursor_form.setValueBuffer("idmodulo", "mod_sysco")
        cursor_form.setValueBuffer("idarea", "sysco")
        # cursor_form.commitBuffer()
        qsa.from_project("formRecordflmodules").load_files(fixture_path("scripts"), "*.py")
        qsa.from_project("formRecordflmodules").load_files(fixture_path("scripts"), "*.qs")
        self.assertTrue(
            qsa.sys.disableObj(qsa.from_project("formRecordflmodules").form, "toolButtonEdit")
        )

        cursor_form.commit()

        self.assertTrue(
            qsa.sys.setObjText(
                qsa.from_project("formRecordflmodules").form, "flfielddb_5", "prueba"
            )
        )
        self.assertTrue(
            qsa.from_project("formRecordflmodules").child("flfielddb_5").value(), "prueba"
        )
        self.assertTrue(
            qsa.sys.filterObj(qsa.from_project("formRecordflmodules").form, "flfielddb_5", "prueba")
        )
        self.assertTrue(
            qsa.sys.testAndRun(qsa.from_project("formRecordflmodules").form, "flfielddb_5")
        )

        qry = qsa.FLSqlQuery()
        qry.setSelect("contenido")
        qry.setFrom("flfiles")
        qry.setWhere("nombre = 'prueba.py'")
        qry.exec_()
        data_qry_py = ""
        if qry.first():
            data_qry_py = qry.value(0)

        qry2 = qsa.FLSqlQuery()
        qry2.setSelect("contenido")
        qry2.setFrom("flfiles")
        qry2.setWhere("nombre = 'prueba.qs'")
        qry2.exec_()
        data_qry_qs = ""
        if qry2.first():
            data_qry_qs = qry2.value(0)

        file_py = codecs.open(fixture_path("scripts/prueba.py"), "r", encoding="UTF8")
        data_file_py = file_py.read()
        file_py.close()

        file_qs = codecs.open(fixture_path("scripts/prueba.qs"), "r", encoding="ISO-8859-1")
        data_file_qs = file_qs.read()
        file_qs.close()

        file_qs_bad = codecs.open(
            fixture_path("scripts/prueba.qs"), "r", encoding="UTF8", errors="ignore"
        )
        data_file_qs_bad = file_qs_bad.read()
        file_qs_bad.close()

        self.assertEqual(data_file_py, data_qry_py)
        self.assertEqual(data_file_qs, data_qry_qs)
        self.assertNotEqual(data_file_qs_bad, data_qry_qs)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
