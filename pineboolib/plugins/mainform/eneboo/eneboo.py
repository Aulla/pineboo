# -*- coding: utf-8 -*-
"""
Main Eneboo-alike UI.
"""
from PyQt5 import QtWidgets, QtCore, QtGui, QtXml

from pineboolib.core import settings
from pineboolib.core.utils import utils_base

from pineboolib.q3widgets import qmessagebox

from pineboolib.fllegacy.aqsobjects import aqsobjectfactory

from pineboolib.fllegacy import flformdb, systype

from pineboolib import logging, application


from typing import Any, Dict, Optional, List, cast, Union


QSA_SYS = systype.SysType()
LOGGER = logging.get_logger(__name__)
AQS = aqsobjectfactory.AQS


class DockListView(QtCore.QObject):
    """DockListWiew class."""

    doc_widget: QtWidgets.QDockWidget
    tree_widget: QtWidgets.QTreeWidget
    action_group: QtWidgets.QActionGroup
    set_visible = QtCore.pyqtSignal(bool)
    Close = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None, name: str = "dockListView", title: str = "") -> None:
        """Initialize the DockListView instance."""

        super(DockListView, self).__init__(parent)
        if parent is None:
            return

        self.setObjectName(name)

        self.doc_widget = QtWidgets.QDockWidget(name, parent)
        self.doc_widget.setObjectName("%sListView" % name)
        self.doc_widget.setFixedWidth(300)

        self.tree_widget = QtWidgets.QTreeWidget(self.doc_widget)
        self.tree_widget.setObjectName(self.objectName())
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setHeaderLabels(["", ""])
        self.tree_widget.headerItem().setHidden(True)
        self.tree_widget.hideColumn(1)

        self.doc_widget.setWidget(self.tree_widget)
        self.doc_widget.setWindowTitle(title)

        """
        w.resizeEnabled = true;
        w.closeMode = true;
        w.setFixedExtentWidth(300);
        """

        self.tree_widget.doubleClicked.connect(self.activateAction)

    def writeState(self) -> None:
        """Save the state and geometry."""

        if self.doc_widget is None:
            raise Exception("self.doc_widget is empty!")

        settings = aqsobjectfactory.AQSettings()
        key = "MainWindow/%s/" % self.doc_widget.objectName()
        # FIXME
        # settings.writeEntry("%splace" % key, self.doc_widget.place())  # Donde está emplazado

        settings.writeEntry("%svisible" % key, self.doc_widget.isVisible())
        settings.writeEntry("%sx" % key, self.doc_widget.x())
        settings.writeEntry("%sy" % key, self.doc_widget.y())
        settings.writeEntry("%swidth" % key, self.doc_widget.width())
        settings.writeEntry("%sheight" % key, self.doc_widget.height())
        # FIXME
        # settings.writeEntry("%soffset", key, self.offset())
        # area = self.area()
        # settings.writeEntry("%sindex" % key, area.findDockWindow(self.doc_widget) if area else None)

    def readState(self) -> None:
        """Read the state and geometry."""

        if self.doc_widget is None:
            raise Exception("self.doc_widget is empty!")

        if self.tree_widget is None:
            raise Exception("self.tree_widget is empty!")

        settings = aqsobjectfactory.AQSettings()
        key = "MainWindow/%s/" % self.doc_widget.objectName()
        # FIXME
        # place = settings.readNumEntry("%splace" % key, AQS.InDock)
        # if place == AQS.OutSideDock:
        #    self.doc_widget.setFloating(True)
        #    self.doc_widget.move(settings.readNumEntry("%sx" % key, self.doc_widget.x()),
        #                 settings.readNumEntry("%sy" % key, self.doc_widget.y()))

        # self.doc_widget.offset = settings.readNumEntry("%soffset" % key, self.offset)
        # index = settings.readNumEntry("%sindex" % key, None)
        # FIXME
        # if index is not None:
        #    area = w.area()
        #    if area:
        #        area.moveDockWindow(w, index)

        width = settings.readNumEntry("%swidth" % key, self.doc_widget.width())
        height = settings.readNumEntry("%sheight" % key, self.doc_widget.height())
        self.tree_widget.resize(width, height)
        # self.doc_widget.resize(width, height)

        if not application.PROJECT.DGI.mobilePlatform():
            visible = settings.readBoolEntry("%svisible" % key, True)
            if visible:
                self.doc_widget.show()

            else:
                self.doc_widget.hide()

            self.set_visible.emit(not self.doc_widget.isHidden())
        else:
            self.doc_widget.hide()
            self.set_visible.emit(False)
            self.doc_widget.close()

    def initFromWidget(self, doc_widget) -> None:
        """Initialize the internal widget."""

        self.doc_widget = doc_widget
        self.tree_widget = doc_widget.widget()
        if self.tree_widget and self.tree_widget.doubleClicked:
            self.tree_widget.doubleClicked.connect(self.activateAction)

    def change_state(self, state: bool) -> None:
        """Change the display status."""
        if self.doc_widget is None:
            raise Exception("not initialized")
        if state:
            self.doc_widget.show()
        else:
            self.doc_widget.close()

    def activateAction(self, item) -> None:
        """Activate the action associated with the active item."""

        if item is None or not self.action_group:
            return

        action_name = item.sibling(item.row(), 1).data()
        if action_name == "":
            return

        action: QtWidgets.QAction = cast(
            QtWidgets.QAction, self.action_group.findChild(QtWidgets.QAction, action_name)
        )
        if action:
            action.triggered.emit()

    def update(
        self, action_group: Optional[QtWidgets.QActionGroup] = None, reverse: bool = False
    ) -> None:
        """Update available items."""
        if not action_group:
            return

        self.action_group = action_group

        if not self.tree_widget:
            return

        self.tree_widget.clear()

        self.buildListView(
            self.tree_widget, AQS.toXml(self.action_group), self.action_group, reverse
        )

    def buildListView(self, parent_item, parent_element, action_group_, reverse: bool) -> None:
        """Build the tree of available options."""

        this_item = None
        node = (
            parent_element.lastChild().toElement()
            if reverse
            else parent_element.firstChild().toElement()
        )
        while not node.isNull():
            if node.attribute("objectName") in ("", "separator"):  # Pasamos de este
                node = (
                    node.previousSibling().toElement()
                    if reverse
                    else node.nextSibling().toElement()
                )
                continue
            class_name = node.attribute("class")
            if class_name.startswith("QAction"):
                if class_name == "QActionGroup":
                    act_group = action_group_.findChild(
                        QtWidgets.QActionGroup, node.attribute("objectName")
                    )
                    if act_group and not act_group.isVisible():
                        node = (
                            node.previousSibling().toElement()
                            if reverse
                            else node.nextSibling().toElement()
                        )
                        continue

                    group_name = node.attribute("objectName")
                    if (
                        group_name not in ("pinebooActionGroup")
                        and not group_name.endswith("Actions")
                        and not group_name.startswith(("pinebooAg"))
                    ) or group_name.endswith("MoreActions"):

                        this_item = QtWidgets.QTreeWidgetItem(parent_item)
                        this_item.setText(0, group_name)

                    else:
                        this_item = parent_item

                    self.buildListView(this_item, node, action_group_, reverse)
                    node = (
                        node.previousSibling().toElement()
                        if reverse
                        else node.nextSibling().toElement()
                    )
                    continue

                if node.attribute("objectName") not in (
                    "pinebooActionGroup",
                    "pinebooActionGroup_actiongroup_name",
                ):

                    action_name = node.attribute("objectName")
                    action = action_group_.findChild(QtWidgets.QAction, action_name)

                    action_group = action_group_.findChild(
                        QtWidgets.QActionGroup, parent_element.attribute("objectName")
                    )
                    if action_group is not None:  # ¢heck if is visible
                        ac_orig = action_group.findChild(QtWidgets.QAction, action_name)
                        if ac_orig and not ac_orig.isVisible():
                            action = None

                    if action is not None:

                        if action_name.endswith("actiongroup_name"):
                            this_item = (
                                parent_item
                                if isinstance(parent_item, QtWidgets.QTreeWidgetItem)
                                else None
                            )
                        else:
                            this_item = QtWidgets.QTreeWidgetItem(parent_item)

                        if this_item is not None:
                            this_item.setIcon(0, action.icon())
                            this_item.setText(1, action_name)
                            this_item.setText(0, node.attribute("text").replace("&", ""))

                self.buildListView(this_item, node, action_group_, reverse)

            node = node.previousSibling().toElement() if reverse else node.nextSibling().toElement()


