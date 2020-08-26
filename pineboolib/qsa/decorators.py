"""Decorators module."""
from pineboolib.core.utils import logging
from pineboolib import application
from . import utils

from typing import Callable, Any, TypeVar, cast
import threading
import functools
import traceback
import time

TYPEFN = TypeVar("TYPEFN", bound=Callable[..., Any])

LOGGER = logging.get_logger(__name__)


def atomic(conn_name: str = "default") -> TYPEFN:
    """Return pineboo atomic decorator."""

    def decorator(fun_: TYPEFN) -> TYPEFN:
        @functools.wraps(fun_)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            id_thread = threading.current_thread().ident
            key = "%s_%s" % (id_thread, conn_name)

            if application.USE_ATOMIC_LIST:
                application.ATOMIC_LIST.append(key)

                while application.ATOMIC_LIST[0] != key:
                    time.sleep(0.01)

            new_session = utils.session(conn_name)
            with new_session.begin():
                LOGGER.debug(
                    "New atomic session : %s, connection : %s, transaction: %s",
                    new_session,
                    conn_name,
                    new_session.transaction,
                )

                application.PROJECT.conn_manager.thread_atomic_sessions[key] = new_session

                try:
                    result_ = fun_(*args, **kwargs)
                except Exception as error:
                    LOGGER.warning(
                        "ATOMIC STACKS\nAPP: %s.\nERROR: %s.",
                        "".join(traceback.format_exc(limit=None)),
                        "".join(traceback.format_stack(limit=None)),
                        stack_info=True,
                    )
                    # new_session.rollback()
                    # new_session.close()
                    del application.PROJECT.conn_manager.thread_atomic_sessions[key]
                    if application.USE_ATOMIC_LIST:
                        application.ATOMIC_LIST.remove(key)
                    raise error

            # new_session.commit()
            new_session.close()

            del application.PROJECT.conn_manager.thread_atomic_sessions[key]
            if application.USE_ATOMIC_LIST:
                application.ATOMIC_LIST.remove(key)
            return result_

        mock_fn: TYPEFN = cast(TYPEFN, wrapper)
        return mock_fn

    return decorator  # type: ignore [return-value] # noqa: F723
