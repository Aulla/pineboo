"""Test utils module."""

from pineboolib import application
import unittest
import threading

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa, utils


class TestUtils(unittest.TestCase):
    """Test Utils module."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_switch(self) -> None:
        """Test switch function."""

        for i in range(4):
            result = None
            for case in qsa.switch(i):
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
        math_ = qsa.Math
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

        self.assertTrue(math_.random() > 0)
        self.assertTrue(math_.max(1, 2) == 2)
        self.assertTrue(math_.min(50, 33) == 33)
        self.assertTrue(math_.min(50, 50.01) == 50)
        self.assertTrue(math_.sqrt(64) == 8)
        self.assertEqual(math_.tan(20), 2.237160944224742)
        self.assertEqual(math_.cos(20), 0.40808206181339196)
        self.assertEqual(math_.acos(0.4), 1.1592794807274085)

        self.assertEqual(math_.E, 2.718281828459045)
        self.assertEqual(math_.PI, 3.141592653589793)
        self.assertEqual(math_.LN2, 0.6931471805599453)
        self.assertEqual(math_.LN10, 2.302585092994046)
        self.assertEqual(math_.LOG2E, 1.44269504089)
        self.assertEqual(math_.LOG10E, 0.4342944819)
        self.assertEqual(math_.SQRT1_2, 0.7071067811865476)
        self.assertEqual(math_.SQRT2, 1.4142135623730951)

    def test_parse_int(self) -> None:
        """Test parse_int function."""

        val_1 = qsa.parseInt("123", 10)
        self.assertEqual(val_1, 123)
        val_2 = qsa.parseInt("11", 2)
        self.assertEqual(val_2, 3)
        val_3 = qsa.parseInt("123,99", 10)
        self.assertEqual(val_3, 123)
        val_4 = qsa.parseInt("0xFE", 16)
        self.assertEqual(val_4, 254)
        val_5 = qsa.parseInt(100.0023, 10)
        self.assertEqual(val_5, 100)
        val_6 = qsa.parseInt(100, 2)
        self.assertEqual(val_6, 4)
        val_7 = qsa.parseInt("99")
        self.assertEqual(val_7, 99)

    def test_parse_float(self) -> None:
        """Test parse_float function."""

        val_1 = qsa.parseFloat(100)
        self.assertEqual(val_1, 100.0)
        val_2 = qsa.parseFloat(100.01)
        self.assertEqual(val_2, 100.01)
        val_3 = qsa.parseFloat("66000")
        self.assertEqual(val_3, 66000.0)
        val_4 = qsa.parseFloat("66000.2122")
        self.assertEqual(val_4, 66000.2122)
        val_5 = qsa.parseFloat("12:00:00")
        self.assertEqual(val_5, 12)
        val_6 = qsa.parseFloat("12:59:00")
        self.assertTrue(val_6 > 12.98 and val_6 < 12.99)

    def test_parse_string(self) -> None:
        """Test parse_string function."""

        val_1 = qsa.parseString(100)
        self.assertEqual(val_1, "100")

    def test_length(self) -> None:
        """Test length."""

        from pineboolib.application.types import Array

        list_ = ["uno", "dos", "tres"]
        dict_ = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4}
        array_1 = Array([1, 2, 3, 4, 5])
        array_2 = Array({"uno": 1, "dos": 2})

        self.assertEqual(qsa.length(list_), 3)
        self.assertEqual(qsa.length(dict_), 4)
        self.assertEqual(qsa.length(array_1), 5)
        self.assertEqual(qsa.length(array_2), 2)

    def test_is_nan(self) -> None:
        """Test isNaN."""

        self.assertTrue(qsa.isNaN("hola"))
        self.assertTrue(qsa.isNaN("0ct"))
        self.assertFalse(qsa.isNaN("0"))
        self.assertFalse(qsa.isNaN(11.21))
        self.assertFalse(qsa.isNaN("16.01"))

    def test_regexp(self) -> None:
        """Test regexp."""
        regexp = qsa.RegExp("d")
        self.assertFalse(regexp.global_)
        regexp.global_ = True
        self.assertTrue(regexp.global_)
        self.assertTrue(regexp.search("dog"))
        self.assertEqual(regexp.replace("dog", "l"), "log")
        self.assertEqual(regexp.cap(0), "d")
        self.assertEqual(regexp.cap(1), None)

    def test_replace(self) -> None:
        """Test replace."""
        regexp = qsa.RegExp("l")
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

        self.my_fun()
        timer_1 = qsa.startTimer(1000, self.my_fun)
        timer_2 = qsa.startTimer(1000, self.my_fun)  # noqa: F841
        timer_3 = qsa.startTimer(1000, self.my_fun)  # noqa: F841
        self.assertEqual(len(utils.TIMERS), 3)
        qsa.killTimer(timer_1)
        self.assertEqual(len(utils.TIMERS), 2)
        qsa.killTimers()
        self.assertEqual(len(utils.TIMERS), 0)

    def test_session(self) -> None:
        """Test session utils."""

        session_ = qsa.thread_session_new()
        self.assertEqual(session_, application.PROJECT.conn_manager.useConn("default").session())
        self.assertTrue(qsa.is_valid_session(session_))

    def test_type(self) -> None:
        """Test typeof function."""

        self.assertEqual(qsa.typeof_("hola"), "string")
        self.assertEqual(qsa.typeof_(True), "boolean")
        self.assertEqual(qsa.typeof_(False), "boolean")
        self.assertEqual(qsa.typeof_(8), "number")
        self.assertEqual(qsa.typeof_(1.01), "number")
        self.assertEqual(qsa.typeof_(0), "number")
        self.assertEqual(qsa.typeof_(qsa.Array()), "object")
        self.assertEqual(qsa.typeof_([]), "object")
        self.assertEqual(qsa.typeof_(qsa), "unknown")

    def test_thread(self) -> None:
        """Test Thread."""

        self.assertEqual(qsa.thread(), threading.current_thread().ident)

    def test_super(self) -> None:
        """Test super function."""

        obj_ = Prueba2()
        self.assertNotEqual(obj_.__class__, "Prueba")
        self.assertTrue(qsa._super("Prueba", obj_))  # type: ignore [arg-type] # noqa: F821

    def test_user_id(self) -> None:
        """Test user ids."""

        self.assertEqual(qsa.user_id(), "test3")
        qsa.set_user_id("pululo")
        self.assertEqual(qsa.user_id(), "pululo")

    def my_fun(self) -> None:
        """ "Callable test function."""
        print("EY")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


class Prueba(object):
    """Prueba class."""

    pass


class Prueba2(Prueba):
    """Prueba2 class."""

    pass
