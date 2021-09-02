"""
Manage Qt Signal-Slot connections.
"""


from PyQt6 import QtCore, QtWidgets  # type: ignore[import]
from pineboolib import logging

import inspect
import weakref
import re


from typing import Callable, Any, Dict, Tuple, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import types  # pragma: no cover
    from pineboolib.qsa import formdbwidget  # noqa F401 # pragma: no cover
    from pineboolib.qsa import object_class  # noqa F401 # pragma: no cover


LOGGER = logging.get_logger(__name__)


class ProxySlot:
    """
    Proxies a method so it doesn't need to be resolved on connect.
    """

    PROXY_FUNCTIONS: Dict[str, "Callable"] = {}

    def __init__(
        self, remote_fn: "types.MethodType", receiver: "QtCore.QObject", slot: str
    ) -> None:
        """Create a proxy for a method."""
        self.key = "%r.%r->%r" % (remote_fn, receiver, slot)
        if self.key not in self.PROXY_FUNCTIONS:
            self.PROXY_FUNCTIONS[self.key] = proxy_fn(
                weakref.WeakMethod(remote_fn), weakref.ref(receiver)
            )
        self.proxy_function = self.PROXY_FUNCTIONS[self.key]

    def getProxyFn(self) -> Callable:
        """Retrieve internal proxy function."""
        return self.proxy_function


def get_expected_args_num(inspected_function: "Callable") -> int:
    """Inspect function to get how many arguments expects."""
    expected_args = inspect.getfullargspec(inspected_function)[0]
    args_num = len(expected_args)

    if args_num and expected_args[0] == "self":
        args_num -= 1

    return args_num


def get_expected_kwargs(inspected_function: "Callable") -> bool:
    """Inspect a function to get if expects keyword args."""
    return True if inspect.getfullargspec(inspected_function)[2] else False


def proxy_fn(weak_ref_method: "weakref.WeakMethod", weak_ref: "weakref.ref") -> "Callable":
    """Create a proxied function, so it does not hold the garbage collector."""

    def function(*args: Any, **kwargs: Any) -> Optional[Any]:
        function_method = weak_ref_method()
        if not function_method:
            return None  # pragma: no cover
        ref = weak_ref()
        if not ref:
            return None  # pragma: no cover

        args_num = get_expected_args_num(function_method)

        if args_num:
            args_list = list(args)
            while len(args_list) < args_num:
                args_list.append(None)
            args = tuple(args_list)

            return function_method(*args[0:args_num], **kwargs)
        else:
            return function_method()

    return function


def slot_done(function: Callable, signal: "QtCore.pyqtSignal") -> Callable:
    """Create a fake slot for QS connects."""

    def new_fn(*args: Any, **kwargs: Any) -> Any:

        # PyQt6-Stubs seems to miss QtCore.pyqtSignal.name (also, this seems to be internal)
        original_signal_name: str = getattr(signal, "signal")

        # Este parche es para evitar que las conexiones de un clicked de error de cantidad de argumentos.
        # En Eneboo se esperaba que signal no contenga argumentos
        if original_signal_name == "2clicked(bool)":
            args = tuple()  # pragma: no cover
        # args_num = get_expected_args_num(fn)
        try:
            return function(*args, **kwargs) if get_expected_kwargs(function) else function(*args)
        except Exception:  # pragma: no cover
            LOGGER.exception("Error trying to create a connection")  # pragma: no cover

        return False  # pragma: no cover

    return new_fn


def connect(
    sender: "QtWidgets.QWidget",
    signal: str,
    receiver: "QtCore.QObject",
    slot: str,
    caller: Optional[Union["formdbwidget.FormDBWidget", "object_class.ObjectClass"]] = None,
) -> Optional[Tuple["QtCore.pyqtSignal", Callable]]:
    """Connect signal to slot for QSA."""

    # Parameters example:
    # caller: <clientes.FormInternalObj object at 0x7f78b5c230f0>
    # sender: <pineboolib.q3widgets.qpushbutton.QPushButton object at 0x7f78b4de1af0>
    # signal: 'clicked()'
    # receiver: <clientes.FormInternalObj object at 0x7f78b5c230f0>
    # slot: 'iface.buscarContacto()'

    if caller is not None:
        LOGGER.trace("* * * Connect:: %s %s %s %s %s", caller, sender, signal, receiver, slot)
    else:
        LOGGER.trace(
            "? ? ? Connect:: %s %s %s %s", sender, signal, receiver, slot
        )  # pragma: no cover
    signal_slot = solve_connection(sender, signal, receiver, slot)

    if not signal_slot:
        return None
    # http://pyqt.sourceforge.net/Docs/PyQt4/qt.html#ConnectionType-enum
    # conntype =
    #    QtCore.Qt.ConnectionType.QueuedConnection,
    #    QtCore.Qt.ConnectionType.UniqueConnection,
    # )
    conntype = QtCore.Qt.ConnectionType.QueuedConnection

    new_signal, new_slot = signal_slot

    try:
        slot_done_fn: Callable = slot_done(new_slot, new_signal)
        # MyPy/PyQt6-Stubs misses connect(type=param)

        new_signal.connect(slot_done_fn, type=conntype)  # type: ignore [attr-defined] # noqa: F821
    except Exception as error:  # pragma: no cover
        LOGGER.warning(  # pragma: no cover
            "ERROR Connecting: %s %s %s %s - %s error:%s",
            sender,
            signal,
            receiver,
            slot,
            error,
            conntype,
        )
        return None  # pragma: no cover

    signal_slot = new_signal, slot_done_fn
    return signal_slot


