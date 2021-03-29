"""
Module for garbage collector checks.
"""
from typing import Any, Callable, List
from . import decorators
from .utils import logging

import threading
import time
import gc

LOGGER = logging.get_logger(__name__)


@decorators.not_implemented_warn()
def async_delete(obj_: Callable, name: str) -> bool:
    """Delete a object."""

    return False


def check_gc_referrers(typename: Any, w_obj: Callable, name: str) -> None:
    """
    Check if any variable is getting out of control.

    Great for checking and tracing memory leaks.
    """

    def checkfn() -> None:

        time.sleep(2)
        try:
            gc.collect()
            obj = w_obj()
            if not obj:
                return
            # TODO: Si ves el mensaje a continuación significa que "algo" ha dejado
            # ..... alguna referencia a un formulario (o similar) que impide que se destruya
            # ..... cuando se deja de usar. Causando que los connects no se destruyan tampoco
            # ..... y que se llamen referenciando al código antiguo y fallando.
            LOGGER.debug("HINT: Objetos referenciando %r::%r (%r) :", typename, obj, name)
            for ref in gc.get_referrers(obj):
                if isinstance(ref, dict):
                    list_: List[str] = []
                    for key, value in ref.items():
                        if value is obj:
                            key = "(**)" + key
                            list_.insert(0, key)
                    # print(" - dict:", repr(x), gc.get_referrers(ref))
                else:
                    if "<frame" in str(repr(ref)):
                        continue
                    # print(" - obj:", repr(ref), [x for x in dir(ref) if getattr(ref, x) is obj])
        except Exception as error:  # noqa : F841
            LOGGER.warning("Error cleaning %r::%r (%r) :", typename, obj, name)

    threading.Thread(target=checkfn).start()
