# -*- coding: utf-8 -*-
from pineboolib.qsa import *
from pineboolib import decorators
from PyQt5 import QtWidgets


class MainForm(object):

    MAX_RECENT = 10
    app_ = None
    ag_menu_ = None
    ag_rec_ = None
    ag_mar_ = None
    dck_mod_ = None
    dck_rec_ = None
    dck_mar_ = None
    tw_ = None
    tw_corner = None  # deprecated
    act_sig_map_ = None
    initialized_mods_ = None
    main_widgets_ = None
    lista_tabs_ = []

    def __init__(self):
        self.ui_ = None
        self.w_ = QMainWindow()
        #self.app_ = QApplication

    def activateWindow(self):
        self.w_.activateWindow()

    @decorators.Deprecated
    def load(self):
        self.initScript()

    def eventFilter(self, o, e):
        if e.type() == AQS.ContextMenu:
            if o == getattr(self.dck_mod_, "w_", None):
                return self.addMarkFromItem(self.dck_mod_.lw_.currentItem(), e.eventData.globalPos)
            elif o == getattr(self.dck_rec_, "w_", None):
                return self.addMarkFromItem(self.dck_rec_.lw_.currentItem(), e.eventData.globalPos)
            elif o == getattr(self.dck_mar_, "w_", None):
                return self.addMarkFromItem(self.dck_mar_.lw_.currentItem(), e.eventData.globalPos)

            pinebooMenu = self.w_.child("pinebooMenu")
            pinebooMenu.exec(e.eventData.globalPos)
            return True

        elif e.type() == AQS.Close:
            if aqApp.mainWidget() and o == aqApp.mainWidget():
                self.w_.setDisabled(True)
                ret = self.exit()
                if not ret:
                    self.w_.setDisabled(False)

                return True

            if o.rtti() == "FormDB":
                self.formClosed(o)

        elif e.type() == AQS.WindowStateChange:
            if sys.isNebulaBuild() and o == self.w_:
                if self.w_.minimized():
                    self.w_.showNormal()
                    self.w_.showFullScreen()
                    return True

                if not self.w_.fullScreen():
                    self.w_.showFullScreen()
                    return True

        return False

    def createUi(self, ui_file):
        mng = aqApp.db().managerModules()
        self.w_ = mng.createUI(ui_file, None, self.w_)
        self.w_.setObjectName("container")

    def exit(self):
        res = MessageBox.Information(sys.translate("¿Quiere salir de la aplicación?"),
                                     MessageBox.Yes, MessageBox.No, MessageBox.NoButton, "Pineboo")
        doExit = True if res == MessageBox.Yes else False
        if doExit:
            self.writeState()
            self.w_.removeEventFilter(self.w_)
            aqApp.generalExit(false)
            self.removeAllPages()

        return doExit

    def writeState(self):
        w = self.w_
        self.dck_mod_.writeState()
        self.dck_rec_.writeState()
        self.dck_mar_.wirteState()

        setting = AQSettings
        key = "MainWindow/"

        settings.writeEntry("%smaximized" % key, w.maximized())
        settings.writeEntry("%sx" % key, w.x())
        settings.writeEntry("%sy" % key, w.y())
        settings.writeEntry("%swidth" % key, w.width())
        settings.writeEntry("%sheight" % key, w.height())

        key += "%s/" % aqApp.db().database()

        open_actions = []

        for i in len(self.tw_):
            open_actions.append(tw.page(i).idMDI())

        settings.writeEntry("%sopenActions" % key, open_actions)
        settings.writeEntry("%scurrentPageIndex" % key, self.tw_.currentPageIndex())

        recent_actions = []
        item = self.dck_rec_.lw_.firstChild()
        while item:
            recent_actions.append(item.text(1))
            item = item.nextSibling()
        settings.writeEntry("%srecentActions" % key, open_actions)

        mark_actions = []
        item = self.dck_mar_.lw_.firstChild()
        while item:
            mark_actions.append(item.text(1))
            item = item.nextSibling()
        settings.writeEntry("%smarkActions" % key, mark_actions)

    def readState(self):
        w = self.w_
        self.dck_mod_.readState()
        self.dck_rec_.readState()
        self.dck_mar_.readState()

        settings = AQSettings()
        key = "MainWindow/"

        if not sys.isNebulaBuild():
            maximized = settings.readBoolEntry("%smaximized" % key)

            if not maximized:
                x = settings.readNumEntry("%sx" % key)
                y = settings.readNumEntry("%sy" % key)
                if sys.osName() == "MACX" and y < 20:
                    y = 20
                w.move(x, y)
                w.resize(settings.readNumEntry("%swidth" % key, w.width()),
                         settings.readNumEntry("%sheight" % key, w.height()))
            else:
                w.showMaximized()
        else:
            w.showFullScreen()
            aqApp.setProxyDesktop(w)

        if self.ag_menu_:
            key += "%s/" % aqApp.db().database()

            open_actions = settings.readListEntry("%sopenActions" % key)
            i = 0
            while i < self.tw_.count():
                self.tw_.page(i).close()
                i += 1

            for open_action in open_actions:
                action = self.ag_menu_.child(open_action, "QAction")
                if not action:
                    continue
                module_name = aqApp.db().managerModules().idModuleOfFile("%s.ui" % action.name)
                if module_name:
                    self.initModule(module_name)

                self.addForm(open_actions[i], action.iconSet().pixmap())

            idx = settings.readNumEntry("%scurrentPageIndex" % key)
            if idx > 0 and idx < len(self.tw_):
                self.tw_.setCurrentPage(idx)

            recent_actions = settings.readListEntry("%srecentActions" % key)
            for recent in reversed(recent_actions):
                self.addRecent(self.ag_menu_.child(recent), "QAction")

            mark_actions = settings.readListEntry("%srecentActions" % key)
            for mark in reversed(mark_actions):
                self.addMark(self.ag_menu_.child(mark), "QAction")

    def init(self):
        self.w_.statusBar().hide()
        self.main_widgets_ = []
        self.initialized_mods_ = {}
        self.act_sig_map_ = QSignalMapper(self.w_, "pinebooActSignalMap")
        # self.act_sig_map_.mapped.connect(self.app_.triggerAction)
        self.act_sig_map_.mapped[str].connect(self.triggerAction)
        self.initTabWidget()
        self.initHelpMenu()
        self.initConfigMenu()
        self.initTextLabels()
        self.initDocks()
        self.initEventFilter()

    def initFromWidget(self, w):
        self.w_ = w
        self.main_widgets_ = []
        self.initialized_mods_ = {}
        self.act_sig_map_ = QSignalMapper(self.w_, "pinebooActSignalMap")
        self.tw_ = w.findChild(QtWidgets.QTabWidget, "tabWidget")
        #self.tw_corner = self.tw_.child("tabWidgetCorner","Qtoolbutton")
        # self.tw_corner.clicked.connect(self.removeCurrentPage)
        self.agMenu_ = w.child("pinebooActionGroup", "QActionGroup")
        self.dck_mod_ = DockListView()
        self.dck_mod_.initFromWidget(w.child("pinebooDockModules", "QDockWindow"))
        self.dck_rec_ = DockListView()
        self.dck_rec_.initFromWidget(w.child("pinebooDockRecent", "QDockWindow"))
        self.dck_mar_ = DockListView()
        self.dck_mar_.initFromWidget(w.child("pinebooDockMark", "QDockWindow"))
        self.initEventFilter()

    def initEventFilter(self):

        #w = self.w_
        self.w_.eventFilterFunction = "aqAppScript.mainWindow_.eventFilter"
        if not sys.isNebulaBuild():
            self.w_.allow_events = [AQS.ContextMenu, AQS.Close]
        else:
            self.w_.allow_events = [AQS.ContextMenu, AQS.Close, AQS.WindowStatechange]

        self.w_.installEventFilter(self.w_)

        self.dck_mod_.w_.installEventFilter(self.w_)
        self.dck_rec_.w_.installEventFilter(self.w_)
        self.dck_mar_.w_.installEventFilter(self.w_)

    def initModule(self, module):

        if module in self.main_widgets_:
            mwi = self.main_widgets_[module]
            mwi.name = module
            aqApp.name = module
            mwi.show()

        if module not in self.initialized_mods_ or self.initialized_mods_[module] is not True:
            self.initialized_mods_[module] = True
            aqApp.call("%s.iface.init" % module, [])

        mng = aqApp.db().managerModules()
        mng.setActiveIdModule(module)

    def removeCurrentPage(self):
        page = self.tw_.currentPage()
        if not page:
            return

        if page.rtti() == "FormDB":
            page.close()

    def removeAllPages(self):
        tw = self.tw_

        # if len(tw):
        #    self.tw_corner.hide()

        for page in tw.pages():
            if page.rtti() == "FLFormDB":
                page.close()

    def formClosed(self):
        if len(self.tw_.pages()) == 1 and self.tw_corner:
            self.tw_corner.hide()

    def addForm(self, action_name, icono):
        tw = self.tw_

        for i in range(tw.count()):
            if tw.widget(i).objectName() == action_name:
                tw.widget(i).close()

        fm = AQFormDB(action_name, tw, None)
        # fm.setMainWidget()
        if fm.mainWidget == None:
            return

        tw.addTab(fm, self.ag_menu_.findChild(QtWidgets.QAction, action_name).icon(), fm.caption)
        fm.setIdMDI(action_name)
        fm.show()

        idx = tw.indexOf(fm)
        self.tw_.setCurrentPage(idx)
        fm.installEventFilter(self.w_)
        # if len(tw.pages()) == 1 and self.tw_corner is not None:
        #    self.tw_corner.show()

    def addRecent(self, action):
        if not action:
            return

        if not self.ag_rec_:
            self.ag_rec_ = QActionGroup(self.w_)
            self.ag_rec_.setObjectName("pinebooAgRec")

        agr = self.ag_rec_
        ac = agr.findChild(QtWidgets.QAction, action.objectName())
        check_max = True
        if ac:
            agr.removeAction(ac)
            check_max = False

        ac = self.cloneAction(action, agr)
        ac.triggered.connect(action.activate)

        lw = self.dck_rec_.lw_
        item_len = 0
        it = lw.headerItem()
        while lw.itemBelow(it):
            item_len += 1

        if check_max and item_len >= self.MAX_RECENT:
            ac = agr.findChild(QtWidgets.QAction, lw.lastItem().text(1))
            if ac:
                agr.removeAction(ac)

        self.dck_rec_.update(agr, True)

    def addMark(self, action):
        if not action:
            return
        if not self.ag_mar:
            self.ag_mar_ = QActionGroup(self.w_, "pinebooAgMar")

        ac = self.cloneAction(action, self.ag_mar_)
        ac.triggered.connect(action.activate)

        self.dck_mar_.update(self.ag_mar_)

    def addMarkFromItem(self, item, pos):
        if not item:
            return False

        if item.text(1) is None:
            return True

        popMenu = QPopupMenu()
        popMenu.insertItem(sys.translate("Añadir Marcadores"), 1)
        if popMenu.exec_(pos) == 1:
            ac = self.ag_menu_.child(item.text(1))
            if ac:
                self.addMark(ac)

        return True

    def removeMarkFromItem(self, item, pos):
        if not item or not self.ag_mar_ or self.dck_mar_.lw_.childCount == 0:
            return False

        if item.text(1) is None:
            return True

        popMenu = QPopupMenu()
        popMenu.insertItem(sys.translate("Eliminar Marcador"), 1)
        if popMenu.exec_(pos) == 1:
            ac = self.ag_mar_.child(item.text(1))
            if ac:
                self.ag_mar_.removeChild(ac)
                self.dck_mar_.update(self.ag_mar_)

        return True

    def updateMenuAndDocks(self):

        self.updateActionGroup()
        pinebooMenu = self.w_.findChild(QtWidgets.QMenu, "menuPineboo")
        pinebooMenu.clear()
        for ac in self.ag_menu_.actions():
            a_ = pinebooMenu.addAction(ac.text())
            self.cloneAction(a_, ac)

        aqApp.setMainWidget(self.w_)

        self.dck_mod_.update(self.ag_menu_)
        self.dck_rec_.update(self.ag_rec_)
        self.dck_mar_.update(self.ag_mar_)

        self.w_.findChild(QtWidgets.QAction, "aboutQtAction").triggered.connect(aqApp.aboutQt)
        self.w_.findChild(QtWidgets.QAction, "aboutPinebooAction").triggered.connect(aqApp.aboutPineboo)
        self.w_.findChild(QtWidgets.QAction, "fontAction").triggered.connect(aqApp.chooseFont)
        self.w_.findChild(QtWidgets.QAction, "styleAction").triggered.connect(aqApp.showStyles)
        self.w_.findChild(QtWidgets.QAction, "helpIndexAction").triggered.connect(aqApp.helpIndex)
        self.w_.findChild(QtWidgets.QAction, "urlEnebooAction").triggered.connect(aqApp.urlPineboo)

    def updateActionGroup(self):

        if self.ag_menu_:
            list_ = AQObjectQueryList(self.ag_menu_, "QAction", "", True, True)
            for obj in list_:
                self.ag_menu_.removeChild(obj)

            self.w_.removeChild(self.ag_menu_)
            self.ag_menu_ = None

        self.ag_menu_ = QActionGroup(self.w_)
        self.ag_menu_.setObjectName("pinebooActionGroup")
        ac_name = QAction(self.ag_menu_)
        ac_name.setObjectName("pinebooActionGroup_actiongroup_name")
        ac_name.setText(sys.translate("Menú"))

        mng = aqApp.db().managerModules()
        areas = mng.listIdAreas()
        for area in areas:
            ag = QActionGroup(self.ag_menu_)
            ag.setObjectName(area)
            if not sys.isDebuggerEnabled() and ag.name == "sys":
                break
            ag_action = QAction(ag)
            ag_action.setObjectName("%s_actiongroup_name" % ag.objectName())
            ag_action.setText(mng.idAreaToDescription(ag.objectName()))
            ag_action.setIcon(QIcon(AQS.Pixmap_fromMineSource("folder.png")))

            modules = mng.listIdModules(ag.objectName())
            for module in modules:
                if module == "sys" and sys.isUserBuild():
                    continue
                ac = QActionGroup(ag)
                ac.setObjectName(module)
                if sys.isQuickBuild():
                    if ac.name == "sys":
                        continue
                actions = self.widgetActions("%s.ui" % ac.objectName(), ac)

                if not actions:
                    ac.setObjectName(None)
                    ac.deleteLater()
                    ac = QAction(ag)
                    ac.setObjectName(module)

                ac_action = QAction(ac)
                ac_action.setObjectName("%s_actiongroup_name" % ac.objectName())
                ac_action.setText(mng.idModuleToDescription(ac.objectName()))
                ac_action.setIcon(self.iconSet16x16(mng.iconModule(ac.objectName())))

                ac_action.triggered.connect(self.act_sig_map_.map)
                self.act_sig_map_.setMapping(
                    ac_action, "triggered():initModule():%s_actiongroup_name" % ac.objectName())
                if ac.objectName() == "sys" and ag.objectName() == "sys":
                    if sys.isDebuggerMode():
                        staticLoad = QAction(ag)
                        staticLoad.setObjectName("staticLoaderSetupAction")
                        staticLoad.setText(sys.translate("Configurar carga estática"))
                        staticLoad.setIcon(QIconSet(AQS.pixmap_fromMineSource("folder_update.png")))
                        staticLoad.triggered.connect(self.act_sig_map_.map)
                        self.act_sig_map_.setMapping(
                            staticLoad, "triggered():staticLoaderSetup():%s" % staticLoad.objectName())

                        reInit = QAction(ag)
                        reInit.setObjectName("reinitAction")
                        reInit.setText(sys.translate("Recargar scripts"))
                        reInit.setIcon(QIconSet(AQS.pixmap_fromMineSource("reload.png")))
                        reInit.triggered.connect(self.act_sig_map_.map)
                        self.act_sig_map_.setMapping(reInit, "triggered():reinit():%s" % reInit.objectName())

        shConsole = QAction(self.ag_menu_)
        shConsole.setObjectName("shConsoleAction")
        shConsole.setText(sys.translate("Mostrar Consola de mensajes"))
        shConsole.setIcon(QIcon(AQS.Pixmap_fromMineSource("consola.png")))
        shConsole.triggered.connect(self.act_sig_map_.map)
        self.act_sig_map_.setMapping(shConsole, "triggered():shConsole():%s" % shConsole.objectName())

        exit = QAction(self.ag_menu_)
        exit.setObjectName("exitAction")
        exit.setText(sys.translate("&Salir"))
        exit.setIcon(QIcon(AQS.Pixmap_fromMineSource("exit.png")))
        exit.triggered.connect(self.act_sig_map_.map)
        self.act_sig_map_.setMapping(exit, "triggered():exit():%s" % exit.objectName())

    def initTabWidget(self):
        self.tw_ = self.w_.findChild(QtWidgets.QTabWidget, "tabWidget")
        self.tw_.removeTab(0)
        """
        tb = self.tw_corner = QToolButton(tw, "tabWidgetCorner")
        tb.autoRaise = False
        tb.setFixedSize(16, 16)
        tb.setIconSet(self.iconset16x16(AQS.Pixmap_fromMineSource("file_close.png")))
        tb.clicked.connect(self.removeCurrentPage)
        tw.setCornerWidget(tb, AQS.TopRight)
        AQS.toolTip_add(tb, sys.translate("Cerrar pestaña"))
        tb.hide()
        """

    def initHelpMenu(self):

        aboutQt = self.w_.findChild(QtWidgets.QAction, "aboutQtAction")
        aboutQt.setIcon(self.iconSet16x16(AQS.Pixmap_fromMineSource("aboutqt.png")))
        # aboutQt.triggered.connect(aqApp.aboutQt)

        aboutPineboo = self.w_.findChild(QtWidgets.QAction, "aboutPinebooAction")
        aboutPineboo.setIcon(self.iconSet16x16(AQS.Pixmap_fromMineSource("pineboo-logo-32.png")))
        # aboutPineboo.triggered.connect(aqApp.aboutPineboo)

        helpIndex = self.w_.findChild(QtWidgets.QAction, "helpIndexAction")
        helpIndex.setIcon(self.iconSet16x16(AQS.Pixmap_fromMineSource("help_index.png")))
        # helpIndex.triggered.connect(aqApp.helpIndex)

        urlPineboo = self.w_.findChild(QtWidgets.QAction, "urlEnebooAction")
        urlPineboo.setIcon(self.iconSet16x16(AQS.Pixmap_fromMineSource("pineboo-logo-32.png")))
        # urlPineboo.triggered.connect(aqApp.urlPineboo)

    def initConfigMenu(self):

        font = self.w_.findChild(QtWidgets.QAction, "fontAction")
        font.setIcon(self.iconSet16x16(AQS.Pixmap_fromMineSource("font.png")))
        # font.triggered.connect(aqApp.chooseFont)

        style = self.w_.findChild(QtWidgets.QAction, "styleAction")
        style.setIcon(self.iconSet16x16(AQS.Pixmap_fromMineSource("estilo.png")))
        # style.triggered.connect(aqApp.showStyles)

    def initTextLabels(self):

        tL = self.w_.findChild(QtWidgets.QLabel, "tLabel")
        tL2 = self.w_.findChild(QtWidgets.QLabel, "tLabel2")
        texto = AQUtil.sqlSelect("flsettings", "valor", "flkey='verticalName'")
        if texto:
            tL.text = texto

        if not AQUtil.sqlSelect("flsettings", "valor", "flkey='PosInfo'"):
            tL2.text = "%s@%s" % (sys.nameUser(), sys.nameBD())
            if sys.osName() == "MACX":
                tL2.text += "     "

    def initDocks(self):
        self.dck_mar_ = DockListView(self.w_, "pinebooDockMarks", sys.translate("Marcadores"))
        self.w_.addDockWidget(AQS.DockLeft, self.dck_mar_.w_)
        self.dck_rec_ = DockListView(self.w_, "pinebooDockRecent", sys.translate("Recientes"))
        self.w_.addDockWidget(AQS.DockLeft, self.dck_rec_.w_)
        self.dck_mod_ = DockListView(self.w_, "pinebooDockModules", sys.translate("Módulos"))
        self.w_.addDockWidget(AQS.DockLeft, self.dck_mod_.w_)

        windowMenu = self.w_.findChild(QtWidgets.QMenu, "windowMenu")
        # FIXMENU
        #windowMenu.insertItem(sys.translate("&Vistas"), self.w_.createDockWindowMenu(AQS.NoToolBars))
        windowMenu.addMenu(sys.translate("&Vistas"))

    def cloneAction(self, act, parent):
        ac = QAction(parent)
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

    def addActions(self, node, actGroup, wi):
        actions = node.elementsByTagName("action")
        i = 0
        while i < actions.length():
            itn = actions.at(i).toElement()
            acw = wi.findChild(QtWidgets.QAction, itn.attribute("name"))
            if acw is None:
                i += 1
                continue

            prev = itn.previousSibling().toElement()
            if not prev.isNull() and prev.tagName() == "separator":
                sep_ = actGroup.addAction("separator")
                sep_.setObjectName("separator")
                sep_.setSeparator(True)
                # actGroup.addSeparator()

            self.cloneAction(acw, actGroup)
            i += 1

    def widgetActions(self, ui_file, parent):
        mng = aqApp.db().managerModules()
        doc = QDomDocument()
        cc = mng.contentCached(ui_file)
        if not cc or not doc.setContent(cc):
            print("WARN::%s::widgetActions::No se ha podido cargar %s" % (__name__, ui_file))
            return None

        w = mng.createUI(ui_file)
        if not w or not w.inherits("QMainWindow"):
            if w:
                self.main_widgets_[w.name] = w

            return None

        w.name = parent.objectName()
        # aqApp.setMainWidget(w)
        # if (sys.isNebulaBuild()):
        #    w.show()

        w.hide()

        settings = AQSettings()
        reduced = settings.readBoolEntry("ebcomportamiento/ActionsMenuRed")
        root = doc.documentElement().toElement()

        ag = QActionGroup(parent)
        ag.setObjectName("%sActions" % parent.objectName())
        #ag.menuText = ag.text = sys.translate("Acciones")
        if not reduced:
            bars = root.namedItem("toolbars").toElement()
            self.addActions(bars, ag, w)

        menu = root.namedItem("menubar").toElement()
        items = menu.elementsByTagName("item")
        if len(items) > 0:
            if not reduced:
                sep_ = ag.addAction("separator")
                sep_.setObjectName("separator")
                sep_.setSeparator(True)

                menu_ag = QActionGroup(ag)
                menu_ag.setObjectName("%sMore" % ag.objectName())
                menu_ag_name = QAction(menu_ag)
                menu_ag_name.setObjectName("%s_actiongroup_name" % ag.objectName())
                menu_ag_name.setText(sys.translate("Más"))
                menu_ag_name.setIcon(QIcon(AQS.Pixmap_fromMineSource("plus.png")))

            i = 0
            while i < items.length():
                itn = items.at(i).toElement()
                if itn.parentNode().toElement().tagName() == "item":
                    i += 1
                    continue

                if not reduced:
                    sub_menu_ag = QActionGroup(menu_ag)
                    sub_menu_ag.setObjectName("%sActions" % menu_ag.objectName())
                else:
                    sub_menu_ag = QActionGroup(ag)
                    sub_menu_ag.setObjectName(ag.objectName())

                sub_menu_ag_name = QAction(sub_menu_ag)
                sub_menu_ag_name.setObjectName("%s_actiongroup_name" % sub_menu_ag.objectName())
                sub_menu_ag_name.setText(sys.toUnicode(itn.attribute("text"), "UTF-8"))
                self.addActions(itn, sub_menu_ag, w)
                i += 1

        conns = root.namedItem("connections").toElement()
        connections = conns.elementsByTagName("connection")
        i = 0
        while i < connections.length():
            itn = connections.at(i).toElement()
            sender = itn.namedItem("sender").toElement().text()
            ac = ag.findChild(QtWidgets.QAction, sender)
            if ac:

                signal = itn.namedItem("signal").toElement().text()
                if signal == "activated()":
                    signal_fix = "triggered"
                    signal = "triggered()"
                slot = itn.namedItem("slot").toElement().text()
                getattr(ac, signal_fix).connect(self.act_sig_map_.map)
                self.act_sig_map_.setMapping(ac, "%s:%s:%s" % (signal, slot, ac.name))
                #getattr(ac, signal).connect(self.act_sig_map_.map)
                # ac.triggered.connect(self.triggerAction)

                #print("Guardando señales  %s:%s:%s de %s" % (signal, slot, ac.name, ac))

            i += 1

        aqApp.setMainWidget(None)
        w.close()
        return ag

    def iconSet16x16(self, pix):
        p_ = QPixmap(pix)
        #img_ = p_.convertToImage()
        #img_.smoothScale(16, 16)
        #ret = QIconSet(QPixmap(img_))
        img_ = QImage(p_)
        img_ = img_.scaled(16, 16)
        ret = QIcon(QPixmap(img_))
        return ret

    def show(self):
        self.w_.show()

    def close(self):
        self.w_.close()

    def initScript(self):
        from pineboolib.utils import filedir

        mw = mainWindow
        mw.createUi(filedir('plugins/mainform/eneboo/mainform.ui'))
        mw.init()
        mw.updateMenuAndDocks()
        mw.initModule("sys")
        # mw.show()
        mw.readState()

    def reinitSript(self):
        main_wid = aqApp.mainWidget() if mainWindow.w_ is None else mainWindow.w_
        if not main_wid or main_wid.name is not "container" or main_wid is mainWindow.w_:
            return

        mw = mainWindow
        mw.initFormWidget(main_wid)
        mw.writeState()
        mw.removeAllPages()
        mw.updateMenuAndDocks()
        mw.initModule("sys")
        mw.readState()

    def aqAppScriptMain(self):
        pass

    def triggerAction(self, signature):
        mw = mainWindow
        sgt = signature.split(":")
        ok = True
        ac = mw.ag_menu_.findChild(QtWidgets.QAction, sgt[2])
        if ac is None:
            debug("triggerAction: Action not Found: %s" % signature)
            return

        signal = sgt[0]
        if signal == "triggered()":
            if not ac.isVisible() or not ac.isEnabled():
                return
        else:
            debug("triggerAction: Unhandled signal: %s" % signature)
            return

        fn_ = sgt[1]
        if fn_ == "initModule()":
            mw.initModule(ac.objectName().replace("_actiongroup_name", ""))

        elif fn_ == "openDefaultForm()":
            mw.addForm(ac.name, ac.icon().pixmap(16, 16))
            mw.addRecent(ac)

        elif fn_ == "execDefaultScript()":
            aqApp.execMainScript(ac.objectName())
            mw.addRecent(ac)

        elif fn_ == "loadModules()":
            sys.loadModules()

        elif fn_ == "exportModules()":
            sys.exportModules()

        elif fn_ == "importModules()":
            sys.importModules()

        elif fn_ == "updatePineboo()":
            sys.updatePineboo()

        elif fn_ == "dumpDatabase()":
            sys.dumpDatabase()

        elif fn_ == "staticLoaderSetup()":
            aqApp.staticLoaderSetup()

        elif fn_ == "reinit()":
            sys.reinit()

        elif fn_ == "mrProper()":
            sys.Mr_Proper()

        elif fn_ == "shConsole()":
            aqApp.showConsole()

        elif fn_ == "exit()":
            mw.close()

        else:
            debug("tiggerAction: Unhandled slot : %s" % signature)

    # def load(self):
    #    from pineboolib.utils import filedir
    #    self.ui_ = pineboolib.project.conn.managerModules().createUI(filedir('plugins/mainform/eneboo/mainform.ui'), None, self)

    @classmethod
    def setDebugLevel(self, q):
        MainForm.debugLevel = q


