"""
Module for garbage collector checks.
"""

from typing import Any, Callable, List

from pineboolib.core.utils import logging

from pineboolib import core
import weakref
import threading
import time

import gc

LOGGER = logging.get_logger(__name__)


def check_delete(obj_: Any, name: str, force: bool = False) -> bool:
    """Delete a object."""

    if not core.DISABLE_CHECK_MEMORY_LEAKS or force:
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
                            if (
                                key in core.PROXY_ACTIONS_DICT.keys()
                            ):  # Falso positivo. Esto es el listado de los hilos.
                                continue
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
                    LOGGER.warning(
                        "HINT: %d Objetos referenciando %r::%r (%r) :",
                        len(list_),
                        typename,
                        obj,
                        name,
                    )
                    for item in list_:
                        LOGGER.warning(item)

        except Exception as error:  # noqa : F841
            LOGGER.warning("Error cleaning %r::%r (%r) :", typename, obj, name)

    threading.Thread(target=checkfn).start()


def check_active_threads(full: bool = False) -> None:
    """Check active threads."""

    current_thread_ids = [thread.ident for thread in threading.enumerate()]
    proxy_keys = core.PROXY_ACTIONS_DICT.keys()
    if full:
        LOGGER.warning("CHECK ACTIVE THREADS")
        # LOGGER.warning("Active threads: %s" % (current_thread_ids))
    for thread_id in list(proxy_keys):
        if thread_id not in current_thread_ids:
            if full:
                LOGGER.warning("Deleting thread %s" % (thread_id))
            script_names_list = core.PROXY_ACTIONS_DICT[thread_id]
            for script_name in list(script_names_list):
                if full:
                    LOGGER.warning("Deleting action %s from thread %s" % (script_name, thread_id))
                delete_proxy_thread(thread_id, script_name)

            core.PROXY_ACTIONS_DICT[thread_id].clear()
            del core.PROXY_ACTIONS_DICT[thread_id]


def delete_proxy_thread(id_thread: int, script_name: str) -> None:
    """Delete actions from thread."""

    from pineboolib.application import qsadictmodules

    action_obj = qsadictmodules.QSADictModules.from_project(script_name)
    if hasattr(action_obj, "loaded_obj"):
        if id_thread in action_obj.loaded_obj.keys():
            obj_ = action_obj.loaded_obj[id_thread]
            action_obj.loaded_obj[id_thread] = None
            del action_obj.loaded_obj[id_thread]
            # quitar script_name de la lista core.PROXY_ACTIONS_DICT[thread_id]

            if hasattr(obj_, "iface"):
                LOGGER.info("Deleting iface from %s, %s" % (script_name, obj_.iface))

                obj_.iface = None

            check_delete(obj_, "proxy.%s" % script_name)


def register_script_name(script_name: str) -> None:
    """Register script name."""
    if not core.DISABLE_CHECK_MEMORY_LEAKS:
        id_thread: int = threading.current_thread().ident  # type: ignore [assignment]
        if id_thread not in core.PROXY_ACTIONS_DICT.keys():
            core.PROXY_ACTIONS_DICT[id_thread] = []

        script_name = script_name if script_name != "sys" else "sys_module"

        if script_name not in core.PROXY_ACTIONS_DICT[id_thread]:
            core.PROXY_ACTIONS_DICT[id_thread].append(script_name)  # type: ignore [union-attr]


def periodic_gc(interval: int = 60) -> None:
    """Periodic cleaning task."""
    while True:
        LOGGER.warning("Starting periodic GC every %s seconds" % interval)
        check_active_threads(True)
        LOGGER.warning("Next periodic GC in %s seconds" % interval)
        time.sleep(interval)
