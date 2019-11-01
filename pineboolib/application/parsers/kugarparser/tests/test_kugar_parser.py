"""Test kugar parser module."""

import unittest
from . import fixture_path
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
        from pineboolib import application
        from pineboolib.plugins.mainform.eneboo import eneboo
        import os

        application.project.main_form = eneboo
        # application.project.main_form.mainWindow = application.project.main_form.MainForm()
        # application.project.main_form.mainWindow.initScript()
        # application.project.main_window = application.project.main_form.mainWindow

        application.project.main_window = application.project.main_form.MainForm()  # type: ignore
        application.project.main_window.initScript()

        qsa_sys = qsa.sys
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        qsa_sys.loadModules(path, False)
        qsa.from_project("flfactppal").iface.valoresIniciales()

        cur_paises = qsa.FLSqlCursor("paises")
        """
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
        """
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

        self.assertTrue(pdf_file)

    def test_parser_tools(self) -> None:
        """Test parser tools."""
        from pineboolib.application.parsers.kugarparser import kparsertools
        from pineboolib import application
        from pineboolib.core.utils.utils_base import load2xml
        from pineboolib.application.database import pnsqlquery, pnsqlcursor
        from pineboolib.qsa import qsa
        import datetime
        import os

        qry = pnsqlquery.PNSqlQuery()
        qry.setTablesList("paises")
        qry.setSelect("codpais, bandera")
        qry.setFrom("paises")
        qry.setWhere("1=1")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        data = qsa.sys.toXmlReportData(qry)
        parser_tools = kparsertools.KParserTools()
        xml_data = load2xml(data.toString()).getroot()

        child = xml_data.findall("Row")[0]
        element = parser_tools.convertToNode(child)
        self.assertTrue(element)
        fecha_ = str(datetime.date.__format__(datetime.date.today(), "%d.%m.%Y"))

        self.assertEqual(parser_tools.getSpecial("Fecha"), fecha_)
        self.assertEqual(parser_tools.getSpecial("[Date]"), fecha_)
        self.assertEqual(parser_tools.getSpecial("NúmPágina", 1), "1")
        self.assertEqual(parser_tools.getSpecial("PageNo", 6), "6")
        self.assertEqual(parser_tools.getSpecial("[NÃºmPÃ¡gina]", 12), "12")
        from PyQt5 import QtCore

        ret_ = QtCore.QLocale.system().toString(float("11.22"), "f", 2)

        self.assertEqual(parser_tools.calculated("11.22", 2, 2), ret_)
        self.assertEqual(parser_tools.calculated("2019-01-31T00:01:02", 3), "31-01-2019")
        self.assertEqual(parser_tools.calculated("codpais", 1, None, child), "ES")

        cur = pnsqlcursor.PNSqlCursor("paises")
        cur.select("1=1")
        cur.first()
        bandera = cur.buffer().value("bandera")
        self.assertEqual(
            parser_tools.parseKey(bandera),
            os.path.abspath("%s/%s.png" % (application.project.tmpdir, bandera)),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
