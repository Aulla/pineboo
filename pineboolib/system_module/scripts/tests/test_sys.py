"""Test_sys module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestSys(unittest.TestCase):
    """TestSys Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_afterCommit_flFiles(self) -> None:
        """Test aftercommit_flfiles function."""
        from pineboolib.application.database import pnsqlcursor

        cur_area = pnsqlcursor.PNSqlCursor("flareas")
        cur_area.setModeAccess(cur_area.Insert)
        cur_area.refreshBuffer()
        cur_area.setValueBuffer("idarea", "A")
        cur_area.setValueBuffer("descripcion", "area A")
        self.assertTrue(cur_area.commitBuffer())
        _cur_modulo = pnsqlcursor.PNSqlCursor("flmodules")
        _cur_modulo.setModeAccess(_cur_modulo.Insert)
        _cur_modulo.refreshBuffer()
        _cur_modulo.setValueBuffer("idarea", "A")
        _cur_modulo.setValueBuffer("idmodulo", "TM")
        _cur_modulo.setValueBuffer("descripcion", "modulo TM")
        self.assertTrue(_cur_modulo.commitBuffer())
        _cur = pnsqlcursor.PNSqlCursor("flfiles")
        _cur.setModeAccess(_cur.Insert)
        _cur.refreshBuffer()
        _cur.setValueBuffer("nombre", "prueba")
        _cur.setValueBuffer("idmodulo", "TM")
        _cur.setValueBuffer("contenido", "Pablito clavó un clavito!")
        self.assertTrue(_cur.commitBuffer())

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
