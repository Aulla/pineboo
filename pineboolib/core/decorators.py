# -*- coding: utf-8 -*-
"""
Collection of useful decorators.

These are mainly intended to tell other devs whether a funcitionality is considered unstable or beta
"""
import time
import re
import functools
from .utils import logging
from PyQt6 import QtCore  # type: ignore
from typing import Callable, Any, Dict, TypeVar, cast

TYPEFN = TypeVar("TYPEFN", bound=Callable[..., Any])

LOGGER = logging.get_logger(__name__)
MSG_EMITTED: Dict[str, float] = {}
CLEAN_REGEX = re.compile(r"\s*object\s+at\s+0x[0-9a-zA-Z]{6,38}", re.VERBOSE)
MINIMUM_TIME_FOR_REPRINT = 300


def clean_repr(obj: Any) -> str:
    """Clean up error texts to make them easier to read on GUI (Internal use only)."""
    return CLEAN_REGEX.sub("", repr(obj))


def not_implemented_warn(func_: "TYPEFN") -> "TYPEFN":
    """
    Mark function as not implemented. Its contents do almost nothing at all. Emits a Warning.

    This one is specific to warn users that when QSA runs the code, it's going to be wrong.
    Adds a Stack/traceback to aid devs locating from where the code was called from.
    """

    @functools.wraps(func_)
    def newfn(*args: Any, **kwargs: Any) -> Any:
        global MSG_EMITTED
        ret = func_(*args, **kwargs)
        x_args = [clean_repr(a) for a in args] + [
            "%s=%s" % (key, clean_repr(value)) for key, value in list(kwargs.items())
        ]
        keyname = func_.__name__ + repr(x_args)
        now = time.time()
        if keyname not in MSG_EMITTED or now - MSG_EMITTED[keyname] > MINIMUM_TIME_FOR_REPRINT:
            MSG_EMITTED[keyname] = now
            LOGGER.warning(
                "Not yet impl.: %s(%s) -> %s", func_.__name__, ", ".join(x_args), repr(ret)
            )
            LOGGER.trace(
                "Not yet impl.: %s(%s) -> %s",
                func_.__name__,
                ", ".join(x_args),
                repr(ret),
                stack_info=True,
            )
        return ret

    mock_fn: TYPEFN = cast(TYPEFN, newfn)  # type: ignore
    return mock_fn


def not_implemented_debug(func_: "TYPEFN") -> "TYPEFN":
    """
    Mark function as not implemented. Its contents do almost nothing at all. Emits a Debug.

    In this case, just a Debug, so mainly intended for devs.
    This means the function not doing anything is usually harmless.
    """

    @functools.wraps(func_)
    def newfn(*args: Any, **kwargs: Any) -> Any:
        global MSG_EMITTED
        ret = func_(*args, **kwargs)
        x_args = [clean_repr(a) for a in args] + [
            "%s=%s" % (key, clean_repr(value)) for key, value in list(kwargs.items())
        ]
        keyname = func_.__name__ + repr(x_args)
        now = time.time()
        if keyname not in MSG_EMITTED or now - MSG_EMITTED[keyname] > MINIMUM_TIME_FOR_REPRINT:
            MSG_EMITTED[keyname] = now
            LOGGER.debug(
                "Not yet impl.: %s(%s) -> %s", func_.__name__, ", ".join(x_args), repr(ret)
            )
        return ret

    mock_fn: TYPEFN = cast(TYPEFN, newfn)  # type: ignore
    return mock_fn


def working_on_this(func_: "TYPEFN") -> "TYPEFN":
    """Emit a message to tell other devs that someone is already working on this function."""

    @functools.wraps(func_)
    def newfn(*args: Any, **kwargs: Any) -> Any:
        global MSG_EMITTED
        ret = func_(*args, **kwargs)
        x_args = [clean_repr(a) for a in args] + [
            "%s=%s" % (key, clean_repr(value)) for key, value in list(kwargs.items())
        ]
        keyname = func_.__name__ + repr(x_args)
        now = time.time()
        if keyname not in MSG_EMITTED or now - MSG_EMITTED[keyname] > MINIMUM_TIME_FOR_REPRINT:
            MSG_EMITTED[keyname] = now
            LOGGER.info(
                "WARN: In Progress: %s(%s) -> %s", func_.__name__, ", ".join(x_args), repr(ret)
            )
        return ret

    mock_fn: TYPEFN = cast(TYPEFN, newfn)  # type: ignore
    return mock_fn


def beta_implementation(func_: "TYPEFN") -> "TYPEFN":
    """Mark function as beta. This means that more or less works but it might need more tweaking or errors may arise."""

    @functools.wraps(func_)
    def newfn(*args: Any, **kwargs: Any) -> Any:
        global MSG_EMITTED
        ret = func_(*args, **kwargs)
        x_args = [clean_repr(a) for a in args] + [
            "%s=%s" % (key, clean_repr(value)) for key, value in list(kwargs.items())
        ]
        keyname = func_.__name__ + repr(x_args)
        now = time.time()
        if keyname not in MSG_EMITTED or now - MSG_EMITTED[keyname] > MINIMUM_TIME_FOR_REPRINT:
            MSG_EMITTED[keyname] = now
            LOGGER.info(
                "WARN: Beta impl.: %s(%s) -> %s", func_.__name__, ", ".join(x_args), repr(ret)
            )
        return ret

    mock_fn: TYPEFN = cast(TYPEFN, newfn)  # type: ignore
    return mock_fn


