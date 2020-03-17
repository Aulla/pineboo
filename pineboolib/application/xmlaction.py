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

        if cursor is not self._cursor:
            del self._cursor
            self._cursor = cursor

    def cursor(self) -> Optional["isqlcursor.ISqlCursor"]:
        """Return xmlAction cursor."""
        if not self._cursor and self._table:
            self._cursor = pnsqlcursor.PNSqlCursor(self._name)

        return self._cursor

    def load(self) -> "formdbwidget.FormDBWidget":
        """
        Load master form.
        """

        loaded = False
        if self._master_widget is not None:
            loaded = (
                self._master_widget.form._loaded if self._master_widget.form is not None else False
            )

        if not loaded:
            # print("RECARGANDO MAESTRO", self._name)
            if self._master_widget is not None:
                self._master_widget.doCleanUp()
                # del self._master_widget

            # LOGGER.info("init: Action: %s", self._name)

            script_name = self._name
            if self._table:
                script_name = self._master_script

            script = load_script.load_script(script_name, self)

            self._master_widget = script.form
            # LOGGER.warning("PROCESSING 2 %s loaded: %s", self._master_widget, loaded)
            if self._master_widget is None:
                raise Exception("After loading script, no master_widget was loaded")

            if not utils_base.is_library():
                # LOGGER.warning("Loading action %s (createForm). . . ", self._name)
                self._master_widget.form = application.PROJECT.conn_manager.managerModules().createForm(
                    action=self
                )
                # LOGGER.warning(
                #    "PROCESSING 3 %s , %s loaded: %s",
                #    self._master_widget,
                #    self._master_widget.form,
                #    loaded,
                # )
                if self._master_widget.form is None:
                    raise Exception("After createForm, no form was loaded")

                self._master_widget.form._loaded = True

            else:
                self._master_widget.form = None

            # LOGGER.warning("PROCESSING 2 %s (%s) loaded: %s", self._master_widget, script, loaded)
            widget = self._master_widget

            LOGGER.debug(
                "End of action load %s (master_widget:%s ; master_form:%s)",
                self._name,
                widget,
                getattr(widget, "form", None),
            )

        result = self._master_widget

        if result is None:
            raise Exception("no master_widget was loaded")

        return result

    def load_record(
        self, cursor: Optional["isqlcursor.ISqlCursor"] = None
    ) -> "formdbwidget.FormDBWidget":
        """
        Load FLFormRecordDB by default.

        @param cursor. Asigna un cursor al FLFormRecord
        @return widget con form inicializado
        """
        loaded = False

        if self._record_widget is not None:
            loaded = (
                self._record_widget.form._loaded if self._record_widget.form is not None else False
            )

        if not loaded:
            # print("RECARGANDO REGISTRO", self._name)
            if self._record_widget is not None:
                self._record_widget.doCleanUp()
                del self._record_widget
                self._record_widget = None

            LOGGER.info("init: Action: %s", self._name)
            script = load_script.load_script(self._record_script, self)
            self._record_widget = script.form

            if self._record_widget is None:
                raise Exception("After loading script, no record_widget was loaded")

            if not utils_base.is_library() and self._record_form:
                LOGGER.info("Loading action %s (createFormRecord). . . ", self._name)
                self._record_widget.form = application.PROJECT.conn_manager.managerModules().createFormRecord(
                    action=self, parent_or_cursor=cursor
                )

                if self._record_widget.form is None:
                    raise Exception("After createFormRecord, no form was loaded")

                self._record_widget._loaded = True
            else:
                self._record_widget.form = None

            if self._record_widget is None:
                raise Exception("No record_widget was loaded")

            if cursor is not None and self._record_widget.form is not None:
                self._record_widget.form.setCursor(cursor)

            widget = self._record_widget

            LOGGER.debug(
                "End of action load %s (record_widget:%s ; record_form:%s)",
                self._name,
                widget,
                getattr(widget, "form", None),
            )

        result = self._record_widget
        if result is None:
            raise Exception("no record_widget was loaded")

        return result

    def openDefaultForm(self) -> None:
        """
        Open Main FLForm specified on defaults.
        """
        LOGGER.info("Opening default form for Action %s", self._name)
        self.load()
        if self._master_widget is not None and self._master_widget.form is not None:
            self._master_widget.form.show()

    def openDefaultFormRecord(self, cursor: "isqlcursor.ISqlCursor", wait: bool = True) -> None:
        """
        Open FLFormRecord specified on defaults.

        @param cursor. Cursor a usar por el FLFormRecordDB
        """

        if self._record_widget is not None:
            form = getattr(self._record_widget, "form", None)
            if form is not None and form._loaded and form.showed:
                QtWidgets.QMessageBox.information(
                    QtWidgets.QApplication.activeWindow(),
                    "Aviso",
                    "Ya hay abierto un formulario de edición de resgistro para esta tabla.\n"
                    "No se abrirán mas para evitar ciclos repetitivos de edición de registros.",
                    QtWidgets.QMessageBox.Yes,
                )
                return

        LOGGER.info("Opening default formRecord for Action %s", self._name)
        self.load_record(cursor)

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

        if self._record_widget is None or not self._record_widget._loaded:
            ret = self.load_record()
        else:
            ret = self._record_widget

        return ret

    def execMainScript(self, action_name: str) -> None:
        """
        Execute function for main action.
        """

        application.PROJECT.call("%s.main" % action_name, [], None, False)

    def execDefaultScript(self):
        """
        Execute script specified on default.
        """

        if self._record_widget is None:
            LOGGER.info("Executing default script for Action %s", self._name)
            script = load_script.load_script(self._master_script, self)
            self._record_widget = script.form

        if self._record_widget is None:
            raise Exception("Unexpected: No form loaded")

        main = None
        iface = getattr(self._record_widget, "iface", None)

        if iface is not None:
            main = getattr(iface, "main", None)

        if main is None:
            main = getattr(self._record_widget, "main", None)

        if main is None:
            raise Exception("main function not found!")
        else:
            main()

    def unknownSlot(self) -> None:
        """Log error for actions with unknown slots or scripts."""

        LOGGER.error("Executing unknown script for Action %s", self._name)
