"""Flformdb module."""

# -*- coding: utf-8 -*-
import traceback
from PyQt6 import QtCore, QtGui, QtWidgets  # type: ignore[import]

from pineboolib import logging

from pineboolib.core import decorators, settings
from pineboolib.core.utils import utils_base

from pineboolib.application.utils import geometry
from pineboolib.application.metadata import pnaction

from pineboolib.q3widgets import qmainwindow

from pineboolib.application.database import pnsqlcursor

from pineboolib import application
from typing import Any, Union, Dict, Optional, Tuple, Type, cast, Callable, TYPE_CHECKING


if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor  # pragma: no cover
    from pineboolib.qsa import formdbwidget  # pragma: no cover


LOGGER = logging.get_logger(__name__)


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
    layout_: "QtWidgets.QVBoxLayout"

    """
    Widget principal del formulario
    """
    main_widget: Optional["QtWidgets.QWidget"]
    """
    Identificador de ventana MDI.

    Generalmente es el nombre de la acción que abre el formulario
    """
    _id_mdi: str

    """
    Capa para botones
    """
    layoutButtons: "QtWidgets.QHBoxLayout"

    """
    Boton Cancelar
    """
    pushButtonCancel: Optional["QtWidgets.QToolButton"]

    """
    Indica que la ventana ya ha sido mostrada una vez
    """
    _showed: bool

    """
    Guarda el contexto anterior que tenia el cursor
    """
    _old_cursor_context: Any

    """
    Indica que el formulario se está cerrando
    """
    _is_closing: bool

    """
    Componente con el foco inicial
    """
    _init_focus_widget: Optional["QtWidgets.QWidget"]

    """
    Guarda el último objeto de formulario unido a la interfaz de script (con bindIface())
    """
    _old_form_object: Any

    """
    Boton Debug Script
    """
    pushButtonDebug: Optional["QtWidgets.QToolButton"]

    """
    Almacena que se aceptado, es decir NO se ha pulsado, botón cancelar
    """
    accepted_: bool

    """
    Nombre del formulario relativo a la acción (form / formRecrd + nombre de la acción)
    """
    _action_name: str

    """
    Interface para scripts
    """
    # iface: Any

    """
    Tamaño de icono por defecto
    """
    _icon_size: "QtCore.QSize"

    # protected slots:

    """
    Uso interno
    """
    _old_form_objectDestroyed = QtCore.pyqtSignal()

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

    bottomToolbar: QtWidgets.QFrame

    toolButtonClose: Optional["QtWidgets.QToolButton"]

    _ui_name: str

    loop: bool
    _action: "pnaction.PNAction"

    eventloop: "QtCore.QEventLoop"

    def __init__(
        self,
        action_or_name: Union["pnaction.PNAction", str],
        parent: Optional[Union["QtWidgets.QWidget", int]] = None,
        load: Union[bool, int] = False,
    ) -> None:
        """Create a new FLFormDB for given action."""
        # self.tiempo_ini = time.time()
        parent_widget: QtWidgets.QWidget

        if isinstance(load, int):
            load = load == 1

        if parent is None or isinstance(parent, int):
            if application.PROJECT.main_window is not None:
                if application.PROJECT.main_window.main_widget is not None:
                    parent_widget = application.PROJECT.main_window.main_widget
                else:

                    parent_widget = application.PROJECT.main_window
            else:
                raise Exception("main_window is not loaded!")
        else:
            parent_widget = parent

        super().__init__(parent_widget)

        self._loaded = False

        if isinstance(action_or_name, str):
            self._action = application.PROJECT.conn_manager.manager().action(action_or_name)
        else:
            self._action = action_or_name

        self.known_instances[(self.__class__, self._action.name())] = self

        self._ui_name = self._action_name = self._action.name()

        if self._action.table():
            if type(self).__name__ == "FLFormRecordDB":
                self._action_name = "formRecord%s" % self._action_name
                # script_name = self._action.scriptFormRecord()
                # self.action_widget = application.PROJECT.actions[self._action.name()]._record_widget
            else:
                self._action_name = "form%s" % self._action_name
                # script_name = self._action.scriptForm()
                # self.action_widget = application.PROJECT.actions[self._action.name()]._master_widget
            self._ui_name = self._action.form()
        else:
            if self._action.scriptForm() or self._action.scriptFormRecord():
                self._ui_name = ""

        # self.mod = self._action.mod
        self.loop = False
        self.eventloop = QtCore.QEventLoop()

        self.layout_ = QtWidgets.QVBoxLayout()
        self.layout_.setContentsMargins(1, 1, 1, 1)
        self.layout_.setSpacing(1)
        self.layout_.setContentsMargins(1, 1, 1, 1)
        self.layout_.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        self.setLayout(self.layout_)

        self.pushButtonCancel = None  # pylint: disable=invalid-name
        self.toolButtonClose = None  # pylint: disable=invalid-name
        self.bottomToolbar = QtWidgets.QFrame()  # pylint: disable=invalid-name
        # self.cursor_ = None
        self._init_focus_widget = None
        self._showed = False
        self._is_closing = False
        self.accepted_ = False
        self.main_widget = None
        # self.iface = None
        self._old_form_object = None
        self._old_cursor_context = None

        self._id_mdi = self._action.name()
        self._icon_size = application.PROJECT.DGI.icon_size()

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

        widget: Union["qmainwindow.QMainWindow", "QtWidgets.QDialog"]

        if not self._action.table():
            widget = qmainwindow.QMainWindow()
        else:
            widget = QtWidgets.QDialog()

        # LOGGER.warning("previo %s %s %s", self._action.form(), self._action.formRecord(), widget)

        self.layout_.insertWidget(0, widget)
        self.layout_.setSpacing(1)
        self.layout_.setContentsMargins(1, 1, 1, 1)
        self.layout_.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        if self._ui_name:

            if application.PROJECT.conn_manager is None:
                raise Exception("Project is not connected yet")

            application.PROJECT.conn_manager.managerModules().createUI(self._ui_name, None, widget)

        self._loaded = True

    def loaded(self) -> bool:
        """Return if the control is initialized."""

        return self._loaded

    @decorators.pyqt_slot()
    def initScript(self) -> bool:
        """
        Call the "init" function of the masterprocess script associated with the form.
        """
        if self._loaded:

            if self.action_widget:
                self.action_widget.clear_connections()

            fun = getattr(self.iface, "init", None)
            if fun is None:
                fun = getattr(self.action_widget, "init", None)

            if fun is not None:
                fun()

            return True

        return False

    # def __del__(self) -> None:
    #    """
    #    Destroyer.
    #    """
    #    # TODO: Esto hay que moverlo al closeEvent o al close()
    #    # ..... los métodos __del__ de python son muy poco fiables.
    #    # ..... Se lanzan o muy tarde, o nunca.
    #    # (De todos modos creo que ya hice lo mismo a mano en el closeEvent en commits anteriores)
    #
    #    self.unbindIface()

    def setCursor(self, cursor: "isqlcursor.ISqlCursor" = None) -> None:  # type: ignore
        """Change current cursor binded to this control."""
        if cursor is None:
            return

        if cursor is not self.cursor_:
            if self.cursor_ is not None:
                if self._old_cursor_context:
                    self.cursor_.setContext(self._old_cursor_context)

                if type(self).__name__ == "FLFormRecodDB":
                    self.cursor_.restoreEditionFlag(self.objectName())
                    self.cursor_.restoreBrowseFlag(self.objectName())

            # if self.cursor_:

            #    cast(QtCore.pyqtSignal, self.cursor_.destroyed).disconnect(self.cursorDestroyed)

            # self.widget.cursor_ = cursor
            self.cursor_ = cursor

            if type(self).__name__ == "FLFormRecodDB":
                self.cursor_.setEdition(False, self.objectName())
                self.cursor_.setBrowse(False, self.objectName())

            # cast(QtCore.pyqtSignal, self.cursor_.destroyed).connect(self.cursorDestroyed)
            iface = self.iface

            if iface is not None and self.cursor_ is not None:
                self._old_cursor_context = self.cursor_.context()
                self.cursor_.setContext(self.iface)

    def cursor(self) -> "isqlcursor.ISqlCursor":  # type: ignore [override] # noqa F821
        """
        To get the cursor used by the form.
        """
        if self.cursor_ is None:
            raise Exception("cursor_ is empty!.")

        return self.cursor_

    def mainWidget(self) -> Optional["QtWidgets.QWidget"]:
        """
        To get the form's main widget.
        """

        return self.main_widget

    def setIdMDI(self, id_: str) -> None:
        """
        Set the MDI ID.
        """

        self._id_mdi = id_

    def idMDI(self) -> str:
        """
        Return the MDI ID.
        """

        return self._id_mdi

    def setMainWidget(self, widget: Optional["QtWidgets.QWidget"] = None) -> None:
        """
        Set widget as the main form.
        """
        if widget is not None:
            self.main_widget = widget
        else:
            self.main_widget = self

    def snapShot(self) -> "QtGui.QImage":
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
                application.PROJECT.tmpdir,
                QtCore.QDateTime.currentDateTime().toString("ddMMyyyyhhmmsszzz"),
            )

            ret = QtWidgets.QFileDialog.getSaveFileName(
                QtWidgets.QApplication.activeWindow(), "Pineboo", tmp_file, "PNG(*.png)"
            )
            path_file = ret[0] if ret else None

        if path_file:
            file_ = QtCore.QFile(path_file)
            if file_.openMode() != QtCore.QIODevice.OpenModeFlag.WriteOnly:
                self.tr("Error I/O al intentar escribir el fichero %s" % path_file)
                return

            self.snapShot().save(file_, "PNG")

    def saveGeometry(self) -> "QtCore.QByteArray":
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

        geometry.save_geometry_form(self.geoName(), geo)
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

    @decorators.pyqt_slot()
    def close(self) -> bool:
        """
        Close the form.
        """
        if self._is_closing or not self._loaded:
            return True

        self._is_closing = True

        super().close()
        self._is_closing = False
        return True

    @decorators.pyqt_slot()
    def accept(self) -> None:
        """
        Activated by pressing the accept button.
        """
        pass

    @decorators.pyqt_slot()
    def reject(self) -> None:
        """
        Activated by pressing the cancel button.
        """
        pass

    @decorators.pyqt_slot()
    def showForDocument(self) -> None:
        """
        Show the form without calling the script "init".

        Used in documentation to avoid conflicts when capturing forms.
        """
        self._showed = True
        if self.main_widget:
            self.main_widget.show()
            self.resize(self.main_widget.size())
        super().show()

    @decorators.pyqt_slot()
    @decorators.not_implemented_warn
    def debugScript(self) -> bool:
        """
        Show the script associated with the form in the Workbench to debug.
        """

        return True

    @decorators.pyqt_slot()
    def get_script(self) -> Optional[str]:
        """
        Return the script associated with the form.
        """

        ifc = self.iface
        if ifc:
            return str(ifc)
        return None

    # private slots:

    @decorators.pyqt_slot()
    def callInitScript(self) -> None:
        """Call QS Script related to this control."""
        if not self.initScript():
            raise Exception("Error initializing the module.")

        if not self._is_closing:
            QtCore.QTimer.singleShot(0, self.emitFormReady)

    def emitFormReady(self) -> None:
        """Emit formReady signal, after the form has been loaded."""

        if "fltesttest" in application.PROJECT.conn_manager.managerModules().listAllIdModules():

            application.PROJECT.call(
                "fltesttest.iface.recibeEvento", ["formReady", self._action_name], None
            )
        self.formReady.emit()

    # protected_:

    def emitFormClosed(self) -> None:
        """Emit formClosed signal."""

        if application.PROJECT.conn_manager is None:
            raise Exception("Project is not connected yet")

        if "fltesttest" in application.PROJECT.conn_manager.managerModules().listAllIdModules():
            application.PROJECT.call(
                "fltesttest.iface.recibeEvento", ["formClosed", self._action_name], None
            )

        self.formClosed.emit()

        widget = self.action_widget

        if widget is not None:
            self.action_widget.closed.emit()

    def action(self) -> "pnaction.PNAction":
        """Get form PNAction."""
        return self._action

    def initForm(self) -> None:
        """
        Initialize the associated script.
        """

        acl = application.PROJECT.aq_app.acl()

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

            # if self._loaded and not self.__class__.__name__ == "FLFormRecordDB":
            # application.PROJECT.conn_manager.managerModules().loadFLTableDBs(self)

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

        self.init_tool_bar()

        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy(0), QtWidgets.QSizePolicy.Policy(0)
        )
        size_policy.setHeightForWidth(True)

        push_button_size = self._icon_size

        if settings.CONFIG.value("application/isDebuggerMode", False):

            pushButtonExport = QtWidgets.QToolButton()  # pylint: disable=invalid-name
            pushButtonExport.setObjectName("pushButtonExport")
            pushButtonExport.setSizePolicy(size_policy)
            pushButtonExport.setMinimumSize(push_button_size)
            pushButtonExport.setMaximumSize(push_button_size)
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
            pushButtonExport.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.bottomToolbar.layout().addWidget(pushButtonExport)
            pushButtonExport.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                self.exportToXml
            )

            if settings.CONFIG.value("ebcomportamiento/show_snaptshop_button", False):
                push_button_snapshot = QtWidgets.QToolButton()
                push_button_snapshot.setObjectName("pushButtonSnapshot")
                push_button_snapshot.setSizePolicy(size_policy)
                push_button_snapshot.setMinimumSize(push_button_size)
                push_button_snapshot.setMaximumSize(push_button_size)
                push_button_snapshot.setIcon(
                    QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-paste.png"))
                )
                push_button_snapshot.setShortcut(QtGui.QKeySequence(self.tr("F8")))
                push_button_snapshot.setWhatsThis("Capturar pantalla(F8)")
                push_button_snapshot.setToolTip("Capturar pantalla(F8)")
                push_button_snapshot.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self.bottomToolbar.layout().addWidget(push_button_snapshot)
                push_button_snapshot.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.saveSnapShot
                )

            spacer = QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
            )
            self.bottomToolbar.layout().addItem(spacer)

        if not self.pushButtonCancel:
            self.pushButtonCancel = QtWidgets.QToolButton()
            self.pushButtonCancel.setObjectName("pushButtonCancel")
            cast(
                QtCore.pyqtSignal, self.pushButtonCancel.clicked
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                cast(Callable, self.close)
            )

        self.pushButtonCancel.setSizePolicy(size_policy)
        self.pushButtonCancel.setMaximumSize(push_button_size)
        self.pushButtonCancel.setMinimumSize(push_button_size)
        self.pushButtonCancel.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-stop.png"))
        )
        # self.pushButtonCancel.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.pushButtonCancel.setFocus()
        self.pushButtonCancel.setShortcut(QtGui.QKeySequence(self.tr("Esc")))
        self.pushButtonCancel.setWhatsThis("Cerrar formulario (Esc)")
        self.pushButtonCancel.setToolTip("Cerrar formulario (Esc)")
        self.bottomToolbar.layout().addWidget(self.pushButtonCancel)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def formName(self) -> str:
        """
        Return internal form name.
        """

        return "form%s" % self._id_mdi

    def name(self) -> str:
        """Get name of the form."""

        return self.formName()

    def geoName(self) -> str:
        """Get name of the form."""
        # FIXME: What this should do exactly?
        return self.formName()

    # def bindIface(self) -> None:
    #    """
    #    Join the script interface to the form object.
    #    """

    #    if self.iface:
    #        self._old_form_object = self.iface

    # def unbindIface(self) -> None:
    #    """
    #    Disconnect the script interface to the form object.
    #    """
    #    if not self.iface:
    #        return

    #    self.iface = self._old_form_object

    # def isIfaceBind(self) -> bool:
    #    """
    #    Indicate if the script interface is attached to the form object.
    #    """

    #    if self.iface:
    #        return True
    #    else:
    #        return False

    def closeEvent(self, event: "QtGui.QCloseEvent") -> None:
        """
        Capture event close.
        """

        self.frameGeometry()

        self.saveGeometry()

        self.hide()
        self.emitFormClosed()
        self._loaded = False

        # from PyQt6.QtWidgets import qApp

        # qApp.processEvents() #Si se habilita pierde mucho tiempo!

        # self.hide()
        try:

            if type(self).__name__ != "FLFormSearchDB":
                super().close()

            instance_name = (self.__class__, self._action.name())
            if instance_name in self.known_instances.keys():
                del self.known_instances[instance_name]

        except Exception:

            LOGGER.error(
                "El FLFormDB %s no se cerró correctamente:\n%s",
                self.formName(),
                traceback.format_exc(),
            )

        parent = self.parent()

        if isinstance(parent, QtWidgets.QMdiSubWindow):
            parent.close()

    def showEvent(self, event: "QtGui.QShowEvent") -> None:
        """
        Capture event show.
        """
        # --> Para mostrar form sin negro previo
        # QtWidgets.QApplication.processEvents()
        # <--

        if not self.loaded():
            return

        if not self._showed:
            self._showed = True

            size = geometry.load_geometry_form(self.geoName())
            if size:
                self.resize(size)

            parent = self.parent()

            if parent and isinstance(parent, QtWidgets.QMdiSubWindow):
                if size:
                    parent.resize(size)
                parent.repaint()

            # self.initMainWidget()

            self.callInitScript()

            if not self._loaded:
                return

            # self.bindIface()

    # def cursorDestroyed(self, obj_: Optional[Any] = None) -> None:
    #    """Clean up. Called when cursor has been deleted."""
    #    if not obj_:
    #        obj_ = self.sender()

    #    if not obj_ or obj_ is self.cursor_:
    #        return

    #    del self.cursor_

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

    def show(self) -> None:
        """
        Initialize components of the main widget.

        @param w Widget to initialize. If not set use
        by default the current main widget.
        """
        main_window = application.PROJECT.main_window
        if main_window is None:
            return

        if hasattr(main_window, "_dict_main_widgets"):
            module_name = application.PROJECT.conn_manager.managerModules().activeIdModule()
            if module_name and main_window and module_name in main_window._dict_main_widgets.keys():
                module_window = cast(
                    QtWidgets.QMainWindow, main_window._dict_main_widgets[module_name]
                )

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

        if self._init_focus_widget is None:
            self._init_focus_widget = self.focusWidget()

        if self._init_focus_widget:
            self._init_focus_widget.setFocus()

        # if not self.tiempo_ini:
        #    self.tiempo_ini = time.time()
        super().show()
        # tiempo_fin = time.time()
        parent_ = self.parent()
        if parent_ and parent_.parent() is None:

            qt_rectangle = self.frameGeometry()
            center_point = self.screen().availableGeometry().center()
            qt_rectangle.moveCenter(center_point)
            self.move(qt_rectangle.topLeft())

        if not self._showed:  # Prueba al restaurar tabs no inicializan scripts
            self.initScript()

        # if settings.readBoolEntry("application/isDebuggerMode", False):
        #    LOGGER.warning("INFO:: Tiempo de carga de %s: %.3fs %s (iface %s)" %
        #                     (self._action_name, tiempo_fin - self.tiempo_ini, self, self.iface))
        # self.tiempo_ini = None

    def initMainWidget(self, widget: Optional["QtWidgets.QWidget"] = None) -> None:
        """Initialize widget."""

        if widget is not None:
            self.main_widget = widget

        if self.main_widget and not getattr(self.main_widget, "_showed", False):
            self.main_widget.show()

    def child(self, child_name: str) -> Optional["QtWidgets.QWidget"]:
        """Get child by name."""
        ret: Optional["QtCore.QObject"] = None
        try:
            ret = self.findChild(QtWidgets.QWidget, child_name)
        except Exception:
            pass

        if ret is not None:
            from . import flfielddb, fltabledb

            if isinstance(ret, (flfielddb.FLFieldDB, fltabledb.FLTableDB)):
                if ret._loaded is False:
                    ret.load()

        return cast(QtWidgets.QWidget, ret)

    # def __getattr__(self, name):
    # if getattr(self.script, "form", None):
    #    return getattr(self.script.form, name)
    # else:
    #    qWarning("%s (%s):No se encuentra el atributo %s" % (self, self.iface, name))

    @decorators.not_implemented_warn
    def exportToXml(self, value_: bool) -> None:
        """Export this widget into an xml."""
        from pineboolib.fllegacy.aqsobjects.aqs import AQS

        xml = AQS.toXml(self, True, True)
        print(xml.toString(2))
        pass

    def get_action_widget(self) -> Optional["formdbwidget.FormDBWidget"]:
        """Return main_widget."""
        widget = None
        if self._action.name() in application.PROJECT.actions.keys():
            action = application.PROJECT.actions[self._action.name()]
            widget = (
                action._record_widget
                if self._action_name.startswith("formRecord")
                else action._master_widget
            )

        return widget

    def set_action_widget(self, obj_: "formdbwidget.FormDBWidget"):
        """Set main widget."""

        action = application.PROJECT.actions[self._action.name()]
        if self._action_name.startswith("formRecord"):
            action._record_widget = obj_
        else:
            action._master_widget = obj_

    def get_cursor(self) -> Optional["isqlcursor.ISqlCursor"]:
        """Return action cursor."""
        return application.PROJECT.actions[self._action.name()].cursor()

    def set_cursor(self, cursor: "isqlcursor.ISqlCursor") -> None:
        """Set action cursor."""
        application.PROJECT.actions[self._action.name()].setCursor(cursor)

    @decorators.pyqt_slot()
    @decorators.not_implemented_warn
    def script(self) -> "str":
        """
        Return the script associated with the form.
        """

        return ""

    def get_iface(self) -> Callable:
        """Return script iface."""

        fun = getattr(self.action_widget, "iface", None)
        return fun

    def init_tool_bar(self) -> None:
        """Init bottomtoolbar."""

        self.bottomToolbar.setMinimumSize(self._icon_size)
        hblay = QtWidgets.QHBoxLayout()
        hblay.setContentsMargins(0, 0, 0, 0)
        hblay.setSpacing(0)
        hblay.addStretch()
        self.bottomToolbar.setLayout(hblay)
        self.bottomToolbar.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.layout_.addWidget(self.bottomToolbar)

    action_widget = property(get_action_widget, set_action_widget)
    cursor_ = property(get_cursor, set_cursor)  # type: ignore [assignment] # noqa: F821
    iface = property(get_iface)
