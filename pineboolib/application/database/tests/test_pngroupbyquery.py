"""Test_pngroupbyquery module."""

import unittest
from pineboolib.application.database import pngroupbyquery


class TestPNGroupByQuery(unittest.TestCase):
    """TestPNGroupByQuery Class."""

    def test_full(self) -> None:
        """Test full"""

        group_by = pngroupbyquery.PNGroupByQuery(1, "prueba")
        self.assertEqual(group_by.level(), 1)
        self.assertEqual(group_by.field(), "prueba")
