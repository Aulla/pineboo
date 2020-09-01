"""Test_flutil module."""

import unittest

from pineboolib.fllegacy import flsettings


class TestSettings(unittest.TestCase):
    """TestSettings class."""

    def test_settings(self) -> None:
        """Test read functions."""

        setting = flsettings.FLSettings()
        setting.writeEntryList("test_uno", [""])
        setting.writeEntryList("test_uno", ["test_uno"])
        setting.writeEntryList("test_dos", [])
        setting.writeEntryList("test_dos", ["test_2_1", "test_2_2"])
        setting.writeEntry("test_tres", "")
        setting.writeEntry("test_tres", "test_tres")
        setting.writeEntry("test_cuatro", False)
        setting.writeEntry("test_cuatro", True)
        setting.writeEntry("test_cinco", 0)
        setting.writeEntry("test_cinco", 10)
        setting.writeEntry("test_double", 0.00)
        setting.writeEntry("test_double", 23.12)

        self.assertEqual(setting.readListEntry("test_dos"), ["test_2_1", "test_2_2"])
        self.assertEqual(setting.readListEntry("test_seis"), [])
        self.assertEqual(setting.readListEntry("test_uno"), ["test_uno"])
        self.assertEqual(setting.readEntry("test_tres"), "test_tres")
        self.assertEqual(setting.readEntry("test_siete", "fallo"), "fallo")
        self.assertEqual(setting.readNumEntry("test_cinco", 12), 10)
        self.assertEqual(setting.readNumEntry("test_ocho", 14), 14)
        self.assertTrue(setting.readBoolEntry("test_cuatro", False))
        self.assertTrue(setting.readBoolEntry("test_nueve", True))
        self.assertTrue(setting.readDoubleEntry("test_double", 23.12))
