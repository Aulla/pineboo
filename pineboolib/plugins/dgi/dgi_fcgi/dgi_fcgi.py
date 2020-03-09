"""Dgi_fcgi module."""
# # -*- coding: utf-8 -*-
from pineboolib import logging
from pineboolib.plugins.dgi.dgi_schema import dgi_schema
from pineboolib.application.utils.check_dependencies import check_dependencies

from pineboolib import application

from typing import Any, Mapping


LOGGER = logging.get_logger(__name__)


class dgi_fcgi(dgi_schema):
    """Dgi_fcgi class."""

    _fcgiCall: str
    _fcgiSocket: str

    def __init__(self) -> None:
        """Inicialize."""
        super(dgi_fcgi, self).__init__()  # desktopEnabled y mlDefault a True
        self._name = "fcgi"
        self._alias = "FastCGI"
        self._fcgiCall = "flfactppal.iface.fcgiProcessRequest"
        self._fcgiSocket = "pineboo-fastcgi.socket"
        self.setUseDesktop(False)
        self.setUseMLDefault(False)
        self.showInitBanner()
        check_dependencies({"flup": "flup-py3"})

    def alternativeMain(self, main_) -> Any:
        """Process alternative main."""
        from flup.server.fcgi import WSGIServer  # type: ignore

        LOGGER.info("=============================================")
        LOGGER.info("FCGI:INFO: Listening socket %s", self._fcgiSocket)
        LOGGER.info("FCGI:INFO: Sending queries to %s", self._fcgiCall)
        par_ = parser(main_, self._fcgiCall)
        WSGIServer(par_.call, bindAddress=self._fcgiSocket).run()

    def setParameter(self, param: str) -> None:
        """Set parameters."""
        if param.find(":") > -1:
            p = param.split(":")
            self._fcgiCall = p[0]
            self._fcgiSocket = p[1]
        else:
            self._fcgiCall = param


"""
Esta clase lanza contra el arbol qsa la consulta recibida y retorna la respuesta proporcionada, si procede
"""


class parser(object):
    """Parser class."""

    _prj = None
    _callScript: str

    def __init__(self, prj: Any, callScript: str) -> None:
        """Inicialize."""
        self._prj = prj
        self._callScript = callScript

    def call(self, environ: Mapping[str, Any], start_response) -> Any:
        """Return value from called function."""
        start_response("200 OK", [("Content-Type", "text/html")])
        aList = environ["QUERY_STRING"]
        try:
            retorno_: Any = application.PROJECT.call(self._callScript, aList)
        except Exception:
            from pineboolib.fllegacy.systype import SysType

            qsa_sys = SysType()

            LOGGER.info(self._callScript, environ["QUERY_STRING"])
            retorno_ = (
                """<html><head><title>Pineboo %s - FastCGI - </title></head><body><h1>Function %s not found!</h1></body></html>"""
                % (qsa_sys.version(), self._callScript)
            )
            pass
        LOGGER.info("FCGI:INFO: Processing '%s' ...", environ["QUERY_STRING"])

        return retorno_
