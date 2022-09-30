# -*- coding: utf-8 -*-
"""PNApplication Module."""


from PyQt6 import QtCore, QtWidgets  # type: ignore[import]

from pineboolib.core import decorators, settings
from pineboolib.core.utils import logging, utils_base

from pineboolib import application
from .database import DB_SIGNALS, utils
from .qsatypes import sysbasetype
from . import qsadictmodules

import sys
from typing import Any, Optional, List, TextIO, cast, Union, Dict, TYPE_CHECKING


if TYPE_CHECKING:
    from .database import pnsqlcursor, pnsqlquery  # noqa: F401 # pragma: no cover
    from .acls import pnaccesscontrollists
    from .translator import pntranslator

    from pineboolib.interfaces import isqlcursor  # noqa: F401 # pragma: no cover
    from PyQt6 import QtXml, QtGui  # noqa: F401 # pragma: no cover
    from pineboolib.application import module as app_module  # pragma: no cover
    from pineboolib.interfaces import dgi_schema  # pragma: no cover
    from pineboolib.application.database import pnconnectionmanager  # pragma: no cover
    from pineboolib.fllegacy import flformdb  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class FLPopupWarn(QtCore.QObject):
    """FLPoppupWarn Class."""

    # FIXME: Incomplete class!
    def __init__(self, mainwindow) -> None:
        """Inicialize."""

        self._main_window = mainwindow


