"""
XMLAction module.
"""


from pineboolib.core.utils import logging, struct, utils_base

from . import load_script
from . import actions_slots

from typing import Optional, Union, TYPE_CHECKING

from pineboolib import application

if TYPE_CHECKING:
    from . import moduleactions  # noqa : F401
    from pineboolib.interfaces import isqlcursor  # noqa: F401
    from xml.etree import ElementTree as ET
    from pineboolib.q3widgets import formdbwidget

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

        # print("*****************************************")
        # print("Name          :", self._name)
        # print("Alias         :", self._alias)
        # print("Description   :", self._description)
        # print("Caption       :", self._caption)
        # print("Master Form   :", self._master_form)
        # print("Master Script :", self._master_script)
        # print("Record Form   :", self._record_form)
        # print("Record Script :", self._record_script)
        # print("Table         :", self._table)
        # print("Module        :", self._mod)

    def load(self) -> "formdbwidget.FormDBWidget":
        """
        Load master form.
        """
        loaded = False
        if self._master_widget is not None:
            loaded = (
                self._master_widget.form._loaded if self._master_widget.form is not None else False
            )

        # LOGGER.warning("PROCESSING %s (%s) loaded: %s", self._name, self._master_widget, loaded)
        if not loaded:
            if self._master_widget is not None:
                if self._master_widget is not None:
                    self._master_widget.doCleanUp()
                del self._master_widget

            # LOGGER.info("init: Action: %s", self._name)

            script_name = self._master_script if self._table else self._name

            if not script_name:
                scrip_name = self._name

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

            LOGGER.warning(
                "End of action load %s (iface:%s ; form_widget:%s)",
                self._name,
                getattr(widget, "iface", None),
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

        LOGGER.warning(
            "PROCESSING 1 %s loaded: %s name: %s", self._record_widget, loaded, self._name
        )
        if not loaded:
            if self._record_widget is not None:
                if self._record_widget is not None:
                    self._record_widget.doCleanUp()
                del self._record_widget

            LOGGER.info("init: Action: %s", self._name)
            script = load_script.load_script(self._record_script, self)
            self._record_widget = script.form
            LOGGER.warning("PROCESSING 2 %s loaded: %s", self._record_widget, loaded)
            if self._record_widget is None:
                raise Exception("After loading script, no master_widget was loaded")

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

            LOGGER.warning(
                "End of action load %s (iface:%s ; form_widget:%s)",
                self._name,
                getattr(widget, "iface", None),
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
        actions_slots.open_default_form(self)

    def openDefaultFormRecord(self, cursor: "isqlcursor.ISqlCursor", wait: bool = True) -> None:
        """
        Open FLFormRecord specified on defaults.

        @param cursor. Cursor a usar por el FLFormRecordDB
        """
        actions_slots.open_default_form_record(self, cursor, wait)

    def formRecordWidget(self) -> None:
        """
        Return formrecord widget.

        This is needed because sometimes there isn't a FLFormRecordDB initialized yet.
        @return wigdet del formRecord.
        """

        return actions_slots.form_record_widget(self)

    def execMainScript(self, name: str) -> None:

        """
        Execute function for main action.
        """

        actions_slots.exec_main_script(name)

    def execDefaultScript(self):

        """
        Execute script specified on default.
        """

        actions_slots.exec_default_script(self)

    def unknownSlot() -> None:
        """Log error for actions with unknown slots or scripts."""

        actions_slots.unknown_slot(self)
