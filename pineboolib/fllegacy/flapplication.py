# -*- coding: utf-8 -*-
"""FLApplication Module."""

from PyQt5 import QtCore, QtWidgets

from pineboolib import logging

from pineboolib.core import decorators
from pineboolib.core.settings import config

from pineboolib.application import project
from pineboolib.application.database import db_signals
from pineboolib.application.qsatypes.sysbasetype import SysBaseType
from pineboolib.application.acls import pnaccesscontrollists

from .fltranslator import FLTranslator

from .fltexteditoutput import FLTextEditOutput

from typing import Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.database.pnsqlcursor import PNSqlCursor  # noqa: F401


logger = logging.getLogger("FLApplication")


class FLPopupWarn(QtCore.QObject):
    """FLPoppupWarn Class."""

    # FIXME: Incomplete class!
    def __init__(self, mainwindow) -> None:
        """Inicialize."""

        self.mainWindow = mainwindow


class FLApplication(QtCore.QObject):
    """FLApplication Class."""

    _inicializing: bool
    _destroying: bool
    _ted_output: Optional[QtWidgets.QWidget]
    _not_exit: bool
    _multi_lang_enabled: bool
    _multi_lang_id: str
    _translator: List[FLTranslator]

    container_: Optional[QtWidgets.QWidget]  # Contenedor actual??

    main_widget_: Optional[QtWidgets.QWidget]

    # project_ = None

    form_alone_: bool
    acl_: Optional[pnaccesscontrollists.PNAccessControlLists]
    popup_warn_: Any
    fl_factory_: Any
    op_check_update_: bool
    style: bool

    init_single_fl_large: bool
    show_debug_: bool
    timer_idle_: Optional[QtCore.QTimer]
    time_user_: QtCore.QTimer
    script_entry_function_: Optional[str]
    _event_loop: Optional[QtCore.QEventLoop]
    window_menu: Optional[QtWidgets.QMenu] = None
    modules_menu: Any

    def __init__(self) -> None:
        """Create new FLApplication."""
        super(FLApplication, self).__init__()
        self.main_widget_ = None
        # self.project_ = None
        self.wb_ = None

        self._translator = []

        self.form_alone_ = False
        self._not_exit = False
        self.timer_idle_ = None
        self.popup_warn_ = None
        self._inicializing = False
        self._destroying = False
        self.fl_factory_ = None
        self.op_check_update_ = False
        self.window_menu = None
        db_signals.notify_begin_transaction_ = False
        db_signals.notify_end_transaction_ = False
        db_signals.notify_roll_back_transaction_ = False
        self._ted_output = None
        self.style = False
        self.init_single_fl_large = False
        self.show_debug_ = True  # FIXME
        self.script_entry_function_ = None

        self.acl_ = None
        # self.fl_factory_ = FLObjectFactory() # FIXME para un futuro
        # self.time_user_ = QtCore.QDateTime.currentDateTime() # Moved to pncontrolsfacotry.SysType
        self._multi_lang_enabled = False
        self._multi_lang_id = QtCore.QLocale().name()[:2].upper()

        self.locale_system_ = QtCore.QLocale.system()
        v = 1.1
        self.comma_separator = self.locale_system_.toString(v, "f", 1)[1]
        self.setObjectName("aqApp")
        self._event_loop = None

    @property
    def event_loop(self) -> QtCore.QEventLoop:
        """Get Eventloop, create one if it does not exist."""
        if self._event_loop is None:
            self._event_loop = QtCore.QEventLoop()
        return self._event_loop

    def eventLoop(self) -> "QtCore.QEventLoop":
        """Create main event loop."""
        return QtCore.QEventLoop()

    @decorators.NotImplementedWarn
    def checkForUpdate(self):
        """Not used in Pineboo."""
        pass

    @decorators.NotImplementedWarn
    def checkForUpdateFinish(self, op):
        """Not used in pineboo."""
        pass

    @decorators.NotImplementedWarn
    def initfcgi(self):
        """Init for fast cgi."""
        pass

    @decorators.NotImplementedWarn
    def addObjectFactory(self, new_object_factory):
        """Add object onctructor. unused."""
        pass

    @decorators.NotImplementedWarn
    def callfcgi(self, call_function, argument_list):
        """Perform fastcgi call."""
        pass

    @decorators.NotImplementedWarn
    def endfcgi(self):
        """End fastcgi call signal."""
        pass

    def localeSystem(self) -> Any:
        """Return locale of the system."""
        return self.locale_system_

    @decorators.NotImplementedWarn
    def openQSWorkbench(self):
        """Open debugger. Unused."""
        pass

    def setMainWidget(self, w) -> None:
        """Set mainWidget."""

        if w is None:
            self.main_widget_ = None
            return

        QtWidgets.QApplication.setActiveWindow(w)
        self.main_widget_ = w

    @decorators.NotImplementedWarn
    def makeStyle(self, style_):
        """Apply specified style."""
        pass

    def chooseFont(self) -> None:
        """Open font selector."""

        font_ = QtWidgets.QFontDialog().getFont()
        if font_:
            QtWidgets.QApplication.setFont(font_[0])
            save_ = [font_[0].family(), font_[0].pointSize(), font_[0].weight(), font_[0].italic()]

            config.set_value("application/font", save_)

    def showStyles(self) -> None:
        """Open style selector."""
        if not self.style:
            self.initStyles()
        # if self.style:
        #    self.style.exec_()

    @decorators.NotImplementedWarn
    def showToggleBars(self):
        """Show toggle bars."""
        pass

    def setStyle(self, style_: str) -> None:
        """Change application style."""
        config.set_value("application/style", style_)
        QtWidgets.QApplication.setStyle(style_)

    def initStyles(self) -> None:
        """Initialize styles."""
        from pineboolib.core.settings import config

        self.style_mapper = QtCore.QSignalMapper()
        self.style_mapper.mapped[str].connect(self.setStyle)  # type: ignore
        style_read = config.value("application/style", None)
        if not style_read:
            style_read = "Fusion"

        style_menu = self.mainWidget().findChild(QtWidgets.QMenu, "style")

        if style_menu:
            ag = QtWidgets.QActionGroup(style_menu)
            for style_ in QtWidgets.QStyleFactory.keys():
                action_ = style_menu.addAction(style_)
                action_.setObjectName("style_%s" % style_)
                action_.setCheckable(True)
                if style_ == style_read:
                    action_.setChecked(True)

                action_.triggered.connect(self.style_mapper.map)
                self.style_mapper.setMapping(action_, style_)
                ag.addAction(action_)
            ag.setExclusive(True)

        self.style = True

    @decorators.NotImplementedWarn
    def getTabWidgetPages(self, wn, n):
        """Get tabs."""
        pass

    @decorators.NotImplementedWarn
    def getWidgetList(self, wn, c):
        """Get widgets."""
        pass

    def aboutQt(self) -> None:
        """Show About QT."""

        QtWidgets.QMessageBox.aboutQt(self.mainWidget())

    def aboutPineboo(self) -> None:
        """Show about Pineboo."""
        if project.DGI.localDesktop():
            fun_about = getattr(project.DGI, "about_pineboo", None)
            if fun_about is not None:
                fun_about()

    def statusHelpMsg(self, text) -> None:
        """Show help message."""
        from pineboolib.core.settings import config

        if config.value("application/isDebuggerMode", False):
            logger.warning("StatusHelpMsg: %s", text)

        if not self.main_widget_:
            return

        self.main_widget_.statusBar().showMessage(text, 2000)

    def openMasterForm(self, action_name, pix) -> None:
        """Open a tab."""
        if action_name in project.actions.keys():
            project.actions[action_name].openDefaultForm()

    @decorators.NotImplementedWarn
    def openDefaultForm(self):
        """Open a default form."""
        pass

    def execMainScript(self, action_name) -> None:
        """Execute main script."""
        if action_name in project.actions.keys():
            project.actions[action_name].execDefaultScript()

    @decorators.NotImplementedWarn
    def execDefaultScript(self):
        """Execute default script."""
        pass

    def loadScriptsFromModule(self, idm) -> None:
        """Load scripts from named module."""
        if idm in project.modules.keys():
            project.modules[idm].load()

    def reinit(self) -> None:
        """Cleanup and restart."""
        if self._inicializing or self._destroying:
            return

        self.stopTimerIdle()
        # self.apAppIdle()
        self._inicializing = True

        if hasattr(project.main_form, "mainWindow"):
            mw = project.main_form.mainWindow

            if mw is not None:
                mw.writeState()
                mw.writeStateModule()
                if hasattr(mw, "_p_work_space"):
                    mw._p_work_space = None

        QtCore.QTimer.singleShot(0, self.reinitP)
        from pineboolib.application.parsers.mtdparser.pnormmodelsfactory import empty_base

        empty_base()

    def startTimerIdle(self) -> None:
        """Start timer."""
        if not self.timer_idle_:
            self.timer_idle_ = QtCore.QTimer()
            self.timer_idle_.timeout.connect(self.aqAppIdle)
        else:
            self.timer_idle_.stop()

        self.timer_idle_.start(1000)

    def stopTimerIdle(self) -> None:
        """Stop timer."""
        if self.timer_idle_ and self.timer_idle_.isActive():
            self.timer_idle_.stop()

    def aqAppIdle(self) -> None:
        """Check and fix transaction level."""
        if QtWidgets.QApplication.activeModalWidget() or QtWidgets.QApplication.activePopupWidget():
            return

        self.checkAndFixTransactionLevel("Application::aqAppIdle()")

    def checkAndFixTransactionLevel(self, ctx=None) -> None:
        """Fix transaction."""
        dict_db = self.db().dictDatabases()
        if not dict_db:
            return

        roll_back_done = False
        for it in dict_db.values():
            if it.transactionLevel() <= 0:
                continue
            roll_back_done = True
            last_active_cursor = it.lastActiveCursor()
            if last_active_cursor is not None:
                last_active_cursor.rollbackOpened(-1)
            if it.transactionLevel() <= 0:
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
        logger.warning("%s\n", msg)

    def clearProject(self) -> None:
        """Cleanup."""
        project.actions = {}
        project.areas = {}
        project.modules = {}
        project.tables = {}

    def acl(self) -> Optional[pnaccesscontrollists.PNAccessControlLists]:
        """Return acl."""
        return self.acl_

    def set_acl(self, acl: pnaccesscontrollists.PNAccessControlLists) -> None:
        """Set acl to pineboo."""
        self.acl_ = acl

    def reinitP(self) -> None:
        """Reinitialize project."""
        from pineboolib.application.qsadictmodules import QSADictModules

        self.db().managerModules().finish()
        self.db().manager().finish()
        self.setMainWidget(None)
        self.db().managerModules().setActiveIdModule("")

        self.clearProject()
        mw = project.main_window
        if self.main_widget_ is None:
            self.main_widget_ = mw

        if project.main_window is None:
            raise Exception("project.main_window is empty!")

        project.main_window.initialized_mods_ = []

        QSADictModules.clean_all()

        project.run()
        self.db().managerModules().loadIdAreas()
        self.db().managerModules().loadAllIdModules()
        # for module_name in project.modules.keys():
        #    project.modules[module_name].load()
        self.db().manager().init()

        self.db().managerModules()
        self.db().manager().cleanupMetaData()

        if self.acl_:
            self.acl_.init()

        self.loadScripts()
        # self.db().managerModules().setShaFromGlobal()
        self.call("sys.init()", [])
        if hasattr(mw, "initToolBox"):
            mw.initToolBox()

        mw.readState()

        if hasattr(mw, "container_"):
            mw.container_.installEventFilter(self)
            # self.container_.setDisable(False)

        self.callScriptEntryFunction()

        self._inicializing = False

        if hasattr(project.main_window, "reinitSript"):
            project.main_window.reinitSript()

    @decorators.NotImplementedWarn
    def showDocPage(self, url):
        """Show documentation."""
        pass

    def timeUser(self) -> Any:
        """Get amount of time running."""

        return SysBaseType.time_user_

    def call(self, function, argument_list=[], object_content=None, show_exceptions=True) -> Any:
        """Call a QS project function."""
        return project.call(function, argument_list, object_content, show_exceptions)

    @decorators.NotImplementedWarn
    def setNotExit(self, b):
        """Protect against window close."""
        self._not_exit = b

    @decorators.NotImplementedWarn
    def printTextEdit(self, editor_):
        """Not implemented."""
        pass

    @decorators.NotImplementedWarn
    def setPrintProgram(self, print_program_):
        """Not implemented."""
        pass

    def setCaptionMainWidget(self, text: str) -> None:
        """Set caption main widget."""
        project.main_form.mainWindow.setCaptionMainWidget(text)

    @decorators.NotImplementedWarn
    def addSysCode(self, code, script_entry_function):
        """Not implemented."""
        pass

    def setScriptEntryFunction(self, script_enttry_function) -> None:
        """Set which QS function to call on startup."""
        self.script_entry_function_ = script_enttry_function

    @decorators.NotImplementedWarn
    def setDatabaseLockDetection(
        self, on, msec_lapsus, lim_checks, show_warn, msg_warn, connection_name
    ):
        """Not implemented."""
        pass

    def popupWarn(self, msg_warn, script_calls=[]) -> None:
        """Show a warning popup."""
        mw = self.container_ or self.main_widget_

        wi = QtWidgets.QWhatsThis

        if script_calls:
            if not mw:
                self.container_ = QtWidgets.QMainWindow(QtWidgets.QApplication.desktop())

            if not self.popup_warn_:
                self.popup_warn_ = FLPopupWarn(mw)  # FIXME: Empty class yet!

            self.popup_warn_.script_calls_ = script_calls
            wi.showText(
                QtWidgets.QApplication.desktop().mapToGlobal(QtCore.QPoint(5, 5)), msg_warn, mw
            )

        else:

            if not mw:
                return

        if mw is None:
            raise Exception("self.container_ and self.main_widget are empty!")

        if not mw.isHidden():
            wi.showText(
                self.mainWidget().mapToGlobal(QtCore.QPoint(mw.width() * 2, 0)), msg_warn, mw
            )
            QtCore.QTimer.singleShot(4000, wi.hideText)
            self.processEvents()

    @decorators.NotImplementedWarn
    def checkDatabaseLocks(self, timer_):
        """Not implemented."""
        pass

    @decorators.NotImplementedWarn
    def saveGeometryForm(self, name, geo):
        """Not implemented."""
        pass

    @decorators.NotImplementedWarn
    def geometryForm(self, name):
        """Not implemented."""
        pass

    def staticLoaderSetup(self) -> None:
        """Initialize static loader."""
        self.db().managerModules().staticLoaderSetup()

    def mrProper(self) -> None:
        """Cleanup database."""
        self.db().conn.Mr_Proper()

    def showConsole(self) -> None:
        """Show application console on GUI."""
        mw = project.main_form.mainWindow
        if mw:
            if self._ted_output:
                self._ted_output.parentWidget().close()

            dw = QtWidgets.QDockWidget("tedOutputDock", mw)
            self._ted_output = FLTextEditOutput(dw)
            dw.setWidget(self._ted_output)
            dw.setWindowTitle(self.tr("Mensajes de Eneboo"))
            mw.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dw)

    def consoleShown(self) -> bool:
        """Return if console is shown."""
        return bool(self._ted_output and not self._ted_output.isHidden())

    def modMainWidget(self, id_modulo: str) -> Optional[QtWidgets.QWidget]:
        """Set module main widget."""
        mw = project.main_window
        mod_widget: Optional[QtWidgets.QWidget] = None
        if hasattr(mw, "_dict_main_widgets"):
            if id_modulo in mw._dict_main_widgets.keys():
                mod_widget = mw._dict_main_widgets[id_modulo]

        if mod_widget is None:
            list_ = QtWidgets.QApplication.topLevelWidgets()
            for w in list_:
                if w.objectName() == id_modulo:
                    mod_widget = w
                    break

        if mod_widget is None and self.mainWidget() is not None:
            mod_widget = self.mainWidget().findChild(QtWidgets.QWidget, id_modulo)

        return mod_widget

    def evaluateProject(self) -> None:
        """Execute QS entry function."""
        QtCore.QTimer.singleShot(0, self.callScriptEntryFunction)

    def callScriptEntryFunction(self) -> None:
        """Execute QS entry function."""
        if self.script_entry_function_:
            self.call(self.script_entry_function_, [], self)
            # self.script_entry_function_ = None

    def emitTransactionBegin(self, o: "PNSqlCursor") -> None:
        """Emit signal."""
        db_signals.emitTransactionBegin(o)

    def emitTransactionEnd(self, o: "PNSqlCursor") -> None:
        """Emit signal."""
        db_signals.emitTransactionEnd(o)

    def emitTransactionRollback(self, o: "PNSqlCursor") -> None:
        """Emit signal."""
        db_signals.emitTransactionRollback(o)

    @decorators.NotImplementedWarn
    def gsExecutable(self):
        """Not implemented."""
        pass

    @decorators.NotImplementedWarn
    def evalueateProject(self):
        """Not implemented."""
        pass

    def DGI(self) -> Any:
        """Return current DGI."""
        return project._DGI

    def singleFLLarge(self) -> bool:
        """
        Para especificar si usa fllarge unificado o multiple (Eneboo/Abanq).

        @return True (Tabla única), False (Múltiples tablas)
        """
        from pineboolib.fllegacy.flutil import FLUtil

        ret = FLUtil().sqlSelect("flsettings", "valor", "flkey='FLLargeMode'")
        if ret == "True":
            return False

        return True

    def msgBoxWarning(self, t, _gui) -> None:
        """Display warning."""
        _gui.msgBoxWarning(t)

    @decorators.NotImplementedWarn
    def showDebug(self):
        """Return if debug is shown."""
        return self.show_debug_

    def db(self) -> Any:
        """Return current connection."""
        return project._conn

    @decorators.NotImplementedWarn
    def classType(self, n):
        """Return class for object."""

        # return type(self.resolveObject(n)())
        return type(n)

    # def __getattr__(self, name):
    #    return getattr(project, name, None)

    def mainWidget(self) -> Any:
        """Return current mainWidget."""
        ret_ = self.main_widget_
        return ret_

    def quit(self) -> None:
        """Handle quit/close signal."""
        if self.main_widget_ is not None:
            self.main_widget_.close()

    def queryExit(self) -> Any:
        """Ask user if really wants to quit."""

        if self._not_exit:
            return False

        if not SysBaseType.interactiveGUI():
            return True

        ret = QtWidgets.QMessageBox.information(
            project.main_form.mainWindow,
            self.tr("Salir ..."),
            self.tr("¿ Quiere salir de la aplicación ?"),
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No,
        )
        return ret == QtWidgets.QMessageBox.Yes

    def loadScripts(self) -> None:
        """Load scripts for all modules."""

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        list_modules = self.db().managerModules().listAllIdModules()
        for it in list_modules:
            self.loadScriptsFromModule(it)

        QtWidgets.QApplication.restoreOverrideCursor()

    def urlPineboo(self) -> None:
        """Open Eneboo URI."""
        SysBaseType.openUrl(["http://eneboo.org/"])

    def helpIndex(self) -> None:
        """Open help."""
        SysBaseType.openUrl(["http://manuales-eneboo-pineboo.org/"])

    def tr(self, sourceText: str, disambiguation: Optional[str] = None, n: int = 0) -> Any:
        """Open translations."""

        return QtWidgets.QApplication.translate("system", sourceText)

    def loadTranslations(self) -> None:
        """
        Install loaded translations.
        """
        translatorsCopy = []
        if self._translator:
            for t in self._translator:
                translatorsCopy.append(t)
            for it in translatorsCopy:
                self.removeTranslator(it)

        lang = QtCore.QLocale().name()[:2]

        if lang == "C":
            lang = "es"

        for module in self.modules().keys():
            self.loadTranslationFromModule(module, lang)

        for it in translatorsCopy:
            if it._sys_trans:
                self.installTranslator(it)
            else:
                del it

    @decorators.BetaImplementation
    def trMulti(self, s, l):
        """
        Lookup translation for certain language.

        @param s, Cadena de texto
        @param l, Idioma.
        @return Cadena de texto traducida.
        """
        return s
        # FIXME: self.tr does not support two arguments.
        # backMultiEnabled = self._multi_lang_enabled
        # ret = self.tr("%s_MULTILANG" % l.upper(), s)
        # self._multi_lang_enabled = backMultiEnabled
        # return ret

    @decorators.BetaImplementation
    def setMultiLang(self, enable, langid):
        """
        Change multilang status.

        @param enable, Boolean con el nuevo estado
        @param langid, Identificador del leguaje a activar
        """
        self._multi_lang_enabled = enable
        if enable and langid:
            self._multi_lang_id = langid.upper()

    def loadTranslationFromModule(self, idM, lang) -> None:
        """
        Load translation from module.

        @param idM, Identificador del módulo donde buscar
        @param lang, Lenguaje a buscar
        """
        self.installTranslator(self.createModTranslator(idM, lang, True))
        # self.installTranslator(self.createModTranslator(idM, "mutliLang"))

    def installTranslator(self, tor) -> None:
        """
        Install translation for app.

        @param tor, Objeto con la traducción a cargar
        """

        if tor is None:
            return
        else:
            QtWidgets.qApp.installTranslator(tor)
            self._translator.append(tor)

    def removeTranslator(self, tor) -> None:
        """
        Delete translation on app.

        @param tor, Objeto con la traducción a cargar
        """
        if tor is None:
            return
        else:
            QtWidgets.qApp.removeTranslator(tor)
            for t in self._translator:
                if t == tor:
                    del t
                    break

    @decorators.NotImplementedWarn
    def createSysTranslator(self, lang, loadDefault):
        """
        Create SYS Module translation.

        @param lang, Idioma a usar
        @param loadDefault, Boolean para cargar los datos por defecto
        @return objeto traducción
        """
        pass

    def createModTranslator(self, idM, lang, loadDefault=False) -> Optional["FLTranslator"]:
        """
        Create new translation for module.

        @param idM, Identificador del módulo
        @param lang, Idioma a usar
        @param loadDefault, Boolean para cargar los datos por defecto
        @return objeto traducción
        """

        fileTs = "%s.%s.ts" % (idM, lang)
        key = None
        if self.db():
            key = self.db().managerModules().shaOfFile(fileTs)

        if idM == "sys":
            if not key:
                key = " "

        if key:
            tor = FLTranslator(self, "%s_%s" % (idM, lang), lang == "multilang")
            if key and tor.loadTsContent(key):
                return tor

        return self.createModTranslator(idM, "es") if loadDefault else None

    def modules(self) -> Any:
        """Return loaded modules."""
        return project.modules

    def commaSeparator(self) -> Any:
        """Return comma separator for floating points on current language."""
        return self.comma_separator

    def tmp_dir(self) -> Any:
        """Return temporary folder."""
        return project.tmpdir

    def transactionLevel(self):
        """Return number of concurrent transactions."""
        return project.conn.transactionLevel()

    def version(self):
        """Return app version."""
        return project.version


"""
class FLPopuWarn(QtWidgets.QWhatsThis):

    script_calls_ = []

    def __init__(self, parent):
        self.script_calls_ = []
        super(FLPopuWarn, self).__init__(parent)

    def clicked(self, href):
        if href:

            if href.find(":") > -1:
                h = href.split(":")[1]
            if h.find(".") == 1:
                pncontrolsfactury.aqApp.call(h.split(".")[1], self.script_calls_[href], h.split(".")[0])
            else:
                pncontrolsfacotry.aqApp.call(h, self.script_calls_[href], None)
"""


# aqApp = FLApplication()
aqApp: FLApplication
