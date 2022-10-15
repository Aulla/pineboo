"""Flformrecord module."""
# -*- coding: utf-8 -*-


from PyQt6 import QtCore, QtGui, QtWidgets  # type: ignore[import]

from pineboolib.core.utils import utils_base
from pineboolib.core import settings, decorators

from pineboolib.application.database import pnsqlcursor
from pineboolib import logging, application


from . import flformdb, flfielddb

from typing import cast, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pnaction  # pragma: no cover
    from pineboolib.interfaces import isqlcursor  # noqa : F401 # pragma: no cover

DEBUG = False

LOGGER = logging.get_logger("FLFormRecordDB")


class FLFormRecordDB(flformdb.FLFormDB):
    """
    FLFormRecordDBInterface Class.

    FLFormDB subclass designed to edit records.

    Basically this class does the same as its class
    FLFormDB base, the only thing you add is two buttons
    Accept and / or Cancel to confirm or cancel
    the changes that are made to the components of
    data it contains.

    This class is suitable for loading forms
    editing records defined in metadata
    (FLTableMetaData).

    @author InfoSiAL S.L.
    """

    """
    Boton Aceptar
    """

    pushButtonAccept: Optional["QtWidgets.QToolButton"]

    """
    Boton Aceptar y continuar
    """
    pushButtonAcceptContinue: Optional["QtWidgets.QToolButton"]

    """
    Boton Primero
    """
    pushButtonFirst: Optional["QtWidgets.QToolButton"]

    """
    Boton Anterior
    """
    pushButtonPrevious: Optional["QtWidgets.QToolButton"]

    """
    Boton Siguiente
    """
    pushButtonNext: Optional["QtWidgets.QToolButton"]

    """
    Boton Ultimo
    """
    pushButtonLast: Optional["QtWidgets.QToolButton"]

    """
    Indica si se debe mostrar el botón Aceptar y Continuar
    """
    _show_accept_continue: bool

    """
    Indica que se está intentando aceptar los cambios
    """
    accepting: bool

    """
    Modo en el que inicialmente está el cursor
    """
    _initial_mode_access: int

    """
    Registra el nivel de anidamiento de transacciones en el que se entra al iniciar el formulario
    """
    _init_translation_level: int

    def __init__(
        self,
        action: "pnaction.PNAction",
        parent_or_cursor: Optional[Union["QtWidgets.QWidget", "isqlcursor.ISqlCursor", int]] = None,
        load: bool = False,
    ) -> None:
        """
        Inicialize.
        """
        LOGGER.trace(
            "__init__: parent_or_cursor=%s, action=%s, load=%s", parent_or_cursor, action, load
        )

        cursor: Optional["pnsqlcursor.PNSqlCursor"] = None
        parent: Optional["QtWidgets.QWidget"] = None

        if isinstance(parent_or_cursor, pnsqlcursor.PNSqlCursor):
            cursor = parent_or_cursor
        elif isinstance(parent_or_cursor, QtWidgets.QWidget):
            parent = parent_or_cursor

        super().__init__(action, parent, load)

        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)

        if cursor:
            self.setCursor(cursor)
        LOGGER.trace("__init__: load formRecord")
        self._ui_name = action.formRecord()
        self.pushButtonAccept = None  # pylint: disable=invalid-name
        self.pushButtonAcceptContinue = None  # pylint: disable=invalid-name
        self.pushButtonFirst = None  # pylint: disable=invalid-name
        self.pushButtonPrevious = None  # pylint: disable=invalid-name
        self.pushButtonNext = None  # pylint: disable=invalid-name
        self.pushButtonLast = None  # pylint: disable=invalid-name

        self.accepting = False
        self._show_accept_continue = True
        self._initial_mode_access = pnsqlcursor.PNSqlCursor.Browse

        if self.cursor_:
            self._initial_mode_access = self.cursor_.modeAccess()

        LOGGER.trace("__init__: load form")
        self.load()
        LOGGER.trace("__init__: init form")
        self.initForm()
        LOGGER.trace("__init__: done")
        self.loop = False

    def setCaptionWidget(self, text: Optional[str] = None) -> None:
        """
        Set the window title.
        """
        if not self.cursor_:
            return

        if not text:
            text = self.cursor_.metadata().alias()

        try:
            if self.cursor_.modeAccess() == self.cursor_.Insert:
                self.setWindowTitle("Insertar %s" % text)
            elif self.cursor_.modeAccess() == self.cursor_.Edit:
                self.setWindowTitle("Editar %s" % text)
            elif self.cursor_.modeAccess() == self.cursor_.Browse:
                self.setWindowTitle("Visualizar %s" % text)
        except RuntimeError as error:
            LOGGER.warning(str(error))

    def formClassName(self) -> str:
        """
        Return the class name of the form at runtime.
        """

        return "FormRecordDB"

    def initForm(self) -> None:
        """
        Initialize the form.
        """

        if self.cursor_ and self.cursor_.metadata():
            # caption = None
            if self._action:
                self.cursor().setAction(self._action)
                if self._action.description():
                    self.setWhatsThis(self._action.description())
                self._id_mdi = self._action.name()

            # self.bindIface()
            # self.setCursor(self.cursor_)

        else:
            self.setCaptionWidget("No hay metadatos")

        acl = application.PROJECT.aq_app.acl()
        if acl:
            acl.process(self)

    def loadControls(self) -> None:
        """Load widgets for this form."""
        if self.pushButtonAcceptContinue:
            self.pushButtonAcceptContinue.hide()

        if self.pushButtonAccept:
            self.pushButtonAccept.hide()

        if self.pushButtonCancel:
            self.pushButtonCancel.hide()

        if self.pushButtonFirst:
            self.pushButtonFirst.hide()

        if self.pushButtonPrevious:
            self.pushButtonPrevious.hide()

        if self.pushButtonNext:
            self.pushButtonNext.hide()

        if self.pushButtonLast:
            self.pushButtonLast.hide()

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
            pushButtonExport.setWhatsThis("Exportar a XML(F3)")
            pushButtonExport.setToolTip("Exportar a XML(F3)")
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

        if self.cursor().modeAccess() in (self.cursor().Edit, self.cursor().Browse):
            if not self.pushButtonFirst:
                self.pushButtonFirst = QtWidgets.QToolButton()
                self.pushButtonFirst.setObjectName("pushButtonFirst")
                self.pushButtonFirst.setIcon(
                    QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-goto-first-ltr.png"))
                )
                self.pushButtonFirst.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.firstRecord
                )
                self.pushButtonFirst.setSizePolicy(size_policy)
                self.pushButtonFirst.setMaximumSize(push_button_size)
                self.pushButtonFirst.setMinimumSize(push_button_size)
                self.pushButtonFirst.setShortcut(QtGui.QKeySequence(self.tr("F5")))
                self.pushButtonFirst.setWhatsThis(
                    "Aceptar los cambios e ir al primer registro (F5)"
                )
                self.pushButtonFirst.setToolTip("Aceptar los cambios e ir al primer registro (F5)")
                self.pushButtonFirst.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self.bottomToolbar.layout().addWidget(self.pushButtonFirst)
                # self.pushButtonFirst.show()

            if not self.pushButtonPrevious:
                self.pushButtonPrevious = QtWidgets.QToolButton()
                self.pushButtonPrevious.setObjectName("pushButtonPrevious")
                self.pushButtonPrevious.setIcon(
                    QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-go-back-ltr.png"))
                )
                self.pushButtonPrevious.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.previousRecord
                )
                self.pushButtonPrevious.setSizePolicy(size_policy)
                self.pushButtonPrevious.setMaximumSize(push_button_size)
                self.pushButtonPrevious.setMinimumSize(push_button_size)
                self.pushButtonPrevious.setShortcut(QtGui.QKeySequence(self.tr("F6")))
                self.pushButtonPrevious.setWhatsThis(
                    "Aceptar los cambios e ir al registro anterior (F6)"
                )
                self.pushButtonPrevious.setToolTip(
                    "Aceptar los cambios e ir al registro anterior (F6)"
                )
                self.pushButtonPrevious.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self.bottomToolbar.layout().addWidget(self.pushButtonPrevious)
                # self.pushButtonPrevious.show()

            if not self.pushButtonNext:
                self.pushButtonNext = QtWidgets.QToolButton()
                self.pushButtonNext.setObjectName("pushButtonNext")
                self.pushButtonNext.setIcon(
                    QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-go-back-rtl.png"))
                )
                self.pushButtonNext.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.nextRecord
                )
                self.pushButtonNext.setSizePolicy(size_policy)
                self.pushButtonNext.setMaximumSize(push_button_size)
                self.pushButtonNext.setMinimumSize(push_button_size)
                self.pushButtonNext.setShortcut(QtGui.QKeySequence(self.tr("F7")))
                self.pushButtonNext.setWhatsThis(
                    "Aceptar los cambios e ir al registro siguiente (F7)"
                )
                self.pushButtonNext.setToolTip(
                    "Aceptar los cambios e ir al registro siguiente (F7)"
                )
                self.pushButtonNext.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self.bottomToolbar.layout().addWidget(self.pushButtonNext)
                # self.pushButtonNext.show()

            if not self.pushButtonLast:
                self.pushButtonLast = QtWidgets.QToolButton()
                self.pushButtonLast.setObjectName("pushButtonLast")
                self.pushButtonLast.setIcon(
                    QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-goto-last-ltr.png"))
                )
                self.pushButtonLast.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.lastRecord
                )
                self.pushButtonLast.setSizePolicy(size_policy)
                self.pushButtonLast.setMaximumSize(push_button_size)
                self.pushButtonLast.setMinimumSize(push_button_size)
                self.pushButtonLast.setShortcut(QtGui.QKeySequence(self.tr("F8")))
                self.pushButtonLast.setWhatsThis("Aceptar los cambios e ir al último registro (F8)")
                self.pushButtonLast.setToolTip("Aceptar los cambios e ir al último registro (F8)")
                self.pushButtonLast.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self.bottomToolbar.layout().addWidget(self.pushButtonLast)
                # self.pushButtonLast.show()

        if not self.cursor().modeAccess() == self.cursor().Browse:
            self.pushButtonAcceptContinue = QtWidgets.QToolButton()
            self.pushButtonAcceptContinue.setObjectName("pushButtonAcceptContinue")
            self.pushButtonAcceptContinue.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                self.acceptContinue
            )
            self.pushButtonAcceptContinue.setSizePolicy(size_policy)
            self.pushButtonAcceptContinue.setMaximumSize(push_button_size)
            self.pushButtonAcceptContinue.setMinimumSize(push_button_size)
            self.pushButtonAcceptContinue.setIcon(
                QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-refresh.png"))
            )
            self.pushButtonAcceptContinue.setShortcut(QtGui.QKeySequence(self.tr("F9")))
            self.pushButtonAcceptContinue.setWhatsThis(
                "Aceptar los cambios y continuar con la edición de un nuevo registro (F9)"
            )
            self.pushButtonAcceptContinue.setToolTip(
                "Aceptar los cambios y continuar con la edición de un nuevo registro (F9)"
            )
            self.pushButtonAcceptContinue.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.bottomToolbar.layout().addWidget(self.pushButtonAcceptContinue)
            if not self._show_accept_continue:
                self.pushButtonAcceptContinue.close()
                # self.pushButtonAcceptContinue.show()

            if not self.pushButtonAccept:
                self.pushButtonAccept = QtWidgets.QToolButton()
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
            self.pushButtonAccept.setShortcut(QtGui.QKeySequence(self.tr("F10")))
            self.pushButtonAccept.setWhatsThis("Aceptar los cambios y cerrar formulario (F10)")
            self.pushButtonAccept.setToolTip("Aceptar los cambios y cerrar formulario (F10)")
            self.pushButtonAccept.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.bottomToolbar.layout().addWidget(self.pushButtonAccept)
            # self.pushButtonAccept.show()

        if not self.pushButtonCancel:
            self.pushButtonCancel = QtWidgets.QToolButton()
            self.pushButtonCancel.setObjectName("pushButtonCancel")
            try:
                self.cursor().autoCommit.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.disablePushButtonCancel
                )
            except Exception:
                pass

            self.pushButtonCancel.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                self.reject
            )

        self.pushButtonCancel.setSizePolicy(size_policy)
        self.pushButtonCancel.setMaximumSize(push_button_size)
        self.pushButtonCancel.setMinimumSize(push_button_size)
        self.pushButtonCancel.setShortcut(QtGui.QKeySequence(self.tr("Esc")))
        self.pushButtonCancel.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-stop.png"))
        )
        if not self.cursor().modeAccess() == self.cursor().Browse:
            self.pushButtonCancel.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.pushButtonCancel.setWhatsThis("Cancelar los cambios y cerrar formulario (Esc)")
            self.pushButtonCancel.setToolTip("Cancelar los cambios y cerrar formulario (Esc)")
        else:
            self.pushButtonCancel.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            self.pushButtonCancel.setFocus()
            # pushButtonCancel->setAccel(4096); FIXME
            self.pushButtonCancel.setWhatsThis("Aceptar y cerrar formulario (Esc)")
            self.pushButtonCancel.setToolTip("Aceptar y cerrar formulario (Esc)")

        # pushButtonCancel->setDefault(true);
        self.bottomToolbar.layout().addItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
            )
        )
        self.bottomToolbar.layout().addWidget(self.pushButtonCancel)
        # self.pushButtonAccept.show()

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        # self.toolButtonAccept = QtGui.QToolButton()
        # self.toolButtonAccept.setIcon(QtGui.QIcon(utils_base.filedir("./core/images/icons","gtk-add.png")))
        # self.toolButtonAccept.clicked.connect(self.validateForm)
        # self.bottomToolbar.layout.addWidget(self.toolButtonAccept)
        self.inicializeControls()

    def formName(self) -> str:
        """
        Return internal form name.
        """

        return "formRecord%s" % self._id_mdi

    def closeEvent(self, event: "QtGui.QCloseEvent") -> None:
        """
        Capture event close.
        """
        self.frameGeometry()
        if self.focusWidget():
            parent = self.focusWidget().parentWidget()
            if parent:
                fdb = cast(flfielddb.FLFieldDB, parent)
                acf_ = getattr(fdb, "autoComFrame_", None)
                if acf_ and acf_.autoComFrame_.isVisible():
                    acf_.hide()
                    return

        if self.cursor_:

            try:
                levels = self.cursor_.transactionLevel() - self._init_translation_level
                if levels > 0:
                    self.cursor_.rollbackOpened(
                        levels,
                        "Se han detectado transacciones no finalizadas en la última operación.\n"
                        "Se van a cancelar las transacciones pendientes.\n"
                        "Los últimos datos introducidos no han sido guardados, por favor\n"
                        "revise sus últimas acciones y repita las operaciones que no\n"
                        "se han guardado.\n"
                        "FLFormRecordDB::closeEvent: %s %s" % (levels, self.name()),
                    )
            except Exception:
                print("ERROR: FLFormRecordDB @ closeEvent :: las transacciones aún no funcionan.")

            if self.accepted_:
                if self.cursor_.commit():
                    self.afterCommitTransaction()
            else:
                if not self.cursor_.rollback():
                    event.ignore()

            self.setCursor(None)

        self.closed.emit()

        super().closeEvent(event)
        # self.deleteLater()

    def validateForm(self) -> bool:
        """
        Form validation.

        Call the "validateForm" function of the associated script when the
        form and only continue with the commit commit when that function
        of script returns TRUE.

        If FLTableMetaData :: concurWarn () is true and two or more sessions / users are.
        Modifying the same fields will display a warning notice.

        @return TRUE if the form has been validated correctly.
        """

        if not self.cursor_:
            return True
        # metadata = self.cursor_.metadata()

        # if self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Edit and metadata.concurWarn():
        #    col_fields = self.cursor_.concurrencyFields()

        #    if col_fields:
        #        pk_name = metadata.primaryKey()
        #        pk_where = (
        #            self.cursor_.db()
        #            .connManager()
        #            .manager()
        #            .formatAssignValue(metadata.field(pk_name), self.cursor_.valueBuffer(pk_name))
        #        )
        #        qry = pnsqlquery.PNSqlQuery(None, self.cursor_.db().connectionName())
        #        qry.setTablesList(metadata.name())
        #        qry.setSelect(col_fields)
        #        qry.setFrom(metadata.name())
        #        qry.setWhere(pk_where)
        #        qry.setForwardOnly(True)

        #        if qry.exec_() and qry.next():
        #            i = 0
        #            for field in col_fields:
        #                # msg = "El campo '%s' con valor '%s' ha sido modificado\npor otro usuario con el valor '%s'" % (
        #                #    mtd.fieldNameToAlias(field), self.cursor_.valueBuffer(field), q.value(i))
        #                res = QtWidgets.QMessageBox.warning(
        #                    QtWidgets.QApplication.focusWidget(),
        #                    "Aviso de concurrencia",
        #                    "\n\n ¿ Desea realmente modificar este campo ?\n\n"
        #                    "Sí : Ignora el cambio del otro usuario y utiliza el valor que acaba de introducir\n"
        #                    "No : Respeta el cambio del otro usuario e ignora el valor que ha introducido\n"
        #                    "Cancelar : Cancela el guardado del registro y vuelve a la edición del registro\n\n",
        #                    cast(
        #                        QtWidgets.QMessageBox.StandardButtons,
        #                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Default,
        #                    ),
        #                    cast(
        #                        QtWidgets.QMessageBox.StandardButton,
        #                        QtWidgets.QMessageBox.No
        #                        | QtWidgets.QMessageBox.Cancel
        #                        | QtWidgets.QMessageBox.Escape,
        #                    ),
        #                )
        #                if res == QtWidgets.QMessageBox.Cancel:
        #                    return False

        #                if res == QtWidgets.QMessageBox.No:
        #                    self.cursor_.setValueBuffer(field, qry.value(i))

        if self.cursor_.modeAccess() in [self.cursor_.Insert, self.cursor_.Edit]:
            fun_ = getattr(self.iface, "validateForm", self.validateForm)
            if fun_ != self.validateForm:
                ret_ = fun_()

                if isinstance(ret_, bool):
                    return ret_

        return True

    def acceptedForm(self) -> None:
        """
        Accept of form.

        Call the "acceptedForm" function of the script associated with the form, when
        the form is accepted and just before committing the registration.
        """

        fun_ = getattr(self.iface, "acceptedForm", self.acceptedForm)
        if fun_ != self.acceptedForm:
            fun_()

    def afterCommitBuffer(self) -> None:
        """
        After setting the changes of the current record buffer.

        Call the "afterCommitBuffer" function of the script associated with the form
        right after committing the registry buffer.
        """

        fun_ = getattr(self.iface, "afterCommitBuffer", self.afterCommitBuffer)
        if fun_ != self.afterCommitBuffer:
            fun_()

    def afterCommitTransaction(self) -> None:
        """
        After fixing the transaction.

        Call the "afterCommitTransaction" function of the script associated with the form,
        right after finishing the current transaction accepting.
        """

        fun_ = getattr(self.iface, "afterCommitTransaction", self.afterCommitTransaction)
        if fun_ != self.afterCommitTransaction:
            fun_()

    def canceledForm(self) -> None:
        """
        Form Cancellation.

        Call the "canceledForm" function of the script associated with the form, when
        cancel the form.
        """
        fun_ = getattr(self.iface, "canceledForm", self.canceledForm)
        if fun_ != self.canceledForm:
            fun_()

    @decorators.pyqt_slot()
    def accept(self) -> None:
        """
        Activate pressing the accept button.
        """

        if self.accepting:
            return

        self.accepting = True

        if not self.cursor_:
            self.close()
            self.accepting = False
            return

        if not self.validateForm():
            self.accepting = False
            return

        if self.cursor_.checkIntegrity():
            self.acceptedForm()
            self.cursor_.setActivatedCheckIntegrity(False)
            if not self.cursor_.commitBuffer():
                self.accepting = False
                return
            else:
                self.cursor_.setActivatedCheckIntegrity(True)
        else:
            self.accepting = False
            return

        self.afterCommitBuffer()
        self.accepted_ = True
        self.close()
        self.accepting = False

    @decorators.pyqt_slot()
    def acceptContinue(self) -> None:
        """
        Activate pressing the accept and continue button.
        """
        if self.accepting:
            return

        self.accepting = True
        if not self.cursor_:
            self.close()
            self.accepting = False
            return

        if not self.validateForm():
            self.accepting = False
            return

        if self.cursor_.checkIntegrity():
            self.acceptedForm()
            self.cursor_.setActivatedCheckIntegrity(False)
            if self.cursor_.commitBuffer():
                self.cursor_.setActivatedCheckIntegrity(True)
                self.cursor_.commit()
                self.cursor_.setModeAccess(pnsqlcursor.PNSqlCursor.Insert)
                self.accepted_ = False
                caption = None
                if self._action:
                    caption = self._action.name()
                if not caption:
                    caption = self.cursor_.metadata().alias()
                self.cursor_.transaction()
                self.setCaptionWidget(caption)
                if self._init_focus_widget:
                    self._init_focus_widget.setFocus()
                self.cursor_.refreshBuffer()
                self.initScript()

        self.accepting = False

    @decorators.pyqt_slot()
    def reject(self) -> None:
        """
        Activate pressing the cancel button.
        """
        self.accepted_ = False
        self.canceledForm()
        self.close()

    @decorators.pyqt_slot()
    def firstRecord(self) -> None:
        """
        Go to the first record.
        """
        if self.cursor_ and not self.cursor_.at() == 0:
            if not self.validateForm():
                return

            if self.cursor_.checkIntegrity():
                self.acceptedForm()
                self.cursor_.setActivatedCheckIntegrity(False)
                if self.cursor_.commitBuffer(False):
                    self.cursor_.setActivatedCheckIntegrity(True)
                    # self.cursor_.commit()
                    self.cursor_.setModeAccess(self._initial_mode_access)
                    self.accepted_ = False
                    # self.cursor_.transaction()
                    self.cursor_.first()
                    self.setCaptionWidget()
                    self.initScript()

    @decorators.pyqt_slot()
    def previousRecord(self) -> None:
        """
        Go to the previous record.
        """
        if self.cursor_ and self.cursor_.isValid():
            if not self.validateForm():
                return

            if self.cursor_.checkIntegrity():
                self.acceptedForm()
                self.cursor_.setActivatedCheckIntegrity(False)
                if self.cursor_.commitBuffer(False):
                    self.cursor_.setActivatedCheckIntegrity(True)
                    # self.cursor_.commit()
                    self.cursor_.setModeAccess(self._initial_mode_access)
                    self.accepted_ = False
                    # self.cursor_.transaction()
                    if self.cursor_.at() == 0:
                        self.cursor_.last()
                    else:
                        self.cursor_.prev()
                    self.setCaptionWidget()
                    self.initScript()

    @decorators.pyqt_slot()
    def nextRecord(self) -> None:
        """
        Go to the next record.
        """

        if self.cursor_ and self.cursor_.isValid():
            if not self.validateForm():
                return

            if self.cursor_.checkIntegrity():
                self.acceptedForm()
                self.cursor_.setActivatedCheckIntegrity(False)
                if self.cursor_.commitBuffer(False):
                    self.cursor_.setActivatedCheckIntegrity(True)
                    # self.cursor_.commit()
                    self.cursor_.setModeAccess(self._initial_mode_access)
                    self.accepted_ = False
                    # self.cursor_.transaction()
                    if self.cursor_.at() == (self.cursor_.size() - 1):
                        self.cursor_.first()
                    else:
                        self.cursor_.next()
                    self.setCaptionWidget()
                    self.initScript()

    @decorators.pyqt_slot()
    def lastRecord(self) -> None:
        """
        Go to the last record.
        """
        if (
            self.cursor_
            and not self.cursor_.at() == (self.cursor_.size() - 1)
            and self.cursor_.isValid()
        ):
            if not self.validateForm():
                return

            if self.cursor_.checkIntegrity():
                self.acceptedForm()
                self.cursor_.setActivatedCheckIntegrity(False)
                if self.cursor_.commitBuffer(False):
                    self.cursor_.setActivatedCheckIntegrity(True)
                    # self.cursor_.commit()
                    self.cursor_.setModeAccess(self._initial_mode_access)
                    self.accepted_ = False
                    # self.cursor_.transaction()
                    self.cursor_.last()
                    self.setCaptionWidget()
                    self.initScript()

    @decorators.pyqt_slot()
    def disablePushButtonCancel(self) -> None:
        """
        Turn off the cancel button.
        """

        if self.pushButtonCancel:
            self.pushButtonCancel.setDisabled(True)

    def show(self) -> None:
        """Show this widget."""

        caption = self._action.caption()
        if not caption:
            caption = self.cursor().metadata().alias()

        cur = self.cursor_

        iface = getattr(self.script, "iface", None)

        if cur:
            if not cur.isValid():
                cur.model().refresh()

            if cur.modeAccess() in (cur.Insert, cur.Edit, cur.Browse):
                cur.transaction()
                self._init_translation_level = cur.transactionLevel()

            if cur.modeAccess() == pnsqlcursor.PNSqlCursor.Insert:
                self._show_accept_continue = True
            else:
                self._show_accept_continue = False

            self.loadControls()

            if iface is not None:
                cur.setContext(iface)

        self.setCaptionWidget(caption)
        super().show()

    def inicializeControls(self) -> None:
        """Initialize UI controls for this form."""
        from pineboolib.fllegacy.flfielddb import FLFieldDB

        for child_ in self.findChildren(QtWidgets.QWidget):
            if isinstance(child_, FLFieldDB):
                loaded = getattr(child_, "_loaded", None)
                if loaded is False:
                    QtCore.QTimer.singleShot(0, child_.load)

    def show_and_wait(self) -> None:
        """Show this form blocking for exit."""
        if self.loop:
            raise Exception("show_and_wait(): Se ha detectado una llamada recursiva")

        self.loop = True
        self.show()
        if self.eventloop:
            self.eventloop.exec()

        self.loop = False

    def hide(self) -> None:
        """Hide this form."""
        if self.loop:
            self.eventloop.exit()
