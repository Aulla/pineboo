"""FlformSearchdb module."""

# -*- coding: utf-8 -*-
from pineboolib import logging, application

from PyQt5 import QtCore, QtWidgets, Qt, QtGui


from pineboolib.core import decorators, settings
from pineboolib.core.utils import utils_base

from pineboolib.application.database import pnsqlcursor

from . import flformdb

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pnaction


LOGGER = logging.get_logger(__name__)


class FLFormSearchDB(flformdb.FLFormDB):
    """
    Subclass of the FLFormDB class, designed to search for a record in a table.

    The behavior of choosing a record is modified for only
    close the form and so the object that invokes it can get
    of the cursor said record.

    It also adds OK and Cancel buttons. Accept indicates that it has been
    chosen the active record (same as double clicking on it or
    press the Enter key) and Cancel abort the operation.

    @author InfoSiAL S.L.
    """

    """
    Boton Aceptar
    """
    pushButtonAccept: Optional[QtWidgets.QToolButton]

    """
    Almacena si se ha abierto el formulario con el método FLFormSearchDB::exec()
    """

    acceptingRejecting_: bool

    def __init__(self, *args) -> None:
        """
        Initialize.
        """
        action: "pnaction.PNAction"
        parent: Optional["QtWidgets.QWidget"] = None
        cursor: "pnsqlcursor.PNSqlCursor"

        if isinstance(args[0], str):
            action = application.PROJECT.conn_manager.manager().action(args[0])
            cursor = pnsqlcursor.PNSqlCursor(action.table())
            if len(args) > 1 and args[1]:
                parent = args[1]

        elif isinstance(args[1], str):
            action = application.PROJECT.conn_manager.manager().action(args[1])
            cursor = args[0]
            if len(args) > 2 and args[2]:
                parent = args[2]
        else:
            raise Exception("Wrong size of arguments")

        if not parent:
            parent = QtWidgets.QApplication.activeModalWidget()

        if cursor is None:
            LOGGER.warning("Se ha llamado a FLFormSearchDB sin nombre de action o cursor")
            return

        if application.PROJECT.conn_manager is None:
            raise Exception("Project is not connected yet")

        super().__init__(action, parent, load=False)

        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setCursor(cursor)

        self.accepted_ = False
        self.inExec_ = False
        self.loop = False
        self.acceptingRejecting_ = False
        self.pushButtonAccept = None

        self.load()
        self.initForm()
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def load(self):
        """Load control."""

        super().load()

        action = application.PROJECT.actions[self._action.name()]
        action.load_master_widget()
        if action._master_widget is not None and not utils_base.is_library():
            action._master_widget._form = self  # type: ignore [assignment] # noqa: F821

    def setAction(self, a: "pnaction.PNAction") -> None:
        """Set a action."""

        if self.cursor_:
            self.cursor_.setAction(a)

    # def __delattr__(self, *args, **kwargs) -> None:
    #    """Delete attributes."""

    #    if self.cursor_:
    #        self.cursor_.restoreEditionFlag(self)
    #        self.cursor_.restoreBrowseFlag(self)

    #    super().__delattr__(self, *args, **kwargs)

    """
    formReady = QtCore.pyqtSignal()
    """

    def loadControls(self) -> None:
        """Load form controls."""

        self.bottomToolbar = QtWidgets.QFrame()
        if self.bottomToolbar:
            self.bottomToolbar.setMaximumHeight(64)
            self.bottomToolbar.setMinimumHeight(16)
            hblay = QtWidgets.QHBoxLayout()
            hblay.setContentsMargins(0, 0, 0, 0)
            hblay.setSpacing(0)
            hblay.addStretch()
            self.bottomToolbar.setLayout(hblay)
            self.bottomToolbar.setFocusPolicy(QtCore.Qt.NoFocus)
            self.layout_.addWidget(self.bottomToolbar)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy(0), QtWidgets.QSizePolicy.Policy(0)
        )
        sizePolicy.setHeightForWidth(True)

        push_button_size = self._icon_size
        if settings.CONFIG.value("application/isDebuggerMode", False):

            pushButtonExport = QtWidgets.QToolButton(self)
            pushButtonExport.setObjectName("pushButtonExport")
            pushButtonExport.setSizePolicy(sizePolicy)
            pushButtonExport.setMinimumSize(push_button_size)
            pushButtonExport.setMaximumSize(push_button_size)
            pushButtonExport.setIcon(
                QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-properties.png"))
            )
            pushButtonExport.setShortcut(Qt.QKeySequence(self.tr("F3")))
            pushButtonExport.setWhatsThis("Exportar a XML(F3)")
            pushButtonExport.setToolTip("Exportar a XML(F3)")
            pushButtonExport.setFocusPolicy(QtCore.Qt.NoFocus)
            self.bottomToolbar.layout().addWidget(pushButtonExport)
            pushButtonExport.clicked.connect(self.exportToXml)

            if settings.CONFIG.value("ebcomportamiento/show_snaptshop_button", False):
                push_button_snapshot = QtWidgets.QToolButton(self)
                push_button_snapshot.setObjectName("pushButtonSnapshot")
                push_button_snapshot.setSizePolicy(sizePolicy)
                push_button_snapshot.setMinimumSize(push_button_size)
                push_button_snapshot.setMaximumSize(push_button_size)
                push_button_snapshot.setIcon(
                    QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-paste.png"))
                )
                push_button_snapshot.setShortcut(Qt.QKeySequence(self.tr("F8")))
                push_button_snapshot.setWhatsThis("Capturar pantalla(F8)")
                push_button_snapshot.setToolTip("Capturar pantalla(F8)")
                push_button_snapshot.setFocusPolicy(QtCore.Qt.NoFocus)
                self.bottomToolbar.layout().addWidget(push_button_snapshot)
                push_button_snapshot.clicked.connect(self.saveSnapShot)

            spacer = QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
            )
            self.bottomToolbar.layout().addItem(spacer)

        if not self.pushButtonAccept:
            self.pushButtonAccept = QtWidgets.QToolButton(self)
            self.pushButtonAccept.setObjectName("pushButtonAccept")
            self.pushButtonAccept.clicked.connect(self.accept)

        self.pushButtonAccept.setSizePolicy(sizePolicy)
        self.pushButtonAccept.setMaximumSize(push_button_size)
        self.pushButtonAccept.setMinimumSize(push_button_size)
        self.pushButtonAccept.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-save.png"))
        )
        # pushButtonAccept->setAccel(Qt.QKeySequence(Qt::Key_F10)); FIXME
        self.pushButtonAccept.setFocus()
        self.pushButtonAccept.setWhatsThis("Seleccionar registro actual y cerrar formulario (F10)")
        self.pushButtonAccept.setToolTip("Seleccionar registro actual y cerrar formulario (F10)")
        self.pushButtonAccept.setFocusPolicy(QtCore.Qt.NoFocus)
        self.bottomToolbar.layout().addWidget(self.pushButtonAccept)
        self.pushButtonAccept.show()

        if not self.pushButtonCancel:
            self.pushButtonCancel = QtWidgets.QToolButton(self)
            self.pushButtonCancel.setObjectName("pushButtonCancel")
            self.pushButtonCancel.clicked.connect(self.reject)

        self.pushButtonCancel.setSizePolicy(sizePolicy)
        self.pushButtonCancel.setMaximumSize(push_button_size)
        self.pushButtonCancel.setMinimumSize(push_button_size)
        self.pushButtonCancel.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-stop.png"))
        )
        self.pushButtonCancel.setFocusPolicy(QtCore.Qt.NoFocus)
        # pushButtonCancel->setAccel(Esc); FIXME
        self.pushButtonCancel.setWhatsThis("Cerrar formulario sin seleccionar registro (Esc)")
        self.pushButtonCancel.setToolTip("Cerrar formulario sin seleccionar registro (Esc)")
        self.bottomToolbar.layout().addWidget(self.pushButtonCancel)
        self.pushButtonCancel.show()
        if self.cursor_ is None:
            raise Exception("Cursor is empty!.")
        self.cursor_.setEdition(False)
        self.cursor_.setBrowse(False)
        self.cursor_.recordChoosed.connect(self.accept)

    def exec_(self, valor: Optional[str] = None) -> bool:
        """
        Show the form and enter a new event loop to wait, to select record.

        The name of a cursor field is expected
        returning the value of that field if the form is accepted
        and a QVariant :: Invalid if canceled.

        @param valor Name of a form cursor field
        @return The value of the field if accepted, or False if canceled
        """

        if not self.cursor_:
            return False

        if self.cursor_.isLocked():
            self.cursor_.setModeAccess(pnsqlcursor.PNSqlCursor.Browse)

        if self.loop or self.inExec_:
            print("FLFormSearchDB::exec(): Se ha detectado una llamada recursiva")
            if self.isHidden():
                super().show()
            if self._init_focus_widget:
                self._init_focus_widget.setFocus()
            return False

        self.inExec_ = True
        self.acceptingRejecting_ = False
        self.accepted_ = False

        super().show()
        if self._init_focus_widget:
            self._init_focus_widget.setFocus()

        if self.iface:
            try:
                QtCore.QTimer.singleShot(50, self.iface.init)
            except Exception:
                pass

        if not self._is_closing:
            QtCore.QTimer.singleShot(0, self.emitFormReady)

        self.loop = True
        if self.eventloop:
            self.eventloop.exec_()
        self.loop = False
        self.inExec_ = False

        if self.accepted_ and valor:
            return self.cursor_.valueBuffer(valor)
        else:
            self.close()
            return False

    def setFilter(self, f: str) -> None:
        """Apply a filter to the cursor."""

        if not self.cursor_:
            return
        previousF = self.cursor_.mainFilter()
        newF = None
        if previousF == "":
            newF = f
        elif f is None or previousF.find(f) > -1:
            return
        else:
            newF = "%s AND %s" % (previousF, f)
        self.cursor_.setMainFilter(newF)

    def formClassName(self) -> str:
        """Return the class name of the form at runtime."""

        return "FormSearchDB"

    def formName(self) -> str:
        """
        Return internal form name.
        """

        return "formSearch%s" % self._id_mdi

    def closeEvent(self, e: QtCore.QEvent) -> None:
        """Capture event close."""

        self.frameGeometry()
        # if self.focusWidget():
        #    fdb = self.focusWidget().parentWidget()
        #    try:
        #        if fdb and fdb.autoComFrame_ and fdb.autoComFrame_.isvisible():
        #            fdb.autoComFrame_.hide()
        #            return
        #    except Exception:
        #        pass

        if self.cursor_ and self.pushButtonCancel:
            if not self.pushButtonCancel.isEnabled():
                return

            self._is_closing = True
            self.setCursor(None)
        else:
            self._is_closing = True

        if self.isHidden():
            # self.saveGeometry()
            # self.closed.emit()
            super().closeEvent(e)
            # self.deleteLater()
        else:
            self.reject()

    @decorators.pyqt_slot()
    def callInitScript(self) -> None:
        """Call the "init" function of the "masterprocess" script associated with the form."""

        pass

    @decorators.pyqt_slot()
    def hide(self) -> None:
        """Redefined for convenience."""

        if self.loop:
            self.loop = False
            self.eventloop.exit()

        if self.isHidden():
            return

        super().hide()

    @decorators.pyqt_slot()
    def accept(self) -> None:
        """Activate pressing the accept button."""

        if self.acceptingRejecting_:
            return
        self.frameGeometry()
        if self.cursor_:
            try:
                self.cursor_.recordChoosed.disconnect(self.accept)
            except Exception:
                pass
        self.acceptingRejecting_ = True
        self.accepted_ = True
        self.saveGeometry()
        self.hide()

        parent = self.parent()
        if isinstance(parent, QtWidgets.QMdiSubWindow):
            parent.hide()

    @decorators.pyqt_slot()
    def reject(self) -> None:
        """Activate pressing the accept button."""

        if self.acceptingRejecting_:
            return
        self.frameGeometry()
        if self.cursor_:
            try:
                self.cursor_.recordChoosed.disconnect(self.accept)
            except Exception:
                pass
        self.acceptingRejecting_ = True
        self.hide()

    @decorators.pyqt_slot()
    def show(self) -> None:
        """Redefined for convenience."""
        self.exec_()

    def setMainWidget(self, w: QtWidgets.QWidget = None) -> None:
        """
        Set widget as the main form.
        """

        if not self.cursor_:
            return

        if w:
            w.hide()
            self.mainWidget_ = w
