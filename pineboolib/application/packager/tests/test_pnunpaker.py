"""
test_pnunpacker Module.
"""

from . import fixture_path

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestPNUnpaker(unittest.TestCase):
    """TestUnpacker Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_pnunpacker(self) -> None:
        """Test eneboopkgs load."""
        from pineboolib.qsa import qsa
        from pineboolib.fllegacy import systype
        import os

        qsa_sys = systype.SysType()
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa_sys.loadModules(path, False))
        qsa_sys.registerUpdate(path)

        qry = qsa.FLSqlQuery()
        qry.setTablesList("flfiles")
        qry.setSelect("count(nombre)")
        qry.setFrom("flfiles")
        qry.setWhere("1=1")
        self.assertTrue(qry.exec_())
        self.assertTrue(qry.first())
        self.assertEqual(qry.value(0), 148)

        qry_2 = qsa.FLSqlQuery()
        qry_2.setTablesList("flfiles")
        qry_2.setSelect("nombre")
        qry_2.setFrom("flfiles")
        qry_2.setWhere("nombre='impuestos.py'")
        self.assertTrue(qry_2.exec_())
        self.assertTrue(qry_2.first())
        self.assertEqual(qry_2.value(0), "impuestos.py")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
