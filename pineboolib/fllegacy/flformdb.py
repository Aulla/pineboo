"""Flformdb module."""

# -*- coding: utf-8 -*-
import traceback
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog, QFileDialog, QApplication
from PyQt5.QtCore import pyqtSignal

from pineboolib import logging
from pineboolib.core import decorators
from pineboolib.core.utils.utils_base import filedir
from pineboolib.application.utils.geometry import loadGeometryForm, saveGeometryForm
from pineboolib.fllegacy.flaction import FLAction
from pineboolib.core.settings import config
from pineboolib.fllegacy import flapplication
from typing import Any, Union, Dict, Optional, Tuple, Type, cast, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.application.database import pnsqlcursor


class FLFormDB(QDialog):
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

    cursor_: Optional["pnsqlcursor.PNSqlCursor"]

    """
    Nombre de la tabla, contiene un valor no vacío cuando
    la clase es propietaria del cursor
    """
    name_: str

    """
    Capa principal del formulario
    """
    layout_: QtWidgets.QLayout

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

    bottomToolbar: Optional[QtWidgets.QToolBar]

    toolButtonClose: Optional[QtWidgets.QToolButton]

    _uiName: str
    _scriptForm: Union[Any, str]

    loop: bool

    logger = logging.getLogger("FLFormDB")

    def __init__(
        self, parent: Optional[QtWidgets.QWidget], action: "FLAction", load: bool = False
    ) -> None:
        """Create a new FLFormDB for given action."""
        # self.tiempo_ini = time.time()
        from pineboolib.application import project

        if not parent:
            parent = flapplication.aqApp.mainWidget()
        # if project.DGI.localDesktop():  # Si es local Inicializa
        # QtWidgets.QWidget.__init__(self, parent)  # FIXME: Porqué pide dos argumentos extra??
        # super(QtWidgets.QWidget, self).__init__(parent)
        super().__init__(parent)

        self._loaded = False
        self.known_instances[(self.__class__, action.name())] = self

        self._action: "FLAction" = action
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

        # if not self._scriptForm and self._action.scriptForm():
        #    self._scriptForm = self._action.scriptForm()

        # if not getattr(self._action, "alias", None):
        #    qWarning("FLFormDB::Cargando un action XML")
        # elif project.DGI.localDesktop():
        # self.setWindowTitle(self._action.alias)

        self.idMDI_ = self._action.name()

        self.logger.info("init: Action: %s", self._action)
        self.script = project.actions[self._action.name()].load_script(script_name, self)
        self.widget = self.script.form

        if hasattr(self.widget, "iface"):
            self.iface = self.widget.iface

        if project._DGI is not None:
            self.iconSize = project.DGI.iconSize()

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
            from pineboolib.application import project

            if project.conn is None:
                raise Exception("Project is not connected yet")

            project.conn.managerModules().createUI(self._uiName, None, self)

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

            if hasattr(self.iface, "init"):  # Meterlo en un hilo
                try:
                    self.iface.init()
                except Exception:
                    from pineboolib.core.error_manager import error_manager
                    from pineboolib.application import project

                    flapplication.aqApp.msgBoxWarning(
                        error_manager(traceback.format_exc(limit=-6, chain=False)), project._DGI
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

    def setCursor(self, cursor: "pnsqlcursor.PNSqlCursor" = None) -> None:  # type: ignore
        """Change current cursor binded to this control."""
        if cursor is not self.cursor_ and self.cursor_ and self.oldCursorCtxt:
            self.cursor_.setContext(self.oldCursorCtxt)

        if not cursor:
            return

        if self.cursor_ and self.cursor_ is not cursor:
            if type(self).__name__ == "FLFormRecodDB":
                self.cursor_.restoreEditionFlag(self)
                self.cursor_.restoreBrowseFlag(self)

        if self.cursor_:

            cast(pyqtSignal, self.cursor_.destroyed).disconnect(self.cursorDestroyed)

        self.cursor_ = cursor

        if type(self).__name__ == "FLFormRecodDB":
            self.cursor_.setEdition(False, self)
            self.cursor_.setBrowse(False, self)

        cast(pyqtSignal, self.cursor_.destroyed).connect(self.cursorDestroyed)
        if self.iface and self.cursor_:
            self.oldCursorCtxt = self.cursor_.context()
            self.cursor_.setContext(self.iface)

    def cursor(self) -> "pnsqlcursor.PNSqlCursor":  # type : ignore
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

            ret = QFileDialog.getSaveFileName(
                QApplication.activeWindow(), "Pineboo", tmp_file, "PNG(*.png)"
            )
            path_file = ret[0] if ret else None

        if path_file:
            fi = QtCore.QFile(path_file)
            if not fi.OpenMode(QtCore.QIODevice.WriteOnly):
                print("FLFormDB : Error I/O al intentar escribir el fichero", path_file)
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

        saveGeometryForm(self.geoName(), geo)
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
        # FIXME: QDialog.accepted() is a signal. We're shadowing it.
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
        from pineboolib.application import project

        if project.conn is None:
            raise Exception("Project is not connected yet")

        if "fltesttest" in project.conn.managerModules().listAllIdModules():
            project.call("fltesttest.iface.recibeEvento", ["formClosed", self.actionName_], None)

        self.formClosed.emit()
        if self.widget:
            self.widget.closed.emit()

    def action(self) -> "FLAction":
        """Get form FLAction."""
        return self._action

    def initForm(self) -> None:
        """
        Initialize the associated script.
        """

        # acl = project.acl()
        acl = None  # FIXME: Add ACL later
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
                from pineboolib.fllegacy.flsqlcursor import FLSqlCursor

                cursor = FLSqlCursor(self._action.table())
                self.setCursor(cursor)

            v = None

            preload_main_filter = getattr(self.iface, "preloadMainFilter", None)

            if preload_main_filter:
                v = preload_main_filter()

            if v is not None and self.cursor_:
                self.cursor_.setMainFilter(v, False)

            # if self._loaded and not self.__class__.__name__ == "FLFormRecordDB":
            # project.conn.managerModules().loadFLTableDBs(self)

            if self._action.description() not in ("", None):
                self.setWhatsThis(self._action.description())

            caption = self._action.caption()

            if caption in ("", None) and self.cursor_ and self.cursor_.metadata():
                caption = self.cursor_.metadata().alias()

            if caption in ("", None):
                caption = "No hay metadatos"
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

        self.bottomToolbar.setLayout(QtWidgets.QHBoxLayout())
        self.bottomToolbar.setLayout(self.bottomToolbar.layout())
        self.bottomToolbar.layout().setContentsMargins(0, 0, 0, 0)
        self.bottomToolbar.layout().setSpacing(0)
        self.bottomToolbar.layout().addStretch()
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

        if config.value("application/isDebuggerMode", False):

            pushButtonExport = QtWidgets.QToolButton()
            pushButtonExport.setObjectName("pushButtonExport")
            pushButtonExport.setSizePolicy(sizePolicy)
            pushButtonExport.setMinimumSize(pbSize)
            pushButtonExport.setMaximumSize(pbSize)
            pushButtonExport.setIcon(
                QtGui.QIcon(filedir("./core/images/icons", "gtk-properties.png"))
            )
            pushButtonExport.setShortcut(QKeySequence(self.tr("F3")))
            pushButtonExport.setWhatsThis("Exportar a XML(F3)")
            pushButtonExport.setToolTip("Exportar a XML(F3)")
            pushButtonExport.setFocusPolicy(QtCore.Qt.NoFocus)
            self.bottomToolbar.layout().addWidget(pushButtonExport)
            pushButtonExport.clicked.connect(self.exportToXml)

            if config.value("ebcomportamiento/show_snaptshop_button", False):
                push_button_snapshot = QtWidgets.QToolButton()
                push_button_snapshot.setObjectName("pushButtonSnapshot")
                push_button_snapshot.setSizePolicy(sizePolicy)
                push_button_snapshot.setMinimumSize(pbSize)
                push_button_snapshot.setMaximumSize(pbSize)
                push_button_snapshot.setIcon(
                    QtGui.QIcon(filedir("./core/images/icons", "gtk-paste.png"))
                )
                push_button_snapshot.setShortcut(QKeySequence(self.tr("F8")))
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
            cast(pyqtSignal, self.pushButtonCancel.clicked).connect(self.close)

        self.pushButtonCancel.setSizePolicy(sizePolicy)
        self.pushButtonCancel.setMaximumSize(pbSize)
        self.pushButtonCancel.setMinimumSize(pbSize)
        self.pushButtonCancel.setIcon(QtGui.QIcon(filedir("./core/images/icons", "gtk-stop.png")))
        # self.pushButtonCancel.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.pushButtonCancel.setFocus()
        self.pushButtonCancel.setShortcut(QKeySequence(self.tr("Esc")))
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
        from PyQt5.QtWidgets import qApp

        qApp.processEvents()

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
        from PyQt5.QtWidgets import QMdiSubWindow

        if isinstance(self.parent(), QMdiSubWindow):
            self.parent().close()

    def showEvent(self, e: Any) -> None:
        """
        Capture event show.
        """
        # --> Para mostrar form sin negro previo
        from PyQt5.QtWidgets import QMdiSubWindow
        from pineboolib.fllegacy.systype import SysType

        qsa_sys = SysType()

        qsa_sys.processEvents()
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

        size = loadGeometryForm(self.geoName())
        if size:
            self.resize(size)

            if self.parent() and isinstance(self.parent(), QMdiSubWindow):
                self.parent().resize(size)
                self.parent().repaint()

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

        #saveGeometryForm(self.geoName(), geo)
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

        # from PyQt5 import QtWidgets
        # from pineboolib.application import project

        # module_name = getattr(project.actions[self._action.name()].mod, "module_name", None)
        # if module_name:

        #    if module_name in flapplication.aqApp._dict_main_widgets.keys():
        #        module_window = flapplication.aqApp._dict_main_widgets[module_name]
        #        mdi_area = module_window.centralWidget()

        #        if isinstance(mdi_area, QtWidgets.QMdiArea) and type(self).__name__ == "FLFormDB":
        #            if not isinstance(self.parent(), QtWidgets.QMdiSubWindow):
        #                # size = self.size()
        #                mdi_area.addSubWindow(self)

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
            from PyQt5.QtWidgets import QDesktopWidget  # type: ignore # Centrado

            qt_rectangle = self.frameGeometry()
            center_point = QDesktopWidget().availableGeometry().center()
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
        ret = self.findChild(QtWidgets.QWidget, child_name, QtCore.Qt.FindChildrenRecursively)
        if ret is not None:
            if hasattr(ret, "_loaded"):
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

        xml = AQS().toXml(self, True, True)
        print(xml.toString(2))
        pass
