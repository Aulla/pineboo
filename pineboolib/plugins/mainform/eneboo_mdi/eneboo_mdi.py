"""Eneboo_mdi module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets, QtGui, QtCore, QtXml  # type: ignore[import]

from pineboolib.core.utils import utils_base
from pineboolib.core import settings

from pineboolib.application.acls import pnaccesscontrollists

from pineboolib.fllegacy.aqsobjects import aqs
from pineboolib.fllegacy import flworkspace, flformdb
from pineboolib.application import pncore
from pineboolib import application
from pineboolib import logging
from pineboolib.interfaces import imainwindow
from pineboolib.q3widgets import qmainwindow


from typing import Any, cast, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.database import pnconnectionmanager  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class MainForm(imainwindow.IMainWindow):
    """MainForm class."""

    acl_: pnaccesscontrollists.PNAccessControlLists
    is_closing_: bool
    mdi_enable_: bool

    main_window: QtWidgets.QMainWindow
    exit_button: QtWidgets.QPushButton

    mdi_toolbuttons: List[QtWidgets.QToolButton]

    tool_box_: Any
    toogle_bars_: Any
    last_text_caption_: str
    _map_geometry_form: List[Any]

    def __init__(self) -> None:
        """Inicialize."""
        super().__init__()
        self._p_work_space = None
        self.main_widget = self
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
        # application.PROJECT.aq_app.startTimerIdle()
        # self.tool_box = None
        # self.modules_menu = None

        if self._dict_main_widgets:
            self._dict_main_widgets = {}

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
            self.container_.setWindowTitle("Pineboo %s" % application.PROJECT.load_version())

        # FLDiskCache.init(self)

        self.window_menu = QtWidgets.QMenu(self.container_)
        self.window_menu.setObjectName("windowMenu")

        self.window_cascade_action = QtGui.QAction(
            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("cascada.png")),
            self.tr("Cascada"),
            self.container_,
        )
        self.window_menu.addAction(self.window_cascade_action)

        self.window_tile_action = QtGui.QAction(
            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("mosaico.png")),
            self.tr("Mosaico"),
            self.container_,
        )
        self.window_menu.addAction(self.window_tile_action)

        self.window_close_action = QtGui.QAction(
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
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
            )
        )
        self.exit_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.exit_button.setToolTip(self.tr("Salir de la aplicación (Ctrl+Q)"))
        self.exit_button.setWhatsThis(self.tr("Salir de la aplicación (Ctrl+Q)"))
        self.exit_button.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
            self.exit_button_clicked
        )

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

        cast(
            QtCore.pyqtSignal, self.window_menu.aboutToShow
        ).connect(  # type: ignore [attr-defined] # noqa: F821
            self.windowMenuAboutToShow
        )

    def initToolBar(self) -> None:
        """Initialize toolbar."""

        if self.main_widget is None:
            return

        menu_bar = self.main_widget.menuBar()  # type: ignore [attr-defined] # noqa: F821
        if menu_bar is None:
            LOGGER.warning("No se encuentra toolbar en %s", self.main_widget.objectName())
            return

        # tb.setMovingEnabled(False)

        menu_bar.addSeparator()
        # what_this_button = QWhatsThis(tb)

        if not self.toogle_bars_:
            self.toogle_bars_ = QtWidgets.QMenu(self.container_)
            self.toogle_bars_.setObjectName("toggleBars")
            # self.toogle_bars_.setCheckable(True)

            # ag = QtGui.QActionGroup(self.container_)
            # ag.setObjectName("agToggleBars")

            tools_action = QtGui.QAction(self.tr("Barra de Herramientas"), self.container_)
            tools_action.setObjectName("Herramientas")
            tools_action.setCheckable(True)
            tools_action.setChecked(True)
            tools_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                self.toggleToolBar
            )
            self.toogle_bars_.addAction(tools_action)

            status_action = QtGui.QAction(self.tr("Barra de Estado"), self.container_)
            status_action.setObjectName("Estado")
            status_action.setCheckable(True)
            status_action.setChecked(True)
            status_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                self.toggleStatusBar
            )
            self.toogle_bars_.addAction(status_action)

            self.main_widget.menuBar().addMenu(  # type: ignore [attr-defined] # noqa: F821
                self.toogle_bars_
            )

        view_action = self.main_widget.menuBar().addMenu(  # type: ignore [attr-defined] # noqa: F821
            self.toogle_bars_
        )
        view_action.setText(self.tr("&Ver"))

        modules_action = self.main_widget.menuBar().addMenu(  # type: ignore [attr-defined] # noqa: F821
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

        state = True if self._p_work_space.subWindowList() else False
        self.window_cascade_action.setEnabled(state)
        self.window_tile_action.setEnabled(state)
        self.window_close_action.setEnabled(state)
        if state:
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

        self.tool_box_ = cast(QtWidgets.QToolBox, self.findChild(QtWidgets.QToolBox, "toolBox"))
        self.modules_menu = cast(QtWidgets.QMenu, self.findChild(QtWidgets.QMenu, "modulesMenu"))

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

        for id_area in self.db().managerModules().listIdAreas():
            descript_area = self.db().managerModules().idAreaToDescription(id_area)
            new_area_bar = QtWidgets.QToolBar(self.tr(descript_area), self.container_)
            new_area_bar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            # new_area_bar.setFrameStyle(QFrame.NoFrame)
            new_area_bar.setOrientation(QtCore.Qt.Orientation.Vertical)
            new_area_bar.layout().setSpacing(3)
            self.tool_box_.addItem(new_area_bar, self.tr(descript_area))
            action_group = QtGui.QActionGroup(new_area_bar)
            action_group.setObjectName(descript_area)
            # ac = QtGui.QAction(ag)
            # ac.setText(descript_area)
            # ac.setUsesDropDown(True)

            list_modules = self.db().managerModules().listIdModules(id_area)
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
                        new_module_action = QtGui.QAction(new_area_bar)
                        new_module_action.setObjectName("StaticLoadAction")
                        new_module_action.setText(self.tr(descript_module))
                        new_module_action.setShortcut(
                            getattr(QtCore.Qt.Key, "Key_%s" % str(chr(char_num))).value
                        )
                        new_module_action.setIcon(
                            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("folder_update.png"))
                        )
                        new_area_bar.addAction(new_module_action)
                        new_module_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                            application.PROJECT.aq_app.staticLoaderSetup
                        )
                        action_group.addAction(new_module_action)
                        char_num += 1

                        descript_module = "%s: %s" % (
                            str(chr(char_num)),
                            self.tr("Reiniciar Script"),
                        )
                        new_module_action = QtGui.QAction(new_area_bar)
                        new_module_action.setObjectName("reinitScriptAction")
                        new_module_action.setText(self.tr(descript_module))
                        new_module_action.setShortcut(
                            getattr(QtCore.Qt.Key, "Key_%s" % str(chr(char_num))).value
                        )
                        new_module_action.setIcon(
                            QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("reload.png"))
                        )
                        new_area_bar.addAction(new_module_action)
                        new_module_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                            application.PROJECT.aq_app.reinit
                        )
                        action_group.addAction(new_module_action)
                        char_num += 1

                    descript_module = "%s: %s" % (
                        str(chr(char_num)),
                        self.tr("Mostrar Consola de mensajes"),
                    )
                    new_module_action = QtGui.QAction(new_area_bar)
                    new_module_action.setObjectName("shConsoleAction")
                    new_module_action.setText(self.tr(descript_module))
                    new_module_action.setShortcut(
                        getattr(QtCore.Qt.Key, "Key_%s" % str(chr(char_num))).value
                    )
                    new_module_action.setIcon(
                        QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("consola.png"))
                    )
                    new_area_bar.addAction(new_module_action)
                    new_module_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                        application.PROJECT.aq_app.showConsole
                    )
                    action_group.addAction(new_module_action)
                    char_num += 1

                descript_module = "%s: %s" % (
                    str(chr(char_num)),
                    self.db().managerModules().idModuleToDescription(mod),
                )
                new_module_action = QtGui.QAction(new_area_bar)
                new_module_action.setObjectName(mod)
                new_module_action.setText(self.tr(descript_module))
                new_module_action.setShortcut(
                    getattr(QtCore.Qt.Key, "Key_%s" % str(chr(char_num))).value
                )
                new_module_action.setIcon(QtGui.QIcon(self.db().managerModules().iconModule(mod)))
                new_area_bar.addAction(new_module_action)
                new_module_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.activateModule
                )
                action_group.addAction(new_module_action)
                char_num += 1

            # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)

            lay = new_area_bar.layout()
            for child in new_area_bar.children():
                if isinstance(child, QtWidgets.QToolButton):
                    self.mdi_toolbuttons.append(child)
                    lay.setAlignment(child, QtCore.Qt.AlignmentFlag.AlignCenter)

            a_menu = self.modules_menu.addMenu(descript_area)
            for action in action_group.actions():
                a_menu.addAction(action)

        descript_area = "Configuración"
        config_tool_bar = QtWidgets.QToolBar(self.tr(descript_area), self.container_)
        config_tool_bar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        # config_tool_bar.setFrameStyle(QFrame.NoFrame)
        config_tool_bar.setOrientation(QtCore.Qt.Orientation.Vertical)
        # config_tool_bar.layout().setSpacing(3)
        self.tool_box_.addItem(config_tool_bar, self.tr(descript_area))

        descript_module = self.tr("Fuente")
        font_action = QtGui.QAction(config_tool_bar)
        font_action.setObjectName("fontAction")
        font_action.setText(self.tr(descript_module))
        # font_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        font_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("font.png")))
        config_tool_bar.addAction(font_action)
        font_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
            application.PROJECT.aq_app.chooseFont
        )

        descript_module = self.tr("Estilo")
        style_action = QtGui.QAction(config_tool_bar)
        style_action.setObjectName("styleAction")
        style_action.setText(self.tr(descript_module))
        # style_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        style_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("estilo.png")))
        config_tool_bar.addAction(style_action)
        style_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
            application.PROJECT.aq_app.showStyles
        )

        descript_module = self.tr("Indice")
        help_action = QtGui.QAction(config_tool_bar)
        help_action.setObjectName("helpAction")
        help_action.setText(self.tr(descript_module))
        # help_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        help_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("help_index.png")))
        config_tool_bar.addAction(help_action)
        help_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
            application.PROJECT.aq_app.helpIndex
        )

        descript_module = self.tr("Acerca de Pineboo")
        about_pineboo_action = QtGui.QAction(config_tool_bar)
        about_pineboo_action.setObjectName("aboutPinebooAction")
        about_pineboo_action.setText(self.tr(descript_module))
        # help_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        about_pineboo_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("about.png")))
        config_tool_bar.addAction(about_pineboo_action)
        about_pineboo_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
            application.PROJECT.aq_app.aboutPineboo
        )

        descript_module = self.tr("Visita Eneboo.org")
        visit_pineboo_action = QtGui.QAction(config_tool_bar)
        visit_pineboo_action.setObjectName("visitPinebooAction")
        visit_pineboo_action.setText(self.tr(descript_module))
        # help_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        visit_pineboo_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("about.png")))
        config_tool_bar.addAction(visit_pineboo_action)
        visit_pineboo_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
            application.PROJECT.aq_app.urlPineboo
        )

        descript_module = self.tr("Acerca de Qt")
        about_qt_action = QtGui.QAction(config_tool_bar)
        about_qt_action.setObjectName("aboutQtAction")
        about_qt_action.setText(self.tr(descript_module))
        # help_action.setShortcut(getattr(QtCore.Qt, "Key_%s" % str(chr(c))))
        about_qt_action.setIcon(QtGui.QIcon(aqs.AQS.pixmap_fromMimeSource("aboutqt.png")))
        config_tool_bar.addAction(about_qt_action)
        about_qt_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
            application.PROJECT.aq_app.aboutQt
        )

        lay = config_tool_bar.layout()
        for child in config_tool_bar.children():
            if isinstance(child, QtWidgets.QToolButton):
                self.mdi_toolbuttons.append(child)
                lay.setAlignment(child, QtCore.Qt.AlignmentFlag.AlignCenter)

        if application.PROJECT.aq_app.acl_:
            application.PROJECT.aq_app.acl_.process(self.container_)

    def eventFilter(self, obj_: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """React to user events."""

        if self._inicializing or application.PROJECT.aq_app._destroying:
            return super().eventFilter(obj_, event)

        # if QtWidgets.QApplication.activeModalWidget() or QtWidgets.QApplication.activePopupWidget():
        #    return super().eventFilter(obj, event)
        obj_ = cast(QtWidgets.QWidget, obj_)
        event_type = event.type()
        main_widget = self.main_widget

        if (
            obj_ != main_widget
            and not isinstance(obj_, QtWidgets.QMainWindow)
            and not isinstance(obj_, qmainwindow.QMainWindow)
        ):

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

        if event_type == QtCore.QEvent.Type.KeyPress:
            # if obj_ == self.container_:
            #    key_ = cast(QtGui.QKeyEvent, event)

            if obj_ == main_widget:
                key_ = cast(QtGui.QKeyEvent, event)
                if (
                    key_.key() == cast(int, QtCore.Qt.Key.Key_Shift.value)
                    and key_.modifiers()  # type: ignore [comparison-overlap] # noqa: F821
                    == QtCore.Qt.KeyboardModifier.ControlModifier  # type: ignore [comparison-overlap] # noqa: F821
                ):
                    self.activateModule(None)
                    return True
                elif (
                    key_.key() == cast(int, QtCore.Qt.Key.Key_Q.value)
                    and key_.modifiers()  # type: ignore [comparison-overlap] # noqa: F821
                    == QtCore.Qt.KeyboardModifier.ControlModifier  # type: ignore [comparison-overlap] # noqa: F821
                ):
                    self.generalExit()
                    return True
                elif key_.key() == cast(
                    int, QtCore.Qt.Key.Key_W.value
                ) and key_.modifiers() in [  # type: ignore [comparison-overlap] # noqa: F821
                    QtCore.Qt.KeyboardModifier.AltModifier,
                    QtCore.Qt.KeyboardModifier.ControlModifier,
                ]:
                    LOGGER.warning("unknown key presset!.")
                    return True
                elif key_.key() == cast(int, QtCore.Qt.Key.Key_Escape.value):
                    obj_.hide()
                    return True

        elif event_type == QtCore.QEvent.Type.Close:
            if obj_ is self and not self.is_closing_:
                ret = self.generalExit()
                if not ret:
                    obj_.setDisabled(False)
                    event.ignore()
            else:
                self.writeStateActions(obj_.objectName())

            return True

        elif event_type == QtCore.QEvent.Type.WindowActivate:
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

        elif event_type == QtCore.QEvent.Type.Resize and obj_ is self:
            for tool_button in self.mdi_toolbuttons:
                tool_button.setMinimumWidth(obj_.width() - 10)

            return True

        return super().eventFilter(obj_, event)

    def activateModule(self, idm=None) -> None:
        """Initialize module."""

        if not idm:
            if self.sender():
                idm = self.sender().objectName()

        if not idm:
            return

        self.writeStateModule()

        widget = None
        if idm in self.db().managerModules().listAllIdModules():
            widget = self._dict_main_widgets[idm] if idm in self._dict_main_widgets.keys() else None
            if widget is None:
                widget = self.db().managerModules().createUI(file_name="%s.ui" % idm)
                if widget is None:

                    return
                if isinstance(widget, qmainwindow.QMainWindow) or widget.findChild(pncore.PNCore):
                    doc = QtXml.QDomDocument()
                    ui_file = "%s.ui" % idm
                    content_cached = self.db().managerModules().contentCached(ui_file)
                    if not content_cached or not doc.setContent(content_cached):
                        if content_cached is None:
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
                        if receiver == "FLWidgetApplication":
                            receiver = idm
                        slot = itn.namedItem("slot").toElement().text()

                        if receiver in [idm, "pncore"] and signal == "triggered()":
                            action_list = []
                            action = cast(QtGui.QAction, widget.findChild(QtGui.QAction, sender))
                            if action is not None:
                                action_list.append(action)

                            for menu in widget.findChildren(QtWidgets.QToolBar):
                                action = cast(QtGui.QAction, menu.findChild(QtGui.QAction, sender))
                                if action is not None and action not in action_list:
                                    action_list.append(action)

                            for action in action_list:
                                if (
                                    action is not None
                                    and sender in application.PROJECT.actions.keys()
                                ):
                                    slot_obj = getattr(
                                        application.PROJECT.actions[sender],
                                        slot[0 : slot.find("(")],
                                        None,
                                    )
                                    action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                                        slot_obj
                                    )
                                else:
                                    LOGGER.warning("Action %s not found", sender)

                widget.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
                self._dict_main_widgets[idm] = widget
                widget.setObjectName(idm)
                if application.PROJECT.aq_app.acl_:
                    application.PROJECT.aq_app.acl_.process(widget)

                self.setMainWidget(widget)
                application.PROJECT.aq_app.call("%s.init()" % idm, [])
                widget.removeEventFilter(self)
                self.db().managerModules().setActiveIdModule(idm)
                self.setMainWidget(widget)
                self.initMainWidget()
                self.showMainWidget(widget)
                widget.installEventFilter(self)
                return

        self.db().managerModules().setActiveIdModule("" if widget is None else idm)

        self.setMainWidget(widget)
        self.showMainWidget(widget)

    def writeState(self) -> None:
        """Write settings back to disk."""

        settings.SETTINGS.set_value("MultiLang/Enabled", self._multi_lang_enabled)
        settings.SETTINGS.set_value("MultiLang/LangId", self._multi_lang_id)

        if self.container_ is not None:
            windows_opened = []
            _list = QtWidgets.QApplication.topLevelWidgets()

            if self._inicializing:
                for item in _list:
                    item.removeEventFilter(self)
                    if item.objectName() in self._dict_main_widgets.keys():
                        if item != self.container_:
                            if item.isVisible():
                                windows_opened.append(item.objectName())
                            item.hide()
                        else:
                            item.setDisabled(True)
            else:
                for item in _list:
                    if (
                        item != self.container_
                        and item.isVisible()
                        and item.objectName() in self._dict_main_widgets.keys()
                    ):
                        windows_opened.append(item.objectName())

            settings.SETTINGS.set_value("windowsOpened/Main", windows_opened)
            settings.SETTINGS.set_value(
                "Geometry/MainWindowMaximized", self.container_.isMaximized()
            )
            if not self.container_.isMaximized():
                settings.SETTINGS.set_value("Geometry/MainWindowX", self.container_.x())
                settings.SETTINGS.set_value("Geometry/MainWindowY", self.container_.y())
                settings.SETTINGS.set_value("Geometry/MainWindowWidth", self.container_.width())
                settings.SETTINGS.set_value("Geometry/MainWindowHeight", self.container_.height())

    def writeStateActions(self, idm: str) -> None:
        """Write state actions forms."""

        container_ = None
        for level_widget in QtWidgets.QApplication.topLevelWidgets():
            if level_widget.objectName() == idm:
                container_ = level_widget
                break

        if container_ and idm:
            for item in [
                item.widget() for item in container_.findChildren(QtWidgets.QMdiSubWindow)  # type: ignore [attr-defined]
            ]:
                key = "Geometry/%s/" % item._action_name
                settings.SETTINGS.set_value("%s/X" % key, item.x())
                settings.SETTINGS.set_value("%s/Y" % key, item.y())
                settings.SETTINGS.set_value("%s/Width" % key, item.width())
                settings.SETTINGS.set_value("%s/Height" % key, item.height())

    def writeStateModule(self) -> None:
        """Write settings for modules."""

        idm = self.db().managerModules().activeIdModule()
        if not idm:
            return

        if self.main_widget is None or self.main_widget.objectName() != idm:
            return

        windows_opened: List[str] = []
        if self._p_work_space is not None:
            for sub_window in self._p_work_space.subWindowList():
                child = sub_window.findChild(QtWidgets.QDialog)
                if child is not None:
                    windows_opened.append(child.idMDI())

        settings.SETTINGS.set_value("windowsOpened/%s" % idm, windows_opened)

        key = "Geometry/%s" % idm
        settings.SETTINGS.set_value("%s/Maximized" % key, self.main_widget.isMaximized())
        settings.SETTINGS.set_value("%s/X" % key, self.main_widget.x())
        settings.SETTINGS.set_value("%s/Y" % key, self.main_widget.y())
        settings.SETTINGS.set_value("%s/Width" % key, self.main_widget.width())
        settings.SETTINGS.set_value("%s/Height" % key, self.main_widget.height())

    def readState(self) -> None:
        """Read settings."""
        self._inicializing = False
        self._dict_main_widgets = {}

        if self.container_:
            rect_ = QtCore.QRect(self.container_.pos(), self.container_.size())
            self._multi_lang_enabled = settings.SETTINGS.value("MultiLang/Enabled", False)
            self._multi_lang_id = settings.SETTINGS.value(
                "MultiLang/LangId", QtCore.QLocale().name()[:2].upper()
            )

            if not settings.SETTINGS.value("Geometry/MainWindowMaximized", False):
                rect_.setX(settings.SETTINGS.value("Geometry/MainWindowX", rect_.x()))
                rect_.setY(settings.SETTINGS.value("Geometry/MainWindowY", rect_.y()))
                rect_.setWidth(settings.SETTINGS.value("Geometry/MainWindowWidth", rect_.width()))
                rect_.setHeight(
                    settings.SETTINGS.value("Geometry/MainWindowHeight", rect_.height())
                )

                frame_geo = self.frameGeometry()
                primary_screen = QtGui.QGuiApplication.primaryScreen()
                frame_geo.moveCenter(primary_screen.geometry().center())
                self.move(frame_geo.topLeft())

                desk = self.container_.frameGeometry()
                inter = desk.intersected(rect_)
                self.container_.resize(rect_.size())
                if inter.width() * inter.height() > (rect_.width() * rect_.height() / 20):
                    self.container_.move(rect_.topLeft())
            else:
                # FIXME: maximizar?
                self.container_.resize(self.container_.frameGeometry().size())

            active_id_module = self.db().managerModules().activeIdModule()

            windows_opened = settings.SETTINGS.value("windowsOpened/Main", [])

            for id_module in windows_opened:
                if id_module in self.db().managerModules().listAllIdModules():
                    widget = None
                    if id_module in self._dict_main_widgets.keys():
                        widget = self._dict_main_widgets[id_module]
                    if widget is None:
                        act = cast(
                            QtGui.QAction, self.container_.findChild(QtGui.QAction, id_module)
                        )
                        if not act or not act.isVisible():
                            continue

                        self.activateModule(id_module)

                        widget = self._dict_main_widgets[id_module]
                        widget.setObjectName(id_module)
                        if application.PROJECT.aq_app.acl_:
                            application.PROJECT.aq_app.acl_.process(widget)

                        self.setCaptionMainWidget("")
                        self.setMainWidget(widget)
                        application.PROJECT.aq_app.call("%s.init()" % id_module, [])
                        self.db().managerModules().setActiveIdModule(id_module)
                        self.setMainWidget(widget)
                        self.initMainWidget()

            for key, widget in self._dict_main_widgets.items():
                if widget.objectName() != active_id_module:
                    widget.installEventFilter(self)
                    widget.show()
                    widget.setFont(QtWidgets.QApplication.font())
                    if not isinstance(widget, QtWidgets.QMainWindow):
                        continue

                    view_back = widget.centralWidget()
                    if view_back is not None:
                        self._p_work_space = cast(
                            flworkspace.FLWorkSpace,
                            view_back.findChild(QtCore.QObject, widget.objectName()),
                        )

            if active_id_module:
                self.container_.show()
                self.container_.setFont(self.font())

            self.activateModule(active_id_module)

    def readStateModule(self) -> None:
        """Read settings for module."""

        mng_modules = self.db().managerModules()
        idm = mng_modules.activeIdModule()
        if not idm:
            return

        main_widget = self.main_widget
        if main_widget is None or main_widget.objectName() != idm:
            return

        self.read_state_widget(idm, main_widget)

        windows_opened = settings.SETTINGS.value("windowsOpened/%s" % idm, [])
        for action_name in windows_opened:
            action = cast(QtGui.QAction, main_widget.findChild(QtGui.QAction, action_name))
            if action and action.isVisible() and action_name in application.PROJECT.actions.keys():

                form = mng_modules.createForm(application.PROJECT.actions[action_name])
                self.read_state_widget(action_name, form)
                form.show()

    def read_state_widget(self, name: str, widget: QtWidgets.QWidget) -> None:
        """Read state from a widget."""

        key = "Geometry/%s" % name
        rect_ = QtCore.QRect(widget.pos(), widget.size())
        if not settings.SETTINGS.value("%s/Maximized" % key, False):
            rect_.setX(settings.SETTINGS.value("%s/X" % key, rect_.x()))
            rect_.setY(settings.SETTINGS.value("%s/Y" % key, rect_.y()))
            rect_.setWidth(settings.SETTINGS.value("%s/Width" % key, rect_.width()))
            rect_.setHeight(settings.SETTINGS.value("%s/Height" % key, rect_.height()))

            # desk = widget.frameGeometry()
            # inter = desk.intersected(rect_)
            widget.resize(rect_.size())
            widget.move(rect_.topLeft())

            # if (inter.width() * inter.height()) - 100 > (rect_.width() * rect_.height()):
            #    widget.move(rect_.topLeft())
            # else:
            #    widget.hide()
            #    widget.resize(desk.size())

    def __del__(self) -> None:
        """Cleanup."""
        self._destroying = True
        application.PROJECT.aq_app.stopTimerIdle()

        if self._dict_main_widgets:
            for key in list(self._dict_main_widgets.keys()):
                del self._dict_main_widgets[key]

            self._dict_main_widgets = {}

        self._ted_output = None

    def initView(self) -> None:
        """Initialize view."""

        if self.main_widget is None:
            return

        view_back = cast(QtWidgets.QMainWindow, self.main_widget).centralWidget()
        if not isinstance(view_back, QtWidgets.QMdiArea):

            view_back = QtWidgets.QMdiArea()
            view_back.setObjectName("mdi_area")
            view_back.setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            # view_back.logo = pixmap_fromMimeSource("pineboo-logo.png")
            # view_back.logo = aqs.AQS.pixmap_fromMimeSource("pineboo-logo.png")
            view_back.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            view_back.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self._p_work_space = flworkspace.FLWorkSpace(
                view_back, self.db().managerModules().activeIdModule()
            )
            self._p_work_space.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
            # p_work_space.setScrollBarsEnabled(True)
            # FIXME: setScrollBarsEnabled
            cast(QtWidgets.QMainWindow, self.main_widget).setCentralWidget(view_back)

    def setMainWidget(self, widget) -> None:
        """Set mainWidget."""
        if not self.container_:
            return

        application.PROJECT.aq_app.setMainWidget(widget)

        main_widget = (
            self.main_widget if isinstance(self.main_widget, QtWidgets.QMainWindow) else None
        )

        if main_widget is None:
            return

        tools_action = None
        status_action = None

        if self.toogle_bars_:
            tool_bar = cast(QtWidgets.QToolBar, main_widget.findChild(QtWidgets.QToolBar))
            for action in self.toogle_bars_.actions():
                if action.objectName() == "Herramientas":
                    tools_action = action
                elif action.objectName() == "Estado":
                    status_action = action

            if tool_bar and tools_action is not None:
                tools_action.setChecked(tool_bar.isVisible())

            if status_action is not None:
                status_action.setChecked(main_widget.statusBar().isVisible())

    def showMainWidget(self, widget) -> None:
        """Show UI."""

        if not self.container_:
            if widget:
                widget.show()
            return

        focus_w = QtWidgets.QApplication.focusWidget()
        if widget is self.container_ or not widget:
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
                self.container_.setWindowTitle("Pineboo %s" % application.PROJECT.load_version())

            return

        if widget.isMinimized():
            widget.showNormal()
        elif not widget.isVisible():
            widget.show()
            widget.setFont(QtWidgets.QApplication.font())

        if focus_w and isinstance(focus_w, QtWidgets.QMainWindow) and focus_w != widget:
            widget.setFocus()
        if not widget.isActiveWindow():
            widget.raise_()
            QtWidgets.QApplication.setActiveWindow(widget)

        if widget:
            view_back = widget.centralWidget()
            if view_back:
                self._p_work_space = view_back.findChild(
                    flworkspace.FLWorkSpace, widget.objectName()
                )
                view_back.show()

        self.setCaptionMainWidget("")
        descript_area = (
            self.db()
            .managerModules()
            .idAreaToDescription(self.db().managerModules().activeIdArea())
        )
        widget.setWindowIcon(
            QtGui.QIcon(self.db().managerModules().iconModule(widget.objectName()))
        )
        self.tool_box_.setCurrentIndex(
            self.tool_box_.indexOf(self.tool_box_.findChild(QtWidgets.QToolBar, descript_area))
        )

    def initMainWidget(self) -> None:
        """Init mainwidget UI."""
        main_widget = cast(QtWidgets.QMainWindow, self.main_widget)
        if not main_widget or not self.container_:
            return

        if main_widget:
            action = main_widget.menuBar().addMenu(self.window_menu)
            action.setText(self.tr("&Ventana"))
            # main_widget.setCentralWidget(None)

        self.initView()
        self.initActions()
        self.initToolBar()
        self.initStatusBar()

        self.readStateModule()

    def setCaptionMainWidget(self, value: str) -> None:
        """Set application title."""
        if value:
            self.last_text_caption_ = value

        main_widget = self.main_widget

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
        if self.main_widget is not None and self._p_work_space is not None:
            self.window_cascade_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                self._p_work_space.cascadeSubWindows
            )
            self.window_tile_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                self._p_work_space.tileSubWindows
            )
            self.window_close_action.triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                self._p_work_space.closeActiveSubWindow
            )

    def initStatusBar(self) -> None:
        """Initialize statusbar."""
        main_widget = self.main_widget

        if not main_widget:
            return

        application.PROJECT.aq_app.statusHelpMsg(self.tr("Listo."))

        if main_widget is not None:
            status_bar = cast(QtWidgets.QMainWindow, main_widget).statusBar()
            status_bar.setSizeGripEnabled(False)

            conexion = QtWidgets.QLabel(status_bar)
            conexion.setText("%s@%s" % (self.db().user(), self.db().DBName()))
            status_bar.addWidget(conexion)

    def toggleToolBar(self, toggle: bool) -> None:
        """Show or hide toolbar."""
        main_widget = cast(QtWidgets.QToolBar, self.main_widget)

        if not main_widget:
            return

        tool_bar = cast(QtWidgets.QToolBar, main_widget.findChild(QtWidgets.QToolBar))

        if not tool_bar:
            return

        if toggle:
            tool_bar.show()
        else:
            tool_bar.hide()

    def toggleStatusBar(self, toggle: bool) -> None:
        """Toggle status bar."""
        main_widget = cast(QtWidgets.QMainWindow, self.main_widget)
        if not main_widget:
            return
        if toggle:
            main_widget.statusBar().show()
        else:
            main_widget.statusBar().hide()

    def generalExit(self, ask_exit=True) -> bool:
        """Perform before close checks."""
        do_exit = True
        if ask_exit:
            do_exit = application.PROJECT.aq_app.queryExit()
        if do_exit:
            self._destroying = True
            # if application.PROJECT.aq_app.consoleShown():
            #    if application.PROJECT.aq_app._ted_output is not None:
            #        application.PROJECT.aq_app._ted_output.close()

            if not application.PROJECT.aq_app.form_alone_:
                self.writeState()
                self.writeStateModule()

            if self.db().driverName():
                self.db().managerModules().finish()
                self.db().manager().finish()
                # QtCore.QTimer.singleShot(0, application.PROJECT.aq_app.quit)

            for main_widget in self._dict_main_widgets.values():
                main_widget.close()

            return True
        else:

            return False
