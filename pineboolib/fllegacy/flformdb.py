"""Flformdb module."""

# -*- coding: utf-8 -*-
import traceback
from PyQt5 import QtCore, QtGui, QtWidgets

from pineboolib import logging

from pineboolib.core import decorators, settings
from pineboolib.core.utils import utils_base

from pineboolib.application.utils import geometry
from pineboolib.application.metadata import pnaction
from pineboolib.application import load_script

from pineboolib.application.database import pnsqlcursor

from pineboolib import application

from . import flapplication


from typing import Any, Union, Dict, Optional, Tuple, Type, cast, Callable, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor


class FLFormDB(QtWidgets.QDialog):
    """
    Represents a form that links to a table.

    It is used as a container of components that want
    link to the database and access the records
    of the cursor. This structure greatly simplifies
    measure access to data since many tasks are
    Automatically managed by this container form.

    At first the form is created empty and we must invoke
    the FLFormDB :: setMainWidget () method, passing it as a parameter
    another widget (usually a form created with QtDesigner),
    which contains different components, this widget will be displayed
    inside this container, self-configuring all the components
    It contains, with the cursor data and metadata. Generally the
    Components will be plugins, such as FLFieldDB or FLTableDB
    """

    """
    Cursor, con los registros, utilizado por el formulario
    """

    cursor_: Optional["isqlcursor.ISqlCursor"]

    """
    Nombre de la tabla, contiene un valor no vacío cuando
    la clase es propietaria del cursor
    """
    name_: str

    """
    Capa principal del formulario
    """
    layout_: QtWidgets.QVBoxLayout

    """
    Widget principal del formulario
    """
    mainWidget_: Optional[QtWidgets.QWidget]
    """
    Identificador de ventana MDI.

    Generalmente es el nombre de la acción que abre el formulario
    """
    idMDI_: str

    """
    Capa para botones
    """
    layoutButtons: QtWidgets.QHBoxLayout

    """
    Boton Cancelar
    """
    pushButtonCancel: Optional[QtWidgets.QToolButton]

    """
    Indica que la ventana ya ha sido mostrada una vez
    """
    showed: bool

    """
    Guarda el contexto anterior que tenia el cursor
    """
    oldCursorCtxt: Any

    """
    Indica que el formulario se está cerrando
    """
    isClosing_: bool

    """
    Componente con el foco inicial
    """
    initFocusWidget_: Optional[QtWidgets.QWidget]

    """
    Guarda el último objeto de formulario unido a la interfaz de script (con bindIface())
    """
    oldFormObj: Any

    """
    Boton Debug Script
    """
    pushButtonDebug: Optional[QtWidgets.QToolButton]

    """
    Almacena que se aceptado, es decir NO se ha pulsado, botón cancelar
    """
    accepted_: bool

    """
    Nombre del formulario relativo a la acción (form / formRecrd + nombre de la acción)
    """
    actionName_: str

    """
    Interface para scripts
    """
    iface: Any

    """
    Tamaño de icono por defecto
    """
    iconSize: QtCore.QSize

    # protected slots:

    """
    Uso interno
    """
    oldFormObjDestroyed = QtCore.pyqtSignal()

    # signals:

    """
    Señal emitida cuando se cierra el formulario
    """
    closed = QtCore.pyqtSignal()

    """
    Señal emitida cuando el formulario ya ha sido inicializado y está listo para usarse
    """
    formReady = QtCore.pyqtSignal()
    formClosed = QtCore.pyqtSignal()

    known_instances: Dict[Tuple[Type["FLFormDB"], str], "FLFormDB"] = {}

    bottomToolbar: Optional[QtWidgets.QFrame]

    toolButtonClose: Optional[QtWidgets.QToolButton]

    _uiName: str
    _scriptForm: Union[Any, str]

    loop: bool
    _action: "pnaction.PNAction"
    logger = logging.getLogger("FLFormDB")

    def __init__(
        self,
        action_or_name: Union["pnaction.PNAction", str],
        parent: Optional[Union[QtWidgets.QWidget, int]] = None,
        load: Union[bool, int] = False,
    ) -> None:
        """Create a new FLFormDB for given action."""
        # self.tiempo_ini = time.time()
        parent_widget: QtWidgets.QWidget = flapplication.aqApp.mainWidget()
        if parent is None or isinstance(parent, int):
            parent_widget = flapplication.aqApp.mainWidget()
        else:
            parent_widget = parent
        # if application.project.DGI.localDesktop():  # Si es local Inicializa
        # QtWidgets.QWidget.__init__(self, parent)  # FIXME: Porqué pide dos argumentos extra??
        # super(QtWidgets.QWidget, self).__init__(parent)
        super().__init__(parent_widget)

        if isinstance(load, int):
            load = load == 1

        self._loaded = False

        if isinstance(action_or_name, str):
            self._action = application.project.conn_manager.manager().action(action_or_name)
        else:
            self._action = action_or_name

        self.known_instances[(self.__class__, self._action.name())] = self

        if type(self).__name__ == "FLFormRecordDB":
            self.actionName_ = "formRecord" + self._action.name()
            script_name = self._action.scriptFormRecord()
        else:
            if self._action.table():
                self.actionName_ = "form" + self._action.name()
                script_name = self._action.scriptForm()
            else:
                # Load of the main script (flfactppal/flfacturac)
                # Currently detected by having no table
                # FIXME: A better detection method should be placed.
                self.actionName_ = self._action.name()
                script_name = self._action.name()

        # self.mod = self._action.mod
        self.loop = False
        self.eventloop = QtCore.QEventLoop()

        self.layout_ = QtWidgets.QVBoxLayout()
        self.layout_.setContentsMargins(1, 1, 1, 1)
        self.layout_.setSpacing(1)
        self.layout_.setContentsMargins(1, 1, 1, 1)
        self.layout_.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.setLayout(self.layout_)
        self._uiName = self._action.form()
        self.pushButtonCancel = None
        self.toolButtonClose = None
        self.bottomToolbar = None
        self.cursor_ = None
        self.initFocusWidget_ = None
        self.showed = False
        self.isClosing_ = False
        self.accepted_ = False
        self.mainWidget_ = None
        self.iface = None
        self.oldFormObj = None
        self.oldCursorCtxt = None

        self.idMDI_ = self._action.name()

        self.logger.info("init: Action: %s", self._action)

        self.script = load_script.load_script(
            script_name, application.project.actions[self._action.name()]
        )
        self.widget = self.script.form
        self.widget.form = self
        if hasattr(self.widget, "iface"):
            self.iface = self.widget.iface

        if application.project._DGI is not None:
            self.iconSize = application.project.DGI.iconSize()

        if load:
            self.load()
            self.initForm()

    def load(self) -> None:
        """Load control."""
        if self._loaded:
            return

        # self.resize(550,350)
        if self.layout_ is None:
            return

        self.layout_.insertWidget(0, self.widget)
        self.layout_.setSpacing(1)
        self.layout_.setContentsMargins(1, 1, 1, 1)
        self.layout_.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

        if self._uiName:

            if application.project.conn_manager is None:
                raise Exception("Project is not connected yet")

            application.project.conn_manager.managerModules().createUI(self._uiName, None, self)

        self._loaded = True

    def loaded(self) -> bool:
        """Return if the control is initialized."""

        return self._loaded

    @decorators.pyqtSlot()
    def initScript(self) -> bool:
        """
        Call the "init" function of the masterprocess script associated with the form.
        """

        if self._loaded:
            if not getattr(self.widget, "iface", None):
                self.iface = (
                    self.widget
                )  # Es posible que no tenga ifaceCtx, así hacemos que sea polivalente

            if self.widget:
                self.widget.clear_connections()

            if hasattr(self.iface, "init"):
                try:
                    self.iface.init()
                except Exception:
                    from pineboolib.core.error_manager import error_manager

                    flapplication.aqApp.msgBoxWarning(
                        error_manager(traceback.format_exc(limit=-6, chain=False)),
                        application.project._DGI,
                    )
                    return False

            return True

        return False

    def __del__(self) -> None:
        """
        Destroyer.
        """
        # TODO: Esto hay que moverlo al closeEvent o al close()
        # ..... los métodos __del__ de python son muy poco fiables.
        # ..... Se lanzan o muy tarde, o nunca.
        # (De todos modos creo que ya hice lo mismo a mano en el closeEvent en commits anteriores)

        self.unbindIface()

    def setCursor(self, cursor: "isqlcursor.ISqlCursor" = None) -> None:  # type: ignore
        """Change current cursor binded to this control."""
        if cursor is not self.cursor_ and self.cursor_ and self.oldCursorCtxt:
            self.cursor_.setContext(self.oldCursorCtxt)

        if not cursor:
            return

        if self.cursor_ and self.cursor_ is not cursor:
            if type(self).__name__ == "FLFormRecodDB":
                self.cursor_.restoreEditionFlag(self.objectName())
                self.cursor_.restoreBrowseFlag(self.objectName())

        if self.cursor_:

            cast(QtCore.pyqtSignal, self.cursor_.destroyed).disconnect(self.cursorDestroyed)

        self.cursor_ = cursor

        if type(self).__name__ == "FLFormRecodDB":
            self.cursor_.setEdition(False, self.objectName())
            self.cursor_.setBrowse(False, self.objectName())

        cast(QtCore.pyqtSignal, self.cursor_.destroyed).connect(self.cursorDestroyed)
        if self.iface and self.cursor_:
            self.oldCursorCtxt = self.cursor_.context()
            self.cursor_.setContext(self.iface)

    def cursor(self) -> "isqlcursor.ISqlCursor":  # type: ignore [override] # noqa F821
        """
        To get the cursor used by the form.
        """
        if self.cursor_ is None:
            raise Exception("cursor_ is empty!.")

        return self.cursor_

    def mainWidget(self) -> Optional[QtWidgets.QWidget]:
        """
        To get the form's main widget.
        """

        return self.mainWidget_

    def setIdMDI(self, id_: str) -> None:
        """
        Set the MDI ID.
        """

        self.idMDI_ = id_

    def idMDI(self) -> str:
        """
        Return the MDI ID.
        """

        return self.idMDI_

    def setMainWidget(self, w: Optional[QtWidgets.QWidget] = None) -> None:
        """
        Set widget as the main form.
        """

        self.mainWidget_ = self

    def snapShot(self) -> QtGui.QImage:
        """
        Return the image or screenshot of the form.
        """
        pix = self.grab()
        return pix.toImage()

    def saveSnapShot(self, path_file: Optional[str] = None) -> None:
        """
        Save the image or screenshot of the form in a PNG format file.
        """
        if not path_file:

            tmp_file = "%s/snap_shot_%s.png" % (
                flapplication.aqApp.tmp_dir(),
                QtCore.QDateTime.currentDateTime().toString("ddMMyyyyhhmmsszzz"),
            )

            ret = QtWidgets.QFileDialog.getSaveFileName(
                QtWidgets.QApplication.activeWindow(), "Pineboo", tmp_file, "PNG(*.png)"
            )
            path_file = ret[0] if ret else None

        if path_file:
            fi = QtCore.QFile(path_file)
            if not fi.OpenMode(QtCore.QIODevice.WriteOnly):
                self.tr("Error I/O al intentar escribir el fichero %s" % path_file)
                return

            self.snapShot().save(fi, "PNG")

    def saveGeometry(self) -> QtCore.QByteArray:
        """Save current window size into settings."""
        # pW = self.parentWidget()
        # if not pW:
        geo = QtCore.QSize(self.width(), self.height())
        if self.isMinimized():
            geo.setWidth(1)
        elif self.isMaximized():
            geo.setWidth(9999)
        # else:
        #    geo = QtCore.QSize(pW.width(), pW.height())

        geometry.saveGeometryForm(self.geoName(), geo)
        return super().saveGeometry()

    def setCaptionWidget(self, text: str) -> None:
        """
        Set the window title.
        """
        if not text:
            return

        self.setWindowTitle(text)

    def accepted(self) -> bool:  # type: ignore
        """
        Return if the form has been accepted.
        """
        # FIXME: QtWidgets.QDialog.accepted() is a signal. We're shadowing it.
        return self.accepted_

    def formClassName(self) -> str:
        """
        Return the class name of the form at runtime.
        """
        return "FormDB"

    def exec_(self) -> bool:
        """
        Only to be compatible with FLFormSearchDB. By default, just call QWidget.show.
        """

        super().show()
        return True

    def hide(self) -> None:
        """Hide control."""
        super().hide()

    @decorators.pyqtSlot()
    def close(self) -> bool:
        """
        Close the form.
        """
        if self.isClosing_ or not self._loaded:
            return True

        self.isClosing_ = True

        super().close()
        self.isClosing_ = False
        return True

    @decorators.pyqtSlot()
    def accept(self) -> None:
        """
        Activated by pressing the accept button.
        """
        pass

    @decorators.pyqtSlot()
    def reject(self) -> None:
        """
        Activated by pressing the cancel button.
        """
        pass

    @decorators.pyqtSlot()
    def showForDocument(self) -> None:
        """
        Show the form without calling the script "init".

        Used in documentation to avoid conflicts when capturing forms.
        """
        self.showed = True
        if self.mainWidget_:
            self.mainWidget_.show()
            self.resize(self.mainWidget_.size())
        super().show()

    @decorators.pyqtSlot()
    @decorators.NotImplementedWarn
    def debugScript(self) -> bool:
        """
        Show the script associated with the form in the Workbench to debug.
        """

        return True

    @decorators.pyqtSlot()
    def get_script(self) -> Optional[str]:
        """
        Return the script associated with the form.
        """

        ifc = self.iface
        if ifc:
            return str(ifc)
        return None

    # private slots:

    @decorators.pyqtSlot()
    def callInitScript(self) -> None:
        """Call QS Script related to this control."""
        if not self.initScript():
            raise Exception("Error initializing the module.")

        if not self.isClosing_:
            QtCore.QTimer.singleShot(0, self.emitFormReady)

    def emitFormReady(self) -> None:
        """Emit formReady signal, after the form has been loaded."""
        from pineboolib.application.qsatypes.sysbasetype import SysBaseType

        qsa_sys = SysBaseType()
        if qsa_sys.isLoadedModule("fltesttest"):

            flapplication.aqApp.call(
                "fltesttest.iface.recibeEvento", ("formReady", self.actionName_), None
            )
        self.formReady.emit()

    # protected_:

    def emitFormClosed(self) -> None:
        """Emit formClosed signal."""

        if application.project.conn_manager is None:
            raise Exception("Project is not connected yet")

        if "fltesttest" in application.project.conn_manager.managerModules().listAllIdModules():
            application.project.call(
                "fltesttest.iface.recibeEvento", ["formClosed", self.actionName_], None
            )

        self.formClosed.emit()
        if self.widget:
            self.widget.closed.emit()

    def action(self) -> "pnaction.PNAction":
        """Get form PNAction."""
        return self._action

    def initForm(self) -> None:
        """
        Initialize the associated script.
        """
        from pineboolib.fllegacy import flapplication

        acl = flapplication.aqApp.acl()

        if acl:
            acl.process(self)

        self.loadControls()

        if self._action is None:
            raise Exception("_action is empty!")

        if self._action.table():
            if (
                not self.cursor_
                or not self.cursor_._action
                or self.cursor_._action.table() is not self._action.table()
            ):
                cursor = pnsqlcursor.PNSqlCursor(self._action.table())
                self.setCursor(cursor)

            v = None

            preload_main_filter = getattr(self.iface, "preloadMainFilter", None)

            if preload_main_filter:
                v = preload_main_filter()

            if v is not None and self.cursor_:
                self.cursor_.setMainFilter(v, False)

            # if self._loaded and not self.__class__.__name__ == "FLFormRecordDB":
            # application.project.conn_manager.managerModules().loadFLTableDBs(self)

            if self._action.description() not in ("", None):
                self.setWhatsThis(self._action.description())

            caption = self._action.caption()

            if caption in ("", None) and self.cursor_ and self.cursor_.metadata():
                caption = self.cursor_.metadata().alias()

            if caption in ("", None):
                caption = QtWidgets.QApplication.translate("FLFormDB", "No hay metadatos")
            self.setCaptionWidget(caption)

    def loadControls(self) -> None:
        """Load form controls."""

        if self.pushButtonCancel:
            self.pushButtonCancel.hide()

        if self.bottomToolbar and self.toolButtonClose:
            self.toolButtonClose.hide()
        self.bottomToolbar = QtWidgets.QFrame()

        if self.bottomToolbar is None:
            raise Exception("bottomToolBar is empty!")

        if self.iconSize is not None:
            self.bottomToolbar.setMinimumSize(self.iconSize)

        hblay = QtWidgets.QHBoxLayout()

        hblay.setContentsMargins(0, 0, 0, 0)
        hblay.setSpacing(0)
        hblay.addStretch()
        self.bottomToolbar.setLayout(hblay)
        self.bottomToolbar.setFocusPolicy(QtCore.Qt.NoFocus)
        if self.layout_ is not None:
            self.layout_.addWidget(self.bottomToolbar)
        # if self.layout:
        #    self.layout = None
        # Limpiamos la toolbar

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy(0), QtWidgets.QSizePolicy.Policy(0)
        )
        sizePolicy.setHeightForWidth(True)

        pbSize = self.iconSize

        if settings.config.value("application/isDebuggerMode", False):

            pushButtonExport = QtWidgets.QToolButton()
            pushButtonExport.setObjectName("pushButtonExport")
            pushButtonExport.setSizePolicy(sizePolicy)
            pushButtonExport.setMinimumSize(pbSize)
            pushButtonExport.setMaximumSize(pbSize)
            pushButtonExport.setIcon(
                QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-properties.png"))
            )
            pushButtonExport.setShortcut(QtGui.QKeySequence(self.tr("F3")))
            pushButtonExport.setWhatsThis(
                QtWidgets.QApplication.translate("FLFormDB", "Exportar a XML(F3)")
            )
            pushButtonExport.setToolTip(
                QtWidgets.QApplication.translate("FLFormDB", "Exportar a XML(F3)")
            )
            pushButtonExport.setFocusPolicy(QtCore.Qt.NoFocus)
            self.bottomToolbar.layout().addWidget(pushButtonExport)
            pushButtonExport.clicked.connect(self.exportToXml)

            if settings.config.value("ebcomportamiento/show_snaptshop_button", False):
                push_button_snapshot = QtWidgets.QToolButton()
                push_button_snapshot.setObjectName("pushButtonSnapshot")
                push_button_snapshot.setSizePolicy(sizePolicy)
                push_button_snapshot.setMinimumSize(pbSize)
                push_button_snapshot.setMaximumSize(pbSize)
                push_button_snapshot.setIcon(
                    QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-paste.png"))
                )
                push_button_snapshot.setShortcut(QtGui.QKeySequence(self.tr("F8")))
                push_button_snapshot.setWhatsThis("Capturar pantalla(F8)")
                push_button_snapshot.setToolTip("Capturar pantalla(F8)")
                push_button_snapshot.setFocusPolicy(QtCore.Qt.NoFocus)
                self.bottomToolbar.layout().addWidget(push_button_snapshot)
                push_button_snapshot.clicked.connect(self.saveSnapShot)

            spacer = QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
            )
            self.bottomToolbar.layout().addItem(spacer)

        if not self.pushButtonCancel:
            self.pushButtonCancel = QtWidgets.QToolButton()
            self.pushButtonCancel.setObjectName("pushButtonCancel")
            cast(QtCore.pyqtSignal, self.pushButtonCancel.clicked).connect(
                cast(Callable, self.close)
            )

        self.pushButtonCancel.setSizePolicy(sizePolicy)
        self.pushButtonCancel.setMaximumSize(pbSize)
        self.pushButtonCancel.setMinimumSize(pbSize)
        self.pushButtonCancel.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-stop.png"))
        )
        # self.pushButtonCancel.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.pushButtonCancel.setFocus()
        self.pushButtonCancel.setShortcut(QtGui.QKeySequence(self.tr("Esc")))
        self.pushButtonCancel.setWhatsThis("Cerrar formulario (Esc)")
        self.pushButtonCancel.setToolTip("Cerrar formulario (Esc)")
        self.bottomToolbar.layout().addWidget(self.pushButtonCancel)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def formName(self) -> str:
        """
        Return internal form name.
        """

        return "form%s" % self.idMDI_

    def name(self) -> str:
        """Get name of the form."""

        return self.formName()

    def geoName(self) -> str:
        """Get name of the form."""
        # FIXME: What this should do exactly?
        return self.formName()

    def bindIface(self) -> None:
        """
        Join the script interface to the form object.
        """

        if self.iface:
            self.oldFormObj = self.iface

    def unbindIface(self) -> None:
        """
        Disconnect the script interface to the form object.
        """
        if not self.iface:
            return

        self.iface = self.oldFormObj

    def isIfaceBind(self) -> bool:
        """
        Indicate if the script interface is attached to the form object.
        """

        if self.iface:
            return True
        else:
            return False

    def closeEvent(self, e: Any) -> None:
        """
        Capture event close.
        """
        self.frameGeometry()

        self.saveGeometry()
        self.setCursor(None)
        # self.closed.emit()
        self.hide()
        self.emitFormClosed()
        # super().closeEvent(e)
        # self._action.mainform_widget = None
        self.deleteLater()
        self._loaded = False
        # from PyQt5.QtWidgets import qApp

        # qApp.processEvents() #Si se habilita pierde mucho tiempo!

        # self.hide()
        try:
            # if hasattr(self.script, "form"):
            #    print("Borrando self.script.form", self.script.form)
            #    self.script.form = None
            if self.widget is not None and type(self).__name__ != "FLFormSearchDB":
                self.widget.close()
                self.widget = None
                # del self.widget

            # self.iface = None
            # del self.iface
            # if hasattr(self, "widget"):
            #    print("Borrando self.widget", self.widget)
            #    self.widget.close()
            #    del self.widget
            instance_name = (self.__class__, self._action.name())
            if instance_name in self.known_instances.keys():
                del self.known_instances[instance_name]

            # if hasattr(self, "script"):
            #    print("Borrando self.script", self.script)
            self.script = None
        except Exception:

            self.logger.error(
                "El FLFormDB %s no se cerró correctamente:\n%s",
                self.formName(),
                traceback.format_exc(),
            )

        parent = self.parent()

        if isinstance(parent, QtWidgets.QMdiSubWindow):
            parent.close()

    def showEvent(self, e: Any) -> None:
        """
        Capture event show.
        """
        # --> Para mostrar form sin negro previo
        QtWidgets.QApplication.processEvents()
        # <--
        if not self.loaded():
            return

        if not self.showed:
            self.showed = True

            # self.initMainWidget()

            self.callInitScript()

            if not self._loaded:
                return

            self.bindIface()

        size = geometry.loadGeometryForm(self.geoName())
        if size:
            self.resize(size)

            parent = self.parent()

            if parent and isinstance(parent, QtWidgets.QMdiSubWindow):
                parent.resize(size)
                parent.repaint()

    def cursorDestroyed(self, obj_: Optional[Any] = None) -> None:
        """Clean up. Called when cursor has been deleted."""
        if not obj_:
            obj_ = self.sender()

        if not obj_ or obj_ is self.cursor_:
            return

        del self.cursor_

    """
    Captura evento ocultar


    def hideEvent(self, h):
        pW = self.parentWidget()
        if not pW:
            geo = QtCore.QSize(self.width(), self.height())
            if self.isMinimized():
                geo.setWidth(1)
            elif self.isMaximized():
                geo.setWidth(9999)
        else:
            geo = QtCore.QSize(pW.width(), pW.height())

        #geometry.saveGeometryForm(self.geoName(), geo)
    """

    def focusInEvent(self, f: Any) -> None:
        """
        Capture Focus Enter Event.
        """

        super().focusInEvent(f)
        if not self.isIfaceBind():
            self.bindIface()

    def show(self) -> None:
        """
        Initialize components of the main widget.

        @param w Widget to initialize. If not set use
        by default the current main widget.
        """

        if hasattr(application.project.main_window, "_dict_main_widgets"):
            module_name = application.project.conn_manager.managerModules().activeIdModule()
            if (
                module_name
                and module_name in application.project.main_window._dict_main_widgets.keys()
            ):
                module_window = application.project.main_window._dict_main_widgets[module_name]

                mdi_area = module_window.centralWidget()
                if isinstance(mdi_area, QtWidgets.QMdiArea):

                    for sub_window in mdi_area.subWindowList():
                        if cast(FLFormDB, sub_window.widget()).formName() == self.formName():
                            mdi_area.setActiveSubWindow(sub_window)
                            return

                    if type(self).__name__ == "FLFormDB":
                        # if not isinstance(self.parent(), QtWidgets.QMdiSubWindow):
                        # size = self.size()
                        mdi_area.addSubWindow(self)

        if self.initFocusWidget_ is None:
            self.initFocusWidget_ = self.focusWidget()

        if self.initFocusWidget_:
            self.initFocusWidget_.setFocus()

        # if not self.tiempo_ini:
        #    self.tiempo_ini = time.time()
        super().show()
        # tiempo_fin = time.time()
        parent_ = self.parent()
        if parent_ and parent_.parent() is None:

            qt_rectangle = self.frameGeometry()
            center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
            qt_rectangle.moveCenter(center_point)
            self.move(qt_rectangle.topLeft())
        # if settings.readBoolEntry("application/isDebuggerMode", False):
        #    self.logger.warning("INFO:: Tiempo de carga de %s: %.3fs %s (iface %s)" %
        #                     (self.actionName_, tiempo_fin - self.tiempo_ini, self, self.iface))
        # self.tiempo_ini = None

    def initMainWidget(self, w: Optional[QtWidgets.QWidget] = None) -> None:
        """Initialize widget."""
        if not self.showed:
            self.show()

    def child(self, child_name: str) -> QtWidgets.QWidget:
        """Get child by name."""
        ret = cast(
            QtWidgets.QWidget,
            self.findChild(QtWidgets.QWidget, child_name, QtCore.Qt.FindChildrenRecursively),
        )
        if ret is not None:
            from . import flfielddb
            from . import fltabledb

            if isinstance(ret, (flfielddb.FLFieldDB, fltabledb.FLTableDB)):
                if ret._loaded is False:
                    ret.load()

        return ret

    # def __getattr__(self, name):
    # if getattr(self.script, "form", None):
    #    return getattr(self.script.form, name)
    # else:
    #    qWarning("%s (%s):No se encuentra el atributo %s" % (self, self.iface, name))

    @decorators.NotImplementedWarn
    def exportToXml(self, b: bool) -> None:
        """Export this widget into an xml."""
        from pineboolib.fllegacy.aqsobjects.aqs import AQS

        xml = AQS.toXml(self, True, True)
        print(xml.toString(2))
        pass
