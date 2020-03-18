"""
XMLAction module.
"""
from PyQt5 import QtWidgets

from pineboolib.core.utils import logging, struct, utils_base

from . import load_script

from typing import Optional, Union, TYPE_CHECKING

from pineboolib import application
from pineboolib.application.database import pnsqlcursor

if TYPE_CHECKING:
    from . import moduleactions  # noqa : F401
    from pineboolib.interfaces import isqlcursor  # noqa: F401
    from xml.etree import ElementTree as ET  # noqa: F401
    from pineboolib.q3widgets import formdbwidget  # noqa: F401

LOGGER = logging.get_logger(__name__)


class XMLAction(struct.ActionStruct):
    """
    Information related to actions specified in XML modules.
    """

    _mod: Optional["moduleactions.ModuleActions"]

    _master_widget: Optional["formdbwidget.FormDBWidget"]
    _record_widget: Optional["formdbwidget.FormDBWidget"]

    _cursor: Optional["isqlcursor.ISqlCursor"]

    def __init__(
        self, module: "moduleactions.ModuleActions", action_xml_or_str: Union["ET.Element", str]
    ) -> None:
        """
        Constructor.
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

        self._master_widget = None
        self._record_widget = None

        self._cursor = None

    def setCursor(self, cursor: Optional["isqlcursor.ISqlCursor"] = None):
        """Set xmlAction cursor."""
        # LOGGER.warning(
        #    "Seteando cursor para %s %s", self._name, self._master_widget, stack_info=True
        # )
        if cursor is not self._cursor:
            del self._cursor
            self._cursor = cursor

    def cursor(self) -> Optional["isqlcursor.ISqlCursor"]:
        """Return xmlAction cursor."""
        if not self._cursor and self._table:
            # LOGGER.warning("Creando cursor para %s %s", self._name, self._master_widget)
            self._cursor = pnsqlcursor.PNSqlCursor(self._name)

        return self._cursor

    def load_widget(self, script_name: str) -> "formdbwidget.FormDBWidget":
        """Return widget."""

        script = load_script.load_script(script_name, self)
        widget = script.form
        if widget is None:
            raise Exception(
                "After loading script, no widget was loaded. action: %s script: %s"
                % (self._name, script_name)
            )

        return widget

    def clear_widget(self, widget: Optional["formdbwidget.FormDBWidget"]) -> None:
        """Clear old widget."""

        if widget is not None:
            widget.doCleanUp()

            if widget is self._master_widget:
                del self._master_widget
                self._master_widget = None
                del widget
            elif widget is self._record_widget:
                del self._record_widget
                self._record_widget = None
                del widget
            # else:
            #    raise Exception("Unknown widget to delete! : %s" % widget)

    def is_form_loaded(self, widget: Optional["formdbwidget.FormDBWidget"]) -> bool:
        """Return if widget.form is loaded."""

        form = getattr(widget, "_form", None)
        return getattr(form, "_loaded", False)

    def load_master_widget(self) -> "formdbwidget.FormDBWidget":
        """
        Load master form.
        """
        if not self.is_form_loaded(self._master_widget):
            self.clear_widget(self._master_widget)

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

        if not self.is_form_loaded(self._record_widget):
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
                if self._record_widget.form.showed:

                    QtWidgets.QMessageBox.information(
                        QtWidgets.QApplication.activeWindow(),
                        "Aviso",
                        "Ya hay abierto un formulario de edición de resgistro para esta tabla.\n"
                        "No se abrirán mas para evitar ciclos repetitivos de edición de registros.",
                        QtWidgets.QMessageBox.Yes,
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

        application.PROJECT.call("%s.main" % action_name, [], None, False)

    def execDefaultScript(self):
        """
        Execute script specified on default.
        """
        widget = self.load_master_widget()

        main = None
        iface = getattr(widget, "iface", None)
        if iface is not None:
            main = getattr(iface, "main", None)
        else:
            main = getattr(widget, "main", None)

        if main is None:
            raise Exception("main function not found!")
        else:
            main()

    def unknownSlot(self) -> None:
        """Log error for actions with unknown slots or scripts."""

        LOGGER.error("Executing unknown script for Action %s", self._name)