def empty(func_: "TYPEFN") -> "TYPEFN":
    """
    Mark function as Empty, not doing anything. Similar to NotImplemented* but does no add traceback.

    This functions are those that we don't think we will need
    """

    @functools.wraps(func_)
    def newfn(*args: Any, **kwargs: Any) -> Any:
        global MSG_EMITTED
        ret = func_(*args, **kwargs)
        x_args = [clean_repr(a) for a in args] + [
            "%s=%s" % (key, clean_repr(value)) for key, value in list(kwargs.items())
        ]
        keyname = func_.__name__
        now = time.time()
        if keyname not in MSG_EMITTED or now - MSG_EMITTED[keyname] > MINIMUM_TIME_FOR_REPRINT:
            MSG_EMITTED[keyname] = now
            LOGGER.info("WARN: Empty: %s(%s) -> %s", func_.__name__, ", ".join(x_args), repr(ret))
        return ret

    mock_fn: TYPEFN = cast(TYPEFN, newfn)  # type: ignore
    return mock_fn


def incomplete(func_: "TYPEFN") -> "TYPEFN":
    """Mark the function as Incomplete, meaning that functionaility is still missing."""

    @functools.wraps(func_)
    def newfn(*args: Any, **kwargs: Any) -> Any:
        global MSG_EMITTED
        ret = func_(*args, **kwargs)
        x_args = [clean_repr(a) for a in args] + [
            "%s=%s" % (key, clean_repr(value)) for key, value in list(kwargs.items())
        ]
        keyname = func_.__name__ + repr(x_args)
        now = time.time()
        if keyname not in MSG_EMITTED or now - MSG_EMITTED[keyname] > MINIMUM_TIME_FOR_REPRINT:
            MSG_EMITTED[keyname] = now
            LOGGER.info(
                "WARN: Incomplete: %s(%s) -> %s", func_.__name__, ", ".join(x_args), repr(ret)
            )
        return ret

    mock_fn: TYPEFN = cast(TYPEFN, newfn)  # type: ignore
    return mock_fn


def need_revision(func_: "TYPEFN") -> "TYPEFN":
    """Mark the function as needs to be revised. Some bug might have been found and needs help from other devs."""

    def newfn(*args: Any, **kwargs: Any) -> Any:
        global MSG_EMITTED
        ret = func_(*args, **kwargs)
        x_args = [clean_repr(a) for a in args] + [
            "%s=%s" % (key, clean_repr(value)) for key, value in list(kwargs.items())
        ]
        keyname = func_.__name__ + repr(x_args)
        now = time.time()
        if keyname not in MSG_EMITTED or now - MSG_EMITTED[keyname] > MINIMUM_TIME_FOR_REPRINT:
            MSG_EMITTED[keyname] = now
            LOGGER.info(
                "WARN: Needs help: %s(%s) -> %s", func_.__name__, ", ".join(x_args), repr(ret)
            )
        return ret

    mock_fn: TYPEFN = cast(TYPEFN, newfn)  # type: ignore
    return mock_fn


def deprecated(func_: "TYPEFN") -> "TYPEFN":
    """Mark functionality as deprecated in favor of other one."""

    @functools.wraps(func_)
    def newfn(*args: Any, **kwargs: Any) -> Any:
        global MSG_EMITTED
        ret = func_(*args, **kwargs)
        x_args = [clean_repr(a) for a in args] + [
            "%s=%s" % (key, clean_repr(value)) for key, value in list(kwargs.items())
        ]
        keyname = func_.__name__ + repr(x_args)
        now = time.time()
        if keyname not in MSG_EMITTED or now - MSG_EMITTED[keyname] > MINIMUM_TIME_FOR_REPRINT:
            MSG_EMITTED[keyname] = now
            LOGGER.info(
                "WARN: Deprecated: %s(%s) -> %s",
                func_.__name__,
                ", ".join(x_args),
                repr(ret),
                stack_info=False,
            )
        return ret

    mock_fn: TYPEFN = cast(TYPEFN, newfn)  # type: ignore
    return mock_fn


def pyqt_slot(*args: Any) -> Callable[["TYPEFN"], "TYPEFN"]:
    """
    Create Qt Slot from class method.

    Same as QtCore.pyQtSlot but with Typing information for mypy.
    Please use this one instead of QtCore.pyQtSlot().
    """

    def _pyqt_slot(func_: TYPEFN) -> TYPEFN:
        return cast(TYPEFN, QtCore.pyqtSlot(*args)(func_))

    return _pyqt_slot
