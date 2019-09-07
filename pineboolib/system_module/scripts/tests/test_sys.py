"""Test_sys module."""

import unittest
from pineboolib.loader.main import init_testing


class TestSys(unittest.TestCase):
    """TestSys Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_afterCommit_flFiles(self) -> None:
        """Test aftercommit_flfiles function."""
        from pineboolib.application.database import pnsqlcursor

        _cur_modulo = pnsqlcursor.PNSqlCursor("flmodules")
        _cur_modulo.select("1=1 ORDER BY idmodulo DESC")
        _cur = pnsqlcursor.PNSqlCursor("flfiles")
        _cur.setModeAccess(_cur.Insert)
        _cur.refreshBuffer()
        _cur.setValueBuffer("nombre", "prueba")
        _cur.setValueBuffer("idmodulo", "TM")
        _cur.setValueBuffer("contenido", "Pablito clavó un clavito!")
        self.assertTrue(_cur.commitBuffer())
