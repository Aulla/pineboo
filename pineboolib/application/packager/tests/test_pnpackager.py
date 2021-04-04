"""Test_process module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.packager import pnpackager
from . import fixture_path


class TestPNPAckager(unittest.TestCase):
    """TestUnpacker Class."""


class TestProcess(unittest.TestCase):
    """TestProcess Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_pnpackager(self) -> None:
        """Test eneboopkgs load."""
        from pineboolib import application
        from pineboolib.fllegacy import systype
        from pineboolib.qsa import qsa
        import os

        file_name = "%s/package.eneboopkg" % application.PROJECT.tmpdir
        if os.path.exists(file_name):
            os.remove(file_name)
        packager = pnpackager.PNPackager(file_name)
        result = packager.pack(fixture_path("principal"))
        self.assertTrue(result, packager.errorMessages())
        self.assertTrue(os.path.exists(file_name))
        self.assertTrue(os.path.exists("%s/modules.def" % os.path.dirname(file_name)))
        self.assertTrue(os.path.exists("%s/files.def" % os.path.dirname(file_name)))

        qsa_sys = systype.SysType()
        self.assertTrue(qsa_sys.loadModules(file_name, False))

        qry = qsa.FLSqlQuery()
        qry.setTablesList("flfiles")
        qry.setSelect("count(nombre)")
        qry.setFrom("flfiles")
        qry.setWhere("1=1")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        self.assertEqual(qry.value(0), 13)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
