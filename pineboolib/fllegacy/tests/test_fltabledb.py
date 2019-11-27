"""Test_fltabledb module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestFLTableDB(unittest.TestCase):
    """Test FLTableDB class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_export_to_ods(self) -> None:
        """Test export to ods."""
        from pineboolib.fllegacy import flformdb, fltabledb
        from pineboolib import application

        application.project.actions["flareas"].openDefaultForm()

        form = application.project.actions["flareas"].mainform_widget
        # form = flformdb.FLFormDB(None, action)
        # self.assertTrue(form)
        # form.load()
        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        self.assertTrue(fltable)
        fltable.exportToOds()
        # self.assertTrue(form._loaded)
        # form.close()
        # self.assertFalse(form._loaded)
        # form.close()
        # self.assertFalse(form._loaded)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
