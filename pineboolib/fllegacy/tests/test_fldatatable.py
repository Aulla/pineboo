"""FLDatatable module."""

from pineboolib.fllegacy import fltabledb
from pineboolib import application
from . import fixture_path

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestFLDataTable(unittest.TestCase):
    """Test FLDataTable class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic1(self):
        """Test basic functions."""
        from pineboolib.fllegacy import systype
        from pineboolib.application import actions_slots
        import os

        qsa_sys = systype.SysType()
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        qsa_sys.loadModules(path, False)
        application.PROJECT.actions["flareas"].load()

        actions_slots.open_default_form(application.PROJECT.actions["flmodules"])

        form = application.PROJECT.actions[  # type: ignore [attr-defined] # noqa F821
            "flmodules"
        ].mainform_widget
        # form = flformdb.FLFormDB(None, action)
        # self.assertTrue(form)
        # form.load()
        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        self.assertTrue(fltable)

        fldatatable = fltable.tableRecords()
        self.assertTrue(fldatatable)
        self.assertEqual(fldatatable.fieldName(1), "idmodulo")

        fldatatable.clearChecked()
        fldatatable.setPrimaryKeyChecked("idmodulo", True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
