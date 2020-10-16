"""Decorators module."""
from pineboolib.core.utils import logging, utils_base
from pineboolib.core import exceptions
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
            application.PROJECT.conn_manager.current_atomic_sessions[
                key
            ], new_session = utils.driver_session(conn_name)
            result_ = None
            try:
                with new_session.begin():
                    LOGGER.debug(
                        "New atomic session : %s, connection : %s, transaction: %s",
                        new_session,
                        conn_name,
                        new_session.transaction,
                    )

                    try:
                        result_ = fun_(*args, **kwargs)

                    except Exception as error:
                        LOGGER.warning(
                            "ATOMIC STACKS\nAPP: %s.\nERROR: %s.",
                            "".join(traceback.format_exc(limit=None)),
                            "".join(traceback.format_stack(limit=None)),
                            stack_info=True,
                        )
                        delete_atomic_session(key)
                        raise error
                if new_session.transaction is not None:
                    raise exceptions.TransactionOpenedException(
                        "the %s.%s function has been called in atomic mode and has left the transaction open."
                        % (fun_.__module__, fun_.__name__)
                    )

                new_session.close()
                delete_atomic_session(key)

            except Exception as error:
                delete_atomic_session(key)
                raise error

            return result_

        mock_fn: TYPEFN = cast(TYPEFN, wrapper)
        return mock_fn

    return decorator  # type: ignore [return-value] # noqa: F723


def delete_atomic_session(key: str) -> None:
    """Delete atomic_session."""
    mng_ = application.PROJECT.conn_manager
    if key in mng_.current_atomic_sessions.keys():
        session_key = mng_.current_atomic_sessions[key]
        if session_key in mng_._thread_sessions.keys():
            del mng_._thread_sessions[session_key]

        del mng_.current_atomic_sessions[key]

    if application.USE_ATOMIC_LIST:
        if key in application.ATOMIC_LIST:
            application.ATOMIC_LIST.remove(key)

    if application.SHOW_TRANSACTIONS_AFTER_ATOMIC:
        sesiones = []
        for ses in mng_._thread_sessions.keys():
            if mng_._thread_sessions[ses].transaction is not None:
                sesiones.append(mng_._thread_sessions[ses])

        if sesiones:
            LOGGER.warning(
                "Al terminar la función atomica, las siguentes sessiones continuan en transaccion:\n%s",
                "".join(
                    [
                        "%s --> %s.\n"
                        % (item._conn_name, item)  # type: ignore [attr-defined] # noqa: F821
                        for item in sesiones
                    ]
                ),
            )
            for conn in mng_.dictDatabases().values():
                key_gen = utils_base.session_id(conn._name)
                if key_gen in mng_._thread_sessions.keys():
                    LOGGER.warning("La sesión de CONN %s continua en transacción", conn._name)

            for ses_th in mng_.get_current_thread_sessions():
                if (
                    mng_.mainConn().driver().is_valid_session(ses_th)
                    and ses_th.transaction is not None
                ):
                    LOGGER.warning(
                        "La sesión de HILO %s continua en transacción",
                        ses_th._conn_name,  # type: ignore [attr-defined] # noqa: F821
                    )


# for session in mng_._thread_sessions.values():
#    if session.transaction is None:
#        raise exception(session._conn_name)
