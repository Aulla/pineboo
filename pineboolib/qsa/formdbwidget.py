"""Formdbwidget module."""
# # -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtCore  # type: ignore[import]

from pineboolib.application import connections
from pineboolib.fllegacy import flsqlcursor

from pineboolib import logging, application


from typing import Set, Tuple, Optional, Any, cast, Union, TYPE_CHECKING
import traceback
import sys
import types


if TYPE_CHECKING:
    from pineboolib.application import xmlaction  # noqa: F401 # pragma: no cover
    from pineboolib.fllegacy import flformdb  # noqa: F401 # pragma: no cover
    from pineboolib.application import proxy

LOGGER = logging.get_logger(__name__)


class FormDBWidget(QtWidgets.QWidget):
    """FormDBWidget class."""

    closed = QtCore.pyqtSignal()
    cursor_: Optional["flsqlcursor.FLSqlCursor"]
    _form: Optional[Union["flformdb.FLFormDB", "FormDBWidget"]]
    _action: Optional["xmlaction.XMLAction"]
    _formconnections: Set[Tuple]
    _my_proxy: "proxy.DelayedObjectProxyLoader"
    iface: Optional[object]
    signal_test = QtCore.pyqtSignal(str, QtCore.QObject)
    _loaded: bool

    def __init__(self, action: Optional["xmlaction.XMLAction"] = None) -> None:
        """Inicialize."""

        super().__init__()

        self._action = action
        self.name = self.__module__
        self.iface = None
        self.cursor_ = None
        self._loaded = False
        self._form = None
        self._formconnections = set([])

        self._class_init()

    def module_connect(self, sender: Any, signal: str, receiver: Any, slot: str) -> None:
        """Connect two objects."""

        signal_slot = connections.connect(sender, signal, receiver, slot, caller=self)
        if signal_slot:
            self._formconnections.add(signal_slot)

    def module_disconnect(self, sender: Any, signal: str, receiver: Any, slot: str) -> None:
        """Disconnect two objects."""

        # print(" > > > disconnect:", self)

        signal_slot = connections.disconnect(sender, signal, receiver, slot)
        if signal_slot:
            for conn_ in self._formconnections:
                # PyQt6-Stubs misses signal.signal
                if (
                    conn_[0].signal
                    == signal_slot[0].signal  # type: ignore [attr-defined] # noqa: F821
                    and conn_[1].__name__ == signal_slot[1].__name__
                ):
                    self._formconnections.remove(conn_)
                    break

    def obj(self) -> "FormDBWidget":
        """Return self."""
        return self

    def mainWidget(self) -> "FormDBWidget":
        """Return mainWidget."""

        return (  # type: ignore [return-value] # noqa : F821
            self._action.load_master_widget()  # type: ignore [return-value] # noqa : F821
            if self._action
            else None
        )

    def parent(self) -> "QtWidgets.QWidget":
        """Return parent widget."""

        return self.form

    def _class_init(self) -> None:
        """Initialize the class."""
        pass

    def set_proxy_parent(self, proxy_parent: "proxy.DelayedObjectProxyLoader") -> None:
        """Set proxy parent for future deletion."""

        self._my_proxy = proxy_parent

    def closeEvent(self, event: "QtCore.QEvent") -> None:
        """Close event."""

        if self._action is None:
            self._action = getattr(self.parent(), "_action")

        self.closed.emit()
        event.accept()  # let the window close

        if self._action is not None:
            LOGGER.debug("closeEvent para accion %r", self._action._name)
            self._action.clear_widget(self)

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

        form = self.form
        if child_name == super().objectName():
            return form
        elif form is not None:
            ret = form.child(child_name)
            if ret is None:
                ret = getattr(form, child_name, None)

        if ret is None:
            raise Exception("control %s not found!, form: %s" % (child_name, form))

        return ret

    def eval(self, text: str) -> Any:
        """Return eval value."""

        return eval(text)

    def cursor(self) -> "flsqlcursor.FLSqlCursor":  # type: ignore [override] # noqa F821
        """Return cursor associated."""

        if self._action is None:
            raise Exception("action is empty!!")

        return cast(flsqlcursor.FLSqlCursor, self._action.cursor())

    def __getattr__(self, name: str) -> "QtWidgets.QWidget":
        """Guess if attribute can be found in other related objects."""

        ret_ = None
        if name == "init":
            return None  # type: ignore [return-value] # noqa F821

        if self._action is not None:

            if self._action._table:
                cursor = self.cursor()
                ret_ = getattr(cursor, name, None)

            if ret_ is None:
                ret_ = getattr(self._action, name, None)

        if ret_ is None:
            if name == "form":
                ret_ = self._get_form()
            else:
                form_ = self._get_form()
                if not isinstance(form_, FormDBWidget):  # type: ignore [unreachable] # noqa: F821
                    ret_ = getattr(form_, name, None)

        if ret_ is None and not TYPE_CHECKING:

            ret_ = getattr(application.PROJECT.aq_app, name, None)
            if ret_ is not None:
                LOGGER.warning(
                    "FormDBWidget: Coearcing attribute %r from aqApp (should be avoided)" % name
                )

        if ret_ is None:
            raise AttributeError("FormDBWidget: Attribute does not exist: %r" % name)

        return ret_

    def _set_form(self, form: Optional[Union["flformdb.FLFormDB", "FormDBWidget"]]) -> None:
        """Set form widget."""
        self._form = form

    def _get_form(self) -> Optional[Union["flformdb.FLFormDB", "FormDBWidget"]]:
        """Return form widget."""

        if self._form in [self, None]:
            if self._action is not None:
                if self is self._action._master_widget and self._action._master_form:
                    self._action.load_master_form()

                elif self is self._action._record_widget and self._action._record_form:
                    self._action.load_record_form()

        # setattr(
        #    sys.modules[self.__module__], "form", self._form
        # )  # Con esto seteamos el global form en el módulo

        return self._form if self._form is not self else None

    def get_module(self) -> "types.ModuleType":
        """Return module."""
        LOGGER.warning(
            "This method is deprecated. Plese replace with qsa._super('class_name', object):\n\t %s",
            traceback.format_stack(limit=2),
        )
        return sys.modules[self.__module__]

    form = property(_get_form, _set_form)
    module = property(get_module)
