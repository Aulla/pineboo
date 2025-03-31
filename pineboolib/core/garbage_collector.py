"""
Module for garbage collector checks.
"""

from typing import Any, Callable, List

from pineboolib.core.utils import logging
from pineboolib.core import DISABLE_CHECK_MEMORY_LEAKS

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


def check_active_threads() -> None:
    """Check active threads."""

    from pineboolib.application import PROXY_ACTIONS_DICT

    current_thread_ids = [thread.ident for thread in threading.enumerate()]
    for thread_id in PROXY_ACTIONS_DICT.keys():

        if thread_id not in current_thread_ids:
            script_names_list = (
                PROXY_ACTIONS_DICT[thread_id] if thread_id in PROXY_ACTIONS_DICT.keys() else []
            )
            LOGGER.debug("Deleting thread %s." % (thread_id))
            for script_name in script_names_list:
                delete_proxy_thread(thread_id, script_name)


def delete_proxy_thread(id_thread: int, script_name: str):
    """Delete actions from thread."""

    from pineboolib.application import qsadictmodules

    action_obj = qsadictmodules.QSADictModules.from_project(script_name)
    if action_obj is not None:
        LOGGER.warning("Deleting action %s from thread %s", script_name, id_thread)
        obj_ = action_obj.loaded_obj[id_thread]
        action_obj.loaded_obj[id_thread] = None
        del action_obj.loaded_obj[id_thread]
        check_delete(obj_, "proxy.widget")


def register_script_name(script_name: str):
    """Register script name."""

    from pineboolib.application import PROXY_ACTIONS_DICT

    check_active_threads()

    id_thread = threading.current_thread().ident
    if id_thread not in PROXY_ACTIONS_DICT.keys():
        PROXY_ACTIONS_DICT[id_thread] = []

    if script_name not in PROXY_ACTIONS_DICT[id_thread]:
        PROXY_ACTIONS_DICT[id_thread].append(script_name)