class PNApplication(QtCore.QObject):
    """PNApplication Class."""

    _inicializing: bool
    _destroying: bool
    _ted_output: Optional["QtWidgets.QWidget"]
    _not_exit: bool
    _multi_lang_enabled: bool
    _multi_lang_id: str
    _translator: List["pntranslator.PNTranslator"]

    container_: Optional["QtWidgets.QWidget"]  # Contenedor actual??
    form_alone_: bool
    acl_: Optional["pnaccesscontrollists.PNAccessControlLists"]

    op_check_update_: bool
    style: bool
    flLargeMode: Optional[bool]

    init_single_fl_large: bool
    show_debug_: bool
    timer_idle_: Optional["QtCore.QTimer"]
    time_user_: "QtCore.QTimer"
    script_entry_function_: str
    _event_loop: Optional["QtCore.QEventLoop"]
    window_menu: Optional["QtWidgets.QMenu"] = None
    modules_menu: Optional["QtWidgets.QMenu"] = None

    transactionBegin: "QtCore.pyqtSignal" = QtCore.pyqtSignal()
    transactionEnd: "QtCore.pyqtSignal" = QtCore.pyqtSignal()
    transactionRollback: "QtCore.pyqtSignal" = QtCore.pyqtSignal()

    def __init__(self) -> None:
        """Create new FLApplication."""
        super().__init__()

        # self.project_ = None
        self.wb_ = None

        self._translator = []

        self.form_alone_ = False
        self._not_exit = False
        self.timer_idle_ = None
        # self.popup_warn_ = None
        self._inicializing = False
        self._destroying = False
        # self.fl_factory_ = None
        self.op_check_update_ = False
        self.window_menu = None
        DB_SIGNALS.notify_begin_transaction_ = False
        DB_SIGNALS.notify_end_transaction_ = False
        DB_SIGNALS.notify_roll_back_transaction_ = False
        self._ted_output = None
        self.style = False
        self.init_single_fl_large = False
        self.show_debug_ = True  # FIXME
        self.script_entry_function_ = ""
        self.flLargeMode = None

        self.acl_ = None
        # self.fl_factory_ = FLObjectFactory() # FIXME para un futuro
        # self.time_user_ = QtCore.QDateTime.currentDateTime() # Moved to pncontrolsfacotry.SysType
        self._multi_lang_enabled = False
        self._multi_lang_id = QtCore.QLocale().name()[:2].upper()

        self.locale_system_ = QtCore.QLocale.system()
        value = 1.1
        self.comma_separator = self.locale_system_.toString(value, "f", 1)[1]
        self.setObjectName("aqApp")
        self._event_loop = None

    @property
    def event_loop(self) -> "QtCore.QEventLoop":
        """Get Eventloop, create one if it does not exist."""
        if self._event_loop is None:
            self._event_loop = QtCore.QEventLoop()
        return self._event_loop

    def eventLoop(self) -> "QtCore.QEventLoop":
        """Create main event loop."""
        return QtCore.QEventLoop()

    def toXmlReportData(self, qry: "pnsqlquery.PNSqlQuery") -> "QtXml.QDomDocument":
        """Return xml from a query."""
        from pineboolib.fllegacy import flreportengine

        rpt_ = flreportengine.FLReportEngine()
        rpt_.setReportData(qry)
        ret = rpt_.reportData()
        return ret

    @decorators.not_implemented_warn
    def checkForUpdate(self):
        """Not used in Pineboo."""
        pass

    @decorators.not_implemented_warn
    def checkForUpdateFinish(self, option):
        """Not used in pineboo."""
        pass

    @decorators.not_implemented_warn
    def initfcgi(self):
        """Init for fast cgi."""
        pass

    @decorators.not_implemented_warn
    def addObjectFactory(self, new_object_factory):
        """Add object onctructor. unused."""
        pass

    @decorators.not_implemented_warn
    def callfcgi(self, call_function, argument_list):
        """Perform fastcgi call."""
        pass

    @decorators.not_implemented_warn
    def endfcgi(self):
        """End fastcgi call signal."""
        pass

    def localeSystem(self) -> "QtCore.QLocale":
        """Return locale of the system."""
        return self.locale_system_

    @decorators.not_implemented_warn
    def openQSWorkbench(self):
        """Open debugger. Unused."""
        pass

    def setMainWidget(self, main_widget) -> None:
        """Set mainWidget."""
        if application.PROJECT.main_window is not None:
            application.PROJECT.main_window.main_widget = main_widget
            if main_widget is not None:
                application.PROJECT.app.setActiveWindow(main_widget)

    @decorators.not_implemented_warn
    def makeStyle(self, style_):
        """Apply specified style."""
        pass

    def chooseFont(self) -> None:
        """Open font selector."""

        font_ = QtWidgets.QFontDialog().getFont()  # type: ignore[misc] # noqa: F821
        if font_:
            application.PROJECT.app.setFont(font_[0])
            save_ = [font_[0].family(), font_[0].pointSize(), font_[0].weight(), font_[0].italic()]

            settings.CONFIG.set_value("application/font", save_)

    def showStyles(self) -> None:
        """Open style selector."""
        if not self.style:
            self.initStyles()
        # if self.style:
        #    self.style.exec()

    @decorators.not_implemented_warn
    def showToggleBars(self):
        """Show toggle bars."""
        pass

    def setStyle(self, style_: str) -> None:
        """Change application style."""
        settings.CONFIG.set_value("application/style", style_)
        application.PROJECT.app.setStyle(style_)  # type: ignore [misc,call-overload] # noqa: F821

    def initStyles(self) -> None:
        """Initialize styles."""

        self.style_mapper = QtCore.QSignalMapper()
        self.style_mapper.mappedString.connect(self.setStyle)  # type: ignore
        style_read = settings.CONFIG.value("application/style", None)
        if not style_read:
            style_read = "Fusion"

        style_menu = self.mainWidget().findChild(  # type: ignore [union-attr] # noqa : F821
            QtWidgets.QMenu, "style"
        )

        if style_menu:
            from PyQt6 import QtGui

            action_group = QtGui.QActionGroup(style_menu)
            for style_ in QtWidgets.QStyleFactory.keys():
                action_ = style_menu.addAction(style_)  # type: ignore [union-attr] # noqa : F821
                action_.setObjectName("style_%s" % style_)
                action_.setCheckable(True)
                if style_ == style_read:
                    action_.setChecked(True)

                action_.triggered.connect(self.style_mapper.map)
                self.style_mapper.setMapping(action_, style_)
                action_group.addAction(action_)
            action_group.setExclusive(True)

        self.style = True

    def getTabWidgetPages(self, widget_name: str, obj_name: str) -> str:
        """Get tabs."""

        action_name = ""
        widget_: Optional["flformdb.FLFormDB"]
        if widget_name.startswith("formRecord"):
            action_name = widget_name[10:]
            action_ = self.db().manager().action(action_name)
            widget_ = self.db().managerModules().createFormRecord(action_)
        elif widget_name.startswith("formSearch"):
            action_name = widget_name[10:]
            action_ = self.db().manager().action(action_name)
            widget_ = self.db().managerModules().createForm(action_)
        else:
            action_name = widget_name[4:]
            action_ = self.db().manager().action(action_name)
            widget_ = self.db().managerModules().createForm(action_)

        if widget_ is None:
            return ""  # type: ignore [unreachable]

        tab_widget = cast(QtWidgets.QTabWidget, widget_.findChild(QtWidgets.QTabWidget, obj_name))
        if tab_widget is None:
            return ""  # type: ignore [unreachable]

        tab_names: str = ""
        for number in range(tab_widget.count()):
            item: "QtWidgets.QWidget" = tab_widget.widget(number)
            tab_names += "%s/%s*" % (item.objectName(), tab_widget.tabText(number))

        return tab_names

    @decorators.not_implemented_warn
    def getWidgetList(self, widget_name: str, class_name: str) -> List:
        """Get widgets."""
        pass

    def aboutQt(self) -> None:
        """Show About QT."""
        main_widget = self.mainWidget()
        if main_widget is not None:
            QtWidgets.QMessageBox.aboutQt(main_widget)

    def aboutPineboo(self) -> None:
        """Show about Pineboo."""
        if application.PROJECT.DGI.localDesktop():
            fun_about = getattr(application.PROJECT.DGI, "about_pineboo", None)
            if fun_about is not None:
                fun_about()

    def statusHelpMsg(self, text) -> None:
        """Show help message."""

        if settings.CONFIG.value("application/isDebuggerMode", False):
            LOGGER.info("StatusHelpMsg: %s", text)

        main_widget = getattr(application.PROJECT.main_window, "main_widget", None)

        if main_widget is None:
            return

        cast(QtWidgets.QMainWindow, main_widget).statusBar().showMessage(text, 2000)

    def loadScriptsFromModule(self, id_module: str) -> None:
        """Load scripts from named module."""
        if id_module in application.PROJECT.modules.keys():
            application.PROJECT.modules[id_module].load()

    def reinit(self) -> None:
        """Cleanup and restart."""
        if self._inicializing or self._destroying:
            return

        self.stopTimerIdle()
        # self.apAppIdle()
        self._inicializing = True

        if application.PROJECT.main_window:
            main_window = application.PROJECT.main_window

            if main_window is not None:
                main_window.writeState()
                main_window.writeStateModule()
                if hasattr(main_window, "_p_work_space"):
                    main_window._p_work_space = None

        self.reinitP()

    def startTimerIdle(self) -> None:
        """Start timer."""
        if not self.timer_idle_:
            self.timer_idle_ = QtCore.QTimer()
            self.timer_idle_.timeout.connect(  # type: ignore [attr-defined] # noqa: F821
                self.aqAppIdle
            )
        else:
            self.timer_idle_.stop()

        self.timer_idle_.start(1000)

    def stopTimerIdle(self) -> None:
        """Stop timer."""
        if self.timer_idle_ and self.timer_idle_.isActive():
            self.timer_idle_.stop()

    def aqAppIdle(self) -> None:
        """Check and fix transaction level."""
        if (
            application.PROJECT.app.activeModalWidget()
            or application.PROJECT.app.activePopupWidget()
        ):
            return

        self.checkAndFixTransactionLevel("Application::aqAppIdle()")

    def checkAndFixTransactionLevel(self, ctx=None) -> None:
        """Fix transaction."""
        dict_db = self.db().dictDatabases()
        if not dict_db:
            return

        roll_back_done = False
        for item in dict_db.values():
            if item.transactionLevel() <= 0:
                continue
            roll_back_done = True
            last_active_cursor = item.lastActiveCursor()
            if last_active_cursor is not None:
                last_active_cursor.rollbackOpened(-1)
            if item.transactionLevel() <= 0:
                continue

        if not roll_back_done:
            return

        msg = self.tr(
            "Se han detectado transacciones abiertas en estado inconsistente.\n"
            "Esto puede suceder por un error en la conexión o en la ejecución\n"
            "de algún proceso de la aplicación.\n"
            "Para mantener la consistencia de los datos se han deshecho las\n"
            "últimas operaciones sobre la base de datos.\n"
            "Los últimos datos introducidos no han sido guardados, por favor\n"
            "revise sus últimas acciones y repita las operaciones que no\n"
            "se han guardado.\n"
        )

        if ctx is not None:

            msg += self.tr("Contexto: %s\n" % ctx)

        # FIXME: Missing _gui parameter
        # self.msgBoxWarning(msg)
        LOGGER.warning("%s\n", msg)

    def clearProject(self) -> None:
        """Cleanup."""
        application.PROJECT.actions = {}
        application.PROJECT.areas = {}
        application.PROJECT.modules = {}
        # application.PROJECT.tables = {}

    def acl(self) -> Optional["pnaccesscontrollists.PNAccessControlLists"]:
        """Return acl."""
        return self.acl_

    def set_acl(self, acl: "pnaccesscontrollists.PNAccessControlLists") -> None:
        """Set acl to pineboo."""

        if application.ENABLE_ACLS:
            self.acl_ = acl
        else:
            LOGGER.warning("ACLS usage is disabled")

    def reinitP(self) -> None:
        """Reinitialize application.PROJECT."""

        from .parsers.parser_mtd import pnormmodelsfactory

        self.db().managerModules().finish()
        self.db().manager().finish()
        self.setMainWidget(None)
        self.db().managerModules().setActiveIdModule("")
        self.clearProject()

        if application.PROJECT.main_window is None and not utils_base.is_library():
            from pineboolib.plugins import mainform

            main_form_name = settings.CONFIG.value("ebcomportamiento/main_form_name", "eneboo")
            main_form = getattr(mainform, main_form_name, None)
            main_form_class = getattr(main_form, "MainForm", None)
            if main_form_class is not None:
                application.PROJECT.main_window = main_form_class()
            # if application.PROJECT.main_form is not None:
            #    application.PROJECT.main_form.mainWindow = application.PROJECT.main_window.MainForm()
            #    application.PROJECT.main_window = application.PROJECT.main_form.mainWindow
            if application.PROJECT.main_window is not None:
                application.PROJECT.main_window.initScript()
                application.PROJECT.main_window.initialized_mods_ = []

        qsadictmodules.QSADictModules.clean_all()
        pnormmodelsfactory.PROCESSED = []
        application.PROJECT.files = {}
        application.PROJECT.conn_manager.useConn("default")
        application.PROJECT.conn_manager.useConn("dbaux")
        application.PROJECT.run()
        # application.PROJECT.load_classes()
        # application.PROJECT.load_orm()
        # application.PROJECT.load_modules()
        self.db().managerModules().reloadStaticLoader()

        self.db().managerModules().loadIdAreas()
        self.db().managerModules().loadAllIdModules()

        self.db().manager().init()

        self.db().managerModules()
        # self.db().manager().cleanupMetaData()
        if self.acl_:
            self.acl_.init()

        self.loadScripts()
        application.PROJECT.load_orm()
        # self.db().managerModules().setShaFromGlobal()

        self._inicializing = False
        if not utils_base.is_library():

            if application.PROJECT.main_window:
                if not hasattr(application.PROJECT.main_window, "initModule"):
                    self.call("sys.init()", [])
                if hasattr(application.PROJECT.main_window, "initToolBox"):
                    application.PROJECT.main_window.initToolBox()

                # mw.readState()

                container = getattr(application.PROJECT.main_window, "container_", None)
                if container is not None:
                    container.installEventFilter(self)
                # self.container_.setDisable(False)

            self.callScriptEntryFunction()

            reinit_func = getattr(application.PROJECT.main_window, "reinitScript", None)
            if reinit_func is not None:
                reinit_func()

        LOGGER.info("Reinit completed!!")

    def showDocPage(self, url_: str) -> None:
        """Show documentation."""

        sysbasetype.SysBaseType.openUrl([url_])

    def toPixmap(self, value: str) -> "QtGui.QPixmap":
        """Create a QPixmap from a text."""

        from pineboolib.application.utils import xpm
        from PyQt6 import QtGui

        ret_ = QtGui.QPixmap()

        file_name = xpm.cache_xpm(value)
        if file_name:
            ret_ = QtGui.QPixmap(file_name)

        return ret_

    def fromPixmap(self, pix_: "QtGui.QPixmap") -> str:
        """Return a text from a QPixmap."""
        ret_: str = ""
        if pix_.isNull():
            return ret_

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        buffer_ = QtCore.QBuffer()
        buffer_.open(QtCore.QIODevice.OpenModeFlag.WriteOnly)
        pix_.save(buffer_, "xpm")

        application.PROJECT.app.restoreOverrideCursor()

        return str(buffer_.data())

    def scalePixmap(
        self, pix_: "QtGui.QPixmap", width: int, height: int, mode_: "QtCore.Qt.AspectRatioMode"
    ) -> "QtGui.QImage":
        """Return QImage scaled from a QPixmap."""

        img_ = pix_.toImage()

        return img_.scaled(height, height, mode_)

    def timeUser(self) -> "str":
        """Get amount of time running."""

        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.DateFormat.ISODate)

    def call(self, function, argument_list=[], object_content=None, show_exceptions=True) -> Any:
        """Call a QS project function."""
        return application.PROJECT.call(function, argument_list, object_content, show_exceptions)

    @decorators.not_implemented_warn
    def setNotExit(self, value: bool) -> None:
        """Protect against window close."""
        self._not_exit = value

    def setNotifyEndTransaction(self, value: bool) -> None:
        """Set notify end transaction mode."""

        DB_SIGNALS.notify_end_transaction_ = value

    def setNotifyBeginTransaction(self, value: bool) -> None:
        """Set notify begin transaction mode."""

        DB_SIGNALS.notify_begin_transaction_ = value

    def setNotifyRollbackTransaction(self, value: bool) -> None:
        """Set notify rollback transaction mode."""

        DB_SIGNALS.notify_roll_back_transaction_ = value

    def notifyBeginTransaction(self) -> bool:
        """Return if notify begin transaction is enabled."""

        return DB_SIGNALS.notify_begin_transaction_

    def notifyEndTransaction(self) -> bool:
        """Return if notify end transaction is enabled."""

        return DB_SIGNALS.notify_end_transaction_

    def notifyRollbackTransaction(self) -> bool:
        """Return if notify rollback transaction is enabled."""

        return DB_SIGNALS.notify_roll_back_transaction_

    @decorators.not_implemented_warn
    def printTextEdit(self, editor_):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def setPrintProgram(self, print_program_):
        """Not implemented."""
        pass

    def setCaptionMainWidget(self, text: str) -> None:
        """Set caption main widget."""
        if application.PROJECT.main_window is not None:
            application.PROJECT.main_window.setCaptionMainWidget(text)

    @decorators.not_implemented_warn
    def addSysCode(self, code, script_entry_function):
        """Not implemented."""
        pass

    def setScriptEntryFunction(self, script_enttry_function) -> None:
        """Set which QS function to call on startup."""
        self.script_entry_function_ = script_enttry_function

    @decorators.not_implemented_warn
    def setDatabaseLockDetection(
        self, on_, msec_lapsus, lim_checks, show_warn, msg_warn, connection_name
    ):
        """Not implemented."""
        pass

    def popupWarn(self, msg_warn: str, script_call: List[Any] = []) -> None:
        """Show a warning popup."""
        main_window = application.PROJECT.main_window

        if main_window is None:
            return

        if script_call:
            self.call(script_call, [], self)

        if not main_window.isHidden():
            QtWidgets.QWhatsThis.showText(
                main_window.mapToGlobal(QtCore.QPoint(main_window.width() * 2, 0)),
                msg_warn,
                main_window,
            )
            QtCore.QTimer.singleShot(2000, QtWidgets.QWhatsThis.hideText)
            application.PROJECT.app.processEvents()  # type: ignore[misc] # noqa: F821

    @decorators.not_implemented_warn
    def checkDatabaseLocks(self, timer_):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def saveGeometryForm(self, name, geo):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def geometryForm(self, name):
        """Not implemented."""
        pass

    def staticLoaderSetup(self) -> None:
        """Initialize static loader."""
        self.db().managerModules().staticLoaderSetup()

    def mrProper(self) -> None:
        """Cleanup database."""
        self.db().mainConn().Mr_Proper()

    def showConsole(self) -> None:
        """Show application console on GUI."""

        if application.PROJECT.main_window is not None:
            if self._ted_output:
                self._ted_output.parentWidget().close()

            dock_widget = QtWidgets.QDockWidget("tedOutputDock", application.PROJECT.main_window)

            if dock_widget is not None:

                self._ted_output = TextEditOutput(dock_widget)
                dock_widget.setWidget(self._ted_output)
                dock_widget.setWindowTitle(self.tr("Mensajes de Eneboo"))
                application.PROJECT.main_window.addDockWidget(
                    QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, dock_widget
                )

    def consoleShown(self) -> bool:
        """Return if console is shown."""

        hidden = getattr(self._ted_output, "isHidden", False)
        return hidden() if hidden is not None else False

    def modMainWidget(self, id_modulo: str) -> Optional["QtWidgets.QWidget"]:
        """Set module main widget."""

        main_window = application.PROJECT.main_window
        if main_window is None:
            return None

        mod_widget: Optional[QtWidgets.QWidget] = None
        dict_main_widgets = getattr(main_window, "_dict_main_widgets", {})
        if id_modulo in dict_main_widgets.keys():
            mod_widget = dict_main_widgets[id_modulo]

        if mod_widget is None:
            list_ = application.PROJECT.app.topLevelWidgets()
            for widget in list_:
                if widget.objectName() == id_modulo:
                    mod_widget = widget
                    break

        if mod_widget is None and self.mainWidget() is not None:
            mod_widget = cast(
                QtWidgets.QWidget, main_window.main_widget.findChild(QtWidgets.QWidget, id_modulo)
            )

        return mod_widget

    def evaluateProject(self) -> None:
        """Execute QS entry function."""
        QtCore.QTimer.singleShot(0, self.callScriptEntryFunction)

    def callScriptEntryFunction(self) -> None:
        """Execute QS entry function."""
        if self.script_entry_function_:
            self.call(self.script_entry_function_, [], self)
            # self.script_entry_function_ = None

    def emitTransactionBegin(
        self, cursor: Union["pnsqlcursor.PNSqlCursor", "isqlcursor.ISqlCursor"]
    ) -> None:
        """Emit signal."""
        self.transactionBegin.emit()
        DB_SIGNALS.emitTransactionBegin(cursor)

    def emitTransactionEnd(
        self, cursor: Union["pnsqlcursor.PNSqlCursor", "isqlcursor.ISqlCursor"]
    ) -> None:
        """Emit signal."""
        self.transactionEnd.emit()
        DB_SIGNALS.emitTransactionEnd(cursor)

    def emitTransactionRollback(
        self, cursor: Union["pnsqlcursor.PNSqlCursor", "isqlcursor.ISqlCursor"]
    ) -> None:
        """Emit signal."""
        self.transactionRollback.emit()
        DB_SIGNALS.emitTransactionRollback(cursor)

    def self_(self) -> "PNApplication":
        """Return self."""

        return self

    @decorators.not_implemented_warn
    def gsExecutable(self):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def evalueateProject(self):
        """Not implemented."""
        pass

    def DGI(self) -> "dgi_schema.dgi_schema":
        """Return current DGI."""
        return application.PROJECT.DGI

    def singleFLLarge(self) -> bool:
        """
        Para especificar si usa fllarge unificado o multiple (Eneboo/Abanq).

        @return True (Tabla única), False (Múltiples tablas)
        """
        if self.flLargeMode is None:
            ret = utils.sql_select("flsettings", "valor", "flkey='FLLargeMode'")
            self.flLargeMode = False if ret in ["True", True] else True
        return self.flLargeMode

    def msgBoxWarning(self, text: str, _gui: Any) -> None:
        """Display warning."""
        _gui.msgBoxWarning(text)

    @decorators.not_implemented_warn
    def showDebug(self):
        """Return if debug is shown."""
        return self.show_debug_

    def db(self) -> "pnconnectionmanager.PNConnectionManager":
        """Return current connection."""
        return application.PROJECT.conn_manager

    def classType(self, obj) -> str:
        """Return class for object."""

        return str(type(obj))

    def mainWidget(self) -> Optional["QtWidgets.QWidget"]:
        """Return current mainWidget."""
        return getattr(application.PROJECT.main_window, "main_widget", None)

    def quit(self) -> None:
        """Handle quit/close signal."""
        main_window = application.PROJECT.main_window
        if main_window is not None:
            main_window.close()

    def queryExit(self) -> bool:
        """Ask user if really wants to quit."""

        if self._not_exit:
            return False

        if application.PROJECT.conn_manager.mainConn().interactiveGUI():

            main_widget = application.PROJECT.main_window
            if main_widget is not None:
                ret = QtWidgets.QMessageBox.question(
                    main_widget,
                    self.tr("Salir ..."),
                    self.tr("¿ Quiere salir de la aplicación ?"),
                    QtWidgets.QMessageBox.StandardButton.Yes,
                    QtWidgets.QMessageBox.StandardButton.No,
                )
                return ret == QtWidgets.QMessageBox.StandardButton.Yes

        return True

    def loadScripts(self) -> None:
        """Load scripts for all modules."""

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        list_modules = self.db().managerModules().listAllIdModules()
        for item in list_modules:
            self.loadScriptsFromModule(item)

        application.PROJECT.app.restoreOverrideCursor()

    def urlPineboo(self) -> None:
        """Open Eneboo URI."""
        sysbasetype.SysBaseType.openUrl(["http://eneboo.org/"])

    def helpIndex(self) -> None:
        """Open help."""
        sysbasetype.SysBaseType.openUrl(["http://manuales-eneboo-pineboo.org/"])

    def loadTranslations(self) -> None:
        """
        Install loaded translations.
        """

        lang = QtCore.QLocale().name()[:2]
        lang = "es" if lang == "C" else lang

        for module in self.modules().keys():
            self.loadTranslationFromModule(module, lang)

        for item in self._translator:
            self.removeTranslator(item)
            if item._sys_trans:
                self.installTranslator(item)

    def trMulti(self, text: str, lang: str):
        """
        Lookup translation for certain language.

        @param text, Cadena de texto
        @param lang, Idioma.
        @return Cadena de texto traducida.
        """
        return application.PROJECT.app.tr("%s_MULTILANG" % lang.upper(), text)

    def setMultiLang(self, enable_: bool, lang_id_: str) -> None:
        """
        Change multilang status.

        @param enable, Boolean con el nuevo estado
        @param langid, Identificador del leguaje a activar
        """
        self._multi_lang_enabled = enable_
        if enable_ and lang_id_:
            self._multi_lang_id = lang_id_.upper()

    def loadTranslationFromModule(self, id_module: str, lang: str) -> None:
        """
        Load translation from module.

        @param idM, Identificador del módulo donde buscar
        @param lang, Lenguaje a buscar
        """
        self.installTranslator(self.createModTranslator(id_module, lang, True))

    def installTranslator(self, tor) -> None:
        """
        Install translation for app.

        @param tor, Objeto con la traducción a cargar
        """

        if tor is not None:
            application.PROJECT.app.installTranslator(tor)
            self._translator.append(tor)

    def removeTranslator(self, tor) -> None:
        """
        Delete translation on app.

        @param tor, Objeto con la traducción a cargar
        """
        if tor is None:
            return
        else:
            application.PROJECT.app.removeTranslator(tor)
            if tor in self._translator:
                self._translator.remove(tor)

    @decorators.not_implemented_warn
    def createSysTranslator(self, lang, load_default):
        """
        Create SYS Module translation.

        @param lang, Idioma a usar
        @param loadDefault, Boolean para cargar los datos por defecto
        @return objeto traducción
        """
        pass

    def createModTranslator(
        self, id_module, lang: str, load_default: bool = False
    ) -> Optional["pntranslator.PNTranslator"]:
        """
        Create new translation for module.

        @param idM, Identificador del módulo
        @param lang, Idioma a usar
        @param loadDefault, Boolean para cargar los datos por defecto
        @return objeto traducción
        """
        file_ts = "%s.%s.ts" % (id_module, lang)
        key = None

        if id_module == "sys":
            key = " "

        else:
            if self.db():
                key = self.db().managerModules().shaOfFile(file_ts)

        if key:
            from .translator import pntranslator

            tor = pntranslator.PNTranslator(
                self.mainWidget(), "%s_%s" % (id_module, lang), lang == "multilang"
            )
            if key and tor.loadTsContent(key):
                return tor

        return self.createModTranslator(id_module, "es") if load_default else None

    def modules(self) -> Dict[str, "app_module.Module"]:
        """Return loaded modules."""
        return application.PROJECT.modules

    def commaSeparator(self) -> str:
        """Return comma separator for floating points on current language."""
        return self.comma_separator

    def tmp_dir(self) -> str:
        """Return temporary folder."""
        return application.PROJECT.tmpdir

    def applicationDirPath(self) -> str:
        """Return application dir path."""

        return application.PROJECT.app.applicationDirPath()

    def transactionLevel(self):
        """Return number of concurrent transactions."""
        return application.PROJECT.conn_manager.useConn("default").transactionLevel()

    def version(self):
        """Return app version."""
        return application.PROJECT.load_version()

    def dialogGetFileImage(self) -> Optional[str]:
        """Get image file name."""

        # from . import flpixmapviewer

        file_dialog = QtWidgets.QFileDialog(
            QtWidgets.QApplication.focusWidget(),
            self.tr("Elegir archivo"),
            application.PROJECT.tmpdir,
            "*",
        )
        # pixmap_viewer = flpixmapview.FLPixmapView(file_dialog)

        # pixmap_viewer.setAutoScaled(True)
        # file_dialog.setContentsPreviewEnabled(True)
        # file_dialog.setContentsPreview(p, p)
        # file_dialog.setPreviewMode(QtWidgets.QFileDialog.Contents)

        file_name = None
        if file_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            list_ = file_dialog.selectedFiles()
            if list_:
                file_name = list_[0]

        return file_name


class TextEditOutput(QtWidgets.QPlainTextEdit):
    """FLTextEditOutput class."""

    oldStdout: TextIO
    oldStderr: TextIO

    def __init__(self, parent: "QtWidgets.QWidget") -> None:
        """Inicialize."""
        super().__init__(parent)

        self.oldStdout = sys.stdout  # pylint: disable=invalid-name
        self.oldStderr = sys.stderr  # pylint: disable=invalid-name
        sys.stdout = self  # type: ignore [assignment] # noqa F821
        sys.stderr = self  # type: ignore [assignment] # noqa F821
        self.setReadOnly(True)

    def write(self, txt: Union[bytearray, bytes, str]) -> None:
        """Set text."""
        txt = str(txt)
        if self.oldStdout:
            self.oldStdout.write(txt)
        self.appendPlainText(txt)

    def flush(self):
        """Flush data."""

        pass

    def close(self) -> bool:
        """Control close."""
        if self.oldStdout:
            sys.stdout = self.oldStdout
        if self.oldStderr:
            sys.stderr = self.oldStderr
        return super().close()


# aqApp = FLApplication()
aqApp: "PNApplication"
