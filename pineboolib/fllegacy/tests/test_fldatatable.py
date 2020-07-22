"""FLDatatable module."""

from pineboolib.fllegacy import fltabledb
from pineboolib import application
from . import fixture_path

from typing import Any

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
        import os

        qsa_sys = systype.SysType()
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa_sys.loadModules(path, False))
        application.PROJECT.actions["flareas"].load_master_widget()

        application.PROJECT.actions["flmodules"].openDefaultForm()

        widget = application.PROJECT.actions["flmodules"]._master_widget

        if widget is None:
            self.assertTrue(widget)
            return

        form = widget.form

        if form is None:
            self.assertTrue(form)
            return

        fltable: Any = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
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
