"""Test utils module."""

import unittest

from pineboolib.qsa import utils


class TestUtils(unittest.TestCase):
    """Test Utils module."""

    def test_switch(self) -> None:
        """Test switch function."""

        for i in range(4):
            result = None
            for case in utils.switch(i):
                if case(0):
                    result = 0
                    break
                if case(1):
                    result = 1
                    break
                if case(2):
                    result = 2
                    break
                if case():
                    result = 4
            if i < 3:
                self.assertEqual(i, result)
            else:
                self.assertFalse(i == result)

    def test_math(self) -> None:
        """Test Math class."""
        math_ = utils.Math
        self.assertEqual(math_.abs(-1), 1)
        self.assertEqual(math_.abs(-2), 2)
        self.assertEqual(math_.abs(0), 0)

        self.assertEqual(math_.ceil(8.001), 9)
        self.assertEqual(math_.ceil(8.51), 9)
        self.assertEqual(math_.ceil(8.99), 9)

        self.assertEqual(math_.floor(8.001), 8)
        self.assertEqual(math_.floor(8.51), 8)
        self.assertEqual(math_.floor(8.99), 8)

        self.assertEqual(math_.pow(2, 1), 2)
        self.assertEqual(math_.pow(3, 2), 9)

        self.assertEqual(math_.round(10.1234, 2), 10.12)
        self.assertEqual(math_.round(0.9698, 2), 0.97)
        self.assertEqual(math_.round(123.969899, 4), 123.9699)

    def test_parse_int(self) -> None:
        """Test parse_int function."""

        val_1 = utils.parseInt("123", 10)
        self.assertEqual(val_1, 123)
        val_2 = utils.parseInt("11", 2)
        self.assertEqual(val_2, 3)
        val_3 = utils.parseInt("123,99", 10)
        self.assertEqual(val_3, 123)
        val_4 = utils.parseInt("0xFE", 16)
        self.assertEqual(val_4, 254)
        val_5 = utils.parseInt(100.0023, 10)
        self.assertEqual(val_5, 100)
        val_6 = utils.parseInt(100, 2)
        self.assertEqual(val_6, 4)
        val_7 = utils.parseInt("99")
        self.assertEqual(val_7, 99)

    def test_parse_float(self) -> None:
        """Test parse_float function."""

        val_1 = utils.parseFloat(100)
        self.assertEqual(val_1, 100.0)
        val_2 = utils.parseFloat(100.01)
        self.assertEqual(val_2, 100.01)
        val_3 = utils.parseFloat("66000")
        self.assertEqual(val_3, 66000.0)
        val_4 = utils.parseFloat("66000.2122")
        self.assertEqual(val_4, 66000.2122)
        val_5 = utils.parseFloat("12:00:00")
        self.assertEqual(val_5, 12)
        val_6 = utils.parseFloat("12:59:00")
        self.assertTrue(val_6 > 12.98 and val_6 < 12.99)

    def test_parse_string(self) -> None:
        """Test parse_string function."""

        val_1 = utils.parseString(100)
        self.assertEqual(val_1, "100")

    def test_length(self) -> None:
        """Test length."""

        from pineboolib.application.types import Array

        list_ = ["uno", "dos", "tres"]
        dict_ = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4}
        array_1 = Array([1, 2, 3, 4, 5])
        array_2 = Array({"uno": 1, "dos": 2})

        self.assertEqual(utils.length(list_), 3)
        self.assertEqual(utils.length(dict_), 4)
        self.assertEqual(utils.length(array_1), 5)
        self.assertEqual(utils.length(array_2), 2)

    def test_is_nan(self) -> None:
        """Test isNaN."""

        self.assertTrue(utils.isnan("hola"))
        self.assertTrue(utils.isnan("0ct"))
        self.assertFalse(utils.isnan("0"))
        self.assertFalse(utils.isnan(11.21))
        self.assertFalse(utils.isnan("16.01"))

    def test_regexp(self) -> None:
        """Test regexp."""
        regexp = utils.RegExp("d")
        self.assertFalse(regexp.global_)
        regexp.global_ = True
        self.assertTrue(regexp.global_)
        self.assertTrue(regexp.search("dog"))
        self.assertEqual(regexp.replace("dog", "l"), "log")
        self.assertEqual(regexp.cap(0), "d")
        self.assertEqual(regexp.cap(1), None)

    def test_replace(self) -> None:
        """Test replace."""
        regexp = utils.RegExp("l")
        name = "pablo lopez"
        replace = utils.replace(name, regexp, "L")
        self.assertEqual(replace, "pabLo lopez")
        regexp.global_ = True
        replace2 = utils.replace(name, regexp, "L")
        self.assertTrue(isinstance(replace2, str))
        self.assertEqual(replace2, "pabLo Lopez")

        replace3 = utils.replace(replace2, "o", "6")
        self.assertEqual(replace3, "pabL6 L6pez")

    def test_timers(self) -> None:
        """Test Timers."""

        timer_1 = utils.startTimer(1000, self.my_fun)
        timer_2 = utils.startTimer(1000, self.my_fun)
        timer_3 = utils.startTimer(1000, self.my_fun)
        self.assertEqual(len(utils.TIMERS), 3)
        utils.killTimer(timer_1)
        self.assertEqual(len(utils.TIMERS), 2)
        utils.killTimers()
        self.assertEqual(len(utils.TIMERS), 0)

    def my_fun(self) -> None:
        """"Callable test function."""
        print("EY")