class DockListView(object):

    w_ = None
    lw_ = None
    ag_ = None

    def __init__(self, parent, name, title):
        if parent is None:
            return

        self.w_ = QtWidgets.QDockWidget(name, parent)

        self.lw_ = QTreeWidget(self.w_)
        self.lw_.setObjectName("%sListView" % name)

        # this.lw_.addColumn("");
        # this.lw_.addColumn("");
        self.lw_.setColumnCount(2)
        self.lw_.setHeaderLabels(["", ""])
        self.lw_.headerItem().setHidden(True)
        # this.lw_.setSorting(-1);
        #this.lw_.rootIsDecorated = true;
        #this.lw_.setColumnWidthMode(1, 0);
        self.lw_.hideColumn(1)
        # self.lw_.headerItem().hide()
        #self.lw_.headerItem().setResizeEnabled(false, 1)

        self.w_.setWidget(self.lw_)
        self.w_.setWindowTitle(title)

        """
        w.resizeEnabled = true;
        w.closeMode = true;
        w.setFixedExtentWidth(300);
        """

        self.lw_.doubleClicked.connect(self.activateAction)

    def writeState(self):

        settings = AQSettings()
        key = "MainWindow/%s/" % self.w_.objectName()
        settings.writeEntry("%splace" % key, self.w_.place())  # Donde está emplazado
        settings.writeEntry("%svisible" % key, self.w_.isVisible())
        settings.writeEntry("%sx", key, self.w_.x())
        settings.writeEntry("%sy", key, self.w_.y())
        settings.writeEntry("%swidth", key, self.w_.width())
        settings.writeEntry("%sheight", key, self.w_.height())
        #settings.writeEntry("%soffset", key, self.offset())
        area = self.area()
        settings.writeEntry("%sindex", key, area.findDockWindow(self.w_) if area else None)

    def readState(self):

        settings = AQSettings()
        key = "MainWindow/%s/" % self.w_.objectName()
        place = settings.readNumEntry("%splace" % key, AQS.InDock)
        if place == AQS.OutSideDock:
            self.w_.setFloating(True)
            self.w_.move(settings.readNumEntry("%sx" % key, self.w_.x()),
                         settings.readNumEntry("%sy" % key, self.w_.y()))

        #self.w_.offset = settings.readNumEntry("%soffset" % key, self.offset)
        index = settings.readNumEntry("%sindex" % key, None)
        # FIXME
        # if index is not None:
        #    area = w.area()
        #    if area:
        #        area.moveDockWindow(w, index)

        width = settings.readNumEntry("%swidth" % key, self.w_.width())
        height = settings.readNumEntry("%sheight" % key, self.w_.height())
        self.lw_.resize(width, height)
        self.w_.resize(width, height)
        visible = settings.readNumEntry("%svisible" % key, True)
        if visible:
            self.w_.show()
        else:
            self.w_.hide()

    def initFromWidget(self, w):
        self.w_ = w
        self.lw_ = w.widget()
        self.lw_.doubleClicked.connect(self.activateAction)

    def activateAction(self, item):
        if item is None:
            return

        action_name = item.siblingAtColumn(1).data()
        if action_name == "":
            return

        ac = self.ag_.findChild(QtWidgets.QAction, action_name)
        if ac:
            ac.triggered.emit()

    def update(self, action_group, reverse=False):
        self.ag_ = action_group
        self.lw_.clear()
        if not action_group:
            return
        self.buildListView(self.lw_, AQS.toXml(action_group), action_group, reverse)

    def buildListView(self, parent_item, parent_element, ag, reverse):
        this_item = None
        node = parent_element.lastChild().toElement() if reverse else parent_element.firstChild().toElement()
        while not node.isNull():
            if node.attribute("objectName") in("", "separator"):  # Pasamos de este
                node = node.previousSibling().toElement() if reverse else node.nextSibling().toElement()
                continue
            class_name = node.attribute("class")
            if node.tagName() == "object" and class_name.startswith("QAction"):
                if node.attribute("visible") == "false":
                    node = node.previousSibling().toElement() if reverse else node.nextSibling().toElement()
                    continue

                if class_name == "QActionGroup":
                    group_name = node.attribute("objectName")
                    if (group_name not in ("pinebooActionGroup") and not group_name.endswith("Actions") and not group_name.startswith(("pinebooAg"))) or group_name.endswith("MoreActions"):

                        this_item = QTreeWidgetItem(parent_item)
                        this_item.setText(0, group_name)

                    else:
                        this_item = parent_item

                    self.buildListView(this_item, node, ag, reverse)
                    node = node.previousSibling().toElement() if reverse else node.nextSibling().toElement()
                    continue

                if node.attribute("objectName") not in("pinebooActionGroup", "pinebooActionGroup_actiongroup_name"):

                    action_name = node.attribute("objectName")

                    ac = ag.findChild(QtWidgets.QAction, action_name)
                    if ac is not None:

                        if action_name.endswith("actiongroup_name"):
                            #action_name = action_name.replace("_actiongroup_name", "")
                            this_item = parent_item
                        else:
                            this_item = QTreeWidgetItem(parent_item)
                        this_item.setIcon(0, ac.icon())  # Code el icono mal!!
                        if class_name == "QAction":
                            this_item.setText(1, action_name)
                        this_item.setText(0, node.attribute("text").replace("&", ""))
                    if node.attribute("enabled") == "false":
                        this_item.setEnabled(False)

                self.buildListView(this_item, node, ag, reverse)

            node = node.previousSibling().toElement() if reverse else node.nextSibling().toElement()


mainWindow = MainForm()
