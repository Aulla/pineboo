"""Dgi_fcgi module."""
# # -*- coding: utf-8 -*-
from pineboolib import logging
from pineboolib.plugins.dgi import dgi_schema
from pineboolib.application.utils.check_dependencies import check_dependencies
from pineboolib.fllegacy import systype

from pineboolib import application

from typing import Any, Mapping


LOGGER = logging.get_logger(__name__)


class DgiFcgi(dgi_schema.DgiSchema):
    """Dgi_fcgi class."""

    _fcgiCall: str
    _fcgiSocket: str

    def __init__(self) -> None:
        """Inicialize."""
        super().__init__()  # desktopEnabled y mlDefault a True
        self._name = "fcgi"
        self._alias = "FastCGI"
        self._fcgi_call = "flfactppal.iface.fcgiProcessRequest"
        self._fcgi_socket = "pineboo-fastcgi.socket"
        self.setUseDesktop(False)
        self.setUseMLDefault(False)
        self.showInitBanner()
        check_dependencies({"flup": "flup-py3"})

    def alternativeMain(self, main_) -> Any:
        """Process alternative main."""
        from flup.server.fcgi import WSGIServer  # type: ignore

        LOGGER.info("=============================================")
        LOGGER.info("FCGI:INFO: Listening socket %s", self._fcgi_socket)
        LOGGER.info("FCGI:INFO: Sending queries to %s", self._fcgi_call)
        par_ = Parser(main_, self._fcgi_call)
        WSGIServer(par_.call, bindAddress=self._fcgi_socket).run()

    def setParameter(self, param: str) -> None:
        """Set parameters."""
        if param.find(":") > -1:
            params_list = param.split(":")
            self._fcgi_call = params_list[0]
            self._fcgi_socket = params_list[1]
        else:
            self._fcgi_call = param


"""
Esta clase lanza contra el arbol qsa la consulta recibida y retorna la respuesta proporcionada, si procede
"""


class Parser(object):
    """Parser class."""

    _prj = None
    _call_script: str

    def __init__(self, prj: Any, callScript: str) -> None:
        """Inicialize."""
        self._prj = prj
        self._call_script = callScript

    def call(self, environ: Mapping[str, Any], start_response) -> Any:
        """Return value from called function."""
        start_response("200 OK", [("Content-Type", "text/html")])
        query_str = environ["QUERY_STRING"]
        try:
            retorno_: Any = application.PROJECT.call(self._call_script, query_str)
        except Exception:
            qsa_sys = systype.SysType()

            LOGGER.info(self._call_script, environ["QUERY_STRING"])
            retorno_ = (
                """<html><head><title>Pineboo %s - FastCGI - </title></head><body><h1>Function %s not found!</h1></body></html>"""
                % (qsa_sys.version(), self._call_script)
            )
            pass
        LOGGER.info("FCGI:INFO: Processing '%s' ...", environ["QUERY_STRING"])

        return retorno_
