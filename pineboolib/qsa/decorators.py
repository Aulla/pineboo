"""Decorators module."""
from pineboolib.core.utils import logging
from pineboolib import application
from . import utils

from typing import Callable, Any, TypeVar, cast
import threading
import functools

TYPEFN = TypeVar("TYPEFN", bound=Callable[..., Any])

LOGGER = logging.get_logger(__name__)


def atomic(conn_name: str = "default") -> TYPEFN:
    """Return pineboo atomic decorator."""

    def decorator(fun_: TYPEFN) -> TYPEFN:
        @functools.wraps(fun_)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            new_session = utils.session(conn_name)
            new_session.begin()

            id_thread = threading.current_thread().ident
            key = "%s_%s" % (id_thread, conn_name)
            # LOGGER.warning(
            #    "NUEVA session: %s, thread: %s, trans: %s",
            #    new_session,
            #    id_thread,
            #    new_session.transaction,
            # )

            application.PROJECT.conn_manager.thread_sessions[key] = new_session

            try:
                result_ = fun_(*args, **kwargs)
            except Exception as error:
                new_session.rollback()
                new_session.close()
                del application.PROJECT.conn_manager.thread_sessions[key]
                LOGGER.warning("ATOMIC: Error : %s", str(error), stack_info=True)
                raise Exception(error)

            new_session.commit()

            new_session.close()
            del application.PROJECT.conn_manager.thread_sessions[key]
            return result_

        mock_fn: TYPEFN = cast(TYPEFN, wrapper)
        return mock_fn

    return decorator  # type: ignore [return-value] # noqa: F723
