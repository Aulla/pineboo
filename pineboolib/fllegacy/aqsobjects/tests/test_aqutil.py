"""Test_aqsutil module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.fllegacy.aqsobjects import aqutil


class TestAQUtil(unittest.TestCase):
    """TestAQUtil Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_nombreCampos(self) -> None:
        """Return array from nombreCampos."""
        from pineboolib.qsa import qsa

        util = aqutil.AQUtil()
        array = util.nombreCampos("flmodules")
        self.assertTrue(qsa.parseInt(array[0]))
        value = array.pop(0)
        self.assertEqual(value, "6")
        self.assertEqual(
            str(array),
            str(qsa.Array("bloqueo", "idmodulo", "idarea", "descripcion", "version", "icono")),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