def disconnect(
    sender: "QtWidgets.QWidget", signal: str, receiver: "QtCore.QObject", slot: str
) -> Optional[Tuple["QtCore.pyqtSignal", Callable]]:
    """Disconnect signal from slot for QSA."""
    signal_slot = solve_connection(sender, signal, receiver, slot)
    if signal_slot:
        signal_, real_slot = signal_slot
        try:
            signal_.disconnect(real_slot)  # type: ignore [attr-defined] # noqa: F821
        except Exception:  # pragma: no cover
            LOGGER.trace(
                "Error disconnecting %r", (sender, signal, receiver, slot), exc_info=True
            )  # pragma: no cover

    return signal_slot


def solve_connection(
    sender: "QtWidgets.QWidget", signal: str, receiver: "QtCore.QObject", slot: str
) -> Optional[Tuple["QtCore.pyqtSignal", "Callable"]]:
    """Try hard to guess which is the correct way of connecting signal to slot. For QSA."""

    match = re.search(r"^(\w+)\.(\w+)(\(.*\))?", slot)
    if slot.endswith("()"):
        slot = slot[:-2]

    if hasattr(sender, "dateChanged"):
        if "valueChanged" in signal:
            signal = signal.replace("valueChanged", "dateChanged")

    elif hasattr(sender, "currentChanged"):
        if "CurrentChanged" in signal:
            signal = signal.replace("CurrentChanged", "currentChanged")

    remote_fn = None

    if slot.find(".") > -1:
        remote_fn = receiver
        for slot_ in slot.split("."):
            remote_fn = getattr(remote_fn, slot_, None)
            if remote_fn is None:
                break
    else:
        remote_fn = getattr(receiver, slot, None)

    sg_name = re.sub(r" *\(.*\)", "", signal)

    # search orig_signal
    original_signal = getattr(sender, sg_name, None)
    if not original_signal and hasattr(sender, "form"):
        original_signal = getattr(
            sender.form, sg_name, None  # type: ignore [attr-defined] # noqa: F821
        )

    if not original_signal:
        LOGGER.error(  # pragma: no cover
            "ERROR: No existe la señal %s para la clase %s", signal, sender.__class__.__name__
        )
        return None  # pragma: no cover

    if remote_fn is not None:

        proxy_slot = ProxySlot(remote_fn, receiver, slot)  # type: ignore [arg-type] # noqa F821
        proxyfn = proxy_slot.getProxyFn()
        return original_signal, proxyfn
    elif match:
        remote_obj = getattr(receiver, match.group(1), None)
        if remote_obj is None:
            raise AttributeError("Object %s not found on %s" % (remote_obj, str(receiver)))
        remote_fn = getattr(remote_obj, match.group(2), None)
        if remote_fn is None:
            raise AttributeError("Object %s not found on %s" % (remote_fn, remote_obj))
        return original_signal, remote_fn  # type: ignore [return-value] # noqa F723

    elif isinstance(receiver, QtCore.QObject):
        if isinstance(slot, str):
            original_slot = getattr(receiver, slot, None)
            if not original_slot:
                iface = getattr(receiver, "iface", None)
                if iface:
                    original_slot = getattr(iface, slot, None)
            if not original_slot:
                LOGGER.error(  # pragma: no cover
                    "Al realizar connect %s:%s -> %s:%s ; "
                    "el es QtCore.QObject pero no tiene slot",
                    sender,
                    signal,
                    receiver,
                    slot,
                )
                return None  # pragma: no cover
            return original_signal, original_slot
