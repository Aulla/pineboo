"""Eneboo_mdi module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui, QtCore, QtXml

from pineboolib.core.utils import utils_base
from pineboolib.core import settings

from pineboolib.application.acls import pnaccesscontrollists

from pineboolib.fllegacy.aqsobjects import aqs
from pineboolib.fllegacy import flworkspace, flformdb
from pineboolib.application import pncore
from pineboolib import application
from pineboolib import logging

from typing import Any, cast, List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.database import pnconnectionmanager

LOGGER = logging.get_logger(__name__)


class MainForm(QtWidgets.QMainWindow):
    """MainForm class."""

    acl_: pnaccesscontrollists.PNAccessControlLists
    is_closing_: bool
    mdi_enable_: bool
    container_: Optional[QtWidgets.QMainWindow]
    main_window: QtWidgets.QMainWindow
    exit_button: QtWidgets.QPushButton
    _p_work_space: Any
    mdi_toolbuttons: List[QtWidgets.QToolButton]
    _dict_main_widgets: Dict[str, QtWidgets.QWidget]
    debug_level: int
    tool_box_: Any
    toogle_bars_: Any
    last_text_caption_: str
    _map_geometry_form: List[Any]

    def __init__(self) -> None:
        """Inicialize."""
        super().__init__()
        self._p_work_space = None
        application.PROJECT.aq_app.main_widget_ = self
        self.is_closing_ = False
        self.mdi_toolbuttons = []
        self._dict_main_widgets = {}

        self.container_ = None
        self.tool_box_ = None
        self.toogle_bars_ = None
        self._map_geometry_form = []
        self.last_text_caption_ = ""

    def reinitScript(self):
        """Reinit script."""

        application.PROJECT.aq_app.startTimerIdle()

        if self._dict_main_widgets:
            self._dict_main_widgets = {}

    @classmethod
    def setdebug_level(self, level: int) -> None:
        """Set a new debug level."""
        MainForm.debug_level = level

    def initScript(self) -> None:
        """Inicialize main script."""

        self.createUi(utils_base.filedir("plugins/mainform/eneboo_mdi/mainform.ui"))

        self.container_ = self
        self.init()

    def db(self) -> "pnconnectionmanager.PNConnectionManager":
        """Return the dababase connection."""

        return application.PROJECT.conn_manager

    def createUi(self, ui_file: str) -> None:
        """Create UI from a file."""

        self.main_window = cast(
            QtWidgets.QMainWindow, self.db().managerModules().createUI(ui_file, None, self)
        )
        self.main_window.setObjectName("container")

    def init(self) -> None:
        """Initialize FLApplication."""

        self._dict_main_widgets = {}

        if self.container_ is None:
            raise Exception("init. self.container_ is empty")

        self.container_.setObjectName("container")
        self.container_.setWindowIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("pineboo.png")))
        if self.db() is not None:
            self.container_.setWindowTitle(self.db().mainConn().DBName())
        else:
            self.container_.setWindowTitle("Pineboo %s" % application.PROJECT.version)

        # FLDiskCache.init(self)

        self.window_menu = QtWidgets.QMenu(self.container_)
        self.window_menu.setObjectName("windowMenu")

        self.window_cascade_action = QtWidgets.QAction(
            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("cascada.png")),
            self.tr("Cascada"),
            self.container_,
        )
        self.window_menu.addAction(self.window_cascade_action)

        self.window_tile_action = QtWidgets.QAction(
            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("mosaico.png")),
            self.tr("Mosaico"),
            self.container_,
        )
        self.window_menu.addAction(self.window_tile_action)

        self.window_close_action = QtWidgets.QAction(
            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("cerrar.png")),
            self.tr("Cerrar"),
            self.container_,
        )
        self.window_menu.addAction(self.window_close_action)

        self.modules_menu = QtWidgets.QMenu(self.container_)
        self.modules_menu.setObjectName("modulesMenu")
        # self.modules_menu.setCheckable(False)

        widget = QtWidgets.QWidget(self.container_)
        widget.setObjectName("widgetContainer")
        vbox_layout = QtWidgets.QVBoxLayout(widget)

        self.exit_button = QtWidgets.QPushButton(
            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("exit.png")), self.tr("Salir"), widget
        )
        self.exit_button.setObjectName("pbSalir")
        self.exit_button.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Q")))
        self.exit_button.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        )
        self.exit_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.exit_button.setToolTip(self.tr("Salir de la aplicación (Ctrl+Q)"))
        self.exit_button.setWhatsThis(self.tr("Salir de la aplicación (Ctrl+Q)"))
        self.exit_button.clicked.connect(self.exit_button_clicked)

        self.tool_box_ = QtWidgets.QToolBox(widget)
        self.tool_box_.setObjectName("toolBox")

        vbox_layout.addWidget(self.exit_button)
        vbox_layout.addWidget(self.tool_box_)
        self.container_.setCentralWidget(widget)

        self.db().manager().init()

        application.PROJECT.aq_app.initStyles()
        self.initMenuBar()

        self.db().manager().loadTables()
        self.db().managerModules().loadKeyFiles()
        self.db().managerModules().loadAllIdModules()
        self.db().managerModules().loadIdAreas()

        # self.acl_ = pnaccesscontrollists.PNAccessControlLists()
        # self.acl_.init()

        # self.loadScripts()
        self.db().managerModules().setShaLocalFromGlobal()
        # application.PROJECT.aq_app.loadTranslations()

        application.PROJECT.call("sys.init", [])
        self.initToolBox()
        self.readState()

        self.container_.installEventFilter(self)
        application.PROJECT.aq_app.startTimerIdle()

    def exit_button_clicked(self):
        """Event when exit button is clicked. Closes the container."""
        if self.generalExit(True):
            self.is_closing_ = True
            self.close()

    def initMenuBar(self) -> None:
        """Initialize menus."""
        if self.window_menu is None:
            raise Exception("initMenuBar. self.window_menu is empty!")

        cast(QtCore.pyqtSignal, self.window_menu.aboutToShow).connect(self.windowMenuAboutToShow)

    def initToolBar(self) -> None:
        """Initialize toolbar."""

        if application.PROJECT.aq_app.main_widget_ is None:
            return

        menu_bar = (
            application.PROJECT.aq_app.main_widget_.menuBar()  # type: ignore [attr-defined] # noqa: F821
        )
        if menu_bar is None:
            LOGGER.warning(
                "No se encuentra toolbar en %s",
                application.PROJECT.aq_app.main_widget_.objectName(),
            )
            return

        # tb.setMovingEnabled(False)

        menu_bar.addSeparator()
        # what_this_button = QWhatsThis(tb)

        if not self.toogle_bars_:
            self.toogle_bars_ = QtWidgets.QMenu(self.container_)
            self.toogle_bars_.setObjectName("toggleBars")
            # self.toogle_bars_.setCheckable(True)

            # ag = QtWidgets.QActionGroup(self.container_)
            # ag.setObjectName("agToggleBars")

            tools_action = QtWidgets.QAction(self.tr("Barra de Herramientas"), self.container_)
            tools_action.setObjectName("Herramientas")
            tools_action.setCheckable(True)
            tools_action.setChecked(True)
            tools_action.triggered.connect(self.toggleToolBar)
            self.toogle_bars_.addAction(tools_action)

            status_action = QtWidgets.QAction(self.tr("Barra de Estado"), self.container_)
            status_action.setObjectName("Estado")
            status_action.setCheckable(True)
            status_action.setChecked(True)
            status_action.triggered.connect(self.toggleStatusBar)
            self.toogle_bars_.addAction(status_action)

            application.PROJECT.aq_app.main_widget_.menuBar().addMenu(  # type: ignore [attr-defined] # noqa: F821
                self.toogle_bars_
            )

        view_action = application.PROJECT.aq_app.main_widget_.menuBar().addMenu(  # type: ignore [attr-defined] # noqa: F821
            self.toogle_bars_
        )
        view_action.setText(self.tr("&Ver"))

        modules_action = application.PROJECT.aq_app.main_widget_.menuBar().addMenu(  # type: ignore [attr-defined] # noqa: F821
            self.modules_menu
        )
        modules_action.setText(self.tr("&Módulos"))

    def windowMenuAboutToShow(self) -> None:
        """Signal called before window menu is shown."""
        if not self._p_work_space:
            return
        if self.window_menu is None:
            return
        self.window_menu.clear()
        self.window_menu.addAction(self.window_cascade_action)
        self.window_menu.addAction(self.window_tile_action)
        self.window_menu.addAction(self.window_close_action)

        if not self._p_work_space.subWindowList():
            self.window_cascade_action.setEnabled(False)
            self.window_tile_action.setEnabled(False)
            self.window_close_action.setEnabled(False)
        else:
            self.window_cascade_action.setEnabled(True)
            self.window_tile_action.setEnabled(True)
            self.window_close_action.setEnabled(True)
            self.window_menu.addSeparator()

        for window in self._p_work_space.subWindowList():
            action = self.window_menu.addAction(window.windowTitle())
            action.setCheckable(True)

            if window == self._p_work_space.activeSubWindow():
                action.setChecked(True)

            action.triggered.connect(window.setFocus)

    def windowMenuActivated(self, id) -> None:
        """Signal called when user clicks on menu."""
        if not self._p_work_space:
            return

        window_list_ = self._p_work_space.subWindowList()
        if window_list_:
            window_list_[id].setFocus()

    def existFormInMDI(self, form_name: str) -> bool:
        """Return if named FLFormDB is open."""
        if form_name is None or not self._p_work_space:
            return False

        for window in self._p_work_space.subWindowList():
            if window.findChild(flformdb.FLFormDB).idMDI() == form_name:
                window.showNormal()
                window.setFocus()
                return True

        return False

    def windowClose(self) -> None:
        """Signal called on close."""
        if self._p_work_space is None:
            return

        self._p_work_space.closeActiveSubWindow()

    def workspace(self) -> Any:
        """Get current workspace."""
        return self._p_work_space

    def initToolBox(self) -> None:
        """Initialize toolbox."""

        main_widget = application.PROJECT.aq_app.main_widget_

        if main_widget is None:
            raise Exception("application.PROJECT.aq_app.main_widget_ is empty!")

        self.tool_box_ = cast(
            QtWidgets.QToolBox, main_widget.findChild(QtWidgets.QToolBox, "toolBox")
        )
        self.modules_menu = cast(
            QtWidgets.QMenu, main_widget.findChild(QtWidgets.QMenu, "modulesMenu")
        )

        if self.tool_box_ is None or self.modules_menu is None:
            return

        self.modules_menu.clear()
        for number in reversed(range(self.tool_box_.count())):
            item = self.tool_box_.widget(number)
            if isinstance(item, QtWidgets.QToolBar):
                item.clear()

            self.tool_box_.removeItem(number)

        for button in self.mdi_toolbuttons:
            self.mdi_toolbuttons.remove(button)

        del self.mdi_toolbuttons
        self.mdi_toolbuttons = []

        char_num = 65

        for it in self.db().managerModules().listIdAreas():
            descript_area = self.db().managerModules().idAreaToDescription(it)
            new_area_bar = QtWidgets.QToolBar(self.tr(descript_area), self.container_)
            new_area_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            # new_area_bar.setFrameStyle(QFrame.NoFrame)
            new_area_bar.setOrientation(QtCore.Qt.Vertical)
            new_area_bar.layout().setSpacing(3)
            self.tool_box_.addItem(new_area_bar, self.tr(descript_area))
            action_group = QtWidgets.QActionGroup(new_area_bar)
            action_group.setObjectName(descript_area)
            # ac = QtWidgets.QAction(ag)
            # ac.setText(descript_area)
            # ac.setUsesDropDown(True)

            list_modules = self.db().managerModules().listIdModules(it)
            list_modules.sort()

            for mod in list_modules:
                if str(chr(char_num)) == "Q":
                    char_num += 1
                    continue

                if mod == "sys":
                    if settings.CONFIG.value("application/isDebuggerMode", False):

                        descript_module = "%s: %s" % (
                            str(chr(char_num)),
                            self.tr("Carga Estática desde Disco Duro"),
                        )
                        new_module_action = QtWidgets.QAction(new_area_bar)
                        new_module_action.setObjectName("StaticLoadAction")
                        new_module_action.setText(self.tr(descript_module))
                        new_module_action.setShortcut(
                            getattr(QtCore.Qt, "Key_%s" % str(chr(char_num)))
                        )
                        new_module_action.setIcon(
                            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("folder_update.png"))
                        )
                        new_area_bar.addAction(new_module_action)
                        new_module_action.triggered.connect(
                            application.PROJECT.aq_app.staticLoaderSetup
                        )
                        action_group.addAction(new_module_action)
                        char_num += 1

                        descript_module = "%s: %s" % (
                            str(chr(char_num)),
                            self.tr("Reiniciar Script"),
                        )
                        new_module_action = QtWidgets.QAction(new_area_bar)
                        new_module_action.setObjectName("reinitScriptAction")
                        new_module_action.setText(self.tr(descript_module))
                        new_module_action.setShortcut(
                            getattr(QtCore.Qt, "Key_%s" % str(chr(char_num)))
                        )
                        new_module_action.setIcon(
                            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("reload.png"))
                        )
                        new_area_bar.addAction(new_module_action)
                        new_module_action.triggered.connect(application.PROJECT.aq_app.reinit)
                        action_group.addAction(new_module_action)
                        char_num += 1

                    descript_module = "%s: %s" % (
                        str(chr(char_num)),
                        self.tr("Mostrar Consola de mensajes"),
                    )
                    new_module_action = QtWidgets.QAction(new_area_bar)
                    new_module_action.setObjectName("shConsoleAction")
                    new_module_action.setText(self.tr(descript_module))
                    new_module_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(char_num))))
                    new_module_action.setIcon(
                        QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("consola.png"))
                    )
                    new_area_bar.addAction(new_module_action)
                    new_module_action.triggered.connect(application.PROJECT.aq_app.showConsole)
                    action_group.addAction(new_module_action)
                    char_num += 1

                descript_module = "%s: %s" % (
                    str(chr(char_num)),
                    self.db().managerModules().idModuleToDescription(mod),
                )
                new_module_action = QtWidgets.QAction(new_area_bar)
                new_module_action.setObjectName(mod)
                new_module_action.setText(self.tr(descript_module))
                new_module_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(char_num))))
                new_module_action.setIcon(QtGui.QIcon(self.db().managerModules().iconModule(mod)))
                new_area_bar.addAction(new_module_action)
                new_module_action.triggered.connect(self.activateModule)
                action_group.addAction(new_module_action)
                char_num += 1

            # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

            lay = new_area_bar.layout()
            for child in new_area_bar.children():
                if isinstance(child, QtWidgets.QToolButton):
                    self.mdi_toolbuttons.append(child)
                    lay.setAlignment(child, QtCore.Qt.AlignCenter)

            a_menu = self.modules_menu.addMenu(descript_area)
            for action in action_group.actions():
                a_menu.addAction(action)

        descript_area = "Configuración"
        config_tool_bar = QtWidgets.QToolBar(self.tr(descript_area), self.container_)
        config_tool_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        # config_tool_bar.setFrameStyle(QFrame.NoFrame)
        config_tool_bar.setOrientation(QtCore.Qt.Vertical)
        # config_tool_bar.layout().setSpacing(3)
        self.tool_box_.addItem(config_tool_bar, self.tr(descript_area))

        descript_module = self.tr("Fuente")
        font_action = QtWidgets.QAction(new_area_bar)
        font_action.setObjectName("fontAction")
        font_action.setText(self.tr(descript_module))
        # font_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        font_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("font.png")))
        config_tool_bar.addAction(font_action)
        font_action.triggered.connect(application.PROJECT.aq_app.chooseFont)
        action_group.addAction(font_action)

        descript_module = self.tr("Estilo")
        style_action = QtWidgets.QAction(new_area_bar)
        style_action.setObjectName("styleAction")
        style_action.setText(self.tr(descript_module))
        # style_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        style_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("estilo.png")))
        config_tool_bar.addAction(style_action)
        style_action.triggered.connect(application.PROJECT.aq_app.showStyles)
        action_group.addAction(style_action)

        descript_module = self.tr("Indice")
        help_action = QtWidgets.QAction(new_area_bar)
        help_action.setObjectName("helpAction")
        help_action.setText(self.tr(descript_module))
        # help_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        help_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("help_index.png")))
        config_tool_bar.addAction(help_action)
        help_action.triggered.connect(application.PROJECT.aq_app.helpIndex)
        action_group.addAction(help_action)

        descript_module = self.tr("Acerca de Pineboo")
        about_pineboo_action = QtWidgets.QAction(new_area_bar)
        about_pineboo_action.setObjectName("aboutPinebooAction")
        about_pineboo_action.setText(self.tr(descript_module))
        # help_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        about_pineboo_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("about.png")))
        config_tool_bar.addAction(about_pineboo_action)
        about_pineboo_action.triggered.connect(application.PROJECT.aq_app.aboutPineboo)
        action_group.addAction(about_pineboo_action)

        descript_module = self.tr("Visita Eneboo.org")
        visit_pineboo_action = QtWidgets.QAction(new_area_bar)
        visit_pineboo_action.setObjectName("visitPinebooAction")
        visit_pineboo_action.setText(self.tr(descript_module))
        # help_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        visit_pineboo_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("about.png")))
        config_tool_bar.addAction(visit_pineboo_action)
        visit_pineboo_action.triggered.connect(application.PROJECT.aq_app.urlPineboo)
        action_group.addAction(visit_pineboo_action)

        descript_module = self.tr("Acerca de Qt")
        about_qt_action = QtWidgets.QAction(new_area_bar)
        about_qt_action.setObjectName("aboutQtAction")
        about_qt_action.setText(self.tr(descript_module))
        # help_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        about_qt_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("aboutqt.png")))
        config_tool_bar.addAction(about_qt_action)
        about_qt_action.triggered.connect(application.PROJECT.aq_app.aboutQt)
        action_group.addAction(about_qt_action)

        lay = config_tool_bar.layout()
        for child in config_tool_bar.children():
            if isinstance(child, QtWidgets.QToolButton):
                self.mdi_toolbuttons.append(child)
                lay.setAlignment(child, QtCore.Qt.AlignCenter)

        if application.PROJECT.aq_app.acl_:
            application.PROJECT.aq_app.acl_.process(self.container_)

    def eventFilter(self, obj_, event) -> Any:
        """React to user events."""
        if self._inicializing or application.PROJECT.aq_app._destroying:
            return super().eventFilter(obj_, obj_)

        # if QtWidgets.QApplication.activeModalWidget() or QtWidgets.QApplication.activePopupWidget():
        #    return super().eventFilter(obj, event)

        event_type = event.type()
        main_widget = application.PROJECT.aq_app.main_widget_
        if obj_ != main_widget and not isinstance(obj_, QtWidgets.QMainWindow):
            return super().eventFilter(obj_, event)

        # aw = None
        # if self._p_work_space is not None:
        #    aw = QtWidgets.QApplication.setActiveWindow(self._p_work_space)
        # if aw is not None and aw != obj and event_type not in (QEvent.Resize, QEvent.Close):
        #     obj.removeEventFilter(self)
        #     if event_type == QEvent.WindowActivate:
        #         if obj == self.container_:
        #             self.activateModule(None)
        #         else:
        #             self.activateModule(obj.objectName())
        #
        #     if self._p_work_space and self.notify(self._p_work_space, ev):
        #         obj.installEventFilter(self)
        #         return True
        #
        #     obj.installEventFilter(self)

        if event_type == QtCore.QEvent.KeyPress:
            if obj_ == self.container_:
                key_ = event

            elif obj_ == main_widget:
                key_ = event
                if key_.key() == QtCore.Qt.Key_Shift and (key_.state() == QtCore.Qt.Key_Control):
                    self.activateModule(None)
                    return True
                elif key_.key() == QtCore.Qt.Key_Q and (key_.state() == QtCore.Qt.Key_Control):
                    self.generalExit()
                    return True
                elif key_.key() == QtCore.Qt.Key_W and (
                    key_.state() in (QtCore.Qt.Key_Control, QtCore.Qt.Key_Alt)
                ):
                    LOGGER.warning("unknown key presset!.")
                    return True
                elif key_.key() == QtCore.Qt.Key_Escape:
                    obj_.hide()
                    return True

        elif event_type == QtCore.QEvent.Close:
            if obj_ is self and not self.is_closing_:
                ret = self.generalExit()
                if not ret:
                    obj_.setDisabled(False)
                    event.ignore()

            return True

        elif event_type == QtCore.QEvent.WindowActivate:
            if obj_ == self.container_:
                self.activateModule(None)
                return True
            else:
                self.activateModule(obj_.objectName())
                return True

        # elif event_type == QtCore.QEvent.MouseButtonPress:
        #    if self.modules_menu:
        #        me = ev
        #        if me.button() == QtCore.Qt.RightButton:
        #            self.modules_menu.pop(QtGui.QCursor.pos())
        #            return True
        #        else:
        #            return False
        #    else:
        #        return False

        elif event_type == QtCore.QEvent.Resize and obj_ is self:
            for tool_button in self.mdi_toolbuttons:
                tool_button.setMinimumWidth(obj_.width() - 10)

            return True

        return super().eventFilter(obj_, event)

    def activateModule(self, idm=None) -> None:
        """Initialize module."""

        if not idm:
            if self.sender():
                idm = self.sender().objectName()

        if idm is None:
            return

        self.writeStateModule()

        w = None
        if idm in self.db().managerModules().listAllIdModules():
            w = self._dict_main_widgets[idm] if idm in self._dict_main_widgets.keys() else None
            if w is None:
                w = self.db().managerModules().createUI(file_name="%s.ui" % idm)
                if not w:
                    return

                if w.findChild(pncore.PNCore):
                    doc = QtXml.QDomDocument()
                    ui_file = "%s.ui" % idm
                    cc = self.db().managerModules().contentCached(ui_file)
                    if not cc or not doc.setContent(cc):
                        if cc:
                            LOGGER.warning("No se ha podido cargar %s" % (ui_file))
                            return None

                    root = doc.documentElement().toElement()
                    conns = root.namedItem("connections").toElement()
                    connections = conns.elementsByTagName("connection")
                    for i in range(connections.length()):
                        itn = connections.at(i).toElement()
                        sender = itn.namedItem("sender").toElement().text()
                        signal = itn.namedItem("signal").toElement().text()
                        if signal in ["activated()", "triggered()"]:
                            signal = "triggered()"
                        receiver = itn.namedItem("receiver").toElement().text()
                        slot = itn.namedItem("slot").toElement().text()
                        if receiver == "pncore" and signal == "triggered()":
                            ac = cast(QtWidgets.QAction, w.findChild(QtWidgets.QAction, sender))
                            if ac is not None and sender in application.PROJECT.actions.keys():
                                sl = getattr(
                                    application.PROJECT.actions[sender],
                                    slot[0 : slot.find("(")],
                                    None,
                                )
                                ac.triggered.connect(sl)
                            else:
                                LOGGER.warning("Action %s not found", sender)

                w.setWindowModality(QtCore.Qt.WindowModal)
                self._dict_main_widgets[idm] = w
                w.setObjectName(idm)
                if application.PROJECT.aq_app.acl_:
                    application.PROJECT.aq_app.acl_.process(w)

                self.setMainWidget(w)
                application.PROJECT.aq_app.call("%s.init()" % idm, [])
                w.removeEventFilter(self)
                self.db().managerModules().setActiveIdModule(idm)
                self.setMainWidget(w)
                self.initMainWidget()
                self.showMainWidget(w)
                w.installEventFilter(self)
                return

        if not w:
            self.db().managerModules().setActiveIdModule("")
        else:
            self.db().managerModules().setActiveIdModule(idm)

        self.setMainWidget(w)
        self.showMainWidget(w)

    def writeState(self) -> None:
        """Write settings back to disk."""

        settings.SETTINGS.set_value("MultiLang/Enabled", self._multi_lang_enabled)
        settings.SETTINGS.set_value("MultiLang/LangId", self._multi_lang_id)

        if self.container_ is not None:
            windows_opened = []
            _list = QtWidgets.QApplication.topLevelWidgets()

            if self._inicializing:
                for it in _list:
                    it.removeEventFilter(self)
                    if it.objectName() in self._dict_main_widgets.keys():
                        if it != self.container_:
                            if it.isVisible():
                                windows_opened.append(it.objectName())
                            it.hide()
                        else:
                            it.setDisabled(True)
            else:
                for it in _list:
                    if (
                        it != self.container_
                        and it.isVisible()
                        and it.objectName() in self._dict_main_widgets.keys()
                    ):
                        windows_opened.append(it.objectName())

            settings.SETTINGS.set_value("windowsOpened/Main", windows_opened)
            settings.SETTINGS.set_value(
                "Geometry/MainWindowMaximized", self.container_.isMaximized()
            )
            if not self.container_.isMaximized():
                settings.SETTINGS.set_value("Geometry/MainWindowX", self.container_.x())
                settings.SETTINGS.set_value("Geometry/MainWindowY", self.container_.y())
                settings.SETTINGS.set_value("Geometry/MainWindowWidth", self.container_.width())
                settings.SETTINGS.set_value("Geometry/MainWindowHeight", self.container_.height())

        for map in self._map_geometry_form:  # FIXME esto no se rellena nunca
            k = "Geometry/%s/" % map.key()
            settings.SETTINGS.set_value("%s/X" % k, map.x())
            settings.SETTINGS.set_value("%s/Y" % k, map.y())
            settings.SETTINGS.set_value("%s/Width" % k, map.width())
            settings.SETTINGS.set_value("%s/Height" % k, map.height())

    def writeStateModule(self) -> None:
        """Write settings for modules."""

        idm = self.db().managerModules().activeIdModule()
        if not idm:
            return

        main_widget = application.PROJECT.aq_app.main_widget_

        if main_widget is None or main_widget.objectName() != idm:
            return

        windows_opened: List[str] = []
        if main_widget is not None and self._p_work_space is not None:
            for w in self._p_work_space.subWindowList():
                s = w.findChild(QtWidgets.QDialog)
                if s is not None:
                    windows_opened.append(s.idMDI())

        settings.SETTINGS.set_value("windowsOpened/%s" % idm, windows_opened)

        k = "Geometry/%s" % idm
        settings.SETTINGS.set_value("%s/Maximized" % k, main_widget.isMaximized())
        settings.SETTINGS.set_value("%s/X" % k, main_widget.x())
        settings.SETTINGS.set_value("%s/Y" % k, main_widget.y())
        settings.SETTINGS.set_value("%s/Width" % k, main_widget.width())
        settings.SETTINGS.set_value("%s/Height" % k, main_widget.height())

    def readState(self) -> None:
        """Read settings."""
        self._inicializing = False
        self._dict_main_widgets = {}

        if self.container_:
            r = QtCore.QRect(self.container_.pos(), self.container_.size())
            self._multi_lang_enabled = settings.SETTINGS.value("MultiLang/Enabled", False)
            self._multi_lang_id = settings.SETTINGS.value(
                "MultiLang/LangId", QtCore.QLocale().name()[:2].upper()
            )

            if not settings.SETTINGS.value("Geometry/MainWindowMaximized", False):
                r.setX(settings.SETTINGS.value("Geometry/MainWindowX", r.x()))
                r.setY(settings.SETTINGS.value("Geometry/MainWindowY", r.y()))
                r.setWidth(settings.SETTINGS.value("Geometry/MainWindowWidth", r.width()))
                r.setHeight(settings.SETTINGS.value("Geometry/MainWindowHeight", r.height()))

                desk = QtWidgets.QApplication.desktop().availableGeometry(self.container_)
                inter = desk.intersected(r)
                self.container_.resize(r.size())
                if inter.width() * inter.height() > (r.width() * r.height() / 20):
                    self.container_.move(r.topLeft())

            else:
                self.container_.resize(
                    QtWidgets.QApplication.desktop().availableGeometry(self.container_).size()
                )

            active_id_module = self.db().managerModules().activeIdModule()

            windows_opened = settings.SETTINGS.value("windowsOpened/Main", [])

            for id_module in windows_opened:
                if id_module in self.db().managerModules().listAllIdModules():
                    w = None
                    if id_module in self._dict_main_widgets.keys():
                        w = self._dict_main_widgets[id_module]
                    if w is None:
                        act = cast(
                            QtWidgets.QAction,
                            self.container_.findChild(QtWidgets.QAction, id_module),
                        )
                        if not act or not act.isVisible():
                            continue

                        self.activateModule(id_module)
                        # w = self.db().managerModules().createUI("%s.ui" % it)
                        # self._dict_main_widgets[it] = w

                        w = self._dict_main_widgets[id_module]
                        w.setObjectName(id_module)
                        if application.PROJECT.aq_app.acl_:
                            application.PROJECT.aq_app.acl_.process(w)

                        self.setCaptionMainWidget(None)
                        self.setMainWidget(w)
                        application.PROJECT.aq_app.call("%s.init()" % id_module, [])
                        self.db().managerModules().setActiveIdModule(id_module)
                        self.setMainWidget(w)
                        self.initMainWidget()

            for k in self._dict_main_widgets.keys():
                w = self._dict_main_widgets[k]
                if w.objectName() != active_id_module:
                    w.installEventFilter(self)
                    w.show()
                    w.setFont(QtWidgets.QApplication.font())
                    if not isinstance(w, QtWidgets.QMainWindow):
                        continue

                    view_back = w.centralWidget()
                    if view_back is not None:
                        self._p_work_space = view_back.findChild(QtWidgets.QWidget, w.objectName())

            if active_id_module:
                self.container_.show()
                self.container_.setFont(self.font())

            self.activateModule(active_id_module)

    def readStateModule(self) -> None:
        """Read settings for module."""

        idm = self.db().managerModules().activeIdModule()
        if not idm:
            return

        main_widget = application.PROJECT.aq_app.main_widget_

        if main_widget is None or main_widget.objectName() != idm:
            return

        # FIXME: restore opened windows
        # windows_opened = settings.SETTINGS.value("windowsOpened/%s" % idm, None)
        # if windows_opened:
        #    for it in windows_opened:
        #        act = cast(QtWidgets.QAction, main_widget.findChild(QtWidgets.QAction, it))
        #        if act and act.isVisible():
        # application.PROJECT.aq_app.openMasterForm(it, act.icon())
        #            application.PROJECT.aq_app.openMasterForm(it)

        r = QtCore.QRect(main_widget.pos(), main_widget.size())
        k = "Geometry/%s" % idm
        if not settings.SETTINGS.value("%s/Maximized" % k, False):
            r.setX(settings.SETTINGS.value("%s/X" % k, r.x()))
            r.setY(settings.SETTINGS.value("%s/Y" % k, r.y()))
            r.setWidth(settings.SETTINGS.value("%s/Width" % k, r.width()))
            r.setHeight(settings.SETTINGS.value("%s/Height" % k, r.height()))
            desk = QtWidgets.QApplication.desktop().availableGeometry(main_widget)
            inter = desk.intersected(r)
            main_widget.resize(r.size())
            if (inter.width() * inter.height()) - 100 > (r.width() * r.height()):
                main_widget.move(r.topLeft())
            else:
                main_widget.hide()
                main_widget.resize(
                    QtWidgets.QApplication.desktop().availableGeometry(main_widget).size()
                )
                main_widget.show()

    def __del__(self) -> None:
        """Cleanup."""
        self._destroying = True
        application.PROJECT.aq_app.stopTimerIdle()
        # self.checkAndFixTransactionLAvel("%s:%s" % (__name__, __class__))
        # app_db = self.db()
        # if app_db:
        #     app_db.setInteractiveGUI(False)
        #     app_db.setQsaExceptions(False)

        if self._dict_main_widgets:
            for mw in self._dict_main_widgets:

                del mw
            del self._dict_main_widgets
            self._dict_main_widgets = {}

        # self.clearProject()
        # self.project_ = None
        self._ted_output = None

        # if app_db:
        #     app_db.finish()
        self.aqApp = None

    def initView(self) -> None:
        """Initialize view."""
        mw = cast(QtWidgets.QMainWindow, application.PROJECT.aq_app.main_widget_)
        if mw is None:
            return

        view_back = mw.centralWidget()
        if not isinstance(view_back, QtWidgets.QMdiArea):

            view_back = QtWidgets.QMdiArea()
            view_back.setObjectName("mdi_area")
            view_back.setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            # view_back.logo = pixmap_fromMimeSource("pineboo-logo.png")
            # view_back.logo = aqs.AQS.pixmap_fromMimeSource("pineboo-logo.png")
            view_back.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            view_back.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            self._p_work_space = flworkspace.FLWorkSpace(
                view_back, self.db().managerModules().activeIdModule()
            )
            self._p_work_space.setAttribute(QtCore.Qt.WA_NoSystemBackground)
            # p_work_space.setScrollBarsEnabled(True)
            # FIXME: setScrollBarsEnabled
            mw.setCentralWidget(view_back)

    def setMainWidget(self, w) -> None:
        """Set mainWidget."""
        if not self.container_:
            return

        # if w == self.container_ or w is None:
        #    QtWidgets.QApplication.setActiveWindow(self.container_)
        #    application.PROJECT.aq_app.main_widget_ = None
        #    return

        application.PROJECT.aq_app.setMainWidget(w)
        # QtWidgets.QApplication.setActiveWindow(w)
        # application.PROJECT.aq_app.main_widget_ = w

        mw = (
            application.PROJECT.aq_app.main_widget_
            if isinstance(application.PROJECT.aq_app.main_widget_, QtWidgets.QMainWindow)
            else None
        )

        if mw is None:
            return

        if self.toogle_bars_:
            tool_bar = cast(QtWidgets.QToolBar, mw.findChild(QtWidgets.QToolBar))
            for ac in self.toogle_bars_.actions():
                if ac.objectName() == "Herramientas":
                    a = ac
                elif ac.objectName() == "Estado":
                    b = ac

            if tool_bar:
                a.setChecked(tool_bar.isVisible())

            b.setChecked(mw.statusBar().isVisible())

    def showMainWidget(self, w) -> None:
        """Show UI."""

        if not self.container_:
            if w:
                w.show()
            return

        focus_w = QtWidgets.QApplication.focusWidget()
        if w is self.container_ or not w:
            if self.container_.isMinimized():
                self.container_.showNormal()
            elif not self.container_.isVisible():
                self.container_.setFont(self.font())
                self.container_.show()

            if (
                focus_w
                and isinstance(focus_w, QtWidgets.QMainWindow)
                and focus_w != self.container_
            ):
                self.container_.setFocus()

            if not self.container_.isActiveWindow():
                self.container_.raise_()
                QtWidgets.QApplication.setActiveWindow(self.container_)

            if self.db() is not None:
                self.container_.setWindowTitle(self.db().mainConn().DBName())
            else:
                self.container_.setWindowTitle("Pineboo %s" % application.PROJECT.version)

            return

        if w.isMinimized():
            w.showNormal()
        elif not w.isVisible():
            w.show()
            w.setFont(QtWidgets.QApplication.font())

        if focus_w and isinstance(focus_w, QtWidgets.QMainWindow) and focus_w != w:
            w.setFocus()
        if not w.isActiveWindow():
            w.raise_()
            QtWidgets.QApplication.setActiveWindow(w)

        if w:
            view_back = w.centralWidget()
            if view_back:
                self._p_work_space = view_back.findChild(flworkspace.FLWorkSpace, w.objectName())
                view_back.show()

        self.setCaptionMainWidget(None)
        descript_area = (
            self.db()
            .managerModules()
            .idAreaToDescription(self.db().managerModules().activeIdArea())
        )
        w.setWindowIcon(QtGui.QIcon(self.db().managerModules().iconModule(w.objectName())))
        self.tool_box_.setCurrentIndex(
            self.tool_box_.indexOf(self.tool_box_.findChild(QtWidgets.QToolBar, descript_area))
        )

    def initMainWidget(self) -> None:
        """Init mainwidget UI."""
        mw = cast(QtWidgets.QMainWindow, application.PROJECT.aq_app.main_widget_)
        if not mw or not self.container_:
            return

        if mw:
            ac = mw.menuBar().addMenu(self.window_menu)
            ac.setText(self.tr("&Ventana"))
            # mw.setCentralWidget(None)

        self.initView()
        self.initActions()
        self.initToolBar()
        self.initStatusBar()

        self.readStateModule()

    def setCaptionMainWidget(self, value) -> None:
        """Set application title."""
        if value:
            self.last_text_caption_ = value

        main_widget = application.PROJECT.aq_app.main_widget_

        if main_widget:
            descript_area = (
                self.db()
                .managerModules()
                .idAreaToDescription(self.db().managerModules().activeIdArea())
            )
            descript_module = self.db().managerModules().idModuleToDescription(self.objectName())

            if descript_area:
                main_widget.setWindowTitle(
                    "%s - %s - %s" % (self.last_text_caption_, descript_area, descript_module)
                )

    def initActions(self) -> None:
        """Initialize actions."""
        if application.PROJECT.aq_app.main_widget_ is not None and self._p_work_space is not None:
            self.window_cascade_action.triggered.connect(self._p_work_space.cascadeSubWindows)
            self.window_tile_action.triggered.connect(self._p_work_space.tileSubWindows)
            self.window_close_action.triggered.connect(self._p_work_space.closeActiveSubWindow)

    def initStatusBar(self) -> None:
        """Initialize statusbar."""
        mw = application.PROJECT.aq_app.main_widget_

        if not mw:
            return

        application.PROJECT.aq_app.statusHelpMsg(self.tr("Listo."))

        if mw is not None:
            status_bar = cast(QtWidgets.QMainWindow, mw).statusBar()
            status_bar.setSizeGripEnabled(False)

            conexion = QtWidgets.QLabel(status_bar)
            conexion.setText("%s@%s" % (self.db().user(), self.db().DBName()))
            status_bar.addWidget(conexion)

    def toggleToolBar(self, toggle: bool) -> None:
        """Show or hide toolbar."""
        mw = cast(QtWidgets.QToolBar, application.PROJECT.aq_app.main_widget_)

        if not mw:
            return

        tb = cast(QtWidgets.QToolBar, mw.findChild(QtWidgets.QToolBar))

        if not tb:
            return

        if toggle:
            tb.show()
        else:
            tb.hide()

    def toggleStatusBar(self, toggle: bool) -> None:
        """Toggle status bar."""
        mw = cast(QtWidgets.QMainWindow, application.PROJECT.aq_app.main_widget_)
        if not mw:
            return
        if toggle:
            mw.statusBar().show()
        else:
            mw.statusBar().hide()

    def generalExit(self, ask_exit=True) -> bool:
        """Perform before close checks."""
        do_exit = True
        if ask_exit:
            do_exit = application.PROJECT.aq_app.queryExit()
        if do_exit:
            self._destroying = True
            if application.PROJECT.aq_app.consoleShown():
                if application.PROJECT.aq_app._ted_output is not None:
                    application.PROJECT.aq_app._ted_output.close()

            if not application.PROJECT.aq_app.form_alone_:
                self.writeState()
                self.writeStateModule()

            if self.db().driverName():
                self.db().managerModules().finish()
                self.db().manager().finish()
                # QtCore.QTimer.singleShot(0, application.PROJECT.aq_app.quit)

            for mw in self._dict_main_widgets.values():
                mw.close()

            return True
        else:

            return False


mainWindow: MainForm
# mainWindow = MainForm()
