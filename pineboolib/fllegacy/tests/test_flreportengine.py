"""Test_flreportengine module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa
import os

from . import fixture_path


class TestFLReportEngine(unittest.TestCase):
    """TestSysType Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa.sys.loadModules(path, False))

    def test_report_data(self) -> None:
        """Test eneboopkgs load."""

        qry = qsa.FLSqlQuery()
        qry.setTablesList("flfiles")
        qry.setSelect("count(nombre)")
        qry.setFrom("flfiles")
        qry.setWhere("1=1")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        res = qsa.sys.toXmlReportData(qry)
        self.assertTrue(res.toString(2).find("</KugarData>") > -1)
    
    def test_print(self) -> None
        """Print a report to pdf printer."""

        report_engine = qsa.FLReportViewer

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
