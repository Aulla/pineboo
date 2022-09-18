"""
XMLAction module.
"""


from pineboolib.core.utils import struct, utils_base
from pineboolib.core import garbage_collector

from pineboolib.application.database import pnsqlcursor
from pineboolib import logging, application

from . import load_script

import threading
from typing import Optional, Union, Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from . import moduleactions  # noqa : F401 # pragma: no cover
    from pineboolib.interfaces import isqlcursor  # noqa: F401 # pragma: no cover
    from xml.etree import ElementTree as ET  # noqa: F401 # pragma: no cover
    from pineboolib.qsa import formdbwidget  # noqa: F401 # pragma: no cover

LOGGER = logging.get_logger(__name__)


class XMLAction(struct.ActionStruct):
    """
    Information related to actions specified in XML modules.
    """

    _mod: Optional["moduleactions.ModuleActions"]

    __master_widget: Dict[int, "formdbwidget.FormDBWidget"]
    __record_widget: Dict[int, "formdbwidget.FormDBWidget"]

    __cursor: Dict[int, "isqlcursor.ISqlCursor"]

    def __init__(
        self, module: "moduleactions.ModuleActions", action_xml_or_str: Union["ET.Element", str]
    ) -> None:
        """
        Initialize.
        """
        if isinstance(action_xml_or_str, str):
            super().__init__()
            self._name = action_xml_or_str
        else:
            super().__init__(action_xml_or_str)
            self._name = self._v("name") or ""

        self._mod = module
        self._alias = self._v("alias") or ""
        self._description = self._v("description") or ""
        self._caption = self._v("caption") or self._description
        self._master_form = self._v("form") or ""
        self._master_script = self._v("scriptform") or ""
        self._record_form = self._v("formrecord") or ""
        self._record_script = self._v("scriptformrecord") or ""
        self._table = self._v("table") or ""
        self._class_script = self._v("class") or ""
        self._class_orm = self._v("model") or ""

        self.__master_widget = {}
        self.__record_widget = {}

        self.__cursor = {}

    def setCursor(self, cursor: Optional["isqlcursor.ISqlCursor"] = None):
        """Set xmlAction cursor."""
        # LOGGER.warning(
        #    "Seteando cursor para %s %s", self._name, self._master_widget, stack_info=True
        # )
        id_thread = threading.current_thread().ident
        if cursor is not self._cursor:
            del self.__cursor[id_thread]  # type: ignore [index, arg-type] # noqa: F821
            self.__cursor[id_thread] = cursor  # type: ignore [assignment, index] # noqa: F821

    def cursor(self) -> Optional["isqlcursor.ISqlCursor"]:
        """Return xmlAction cursor."""
        if not self._cursor and self._table:

            # LOGGER.warning("Creando cursor para %s %s", self._name, self._master_widget)
            self._cursor = pnsqlcursor.PNSqlCursor(self._name)

        return self._cursor

    def load_widget(self, script_name: str) -> "formdbwidget.FormDBWidget":
        """Return widget."""

        return load_script.load_script(script_name, self)

    def clear_widget(self, widget: Optional["formdbwidget.FormDBWidget"]) -> None:
        """Clear old widget."""

        if widget is not None:
            id_thread = threading.current_thread().ident or 0

            widget.clear_connections()
            proxy_parent = getattr(widget, "_my_proxy", None)
            if proxy_parent is not None and id_thread in proxy_parent.loaded_obj.keys():
                del proxy_parent.loaded_obj[id_thread]

            if widget is self._record_widget:
                del self.__record_widget[id_thread]
            elif widget is self._master_widget:
                del self.__master_widget[id_thread]

            # from PyQt5 import QtCore

            if widget._form is not None:
                # if application.PROJECT.main_window:
                #    # if application.PROJECT.main_window.main_widget is widget._form:
                #    for child in application.PROJECT.main_window.findChildren(QtCore.QObject):
                #        if child is widget._form:
                #            del child

                # obj_form = widget._form
                # Cerrando hijos ...

                # for child in widget._form.findChildren(QtCore.QObject):
                #    if hasattr(child, "_loaded"):
                #        child._top_widget = None
                #    if hasattr(child, "fltable_iface"):
                #        child.fltable_iface = None
                self.clear_form(widget)
                # print(widget._form)

                # garbage_collector.check_delete(obj_form, "widget.form")

            if hasattr(widget, "iface"):
                if hasattr(widget.iface, "ctx"):
                    obj_ctx = widget.iface.ctx  # type: ignore [attr-defined] # noqa: F821
                    widget.iface.ctx.deleteLater()  # type: ignore [attr-defined] # noqa: F821
                    widget.iface.ctx = None  # type: ignore [attr-defined] # noqa: F821
                    garbage_collector.check_delete(obj_ctx, "widget.iface.ctx")
                obj_iface = widget.iface
                del widget.iface
                widget.iface = None
                garbage_collector.check_delete(obj_iface, "widget.iface")

            garbage_collector.check_delete(widget, "widget")
            # del widget

    def clear_form(self, widget: "formdbwidget.FormDBWidget") -> bool:
        """Delete form associated ."""
        if widget._form is not None:
            widget._form.setParent(None)  # type: ignore [call-overload] # noqa: F821
            widget._form.deleteLater()
            widget._form = None

        return True

    def is_form_loaded(self, widget: Optional["formdbwidget.FormDBWidget"]) -> bool:
        """Return if widget.form is loaded."""

        form = getattr(widget, "_form", None)
        return getattr(form, "_loaded", False)

    def load_class(self):
        """Load and return class."""
        if self._class_script:
            return load_script.load_class(self._class_script)

    def load_master_widget(self) -> "formdbwidget.FormDBWidget":
        """
        Load master form.
        """
        if not self.is_form_loaded(self._master_widget):
            if self._table or (not self._table and self._master_widget is None):
                self._master_widget = self.load_widget(
                    self._master_script if self._table else self._name
                )

        if self._master_widget is None:
            raise Exception("After load_master_widget, no widget was loaded")

        return self._master_widget

    def load_record_widget(self) -> "formdbwidget.FormDBWidget":
        """
        Load FLFormRecordDB by default.

        """
        if self._record_widget is None:
            self._record_widget = self.load_widget(self._record_script)
        elif self._record_widget._form is not None and not self.is_form_loaded(self._record_widget):
            self.clear_widget(self._record_widget)

            self._record_widget = self.load_widget(self._record_script)

        if self._record_widget is None:
            raise Exception("After load_record_widget, no widget was loaded")

        return self._record_widget

    def load_master_form(self) -> None:
        """Load master_widget.form."""

        if not self.is_form_loaded(self._master_widget):
            if self._master_widget is None:
                self._master_widget = self.load_master_widget()

            form = None
            if not utils_base.is_library():
                form = application.PROJECT.conn_manager.managerModules().createForm(action=self)
                if form is None:
                    raise Exception("After createForm, no form was loaded")
                else:
                    form._loaded = True

            self._master_widget._form = form  # type: ignore [assignment] # noqa: F821

            if form is not None:
                preload_main_filter = getattr(form.iface, "preloadMainFilter", None)
                if preload_main_filter is not None:
                    value = preload_main_filter()
                    if value is not None and form.cursor_:
                        form.cursor_.setMainFilter(value, False)

    def load_record_form(self, cursor: Optional["isqlcursor.ISqlCursor"] = None) -> None:
        """Load record_widget.form."""

        if not self.is_form_loaded(self._record_widget):
            if self._record_widget is None:
                self._record_widget = self.load_record_widget()

            form = None
            if not utils_base.is_library():
                form = application.PROJECT.conn_manager.managerModules().createFormRecord(
                    action=self, parent_or_cursor=cursor
                )

                if form is None:
                    raise Exception("After createFormRecord, no form was loaded")
                else:
                    form._loaded = True

            if cursor is not None:
                if form is not None:
                    form.setCursor(cursor)
                else:
                    LOGGER.warning(
                        "add cursor?. the form does not exist!!. action: %s record_form: %s",
                        self._name,
                        self._record_form,
                    )

            self.clear_form(self._record_widget)
            self._record_widget._form = form  # type: ignore [assignment] # noqa: F821

    def openDefaultForm(self) -> None:
        """
        Open Main FLForm specified on defaults.
        """
        LOGGER.info("Opening default form for Action %s", self._name)
        self.load_master_form()
        if self._master_widget is not None and self._master_widget.form is not None:
            self._master_widget.form.show()

    def openDefaultFormRecord(self, cursor: "isqlcursor.ISqlCursor", wait: bool = True) -> None:
        """
        Open FLFormRecord specified on defaults.

        @param cursor. Cursor a usar por el FLFormRecordDB
        """

        if self.is_form_loaded(self._record_widget):
            if self._record_widget is not None and self._record_widget.form is not None:
                if self._record_widget.form._showed:
                    msg = "Ya hay abierto un formulario de edición de registro para esta tabla.\n"
                    "No se abrirán mas para evitar ciclos repetitivos de edición de registros."
                    application.PROJECT.message_manager().send(
                        "msgBoxInfo", None, [msg, None, "Aviso"]
                    )

            LOGGER.warning("formRecord%s is already loaded!", self._record_form)
            return

        self.load_record_form(cursor)

        if self._record_widget is not None and self._record_widget.form is not None:
            if wait:
                self._record_widget.form.show_and_wait()
            else:
                self._record_widget.form.show()

    def formRecordWidget(self) -> "formdbwidget.FormDBWidget":
        """
        Return formrecord widget.

        This is needed because sometimes there isn't a FLFormRecordDB initialized yet.
        @return wigdet del formRecord.
        """

        return self.load_record_widget()

    def execMainScript(self, action_name: str) -> None:
        """
        Execute function for main action.
        """
        application.PROJECT.call("form%s.main" % action_name, [], None, True)

    def execDefaultScript(self):
        """
        Execute script specified on default.
        """
        widget = self.load_master_widget()

        base_function = getattr(widget, "iface", widget)

        main = getattr(base_function, "main", None)
        if main is None:
            raise Exception("main function not found!")
        else:
            main()

    def unknownSlot(self) -> None:
        """Log error for actions with unknown slots or scripts."""

        LOGGER.error("Executing unknown script for Action %s", self._name)

    def get_master_widget(self) -> "formdbwidget.FormDBWidget":
        """Return master widget."""

        self.thread_cleaner()

        id_thread = threading.current_thread().ident
        if id_thread not in self.__master_widget.keys():
            self.__master_widget[id_thread] = None  # type: ignore [assignment, index] # noqa: F821

        return self.__master_widget[id_thread]  # type: ignore [index] # noqa: F821

    def set_master_widget(self, widget: Optional["formdbwidget.FormDBWidget"] = None) -> None:
        """Set master widget."""

        id_thread = threading.current_thread().ident
        self.__master_widget[id_thread] = widget  # type: ignore [assignment, index] # noqa: F821

    def get_record_widget(self) -> "formdbwidget.FormDBWidget":
        """Return record widget."""

        self.thread_cleaner()

        id_thread = threading.current_thread().ident
        if id_thread not in self.__record_widget.keys():
            self.__record_widget[id_thread] = None  # type: ignore [assignment, index] # noqa: F821

        return self.__record_widget[id_thread]  # type: ignore [index] # noqa: F821

    def set_record_widget(self, widget: Optional["formdbwidget.FormDBWidget"] = None) -> None:
        """Set record widget."""

        id_thread = threading.current_thread().ident
        self.__record_widget[id_thread] = widget  # type: ignore [assignment, index] # noqa: F821

    def get_action_cursor(self) -> Optional["isqlcursor.ISqlCursor"]:
        """Return action cursor."""

        self.thread_cleaner()

        id_thread = threading.current_thread().ident
        if id_thread not in self.__cursor.keys():
            return None

        return self.__cursor[id_thread]  # type: ignore [index] # noqa: F821

    def set_action_cursor(self, cursor: "isqlcursor.ISqlCursor") -> None:
        """Set action cursor."""

        id_thread = threading.current_thread().ident
        self.__cursor[id_thread] = cursor  # type: ignore [index] # noqa: F821

    def thread_cleaner(self) -> None:
        """Clean unused threads."""

        # limpieza
        threads_ids: List[Optional[int]] = [thread.ident for thread in threading.enumerate()]
        obj_list: List[Dict[int, Any]] = [self.__cursor, self.__master_widget, self.__record_widget]
        for obj_ in obj_list:
            for id_thread in list(obj_.keys()):  # type: ignore [attr-defined] # noqa: F821
                if obj_[id_thread] is not None:
                    if id_thread not in threads_ids:
                        obj_to_delete = obj_[id_thread]
                        obj_[id_thread] = None
                        del obj_[id_thread]
                        garbage_collector.check_delete(obj_to_delete, self._name)

    _master_widget = property(get_master_widget, set_master_widget)
    _record_widget = property(get_record_widget, set_record_widget)
    _cursor = property(get_action_cursor, set_action_cursor)
