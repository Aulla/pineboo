"""Decorators module."""

from pineboolib.core.utils import logging, utils_base
from pineboolib import application
from pineboolib.qsa import utils


from typing import Callable, Any, TypeVar, cast, Optional

import threading
import functools
import traceback
import time
from sqlalchemy import exc  # type: ignore [import]

TYPEFN = TypeVar("TYPEFN", bound=Callable[..., Any])

LOGGER = logging.get_logger(__name__)


def atomic(
    conn_name: str = "default", wait: bool = True, after_commit: Optional[Callable] = None
) -> "TYPEFN":  # type: ignore [type-var, misc]
    """Return pineboo atomic decorator."""

    def decorator(fun_: TYPEFN) -> TYPEFN:
        @functools.wraps(fun_)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = utils_base.session_id(conn_name)
            if wait:
                _wait(key)

            mng_ = application.PROJECT.conn_manager
            while True:
                new_session = utils.driver_session(conn_name)
                if mng_.check_connections():
                    break

            mng_.useConn(conn_name)._session_atomic = new_session
            result_ = None
            try:
                try:
                    with new_session.begin():
                        session_id = utils_base.session_id()
                        orig_transaction = new_session.transaction
                        LOGGER.debug(
                            "New atomic session : %s, connection : %s, transaction: %s",
                            new_session,
                            conn_name,
                            orig_transaction,
                        )

                        try:
                            result_ = fun_(*args, **kwargs)
                            if new_session.transaction is None:
                                LOGGER.warning(
                                    "FIXME:: LA TRANSACCION ATOMICA FINALIZÓ ANTES DE TIEMPO:\nmodule:%s\nfunction:%s\n"
                                    % (fun_.__module__, fun_)
                                )
                            elif new_session.transaction is not orig_transaction:
                                LOGGER.warning(
                                    "FIXME:: LA TRANSACCION ATOMICA FINAL NO ES LA INICIAL:\n module:%s\n function:%s\n"
                                    % (fun_.__module__, fun_)
                                    + "inicial:%s\n final:%s\n"
                                    % (orig_transaction, new_session.transaction)
                                )

                            elif after_commit:
                                # Solo se ejecuta si la transaccion inicial y final es la misma
                                after_commit(session_id)  # type: ignore [truthy-function]
                        except Exception as error:
                            LOGGER.warning(
                                "ATOMIC STACKS\nARGS:%s.\nKWARGS:%s.\nAPP: %s.\nERROR: %s.",
                                args,
                                kwargs,
                                "".join(traceback.format_exc(limit=None)),
                                "".join(traceback.format_stack(limit=None)),
                                stack_info=True,
                            )
                            raise error
                except exc.ResourceClosedError as error:
                    LOGGER.warning("Error al cerrar la transacción : %s, pero continua ....", error)

                _delete_data(conn_name, wait)

            except Exception as error:
                _delete_data(conn_name, wait)
                raise error

            return result_

        mock_fn: TYPEFN = cast(TYPEFN, wrapper)
        return mock_fn

    return decorator  # type: ignore [return-value] # noqa: F723


def serialize(conn_name: str = "default") -> "TYPEFN":  # type: ignore [type-var, misc]
    """Return pineboo atomic decorator."""

    def decorator(fun_: "TYPEFN") -> "TYPEFN":
        @functools.wraps(fun_)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = utils_base.session_id(conn_name)
            _wait(key)

            while True:
                if application.PROJECT.conn_manager.check_connections():
                    break

            # new_session = utils.driver_session(conn_name)[1]

            result_ = None
            try:
                LOGGER.debug("New serialize function connection : %s", conn_name)

                try:
                    result_ = fun_(*args, **kwargs)
                except Exception as error:
                    LOGGER.warning(
                        "SERIALIZE STACKS\nARGS:%s.\nKWARGS:%s.\nAPP: %s.\nERROR: %s.",
                        args,
                        kwargs,
                        "".join(traceback.format_exc(limit=None)),
                        "".join(traceback.format_stack(limit=None)),
                        stack_info=True,
                    )
                    raise error

                _delete_data(conn_name)

            except Exception as error:
                _delete_data(conn_name)
                raise error

            return result_

        mock_fn: TYPEFN = cast(TYPEFN, wrapper)
        return mock_fn

    return decorator  # type: ignore [return-value] # noqa: F723


def _wait(key: str) -> None:
    id_thread = threading.current_thread().ident
    if id_thread not in application.SERIALIZE_LIST.keys():
        application.SERIALIZE_LIST[id_thread] = []  # type: ignore [index] # noqa: F821

    application.SERIALIZE_LIST[id_thread].append(key)  # type: ignore [index] # noqa: F821

    while (
        application.SERIALIZE_LIST[id_thread][0] != key  # type: ignore [index] # noqa: F821
    ):  # type: ignore [index] # noqa: F821
        time.sleep(0.01)


def _delete_data(conn_name: str = "", wait: bool = True) -> None:
    """Delete data."""
    mng_ = application.PROJECT.conn_manager
    conn = mng_.useConn(conn_name)

    if conn is not None:
        if application.SHOW_CONNECTION_EVENTS:
            LOGGER.debug("Removing sessions from connection %s", conn_name)
        if conn._session_atomic is not None:
            conn._session_atomic.close()
            conn._session_atomic = None
        if conn._session_legacy is not None:
            conn._session_legacy.close()
            conn._session_legacy = None

    if mng_.REMOVE_CONNECTIONS_AFTER_ATOMIC:
        time.sleep(0.05)
        for item in mng_.enumerate():
            if application.SHOW_CONNECTION_EVENTS:
                LOGGER.debug("Removing connection %s after decorator", item)
            mng_.removeConn(item)

    if wait:
        id_thread: int = threading.current_thread().ident or -1
        key = utils_base.session_id(conn_name)
        if id_thread in application.SERIALIZE_LIST.keys():
            if key in application.SERIALIZE_LIST[id_thread]:  # type: ignore [index] # noqa: F821
                application.SERIALIZE_LIST[id_thread].remove(
                    key
                )  # type: ignore [index] # noqa: F821
