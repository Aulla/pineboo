"""Test kugar parser module."""

import unittest
from . import fixture_read, fixture_path
from pineboolib.loader.main import init_testing, finish_testing


class TestParser(unittest.TestCase):
    """Test Parsing KUT to PDF."""

    @classmethod
    def setUpClass(cls) -> None:
        """Init test project."""
        init_testing()

    def test_kugar_parser_1(self) -> None:
        """Test parser."""

        from pineboolib.qsa import qsa
        from pineboolib import plugins
        from pineboolib import application
        from pineboolib.plugins.mainform.eneboo import eneboo
        import os

        application.project.main_form = eneboo
        application.project.main_form.mainWindow = application.project.main_form.MainForm()
        application.project.main_form.mainWindow.initScript()
        application.project.main_window = application.project.main_form.mainWindow

        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        qsa_sys.loadModules(path, False)
        cur_paises = qsa.FLSqlCursor("paises")
        cur_paises.setModeAccess(cur_paises.Insert)
        cur_paises.refreshBuffer()
        cur_paises.setValueBuffer("codpais", "ES")
        cur_paises.setValueBuffer("nombre", "ESPAÑA")
        self.assertTrue(cur_paises.commitBuffer())
        cur_paises.setModeAccess(cur_paises.Insert)
        cur_paises.refreshBuffer()
        cur_paises.setValueBuffer("codpais", "PT")
        cur_paises.setValueBuffer("nombre", "PORTUGAL")
        self.assertTrue(cur_paises.commitBuffer())

        cur_paises.select("1=1")
        cur_paises.first()
        init_ = cur_paises.valueBuffer("codpais")
        cur_paises.last()
        last_ = cur_paises.valueBuffer("codpais")
        qry_paises = qsa.FLSqlQuery("paises")
        qry_paises.setValueParam("from", init_)
        qry_paises.setValueParam("to", last_)

        rpt_viewer_ = qsa.FLReportViewer()
        rpt_viewer_.setReportTemplate("paises")
        rpt_viewer_.setReportData(qry_paises)

        rpt_viewer_.renderReport()
        if rpt_viewer_.rptEngine_ and hasattr(rpt_viewer_.rptEngine_, "parser_"):
            pdf_file = rpt_viewer_.rptEngine_.parser_.get_file_name()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
