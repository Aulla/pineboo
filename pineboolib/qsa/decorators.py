"""Decorators module."""
from pineboolib.core.utils import logging, utils_base
from pineboolib import application
from . import utils


from typing import Callable, Any, TypeVar, cast
import threading
import functools
import traceback
import time
from sqlalchemy import exc, orm

TYPEFN = TypeVar("TYPEFN", bound=Callable[..., Any])

LOGGER = logging.get_logger(__name__)


def atomic(conn_name: str = "default", wait: bool = True) -> TYPEFN:
    """Return pineboo atomic decorator."""

    def decorator(fun_: TYPEFN) -> TYPEFN:
        @functools.wraps(fun_)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            key = utils_base.session_id(conn_name)
            if wait:
                _wait(key)

            application.PROJECT.conn_manager.current_atomic_sessions[
                key
            ], new_session = utils.driver_session(conn_name)
            result_ = None
            try:
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
                            if new_session.transaction is None:
                                LOGGER.warning(
                                    "FIXME:: LA TRANSACCION ATOMICA FINALIZÓ ANTES DE TIEMPO:\nmodule:%s\nfunction:%s\n",
                                    fun_.__module__,
                                    fun_,
                                )
                        except Exception as error:
                            LOGGER.warning(
                                "ATOMIC STACKS\nAPP: %s.\nERROR: %s.",
                                "".join(traceback.format_exc(limit=None)),
                                "".join(traceback.format_stack(limit=None)),
                                stack_info=True,
                            )
                            raise error
                except exc.ResourceClosedError as error:
                    LOGGER.warning("Error al cerrar la transacción : %s, pero continua ....", error)

                _delete_data(new_session, key, wait)

            except Exception as error:
                _delete_data(new_session, key, wait)
                raise error

            return result_

        mock_fn: TYPEFN = cast(TYPEFN, wrapper)
        return mock_fn

    return decorator  # type: ignore [return-value] # noqa: F723


def serialize(conn_name: str = "default") -> TYPEFN:
    """Return pineboo atomic decorator."""

    def decorator(fun_: TYPEFN) -> TYPEFN:
        @functools.wraps(fun_)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = utils_base.session_id(conn_name)
            _wait(key)

            new_session = utils.driver_session(conn_name)[1]

            result_ = None
            try:
                LOGGER.debug("New serialize session : %s, connection : %s", new_session, conn_name)

                try:
                    result_ = fun_(*args, **kwargs)
                except Exception as error:
                    LOGGER.warning(
                        "SERIALIZE STACKS\nAPP: %s.\nERROR: %s.",
                        "".join(traceback.format_exc(limit=None)),
                        "".join(traceback.format_stack(limit=None)),
                        stack_info=True,
                    )
                    raise error

                _delete_data(new_session, key)

            except Exception as error:

                _delete_data(new_session, key)
                raise error

            return result_

        mock_fn: TYPEFN = cast(TYPEFN, wrapper)
        return mock_fn

    return decorator  # type: ignore [return-value] # noqa: F723


def _delete_data(session: "orm.Session", key: str, wait: bool = True) -> None:
    """Delete data."""

    application.PROJECT.conn_manager.remove_session(session)
    _delete_session(key, wait)


def _wait(key: str) -> None:
    id_thread = threading.current_thread().ident
    if id_thread not in application.SERIALIZE_LIST.keys():
        application.SERIALIZE_LIST[id_thread] = []  # type: ignore [index] # noqa: F821

    application.SERIALIZE_LIST[id_thread].append(key)  # type: ignore [index] # noqa: F821

    while (
        application.SERIALIZE_LIST[id_thread][0] != key  # type: ignore [index] # noqa: F821
    ):  # type: ignore [index] # noqa: F821
        time.sleep(0.01)

    application.PROJECT.conn_manager.check_connections()


def _delete_session(key: str, wait: bool = True) -> None:
    """Delete atomic_session."""
    mng_ = application.PROJECT.conn_manager
    if key in mng_.current_atomic_sessions.keys():
        session_key = mng_.current_atomic_sessions[key]
        if session_key in mng_._thread_sessions.keys():
            del mng_._thread_sessions[session_key]

        del mng_.current_atomic_sessions[key]

    id_thread = threading.current_thread().ident

    # Delete all thread connections.
    if mng_.REMOVE_CONNECTIONS_AFTER_ATOMIC:
        for conn_name in mng_.enumerate():
            mng_.removeConn(conn_name)

    if wait and id_thread in application.SERIALIZE_LIST.keys():
        if key in application.SERIALIZE_LIST[id_thread]:  # type: ignore [index] # noqa: F821
            application.SERIALIZE_LIST[id_thread].remove(key)  # type: ignore [index] # noqa: F821