class MainForm(QtWidgets.QMainWindow):
    """
    Create Eneboo-alike UI.
    """

    MAX_RECENT = 10
    app_ = None
    ag_menu_: Optional[QtWidgets.QActionGroup]
    ag_rec_: Optional[QtWidgets.QActionGroup]
    ag_mar_: Optional[QtWidgets.QActionGroup]
    dck_mod_: DockListView
    dck_rec_: DockListView
    dck_mar_: DockListView
    tab_widget: QtWidgets.QTabWidget
    w_: QtWidgets.QMainWindow
    # tw_corner = None  # deprecated
    act_sig_map_: QtCore.QSignalMapper
    initialized_mods_: List[str]
    main_widgets_: Dict[str, QtWidgets.QWidget] = {}
    debugLevel: int
    # lista_tabs_ = []

    def __init__(self) -> None:
        """Construct Eneboo-alike UI."""
        super().__init__()

        self.ag_menu_ = None
        self.ag_rec_ = None
        self.ag_mar_ = None

    def eventFilter(self, obj_: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Process GUI events."""

        if isinstance(event, AQS.ContextMenu):
            if obj_ == getattr(self.dck_mod_, "doc_widget", None):
                return self.addMarkFromItem(
                    self.dck_mod_.tree_widget.currentItem(), event.globalPos()
                )
            elif obj_ == getattr(self.dck_rec_, "doc_widget", None):
                return self.addMarkFromItem(
                    self.dck_rec_.tree_widget.currentItem(), event.globalPos()
                )
            elif obj_ == getattr(self.dck_mar_, "doc_widget", None):
                return self.removeMarkFromItem(
                    self.dck_mar_.tree_widget.currentItem(), event.globalPos()
                )

            # pinebooMenu = self.main_widget.child("pinebooMenu")
            # pinebooMenu.exec_(e.globalPos)
            return True

        elif isinstance(event, AQS.Close):
            if isinstance(obj_, MainForm):
                self.main_widget.setDisabled(True)
                ret = self.exit()
                if not ret:
                    self.main_widget.setDisabled(False)
                    event.ignore()

                return True

            elif isinstance(obj_, QtWidgets.QDockWidget):
                cast(QtCore.pyqtSignal, obj_.topLevelChanged).emit(False)
            elif isinstance(obj_, flformdb.FLFormDB):
                for number in range(self.tab_widget.count()):
                    if self.tab_widget.widget(number) is obj_:
                        self.tab_widget.removeTab(number)
                        break

        elif isinstance(event, AQS.Show):
            if isinstance(obj_, flformdb.FLFormDB):
                return True

        return False

    def createUi(self, ui_file: str) -> None:
        """Create UI from file path."""

        mng = application.PROJECT.conn_manager.managerModules()
        self.main_widget = cast(QtWidgets.QMainWindow, mng.createUI(ui_file, None, self))
        self.main_widget.setObjectName("container")

    def exit(self) -> bool:
        """Process exit events."""
        res = qmessagebox.QMessageBox.information(
            "¿ Quiere salir de la aplicación ?",
            qmessagebox.QMessageBox.Yes,
            qmessagebox.QMessageBox.No,
            None,
            "Pineboo",
        )

        do_exit = res == qmessagebox.QMessageBox.Yes
        if do_exit:
            self.writeState()
            self.main_widget.removeEventFilter(self.main_widget)
            self.removeAllPages()

        return do_exit

    def writeStateModule(self) -> None:
        """Write settings for modules."""

        pass

    def writeState(self) -> None:
        """Save settings."""

        if self.dck_rec_ is None:
            raise Exception("Recent dockListView is missing!")

        if self.dck_mod_ is None:
            raise Exception("Modules dockListView is missing!")

        if self.dck_mar_ is None:
            raise Exception("BookMarks dockListView is missing!")

        self.dck_mod_.writeState()
        self.dck_rec_.writeState()
        self.dck_mar_.writeState()

        settings = aqsobjectfactory.AQSettings()
        key = "MainWindow/"

        settings.writeEntry("%smaximized" % key, self.main_widget.isMaximized())
        settings.writeEntry("%sx" % key, self.main_widget.x())
        settings.writeEntry("%sy" % key, self.main_widget.y())
        settings.writeEntry("%swidth" % key, self.main_widget.width())
        settings.writeEntry("%sheight" % key, self.main_widget.height())

        key += "%s/" % application.PROJECT.conn_manager.database()

        open_actions = []

        for i in range(self.tab_widget.count()):
            open_actions.append(cast(flformdb.FLFormDB, self.tab_widget.widget(i)).idMDI())

        settings.writeEntryList("%sopenActions" % key, open_actions)
        settings.writeEntry("%scurrentPageIndex" % key, self.tab_widget.currentIndex())

        recent_actions = []
        root_recent = self.dck_rec_.tree_widget.invisibleRootItem()
        count_recent = root_recent.childCount()
        for i in range(count_recent):
            recent_actions.append(root_recent.child(i).text(1))
        settings.writeEntryList("%srecentActions" % key, recent_actions)

        mark_actions = []
        root_mark = self.dck_mar_.tree_widget.invisibleRootItem()
        count_mark = root_mark.childCount()
        for i in range(count_mark):
            mark_actions.append(root_mark.child(i).text(1))
        settings.writeEntryList("%smarkActions" % key, mark_actions)

    def readState(self) -> None:
        """Read settings."""

        if self.dck_rec_ is None:
            raise Exception("Recent dockListView is missing!")

        if self.dck_mod_ is None:
            raise Exception("Modules dockListView is missing!")

        if self.dck_mar_ is None:
            raise Exception("BookMarks dockListView is missing!")

        self.dck_mod_.readState()
        self.dck_rec_.readState()
        self.dck_mar_.readState()

        settings = aqsobjectfactory.AQSettings()
        key = "MainWindow/"

        maximized = settings.readBoolEntry("%smaximized" % key)

        if not maximized:
            pos_x = settings.readNumEntry("%sx" % key)
            pos_y = settings.readNumEntry("%sy" % key)
            if QSA_SYS.osName() == "MACX" and pos_y < 20:
                pos_y = 20
            self.main_widget.move(pos_x, pos_y)
            self.main_widget.resize(
                settings.readNumEntry("%swidth" % key, self.main_widget.width()),
                settings.readNumEntry("%sheight" % key, self.main_widget.height()),
            )
        else:
            self.main_widget.showMaximized()

        self.loadTabs()

    def loadTabs(self) -> None:
        """Load tabs."""
        if self.ag_menu_:

            settings = aqsobjectfactory.AQSettings()
            key = "MainWindow/%s/" % application.PROJECT.conn_manager.database()

            open_actions = settings.readListEntry("%sopenActions" % key)

            if self.tab_widget is None:
                raise Exception("tab_widget is empty!")

            for number in range(self.tab_widget.count()):
                self.tab_widget.widget(number).close()
                self.tab_widget.removeTab(number)

            actions_opened: List[str] = []
            for open_action in open_actions:
                if open_action in actions_opened:
                    continue
                else:
                    actions_opened.append(open_action)

                action = cast(
                    QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, open_action)
                )
                if not action or not action.isVisible():
                    continue
                module_name = application.PROJECT.conn_manager.managerModules().idModuleOfFile(
                    "%s.ui" % action.objectName()
                )
                if module_name:
                    self.initModule(module_name)

                self.addForm(open_action, action.icon().pixmap(16, 16))

            idx = settings.readNumEntry("%scurrentPageIndex" % key)
            if idx > 0 and idx < len(self.tab_widget):
                self.tab_widget.setCurrentWidget(self.tab_widget.widget(idx))

            recent_actions = settings.readListEntry("%srecentActions" % key)
            for recent in reversed(recent_actions):
                self.addRecent(
                    cast(QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, recent))
                )

            mark_actions = settings.readListEntry("%smarkActions" % key)
            for mark in reversed(mark_actions):
                self.addMark(
                    cast(QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, mark))
                )

    def init(self) -> None:
        """Initialize UI."""
        self.main_widget.statusBar().hide()
        self.main_widgets_ = {}
        self.initialized_mods_ = []
        self.act_sig_map_ = QtCore.QSignalMapper(self.main_widget)
        self.act_sig_map_.setObjectName("pinebooActSignalMap")
        self.act_sig_map_.mapped[str].connect(self.triggerAction)  # type: ignore
        self.initTabWidget()
        self.initHelpMenu()
        self.initConfigMenu()
        self.initTextLabels()
        self.initDocks()
        self.initEventFilter()

    def initFromWidget(self, main_window: "QtWidgets.QMainWindow") -> None:
        """Initialize UI from a base widget."""
        self.main_widget = main_window
        self.main_widgets_ = {}
        self.initialized_mods_ = []
        self.act_sig_map_ = QtCore.QSignalMapper(self.main_widget)
        self.act_sig_map_.setObjectName("pinebooActSignalMap")
        self.tab_widget = cast(
            QtWidgets.QTabWidget, self.main_widget.findChild(QtWidgets.QTabWidget, "tabWidget")
        )
        self.action_group_menu = cast(
            QtWidgets.QActionGroup,
            self.main_widget.findChild(QtWidgets.QActionGroup, "pinebooActionGroup"),
        )
        self.dck_mod_ = DockListView()
        self.dck_mod_.initFromWidget(
            cast(
                QtWidgets.QDockWidget,
                self.main_widget.findChild(QtWidgets.QDockWidget, "pinebooDockModulesListView"),
            )
        )
        self.dck_rec_ = DockListView()
        self.dck_rec_.initFromWidget(
            cast(
                QtWidgets.QDockWidget,
                self.main_widget.findChild(QtWidgets.QDockWidget, "pinebooDockRecentListView"),
            )
        )
        self.dck_mar_ = DockListView()
        self.dck_mar_.initFromWidget(
            cast(
                QtWidgets.QDockWidget,
                self.main_widget.findChild(QtWidgets.QDockWidget, "pinebooDockMarksListView"),
            )
        )
        self.initEventFilter()

    def initEventFilter(self) -> None:
        """Install event filters."""
        # w = self.main_widget
        # self.main_widget.eventFilterFunction = (
        #    "flapplication.flapplication.aqApp.Script.mainWindow_.eventFilter"
        # )

        # self.main_widget.allow_events = [AQS.ContextMenu, AQS.Close]

        self.main_widget.installEventFilter(self)
        if self.dck_mod_ and self.dck_mod_.doc_widget:
            self.dck_mod_.doc_widget.installEventFilter(self)
        if self.dck_rec_ and self.dck_rec_.doc_widget:
            self.dck_rec_.doc_widget.installEventFilter(self)
        if self.dck_mar_ and self.dck_mar_.doc_widget:
            self.dck_mar_.doc_widget.installEventFilter(self)

    def initModule(self, module: str) -> None:
        """Initialize main module."""
        if module in self.main_widgets_:
            mwi = self.main_widgets_[module]
            mwi.setObjectName(module)
            application.PROJECT.aq_app.setObjectName(module)
            mwi.show()

        if module not in self.initialized_mods_:
            self.initialized_mods_.append(module)
            application.PROJECT.call("%s.iface.init" % module, [], None, False)

        mng = application.PROJECT.conn_manager.managerModules()
        mng.setActiveIdModule(module)

    def removeCurrentPage(self, idx: Optional[int] = None) -> None:
        """Close tab."""
        if self.tab_widget is None:
            raise Exception("Not initialized.")

        if idx is None:
            for number in range(self.tab_widget.count()):
                if self.tab_widget.widget(number) is self.tab_widget.currentWidget():
                    idx = number
                    break

        if idx is not None:
            if isinstance(self.tab_widget.widget(idx), QtWidgets.QDialog):
                self.tab_widget.widget(idx).close()
                self.tab_widget.removeTab(idx)

    def removeAllPages(self) -> None:
        """Close all tabs."""
        if self.tab_widget is None:
            raise Exception("Not initialized.")

        # if len(tw):
        #    self.tab_widgetcorner.hide()

        for number in range(self.tab_widget.count()):
            if self.tab_widget.widget(number):
                self.tab_widget.widget(number).close()

    def addForm(self, action_str: str, icono: "QtGui.QPixmap") -> None:
        """Add new tab."""

        if self.tab_widget is None:
            raise Exception("tab_widget is empty!")

        action_name = action_str

        for i in range(self.tab_widget.count()):
            form = self.tab_widget.widget(i)
            if isinstance(form, flformdb.FLFormDB):
                if form.action().name() == action_name:
                    form.close()
                    break
        if self.ag_menu_:
            action = cast(
                QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, action_name)
            )
            icon = action.icon() if action is not None else None
            form = aqsobjectfactory.AQFormDB(action_name, self.tab_widget)
            form.setMainWidget()

            try:
                title = form.windowTitle()

                if not form.mainWidget():
                    return
                if self.ag_menu_:
                    self.tab_widget.addTab(form, icon, title)

                form.setIdMDI(action_name)
                form.show()

                self.tab_widget.setCurrentWidget(form)
                form.installEventFilter(self.main_widget)

            except Exception as error:
                LOGGER.warning("addForm: %s", str(error))

    def addRecent(self, action: QtWidgets.QAction) -> None:
        """Add new entry to recent list."""
        if not action:
            return

        if not self.ag_rec_:
            self.ag_rec_ = QtWidgets.QActionGroup(self.main_widget)

        check_max = True

        new_ag_rec_ = QtWidgets.QActionGroup(self.main_widget)
        new_ag_rec_.setObjectName("pinebooAgRec")

        self.cloneAction(action, new_ag_rec_)

        for item in self.ag_rec_.actions():
            if item.objectName() == action.objectName():
                check_max = False
                continue

            self.cloneAction(item, new_ag_rec_)

        self.ag_rec_ = new_ag_rec_
        if self.dck_rec_ is None:
            return
        tree_widget = self.dck_rec_.tree_widget
        if tree_widget is None:
            return
        if check_max and tree_widget.topLevelItemCount() >= self.MAX_RECENT:
            last_name = tree_widget.topLevelItem(tree_widget.topLevelItemCount() - 1).text(1)
            action_ = cast(QtWidgets.QAction, self.ag_rec_.findChild(QtWidgets.QAction, last_name))
            if action_:
                self.ag_rec_.removeAction(action_)
                del action_

        self.dck_rec_.update(self.ag_rec_)

    def addMark(self, action: QtWidgets.QAction) -> None:
        """Add new entry to Mark list."""
        if not action:
            return

        if not self.ag_mar_:
            self.ag_mar_ = QtWidgets.QActionGroup(self.main_widget)

        new_ag_mar = QtWidgets.QActionGroup(self.main_widget)
        new_ag_mar.setObjectName("pinebooAgMar")

        for item in self.ag_mar_.actions():
            if item.objectName() == action.objectName():
                continue

            self.cloneAction(item, new_ag_mar)

        self.cloneAction(action, new_ag_mar)

        self.ag_mar_ = new_ag_mar
        if self.dck_mar_:
            self.dck_mar_.update(self.ag_mar_, True)

    def addMarkFromItem(self, item: Any, pos: QtCore.QPoint) -> bool:
        """Add a new item to the Bookmarks docket."""

        if not item:
            return False

        if item.text(1) is None:
            return True

        pop_menu = QtWidgets.QMenu()
        pop_menu.move(pos)
        pop_menu.addAction(self.tr("Añadir Marcadores"))
        res = pop_menu.exec_()
        if res and self.ag_menu_ is not None:
            action = cast(
                QtWidgets.QAction, self.ag_menu_.findChild(QtWidgets.QAction, item.text(1))
            )
            if action and not action.objectName().endswith("actiongroup_name"):
                self.addMark(action)

        return True

    def removeMarkFromItem(self, item: Any, pos: QtCore.QPoint) -> bool:
        """Add a new item to the Bookmarks docket."""
        if not item or not self.ag_mar_ or self.dck_mar_ is None:
            return False
        if (
            self.dck_mar_.tree_widget is None
            or self.dck_mar_.tree_widget.invisibleRootItem().childCount() == 0
        ):
            return False
        if item.text(1) is None:
            return True

        pop_menu = QtWidgets.QMenu()
        pop_menu.move(pos)
        pop_menu.addAction(self.tr("Eliminar Marcador"))
        res = pop_menu.exec_()
        if res:
            action = cast(
                QtWidgets.QAction, self.ag_mar_.findChild(QtWidgets.QAction, item.text(1))
            )
            if action and self.ag_mar_:
                self.ag_mar_.removeAction(action)
                del action
                self.dck_mar_.update(self.ag_mar_)

        return True

    def updateMenu(self, action_group: "QtWidgets.QActionGroup", parent: Any) -> None:
        """Update the modules menu with the available options."""
        object_list = cast(
            List[Union[QtWidgets.QAction, QtWidgets.QActionGroup]], action_group.children()
        )
        for obj_ in object_list:
            o_name = obj_.objectName()
            if not getattr(obj_, "isVisible", None) or not obj_.isVisible():
                continue
            if isinstance(obj_, QtWidgets.QActionGroup):
                new_parent = parent

                ac_obj = cast(
                    QtWidgets.QAction,
                    obj_.findChild(QtWidgets.QAction, "%s_actiongroup_name" % o_name),
                )
                if ac_obj:
                    if not o_name.endswith("Actions") or o_name.endswith("MoreActions"):
                        new_parent = parent.addMenu(ac_obj.icon(), ac_obj.text())
                        new_parent.triggered.connect(ac_obj.trigger)

                self.updateMenu(obj_, new_parent)
                continue

            elif o_name.endswith("_actiongroup_name"):
                continue

            elif o_name == "separator":
                action = parent.addAction("")
                action.setSeparator(True)
            else:
                if isinstance(obj_, QtWidgets.QAction):
                    if self.ag_menu_:
                        obj_real = cast(
                            QtWidgets.QAction,
                            self.ag_menu_.findChild(QtWidgets.QAction, obj_.objectName()),
                        )
                        if obj_real is not None:
                            obj_ = obj_real  # Fix invalid QActions
                    action = parent.addAction(obj_.text())
                    action.setIcon(obj_.icon())
                    action.triggered.connect(obj_.trigger)
                else:
                    continue

            action.setObjectName(o_name)

    def updateMenuAndDocks(self) -> None:
        """Update the main menu and dockers."""
        # FIXME: Duplicated piece of code
        self.updateActionGroup()
        pineboo_menu = cast(
            QtWidgets.QMenu, self.main_widget.findChild(QtWidgets.QMenu, "menuPineboo")
        )
        pineboo_menu.clear()

        if self.ag_menu_ is None:
            raise Exception("ag_menu_ is empty!")

        self.updateMenu(self.ag_menu_, pineboo_menu)

        application.PROJECT.aq_app.setMainWidget(self.main_widget)

        if self.ag_menu_ is None:
            raise Exception("ag_menu_ is empty!")

        if not self.ag_rec_:
            self.ag_rec_ = QtWidgets.QActionGroup(self.main_widget)

        if not self.ag_mar_:
            self.ag_mar_ = QtWidgets.QActionGroup(self.main_widget)

        if self.dck_rec_ is None:
            raise Exception("Recent dockListView is missing!")

        if self.dck_mod_ is None:
            raise Exception("Modules dockListView is missing!")

        if self.dck_mar_ is None:
            raise Exception("BookMarks dockListView is missing!")

        self.dck_mod_.update(self.ag_menu_)
        self.dck_rec_.update(self.ag_rec_)
        self.dck_mar_.update(self.ag_mar_)
        cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "aboutQtAction")
        ).triggered.connect(application.PROJECT.aq_app.aboutQt)
        cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "aboutPinebooAction")
        ).triggered.connect(application.PROJECT.aq_app.aboutPineboo)
        cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "fontAction")
        ).triggered.connect(application.PROJECT.aq_app.chooseFont)
        cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QMenu, "style")
        ).triggered.connect(application.PROJECT.aq_app.showStyles)
        cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "helpIndexAction")
        ).triggered.connect(application.PROJECT.aq_app.helpIndex)
        cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "urlPinebooAction")
        ).triggered.connect(application.PROJECT.aq_app.urlPineboo)

    def updateActionGroup(self) -> None:
        """Update the available actions."""

        if self.ag_menu_:
            list_ = self.ag_menu_.children()
            for obj in list_:
                if isinstance(obj, QtWidgets.QAction):
                    self.ag_menu_.removeAction(obj)
                    del obj

            self.ag_menu_.deleteLater()
            del self.ag_menu_

        self.ag_menu_ = QtWidgets.QActionGroup(self.main_widget)
        self.ag_menu_.setObjectName("pinebooActionGroup")
        ac_name = QtWidgets.QAction(self.ag_menu_)
        ac_name.setObjectName("pinebooActionGroup_actiongroup_name")
        ac_name.setText(self.tr("Menú"))

        mng = application.PROJECT.conn_manager.managerModules()
        areas = mng.listIdAreas()

        if self.act_sig_map_ is None:
            raise Exception("self.act_sig_map_ is empty!")

        for area in areas:
            if not QSA_SYS.isDebuggerEnabled() and area == "sys":
                break
            action_group = QtWidgets.QActionGroup(self.ag_menu_)
            action_group.setObjectName(area)
            ag_action = QtWidgets.QAction(action_group)
            ag_action.setObjectName("%s_actiongroup_name" % action_group.objectName())
            ag_action.setText(mng.idAreaToDescription(action_group.objectName()))
            ag_action.setIcon(QtGui.QIcon(AQS.pixmap_fromMimeSource("folder.png")))

            modules = mng.listIdModules(action_group.objectName())
            for module in modules:
                if module == "sys" and QSA_SYS.isUserBuild():
                    continue
                action: Union[QtWidgets.QAction, QtWidgets.QActionGroup] = QtWidgets.QActionGroup(
                    action_group
                )
                action.setObjectName(module)
                if QSA_SYS.isQuickBuild():
                    if module == "sys":
                        continue
                actions = self.widgetActions("%s.ui" % action.objectName(), action)

                if not actions:
                    # ac.setObjectName("")
                    action.deleteLater()
                    action = QtWidgets.QAction(action_group)
                    if action:
                        action.setObjectName(module)

                ac_action = QtWidgets.QAction(action)
                ac_action.setObjectName("%s_actiongroup_name" % action.objectName())
                ac_action.setText(mng.idModuleToDescription(action.objectName()))
                ac_action.setIcon(self.iconSet16x16(mng.iconModule(action.objectName())))

                ac_action.triggered.connect(self.act_sig_map_.map)
                self.act_sig_map_.setMapping(
                    ac_action, "triggered():initModule():%s_actiongroup_name" % action.objectName()
                )
                if action.objectName() == "sys" and action_group.objectName() == "sys":
                    if QSA_SYS.isDebuggerMode():
                        static_load = QtWidgets.QAction(action_group)
                        static_load.setObjectName("staticLoaderSetupAction")
                        static_load.setText(self.tr("Configurar carga estática"))
                        static_load.setIcon(
                            QtGui.QIcon(AQS.pixmap_fromMimeSource("folder_update.png"))
                        )
                        static_load.triggered.connect(self.act_sig_map_.map)
                        self.act_sig_map_.setMapping(
                            static_load,
                            "triggered():staticLoaderSetup():%s" % static_load.objectName(),
                        )

                        re_init = QtWidgets.QAction(action_group)
                        re_init.setObjectName("reinitAction")
                        re_init.setText(self.tr("Recargar scripts"))
                        re_init.setIcon(QtGui.QIcon(AQS.pixmap_fromMimeSource("reload.png")))
                        re_init.triggered.connect(self.act_sig_map_.map)
                        self.act_sig_map_.setMapping(
                            re_init, "triggered():reinit():%s" % re_init.objectName()
                        )

        sh_console = QtWidgets.QAction(self.ag_menu_)
        sh_console.setObjectName("shConsoleAction")
        sh_console.setText(self.tr("Mostrar Consola de mensajes"))
        sh_console.setIcon(QtGui.QIcon(AQS.pixmap_fromMimeSource("consola.png")))
        sh_console.triggered.connect(self.act_sig_map_.map)
        self.act_sig_map_.setMapping(
            sh_console, "triggered():shConsole():%s" % sh_console.objectName()
        )

        exit = QtWidgets.QAction(self.ag_menu_)
        exit.setObjectName("exitAction")
        exit.setText(self.tr("&Salir"))
        exit.setIcon(QtGui.QIcon(AQS.pixmap_fromMimeSource("exit.png")))
        exit.triggered.connect(self.act_sig_map_.map)
        self.act_sig_map_.setMapping(exit, "triggered():exit():%s" % exit.objectName())

    def initTabWidget(self) -> None:
        """Initialize the TabWidget."""
        self.tab_widget = cast(
            QtWidgets.QTabWidget, self.main_widget.findChild(QtWidgets.QTabWidget, "tabWidget")
        )
        if self.tab_widget is None:
            raise Exception("no tabWidget found")
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested[int].connect(self.removeCurrentPage)  # type: ignore
        self.tab_widget.removeTab(0)
        """
        tb = self.tw_corner = QToolButton(tw, "tabWidgetCorner")
        tb.autoRaise = False
        tb.setFixedSize(16, 16)
        tb.setIconSet(self.iconset16x16(AQS.pixmap_fromMimeSource("file_close.png")))
        tb.clicked.connect(self.removeCurrentPage)
        tw.setCornerWidget(tb, AQS.TopRight)
        AQS.toolTip_add(tb, self.tr("Cerrar pestaña"))
        tb.hide()
        """

    def initHelpMenu(self) -> None:
        """Initialize help menu."""

        aboutQt = cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "aboutQtAction")
        )
        aboutQt.setIcon(self.iconSet16x16(AQS.pixmap_fromMimeSource("aboutqt.png")))
        # aboutQt.triggered.connect(flapplication.aqApp.aboutQt)

        aboutPineboo = cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "aboutPinebooAction")
        )
        aboutPineboo.setIcon(self.iconSet16x16(AQS.pixmap_fromMimeSource("pineboo-logo-32.png")))
        # aboutPineboo.triggered.connect(flapplication.aqApp.aboutPineboo)

        helpIndex = cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "helpIndexAction")
        )
        helpIndex.setIcon(self.iconSet16x16(AQS.pixmap_fromMimeSource("help_index.png")))
        # helpIndex.triggered.connect(flapplication.aqApp.helpIndex)

        urlPineboo = cast(
            QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "urlPinebooAction")
        )
        urlPineboo.setIcon(self.iconSet16x16(AQS.pixmap_fromMimeSource("pineboo-logo-32.png")))
        # urlPineboo.triggered.connect(flapplication.aqApp.urlPineboo)

    def initConfigMenu(self) -> None:
        """Initialize config menu."""
        font = cast(QtWidgets.QAction, self.main_widget.findChild(QtWidgets.QAction, "fontAction"))
        font.setIcon(self.iconSet16x16(AQS.pixmap_fromMimeSource("font.png")))
        # font.triggered.connect(flapplication.aqApp.chooseFont)

        style = cast(QtWidgets.QMenu, self.main_widget.findChild(QtWidgets.QMenu, "style"))

        application.PROJECT.aq_app.initStyles()
        style.setIcon(self.iconSet16x16(AQS.pixmap_fromMimeSource("estilo.png")))
        # style.triggered.connect(flapplication.aqApp.showStyles)

    def initTextLabels(self) -> None:
        """Initialize the tags in the mainForm base."""

        text_label = cast(QtWidgets.QLabel, self.main_widget.findChild(QtWidgets.QLabel, "tLabel"))
        text_label2 = cast(
            QtWidgets.QLabel, self.main_widget.findChild(QtWidgets.QLabel, "tLabel2")
        )
        texto = aqsobjectfactory.AQUtil.sqlSelect("flsettings", "valor", "flkey='verticalName'")
        if texto and texto != "False":
            text_label.setText(texto)

        if aqsobjectfactory.AQUtil.sqlSelect("flsettings", "valor", "flkey='PosInfo'") == "True":
            text_ = "%s@%s" % (QSA_SYS.nameUser(), QSA_SYS.nameBD())
            if QSA_SYS.osName() == "MACX":
                text_ += "     "

            text_label2.setText(text_)

    def initDocks(self) -> None:
        """Initialize the 3 available docks."""

        self.dck_mar_ = DockListView(self.main_widget, "pinebooDockMarks", self.tr("Marcadores"))
        self.main_widget.addDockWidget(AQS.DockLeft, self.dck_mar_.doc_widget)
        self.dck_rec_ = DockListView(self.main_widget, "pinebooDockRecent", self.tr("Recientes"))
        self.main_widget.addDockWidget(AQS.DockLeft, self.dck_rec_.doc_widget)
        self.dck_mod_ = DockListView(self.main_widget, "pinebooDockModules", self.tr("Módulos"))
        self.main_widget.addDockWidget(AQS.DockLeft, self.dck_mod_.doc_widget)

        windowMenu = cast(
            QtWidgets.QMenu, self.main_widget.findChild(QtWidgets.QMenu, "windowMenu")
        )
        sub_menu = windowMenu.addMenu(self.tr("&Vistas"))

        docks = cast(List[DockListView], self.main_widget.findChildren(DockListView))
        for dock in docks:
            ac = sub_menu.addAction(dock.doc_widget.windowTitle())
            ac.setCheckable(True)
            # FIXME: Comprobar si estoy visible o no
            # ac.setChecked(dock.doc_widget.isVisible())
            dock.set_visible.connect(ac.setChecked)
            ac.triggered.connect(dock.change_state)
            cast(QtCore.pyqtSignal, dock.doc_widget.topLevelChanged).connect(ac.setChecked)
            # dock.doc_widget.Close.connect(ac.setChecked)

    def cloneAction(self, act, parent) -> Any:
        """Clone one action into another."""

        ac = QtWidgets.QAction(parent)
        ac.setObjectName(act.objectName())
        ac.setText(act.text())
        ac.setStatusTip(act.statusTip())
        ac.setToolTip(act.toolTip())
        ac.setWhatsThis(act.whatsThis())
        ac.setEnabled(act.isEnabled())
        ac.setVisible(act.isVisible())
        ac.triggered.connect(act.trigger)
        ac.toggled.connect(act.toggle)
        if not act.icon().isNull():
            ac.setIcon(self.iconSet16x16(act.icon().pixmap(16, 16)))

        return ac

    def addWidgetActions(self, node, action_group, wi) -> None:
        """Add actions belonging to a widget."""
        actions = node.elementsByTagName("action")
        if len(actions) == 0:
            actions = node.elementsByTagName("addaction")
        hide_group = True
        for i in range(len(actions)):
            item = actions.at(i).toElement()
            action_widget = wi.findChild(QtWidgets.QAction, item.attribute("name"))
            if action_widget is None:
                continue

            if action_widget.isVisible():
                hide_group = False

            prev = item.previousSibling().toElement()
            if not prev.isNull() and prev.tagName() == "separator":
                sep_ = action_group.addAction("separator")
                sep_.setObjectName("separator")
                sep_.setSeparator(True)
                # actGroup.addSeparator()

            self.cloneAction(action_widget, action_group)

        if hide_group:
            action_group.setVisible(False)

    def widgetActions(self, ui_file: str, parent: Any) -> Any:
        """Collect the actions provided by a widget."""
        mng = application.PROJECT.conn_manager.managerModules()
        doc = QtXml.QDomDocument()
        cc = mng.contentCached(ui_file)
        if not cc or not doc.setContent(cc):
            if cc:
                LOGGER.warning("No se ha podido cargar %s" % (ui_file))
            return None

        w = mng.createUI(ui_file)
        if w is None:
            raise Exception("Failed to create UI from %r" % ui_file)
        if not isinstance(w, QtWidgets.QMainWindow):
            if w:
                self.main_widgets_[w.objectName()] = w

            return None

        w.setObjectName(parent.objectName())

        if application.PROJECT.aq_app.acl_:
            application.PROJECT.aq_app.acl_.process(w)

        # flapplication.aqApp.setMainWidget(w)

        # if (QSA_SYS.isNebulaBuild()):
        #    w.show()

        w.hide()

        reduced = settings.CONFIG.value("ebcomportamiento/ActionsMenuRed", False)
        root = doc.documentElement().toElement()
        ag = QtWidgets.QActionGroup(parent)
        ag.setObjectName("%sActions" % parent.objectName())

        if root.attribute("version") == "3.3":
            bars = root.namedItem("toolbars").toElement()
            menu = root.namedItem("menubar").toElement()
            items = menu.elementsByTagName("item")

        else:
            widgets = root.elementsByTagName("widget")
            for widget in range(widgets.size()):
                if widgets.item(widget).toElement().attribute("class") == "QToolBar":
                    bars = widgets.item(widget).toElement()
                elif widgets.item(widget).toElement().attribute("class") == "QMenuBar":
                    menu_ = widgets.item(widget)
                    items = menu_.toElement().elementsByTagName("widget")

        if not reduced:
            self.addWidgetActions(bars, ag, w)

        if len(items) > 0:
            if not reduced:
                sep_ = ag.addAction("separator")
                sep_.setObjectName("separator")
                sep_.setSeparator(True)

                menu_ag = QtWidgets.QActionGroup(ag)
                menu_ag.setObjectName("%sMore" % ag.objectName())
                menu_ag_name = QtWidgets.QAction(menu_ag)
                menu_ag_name.setObjectName("%s_actiongroup_name" % ag.objectName())
                menu_ag_name.setText(self.tr("Mas"))
                menu_ag_name.setIcon(QtGui.QIcon(AQS.pixmap_fromMimeSource("plus.png")))
            else:
                menu_ag = QtWidgets.QActionGroup(ag)
                menu_ag.setObjectName(ag.objectName())

            for i in range(len(items)):
                itn = items.at(i).toElement()
                if itn.parentNode().toElement().tagName() == "item":
                    continue

                sub_menu_ag = QtWidgets.QActionGroup(menu_ag)

                if root.attribute("version") == "3.3":
                    text = itn.attribute("text")
                else:
                    text = itn.text()

                if not reduced:
                    sub_menu_ag.setObjectName("%sActions" % menu_ag.objectName())

                else:
                    sub_menu_ag.setObjectName(text)

                sub_menu_ag_name = QtWidgets.QAction(sub_menu_ag)
                sub_menu_ag_name.setObjectName("%s_actiongroup_name" % sub_menu_ag.objectName())
                sub_menu_ag_name.setText(QSA_SYS.toUnicode(text, "iso-8859-1"))

                self.addWidgetActions(itn, sub_menu_ag, w)

        conns = root.namedItem("connections").toElement()
        connections = conns.elementsByTagName("connection")
        mapped_list: List[str] = []
        for i in range(connections.length()):
            itn = connections.at(i).toElement()
            sender = itn.namedItem("sender").toElement().text()
            ac = ag.findChild(QtWidgets.QAction, sender)
            if ac:

                signal = itn.namedItem("signal").toElement().text()
                if signal in ["activated()", "triggered()"]:
                    signal_fix = "triggered"
                    signal = "triggered()"

                slot = itn.namedItem("slot").toElement().text()
                if self.act_sig_map_ is not None:
                    map_name = "%s:%s:%s" % (signal, slot, ac.objectName())
                    if map_name not in mapped_list:
                        getattr(ac, signal_fix).connect(self.act_sig_map_.map)
                        self.act_sig_map_.setMapping(ac, map_name)
                        mapped_list.append(map_name)
                # getattr(ac, signal).connect(self.act_sig_map_.map)
                # ac.triggered.connect(self.triggerAction)

                # print("Guardando señales  %s:%s:%s de %s" % (signal, slot, ac.name, ac))

        # flapplication.aqApp.setMainWidget(None)
        w.close()
        return ag

    def iconSet16x16(self, pix: "QtGui.QPixmap") -> "QtGui.QIcon":
        """Reduce the size of a pixmap to 16 * 16."""

        p_ = QtGui.QPixmap(pix)
        # img_ = p_.convertToImage()
        # img_.smoothScale(16, 16)
        # ret = QtGui.QIconSet(QPixmap(img_))
        img_ = QtGui.QImage(p_)
        if not img_.isNull():
            img_ = img_.scaled(16, 16)
        ret = QtGui.QIcon(QtGui.QPixmap(img_))
        return ret

    def show(self) -> None:
        """Show the mainform."""

        super(MainForm, self).show()
        self.activateWindow()

    def initScript(self) -> None:
        """Startup process."""

        application.PROJECT.aq_app.main_widget_ = self

        self.createUi(utils_base.filedir("plugins/mainform/eneboo/mainform.ui"))

        self.init()

        self.updateMenuAndDocks()
        self.initModule("sys")
        self.show()
        self.readState()

    def reinitSript(self) -> None:
        """Re-start process."""
        main_wid = (
            application.PROJECT.aq_app.mainWidget()
            if self.main_widget is None
            else self.main_widget
        )
        if main_wid is None or main_wid.objectName() != "container":
            return

        mw = self
        # mw.initFormWidget(main_wid)
        mw.writeState()
        mw.removeAllPages()
        cast(
            QtWidgets.QAction, mw.main_widget.findChild(QtWidgets.QAction, "aboutQtAction")
        ).triggered.disconnect(application.PROJECT.aq_app.aboutQt)
        cast(
            QtWidgets.QAction, mw.main_widget.findChild(QtWidgets.QAction, "aboutPinebooAction")
        ).triggered.disconnect(application.PROJECT.aq_app.aboutPineboo)
        mw.updateMenuAndDocks()
        mw.initModule("sys")
        mw.readState()

    def triggerAction(self, signature: str) -> None:
        """Start a process according to a given pattern."""
        mw = self
        sgt = signature.split(":")
        # ok = True
        if mw.ag_menu_ is None:
            raise Exception("Not initialized")
        ac: Optional[QtWidgets.QAction] = cast(
            QtWidgets.QAction, mw.ag_menu_.findChild(QtWidgets.QAction, sgt[2])
        )
        if ac is None:
            LOGGER.debug("triggerAction: Action not Found: %s" % signature)
            return

        signal = sgt[0]
        if signal == "triggered()":
            if not ac.isVisible() or not ac.isEnabled():
                return
        else:
            LOGGER.debug("triggerAction: Unhandled signal: %s" % signature)
            return

        fn_ = sgt[1]
        if fn_ == "initModule()":
            mw.initModule(ac.objectName().replace("_actiongroup_name", ""))

        elif fn_ == "openDefaultForm()":
            mw.addForm(ac.objectName(), ac.icon().pixmap(16, 16))
            mw.addRecent(ac)

        elif fn_ == "execDefaultScript()":
            mw.addRecent(ac)
            action_name = ac.objectName()
            if action_name in application.PROJECT.actions.keys():
                application.PROJECT.actions[action_name].execMainScript(action_name)

        elif fn_ == "loadModules()":
            QSA_SYS.loadModules()

        elif fn_ == "exportModules()":
            QSA_SYS.exportModules()

        elif fn_ == "importModules()":
            QSA_SYS.importModules()

        elif fn_ == "updatePineboo()":
            QSA_SYS.updatePineboo()

        elif fn_ == "staticLoaderSetup()":
            application.PROJECT.aq_app.staticLoaderSetup()

        elif fn_ == "reinit()":
            QSA_SYS.reinit()

        elif fn_ == "mrProper()":
            QSA_SYS.Mr_Proper()

        elif fn_ == "shConsole()":
            application.PROJECT.aq_app.showConsole()

        elif fn_ == "exit()":
            self.close()

        else:
            LOGGER.debug("tiggerAction: Unhandled slot : %s" % signature)

    @classmethod
    def setDebugLevel(self, q: int) -> None:
        """Specify debug level."""

        self.debugLevel = q

    def child(self, name: str) -> Optional[QtCore.QObject]:
        """Find a child widget."""

        return self.main_widget.findChild(QtWidgets.QWidget, name)

    def setCaptionMainWidget(self, value) -> None:
        """Set application title."""

        self.setWindowTitle("Pineboo %s - %s" % (application.PROJECT.version, value))


mainWindow: MainForm
# mainWindow = MainForm()
