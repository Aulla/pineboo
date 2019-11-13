"""Dgi_server module."""
# # -*- coding: utf-8 -*-
import traceback
import inspect
import datetime

from PyQt5 import QtCore, QtWidgets

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher  # type: ignore

from pineboolib import logging
from pineboolib.plugins.dgi.dgi_schema import dgi_schema


from typing import Any, TypeVar, Union, Dict, List, Optional

_T0 = TypeVar("_T0")

logger = logging.getLogger(__name__)

cursor_dict: Dict[str, Any] = {}


class Parser_options(object):
    """Parser_options class."""

    def hello(self, *args) -> str:
        """Return hello msg."""

        return "Welcome to pineboo server"

    def db_name(self, *args) -> str:
        """Return database name."""
        from pineboolib.fllegacy.flapplication import aqApp

        return aqApp.db().DBName()

    def __getattr__(self, name) -> None:
        """Return fail attribute location message."""
        print("** Parser_options no contiene", name)


Parser_server = Parser_options()


def normalize_data(data: _T0) -> Union[list, _T0]:
    """Normalize value before send to client."""
    if isinstance(data, (list, tuple)):
        new_data: List[Union[str, Any]] = []
        for line in data:
            if isinstance(line, (datetime.date, datetime.time)):
                # print("premio!!", type(line), line, type(data))
                new_data.append(line.__str__())
            else:
                # print(type(line), line)
                new_data.append(normalize_data(line))

    return new_data


class Parser(object):
    """Parser class."""

    @Request.application  # type: ignore
    def receive(self, request: Any) -> Any:
        """Process a clinet request."""
        response = None
        # print("**", request.data)
        try:
            response = JSONRPCResponseManager.handle(request.data, dispatcher)
        except Exception:
            return Response("Not found", mimetype="application/json")

        return Response(response.json, mimetype="application/json")

    @dispatcher.add_method  # type: ignore
    def call_function(*args) -> Optional[Any]:
        """Return result from a called function."""
        dict_: Dict[str, Any] = args[0]  # type: ignore
        func_name = dict_["function"]
        arguments = dict_["arguments"]
        from pineboolib.application import project

        result = project.call(func_name, arguments)
        print("Llamada remota: %s(%s) --> %s" % (func_name, ", ".join(arguments), result))
        return result

    @dispatcher.add_method  # type: ignore
    def dbdata(*args) -> Union[List[Any], str]:
        """Return data from database."""
        dict_: Dict[str, Any] = args[0]  # type: ignore
        from pineboolib.application import project

        list_fun: List[str] = dict_["function"].split("__")  # type: ignore
        fun_name = list_fun[1]
        id_conn = list_fun[0]
        cursor = None

        if fun_name == "hello":
            project.conn_manager.removeConn("%s_remote_client" % id_conn)
            # list_to_delete = []
            for k in list(cursor_dict.keys()):
                if k.startswith(id_conn):
                    cursor_dict[k] = None
                    del cursor_dict[k]

        conn = project.conn_manager.useConn("%s_remote_client" % id_conn)

        # print("--->", dict_["function"], dict_["arguments"]["cursor_id"] if "cursor_id" in dict_["arguments"] else None)

        if "cursor_id" in dict_["arguments"]:
            if not "%s_%s" % (id_conn, dict_["arguments"]["cursor_id"]) in cursor_dict.keys():
                cursor_dict["%s_%s" % (id_conn, dict_["arguments"]["cursor_id"])] = conn.cursor()

            cursor = cursor_dict["%s_%s" % (id_conn, dict_["arguments"]["cursor_id"])]

        if fun_name == "execute":
            try:
                if cursor is None:
                    raise Exception("No cursor")
                cursor.execute(dict_["arguments"]["sql"])
            #    for data in cursor_dict[dict_["arguments"]["cursor_id"]]:
            #        res.append(data)

            except Exception:
                print(
                    "Error %s  %s %s"
                    % (dict_["arguments"]["cursor_id"], dict_["arguments"]["sql"], fun_name),
                    traceback.format_exc(),
                )

        elif fun_name == "fetchone":
            ret: List[Any] = []
            try:
                if cursor is None:
                    raise Exception("No cursor")
                ret = cursor.fetchone()
            except Exception:
                print("Error %s" % fun_name, traceback.format_exc())
            return normalize_data(ret)

        elif fun_name == "refreshQuery":
            try:
                if cursor is None:
                    raise Exception("No cursor")
                fun = getattr(conn.driver(), fun_name)

                fun(
                    dict_["arguments"]["curname"],
                    dict_["arguments"]["fields"],
                    dict_["arguments"]["table"],
                    dict_["arguments"]["where"],
                    cursor,
                    conn.driver().conn_,
                )
            except Exception:
                print("Error refreshQuery", traceback.format_exc())

        elif fun_name == "refreshFetch":
            try:
                if cursor is None:
                    raise Exception("No cursor")
                fun = getattr(conn.driver(), fun_name)

                fun(
                    dict_["arguments"]["number"],
                    dict_["arguments"]["curname"],
                    dict_["arguments"]["table"],
                    cursor,
                    dict_["arguments"]["fields"],
                    dict_["arguments"]["where_filter"],
                )
            except Exception:
                print("Error refreshFetch", traceback.format_exc())

        elif fun_name == "fetchAll":
            try:
                if cursor is None:
                    raise Exception("No cursor")
                fun = getattr(conn.driver(), fun_name)

                ret = fun(
                    cursor,
                    dict_["arguments"]["tablename"],
                    dict_["arguments"]["where_filter"],
                    dict_["arguments"]["fields"],
                    dict_["arguments"]["curname"],
                )
                return normalize_data(ret)
            except Exception:
                print("Error fetchAll", traceback.format_exc())

        elif fun_name == "fetchall":
            try:
                if cursor is None:
                    raise Exception("No cursor")
                ret_ = cursor.fetchall()
                return normalize_data(ret_)
            except Exception:
                print("Error fetchall", traceback.format_exc())

        elif fun_name == "close":
            try:
                if cursor is None:
                    raise Exception("No cursor")
                cursor.close()
                del cursor
                del cursor_dict["%s_%s" % (id_conn, dict_["arguments"]["cursor_id"])]
                # print("3 close", dict_["arguments"]["cursor_id"])
            except Exception:
                print("Error %s" % fun_name, traceback.format_exc())

        else:

            fun = getattr(conn.driver(), fun_name, None)

            if fun is None:
                fun = getattr(Parser_server, fun_name, None)

            if fun is not None:
                expected_args = inspect.getargspec(fun)[0]
                args_num = len(expected_args)
                # print("-->", fun, dict_["arguments"][:args_num])
                return normalize_data(fun(*dict_["arguments"][:args_num]))

            return "Desconocido"

        return []


