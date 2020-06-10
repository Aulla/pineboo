from pineboolib.core.utils import logging
from pineboolib import application
from typing import Callable, Any, Dict, TypeVar, cast
import threading
import functools

TYPEFN = TypeVar("TYPEFN", bound=Callable[..., Any])

LOGGER = logging.get_logger(__name__)

from . import utils


def atomic(conn_name="default") -> TYPEFN:
    """Return pineboo atomic decorator."""

    def decorator(fun_):
        @functools.wraps(fun_)
        def wrapper(*args, **kwargs):
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

            result_ = fun_(*args, **kwargs)

            if result_ is False:
                new_session.rollback()
            else:
                new_session.commit()
            new_session.close()
            application.PROJECT.conn_manager.thread_sessions[key] = None
            return result_

        mock_fn: TYPEFN = cast(TYPEFN, wrapper)  # type: ignore
        return mock_fn

    return decorator
