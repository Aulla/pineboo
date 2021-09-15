"""
Utility functions for QS files.
"""
import traceback
import re
import math
import sys
import threading
import os

from PyQt6 import QtCore

from pineboolib.application import types, qsadictmodules
from pineboolib.core.utils import utils_base, logging

from pineboolib import application

from typing import (
    Any,
    Optional,
    Union,
    Match,
    List,
    Generator,
    Callable,
    Iterable,
    Dict,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from sqlalchemy.engine import (  # type: ignore [import] # noqa: F401, F821
        base,
    )  # pragma: no cover
    from pineboolib.interfaces import isession  # pragma: no cover

LOGGER = logging.get_logger(__name__)

TIMERS: List[QtCore.QTimer] = []


class Switch(object):
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


class QsaRegExp(object):
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


def reg_exp(str_re: str) -> QsaRegExp:
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

    return QsaRegExp(str_re, is_global)


class MathClass(object):
    """QSA Math emulation class."""

    def abs(self, value: Union[int, float]) -> Union[int, float]:
        """Get absolute value."""
        return math.fabs(value)

    def acos(self, value: Union[float, int]) -> float:
        """Return the arc cosine."""

        return math.acos(value)

    def cos(self, value: Union[float, int]) -> float:
        """Return the cosine of value."""

        return math.cos(value)

    def asin(self, value: Union[float, int]) -> float:
        """Return the arc sine of value."""

        return math.asin(value)

    def sin(self, value: Union[float, int]) -> float:
        """Return the sine of value."""

        return math.sin(value)

    def atan(self, value: Union[float, int]) -> float:
        """Return the arc tangent of value."""

        return math.atan(value)

    def atan2(self, value_y: Union[float, int], value_x: Union[float, int]) -> float:
        """Return the arc tangent."""

        return math.atan2(value_y, value_x)

    def tan(self, value: Union[float, int]) -> float:
        """Return the tangent of value."""

        return math.tan(value)

    def exp(self, value: Union[float, int]) -> float:
        """Return e raised to the power of value."""

        return math.exp(value)

    def ceil(self, value: float) -> int:
        """Round number to its ceiling."""
        return math.ceil(value)

    def floor(self, value: float) -> int:
        """Round number to its floor."""
        return math.floor(value)

    def log(self, value: Union[float, int]) -> float:
        """Return the logarithm of value to the given base."""

        return math.log(value)

    def random(self) -> float:
        """Return a pseudo-random floating point number between 0 and 1."""
        import random

        return random.random()

    def max(self, number1: Union[float, int], number2: Union[float, int]) -> Union[float, int]:
        """Return the largest of number1 and number2."""

        return max([number1, number2])

    def min(self, number1: Union[float, int], number2: Union[float, int]) -> Union[float, int]:
        """Return the smallest of number1 and number2."""

        return min([number1, number2])

    def pow(self, base_: float, exp: float) -> float:
        """Raise base to the power of exp."""
        return math.pow(base_, exp)

    def round(self, value_1: float, value_2: int = 2) -> float:
        """Round a number x to y decimal places."""
        return round(float(value_1), value_2)

    def sqrt(self, value: Union[float, int]) -> float:
        """Return the square root of the number passed in the parameter."""

        return math.sqrt(value)

    def _get_pi(self) -> float:
        """Return PI value."""

        return 3.141592653589793

    def _get_eulen(self) -> float:
        """Return eulers constant. The base for natural logarithms."""

        return 2.718281828459045

    def _get_ln2(self) -> float:
        """Return natural logarithm of 2."""

        return 0.6931471805599453

    def _get_ln10(self) -> float:
        """Return natural logarithm of 10."""

        return 2.302585092994046

    def _get_log2e(self) -> float:
        """Return base 2 logarithm of E."""

        return 1.44269504089

    def _get_log10e(self) -> float:
        """Return base 2 logarithm of E."""

        return 0.4342944819

    def _get_sqrt1_2(self) -> float:
        """Return square root of 1/2."""

        return 0.7071067811865476

    def _get_sqrt2(self) -> float:
        """Return square root of 2."""

        return 1.4142135623730951

    PI = property(_get_pi)
    E = property(_get_eulen)
    LN2 = property(_get_ln2)
    LN10 = property(_get_ln10)
    LOG2E = property(_get_log2e)
    LOG10E = property(_get_log10e)
    SQRT1_2 = property(_get_sqrt1_2)
    SQRT2 = property(_get_sqrt2)


def parse_float(value: Any) -> float:
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


def parse_string(obj: Any) -> str:
    """
    Convert to string almost any value.

    @param obj. valor a convertir
    @return str del objeto dado
    """
    return obj.toString() if hasattr(obj, "toString") else str(obj)


def parse_int(value: Union[float, int, str], base_: int = 10) -> int:
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
        ret_ = int(tmp_value, base_)
        # ret_ = int(str(x), base)

    return ret_


def length(obj: Any = "") -> int:
    """
    Get length of any object.

    @param obj, objeto a obtener longitud
    @return longitud del objeto
    """
    if obj is None:
        return 0

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


def start_timer(time: int, fun: Callable) -> "QtCore.QTimer":
    """Create new timer that calls a function."""
    global TIMERS
    timer = QtCore.QTimer()
    timer.timeout.connect(fun)  # type: ignore [attr-defined] # noqa: F821
    timer.start(time)
    TIMERS.append(timer)
    return timer


def kill_timer(timer: Optional["QtCore.QTimer"] = None) -> None:
    """Stop a given timer."""
    global TIMERS
    if timer is not None:
        timer.stop()
        TIMERS.remove(timer)


def kill_timers() -> None:
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

    application.PROJECT.message_manager().send("debug", None, [utils_base.ustr(txt)])


def format_exc(exc: Optional[int] = None) -> str:
    """Format a traceback."""
    return traceback.format_exc(exc)


def is_nan(value: Any) -> bool:
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
        value = float(value)
        return math.isnan(value)
    except ValueError:
        return True


def isnan(value: Any) -> bool:
    """Return if a number is NaN."""
    return is_nan(value)


def replace(source: str, search: Any, replace: str) -> str:
    """Replace for QSA where detects if "search" is a Regexp."""
    if isinstance(search, str):
        return source.replace(search, str(replace))
    else:
        return search.replace(source, replace)


def splice(*args: Any) -> Any:
    """Splice Iterables."""

    real_args = args[1:]
    array_ = args[0]
    if hasattr(array_, "splice"):
        array_.splice(real_args)
    else:
        if isinstance(array_, list):
            new_array_ = []

            if len(real_args) == 2:  # Delete
                pos_ini = real_args[0]
                length_ = real_args[1]
                for i in reversed(range(pos_ini, pos_ini + length_)):
                    array_.pop(i)

            elif len(real_args) > 2 and real_args[1] == 0:  # Insertion

                for value in reversed(real_args[2:]):
                    array_.insert(real_args[0], value)

            elif len(real_args) > 2 and real_args[1] > 0:  # Replacement
                pos_ini = real_args[0]
                replacement_size = real_args[1]
                new_values = real_args[2:]

                count_1 = 0
                count_2 = 0
                for old_value in array_:
                    if count_1 < pos_ini:
                        new_array_.append(old_value)
                    else:
                        if count_2 < replacement_size:
                            if count_2 == 0:
                                for new_value in new_values:
                                    new_array_.append(new_value)

                            count_2 += 1
                        else:
                            new_array_.append(old_value)

                    count_1 += 1
                array_ = new_array_


class Sort:
    """Sort Class."""

    _function: Optional[Callable] = None

    def __init__(self, function: Optional[Callable] = None):
        """Initialize function."""
        self._function = function

    def sort_(self, array_: Iterable) -> List:
        """Sort function."""

        new_array_: List = []
        if self._function is not None:
            for pos, value in enumerate(array_):
                found = False
                for new_pos, new_value in enumerate(list(new_array_)):

                    result = self._function(value, new_value)
                    # print("Comparando", value, new_value, result, "-->", new_array_)
                    if result == 0:
                        # print("Es igual (%s == %s)" % (value, new_value))
                        new_array_.append(value)
                        found = True
                        break
                    elif result == 1:
                        # print("Es mayor (%s > %s)" % (value, new_value))
                        continue

                    elif result == -1:
                        # print("Es menor (%s < %s)" % (value, new_value))
                        new_array_.insert(new_pos, value)
                        found = True
                        break

                if not found:
                    new_array_.append(value)
        else:
            new_array_ = sorted(array_)

        array_ = new_array_
        return new_array_


class NumberAttr:
    """Class Number_attr."""

    MIN_VALUE = -sys.maxsize - 1
    MAX_VALUE = sys.maxsize


def user_id() -> str:
    """Return user_id."""

    result = getattr(qsadictmodules.QSADictModules.from_project("sys").iface, "current_user")
    if not result:
        result = application.PROJECT.session_id()
    return result


def set_user_id(user_id: str) -> None:
    """Set user id."""

    qsadictmodules.from_project("sys").iface.current_user = user_id


def driver_session(conn_name: str = "default") -> "isession.PinebooSession":
    """Return driver session."""

    return application.PROJECT.conn_manager.useConn(conn_name).driver().session()


def session(conn_name: str = "default", legacy: bool = False) -> "isession.PinebooSession":
    """Return session connection."""

    return (
        application.PROJECT.conn_manager.useConn(conn_name).session()
        if legacy
        else driver_session(conn_name)
    )


def thread_session_new(conn_name: str = "default") -> "isession.PinebooSession":
    """Return thread session new."""

    return session(conn_name, True)


def thread_session_current(conn_name: str = "default") -> Optional["isession.PinebooSession"]:
    """Return session current."""

    return application.PROJECT.conn_manager.useConn(conn_name)._session_legacy


def is_valid_session(session: "isession.PinebooSession", raise_error: bool = False) -> bool:
    """Return if a session is valid."""

    return application.PROJECT.conn_manager.is_valid_session(session, raise_error)


def thread_session_free(conn_name: str = "default") -> None:
    """Close and delete current thread session."""

    session = application.PROJECT.conn_manager.useConn(conn_name)._session_legacy
    application.PROJECT.conn_manager.useConn(conn_name)._session_legacy = None
    if session is not None:
        session.close()


def thread() -> int:
    """Return thread id."""

    return threading.current_thread().ident or -1


def session_atomic(conn_name: str = "default") -> Optional["isession.PinebooSession"]:
    """Return atomic_session."""

    return application.PROJECT.conn_manager.useConn(conn_name)._session_atomic


def ws_channel_send(msg: Any = "", group_name: str = "") -> None:
    """Send message to websocket channel."""

    if application.USE_WEBSOCKET_CHANNEL:
        from asgiref.sync import async_to_sync  # type: ignore [import] # noqa: F723
        from channels.layers import get_channel_layer  # type: ignore [import] # noqa: F723

        json = {"type": "send.msg", "content": msg}

        channel_layer = get_channel_layer()
        user_id = application.PROJECT.session_id()
        if group_name:
            async_to_sync(channel_layer.group_send)(group_name, json)
        else:
            async_to_sync(channel_layer.send)(user_id, json)


def ws_channel_send_type(json: Dict, group_name: str = "") -> None:
    """Send message to websocket channel."""

    if application.USE_WEBSOCKET_CHANNEL:
        from asgiref.sync import async_to_sync  # type: ignore [import] # noqa: F723
        from channels.layers import get_channel_layer  # type: ignore [import] # noqa: F723

        channel_layer = get_channel_layer()
        user_id = application.PROJECT.session_id()
        if group_name:
            async_to_sync(channel_layer.group_send)(group_name, json)
        else:
            async_to_sync(channel_layer.send)(user_id, json)


def typeof_(obj: Any) -> str:
    """Return type name froma n object."""

    result = "unknown"

    if isinstance(obj, str):
        result = "string"
    elif isinstance(obj, bool):
        result = "boolean"
    elif isinstance(obj, (int, float)):
        result = "number"
    elif isinstance(obj, (dict, list, types.Array)):
        result = "object"

    return result


def _super(class_name: str, obj: Callable) -> "super":
    """Super class."""

    for classes in obj.__class__.__mro__:
        if classes.__name__ == class_name:
            return super(classes, obj)

    raise Exception("Superclass %s not found." % class_name)


def pool_status(conn_name: str = "main_conn") -> str:
    """Return pool status used for the conn_name."""

    return application.PROJECT.conn_manager.pool_status(conn_name)


def memory_status() -> None:
    """Return memory status."""

    from pineboolib.fllegacy import flutil

    time_stamp = flutil.FLUtil().timestamp()
    file_path = os.path.join(application.PROJECT.tmpdir, "%s.txt" % time_stamp)

    file_ = open(file_path, "w", encoding="UTF-8")

    try:
        from pympler import muppy, summary  # type: ignore [import] # noqa: F821

        all_objects = muppy.get_objects()

        file_.write("TYPES,OBJECTS,MEMORY SIZE")
        sum_memory = 0
        sum_objects = 0
        for item in summary.summarize(all_objects):
            file_.write("\n%s" % item)
            sum_objects += item[1]
            sum_memory += item[2]

        file_.write("\nOBJECTS IN MEMORY  : %s" % len(all_objects))
        file_.write("\nTOTAL MEMORY USAGE : %s" % sum_memory)
        file_.close()
        LOGGER.warning(
            "MEMORY_STATUS: File %s is created with debug. Usage(%s)", file_path, sum_memory
        )

    except ImportError:
        LOGGER.warning("need install 'pympler' module first.")


def qt_translate_noop(string: str, path: str, mod: str) -> str:
    """Return a translation."""

    return utils_base.qt_translate_noop(string, path, mod)
