"""
Module for garbage collector checks.
"""
from typing import Any, Callable, List

from .utils import logging
from . import DISABLE_CHECK_MEMORY_LEAKS

import weakref
import threading

import gc

LOGGER = logging.get_logger(__name__)


def check_delete(obj_: Any, name: str, force: bool = False) -> bool:
    """Delete a object."""

    if not DISABLE_CHECK_MEMORY_LEAKS or force:
        check_gc_referrers(obj_.__class__.__name__, weakref.ref(obj_), name)
    return True


def check_gc_referrers(typename: Any, w_obj: Callable, name: str) -> None:
    """
    Check if any variable is getting out of control.

    Great for checking and tracing memory leaks.
    """

    def checkfn() -> None:

        # time.sleep(2)
        list_: List[str] = []
        try:
            if w_obj is not None:
                gc.collect()
                obj = w_obj()
                if not obj:
                    return
                # TODO: Si ves el mensaje a continuación significa que "algo" ha dejado
                # ..... alguna referencia a un formulario (o similar) que impide que se destruya
                # ..... cuando se deja de usar. Causando que los connects no se destruyan tampoco
                # ..... y que se llamen referenciando al código antiguo y fallando.
                for ref in gc.get_referrers(obj):
                    if "<frame" in str(repr(ref)):
                        continue

                    elif isinstance(ref, dict):
                        for key, value in ref.items():
                            if value is obj:
                                list_.append(
                                    "(%s.%s -> %s (%s)" % (ref.__class__.__name__, key, name, ref)
                                )
                        # print(" - dict:", repr(x), gc.get_referrers(ref))
                    else:
                        list_.append(
                            "(%s) %s.%s -> %s (%s)"
                            % (ref.__class__.__name__, type(ref), str(repr(ref)), name, ref)
                        )
                        # print(" - obj:", repr(ref), [x for x in dir(ref) if getattr(ref, x) is obj])
                if list_:
                    LOGGER.warning("HINT: Objetos referenciando %r::%r (%r) :", typename, obj, name)
                    for item in list_:
                        LOGGER.warning(item)

        except Exception as error:  # noqa : F841
            LOGGER.warning("Error cleaning %r::%r (%r) :", typename, obj, name)

    threading.Thread(target=checkfn).start()
