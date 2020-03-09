"""
Test for utils_base.
"""
from pineboolib.core.utils import utils_base

import unittest


class TestUtilsBase(unittest.TestCase):
    """TestUtilsBase class."""

    def test_basics(self) -> None:
        """Test basic functions."""

        self.assertEqual(utils_base.auto_qt_translate_text("hola 123"), "hola 123")
        self.assertEqual(utils_base.one(["1", 2, "3"]), "1")
        self.assertEqual(utils_base.one([], "no"), "no")

        self.assertTrue(utils_base.text2bool("True"))
        self.assertTrue(utils_base.text2bool("true"))
        self.assertTrue(utils_base.text2bool("yes"))
        self.assertTrue(utils_base.text2bool("1"))
        self.assertTrue(utils_base.text2bool("on"))
        self.assertTrue(utils_base.text2bool("sí"))
        self.assertFalse(utils_base.text2bool("false"))
        self.assertFalse(utils_base.text2bool("No"))
        self.assertFalse(utils_base.text2bool("0"))
        self.assertFalse(utils_base.text2bool("OFF"))

    def test_ustr(self) -> None:
        """Test ustr function."""

        self.assertEqual(utils_base.ustr(1.01), "1.01")
        self.assertEqual(utils_base.ustr(6.00), "6")
        self.assertEqual(utils_base.ustr(0.21), "0.21")
        self.assertEqual(utils_base.ustr(22.0001), "22.0001")
        self.assertEqual(utils_base.ustr(b"hola"), "hola")
        self.assertEqual(utils_base.ustr(), "")
        self.assertEqual(utils_base.ustr("vale ", 0.21), "vale 0.21")
        self.assertEqual(utils_base.ustr("test ", 7.00, " pvp"), "test 7 pvp")

    def test_format_numbers(self) -> None:
        """Test format double."""

        self.assertEqual(
            utils_base.format_double(100, 3, 2), "100%s00" % utils_base.DECIMAL_SEPARATOR
        )
        self.assertEqual(
            utils_base.format_double(12.21, 3, 3), "12%s210" % utils_base.DECIMAL_SEPARATOR
        )
        self.assertEqual(utils_base.format_int(12.12), "12")
        self.assertEqual(utils_base.format_int(13.99), "13")

    def test_basic_1(self) -> None:
        """Test basic."""

        self.assertEqual(utils_base.auto_qt_translate_text("prueba"), "prueba")
        self.assertEqual(
            utils_base.auto_qt_translate_text('QT_TRANSLATE_NOOP("MetaData","Versión")'), "Versión"
        )

        utils_base.trace_function(utils_base.auto_qt_translate_text)
