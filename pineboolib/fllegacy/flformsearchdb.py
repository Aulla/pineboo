"""FlformSearchdb module."""

# -*- coding: utf-8 -*-
from pineboolib import logging, application

from PyQt6 import QtCore, QtWidgets, QtGui  # type: ignore[import]


from pineboolib.core import decorators, settings
from pineboolib.core.utils import utils_base

from pineboolib.application.database import pnsqlcursor

from . import flformdb

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pnaction  # pragma: no cover


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
    pushButtonAccept: Optional["QtWidgets.QToolButton"]

    """
    Almacena si se ha abierto el formulario con el método FLFormSearchDB::exec()
    """

    _accepting_rejecting: bool
    _in_exec: bool

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
        elif isinstance(args[0], pnsqlcursor.PNSqlCursor):
            cursor = args[0]
            parent = args[1]
            action_ = cursor.action()
            if action_:
                action = action_

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

        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        if cursor.actionName() != action.name():
            cursor.setAction(action)

        self.setCursor(cursor)

        self.accepted_ = False
        self._in_exec = False
        self.loop = False
        self._accepting_rejecting = False
        self.pushButtonAccept = None  # pylint: disable=invalid-name

        self.load()
        self.initForm()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def load(self):
        """Load control."""

        super().load()

        action = application.PROJECT.actions[self._action.name()]
        action.load_master_widget()
        if action._master_widget is not None and not utils_base.is_library():
            action._master_widget._form = self  # type: ignore [assignment] # noqa: F821

    def setAction(self, action: "pnaction.PNAction") -> None:
        """Set a action."""

        if self.cursor_:
            self.cursor_.setAction(action)

    """
    formReady = QtCore.pyqtSignal()
    """

    def loadControls(self) -> None:
        """Load form controls."""

        self.init_tool_bar()

        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy(0), QtWidgets.QSizePolicy.Policy(0)
        )
        size_policy.setHeightForWidth(True)

        push_button_size = self._icon_size
        if settings.CONFIG.value("application/isDebuggerMode", False):

            pushButtonExport = QtWidgets.QToolButton(self)  # pylint: disable=invalid-name
            pushButtonExport.setObjectName("pushButtonExport")
            pushButtonExport.setSizePolicy(size_policy)
            pushButtonExport.setMinimumSize(push_button_size)
            pushButtonExport.setMaximumSize(push_button_size)
            pushButtonExport.setIcon(
                QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-properties.png"))
            )
            pushButtonExport.setShortcut(QtGui.QKeySequence(self.tr("F3")))
            pushButtonExport.setWhatsThis("Exportar a XML(F3)")
            pushButtonExport.setToolTip("Exportar a XML(F3)")
            pushButtonExport.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.bottomToolbar.layout().addWidget(pushButtonExport)
            pushButtonExport.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                self.exportToXml
            )

            if settings.CONFIG.value("ebcomportamiento/show_snaptshop_button", False):
                push_button_snapshot = QtWidgets.QToolButton(self)
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

        if not self.pushButtonAccept:
            self.pushButtonAccept = QtWidgets.QToolButton(self)
            self.pushButtonAccept.setObjectName("pushButtonAccept")
            self.pushButtonAccept.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                self.accept
            )

        self.pushButtonAccept.setSizePolicy(size_policy)
        self.pushButtonAccept.setMaximumSize(push_button_size)
        self.pushButtonAccept.setMinimumSize(push_button_size)
        self.pushButtonAccept.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-save.png"))
        )
        # pushButtonAccept->setAccel(QtGui.QKeySequence(Qt::Key_F10)); FIXME
        self.pushButtonAccept.setFocus()
        self.pushButtonAccept.setWhatsThis("Seleccionar registro actual y cerrar formulario (F10)")
        self.pushButtonAccept.setToolTip("Seleccionar registro actual y cerrar formulario (F10)")
        self.pushButtonAccept.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.bottomToolbar.layout().addWidget(self.pushButtonAccept)
        self.pushButtonAccept.show()

        if not self.pushButtonCancel:
            self.pushButtonCancel = QtWidgets.QToolButton(self)
            self.pushButtonCancel.setObjectName("pushButtonCancel")
            self.pushButtonCancel.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                self.reject
            )

        self.pushButtonCancel.setSizePolicy(size_policy)
        self.pushButtonCancel.setMaximumSize(push_button_size)
        self.pushButtonCancel.setMinimumSize(push_button_size)
        self.pushButtonCancel.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-stop.png"))
        )
        self.pushButtonCancel.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
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

        if self.loop or self._in_exec:
            print("FLFormSearchDB::exec(): Se ha detectado una llamada recursiva")
            if self.isHidden():
                super().show()
            if self._init_focus_widget:
                self._init_focus_widget.setFocus()
            return False

        self._in_exec = True
        self._accepting_rejecting = False
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
            self.eventloop.exec()
        self.loop = False
        self._in_exec = False

        if self.accepted_ and valor:
            return self.cursor_.valueBuffer(valor)
        else:
            self.close()
            return False

    def setFilter(self, filter: str) -> None:
        """Apply a filter to the cursor."""

        if not self.cursor_:
            return
        previous_filter = self.cursor_.mainFilter()

        new_filter = ""
        if not previous_filter:
            new_filter = filter
        elif not filter or previous_filter.find(filter) > -1:
            return
        else:
            new_filter = "%s AND %s" % (previous_filter, filter)

        self.cursor_.setMainFilter(new_filter)

    def formClassName(self) -> str:
        """Return the class name of the form at runtime."""

        return "FormSearchDB"

    def formName(self) -> str:
        """
        Return internal form name.
        """

        return "formSearch%s" % self._id_mdi

    def closeEvent(self, event: "QtGui.QCloseEvent") -> None:
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
            super().closeEvent(event)
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

        if self._accepting_rejecting:
            return
        self.frameGeometry()
        if self.cursor_:
            try:
                self.cursor_.recordChoosed.disconnect(self.accept)
            except Exception:
                pass
        self._accepting_rejecting = True
        self.accepted_ = True
        self.saveGeometry()
        self.hide()

        parent = self.parent()
        if isinstance(parent, QtWidgets.QMdiSubWindow):
            parent.hide()

    @decorators.pyqt_slot()
    def reject(self) -> None:
        """Activate pressing the accept button."""

        if self._accepting_rejecting:
            return
        self.frameGeometry()
        if self.cursor_:
            try:
                self.cursor_.recordChoosed.disconnect(self.accept)
            except Exception:
                pass
        self._accepting_rejecting = True
        self.hide()

    @decorators.pyqt_slot()
    def show(self) -> None:
        """Redefined for convenience."""
        self.exec_()


# ===============================================================================
#     def setMainWidget(self, w: QtWidgets.QWidget = None) -> None:
#         """
#         Set widget as the main form.
#         """
#
#         if not self.cursor_:
#             return
#
#         if w:
#             w.hide()
#             self.mainWidget_ = w
# ===============================================================================
