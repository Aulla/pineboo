"""Test_flformrecorddb module."""

from pineboolib import application
from . import fixture_path

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestFLFormrecordCursor(unittest.TestCase):
    """TestFLFormrecordCursor Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_cursor_asignment(self) -> None:
        """Test flformrecord cursor assignment"""

        from pineboolib.application import qsadictmodules
        from pineboolib.application.database import pnsqlcursor

        from pineboolib.fllegacy import systype
        import os

        qsa_sys = systype.SysType()
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa_sys.loadModules(path, False))
        application.PROJECT.actions["flareas"].load_master_widget()

        cursor_1 = pnsqlcursor.PNSqlCursor("flareas")
        cursor_1.select()
        cursor_1.setModeAccess(cursor_1.Insert)
        cursor_1.refreshBuffer()
        cursor_1.editRecord(False)

        cursor_3 = pnsqlcursor.PNSqlCursor("flareas")

        module_ = qsadictmodules.QSADictModules.from_project("formRecordflareas")
        self.assertTrue(module_)
        cursor_2 = module_.cursor()

        self.assertNotEqual(cursor_1, cursor_3)
        self.assertEqual(cursor_1, cursor_2)

    def test_flformrecord_show_again_and_others(self) -> None:
        """Check if a FLformRecordDB is shown again"""
        from pineboolib.application import qsadictmodules

        module_ = qsadictmodules.QSADictModules.from_project("formRecordflareas")
        form = module_.form
        self.assertFalse(form.accept())
        pb_cancel = form.pushButtonCancel
        self.assertTrue(pb_cancel.isEnabled())
        form.disablePushButtonCancel()
        self.assertFalse(pb_cancel.isEnabled())
        form.close()
        cursor = module_.form.cursor()
        cursor.select()
        form.lastRecord()
        form.previousRecord()
        form.firstRecord()
        form.nextRecord()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
