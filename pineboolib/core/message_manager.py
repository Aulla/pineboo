"""
Module for Manager class.
"""
# from PyQt5 import QtWidgets
from typing import Any, Iterable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import dgi_schema  # pragma: no cover


class Manager(object):
    """
    Creates a sensible DGI interface connection to show messages.

    Mainly used to display progress in splash screen
    """

    _dgi: Optional["dgi_schema.dgi_schema"] = None

    def __init__(self, dgi: "dgi_schema.dgi_schema") -> None:
        """Create a Manager with specified DGI."""
        self._dgi = dgi

    def send(self, type_: str, function_: Optional[str] = None, data_: Iterable[Any] = None) -> Any:
        """Send a progress event to the manager."""
        if self._dgi is None:
            return None

        obj_ = getattr(self._dgi, type_, None)
        ret_ = None
        if obj_:
            if function_ is not None:
                attr_ = getattr(obj_, function_, None)
            else:
                attr_ = obj_

            if attr_ is None:
                return
            else:
                if not data_:
                    ret_ = attr_()
                else:
                    ret_ = attr_(*data_)
                # QtWidgets.QApplication.processEvents()

        if ret_ is not None:
            return ret_