class dgi_server(dgi_schema):
    """di_server class."""

    _par: Optional[Parser]

    def __init__(self) -> None:
        """Inicialize."""
        # desktopEnabled y mlDefault a True
        super().__init__()
        self._par = None
        self._name = "server"
        self._alias = "SERVER"
        self._listenSocket = 4000
        self.setUseDesktop(False)
        self.setUseMLDefault(False)
        self.setLocalDesktop(False)
        self.showInitBanner()
        self._mainForm = None
        self._show_object_not_found_warnings = False
        self.qApp = QtWidgets.QApplication
        # self.ParserDGI = ParserJson()

    def alternativeMain(self, options: Any) -> None:
        """Load alternative main."""
        if options.dgi_parameter:
            self._listenSocket = int(options.dgi_parameter)

    def exec_(self) -> None:
        """Execute DGI."""
        self._par = Parser()
        self.launchServer()

    def launchServer(self) -> None:
        """Launch server."""
        # run_simple('localhost', self._listenSocket, self._par.receive, ssl_context="adhoc")
        if self._par is None:
            raise Exception("Parser not found")
        run_simple("0.0.0.0", self._listenSocket, self._par.receive)

    def __getattr__(self, name: str) -> Optional[QtCore.QObject]:
        """Return a attribute from specific object."""
        return super().resolveObject(self._name, name)

    def accept_file(self, name: str) -> bool:
        """Return files accepted by client."""

        return False if name.endswith((".ui")) else True
