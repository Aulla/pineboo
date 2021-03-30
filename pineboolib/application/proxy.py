"""
Proxy Module.
"""
from pineboolib import logging
from pineboolib.core import garbage_collector

from typing import Any, Optional, Dict, Callable, TYPE_CHECKING
import threading

if TYPE_CHECKING:
    from pineboolib.fllegacy.flformdb import FLFormDB  # noqa: F401 # pragma: no cover
    from pineboolib.qsa import formdbwidget  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class DelayedObjectProxyLoader(object):
    """
    Delay load of an object until its first accessed.

    This is used to create entities such "formclientes" or "flfactppal" ahead of time and
    publish them in pineboolib.qsa.qsa so the code can freely call flfactppal.iface.XXX.

    Once the first attribute is called, the object is loaded.

    QSA Code should avoid calling directly "formclientes" and instead use QSADictModules or SafeQSA
    """

    def __init__(
        self,
        obj: Callable[..., "formdbwidget.FormDBWidget"],
        name: Optional[str] = None,
        *args: str,
        **kwargs: str
    ) -> None:
        """Initialize."""
        LOGGER.trace("obj: %r", obj)
        self._name: str = name or "unnamed-loader"
        self._obj = obj
        self._args = args
        self._kwargs = kwargs
        self.loaded_obj: Dict[int, Optional["formdbwidget.FormDBWidget"]] = {}

    def __load(self) -> "formdbwidget.FormDBWidget":
        """
        Load a new object.

        @return objeto nuevo o si ya existe , cacheado
        """
        list_name = self._name.split(".")
        id_thread = threading.current_thread().ident

        # limpieza de objetos
        for key in list(self.loaded_obj.keys()):
            if key not in list([thread.ident for thread in threading.enumerate()]):
                obj_ = self.loaded_obj[key]
                self.loaded_obj[key] = None
                del self.loaded_obj[key]
                garbage_collector.check_delete(obj_, "proxy.widget")

        if not list_name[-1].startswith("formRecord"):
            if id_thread in self.loaded_obj.keys():
                if getattr(
                    self.loaded_obj[id_thread], "_loader", True  # type: ignore [index] # noqa: F821
                ):
                    return self.loaded_obj[  # type: ignore [index, return-value] # noqa: F821, F723
                        id_thread  # type: ignore [index, return-value] # noqa: F821, F723
                    ]

        self.loaded_obj[id_thread] = self._obj(  # type: ignore [index] # noqa: F821
            *self._args, **self._kwargs
        )

        LOGGER.debug(
            "DelayedObjectProxyLoader: name: %s, object: %s( *%s **%s) ---> %s",
            self._name,
            self._obj,
            self._args,
            self._kwargs,
            self.loaded_obj[id_thread],  # type: ignore [index] # noqa: F821
        )

        return_object = self.loaded_obj[id_thread]  # type: ignore [index] # noqa: F821

        if return_object is None:
            del self.loaded_obj[id_thread]  # type: ignore [arg-type] # noqa: F821
            raise Exception("Failed to load object")
        else:
            return_object.set_proxy_parent(self)
            return return_object

    def class_(self):
        """Return class."""
        return self._obj(*self._args, **self._kwargs)

    def __getattr__(self, name: str) -> Any:  # Solo se lanza si no existe la propiedad.
        """
        Return attribute or method from internal object.

        @param name. Nombre del la función buscada
        @return el objecto del XMLAction afectado
        """

        obj_ = self.__load()
        return getattr(obj_, name, getattr(obj_, name, None))
