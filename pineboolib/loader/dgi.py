"""DGI Module."""

from pineboolib import logging

from typing import Callable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces.dgi_schema import dgi_schema  # pragma: no cover
    from pineboolib.plugins.dgi.dgi_qt import dgi_qt  # pragma: no cover
    from pineboolib.plugins.dgi.dgi_fcgi import dgi_fcgi  # pragma: no cover


LOGGER = logging.get_logger(__name__)


def load_dgi(name: str, param: Any) -> "dgi_schema":
    """Load a DGI module dynamically."""

    dgi_entrypoint = DGILoader.load_dgi(name)

    try:
        dgi = dgi_entrypoint()  # FIXME: Necesitamos ejecutar código dinámico tan pronto?
    except Exception:
        LOGGER.exception("Error inesperado al cargar el módulo DGI %s" % name)
        raise

    if param:
        dgi.setParameter(param)

    LOGGER.debug("DGI loaded: %s", name)

    return dgi


class DGILoader(object):
    """DGILoader Class."""

    @staticmethod
    def load_dgi_qt() -> "dgi_qt.DgiQt":
        """Load dgi qt."""

        from pineboolib.plugins.dgi.dgi_qt import dgi_qt as dgi

        return dgi.DgiQt()

    @staticmethod
    def load_dgi_fcgi() -> "dgi_fcgi.DgiFcgi":
        """Load dgi fcgi."""

        from pineboolib.plugins.dgi.dgi_fcgi import dgi_fcgi as dgi

        return dgi.DgiFcgi()

    @classmethod
    def load_dgi(cls, name: str) -> Callable:
        """Load dgi specified by name."""

        loader = getattr(cls, "load_dgi_%s" % name, None)
        if not loader:
            raise ValueError("Unknown DGI %s" % name)
        return loader
