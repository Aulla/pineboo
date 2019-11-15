"""
XMLAction module.
"""
from pineboolib.core.utils import logging


from pineboolib.core.utils.struct import ActionStruct
from . import load_script

from pineboolib.fllegacy import flformdb
from pineboolib.fllegacy import flformrecorddb

from typing import Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.fllegacy.flaction import FLAction  # noqa: F401

    from .moduleactions import ModuleActions  # noqa: F401
    from .database.pnsqlcursor import PNSqlCursor  # noqa: F401
    from .projectmodule import Project


class XMLAction(ActionStruct):
    """
    Information related to actions specified in XML modules.
    """

    logger = logging.getLogger("main.XMLAction")
    mod: Optional["ModuleActions"]
    alias: str

    def __init__(self, *args, project: "Project", name: Optional[str] = None, **kwargs) -> None:
        """
        Constructor.
        """
        super(XMLAction, self).__init__(*args, **kwargs)
        self.mod = None
        self.project = project
        if not self.project:
            raise ValueError("XMLActions must belong to a project")
        self.form = self._v("form")
        self.name = name or self._rv("name")  # Mandatory
        self.description = self._v("description")
        self.caption = self._v("caption")
        alias = self._v("alias")
        if alias:
            self.alias = alias
        self.scriptform = self._v("scriptform")
        self.table = self._v("table")
        self.mainform = self._v("mainform")
        self.mainscript = self._v("mainscript")
        self.formrecord = self._v("formrecord")
        self.scriptformrecord = self._v("scriptformrecord")
        self.mainform_widget: Optional[flformdb.FLFormDB] = None
        self.formrecord_widget: Optional[flformrecorddb.FLFormRecordDB] = None
        self._loaded = False

    def loadRecord(self, cursor: Optional["PNSqlCursor"]) -> "flformrecorddb.FLFormRecordDB":
        """
        Load FLFormRecordDB by default.

        @param cursor. Asigna un cursor al FLFormRecord
        @return widget con form inicializado
        """
        self._loaded = getattr(self.formrecord_widget, "_loaded", False)
        if not self._loaded:
            if self.formrecord_widget and getattr(self.formrecord_widget, "widget", None):
                self.formrecord_widget.widget.doCleanUp()
                # self.formrecord_widget.widget = None

            self.logger.debug("Loading record action %s . . . ", self.name)
            if self.project.DGI.useDesktop():
                # FIXME: looks like code duplication. Bet both sides of the IF do the same.
                self.formrecord_widget = cast(
                    flformrecorddb.FLFormRecordDB,
                    self.project.conn_manager.managerModules().createFormRecord(
                        action=self, parent_or_cursor=cursor
                    ),
                )
            else:
                # self.script = getattr(self, "script", None)
                # if isinstance(self.script, str) or self.script is None:
                script = load_script.load_script(self.scriptformrecord, self)
                self.formrecord_widget = script.form
                if self.formrecord_widget is None:
                    raise Exception("After loading script, no form was loaded")
                self.formrecord_widget.widget = self.formrecord_widget
                self.formrecord_widget.iface = self.formrecord_widget.widget.iface
                self.formrecord_widget._loaded = True
            # self.formrecord_widget.setWindowModality(Qt.ApplicationModal)
            self.logger.debug(
                "End of record action load %s (iface:%s ; widget:%s)",
                self.name,
                getattr(self.formrecord_widget, "iface", None),
                getattr(self.formrecord_widget, "widget", None),
            )
        if self.formrecord_widget is None:
            raise Exception("Unexpected: No formrecord loaded")

        if cursor:
            self.formrecord_widget.setCursor(cursor)

        return self.formrecord_widget

    def load(self) -> "flformdb.FLFormDB":
        """
        Load master form.
        """
        self._loaded = getattr(self.mainform_widget, "_loaded", False)
        if not self._loaded:
            if self.mainform_widget is not None and getattr(self.mainform_widget, "widget", None):
                self.mainform_widget.widget.doCleanUp()

            if self.project.DGI.useDesktop():
                self.logger.info("Loading action %s (createForm). . . ", self.name)
                self.mainform_widget = cast(
                    flformdb.FLFormDB,
                    self.project.conn_manager.managerModules().createForm(action=self),
                )
            else:
                self.logger.info(
                    "Loading action %s (load_script %s). . . ", self.name, self.scriptform
                )
                script = load_script.load_script(self.scriptform, self)
                self.mainform_widget = script.form  # FormDBWidget FIXME: Add interface for types
                if self.mainform_widget is None:
                    raise Exception("After loading script, no form was loaded")
                self.mainform_widget.widget = self.mainform_widget
                self.mainform_widget.iface = self.mainform_widget.widget.iface
                self.mainform_widget._loaded = True

            self.logger.debug(
                "End of action load %s (iface:%s ; widget:%s)",
                self.name,
                getattr(self.mainform_widget, "iface", None),
                getattr(self.mainform_widget, "widget", None),
            )
        if self.mainform_widget is None:
            raise Exception("Unexpected: No form loaded")

        return self.mainform_widget

    def execMainScript(self, name: str) -> None:
        """
        Execute function for main action.
        """
        a = self.project.conn_manager.manager().action(name)
        if not a:
            self.logger.warning("No existe la acción %s", name)
            return
        self.project.call("%s.main" % a.name(), [], None, False)

    def formRecordWidget(self) -> "flformrecorddb.FLFormRecordDB":
        """
        Return formrecord widget.

        This is needed because sometimes there isn't a FLFormRecordDB initialized yet.
        @return wigdet del formRecord.
        """
        if not getattr(self.formrecord_widget, "_loaded", None):
            self.loadRecord(None)

        if self.formrecord_widget is None:
            raise Exception("Unexpected: No form loaded")
        return self.formrecord_widget

    # FIXME: cursor is FLSqlCursor but should be something core, not "FL". Also, an interface
    def openDefaultFormRecord(self, cursor: "PNSqlCursor", wait: bool = True) -> None:
        """
        Open FLFormRecord specified on defaults.

        @param cursor. Cursor a usar por el FLFormRecordDB
        """
        if self.formrecord_widget is not None:
            if getattr(self.formrecord_widget, "_loaded", False):
                if self.formrecord_widget.showed:
                    from PyQt5 import QtWidgets

                    QtWidgets.QMessageBox.information(
                        QtWidgets.QApplication.activeWindow(),
                        "Aviso",
                        "Ya hay abierto un formulario de edición de resgistro para esta tabla.\n"
                        "No se abrirán mas para evitar ciclos repetitivos de edición de registros.",
                        QtWidgets.QMessageBox.Yes,
                    )
                    return

        self.logger.info("Opening default formRecord for Action %s", self.name)
        w = self.loadRecord(cursor)
        # w.init()
        if w:
            if wait:
                w.show_and_wait()
            else:
                w.show()

    def openDefaultForm(self) -> None:
        """
        Open Main FLForm specified on defaults.
        """
        self.logger.info("Opening default form for Action %s", self.name)
        w = self.load()

        if w:
            if self.project.DGI.localDesktop():
                w.show()

    def execDefaultScript(self) -> None:
        """
        Execute script specified on default.
        """
        self.logger.info("Executing default script for Action %s", self.name)
        script = load_script.load_script(self.scriptform, self)

        self.mainform_widget = script.form
        if self.mainform_widget is None:
            raise Exception("Unexpected: No form loaded")

        main = getattr(self.mainform_widget.widget, "iface", self.mainform_widget.widget)
        main.main()
        # if self.mainform_widget.widget.iface is not None:
        #    self.mainform_widget.iface.main()
        # else:
        #    self.mainform_widget.widget.main()

    def unknownSlot(self) -> None:
        """Log error for actions with unknown slots or scripts."""
        self.logger.error("Executing unknown script for Action %s", self.name)
