"""Flfieldb module."""

# -*- coding: utf-8 -*-

from PyQt6 import QtCore, QtGui, QtWidgets  # type: ignore[import]

from pineboolib.application.database import pnsqlcursor, pnsqlquery
from pineboolib.application.metadata import pnrelationmetadata
from pineboolib.application import types
from pineboolib.application.utils import xpm

from pineboolib.core.utils import utils_base
from pineboolib.core import settings, decorators

from pineboolib.q3widgets import qpushbutton, qtextedit, qlineedit, qcombobox

from pineboolib import application, logging

from . import (
    fllineedit,
    flutil,
    fldateedit,
    fltimeedit,
    flpixmapview,
    flspinbox,
    fldatatable,
    flcheckbox,
    fluintvalidator,
    flintvalidator,
    fldoublevalidator,
    flformsearchdb,
    fltabledb,
)

import datetime


from typing import Any, Optional, cast, Union, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor  # pragma: no cover

LOGGER = logging.get_logger(__name__)


class FLFieldDB(QtWidgets.QWidget):
    """FLFieldDB class."""

    _loaded: bool
    _parent: QtWidgets.QWidget

    _tipo: str
    _part_decimal: int
    autoSelect: bool

    editor_: Union[
        fllineedit.FLLineEdit,
        fldateedit.FLDateEdit,
        fltimeedit.FLTimeEdit,
        qtextedit.QTextEdit,
        flcheckbox.FLCheckBox,
        qcombobox.QComboBox,
        qlineedit.QLineEdit,
    ]  # Editor para el contenido del campo que representa el componente
    _editor_img: flpixmapview.FLPixmapView
    _field_name: str  # Nombre del campo de la tabla al que esta asociado este componente
    _table_name: str  # Nombre de la tabla fóranea
    _action_name: str  # Nombre de la accion
    _foreign_field: str  # Nombre del campo foráneo
    _field_relation: str  # Nombre del campo de la relación
    _filter: str  # Nombre del campo de la relación
    cursor_: Optional[
        "isqlcursor.ISqlCursor"
    ]  # Cursor con los datos de la tabla origen para el componente
    _cursor_init: bool  # Indica que si ya se ha inicializado el cursor
    _cursor_aux_init: bool  # Indica que si ya se ha inicializado el cursor auxiliar
    _cursor_aux: Optional[
        "isqlcursor.ISqlCursor"
    ]  # Cursor auxiliar de uso interno para almacenar los registros de la tabla relacionada con la de origen

    _showed: bool
    _show_alias: bool
    _auto_com_popup: Optional["fldatatable.FLDataTable"]
    _auto_com_frame: Optional["QtWidgets.QWidget"]
    _auto_com_field_name: str
    _auto_com_field_relation: Optional[str]
    _accel: Dict[str, "QtGui.QShortcut"]
    _keep_disabled: bool

    _pbaux: Optional["qpushbutton.QPushButton"]
    _pbaux2: Optional["qpushbutton.QPushButton"]
    _pbaux3: Optional["qpushbutton.QPushButton"]
    _pbaux4: Optional["qpushbutton.QPushButton"]
    _field_alias: Optional[str]
    _show_editor: bool
    _field_map_value: Optional["FLFieldDB"]
    _auto_com_mode: str  # NeverAuto, OnDemandF4, AlwaysAuto
    _timer_auto_comp: QtCore.QTimer
    _text_format: QtCore.Qt.TextFormat
    _init_not_null_color: bool
    _text_label_db: Optional[QtWidgets.QLabel]
    _widgets_layout: Optional[QtWidgets.QHBoxLayout]

    _refresh_later: Optional[str]

    _push_button_db: qpushbutton.QPushButton
    keyF4Pressed: QtCore.pyqtSignal = QtCore.pyqtSignal()
    labelClicked: QtCore.pyqtSignal = QtCore.pyqtSignal()
    keyReturnPressed: QtCore.pyqtSignal = QtCore.pyqtSignal()
    lostFocus: QtCore.pyqtSignal = QtCore.pyqtSignal()
    textChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    keyF2Pressed: QtCore.pyqtSignal = QtCore.pyqtSignal()

    _first_refresh: bool

    """
    Tamaño de icono por defecto
    """
    _icon_size: QtCore.QSize

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """Inicialize."""

        super(FLFieldDB, self).__init__(parent)
        self._loaded = False

        # self.editor_ = QtWidgets.QWidget(parent)
        # self.editor_.hide()
        self.cursor_ = None
        self._cursor_init = False
        self._cursor_aux_init_ = False
        self._show_alias = True
        self._show_editor = True
        self._auto_com_mode = "OnDemandF4"
        self._auto_com_popup = None
        self._auto_com_frame = None
        self._auto_com_field_relation = None
        self.setObjectName("FLFieldDB")
        self._showed = False
        self._refresh_later = None
        self._keep_disabled = False
        self._init_not_null_color = False
        self._action_name = ""
        self._pbaux = None
        self._pbaux2 = None
        self._pbaux3 = None
        self._pbaux4 = None
        self._accel = {}
        self._text_format = QtCore.Qt.TextFormat.AutoText
        self._text_label_db = None
        self._widgets_layout = None
        self._first_refresh = False
        self._field_map_value = None

        self._max_pix_size = settings.CONFIG.value("ebcomportamiento/maxPixImages", None)
        self._auto_com_mode = settings.CONFIG.value("ebcomportamiento/autoComp", "OnDemandF4")
        if self._max_pix_size in (None, ""):
            self._max_pix_size = 600
        self._max_pix_size = int(self._max_pix_size)
        # self._editor_img = None

        self._icon_size = application.PROJECT.DGI.icon_size()

        self._horizontal_layout = QtWidgets.QVBoxLayout(self)
        self._horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self._horizontal_layout.setSpacing(1)
        # self._horizontal_layout.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)

        self._buttons_layout = QtWidgets.QHBoxLayout()
        self._buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._buttons_layout.setSpacing(1)
        self._buttons_layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)

        # self._buttons_layout.SetMinimumSize(22,22)
        # self._buttons_layout.SetMaximumSize(22,22)

        self._widgets_layout = QtWidgets.QHBoxLayout()
        self._widgets_layout.setSpacing(1)
        self._widgets_layout.setContentsMargins(0, 0, 0, 0)
        self._widgets_layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        self._horizontal_layout.addLayout(self._buttons_layout)
        self._horizontal_layout.addLayout(self._widgets_layout)
        self._table_name = ""
        self._foreign_field = ""
        self._field_relation = ""
        self._field_name = ""

        self._text_label_db = QtWidgets.QLabel()
        self._text_label_db.setObjectName("_text_label_db")
        if self._text_label_db is not None:
            self._text_label_db.setMinimumHeight(16)  # No inicia originalmente aqui
            self._text_label_db.setAlignment(
                cast(
                    QtCore.Qt.AlignmentFlag,
                    QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft,
                )
            )
            # self._text_label_db.setFrameShape(QtGui.QFrame.WinPanel)
            self._text_label_db.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
            self._text_label_db.setLineWidth(0)
            self._text_label_db.setTextFormat(QtCore.Qt.TextFormat.PlainText)
            self._text_label_db.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
            )

        self._field_alias = ""
        self._filter = ""

        self._widgets_layout.addWidget(self._text_label_db)

        self._push_button_db = qpushbutton.QPushButton(self)
        self._push_button_db.setObjectName("_push_button_db")

        self.setFocusProxy(self._push_button_db)
        # self._push_button_db.setFlat(True)
        pb_size_polizy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        pb_size_polizy.setHeightForWidth(True)
        self._push_button_db.setSizePolicy(pb_size_polizy)
        self._push_button_db.setMinimumSize(self._icon_size)
        self._push_button_db.setMaximumSize(self._icon_size)
        self._push_button_db.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._push_button_db.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "flfielddb.png"))
        )
        self._push_button_db.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
            self.searchValue
        )

        self.timer_1 = QtCore.QTimer(self)

        self._cursor_aux = None

        from . import flformdb

        while not isinstance(parent, flformdb.FLFormDB):
            parent = parent.parentWidget()

            if not parent:
                break

        self._top_widget = cast(flformdb.FLFormDB, parent)

    def load(self) -> None:
        """Load the cursor and initialize the control according to the type of data."""

        if self._loaded:
            return

        self._loaded = True
        if self._top_widget:
            self.cursor_ = self._top_widget.cursor()
            # print("Hay topWidget en %s", self)

        if self.cursor_ and self.cursor_.private_cursor.buffer_:

            pass
            # LOGGER.info(
            #    "*** FLFieldDB::loaded: cursor: %r name: %r at:%r",
            #    self.cursor_,
            #    self.cursor_.curName(),
            #    self.cursor_.at(),
            # )
            # cur_values = [f.value for f in self.cursor_.private_cursor.buffer_.fieldsList()]
            # LOGGER.info("*** cursor Buffer: %r", cur_values)
        else:
            LOGGER.warning(
                "FLFieldDB::loaded: problem found!, top_widget: %s, cursor: %s, curname: %s, buffer. %s",
                self._top_widget,
                self.cursor_,
                self.cursor_.curName() if self.cursor_ is not None else None,
                self.cursor_.private_cursor.buffer_ if self.cursor_ is not None else None,
                stack_info=True,
            )

        self._part_decimal = 0
        self.initCursor()
        if (
            self._table_name
            and self.cursor_ is not None
            and not self.cursor_.db().connManager().manager().metadata(self._table_name)
        ):
            self.cursor_ = None
            self.initFakeEditor()
        else:
            self.initEditor()

    def setName(self, value: str) -> None:
        """Specify the name of the control."""
        self.setObjectName(str(value))

    def actionName(self) -> str:
        """
        Return the name of the action.

        @return Name of the action
        """
        if not self._action_name:
            raise ValueError("actionName is not defined!")
        return self._action_name

    def setActionName(self, action_name: str) -> None:
        """
        Set the name of the action.

        @param action_name Name of the action
        """
        self._action_name = str(action_name)

    def fieldName(self) -> str:
        """
        Return the name of the field.

        @return Field Name
        """

        if not self._field_name:
            raise ValueError("fieldName is not defined!")
        return self._field_name

    def setFilter(self, filter: str) -> None:
        """Set a filter to the cursor."""

        self._filter = filter
        self.setMapValue()

    def filter(self) -> str:
        """Return the cursor filter."""

        return self._filter

    def setFieldName(self, field_name: str) -> None:
        """
        Set the name of the field.

        @param field_name Field name
        """
        self._field_name = field_name

    def tableName(self) -> str:
        """
        Return the name of the foreign table.

        @return Table name
        """
        return self._table_name

    def setTableName(self, foreign_table: str) -> None:
        """
        Set the name of the foreign table.

        @param foreign_table Table name
        """

        if foreign_table:
            self._table_name = foreign_table
        else:
            self._table_name = ""

    def foreignField(self) -> str:
        """
        Return the name of the foreign field.

        @return Field Name
        """

        return self._foreign_field

    def setForeignField(self, foreign_field_name: str) -> None:
        """
        Set the name of the foreign field.

        @param foreign_field_name Field Name.
        """
        self._foreign_field = foreign_field_name

    def fieldRelation(self) -> str:
        """
        Return the name of the related field.

        @return Field Name.
        """

        return self._field_relation

    def setFieldRelation(self, field_relation: str) -> None:
        """
        Set the name of the related field.

        @param field_relation Field name
        """
        self._field_relation = field_relation

    def setFieldAlias(self, alias: str) -> None:
        """
        Set the field alias, shown on its label if showAlias is True.

        @param alias Field alias, is the value of the tag. If it is empty it does nothing.
        """

        if alias:
            self._field_alias = alias
            if self._show_alias and self._text_label_db:
                self._text_label_db.setText(self._field_alias)

    def setTextFormat(self, text_format: "QtCore.Qt.TextFormat") -> None:
        """
        Set the text format.

        @param text_format Text field format
        """
        # FIXME: apply to control!
        self._text_format = text_format
        # ted = self.editor_
        # if isinstance(ted, qtextedit.QTextEdit):
        #    ted.setTextFormat(self._text_format)

    def textFormat(self) -> "QtCore.Qt.TextFormat":
        """
        Return text field format.

        @return The format of the text.
        """

        # ted = self.editor_
        # if isinstance(ted, qtextedit.QTextEdit):
        #    return ted.textFormat()
        return self._text_format

    def setEchoMode(
        self, mode: "qlineedit.QLineEdit.EchoMode"  # type: ignore[name-defined]
    ) -> None:
        """
        Set the "echo" mode.

        @param mode Mode (Normal, NoEcho, Password)
        """
        if isinstance(self.editor_, (fllineedit.FLLineEdit, QtWidgets.QLineEdit)):
            self.editor_.setEchoMode(mode)

    def echoMode(self) -> "qlineedit.QLineEdit.EchoMode":  # type: ignore[name-defined]
        """
        Return the echo mode.

        @return The "echo" mode (Normal, NoEcho, Password)
        """
        if isinstance(self.editor_, (fllineedit.FLLineEdit, QtWidgets.QLineEdit)):
            return self.editor_.echoMode()
        else:
            return QtWidgets.QLineEdit.EchoMode.Normal

    def _process_autocomplete_events(self, event: QtCore.QEvent) -> bool:
        """Process autocomplete events."""

        timer_active = False
        if self._auto_com_frame and self._auto_com_frame.isVisible():
            if event.type() == QtCore.QEvent.Type.KeyPress:
                key = cast(QtGui.QKeyEvent, event)
            if key.key() == cast(int, QtCore.Qt.Key.Key_Down) and self._auto_com_popup:
                self._auto_com_popup.setQuickFocus()
                return True

            # --> WIN
            if self.editor_:
                self.editor_.releaseKeyboard()
            if self._auto_com_popup:
                self._auto_com_popup.releaseKeyboard()
            # <-- WIN

            self._auto_com_frame.hide()
            if self.editor_ and key.key() == cast(int, QtCore.Qt.Key.Key_Backspace):
                cast(fllineedit.FLLineEdit, self.editor_).backspace()

            if not self._timer_auto_comp:
                self._timer_auto_comp = QtCore.QTimer(self)
                self._timer_auto_comp.timeout.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.toggleAutoCompletion
                )
            else:
                self._timer_auto_comp.stop()

            if not key.key() in (
                cast(int, QtCore.Qt.Key.Key_Enter),
                cast(int, QtCore.Qt.Key.Key_Return),
            ):
                timer_active = True
                self._timer_auto_comp.start(500)
            else:
                QtCore.QTimer.singleShot(0, self.autoCompletionUpdateValue)
                return True
        if (
            not timer_active
            and self._auto_com_mode == "AlwaysAuto"
            and (not self._auto_com_frame or not self._auto_com_frame.isVisible())
        ):
            if key.key() in (
                cast(int, QtCore.Qt.Key.Key_Backspace),
                cast(int, QtCore.Qt.Key.Key_Delete),
                cast(int, QtCore.Qt.Key.Key_Space),
                cast(int, QtCore.Qt.Key.Key_ydiaeresis),
            ):
                if not self._timer_auto_comp:
                    self._timer_auto_comp = QtCore.QTimer(self)
                    self._timer_auto_comp.timeout.connect(  # type: ignore [attr-defined] # noqa: F821
                        self.toggleAutoCompletion
                    )
                else:
                    self._timer_auto_comp.stop()

                if not key.key() in (
                    cast(int, QtCore.Qt.Key.Key_Enter),
                    cast(int, QtCore.Qt.Key.Key_Return),
                ):
                    timer_active = True
                    self._timer_auto_comp.start(500)
                else:
                    QtCore.QTimer.singleShot(0, self.autoCompletionUpdateValue)
                    return True
        return False

    @decorators.pyqt_slot()
    @decorators.pyqt_slot(int)
    def eventFilter(self, obj: "QtCore.QObject", event: "QtCore.QEvent") -> bool:
        """
        Process Qt events for keypresses.
        """

        if obj is None:
            return True

        super().eventFilter(obj, event)
        if event.type() == QtCore.QEvent.Type.KeyPress:
            key_ = cast(QtGui.QKeyEvent, event)
            if self._process_autocomplete_events(event):
                return True

            if isinstance(obj, fllineedit.FLLineEdit):
                if key_.key() == cast(int, QtCore.Qt.Key.Key_F4):
                    self.keyF4Pressed.emit()
                    return True
            elif isinstance(obj, qtextedit.QTextEdit):
                if key_.key() == cast(int, QtCore.Qt.Key.Key_F4):
                    self.keyF4Pressed.emit()
                    return True
                return False

            if key_.key() in [
                cast(int, QtCore.Qt.Key.Key_Enter),
                cast(int, QtCore.Qt.Key.Key_Return),
            ]:
                self.focusNextPrevChild(True)
                self.keyReturnPressed.emit()
                return True

            elif key_.key() == cast(int, QtCore.Qt.Key.Key_Up):
                self.focusNextPrevChild(False)
                return True

            elif key_.key() == cast(int, QtCore.Qt.Key.Key_Down):
                self.focusNextPrevChild(True)
                return True

            elif key_.key() == cast(int, QtCore.Qt.Key.Key_F2):
                self.keyF2Pressed.emit()
                return True

            return False

        # elif isinstance(event, QtCore.QEvent.MouseButtonRelease) and
        # isinstance(obj,self._text_label_db) and event.button() == QtCore.Qt.LeftButton:
        elif (
            event.type() == QtCore.QEvent.Type.MouseButtonRelease
            and isinstance(obj, type(self._text_label_db))
            and cast(QtGui.QMouseEvent, event).button() == QtCore.Qt.MouseButton.LeftButton
        ):
            self.emitLabelClicked()
            return True
        else:
            return False

    @decorators.pyqt_slot()
    def updateValue(self, data: Any = None):
        """
        Update the value of the field with a text string.

        @param data Text string to update the field
        """

        if not self.cursor_ or self._table_name:
            return

        is_null = False
        data = None

        if hasattr(self, "editor_"):

            if isinstance(self.editor_, fldateedit.FLDateEdit):
                data = str(self.editor_.getDate())
                if not data:
                    is_null = True

                if not self.cursor_.bufferIsNull(self._field_name):

                    if str(data) == self.cursor_.valueBuffer(self._field_name):
                        return
                elif is_null:
                    return

                data = QtCore.QDate().toString("dd-MM-yyyy") if is_null else data

            elif isinstance(self.editor_, fltimeedit.FLTimeEdit):
                data = str(self.editor_.time().toString("hh:mm:ss"))

                if not data:
                    is_null = True
                if not self.cursor_.bufferIsNull(self._field_name):

                    if str(data) == self.cursor_.valueBuffer(self._field_name):
                        return
                elif is_null:
                    return

                data = str(QtCore.QTime().toString("hh:mm:ss")) if is_null else data

            elif isinstance(self.editor_, flcheckbox.FLCheckBox):
                data = self.editor_.checked
                if not self.cursor_.bufferIsNull(self._field_name):
                    if data == bool(self.cursor_.valueBuffer(self._field_name)):
                        return

            elif isinstance(self.editor_, qtextedit.QTextEdit):
                data = str(self.editor_.toPlainText())
                if not self.cursor_.bufferIsNull(self._field_name):
                    if self.cursor_.valueBuffer(self._field_name) == data:
                        return

            elif isinstance(self.editor_, fllineedit.FLLineEdit):

                data = self.editor_.text()

                if not self.cursor_.bufferIsNull(self._field_name):
                    if data == self.cursor_.valueBuffer(self._field_name):
                        return

            elif isinstance(self.editor_, qcombobox.QComboBox):
                data = str(self.editor_.getCurrentText())

                if not self.cursor_.bufferIsNull(self._field_name):
                    if data == self.cursor_.valueBuffer(self._field_name):
                        return

        elif hasattr(self, "_editor_img"):
            if data == self.cursor_.valueBuffer(self._field_name):
                return

        if data is not None:
            self.cursor_.setValueBuffer(self._field_name, data)

    def status(self) -> None:
        """
        Return a report with the control status.
        """

        LOGGER.info("****************STATUS**************")
        LOGGER.info("FLField: %s", self._field_name)
        LOGGER.info("FieldAlias: %s", self._field_alias)
        LOGGER.info("FieldRelation: %s", self._field_relation)
        LOGGER.info("Cursor: %s", self.cursor_)
        LOGGER.info("CurName: %s", self.cursor().curName() if self.cursor_ else None)
        LOGGER.info(
            "Editor: %s, EditorImg: %s"
            % (getattr(self, "editor_", None), getattr(self, "_editor_img", None))
        )
        LOGGER.info("RefreshLaterEditor: %s", self._refresh_later)
        LOGGER.info("************************************")

    def setValue(self, value: Any = "") -> None:
        """
        Set the value contained in the field.

        @param v Value to set
        """

        if not self.cursor_:
            LOGGER.error(
                "FLFieldDB(%s):ERROR: El control no tiene cursor todavía. (%s)",
                self._field_name,
                self,
            )
            return
        # if v:
        #    print("FLFieldDB(%s).setValue(%s) ---> %s" % (self._field_name, v, self.editor_))
        if value is None:
            value = ""

        table_metadata = self.cursor_.metadata()
        if not table_metadata:
            return

        field = table_metadata.field(self._field_name)
        if field is None:
            LOGGER.warning("FLFieldDB::setValue(%s) : No existe el campo ", self._field_name)
            return

        type_ = field.type()

        # v = QVariant(cv)
        if field.hasOptionsList():
            idx = -1
            if type_ == "string":
                if value in field.optionsList():
                    idx = field.optionsList().index(value)
                else:
                    LOGGER.warning(
                        "No se encuentra el valor %s en las opciones %s", value, field.optionsList()
                    )
            if idx == -1:
                cast(qcombobox.QComboBox, self.editor_).setCurrentItem(value)
            self.updateValue(cast(qcombobox.QComboBox, self.editor_).currentText)
            return

        if type_ == "pixmap":
            if self._editor_img:

                if not value:
                    self._editor_img.clear()
                    return
                pix = QtGui.QPixmap(value)
                # if not QtGui.QPixmapCache().find(cs.left(100), pix):
                # print("FLFieldDB(%s) :: La imagen no se ha cargado correctamente" % self._field_name)
                #    QtGui.QPixmapCache().insert(cs.left(100), pix)
                # print("PIX =", pix)
                if pix:
                    self._editor_img.setPixmap(pix)
                else:
                    self._editor_img.clear()
        else:
            if not self.editor_:
                return

        if type_ in ("uint", "int"):
            do_home = False
            editor_int = cast(fllineedit.FLLineEdit, self.editor_)
            if not editor_int.text():
                do_home = True

            editor_int.setText(value if value else 0)

            if do_home:
                editor_int.home(False)

        elif type_ == "string":
            do_home = False
            editor_str = cast(fllineedit.FLLineEdit, self.editor_)
            if not editor_str.text():
                do_home = True

            editor_str.setText(value)

            if do_home:
                editor_str.home(False)

        elif type_ == "stringlist":

            cast(fllineedit.FLLineEdit, self.editor_).setText(value)

        elif type_ == "double":
            num_ = str(round(float(value or 0), self._part_decimal or field.partDecimal()))

            cast(fllineedit.FLLineEdit, self.editor_).setText(num_)

        elif type_ == "serial":
            cast(fllineedit.FLLineEdit, self.editor_).setText(value)

        elif type_ == "date":
            editor_date = cast(fldateedit.FLDateEdit, self.editor_)
            if not value:
                editor_date.setDate(QtCore.QDate())
            elif isinstance(value, str):
                if value.find("T") > -1:
                    value = value[0 : value.find("T")]
                editor_date.setDate(QtCore.QDate.fromString(value, "yyyy-MM-dd"))
            else:
                editor_date.setDate(value)

        elif type_ == "time":
            if not value:
                value = QtCore.QTime()

            cast(fltimeedit.FLTimeEdit, self.editor_).setTime(value)

        elif type_ == "bool":
            if value not in [None, ""]:
                cast(flcheckbox.FLCheckBox, self.editor_).setChecked(value)

        elif type_ == "timestamp":
            do_home = False
            editor_ts = cast(fllineedit.FLLineEdit, self.editor_)
            if not editor_ts.text():
                do_home = True

            editor_ts.setText(value)

            if do_home:
                editor_ts.home(False)
        elif type_ == "json":
            do_home = False
            editor_ts = cast(fllineedit.FLLineEdit, self.editor_)
            if not editor_ts.text():
                do_home = True

            editor_ts.setText(value)

            if do_home:
                editor_ts.home(False)

    def value(self) -> Any:
        """
        Return the value contained in the field.
        """
        if not self.cursor_:
            return None

        table_metadata = self.cursor_.metadata()
        if not table_metadata:
            return None

        field = table_metadata.field(self._field_name)
        if field is None:
            LOGGER.warning(self.tr("FLFieldDB::value() : No existe el campo %s" % self._field_name))
            return None

        value: Any = None

        if field.hasOptionsList():
            value = int(cast(qcombobox.QComboBox, self.editor_).currentItem())
            return value

        type_ = field.type()
        # fltype = FLFieldMetaData.flDecodeType(type_)

        if self.cursor_.bufferIsNull(self._field_name):
            if type_ == "double" or type_ == "int" or type_ == "uint":
                return 0

        if type_ in ("string", "stringlist", "timestamp", "json"):
            if self.editor_:
                ed_ = self.editor_
                if isinstance(ed_, fllineedit.FLLineEdit):
                    value = ed_.text()

        if type_ in ("int", "uint"):
            if self.editor_:
                ed_ = self.editor_
                if isinstance(ed_, fllineedit.FLLineEdit):
                    value = ed_.text()
                    if value == "":
                        value = 0
                    else:
                        value = int(value)

        if type_ == "double":
            if self.editor_:
                ed_ = self.editor_
                if isinstance(ed_, fllineedit.FLLineEdit):
                    value = ed_.text()
                    if value == "":
                        value = 0.00
                    else:
                        value = float(value)

        elif type_ == "serial":
            if self.editor_:
                ed_ = self.editor_
                if isinstance(ed_, flspinbox.FLSpinBox):
                    value = ed_.value()

        elif type_ == "pixmap":
            value = self.cursor_.valueBuffer(self._field_name)

        elif type_ == "date":
            if self.editor_:
                value = cast(fldateedit.FLDateEdit, self.editor_).date
                if value:

                    value = types.Date(value)

        elif type_ == "time":
            if self.editor_:
                value = cast(fltimeedit.FLTimeEdit, self.editor_).time().toString()

        elif type_ == "bool":
            if self.editor_:
                value = cast(flcheckbox.FLCheckBox, self.editor_).isChecked()

        # v.cast(fltype)
        return value

    def selectAll(self) -> None:
        """
        Mark the field content as selected.
        """
        if not self.cursor_:
            return

        if not self.cursor_.metadata():
            return

        field = self.cursor_.metadata().field(self._field_name)
        if field is None:
            return
        type_ = field.type()

        if type_ in ("double", "int", "uint", "string", "timestamp", "json"):
            editor_le = cast(fllineedit.FLLineEdit, self.editor_)
            if editor_le:
                editor_le.selectAll()

        elif type_ == "serial":
            editor_se = cast(fllineedit.FLLineEdit, self.editor_)
            if editor_se:
                editor_se.selectAll()

    def cursor(self) -> "isqlcursor.ISqlCursor":  # type: ignore [override] # noqa F821
        """
        Return the cursor from where the data is obtained.

        Very useful to be used in external table mode (fieldName and tableName
        defined, foreingField and blank fieldRelation).
        """
        if self.cursor_ is None:
            raise Exception("cursor_ is empty!.")

        return self.cursor_

    def showAlias(self) -> bool:
        """
        Return the value of the showAlias property.

        This property is used to know if you have to show the alias when you are
        in related cursor mode.
        """

        return self._show_alias

    def setShowAlias(self, value: bool) -> None:
        """
        Set the state of the showAlias property.
        """

        self._show_alias = value
        if self._text_label_db:
            if self._show_alias:
                self._text_label_db.show()
            else:
                self._text_label_db.hide()

    def insertAccel(self, key: str) -> str:
        """
        Insert a key combination as a keyboard accelerator, returning its identifier.

        @param key Text string representing the key combination (eg "Ctrl + Shift + O")
        @return The identifier internally associated with the key combination acceleration inserted
        """

        if str(key) not in self._accel.keys():
            accel = QtGui.QShortcut(QtGui.QKeySequence(key), self)
            # accel.activated.connect(self.ActivatedAccel)
            self._accel[str(accel.id())] = accel  # type: ignore [attr-defined]

        return str(accel.id())  # type: ignore [attr-defined]

    def removeAccel(self, key: str) -> bool:
        """
        Eliminate, deactivate, a combination of acceleration keys according to their identifier.

        @param identifier Accelerator key combination identifier
        """

        if str(key) in self._accel.keys():
            del self._accel[str(key)]

        return True

    def setKeepDisabled(self, keep: bool) -> None:
        """
        Set the ability to keep the component disabled ignoring possible ratings for refreshments.

        See FLFieldDB :: _keep_disabled.
        """

        self._keep_disabled = keep

    def showEditor(self) -> bool:
        """
        Return the value of the showEditor property.
        """
        return self._show_editor

    def setShowEditor(self, show: bool) -> None:
        """
        Set the value of the showEditor property.
        """

        self._show_editor = show
        editor: Optional["QtWidgets.QWidget"] = None
        if hasattr(self, "editor_"):
            editor = self.editor_
        elif hasattr(self, "_editor_img"):
            editor = self._editor_img

        if editor:
            if show:
                editor.show()
            else:
                editor.hide()

    def setPartDecimal(self, part_decimal: int) -> None:
        """
        Set the number of decimals.
        """
        self._part_decimal = part_decimal
        self.refreshQuick(self._field_name)
        # self.editor_.setText(self.editor_.text(),False)

    def setAutoCompletionMode(self, mode: str) -> None:
        """
        Set automatic completion assistant mode.
        """
        self._auto_com_mode = mode

    def autoCompletionMode(self) -> str:
        """
        Return automatic completion assistant mode.
        """
        return self._auto_com_mode

    @decorators.pyqt_slot()
    @decorators.pyqt_slot("QString")
    def refresh(self, field_name: Optional[str] = None) -> None:
        """
        Refresh the content of the field with the cursor values of the source table.

        If the name of a field is indicated it only "refreshes" if the indicated field
        matches the fieldRelation property, taking the field value as a filter
        fieldRelation of the related table. If no name of Field refreshment is always carried out.

        @param field_name Name of a field
        """

        if not self.cursor_ or not isinstance(self.cursor_, pnsqlcursor.PNSqlCursor):
            LOGGER.debug("FLField.refresh() Cancelado")
            return
        table_metadata = self.cursor_.metadata()
        if not table_metadata:
            return

        value = None
        nulo = False
        if not field_name:
            value = self.cursor_.valueBuffer(self._field_name)
            nulo = (
                self.cursor_.isNull(self._field_relation)
                if self._field_relation
                else self.cursor_.isNull(self._field_name)
            )

            # if self.cursor_.cursorRelation():
            # print(1)
            # if self.cursor_.cursorRelation().valueBuffer(self._field_relation) in ("", None):
            # FIXME: Este código estaba provocando errores al cargar formRecord hijos
            # ... el problema es, que posiblemente el cursorRelation entrega información
            # ... errónea, y aunque comentar el código soluciona esto, seguramente esconde
            # ... otros errores en el cursorRelation. Pendiente de investigar más.
            # v = None
            # if DEBUG: print("FLFieldDB: valueBuffer padre vacío.")

        else:
            if not self._field_relation:
                raise ValueError("_field_relation is not defined!")

            if not self._cursor_aux and field_name.lower() == self._field_relation.lower():
                if self.cursor_.bufferIsNull(self._field_relation):
                    return

                field = table_metadata.field(self._field_relation)
                if field is None:
                    return

                relation_m1 = field.relationM1()
                if relation_m1 is None:
                    return

                tmd = pnsqlcursor.PNSqlCursor(relation_m1.foreignTable()).private_cursor.metadata_
                if tmd is None:
                    return

                if not field.relationM1():
                    LOGGER.info("FLFieldDB :El campo de la relación debe estar relacionado en M1")
                    return

                value = self.cursor_.valueBuffer(self._field_relation)
                qry = pnsqlquery.PNSqlQuery()
                qry.setForwardOnly(True)
                relation_m1 = field.relationM1()
                if relation_m1 is None:
                    raise ValueError("relationM1 does not exist!")

                qry.setTablesList(relation_m1.foreignTable())
                qry.setSelect("%s,%s" % (self.foreignField(), relation_m1.foreignField()))
                qry.setFrom(relation_m1.foreignTable())
                where = field.formatAssignValue(relation_m1.foreignField(), value, True)
                filter_ac = self.cursor_.filterAssoc(self._field_relation, tmd)
                if filter_ac:
                    if not where:
                        where = filter_ac
                    else:
                        where += " AND %s" % filter_ac

                # if not self._filter:
                #    q.setWhere(where)
                # else:
                #    q.setWhere(str(self._filter + " AND " + where))
                if self._filter:
                    where = "%s AND %s" % (self._filter, where)

                qry.setWhere(where)
                if qry.exec_() and qry.next():
                    value_0 = qry.value(0)
                    value_1 = qry.value(1)
                    if not value_0 == self.value():
                        self.setValue(value_0)
                    if not value_1 == value:
                        self.cursor_.setValueBuffer(self._field_relation, value_1)

            return

        field = table_metadata.field(str(self._field_name))
        if field is None:
            return
        type_ = field.type()

        if (
            not type_ == "pixmap"
            and getattr(self, "editor_", None) is None
            and field_name is not None
        ):
            self._refresh_later = field_name
            return

        mode_access = self.cursor_.modeAccess()
        part_decimal = None
        if self._part_decimal:
            part_decimal = self._part_decimal
        else:
            part_decimal = field.partDecimal() or 0
            self._part_decimal = field.partDecimal()

        hol = field.hasOptionsList()

        field_dis = mode_access == self.cursor_.Browse

        # if isinstance(v , QString): #Para quitar
        # v = str(v)

        # LOGGER.info(
        #    "FLFieldDB:: refresh field_name:%r fieldName:%r v:%s"
        #    % (field_name, self._field_name, repr(value)[:64])
        # )

        if self._keep_disabled or self.cursor_.fieldDisabled(self._field_name):
            field_dis = True

        elif mode_access == self.cursor_.Edit:
            if (
                field.isPrimaryKey()
                or table_metadata.fieldListOfCompoundKey(self._field_name)
                or not field.editable()
            ):
                field_dis = True

        self.setEnabled(not field_dis)

        if type_ == "double":
            editor_dbl = cast(fllineedit.FLLineEdit, self.editor_)
            try:
                cast(
                    QtCore.pyqtSignal, editor_dbl.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.debug("Error al desconectar señal textChanged", exc_info=True)
            text_ = None

            if nulo:
                default_value = field.defaultValue()

                if field.allowNull() or default_value is not None:
                    editor_dbl.setText(default_value or "")

            else:
                if not value:
                    value = 0.0
                text_ = str(round(float(value), part_decimal))
                pos_dot = text_.find(".")

                if pos_dot is not None and pos_dot > -1:
                    while len(text_[pos_dot + 1 :]) < part_decimal:
                        text_ = "%s0" % text_
                editor_dbl.setText(text_)

            cast(
                QtCore.pyqtSignal, editor_dbl.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

            # if v == None and not nulo:
            #    self.editor_.setText("0.00")

        elif type_ == "string":

            do_home = False
            if not hol:
                editor_str = cast(fllineedit.FLLineEdit, self.editor_)
                try:
                    cast(
                        QtCore.pyqtSignal, editor_str.textChanged
                    ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal textChanged")
            else:
                editor_cb = cast(qcombobox.QComboBox, self.editor_)

            if value is not None:
                if hol:
                    if value.find("QT_TRANSLATE") != -1:
                        value = utils_base.AQTT(value)
                    idx = field.getIndexOptionsList(value)
                    if idx is not None:
                        editor_cb.setCurrentIndex(idx)
                else:
                    editor_str.setText(value)
            else:
                if hol:
                    editor_cb.setCurrentIndex(0)
                else:
                    def_val = field.defaultValue() or ""
                    editor_str.setText(def_val if not nulo else "")

            if not hol:
                if do_home:
                    editor_str.home(False)

                cast(
                    QtCore.pyqtSignal, editor_str.textChanged
                ).connect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )

        elif type_ in ("timestamp", "json"):

            do_home = False
            editor_str = cast(fllineedit.FLLineEdit, self.editor_)
            try:
                cast(
                    QtCore.pyqtSignal, editor_str.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal textChanged")

            if value is not None:
                editor_str.setText(value)
            else:
                def_val = field.defaultValue() or ""
                editor_str.setText(def_val if not nulo else "")

            if do_home:
                editor_str.home(False)

            cast(
                QtCore.pyqtSignal, editor_str.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ in ("int", "uint"):
            editor_int = cast(fllineedit.FLLineEdit, self.editor_)
            try:
                cast(
                    QtCore.pyqtSignal, editor_int.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal textChanged")

            if nulo and not value:
                default_value = field.defaultValue()
                if field.allowNull():
                    if default_value is None:
                        editor_int.setText("")
                    else:
                        editor_int.setText(default_value)
                else:
                    if default_value is not None:
                        editor_int.setText(default_value)

            else:
                if not value:
                    editor_int.setText(str(0))
                else:
                    editor_int.setText(value)

            cast(
                QtCore.pyqtSignal, editor_int.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "serial":
            editor_serial = cast(fllineedit.FLLineEdit, self.editor_)
            try:
                cast(
                    QtCore.pyqtSignal, editor_serial.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal textChanged")
            editor_serial.setText(str(0))

            cast(
                QtCore.pyqtSignal, editor_serial.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "pixmap":
            if not hasattr(self, "_editor_img"):

                self._editor_img = flpixmapview.FLPixmapView(self)
                self._editor_img.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self._editor_img.setSizePolicy(self.sizePolicy())
                self._editor_img.setMinimumSize(self.minimumSize())
                self._editor_img.setMaximumSize(self.maximumSize())
                # self._editor_img.setMinimumSize(self.minimumSize())
                self._editor_img.setAutoScaled(True)
                # self._widgets_layout.removeWidget(self._push_button_db)
                if self._widgets_layout is None:
                    raise Exception("_widgets_layout is empty!")
                self._widgets_layout.addWidget(self._editor_img)
                self._push_button_db.hide()

                if field.visible():
                    self._editor_img.show()
                else:
                    return
                # else:
            # if mode_access == pnsqlcursor.PNSqlCursor.Browse:
            if field.visible():
                # cs = QString()
                if not value:
                    self._editor_img.clear()
                    return
                    # cs = v.toString()
                # if cs.isEmpty():
                #    self._editor_img.clear()
                #    return
                if isinstance(value, str):
                    if value.find("static char") > -1:

                        value = xpm.cache_xpm(value)

                pix = QtGui.QPixmap(value)
                # if not QtGui.QPixmapCache.find(cs.left(100), pix):
                # pix.loadFromData()
                # QtGui.QPixmapCache.insert(cs.left(100), pix)

                if pix:
                    self._editor_img.setPixmap(pix)
                else:
                    self._editor_img.clear()

            # if mode_access == pnsqlcursor.PNSqlCursor.Browse:
            # self._push_button_db.setVisible(False)

        elif type_ == "date":
            editor_date = cast(fldateedit.FLDateEdit, self.editor_)
            if self.cursor_.modeAccess() == self.cursor_.Insert and nulo and not field.allowNull():
                default_value = field.defaultValue()
                if default_value is not None:
                    default_value = QtCore.QDate.fromString(str(default_value))
                else:
                    default_value = QtCore.QDate.currentDate()

                editor_date.setDate(default_value)
                self.updateValue(default_value)

            else:
                try:
                    cast(
                        QtCore.pyqtSignal, editor_date.dateChanged
                    ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal textChanged")

                if value:
                    util = flutil.FLUtil()
                    value = util.dateDMAtoAMD(value)
                    editor_date.setDate(value)
                else:
                    editor_date.setDate()

                cast(
                    QtCore.pyqtSignal, editor_date.dateChanged
                ).connect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )

        elif type_ == "time":
            editor_time = cast(fltimeedit.FLTimeEdit, self.editor_)
            if self.cursor_.modeAccess() == self.cursor_.Insert and nulo and not field.allowNull():
                default_value = field.defaultValue()
                if default_value is not None:
                    default_value = QtCore.QTime.fromString(str(default_value))
                else:
                    default_value = QtCore.QTime.currentTime()

                editor_time.setTime(default_value)
                self.updateValue(default_value)

            else:
                try:
                    cast(
                        QtCore.pyqtSignal, editor_time.timeChanged
                    ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal timeChanged")

                if value is not None:
                    editor_time.setTime(value)

                cast(
                    QtCore.pyqtSignal, editor_time.timeChanged
                ).connect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )

        elif type_ == "stringlist":
            editor_sl = cast(qtextedit.QTextEdit, self.editor_)
            try:
                cast(
                    QtCore.pyqtSignal, editor_sl.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal timeChanged")
            if value is not None:
                editor_sl.setText(value)
            else:
                def_val = field.defaultValue() or ""
                editor_sl.setText(str(def_val))
            cast(
                QtCore.pyqtSignal, editor_sl.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "bool":
            editor_bool = cast(flcheckbox.FLCheckBox, self.editor_)
            try:
                cast(
                    QtCore.pyqtSignal, editor_bool.toggled
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal toggled")

            if value is not None:

                editor_bool.setChecked(value)
            else:
                def_val = field.defaultValue()
                if def_val is not None:
                    editor_bool.setChecked(def_val)

            cast(
                QtCore.pyqtSignal, editor_bool.toggled
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        if not field.visible():
            if self.editor_:
                self.editor_.hide()
            elif self._editor_img:
                self._editor_img.hide()
            self.setEnabled(False)

    """
    Refresco rápido
    """

    @decorators.pyqt_slot("QString")
    def refreshQuick(self, field_name: Optional[str] = None) -> None:
        """Refresh value quick."""
        if not field_name or not field_name == self._field_name or not self.cursor_:
            return

        table_metadata = self.cursor_.metadata()
        field = table_metadata.field(self._field_name)

        if field is None:
            return

        if field.outTransaction():
            return

        type_ = field.type()

        if not type_ == "pixmap" and not self.editor_:
            return
        value = self.cursor_.valueBuffer(self._field_name, True)
        nulo = self.cursor_.bufferIsNull(self._field_name)

        if self._part_decimal < 0:
            self._part_decimal = field.partDecimal()

        if type_ == "double":
            editor_le = cast(fllineedit.FLLineEdit, self.editor_)
            # part_decimal = self._part_decimal if self._part_decimal > -1 else field.partDecimal()

            e_text = editor_le.text() if editor_le.text() else 0.0
            if float(str(e_text)) == float(value):
                return
            try:
                cast(
                    QtCore.pyqtSignal, editor_le.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal textChanged")

            if not nulo:
                value = round(value, self._part_decimal)

            editor_le.setText(value, False)

            cast(
                QtCore.pyqtSignal, editor_le.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "string":
            do_home = False
            has_options_list = field.hasOptionsList()

            if has_options_list:
                combo = cast(qcombobox.QComboBox, self.editor_)
                if str(value) == combo.currentText:
                    return
            else:
                editor = cast(fllineedit.FLLineEdit, self.editor_)
                if str(value) == editor.text():
                    return

                if not editor.text():
                    do_home = True

                cast(
                    QtCore.pyqtSignal, editor.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )

            if value:
                if has_options_list:
                    combo.setCurrentText(value)

                else:
                    editor.setText(value, False)

            else:
                if has_options_list:
                    combo.setCurrentIndex(0)

                else:
                    editor.setText("", False)

            if not has_options_list:
                if do_home:
                    editor.home(False)

                cast(
                    QtCore.pyqtSignal, editor.textChanged
                ).connect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )

        elif type_ in ("uint", "int", "serial", "timestamp", "json"):
            editor_le = cast(fllineedit.FLLineEdit, self.editor_)
            if value == editor_le.text():
                return
            try:
                cast(
                    QtCore.pyqtSignal, editor_le.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal textChanged")

            if not nulo:
                editor_le.setText(value)

            cast(
                QtCore.pyqtSignal, editor_le.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "pixmap":
            if not self._editor_img:
                self._editor_img = flpixmapview.FLPixmapView(self)
                self._editor_img.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self._editor_img.setSizePolicy(self.sizePolicy())
                self._editor_img.setMaximumSize(self.maximumSize())
                # self._editor_img.setMinimumSize(self.minimumSize())
                self._editor_img.setAutoScaled(True)
                if self._widgets_layout is None:
                    raise Exception("_widgets_layout is empty!")
                self._widgets_layout.addWidget(self._editor_img)
                if field.visible():
                    self._editor_img.show()

            if not nulo:
                if not value:
                    self._editor_img.clear()
                    return

            if isinstance(value, str):
                if value.find("static char") > -1:
                    value = xpm.cache_xpm(value)

            pix = QtGui.QPixmap(value)
            # pix.loadFromData(value)

            if pix.isNull():
                self._editor_img.clear()
            else:
                self._editor_img.setPixmap(pix)

        elif type_ == "date":
            editor_d = cast(fldateedit.FLDateEdit, self.editor_)
            if value == editor_d.date:
                return

            try:
                cast(
                    QtCore.pyqtSignal, editor_d.dateChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal dateChanged")
            editor_d.setDate(value)
            cast(
                QtCore.pyqtSignal, editor_d.dateChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "time":
            editor_t = cast(fltimeedit.FLTimeEdit, self.editor_)
            if value == str(editor_t.time()):
                return

            try:
                cast(
                    QtCore.pyqtSignal, editor_t.timeChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal")

            if value is None:
                value = "00:00:00"

            editor_t.setTime(value)
            cast(
                QtCore.pyqtSignal, editor_t.timeChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "stringlist":
            editor_sl = cast(qtextedit.QTextEdit, self.editor_)
            if value == str(editor_sl.toPlainText()):
                return

            try:
                cast(
                    QtCore.pyqtSignal, editor_sl.textChanged
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal")

            editor_sl.setText(value)
            cast(
                QtCore.pyqtSignal, editor_sl.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "bool":
            editor_b = cast(flcheckbox.FLCheckBox, self.editor_)
            if value == editor_b.isChecked():
                return

            try:
                cast(
                    QtCore.pyqtSignal, editor_b.toggled
                ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.updateValue
                )
            except Exception:
                LOGGER.exception("Error al desconectar señal")

            editor_b.setChecked(value)
            cast(
                QtCore.pyqtSignal, editor_b.toggled
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

    def initCursor(self) -> None:
        """
        Start the cursor according to this field either from the source table or from a related table.
        """
        if application.PROJECT.conn_manager is None:
            raise Exception("Project is not connected yet")

        self._top_widget.formClosed.connect(self.closeCursor)

        cursor_backup = None
        if self._table_name and not self._foreign_field and not self._field_relation:
            cursor_backup = self.cursor_
            if not self._top_widget:
                return

            self.cursor_ = pnsqlcursor.PNSqlCursor(
                self._table_name,
                True,
                application.PROJECT.conn_manager.useConn("default").connectionName(),
                None,
                None,
                self,
            )

            self.cursor_.setModeAccess(pnsqlcursor.PNSqlCursor.Browse)
            if self._showed:
                try:
                    self.cursor_.cursorUpdated.disconnect(self.refresh)
                except Exception:
                    LOGGER.exception("Error al desconectar señal")
            self.cursor_.cursorUpdated.connect(self.refresh)
            return
        else:
            if cursor_backup:
                try:
                    if self.cursor_ is not None:
                        self.cursor_.cursorUpdated.disconnect(self.refresh)
                except Exception:
                    LOGGER.exception("Error al desconectar señal")
                self.cursor_ = cursor_backup

        if not self.cursor_:
            return

        if not self._table_name or not self._foreign_field or not self._field_relation:
            if self._foreign_field and self._field_relation:
                if self._showed:
                    try:
                        self.cursor_.bufferChanged.disconnect(self.refresh)
                    except Exception:
                        LOGGER.exception("Error al desconectar señal")

                self.cursor_.bufferChanged.connect(self.refresh)

            if self._showed:
                try:
                    self.cursor_.newBuffer.disconnect(self.refresh)
                except Exception:
                    LOGGER.exception("Error al desconectar señal")

                try:
                    self.cursor_.bufferChanged.disconnect(self.refreshQuick)
                except Exception:
                    LOGGER.exception("Error al desconectar señal")

            self.cursor_.newBuffer.connect(self.refresh)
            self.cursor_.bufferChanged.connect(self.refreshQuick)
            return

        table_metadata = self.cursor_.db().connManager().manager().metadata(self._table_name)
        if not table_metadata:
            return

        try:
            self.cursor_.newBuffer.disconnect(self.refresh)
        except TypeError:
            pass

        try:
            self.cursor_.bufferChanged.disconnect(self.refreshQuick)
        except TypeError:
            pass

        self._cursor_aux = self.cursor()
        if not self.cursor().metadata():
            return

        cursor_name = self.cursor().metadata().name()

        relation_metadata = table_metadata.relation(
            self._field_relation, self._foreign_field, cursor_name
        )
        if not relation_metadata:
            check_integrity = False
            rel_m1 = self.cursor_.metadata().relation(
                self._foreign_field, self._field_relation, self._table_name
            )
            if rel_m1:
                if rel_m1.cardinality() == pnrelationmetadata.PNRelationMetaData.RELATION_1M:
                    check_integrity = True
            field_metadata = table_metadata.field(self._field_relation)

            if field_metadata is not None:
                relation_metadata = pnrelationmetadata.PNRelationMetaData(
                    cursor_name,
                    self._foreign_field,
                    pnrelationmetadata.PNRelationMetaData.RELATION_1M,
                    False,
                    False,
                    check_integrity,
                )

                field_metadata.addRelationMD(relation_metadata)
                LOGGER.trace(
                    "FLFieldDB : La relación entre la tabla del formulario ( %s ) y la tabla ( %s ) de este campo ( %s ) no existe, "
                    "pero sin embargo se han indicado los campos de relación( %s, %s)",
                    cursor_name,
                    self._table_name,
                    self._field_name,
                    self._field_relation,
                    self._foreign_field,
                )
                LOGGER.trace(
                    "FLFieldDB : Creando automáticamente %s.%s --1M--> %s.%s",
                    self._table_name,
                    self._field_relation,
                    cursor_name,
                    self._foreign_field,
                )
            else:
                LOGGER.trace(
                    "FLFieldDB : El campo ( %s ) indicado en la propiedad fieldRelation no se encuentra en la tabla ( %s )",
                    self._field_relation,
                    self._table_name,
                )

        if self._table_name:

            self.cursor_ = pnsqlcursor.PNSqlCursor(
                self._table_name,
                False,
                self.cursor_.connectionName(),
                self._cursor_aux,
                relation_metadata,
                self,
            )

            self.cursor_.select()
            self.cursor_.first()

        if not self.cursor_:
            self.cursor_ = self._cursor_aux
            if self._showed:
                try:
                    self.cursor_.newBuffer.disconnect(self.refresh)
                except Exception:
                    LOGGER.exception("Error al desconectar señal")

                try:
                    self.cursor_.bufferChanged.disconnect(self.refreshQuick)
                except Exception:
                    LOGGER.exception("Error al desconectar señal")

            self.cursor_.newBuffer.connect(self.refresh)
            self.cursor_.bufferChanged.connect(self.refreshQuick)
            self._cursor_aux = None
            return
        else:
            if self._showed:
                try:
                    self.cursor_.newBuffer.disconnect(self.setNoShowed)
                except Exception:
                    LOGGER.exception("Error al desconectar señal")
            self.cursor_.newBuffer.connect(self.setNoShowed)

        self.cursor_.setModeAccess(pnsqlcursor.PNSqlCursor.Browse)
        if self._showed:
            try:
                self.cursor_.newBuffer.disconnect(self.refresh)
            except Exception:
                LOGGER.exception("Error al desconectar señal")

            try:
                self.cursor_.bufferChanged.disconnect(self.refreshQuick)
            except Exception:
                LOGGER.exception("Error al desconectar señal")

        self.cursor_.newBuffer.connect(self.refresh)
        self.cursor_.bufferChanged.connect(self.refreshQuick)

        # self.cursor_.append(self.cursor_.db().db().recordInfo(self._table_name).find(self._field_name)) #FIXME
        # self.cursor_.append(self.cursor_.db().db().recordInfo(self._table_name).find(self._field_relation))
        # #FIXME

    def closeCursor(self) -> None:
        """Close cursor connections."""
        if self.cursor_:
            self.cursor_.newBuffer.disconnect(self.refresh)
            self.cursor_.bufferChanged.disconnect(self.refreshQuick)
            try:
                self.cursor_.cursorUpdated.disconnect(self.refresh)
            except Exception:
                pass
            cursor_rel = self.cursor_.cursorRelation()
            if cursor_rel:
                try:
                    cursor_rel.newBuffer.disconnect(self.cursor_.refresh)
                except Exception:
                    pass

                try:
                    cursor_rel.bufferChanged.disconnect(self.cursor_.refresh)
                except Exception:
                    pass

        self._top_widget.formClosed.disconnect(self.closeCursor)
        self._cursor_aux = None
        self.cursor_ = None
        # TODO: buscar copias de cursor_ y cursor_aux "VIVAS"

    def initEditor(self) -> None:
        """
        Create and start the appropriate editor.

        To edit the data type content in the field (eg: if the field contains a date it creates and start a QDataEdit)
        """
        if not self.cursor_:
            return

        # if self.editor_:
        #    del self.editor_
        #    self.editor_ = None

        # if self._editor_img:
        #    del self._editor_img
        #    self._editor_img = None

        table_metadata = self.cursor_.metadata()
        if not table_metadata:
            return

        field = table_metadata.field(self._field_name)
        if field is None:
            return

        type_ = field.type()
        len_ = field.length()
        part_integer = field.partInteger()
        part_decimal = None
        if type_ == "double":
            if self._part_decimal:
                part_decimal = self._part_decimal
            else:
                part_decimal = field.partDecimal()
                self._part_decimal = field.partDecimal()

        regex_validator = field.regExpValidator()
        hol = field.hasOptionsList()

        foreign_table = None
        field_relation = field.relationM1()
        if field_relation is not None:
            if not field_relation.foreignTable() == table_metadata.name():
                foreign_table = field_relation.foreignTable()

        has_push_button_db = False
        self._field_alias = field.alias()

        if self._field_alias is None:
            raise Exception(
                "alias from %s.%s is not defined!" % (field.metadata().name(), field.name())
            )

        if self._text_label_db:
            self._text_label_db.setFont(self.font())
            if type_ not in ["pixmap", "bool"]:
                if not field.allowNull() and field.editable():
                    self._text_label_db.setText("%s*" % self._field_alias)
                else:
                    self._text_label_db.setText(self._field_alias)
            else:
                self._text_label_db.hide()

        if foreign_table:
            has_push_button_db = True
            tmd = self.cursor_.db().connManager().manager().metadata(foreign_table)
            if not tmd and self._push_button_db:
                self._push_button_db.setDisabled(True)
                field.setEditable(False)

            # if tmd and not tmd.inCache():
            #    del tmd

        self._init_max_size = self.maximumSize()
        self._init_min_size = self.minimumSize()

        if type_ in ("uint", "int", "double", "string", "timestamp", "json"):
            self.initEditorControlForNumber(
                has_option_list=hol,
                field=field,
                type_=type_,
                part_decimal=part_decimal,
                part_integer=part_integer,
                len_=len_,
                regexp_=regex_validator,
                has_push_button_db=has_push_button_db,
            )
        elif type_ == "serial":
            self.editor_ = fllineedit.FLLineEdit(self, "editor")
            self.editor_.setFont(self.font())
            self.editor_.setMaxValue(pow(10, field.partInteger()) - 1)
            size_policy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy(7), QtWidgets.QSizePolicy.Policy.Fixed
            )
            size_policy.setHeightForWidth(True)
            self.editor_.setSizePolicy(size_policy)
            if self._widgets_layout:
                self._widgets_layout.addWidget(self.editor_)
            self.editor_.installEventFilter(self)
            self.editor_.setDisabled(True)
            self.editor_.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            if self._push_button_db:
                self._push_button_db.hide()

            if self._showed:
                try:
                    self.editor_.textChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal")
            self.editor_.textChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        elif type_ == "pixmap":
            # if not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
            if not self.tableName():
                if not hasattr(self, "_editor_img") and self._widgets_layout:
                    self._widgets_layout.setDirection(QtWidgets.QBoxLayout.Direction.TopToBottom)
                    self._editor_img = flpixmapview.FLPixmapView(self)
                    self._editor_img.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                    self._editor_img.setSizePolicy(self.sizePolicy())
                    self._editor_img.setMaximumSize(self.maximumSize())
                    self._editor_img.setMinimumSize(self.minimumSize())
                    if self._icon_size:
                        self.setMinimumHeight(self._icon_size.height() + self.minimumHeight() + 1)
                        self.setMinimumWidth(self._icon_size.width() * 4)
                    self._editor_img.setAutoScaled(True)
                    self._widgets_layout.removeWidget(self._push_button_db)
                    self._widgets_layout.addWidget(self._editor_img)

                if self._text_label_db:
                    self._text_label_db.hide()

                size_policy = QtWidgets.QSizePolicy(
                    QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
                )
                # size_policy.setHeightForWidth(True)

                if not self._pbaux3:
                    space_item = QtWidgets.QSpacerItem(
                        20,
                        20,
                        QtWidgets.QSizePolicy.Policy.Expanding,
                        QtWidgets.QSizePolicy.Policy.Minimum,
                    )
                    self._buttons_layout.addItem(space_item)
                    self._pbaux3 = qpushbutton.QPushButton(self)
                    if self._pbaux3:
                        self._pbaux3.setSizePolicy(size_policy)
                        self._pbaux3.setMinimumSize(self._icon_size)
                        self._pbaux3.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                        self._pbaux3.setIcon(
                            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-open.png"))
                        )
                        self._pbaux3.setText("")
                        self._pbaux3.setToolTip("Abrir fichero de imagen")
                        self._pbaux3.setWhatsThis("Abrir fichero de imagen")
                        self._buttons_layout.addWidget(self._pbaux3)
                        # if self._showed:
                        #    try:
                        #        self._pbaux3.clicked.disconnect(self.searchPixmap)
                        #    except Exception:
                        #        LOGGER.exception("Error al desconectar señal")
                        self._pbaux3.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                            self.searchPixmap
                        )

                        self._pbaux3.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
                        self._pbaux3.installEventFilter(self)

                if not self._pbaux4:
                    self._pbaux4 = qpushbutton.QPushButton(self)
                    if self._pbaux4:
                        self._pbaux4.setSizePolicy(size_policy)
                        self._pbaux4.setMinimumSize(self._icon_size)
                        self._pbaux4.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                        self._pbaux4.setIcon(
                            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-paste.png"))
                        )
                        self._pbaux4.setText("")
                        self._pbaux4.setToolTip("Pegar imagen desde el portapapeles")
                        self._pbaux4.setWhatsThis("Pegar imagen desde el portapapeles")
                        self._buttons_layout.addWidget(self._pbaux4)
                        # if self._showed:
                        #    try:
                        #        self._pbaux4.clicked.disconnect(self.setPixmapFromClipboard)
                        #    except Exception:
                        #        LOGGER.exception("Error al desconectar señal")
                        self._pbaux4.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                            self.setPixmapFromClipboard
                        )

                if not self._pbaux:
                    self._pbaux = qpushbutton.QPushButton(self)
                    if self._pbaux:
                        self._pbaux.setSizePolicy(size_policy)
                        self._pbaux.setMinimumSize(self._icon_size)
                        self._pbaux.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                        self._pbaux.setIcon(
                            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-clear.png"))
                        )
                        self._pbaux.setText("")
                        self._pbaux.setToolTip("Borrar imagen")
                        self._pbaux.setWhatsThis("Borrar imagen")
                        self._buttons_layout.addWidget(self._pbaux)
                        # if self._showed:
                        #    try:
                        #        self._pbaux.clicked.disconnect(self.clearPixmap)
                        #    except Exception:
                        #        LOGGER.exception("Error al desconectar señal")
                        self._pbaux.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                            self.clearPixmap
                        )

                if not self._pbaux2:
                    self._pbaux2 = qpushbutton.QPushButton(self)
                    if self._pbaux2:
                        savepixmap_ = QtWidgets.QMenu(self._pbaux2)
                        savepixmap_.addAction("JPG")
                        savepixmap_.addAction("XPM")
                        savepixmap_.addAction("PNG")
                        savepixmap_.addAction("BMP")

                        self._pbaux2.setMenu(savepixmap_)
                        self._pbaux2.setSizePolicy(size_policy)
                        self._pbaux2.setMinimumSize(self._icon_size)
                        self._pbaux2.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                        self._pbaux2.setIcon(
                            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-save.png"))
                        )
                        self._pbaux2.setText("")
                        self._pbaux2.setToolTip("Guardar imagen como...")
                        self._pbaux2.setWhatsThis("Guardar imagen como...")
                        self._buttons_layout.addWidget(self._pbaux2)
                        # if self._showed:
                        #    try:
                        #        savepixmap_.triggered.disconnect(self.savePixmap)
                        #    except Exception:
                        #        LOGGER.exception("Error al desconectar señal")
                        triggered = cast(QtCore.pyqtSignal, savepixmap_.triggered)
                        triggered.connect(  # type: ignore [attr-defined] # noqa: F821
                            self.savePixmap
                        )

                    if self._push_button_db:
                        if has_push_button_db:
                            self._push_button_db.installEventFilter(self)
                        else:
                            self._push_button_db.setDisabled(True)

        elif type_ == "date":
            self.editor_ = fldateedit.FLDateEdit(self, "editor")
            self.editor_.setFont(self.font())
            size_policy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy(7), QtWidgets.QSizePolicy.Policy.Fixed
            )
            size_policy.setHeightForWidth(True)
            self.editor_.setSizePolicy(size_policy)
            if self._widgets_layout:
                self._widgets_layout.insertWidget(1, self.editor_)

            # self.editor_.setOrder(QtGui.QDateEdit.DMY)
            # self.editor_.setAutoAdvance(True)
            # self.editor_.setSeparator("-")
            self.editor_.installEventFilter(self)
            if self._push_button_db:
                self._push_button_db.hide()

            if not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
                # if not self._pbaux:
                #    #self._pbaux = qpushbutton.QPushButton(self)
                #    # self._pbaux.setFlat(True)
                #    #size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7) ,QtGui.QSizePolicy.Policy(0))
                #    # size_policy.setHeightForWidth(True)
                #    # self._pbaux.setSizePolicy(sizePolicy)
                #    #self._pbaux.setMinimumSize(25, 25)
                #    #self._pbaux.setMaximumSize(25, 25)
                #    # self._pbaux.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                #    # self._pbaux.setIcon(QtGui.QIcon(utils_base.filedir("./core/images/icons","date.png")))
                #    # self._pbaux.setText("")
                #    #self._pbaux.setToolTip("Seleccionar fecha (F2)")
                #    #self._pbaux.setWhatsThis("Seleccionar fecha (F2)")
                #    # self._buttons_layout.addWidget(self._pbaux) FIXME
                #    # self._widgets_layout.addWidget(self._pbaux)
                #    # if self._showed:
                #        # self._pbaux.clicked.disconnect(self.toggleDatePicker)
                #        # self.KeyF2Pressed_.disconnect(self._pbaux.animateClick)
                #    # self._pbaux.clicked.connect(self.toggleDatePicker)
                #    # self.keyF2Pressed_.connect(self._pbaux.animateClick) #FIXME
                self.editor_.setCalendarPopup(True)

            if self._showed:
                try:
                    cast(
                        QtCore.pyqtSignal, self.editor_.dateChanged
                    ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal")

            cast(
                QtCore.pyqtSignal, self.editor_.dateChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )
            if (
                self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Insert
                and not field.allowNull()
            ):
                default_value = field.defaultValue()
                if default_value is None:
                    self.editor_.setDate(QtCore.QDate.currentDate().toString("dd-MM-yyyy"))
                else:
                    self.editor_.setDate(default_value.toDate())

        elif type_ == "time":
            self.editor_ = fltimeedit.FLTimeEdit(self)
            self.editor_.setFont(self.font())
            # self.editor_.setAutoAdvance(True)
            size_policy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy(7), QtWidgets.QSizePolicy.Policy.Fixed
            )
            size_policy.setHeightForWidth(True)
            self.editor_.setSizePolicy(size_policy)
            if self._widgets_layout:
                self._widgets_layout.addWidget(self.editor_)
            self.editor_.installEventFilter(self)
            if self._push_button_db:
                self._push_button_db.hide()
            if self._showed:
                try:
                    cast(
                        QtCore.pyqtSignal, self.editor_.timeChanged
                    ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal")

            cast(
                QtCore.pyqtSignal, self.editor_.timeChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )
            if (
                self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Insert
                and not field.allowNull()
            ):
                default_value = field.defaultValue()
                # if not default_value.isValid() or default_value.isNull():
                if default_value is None:
                    self.editor_.setTime(QtCore.QTime.currentTime())
                else:
                    self.editor_.setTime(default_value.toTime())

        elif type_ == "stringlist":

            self.editor_ = qtextedit.QTextEdit(self)
            self.editor_.setFont(self.font())
            self.editor_.setTabChangesFocus(True)
            self.setMinimumHeight(100)
            # self.editor_.setMinimumHeight(100)
            # self.editor_.setMaximumHeight(120)
            size_policy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            )
            size_policy.setHeightForWidth(True)
            self.editor_.setSizePolicy(size_policy)
            # ted.setTexFormat(self._text_format)
            # if isinstance(self._text_format, QtCore.Qt.RichText) and not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
            # self._widgets_layout.setDirection(QtGui.QBoxLayout.Down)
            # self._widgets_layout.remove(self._text_label_db)
            # textEditTab_ = AQTextEditBar(self, "extEditTab_", self._text_label_db) #FIXME
            # textEditTab_.doConnections(ted)
            # self._widgets_layout.addWidget(textEditTab_)
            # self.setMinimumHeight(120)
            if self._widgets_layout:
                self._widgets_layout.addWidget(self.editor_)
            # verticalSpacer = QtWidgets.QSpacerItem(
            #    20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            # )
            # self._horizontal_layout.addItem(verticalSpacer)
            self.editor_.installEventFilter(self)

            if self._showed:
                try:
                    cast(
                        QtCore.pyqtSignal, self.editor_.textChanged
                    ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal")

            cast(
                QtCore.pyqtSignal, self.editor_.textChanged
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

            self.keyF4Pressed.connect(self.toggleAutoCompletion)
            if self._auto_com_mode == "OnDemandF4":
                self.editor_.setToolTip("Para completado automático pulsar F4")
                self.editor_.setWhatsThis("Para completado automático pulsar F4")
            elif self._auto_com_mode == "AlwaysAuto":
                self.editor_.setToolTip("Completado automático permanente activado")
                self.editor_.setWhatsThis("Completado automático permanente activado")
            else:
                self.editor_.setToolTip("Completado automático desactivado")
                self.editor_.setWhatsThis("Completado automático desactivado")

        elif type_ == "bool":

            alias = table_metadata.fieldNameToAlias(self._field_name)
            if not alias:
                raise Exception("alias is empty!")

            self.editor_ = flcheckbox.FLCheckBox(self)
            # self.editor_.setName("editor")
            self.editor_.setText(alias)
            self.editor_.setFont(self.font())
            self.editor_.installEventFilter(self)

            self.editor_.setMinimumWidth((len(alias) * self.fontMetrics().maxWidth()) + 2)
            size_policy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy(7), QtWidgets.QSizePolicy.Policy.Fixed
            )
            size_policy.setHeightForWidth(True)
            self.editor_.setSizePolicy(size_policy)
            if self._widgets_layout:
                self._widgets_layout.addWidget(self.editor_)

            if self._showed:
                try:
                    self.editor_.toggled.disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal")
            self.editor_.toggled.connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        if hasattr(self, "editor_"):
            self.editor_.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            self.setFocusProxy(self.editor_)

            if has_push_button_db:
                if self._push_button_db:
                    self.setTabOrder(self._push_button_db, self.editor_)
                    self._push_button_db.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self.editor_.setToolTip("Para buscar un valor en la tabla relacionada pulsar F2")
                self.editor_.setWhatsThis("Para buscar un valor en la tabla relacionada pulsar F2")

        elif hasattr(self, "_editor_img"):
            self._editor_img.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            if has_push_button_db:
                if self._push_button_db:
                    self._push_button_db.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        if not has_push_button_db:
            if self._push_button_db:
                self._push_button_db.hide()

        if self._init_max_size.width() < 80:
            self.setShowEditor(False)
        else:
            self.setShowEditor(self._show_editor)

        if self._refresh_later is not None:
            self.refresh(self._refresh_later)
            self._refresh_later = None

    def initEditorControlForNumber(
        self,
        has_option_list: bool,
        field,
        type_,
        part_decimal,
        part_integer,
        len_,
        regexp_,
        has_push_button_db,
    ) -> None:
        """Inicialize control for number."""

        if self.cursor_ is None:
            raise Exception("cursor_ is empty!.")

        if has_option_list:
            self.editor_ = qcombobox.QComboBox()
            # style_ = self.editor_.styleSheet()
            self.editor_.setParent(self)

            self.editor_.setObjectName("editor")
            # self.editor_.setEditable(False)
            # self.editor_.setAutoCompletion(True)
            self.editor_.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed
            )
            self.editor_.setMinimumSize(self._icon_size)
            self.editor_.setFont(self.font())
            # if not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
            # if not field.allowNull():
            # self.editor_.palette().setColor(self.editor_.backgroundRole(), self.notNullColor())
            # self.editor_.setStyleSheet('background-color:' + self.notNullColor().name())
            # if not field.allowNull() and field.editable():
            #    self.editor_.setStyleSheet(
            #        "background-color:%s; color:%s"
            #        % (self.notNullColor(), QtGui.QColor(QtCore.Qt.black).name())
            #    )
            # else:
            #    self.editor_.setStyleSheet(style_)

            old_translated = []
            old_not_translated = field.optionsList()
            for item in old_not_translated:
                old_translated.append(item)
            self.editor_.addItems(old_translated)
            self.editor_.installEventFilter(self)
            if self._showed:
                try:
                    cast(
                        QtCore.pyqtSignal, self.editor_.activated
                    ).disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal")
            cast(
                QtCore.pyqtSignal, self.editor_.activated
            ).connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )

        else:

            self.editor_ = fllineedit.FLLineEdit(self, "editor")
            self.editor_.setFont(self.font())
            if self._icon_size and self.font().pointSize() < 10:
                self.editor_.setMinimumSize(self._icon_size)
                self.editor_.setMaximumHeight(self._icon_size.height())

            self.editor_._tipo = type_
            self.editor_._part_decimal = part_decimal
            if not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
                if not field.allowNull() and field.editable() and type_ not in ("time", "date"):
                    # self.editor_.palette().setColor(self.editor_.backgroundRole(), self.notNullColor())
                    self.editor_.setStyleSheet(
                        "background-color:%s; color:%s"
                        % (self.notNullColor(), QtGui.QColor(QtCore.Qt.GlobalColor.black).name())
                    )
                self.editor_.installEventFilter(self)

            if type_ == "double":

                self.editor_.setValidator(
                    fldoublevalidator.FLDoubleValidator(
                        ((pow(10, part_integer) - 1) * -1),
                        pow(10, part_integer) - 1,
                        self.editor_._part_decimal,
                        self.editor_,
                    )
                )
                self.editor_.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            else:
                if type_ == "uint":

                    self.editor_.setValidator(
                        fluintvalidator.FLUIntValidator(0, pow(10, part_integer), self.editor_)
                    )
                    pass
                elif type_ == "int":

                    self.editor_.setValidator(
                        flintvalidator.FLIntValidator(
                            ((pow(10, part_integer) - 1) * -1),
                            pow(10, part_integer) - 1,
                            self.editor_,
                        )
                    )
                    self.editor_.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
                else:
                    self.editor_.setMaxValue(len_)
                    if regexp_:
                        self.editor_.setValidator(
                            QtGui.QRegularExpressionValidator(
                                QtCore.QRegularExpression(regexp_), self.editor_
                            )
                        )

                    self.editor_.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

                    self.keyF4Pressed.connect(self.toggleAutoCompletion)
                    if self._auto_com_mode == "OnDemandF4":
                        self.editor_.setToolTip("Para completado automático pulsar F4")
                        self.editor_.setWhatsThis("Para completado automático pulsar F4")
                    elif self._auto_com_mode == "AlwaysAuto":
                        self.editor_.setToolTip("Completado automático permanente activado")
                        self.editor_.setWhatsThis("Completado automático permanente activado")
                    else:
                        self.editor_.setToolTip("Completado automático desactivado")
                        self.editor_.setWhatsThis("Completado automático desactivado")

            self.editor_.installEventFilter(self)

            if self._showed:
                try:
                    self.editor_.lostFocus.disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.emitLostFocus
                    )
                    self.editor_.textChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.updateValue
                    )
                    self.editor_.textChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.emitTextChanged
                    )
                except Exception:
                    LOGGER.exception("Error al desconectar señal")

            self.editor_.lostFocus.connect(self.emitLostFocus)
            self.editor_.textChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.updateValue
            )
            self.editor_.textChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.emitTextChanged
            )

            if has_push_button_db and self._push_button_db:
                if self._showed:
                    try:
                        self.keyF2Pressed.disconnect(self._push_button_db.animateClick)
                        self.labelClicked.disconnect(self.openFormRecordRelation)
                    except Exception:
                        LOGGER.exception("Error al desconectar señal")

                self.keyF2Pressed.connect(self._push_button_db.animateClick)  # FIXME
                self.labelClicked.connect(self.openFormRecordRelation)
                if not self._text_label_db:
                    raise ValueError("_text_label_db is not defined!")

                self._text_label_db.installEventFilter(self)
                tlf = self._text_label_db.font()
                tlf.setUnderline(True)
                self._text_label_db.setFont(tlf)
                color_ = QtGui.QColor(QtCore.Qt.GlobalColor.darkBlue)
                # self._text_label_db.palette().setColor(self._text_label_db.foregroundRole(), cB)
                self._text_label_db.setStyleSheet("color:" + color_.name())
                self._text_label_db.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy(7), QtWidgets.QSizePolicy.Policy.Fixed
        )
        size_policy.setHeightForWidth(True)
        self.editor_.setSizePolicy(size_policy)
        if self._widgets_layout is not None:
            self._widgets_layout.addWidget(self._push_button_db)
            self._widgets_layout.addWidget(self.editor_)

    def clearPixmap(self) -> None:
        """
        Delete image in Pixmap type fields.
        """
        if self._editor_img:
            self._editor_img.clear()
            if self.cursor_ is None:
                raise Exception("cursor_ is empty!.")

            self.cursor_.setValueBuffer(self._field_name, None)

    @decorators.pyqt_slot(QtGui.QAction)
    def savePixmap(self, action_: "QtGui.QAction") -> None:
        """
        Save image in Pixmap type fields.

        @param fmt Indicates the format in which to save the image
        """
        if self._editor_img:
            ext = action_.text().lower()
            filename = "imagen.%s" % ext
            ext = "*.%s" % ext
            util = flutil.FLUtil()
            savefilename = QtWidgets.QFileDialog.getSaveFileName(
                self, util.translate("Pineboo", "Guardar imagen como"), filename, ext
            )
            if savefilename:
                pix = QtGui.QPixmap(self._editor_img.pixmap())
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
                if pix:
                    if not pix.save(savefilename[0]):
                        QtWidgets.QMessageBox.warning(
                            self,
                            util.translate("Pineboo", "Error"),
                            util.translate("Pineboo", "Error guardando fichero"),
                        )

            QtWidgets.QApplication.restoreOverrideCursor()

    @decorators.pyqt_slot()
    def toggleAutoCompletion(self) -> None:
        """
        Show / Hide the auto-completion wizard.
        """
        if self._auto_com_mode == "NeverAuto":
            return

        if not self._auto_com_frame and self.cursor_ is not None:
            self._auto_com_frame = QtWidgets.QWidget(self, QtCore.Qt.WindowType.Popup)
            lay = QtWidgets.QVBoxLayout()
            self._auto_com_frame.setLayout(lay)
            self._auto_com_frame.setWindowTitle("autoComFrame")
            # self._auto_com_frame->setFrameStyle(QFrame::PopupPanel | QFrame::Raised);
            # self._auto_com_frame->setLineWidth(1);
            self._auto_com_frame.hide()

            if not self._auto_com_popup:
                table_metadata = self.cursor_.metadata()
                field = table_metadata.field(self._field_name) if table_metadata else None

                if field is not None:
                    self._auto_com_popup = fldatatable.FLDataTable(None, "autoComPopup", True)
                    lay.addWidget(self._auto_com_popup)
                    cur: Optional["isqlcursor.ISqlCursor"] = None
                    field_relation = field.relationM1()

                    if field_relation is None:
                        if self._field_relation is not None and self._foreign_field is not None:
                            self._auto_com_field_name = self._foreign_field

                            mtd_relation = (
                                table_metadata.field(self._field_relation)
                                if table_metadata
                                else None
                            )

                            if mtd_relation is None:
                                return

                            field_relation_frel = mtd_relation.relationM1()

                            if field_relation_frel is None:
                                raise Exception("fRel.relationM1 is empty!.")

                            self._auto_com_field_relation = field_relation_frel.foreignField()
                            cur = pnsqlcursor.PNSqlCursor(
                                field_relation_frel.foreignTable(),
                                False,
                                self.cursor_.db().connectionName(),
                                None,
                                None,
                                self._auto_com_frame,
                            )
                            table_metadata = cur.metadata()
                            field = (
                                table_metadata.field(self._auto_com_field_name)
                                if table_metadata
                                else field
                            )
                        else:
                            self._auto_com_field_name = self._field_name
                            self._auto_com_field_relation = None
                            cur = pnsqlcursor.PNSqlCursor(
                                table_metadata.name(),
                                False,
                                self.cursor_.db().connectionName(),
                                None,
                                None,
                                self._auto_com_frame,
                            )

                    else:

                        self._auto_com_field_name = field_relation.foreignField()
                        self._auto_com_field_relation = None
                        cur = pnsqlcursor.PNSqlCursor(
                            field_relation.foreignTable(),
                            False,
                            self.cursor_.db().connectionName(),
                            None,
                            None,
                            self._auto_com_frame,
                        )
                        table_metadata = cur.metadata()
                        field = (
                            table_metadata.field(self._auto_com_field_name)
                            if table_metadata
                            else field
                        )

                    # Añade campo al cursor ...    FIXME!!
                    # cur.append(self._auto_com_field_name, field.type(), -1, field.length(), -1)

                    # for fieldNames in table_metadata.fieldNames().split(","):
                    #    field = table_metadata.field(fieldNames)
                    #    if field:
                    # cur.append(field.name(), field.type(), -1, field.length(), -1,
                    # "Variant", None, True) #qvariant,0,true

                    if self._auto_com_field_relation is not None and self._top_widget:
                        list1 = cast(List[FLFieldDB], self._top_widget.findChildren(FLFieldDB))
                        for itf in list1:
                            if itf.fieldName() == self._auto_com_field_relation:
                                filter = itf.filter()
                                if filter is not None:
                                    cur.setMainFilter(filter)
                                break

                    self._auto_com_popup.setFLSqlCursor(cur)
                    # FIXME
                    # self._auto_com_popup.setTopMargin(0)
                    # self._auto_com_popup.setLeftMargin(0)
                    self._auto_com_popup.horizontalHeader().hide()
                    self._auto_com_popup.verticalHeader().hide()

                    cur.newBuffer.connect(self.autoCompletionUpdateValue)
                    self._auto_com_popup.recordChoosed.connect(self.autoCompletionUpdateValue)

        if self._auto_com_popup:
            cur = cast(pnsqlcursor.PNSqlCursor, self._auto_com_popup.cursor())
            if cur is None:
                raise Exception("Unexpected: No cursor could be obtained")
            table_metadata = cur.metadata()
            field = table_metadata.field(self._auto_com_field_name) if table_metadata else None

            if field:
                _filter = (
                    self.cursor()
                    .db()
                    .connManager()
                    .manager()
                    .formatAssignValueLike(field, self.value(), True)
                )
                self._auto_com_popup.setFilter(_filter)
                self._auto_com_popup.setSort("%s ASC" % self._auto_com_field_name)
                self._auto_com_popup.refresh()

            if self._auto_com_frame is None:
                raise Exception("_auto_com_frame is empty")

            if not self._auto_com_frame.isVisible() and cur.size() > 1:
                tmp_point = None
                if self._show_alias and self._text_label_db:
                    tmp_point = self.mapToGlobal(self._text_label_db.geometry().bottomLeft())
                elif self._push_button_db and not self._push_button_db.isHidden():
                    tmp_point = self.mapToGlobal(self._push_button_db.geometry().bottomLeft())
                else:
                    tmp_point = self.mapToGlobal(self.editor_.geometry().bottomLeft())

                frame_width = self.width()
                if frame_width < self._auto_com_popup.width():
                    frame_width = self._auto_com_popup.width()

                if frame_width < self._auto_com_frame.width():
                    frame_width = self._auto_com_frame.width()

                self._auto_com_frame.setGeometry(tmp_point.x(), tmp_point.y(), frame_width, 300)
                self._auto_com_frame.show()
                self._auto_com_frame.setFocus()
            elif self._auto_com_frame.isVisible() and cur.size() == 1:
                self._auto_com_frame.hide()

            cur.first()
            del cur

    def autoCompletionUpdateValue(self) -> None:
        """
        Update the value of the field from the content that offers the auto completion wizard.
        """
        if not self._auto_com_popup or not self._auto_com_frame:
            return

        cur = cast(pnsqlcursor.PNSqlCursor, self._auto_com_popup.cursor())
        if not cur or not cur.isValid():
            return

        if isinstance(self.sender(), fldatatable.FLDataTable):
            self.setValue(cur.valueBuffer(self._auto_com_field_name))
            self._auto_com_frame.hide()
            # ifdef Q_OS_WIN32
            # if (editor_)
            #    editor_->releaseKeyboard();
            # if (_auto_com_popup)
            #    _auto_com_popup->releaseKeyboard();
            # endif
        elif isinstance(self.editor_, qtextedit.QTextEdit):
            self.setValue(self._auto_com_field_name)
        else:
            editor = cast(qlineedit.QLineEdit, self.editor_)
            if self._auto_com_frame.isVisible() and not editor.hasFocus():
                if not self._auto_com_popup.hasFocus():
                    cval = str(cur.valueBuffer(self._auto_com_field_name))
                    val = editor.text
                    editor.autoSelect = False  # pylint: disable=invalid-name
                    editor.setText(cval)
                    editor.setFocus()
                    editor.setCursorPosition(len(cval))
                    editor.cursorBackward(True, len(cval) - len(val))
                    # ifdef Q_OS_WIN32
                    # ed->grabKeyboard();
                    # endif
                else:
                    self.setValue(cur.valueBuffer(self._auto_com_field_name))

            elif not self._auto_com_frame.isVisible():
                cval = str(cur.valueBuffer(self._auto_com_field_name))
                val = editor.text
                editor.autoSelect = False
                editor.setText(cval)
                editor.setFocus()
                editor.setCursorPosition(len(cval))
                editor.cursorBackward(True, len(cval) - len(val))

        if self._auto_com_field_relation is not None and not self._auto_com_frame.isVisible():
            if self.cursor_ is not None and self._field_relation is not None:
                self.cursor_.setValueBuffer(
                    self._field_relation, cur.valueBuffer(self._auto_com_field_relation)
                )

    @decorators.pyqt_slot()
    def openFormRecordRelation(self) -> None:
        """
        Open an edit form for the value selected in its corresponding action.
        """
        if not self.cursor_:
            return

        if not self._field_name:
            return

        table_metadata = self.cursor_.metadata()
        if not table_metadata:
            return

        field = table_metadata.field(self._field_name)
        if field is None:
            return

        field_relation = field.relationM1()

        if field_relation is None:
            LOGGER.info("FLFieldDB : El campo de búsqueda debe tener una relación M1")
            return

        field_metadata = field.associatedField()

        value = self.cursor_.valueBuffer(field.name())
        if value in [None, ""] or (
            field_metadata is not None and self.cursor_.bufferIsNull(field_metadata.name())
        ):
            QtWidgets.QMessageBox.warning(
                QtWidgets.QApplication.focusWidget(),
                "Aviso",
                "Debe indicar un valor para %s" % field.alias(),
                QtWidgets.QMessageBox.StandardButton.Ok,
            )
            return

        self.cursor_.db().connManager().manager()
        cursor = pnsqlcursor.PNSqlCursor(
            field_relation.foreignTable(), True, self.cursor_.db().connectionName()
        )
        # c = pnsqlcursor.PNSqlCursor(field.relationM1().foreignTable())
        cursor.select(
            self.cursor_.db()
            .connManager()
            .manager()
            .formatAssignValue(field_relation.foreignField(), field, value, True)
        )
        # if c.size() <= 0:
        #    return

        if cursor.first():

            cursor.setAction(self._action_name)

            mode_access = self.cursor_.modeAccess()
            if mode_access in [self.cursor_.Insert, self.cursor_.Del]:
                mode_access = self.cursor_.Edit

            cursor.openFormInMode(mode_access, False)

    @decorators.pyqt_slot()
    @decorators.pyqt_slot(int)
    def searchValue(self) -> None:
        """
        Open a dialog to search the related table.
        """
        if not self.cursor_:
            return

        if not self._field_name:
            return
        table_metadata = self.cursor_.metadata()
        if not table_metadata:
            return

        field = table_metadata.field(self._field_name)
        if field is None:
            return

        field_relation = field.relationM1()

        if not field_relation:
            LOGGER.info("FLFieldDB : El campo de búsqueda debe tener una relación M1")
            return

        field_metadata = field.associatedField()

        form_search: "flformsearchdb.FLFormSearchDB"

        if field_metadata is not None:
            fmd_relation = field_metadata.relationM1()

            if fmd_relation is None:
                LOGGER.info("FLFieldDB : El campo asociado debe tener una relación M1")
                return
            value = self.cursor_.valueBuffer(field_metadata.name())
            if value is None or self.cursor_.bufferIsNull(field_metadata.name()):
                QtWidgets.QMessageBox.warning(
                    QtWidgets.QApplication.focusWidget(),
                    "Aviso",
                    "Debe indicar un valor para %s" % field_metadata.alias(),
                )
                return

            mng = self.cursor_.db().connManager().manager()
            cursor = pnsqlcursor.PNSqlCursor(
                fmd_relation.foreignTable(), True, self.cursor_.db().connectionName()
            )
            cursor.select(
                mng.formatAssignValue(fmd_relation.foreignField(), field_metadata, value, True)
            )
            if cursor.size() > 0:
                cursor.first()

            cursor2 = pnsqlcursor.PNSqlCursor(
                field_relation.foreignTable(),
                True,
                self.cursor_.db().connectionName(),
                cursor,
                fmd_relation,
            )

            # if self._action_name is None:
            #    a = mng.action(field.relationM1().foreignTable())
            # else:
            #    a = mng.action(self._action_name)
            #    if not a:
            #        return
            #    a.setTable(field.relationM1().foreignField())

            form_search = flformsearchdb.FLFormSearchDB(cursor2, self._top_widget)
            form_search.setFilter(
                mng.formatAssignValue(fmd_relation.foreignField(), field_metadata, value, True)
            )
        else:
            mng = self.cursor_.db().connManager().manager()
            if not self._action_name:
                action_ = mng.action(field_relation.foreignTable())
                if not action_:
                    return
            else:
                action_ = mng.action(self._action_name)
                if not action_:
                    return
                action_.setTable(field_relation.foreignTable())
            cursor = pnsqlcursor.PNSqlCursor(
                action_.table(), True, self.cursor_.db().connectionName()
            )
            # f = flformsearchdb.FLFormSearchDB(c, a.name(), self._top_widget)
            form_search = flformsearchdb.FLFormSearchDB(cursor, action_.name(), self._top_widget)
        form_search.setMainWidget()

        list_objs = form_search.findChildren(fltabledb.FLTableDB)
        obj_tdb = None

        if list_objs:
            obj_tdb = cast(fltabledb.FLTableDB, list_objs[0])
            if not obj_tdb.loaded():
                obj_tdb.load()
        if field_metadata is not None and obj_tdb is not None:
            # obj_tdb.setTableName(field.relationM1().foreignTable())
            # obj_tdb.setFieldRelation(field.associatedFieldFilterTo())
            # obj_tdb.setForeignField(field_metadata.relationM1().foreignField())
            if fmd_relation is not None:
                if fmd_relation.foreignTable() == table_metadata.name():
                    obj_tdb.setReadOnly(True)

        if self._filter:
            form_search.setFilter(self._filter)
        if form_search.mainWidget():
            cur_value = self.value()
            if obj_tdb:

                if field.type() == "string" and cur_value:
                    obj_tdb.setInitSearch(cur_value)
                    obj_tdb.putFirstCol(field_relation.foreignField())

                QtCore.QTimer.singleShot(0, obj_tdb._line_edit_search.setFocus)
            else:
                select = ""
                if cur_value:
                    select = mng.formatAssignValue(
                        cursor.primaryKey(),
                        cursor.metadata().field(cursor.primaryKey()),
                        cur_value,
                        True,
                    )
                cursor.select(select)
                cursor.first()

        value = form_search.exec_(field_relation.foreignField())
        form_search.close()
        # if cursor:
        #    del cursor
        if value:
            # self.setValue("")
            self.setValue(value)

    @decorators.pyqt_slot()
    def searchPixmap(self) -> None:
        """
        Open a dialog to search for an image file.

        If the field is not of the Pixmap type it does nothing.
        """
        if not self.cursor_ or not self._editor_img:
            return

        if not self._field_name:
            return

        table_metadata = self.cursor_.metadata()
        if not table_metadata:
            return

        field = table_metadata.field(self._field_name)

        if field is None:
            return

        if field.type() == "pixmap":
            file_dialog = QtWidgets.QFileDialog(
                self.parentWidget(), self.tr("Elegir archivo"), "", "*"
            )
            file_dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
            filename = None
            if file_dialog.exec() == cast(int, QtWidgets.QDialog.DialogCode.Accepted):
                filename = file_dialog.selectedFiles()

            if not filename:
                return
            self.setPixmap(filename[0])

    def setPixmap(self, filename: str) -> None:
        """
        Load an image into the pixmap type field.

        @param filename: Path to the file that contains the image
        """
        img = QtGui.QImage(filename)

        if not img:
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        pix = QtGui.QPixmap()
        buffer = QtCore.QBuffer()

        if img.width() <= self._max_pix_size and img.height() <= self._max_pix_size:
            pix.convertFromImage(img)
        else:
            new_width = 0
            new_height = 0
            if img.width() < img.height():
                new_height = self._max_pix_size
                new_width = round(new_height * img.width() / img.height())
            else:
                new_width = self._max_pix_size
                new_height = round(new_width * img.height() / img.width())
            pix.convertFromImage(img.scaled(new_width, new_height))

        QtWidgets.QApplication.restoreOverrideCursor()

        if not pix:
            return

        if self._editor_img is None:
            raise Exception("_editor_img is empty!")

        self._editor_img.setPixmap(pix)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        buffer.open(QtCore.QBuffer.OpenModeFlag.ReadWrite)
        pix.save(buffer, "XPM")

        QtWidgets.QApplication.restoreOverrideCursor()

        if not buffer:
            return

        text_ = buffer.data().data().decode("utf8")

        if text_.find("*dummy") > -1:
            text_ = text_.replace(
                "*dummy",
                "%s_%s_%s"
                % (
                    self.cursor().metadata().name(),
                    self._field_name,
                    QtCore.QDateTime().currentDateTime().toString("ddhhmmssz"),
                ),
            )
        self.updateValue(text_)

    def setPixmapFromPixmap(self, pixmap: QtGui.QPixmap, width: int = 0, height: int = 0) -> None:
        """
        Set an image into the pixmap type field with the preferred width and height.

        @param pixmap: pixmap to load in the field
        @param width: preferred width of the image
        @param height: preferred height of the image
        @author Silix
        """

        if pixmap.isNull():
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        pix = QtGui.QPixmap()
        buffer = QtCore.QBuffer()

        img = pixmap.toImage()

        if width and height:
            pix.convertFromImage(img.scaled(width, height))
        else:
            pix.convertFromImage(img)

        QtWidgets.QApplication.restoreOverrideCursor()
        if not pix:
            return

        if self._editor_img is None:
            raise Exception("_editor_img is empty!")

        self._editor_img.setPixmap(pix)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        buffer.open(QtCore.QBuffer.OpenModeFlag.ReadWrite)
        pix.save(buffer, "XPM")

        QtWidgets.QApplication.restoreOverrideCursor()

        if not buffer:
            return

        text_ = buffer.data().data().decode("utf8")

        # if not QtGui.QPixmapCache.find(s.left(100)):
        #    QtGui.QPixmapCache.insert(s.left(100), pix)
        self.updateValue(text_)

    @decorators.pyqt_slot(bool)
    def setPixmapFromClipboard(self) -> None:
        """
        Upload an image from the clipboard into the pixmap type field.

        @author Silix
        """
        clb = QtWidgets.QApplication.clipboard()
        img = clb.image()

        if not isinstance(img, QtGui.QImage):
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        pix = QtGui.QPixmap()
        buffer = QtCore.QBuffer()

        if img.width() <= self._max_pix_size and img.height() <= self._max_pix_size:
            pix.convertFromImage(img)
        else:
            new_width = 0
            new_height = 0
            if img.width() < img.height():
                new_height = self._max_pix_size
                new_width = round(new_height * img.width() / img.height())
            else:
                new_width = self._max_pix_size
                new_height = round(new_width * img.height() / img.width())

            pix.convertFromImage(img.scaled(new_width, new_height))

        QtWidgets.QApplication.restoreOverrideCursor()

        if not pix:
            return

        if self._editor_img is None:
            raise Exception("_editor_img is empty!")

        self._editor_img.setPixmap(pix)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        buffer.open(QtCore.QBuffer.OpenModeFlag.ReadWrite)
        pix.save(buffer, "XPM")

        QtWidgets.QApplication.restoreOverrideCursor()

        if not buffer:
            return

        text_ = buffer.data().data().decode("utf8")

        # if not QtGui.QPixmapCache.find(s.left(100)):
        #    QtGui.QPixmapCache.insert(s.left(100), pix)
        self.updateValue(text_)

    @decorators.not_implemented_warn
    def pixmap(self) -> QtGui.QPixmap:
        """
        Return the image object associated with the field.

        @return image associated to the field.
        @author Silix
        """
        return QtGui.QPixmap(self.value())

    def emitLostFocus(self) -> None:
        """
        Emit the lost focus signal.
        """
        self.lostFocus.emit()

    @decorators.pyqt_slot()
    def setNoShowed(self) -> None:
        """Set the control is not shown."""

        if self._foreign_field and self._field_relation:
            self._showed = False
            if self.isVisible():
                self.showWidget()

    @decorators.pyqt_slot(str)
    def setMapValue(self, value: Optional[str] = None) -> None:
        """
        Set the value of this field based on the result of the query.

        Whose clause 'where' is; field name of the object that sends the same signal
        to the value indicated as parameter.

        Only FLFielDB type objects can be connected, and their normal use is to connect
        the FLFieldDB :: textChanged (cons QString &) signal to this slot.

        @param v Value
        """

        if value is not None:
            self._field_map_value = cast(FLFieldDB, self.sender())
            self._map_value = value
            self.setMapValue()
        else:
            if not self._field_map_value:
                return

            if not self.cursor_:
                return

            table_metadata = self.cursor_.metadata()
            if not table_metadata:
                return

            field_name = self._field_map_value.fieldName()
            field = table_metadata.field(self._field_name)
            field_sender = table_metadata.field(field_name)

            if field is None or not field_sender:
                return

            field_relation = field.relationM1()

            if field_relation is not None:
                if not field_relation.foreignTable() == table_metadata.name():
                    mng = self.cursor_.db().connManager().manager()
                    relation_table = field_relation.foreignTable()
                    foreign_field = self._field_map_value.foreignField()
                    if foreign_field is None:
                        raise Exception("foreign field not found.")

                    qry = pnsqlquery.PNSqlQuery(None, self.cursor_.db().connectionName())
                    qry.setForwardOnly(True)
                    qry.setTablesList(relation_table)
                    qry.setSelect("%s,%s" % (field_relation.foreignField(), foreign_field))
                    qry.setFrom(relation_table)

                    where = mng.formatAssignValue(
                        foreign_field, field_sender, self._map_value, True
                    )
                    assoc_metadata = mng.metadata(relation_table)
                    filtert_ac = self.cursor_.filterAssoc(foreign_field, assoc_metadata)
                    if assoc_metadata and not assoc_metadata.inCache():
                        del assoc_metadata

                    if filtert_ac:
                        if not where:
                            where = filtert_ac
                        else:
                            where = "%s AND %s" % (where, filtert_ac)

                    if not self._filter:
                        qry.setWhere(where)
                    else:
                        qry.setWhere("%s AND %s" % (self._filter, where))

                    if qry.exec_() and qry.next():
                        # self.setValue("")
                        self.setValue(qry.value(0))

    @decorators.pyqt_slot()
    def emitKeyF2Pressed(self) -> None:
        """
        Emit the keyF2Pressed signal.

        The publisher's key_F2_Pressed signal (only if the editor is fllineedit.FLLineEdit)
        It is connected to this slot.
        """
        self.keyF2Pressed.emit()

    @decorators.pyqt_slot()
    def emitLabelClicked(self) -> None:
        """
        Emit the labelClicked signal. It is used in the M1 fields to edit the edition form of the selected value.
        """
        self.labelClicked.emit()

    @decorators.pyqt_slot(str)
    def emitTextChanged(self, text_: str) -> None:
        """
        Emit the textChanged signal.

        The textChanged signal from the editor (only if the editor is fllineedit.FLLineEdit)
        It is connected to this slot.
        """
        self.textChanged.emit(text_)

    # @decorators.pyqt_slot(int)
    # def ActivatedAccel(self, identifier: int) -> None:
    #    """
    #    Emit the activatedAccel (int) signal.
    #    """
    #    if self.editor_ and self.editor_.hasFocus:
    #        self._accel.activated.emit(identifier)

    def setDisabled(self, disable: bool) -> None:
        """Set if the control is disbled."""
        self.setEnabled(not disable)
        self.setKeepDisabled(disable)

    def setEnabled(self, enable: bool) -> None:
        """Set if the control is enabled."""

        if hasattr(self, "editor_"):
            if self.cursor_ is None:
                self.editor_.setDisabled(True)
                self.editor_.setStyleSheet("background-color: #f0f0f0")
            else:

                read_only = getattr(self.editor_, "setReadOnly", None)

                if read_only is not None:
                    table_metadata = self.cursor_.metadata()
                    field = table_metadata.field(self._field_name)

                    if field is None:
                        raise Exception("field is empty!.")

                    if not enable or not field.editable():
                        self.editor_.setStyleSheet("background-color: #f0f0f0")
                        read_only(True)
                    else:
                        read_only(not enable)
                        if (
                            not field.allowNull()
                            and not (field.type() in ["date", "time"])
                            and (self.cursor_ and self.cursor_.modeAccess() != self.cursor_.Browse)
                        ):
                            if not isinstance(self.editor_, qcombobox.QComboBox):
                                self.editor_.setStyleSheet(
                                    "background-color:%s; color:%s"
                                    % (
                                        self.notNullColor(),
                                        QtGui.QColor(QtCore.Qt.GlobalColor.black).name(),
                                    )
                                )
                            else:
                                self.editor_.setEditable(False)
                                self.editor_.setStyleSheet(self.styleSheet())
                        else:
                            self.editor_.setStyleSheet(self.styleSheet())

                else:
                    self.editor_.setEnabled(enable)
        if self._push_button_db:
            self._push_button_db.setEnabled(enable)
        return  # Mirar esto!! FIXME

        self.setAttribute(QtCore.Qt.WA_ForceDisabled, not enable)

        if (
            not self.isTopLevel()
            and self.parentWidget()
            and not self.parentWidget().isEnabled()
            and enable
        ):
            return

        if enable:
            if self.testAttribute(QtCore.Qt.WA_Disabled):
                self.setAttribute(QtCore.Qt.WA_Disabled, False)
                self.enabledChange(not enable)
                if self.children():
                    for child in self.children():
                        if not child.testAttribute(QtCore.Qt.WA_ForceDisabled):
                            if isinstance(child, qlineedit.QLineEdit):
                                allow_null = True
                                table_metadata = self.cursor_.metadata()
                                if table_metadata:
                                    field = table_metadata.field(self._field_name)
                                    if field and not field.allowNull():
                                        allow_null = False

                                if allow_null:
                                    color_bg = QtGui.QColor.blue()
                                    color_bg = (
                                        QtWidgets.QApplication()
                                        .palette()
                                        .color(QtGui.QPalette.Active, QtGui.QPalette.Base)
                                    )
                                else:
                                    color_bg = self.NotNullColor()

                                child.setDisabled(False)
                                child.setReadOnly(False)
                                child.palette().setColor(QtGui.QPalette.Base, color_bg)
                                child.setCursor(QtCore.Qt.IBeamCursor)
                                child.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
                                continue
                            child.setEnabled(True)

            else:
                if not self.testAttribute(QtCore.Qt.WA_Disabled):
                    if self.focusWidget() is self:
                        parent_is_enabled = False
                        if not self.parentWidget() or self.parentWidget().isEnabled():
                            parent_is_enabled = True
                        if not parent_is_enabled or not self.focusNextPrevChild(True):
                            self.clearFocus()
                    self.setAttribute(QtCore.Qt.WA_Disabled)
                    self.enabledChange(not enable)

                    if self.children():
                        for child in self.children():
                            if isinstance(child, qlineedit.QLineEdit):
                                child.setDisabled(False)
                                child.setReadOnly(True)
                                child.setCursor(QtCore.Qt.IBeamCursor)
                                child.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                                continue

                            elif isinstance(child, qtextedit.QTextEdit):
                                child.setDisabled(False)
                                child.setReadOnly(True)
                                child.viewPort().setCursor(QtCore.Qt.IBeamCursor)
                                child.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                                continue

                            if child is self._text_label_db and self._push_button_db:
                                child.setDisabled(False)
                                continue

                            child.setEnabled(False)
                            child.setAttribute(QtCore.Qt.WA_ForceDisabled, False)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        """Process event show."""
        self.load()
        if self._loaded:
            self.showWidget()
        super().showEvent(event)

    def showWidget(self) -> None:
        """
        Show the widget.
        """
        if self._loaded:
            if not self._showed:
                if self._top_widget:
                    self._showed = True
                    if not self._first_refresh:
                        self.refresh()
                        self._first_refresh = True

                    # if self._cursor_aux:
                    # print("Cursor auxiliar a ", self._table_name)
                    if (
                        self._cursor_aux
                        and self.cursor_
                        and self.cursor_.bufferIsNull(self._field_name)
                    ):

                        if (
                            self._foreign_field is not None
                            and self._field_relation is not None
                            and not self._cursor_aux.bufferIsNull(self._foreign_field)
                        ):
                            mng = self.cursor_.db().connManager().manager()
                            table_metadata = self.cursor_.metadata()
                            if table_metadata:
                                value = self._cursor_aux.valueBuffer(self._foreign_field)
                                # print("El valor de %s.%s es %s" % (table_metadata.name(), self._foreign_field, v))
                                if not self._table_name:
                                    raise ValueError("_table_name no puede ser Nulo")

                                if not self._field_name:
                                    raise ValueError("_field_name no puede ser Nulo")
                                # FIXME q = pnsqlquery.PNSqlQuery(False,
                                # self.cursor_.db().connectionName())
                                qry = pnsqlquery.PNSqlQuery(
                                    None, self.cursor_.db().connectionName()
                                )
                                qry.setForwardOnly(True)
                                qry.setTablesList(self._table_name)
                                qry.setSelect(self._field_name)
                                qry.setFrom(self._table_name)
                                where = mng.formatAssignValue(
                                    table_metadata.field(self._field_relation), value, True
                                )
                                filtert_ac = self._cursor_aux.filterAssoc(
                                    self._foreign_field, table_metadata
                                )

                                if filtert_ac:
                                    # print("FilterAC == ", filtert_ac)
                                    if where not in (None, ""):
                                        where = filtert_ac
                                    else:
                                        where = "%s AND %s" % (where, filtert_ac)

                                qry.setWhere(
                                    "%s AND %s" % (self._filter, where) if self._filter else where
                                )
                                # print("where tipo", type(where))
                                # print("Consulta = %s" % q.sql())
                                if qry.exec_() and qry.first():
                                    value = qry.value(0)
                                    if isinstance(value, str):
                                        if value[0:3] == "RK@":
                                            value = self.cursor_.fetchLargeValue(value)
                                    if isinstance(value, datetime.date):
                                        value = value.strftime("%d-%m-%Y")
                                    self.setValue(value)
                                # if not table_metadata.inCache():
                                #    del table_metadata
                    else:
                        if (
                            self.cursor_ is None
                            or self.cursor_.metadata().field(self._field_name) is None
                            and not self._foreign_field
                        ):
                            self.initFakeEditor()

                else:
                    self.initFakeEditor()

                self._showed = True

    def editor(self) -> "QtWidgets.QWidget":
        """Return editor control."""

        return self.editor_

    def initFakeEditor(self) -> None:
        """
        Initialize a false and non-functional editor.

        This is used when the form is being edited with the designer and not
        You can display the actual editor for not having a connection to the database.
        Create a very schematic preview of the editor, but enough to
        See the position and approximate size of the actual editor.
        """
        if hasattr(self, "editor_"):
            return

        has_push_button_db = None
        if not self._table_name and not self._foreign_field and not self._field_relation:
            has_push_button_db = True
        else:
            has_push_button_db = False

        if not self._field_name:
            self._field_alias = self.tr("Error: fieldName vacio")
        else:
            self._field_alias = self._field_name

        self.editor_ = qlineedit.QLineEdit(self)
        self.editor_.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed
        )
        if self._text_label_db:
            self._text_label_db.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Fixed
            )
        # self.editor_.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        self.editor_.setMinimumWidth(100)
        # if application.PROJECT.DGI.mobilePlatform():
        #    self.editor_.setMinimumHeight(60)

        if self._widgets_layout:
            self._widgets_layout.addWidget(self.editor_)
        self.editor_.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setFocusProxy(self.editor_)

        if not self.tableName():
            self._show_editor = False
            self._text_label_db = None

        if self._text_label_db:
            self._text_label_db.setText(self._field_alias)
            if self._show_alias:
                self._text_label_db.show()
            else:
                self._text_label_db.hide()

        if has_push_button_db:
            if self._push_button_db:
                self.setTabOrder(self._push_button_db, self.editor_)
                self._push_button_db.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                self._push_button_db.show()
        else:
            if self._push_button_db:
                self._push_button_db.hide()

        prty = ""
        if self._table_name:
            prty += "tN:" + str(self._table_name).upper() + ","
        if self._foreign_field:
            prty += "fF:" + str(self._foreign_field).upper() + ","
        if self._field_relation:
            prty += "fR:" + str(self._field_relation).upper() + ","
        if self._action_name:
            prty += "aN:" + str(self._action_name).upper() + ","

        if prty != "":
            self.editor_.setText(prty)
            self.setEnabled(False)
            self.editor_.home(False)

        if self.maximumSize().width() < 80:
            self.setShowEditor(False)
        else:
            self.setShowEditor(self._show_editor)

    def notNullColor(self) -> QtGui.QColor:
        """
        Require Field Color.
        """
        if not self._init_not_null_color:
            self._init_not_null_color = True
        self._not_null_color = settings.CONFIG.value(
            "ebcomportamiento/colorObligatorio", QtGui.QColor(255, 233, 173).name()
        )

        return self._not_null_color
