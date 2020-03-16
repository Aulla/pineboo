"""Formdbwidget module."""
# # -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore

from pineboolib.application.database import pnsqlcursor

# from pineboolib.fllegacy import flapplication
from pineboolib import application, logging


from typing import Set, Tuple, Optional, Any, TYPE_CHECKING
import weakref
import sys

if TYPE_CHECKING:
    from pineboolib.application import xmlaction  # noqa: F401
    from pineboolib.interfaces import isqlcursor

LOGGER = logging.get_logger(__name__)


class FormDBWidget(QtWidgets.QWidget):
    """FormDBWidget class."""

    closed = QtCore.pyqtSignal()
    cursor_: Optional["isqlcursor.ISqlCursor"]
    form: Any
    iface: Optional[object]
    signal_test = QtCore.pyqtSignal(str, QtCore.QObject)

    def __init__(self, action: Optional["xmlaction.XMLAction"] = None):
        """Inicialize."""

        super().__init__()

        self._module = sys.modules[self.__module__]
        self._action = action
        self.iface = None
        self.cursor_ = None
        # self.parent_ = parent or QtWidgets.QWidget()

        # if parent and hasattr(parent, "parentWidget"):
        #    self.parent_ = parent.parentWidget()

        self.form = None  # Limpiar self.form al inicializar... Luego flformdb se asigna..
        # from pineboolib.fllegacy import flformdb

        # if isinstance(parent, flformdb.FLFormDB):
        #    self.form = parent

        self._formconnections: Set[Tuple] = set([])

        self._class_init()

    def module_connect(self, sender: Any, signal: str, receiver: Any, slot: str) -> None:
        """Connect two objects."""

        # print(" > > > connect:", sender, " signal ", str(signal))
        from pineboolib.application import connections

        signal_slot = connections.connect(sender, signal, receiver, slot, caller=self)
        if not signal_slot:
            return

        self._formconnections.add(signal_slot)

    def module_disconnect(self, sender: Any, signal: str, receiver: Any, slot: str) -> None:
        """Disconnect two objects."""

        # print(" > > > disconnect:", self)
        from pineboolib.application import connections

        signal_slot = connections.disconnect(sender, signal, receiver, slot, caller=self)
        if not signal_slot:
            return

        for sl in self._formconnections:
            # PyQt5-Stubs misses signal.signal
            if (
                sl[0].signal == getattr(signal_slot[0], "signal")
                and sl[1].__name__ == signal_slot[1].__name__
            ):
                self._formconnections.remove(sl)
                break

    def obj(self) -> "FormDBWidget":
        """Return self."""
        return self

    def parent(self) -> QtWidgets.QWidget:
        """Return parent widget."""

        return self.parentWidget()

    def _class_init(self) -> None:
        """Initialize the class."""
        pass

    # def init(self):
    #    """Evento init del motor. Llama a interna_init en el QS"""
    #    pass

    def closeEvent(self, event: QtCore.QEvent) -> None:
        """Close event."""

        if self._action is None:
            self._action = getattr(self.parent(), "_action")

        if self._action is not None:
            LOGGER.debug("closeEvent para accion %r", self._action.name)
        self.closed.emit()
        event.accept()  # let the window close
        self.doCleanUp()

    def doCleanUp(self) -> None:
        """Cleanup gabange and connections."""

        self.clear_connections()
        iface = getattr(self, "iface", None)
        if iface is not None and self._action is not None:
            from pineboolib.core.garbage_collector import check_gc_referrers

            check_gc_referrers(
                "FormDBWidget.iface:" + iface.__class__.__name__,
                weakref.ref(self.iface),
                self._action.name,
            )

            delattr(self.iface, "ctx")

            del self._action.formrecord_widget

            self.iface = None
            self._action.formrecord_widget = None

    def clear_connections(self) -> None:
        """Clear al conecctions established on the module."""

        # Limpiar todas las conexiones hechas en el script
        for signal, slot in self._formconnections:
            try:
                signal.disconnect(slot)
                LOGGER.debug("Señal desconectada al limpiar: %s %s" % (signal, slot))
            except Exception:
                # LOGGER.exception("Error al limpiar una señal: %s %s" % (signal, slot))
                pass
        self._formconnections.clear()

    def child(self, child_name: str) -> Any:
        """Return child from name."""
        ret = None
        if self.form:
            ret = self.form.child(child_name)

            if ret is None:
                if child_name == super().objectName():
                    return self.form
                else:
                    ret = getattr(self.form, child_name, None)

        if ret is None:
            parent = self.parent()
            if parent is not None:
                ret = getattr(parent, child_name, None)

        if ret is None:
            raise Exception("control %s not found!" % child_name)

        return ret

    def cursor(self) -> "isqlcursor.ISqlCursor":  # type: ignore [override] # noqa F821
        """Return cursor associated."""

        if not self.cursor_:
            if self.form is not None:
                self.cursor_ = self.form.cursor_

            if not self.cursor_:
                if self._action:
                    action = application.PROJECT.conn_manager.manager().action(self._action.name)
                    self.cursor_ = pnsqlcursor.PNSqlCursor(action.name())
                else:
                    raise Exception("_action is empty!.")

        return self.cursor_

    def __getattr__(self, name: str) -> QtWidgets.QWidget:
        """Guess if attribute can be found in other related objects."""
        print("**", name, self.parent())
        ret_ = getattr(self.cursor_, name, None)
        if ret_ is None and self.parent():
            parent_ = self.parent()
            ret_ = getattr(parent_, name, None)
            if ret_ is None:
                script = getattr(parent_, "script", None)
                if script is not None:
                    ret_ = getattr(script, name, None)

        if ret_ is None and not TYPE_CHECKING:
            # FIXME: q3widgets should not interact with fllegacy
            from pineboolib.fllegacy import flapplication

            ret_ = getattr(flapplication.aqApp, name, None)
            if ret_ is not None:
                LOGGER.warning(
                    "FormDBWidget: Coearcing attribute %r from aqApp (should be avoided)" % name
                )

        if ret_ is None:
            raise AttributeError("FormDBWidget: Attribute does not exist: %r" % name)

        return ret_

    # def __hasattr__(self, name: str) -> bool:
    #    """Guess if attribute can be found in other related objects."""

    #    ret_ = hasattr(self.cursor_, name)
    #    if not ret_:
    #        parent_ = self.parent()
    #        ret_ = hasattr(parent_, name)
    #        if not ret_:
    #            script = getattr(parent_, "script", None)
    #            if script is not None:
    #                ret_ = hasattr(script, name)

    #    return ret_

    # def __iter__(self) -> Any:
    #    """Return iter."""

    #    self._iter_current = -1
    #    return self

    # def __next__(self) -> Any:
    #    """Return next."""

    #    self._iter_current = 0 if self._iter_current == -1 else self._iter_current + 1

    #    list_ = [attr for attr in dir(self) if not attr[0] == "_"]
    #    if self._iter_current >= len(list_):
    #        raise StopIteration

    #    return list_[self._iter_current]
