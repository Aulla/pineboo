"""Test_pnparameterquery module."""

import unittest
from pineboolib.application.database import pnparameterquery


class TestPNParameterQuery(unittest.TestCase):
    """TestPNParameterQuery Class."""

    def test_full(self) -> None:
        """Test full"""

        param = pnparameterquery.PNParameterQuery("prueba", "Campo de prueba", 2)
        param.setValue("Esto es una prueba")

        self.assertEqual(param.name(), "prueba")
        self.assertEqual(param.alias(), "Campo de prueba")
        self.assertEqual(param.type(), 2)
        self.assertEqual(param.value(), "Esto es una prueba")
