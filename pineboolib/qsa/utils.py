"""
Utility functions for QS files.
"""
import traceback
import re
import math
import sys

from PyQt5 import QtCore
from pineboolib.core.utils.utils_base import ustr
from pineboolib.core.utils import logging

from typing import Any, Optional, Union, Match, List, Generator, Callable

LOGGER = logging.getLogger(__name__)

TIMERS: List[QtCore.QTimer] = []


class switch(object):
    """
    Switch emulation class.

    from: http://code.activestate.com/recipes/410692/
    This class provides the functionality we want. You only need to look at
    this if you want to know how this works. It only needs to be defined
    once, no need to muck around with its internals.
    """

    def __init__(self, value: Any):
        """Construct new witch from initial value."""
        self.value = value
        self.fall = False

    def __iter__(self) -> Generator:
        """Return the match method once, then stop."""
        yield self.match

    def match(self, *args: List[Any]) -> bool:
        """Indicate whether or not to enter a case suite."""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False


class qsaRegExp(object):
    """
    Regexp emulation class.
    """

    result_: Optional[Match[str]]

    def __init__(self, str_re: str, is_global: bool = False):
        """Create new regexp."""
        self.str_re = str_re
        self.pattern = re.compile(self.str_re)
        self.is_global = is_global
        self.result_ = None

    def search(self, text: str) -> Optional[Match[str]]:
        """Return Match from search."""
        self.result_ = None
        if self.pattern is not None:
            self.result_ = self.pattern.search(text)
        return self.result_

    def replace(self, target: str, new_value: str) -> str:
        """Replace string using regex."""
        count = 1 if not self.is_global else 0
        return self.pattern.sub(new_value, target, count)

    def cap(self, i: int) -> Optional[str]:
        """Return regex group number "i"."""
        if self.result_ is None:
            return None

        try:
            return self.result_.group(i)
        except Exception:
            LOGGER.exception("Error calling cap(%s)" % i)
            return None

    def get_global(self) -> bool:
        """Return if regex is global."""
        return self.is_global

    def set_global(self, state: bool) -> None:
        """Set regex global flag."""
        self.is_global = state

    global_ = property(get_global, set_global)


def RegExp(str_re: str) -> qsaRegExp:
    """
    Return qsaRegexp object from search.

    @param strRE. Cadena de texto
    @return valor procesado
    """
    is_global = False
    if str_re[-2:] == "/g":
        str_re = str_re[:-2]
        is_global = True
    elif str_re[-1:] == "/":
        str_re = str_re[:-1]

    if str_re[:1] == "/":
        str_re = str_re[1:]

    return qsaRegExp(str_re, is_global)


class Math(object):
    """QSA Math emulation class."""

    @staticmethod
    def abs(value: Union[int, float]) -> Union[int, float]:
        """Get absolute value."""
        return math.fabs(value)

    @staticmethod
    def ceil(value: float) -> int:
        """Round number to its ceiling."""
        return math.ceil(value)

    @staticmethod
    def floor(value: float) -> int:
        """Round number to its floor."""
        return math.floor(value)

    @staticmethod
    def pow(base: float, exp: float) -> float:
        """Raise base to the power of exp."""
        return math.pow(base, exp)

    @staticmethod
    def round(value_1: float, value_2: int = 2) -> float:
        """Round a number x to y decimal places."""
        return round(float(value_1), value_2)


def parseFloat(value: Any) -> float:
    """
    Convert to float from almost any value.

    @param value. valor a convertir
    @return Valor tipo float, o parametro x , si no es convertible
    """
    ret = 0.00
    try:
        if isinstance(value, str) and value.find(":") > -1:
            # Convertimos a horas
            list_ = value.split(":")
            value = float(list_[0])  # Horas
            value += float(list_[1]) / 60  # Minutos a hora
            value += float(list_[2]) / 3600  # Segundos a hora

        if isinstance(value, str):
            try:
                return float(value)
            except Exception:
                value = value.replace(".", "")
                value = value.replace(",", ".")
                try:
                    return float(value)
                except Exception:
                    return float("nan")

        else:
            ret = 0.0 if value in (None, "") else float(value)

        if ret == int(ret):
            return int(ret)

        return ret
    except Exception:
        LOGGER.exception("parseFloat: Error converting %s to float", value)
        return float("nan")


def parseString(obj: Any) -> str:
    """
    Convert to string almost any value.

    @param obj. valor a convertir
    @return str del objeto dado
    """
    return obj.toString() if hasattr(obj, "toString") else str(obj)


def parseInt(value: Union[float, int, str], base: int = 10) -> int:
    """
    Convert to int almost any value.

    @param x. Value to cenvert
    @return integer value
    """
    ret_ = 0

    tmp_value = str(value)
    if tmp_value.find(".") > -1:
        tmp_value = tmp_value[0 : tmp_value.find(".")]

    if tmp_value.find(",") > -1:
        tmp_value = tmp_value[0 : tmp_value.find(",")]

    if value is not None:
        # x = float(x)
        ret_ = int(tmp_value, base)
        # ret_ = int(str(x), base)

    return ret_


def length(obj: Any) -> int:
    """
    Get length of any object.

    @param obj, objeto a obtener longitud
    @return longitud del objeto
    """
    if hasattr(obj, "length"):
        if isinstance(obj.length, int):
            return obj.length
        else:
            return obj.length()

    else:
        if isinstance(obj, dict) and "result" in obj.keys():
            return len(obj) - 1
        else:
            return len(obj)


def text(obj: Any) -> str:
    """
    Get text property from object.

    @param obj. Objeto a procesar
    @return Valor de text o text()
    """
    try:
        return obj.text()
    except Exception:
        return obj.text


def startTimer(time: int, fun: Callable) -> "QtCore.QTimer":
    """Create new timer that calls a function."""
    global TIMERS
    timer = QtCore.QTimer()
    timer.timeout.connect(fun)
    timer.start(time)
    TIMERS.append(timer)
    return timer


def killTimer(timer: Optional["QtCore.QTimer"] = None) -> None:
    """Stop a given timer."""
    global TIMERS
    if timer is not None:
        timer.stop()
        TIMERS.remove(timer)


def killTimers() -> None:
    """Stop and deletes all timers that have been created with startTimer()."""
    global TIMERS
    for timer in TIMERS:
        timer.stop()

    TIMERS = []


def debug(txt: Union[bool, str, int, float]) -> None:
    """
    Debug for QSA messages.

    @param txt. Mensaje.
    """
    from pineboolib import application

    application.PROJECT.message_manager().send("debug", None, [ustr(txt)])


def format_exc(exc: Optional[int] = None) -> str:
    """Format a traceback."""
    return traceback.format_exc(exc)


def isNaN(value: Any) -> bool:
    """
    Check if value is NaN.

    @param x. Valor numérico
    @return True o False
    """
    if value in [None, ""]:
        return True

    if isinstance(value, str) and value.find(":"):
        value = value.replace(":", "")
    try:
        float(value)
        return False
    except ValueError:
        return True


def isnan(value: Any) -> bool:
    """Return if a number is NaN."""
    return isNaN(value)


def replace(source: str, search: Any, replace: str) -> str:
    """Replace for QSA where detects if "search" is a Regexp."""
    if isinstance(search, str):
        return source.replace(search, str(replace))
    else:
        return search.replace(source, replace)


class Number_attr:
    """Class Number_attr."""

    MIN_VALUE = -sys.maxsize - 1
    MAX_VALUE = sys.maxsize


Number = Number_attr()
