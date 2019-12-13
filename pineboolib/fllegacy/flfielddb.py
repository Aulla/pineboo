"""Flfieldb module."""

# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

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
    from pineboolib.interfaces import isqlcursor


class FLFieldDB(QtWidgets.QWidget):
    """FLFieldDB class."""

    logger = logging.getLogger("FLFieldDB")
    _loaded: bool
    _parent: QtWidgets.QWidget

    _tipo: str
    _partDecimal: int
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
    editorImg_: flpixmapview.FLPixmapView
    fieldName_: str  # Nombre del campo de la tabla al que esta asociado este componente
    tableName_: str  # Nombre de la tabla fóranea
    actionName_: str  # Nombre de la accion
    foreignField_: str  # Nombre del campo foráneo
    fieldRelation_: str  # Nombre del campo de la relación
    filter_: str  # Nombre del campo de la relación
    cursor_: Optional[
        "isqlcursor.ISqlCursor"
    ]  # Cursor con los datos de la tabla origen para el componente
    cursorInit_: bool  # Indica que si ya se ha inicializado el cursor
    cursorAuxInit: bool  # Indica que si ya se ha inicializado el cursor auxiliar
    cursorBackup_: Optional[
        "isqlcursor.ISqlCursor"
    ]  # Backup del cursor por defecto para acceder al modo tabla externa
    cursorAux: Optional[
        "isqlcursor.ISqlCursor"
    ]  # Cursor auxiliar de uso interno para almacenar los registros de la tabla relacionada con la de origen

    showed: bool
    showAlias_: bool
    autoComPopup_: Optional[fldatatable.FLDataTable]
    autoComFrame_: Optional[QtWidgets.QWidget]
    autoComFieldName_: str
    autoComFieldRelation_: Optional[str]
    accel_: Dict[str, QtWidgets.QShortcut]
    keepDisabled_: bool

    pbAux_: Optional[qpushbutton.QPushButton]
    pbAux2_: Optional[qpushbutton.QPushButton]
    pbAux3_: Optional[qpushbutton.QPushButton]
    pbAux4_: Optional[qpushbutton.QPushButton]
    fieldAlias_: Optional[str]
    showEditor_: bool
    field_map_value_: Optional["FLFieldDB"]
    autoCompMode_: str  # NeverAuto, OnDemandF4, AlwaysAuto
    timerAutoComp_: QtCore.QTimer
    textFormat_: QtCore.Qt.TextFormat
    initNotNullColor_: bool
    textLabelDB: Optional[QtWidgets.QLabel]
    FLWidgetFieldDBLayout: Optional[QtWidgets.QHBoxLayout]

    _refreshLaterEditor: Optional[str]

    pushButtonDB: qpushbutton.QPushButton
    keyF4Pressed: QtCore.pyqtSignal = QtCore.pyqtSignal()
    labelClicked: QtCore.pyqtSignal = QtCore.pyqtSignal()
    keyReturnPressed: QtCore.pyqtSignal = QtCore.pyqtSignal()
    lostFocus: QtCore.pyqtSignal = QtCore.pyqtSignal()
    textChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    keyF2Pressed: QtCore.pyqtSignal = QtCore.pyqtSignal()

    firstRefresh: bool

    """
    Tamaño de icono por defecto
    """
    iconSize: QtCore.QSize

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """Inicialize."""

        super(FLFieldDB, self).__init__(parent)
        self._loaded = False
        self.DEBUG = False  # FIXME: debe recoger DEBUG de pineboolib.project
        # self.editor_ = QtWidgets.QWidget(parent)
        # self.editor_.hide()
        self.cursor_ = None
        self.cursorBackup_ = None
        self.cursorInit_ = False
        self.cursorAuxInit_ = False
        self.showAlias_ = True
        self.showEditor_ = True
        self.autoCompMode_ = "OnDemandF4"
        self.autoComPopup_ = None
        self.autoComFrame_ = None
        self.autoComFieldRelation_ = None
        self.setObjectName("FLFieldDB")
        self.showed = False
        self._refreshLaterEditor = None
        self.keepDisabled_ = False
        self.initNotNullColor_ = False
        self.actionName_ = ""
        self.pbAux_ = None
        self.pbAux2_ = None
        self.pbAux3_ = None
        self.pbAux4_ = None
        self.accel_ = {}
        self.textFormat_ = QtCore.Qt.AutoText
        self.textLabelDB = None
        self.FLWidgetFieldDBLayout = None
        self.firstRefresh = False
        self.field_map_value_ = None

        self.maxPixImages_ = settings.config.value("ebcomportamiento/maxPixImages", None)
        self.autoCompMode_ = settings.config.value("ebcomportamiento/autoComp", "OnDemandF4")
        if self.maxPixImages_ in (None, ""):
            self.maxPixImages_ = 600
        self.maxPixImages_ = int(self.maxPixImages_)
        # self.editorImg_ = None

        self.iconSize = application.project.DGI.iconSize()

        self.FLLayoutH = QtWidgets.QVBoxLayout(self)
        self.FLLayoutH.setContentsMargins(0, 0, 0, 0)
        self.FLLayoutH.setSpacing(1)
        # self.FLLayoutH.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)

        self.lytButtons = QtWidgets.QHBoxLayout()
        self.lytButtons.setContentsMargins(0, 0, 0, 0)
        self.lytButtons.setSpacing(1)
        self.lytButtons.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

        # self.lytButtons.SetMinimumSize(22,22)
        # self.lytButtons.SetMaximumSize(22,22)

        self.FLWidgetFieldDBLayout = QtWidgets.QHBoxLayout()
        self.FLWidgetFieldDBLayout.setSpacing(1)
        self.FLWidgetFieldDBLayout.setContentsMargins(0, 0, 0, 0)
        self.FLWidgetFieldDBLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.FLLayoutH.addLayout(self.lytButtons)
        self.FLLayoutH.addLayout(self.FLWidgetFieldDBLayout)
        self.tableName_ = ""
        self.foreignField_ = ""
        self.fieldRelation_ = ""

        self.textLabelDB = QtWidgets.QLabel()
        self.textLabelDB.setObjectName("textLabelDB")
        if self.textLabelDB is not None:
            self.textLabelDB.setMinimumHeight(16)  # No inicia originalmente aqui
            self.textLabelDB.setAlignment(
                cast(QtCore.Qt.AlignmentFlag, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            )
            # self.textLabelDB.setFrameShape(QtGui.QFrame.WinPanel)
            self.textLabelDB.setFrameShadow(QtWidgets.QFrame.Plain)
            self.textLabelDB.setLineWidth(0)
            self.textLabelDB.setTextFormat(QtCore.Qt.PlainText)
            self.textLabelDB.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.fieldAlias_ = ""
        self.filter_ = ""

        self.FLWidgetFieldDBLayout.addWidget(self.textLabelDB)

        self.pushButtonDB = qpushbutton.QPushButton(self)
        self.pushButtonDB.setObjectName("pushButtonDB")

        self.setFocusProxy(self.pushButtonDB)
        # self.pushButtonDB.setFlat(True)
        PBSizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        PBSizePolicy.setHeightForWidth(True)
        self.pushButtonDB.setSizePolicy(PBSizePolicy)
        self.pushButtonDB.setMinimumSize(self.iconSize)
        self.pushButtonDB.setMaximumSize(self.iconSize)
        self.pushButtonDB.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButtonDB.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "flfielddb.png"))
        )
        self.pushButtonDB.clicked.connect(self.searchValue)

        self.timer_1 = QtCore.QTimer(self)

        self.cursorAux = None

        from . import flformdb

        while not isinstance(parent, flformdb.FLFormDB):
            parent = parent.parentWidget()

            if not parent:
                break

        self.topWidget_ = cast(flformdb.FLFormDB, parent)

    def load(self) -> None:
        """Load the cursor and initialize the control according to the type of data."""

        if self._loaded:
            return

        self._loaded = True
        if self.topWidget_:
            self.cursor_ = self.topWidget_.cursor()
            # print("Hay topWidget en %s", self)
        if self.DEBUG:
            if self.cursor_ and self.cursor_.d.buffer_:
                self.logger.info(
                    "*** FLFieldDB::loaded: cursor: %r name: %r at:%r",
                    self.cursor_,
                    self.cursor_.curName(),
                    self.cursor_.at(),
                )
                cur_values = [f.value for f in self.cursor_.d.buffer_.fieldsList()]
                self.logger.info("*** cursor Buffer: %r", cur_values)
            else:
                self.logger.warning("*** FLFieldDB::loaded: SIN cursor ??")

        self.cursorBackup_ = None
        self._partDecimal = 0
        self.initCursor()
        if (
            self.tableName_
            and self.cursor_ is not None
            and not self.cursor_.db().connManager().manager().metadata(self.tableName_)
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
        if not self.actionName_:
            raise ValueError("actionName is not defined!")
        return self.actionName_

    def setActionName(self, action_name: str) -> None:
        """
        Set the name of the action.

        @param action_name Name of the action
        """
        self.actionName_ = str(action_name)

    def fieldName(self) -> str:
        """
        Return the name of the field.

        @return Field Name
        """

        if not self.fieldName_:
            raise ValueError("fieldName is not defined!")
        return self.fieldName_

    def setFilter(self, filter: str) -> None:
        """Set a filter to the cursor."""

        self.filter_ = filter
        self.setMapValue()

    def filter(self) -> str:
        """Return the cursor filter."""

        return self.filter_

    def setFieldName(self, field_name: str) -> None:
        """
        Set the name of the field.

        @param field_name Field name
        """
        self.fieldName_ = field_name

    def tableName(self) -> str:
        """
        Return the name of the foreign table.

        @return Table name
        """
        return self.tableName_

    def setTableName(self, foreign_table: str) -> None:
        """
        Set the name of the foreign table.

        @param foreign_table Table name
        """

        if foreign_table:
            self.tableName_ = foreign_table
        else:
            self.tableName_ = ""

    def foreignField(self) -> str:
        """
        Return the name of the foreign field.

        @return Field Name
        """

        return self.foreignField_

    def setForeignField(self, foreign_field_name: str) -> None:
        """
        Set the name of the foreign field.

        @param foreign_field_name Field Name.
        """
        self.foreignField_ = foreign_field_name

    def fieldRelation(self) -> str:
        """
        Return the name of the related field.

        @return Field Name.
        """

        return self.fieldRelation_

    def setFieldRelation(self, field_relation: str) -> None:
        """
        Set the name of the related field.

        @param field_relation Field name
        """
        self.fieldRelation_ = field_relation

    def setFieldAlias(self, alias: str) -> None:
        """
        Set the field alias, shown on its label if showAlias ​​is True.

        @param alias Field alias, is the value of the tag. If it is empty it does nothing.
        """

        if alias:
            self.fieldAlias_ = alias
            if self.showAlias_ and self.textLabelDB:
                self.textLabelDB.setText(self.fieldAlias_)

    def setTextFormat(self, text_format: QtCore.Qt.TextFormat) -> None:
        """
        Set the text format.

        @param text_format Text field format
        """
        # FIXME: apply to control!
        self.textFormat_ = text_format
        # ted = self.editor_
        # if isinstance(ted, qtextedit.QTextEdit):
        #    ted.setTextFormat(self.textFormat_)

    def textFormat(self) -> int:
        """
        Return text field format.

        @return The format of the text.
        """

        # ted = self.editor_
        # if isinstance(ted, qtextedit.QTextEdit):
        #    return ted.textFormat()
        return self.textFormat_

    def setEchoMode(self, m: qlineedit.QLineEdit.EchoMode) -> None:
        """
        Set the "echo" mode.

        @param m Mode (Normal, NoEcho, Password)
        """
        if isinstance(self.editor_, qlineedit.QLineEdit):
            self.editor_.setEchoMode(m)

    def echoMode(self) -> int:
        """
        Return the echo mode.

        @return The "echo" mode (Normal, NoEcho, Password)
        """
        if isinstance(self.editor_, qlineedit.QLineEdit):
            return self.editor_.echoMode()

        return qlineedit.QLineEdit.Normal

    def _process_autocomplete_events(self, event: QtCore.QEvent) -> bool:
        """Process autocomplete events."""

        timerActive = False
        if self.autoComFrame_ and self.autoComFrame_.isVisible():
            if event.type() == QtCore.QEvent.KeyPress:
                key = cast(QtGui.QKeyEvent, event)
            if key.key() == QtCore.Qt.Key_Down and self.autoComPopup_:
                self.autoComPopup_.setQuickFocus()
                return True

            # --> WIN
            if self.editor_:
                self.editor_.releaseKeyboard()
            if self.autoComPopup_:
                self.autoComPopup_.releaseKeyboard()
            # <-- WIN

            self.autoComFrame_.hide()
            if self.editor_ and key.key() == QtCore.Qt.Key_Backspace:
                cast(fllineedit.FLLineEdit, self.editor_).backspace()

            if not self.timerAutoComp_:
                self.timerAutoComp_ = QtCore.QTimer(self)
                self.timerAutoComp_.timeout.connect(self.toggleAutoCompletion)
            else:
                self.timerAutoComp_.stop()

            if not key.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
                timerActive = True
                self.timerAutoComp_.start(500)
            else:
                QtCore.QTimer.singleShot(0, self.autoCompletionUpdateValue)
                return True
        if (
            not timerActive
            and self.autoCompMode_ == "AlwaysAuto"
            and (not self.autoComFrame_ or not self.autoComFrame_.isVisible())
        ):
            if key.key() in (
                QtCore.Qt.Key_Backspace,
                QtCore.Qt.Key_Delete,
                QtCore.Qt.Key_Space,
                QtCore.Qt.Key_ydiaeresis,
            ):
                if not self.timerAutoComp_:
                    self.timerAutoComp_ = QtCore.QTimer(self)
                    self.timerAutoComp_.timeout.connect(self.toggleAutoCompletion)
                else:
                    self.timerAutoComp_.stop()

                if not key.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
                    timerActive = True
                    self.timerAutoComp_.start(500)
                else:
                    QtCore.QTimer.singleShot(0, self.autoCompletionUpdateValue)
                    return True
        return False

    @decorators.pyqtSlot()
    @decorators.pyqtSlot(int)
    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent):
        """
        Process Qt events for keypresses.
        """
        if obj is None:
            return True

        QtWidgets.QWidget.eventFilter(self, obj, event)
        if event.type() == QtCore.QEvent.KeyPress:
            k = cast(QtGui.QKeyEvent, event)
            if self._process_autocomplete_events(event):
                return True

            if isinstance(obj, fllineedit.FLLineEdit):
                if k.key() == QtCore.Qt.Key_F4:
                    self.keyF4Pressed.emit()
                    return True
            elif isinstance(obj, qtextedit.QTextEdit):
                if k.key() == QtCore.Qt.Key_F4:
                    self.keyF4Pressed.emit()
                    return True
                return False

            if k.key() == QtCore.Qt.Key_Enter or k.key() == QtCore.Qt.Key_Return:
                self.focusNextPrevChild(True)
                self.keyReturnPressed.emit()
                return True

            if k.key() == QtCore.Qt.Key_Up:
                self.focusNextPrevChild(False)
                return True

            if k.key() == QtCore.Qt.Key_Down:
                self.focusNextPrevChild(True)
                return True

            if k.key() == QtCore.Qt.Key_F2:
                self.keyF2Pressed.emit()
                return True

            return False

        # elif isinstance(event, QtCore.QEvent.MouseButtonRelease) and
        # isinstance(obj,self.textLabelDB) and event.button() == QtCore.Qt.LeftButton:
        elif (
            event.type() == QtCore.QEvent.MouseButtonRelease
            and isinstance(obj, type(self.textLabelDB))
            and cast(QtGui.QMouseEvent, event).button() == QtCore.Qt.LeftButton
        ):
            self.emitLabelClicked()
            return True
        else:
            return False

    @decorators.pyqtSlot()
    def updateValue(self, data: Any = None):
        """
        Update the value of the field with a text string.

        @param data Text string to update the field
        """
        # print("Update Value", type(data), type(self.editor_))
        # if isinstance(data, QString): #Para quitar en el futuro
        #   data = str(data)
        if not self.cursor_:
            return

        isNull = False

        if hasattr(self, "editor_"):

            if isinstance(self.editor_, fldateedit.FLDateEdit):
                data = str(self.editor_.getDate())
                if not data:
                    isNull = True

                if not self.cursor_.bufferIsNull(self.fieldName_):

                    if str(data) == self.cursor_.valueBuffer(self.fieldName_):
                        return
                elif isNull:
                    return

                if isNull:
                    self.cursor_.setValueBuffer(
                        self.fieldName_, QtCore.QDate().toString("dd-MM-yyyy")
                    )
                else:
                    self.cursor_.setValueBuffer(self.fieldName_, data)

            elif isinstance(self.editor_, fltimeedit.FLTimeEdit):
                data = str(self.editor_.time().toString("hh:mm:ss"))

                if not data:
                    isNull = True
                if not self.cursor_.bufferIsNull(self.fieldName_):

                    if str(data) == self.cursor_.valueBuffer(self.fieldName_):
                        return
                elif isNull:
                    return

                if isNull:
                    self.cursor_.setValueBuffer(
                        self.fieldName_, str(QtCore.QTime().toString("hh:mm:ss"))
                    )
                else:
                    self.cursor_.setValueBuffer(self.fieldName_, data)

            elif isinstance(self.editor_, flcheckbox.FLCheckBox):
                data = bool(self.editor_.checkState())

                if not self.cursor_.bufferIsNull(self.fieldName_):
                    if data == bool(self.cursor_.valueBuffer(self.fieldName_)):
                        return

                self.cursor_.setValueBuffer(self.fieldName_, data)

            elif isinstance(self.editor_, qtextedit.QTextEdit):
                data = str(self.editor_.toPlainText())
                if not self.cursor_.bufferIsNull(self.fieldName_):
                    if self.cursor_.valueBuffer(self.fieldName_) == data:
                        return

                self.cursor_.setValueBuffer(self.fieldName_, data)

            elif isinstance(self.editor_, fllineedit.FLLineEdit):

                data = self.editor_.text()
                if not self.cursor_.bufferIsNull(self.fieldName_):
                    if data == self.cursor_.valueBuffer(self.fieldName_):
                        return
                self.cursor_.setValueBuffer(self.fieldName_, data)

            elif isinstance(self.editor_, qcombobox.QComboBox):
                data = str(self.editor_.getCurrentText())

                if not self.cursor_.bufferIsNull(self.fieldName_):
                    if data == self.cursor_.valueBuffer(self.fieldName_):
                        return

                self.cursor_.setValueBuffer(self.fieldName_, str(data))

        elif hasattr(self, "editorImg_"):
            if not data == self.cursor_.valueBuffer(self.fieldName_):
                self.cursor_.setValueBuffer(self.fieldName_, data)

    def status(self) -> None:
        """
        Return a report with the control status.
        """

        self.logger.info("****************STATUS**************")
        self.logger.info("FLField:", self.fieldName_)
        self.logger.info("FieldAlias:", self.fieldAlias_)
        self.logger.info("FieldRelation:", self.fieldRelation_)
        self.logger.info("Cursor:", self.cursor_)
        self.logger.info("CurName:", self.cursor().curName() if self.cursor_ else None)
        self.logger.info(
            "Editor: %s, EditorImg: %s"
            % (getattr(self, "editor_", None), getattr(self, "editorImg_", None))
        )
        self.logger.info("RefreshLaterEditor:", self._refreshLaterEditor)
        self.logger.info("************************************")

    def setValue(self, v: Any) -> None:
        """
        Set the value contained in the field.

        @param v Value to set
        """

        if not self.cursor_:
            self.logger.error(
                "FLFieldDB(%s):ERROR: El control no tiene cursor todavía. (%s)",
                self.fieldName_,
                self,
            )
            return
        # if v:
        #    print("FLFieldDB(%s).setValue(%s) ---> %s" % (self.fieldName_, v, self.editor_))

        if v == "":
            v = None

        tMD = self.cursor_.metadata()
        if not tMD:
            return

        field = tMD.field(self.fieldName_)
        if field is None:
            self.logger.warning("FLFieldDB::setValue(%s) : No existe el campo ", self.fieldName_)
            return

        type_ = field.type()

        # v = QVariant(cv)
        if field.hasOptionsList():
            idxItem = -1
            if type_ == "string":
                if v in field.optionsList():
                    idxItem = field.optionsList().index(v)
                else:
                    self.logger.warning(
                        "No se encuentra el valor %s en las opciones %s", v, field.optionsList()
                    )
            if idxItem == -1:
                cast(qcombobox.QComboBox, self.editor_).setCurrentItem(v)
            self.updateValue(cast(qcombobox.QComboBox, self.editor_).currentText)
            return

        if type_ == "pixmap":
            if self.editorImg_:

                if v is None:
                    self.editorImg_.clear()
                    return
                pix = QtGui.QPixmap(v)
                # if not QtGui.QPixmapCache().find(cs.left(100), pix):
                # print("FLFieldDB(%s) :: La imagen no se ha cargado correctamente" % self.fieldName_)
                #    QtGui.QPixmapCache().insert(cs.left(100), pix)
                # print("PIX =", pix)
                if pix:
                    self.editorImg_.setPixmap(pix)
                else:
                    self.editorImg_.clear()
        else:
            if not self.editor_:
                return

        if type_ in ("uint", "int"):
            doHome = False
            editor_int = cast(fllineedit.FLLineEdit, self.editor_)
            if not editor_int.text():
                doHome = True

            editor_int.setText(v if v else "0")

            if doHome:
                editor_int.home(False)

        elif type_ == "string":
            doHome = False
            editor_str = cast(fllineedit.FLLineEdit, self.editor_)
            if not editor_str.text():
                doHome = True

            editor_str.setText(v if v else "")

            if doHome:
                editor_str.home(False)

        elif type_ == "stringlist":

            cast(fllineedit.FLLineEdit, self.editor_).setText("" if v is None else v)

        elif type_ == "double":
            s = ""
            if v is not None:
                s = str(
                    round(float(v), self._partDecimal if self._partDecimal else field.partDecimal())
                )

            cast(fllineedit.FLLineEdit, self.editor_).setText(s)

        elif type_ == "serial":
            cast(fllineedit.FLLineEdit, self.editor_).setText(str(v) if v is not None else "")

        elif type_ == "date":
            editor_date = cast(fldateedit.FLDateEdit, self.editor_)
            if v is None:
                editor_date.setDate(QtCore.QDate())
            elif isinstance(v, str):
                if v.find("T") > -1:
                    v = v[0 : v.find("T")]
                editor_date.setDate(QtCore.QDate.fromString(v, "yyyy-MM-dd"))
            else:
                editor_date.setDate(v)

        elif type_ == "time":
            if v is None:
                v = QtCore.QTime()

            cast(fltimeedit.FLTimeEdit, self.editor_).setTime(v)

        elif type_ == "bool":
            if v is not None:
                cast(flcheckbox.FLCheckBox, self.editor_).setChecked(v)

        elif type_ == "timestamp":
            doHome = False
            editor_ts = cast(fllineedit.FLLineEdit, self.editor_)
            if not editor_ts.text():
                doHome = True

            editor_ts.setText(v if v else "")

            if doHome:
                editor_ts.home(False)

    def value(self) -> Any:
        """
        Return the value contained in the field.
        """
        if not self.cursor_:
            return None

        tMD = self.cursor_.metadata()
        if not tMD:
            return None

        field = tMD.field(self.fieldName_)
        if field is None:
            self.logger.warning(
                self.tr("FLFieldDB::value() : No existe el campo %s" % self.fieldName_)
            )
            return None

        v: Any = None

        if field.hasOptionsList():
            v = int(cast(qcombobox.QComboBox, self.editor_).currentItem())
            return v

        type_ = field.type()
        # fltype = FLFieldMetaData.flDecodeType(type_)

        if self.cursor_.bufferIsNull(self.fieldName_):
            if type_ == "double" or type_ == "int" or type_ == "uint":
                return 0

        if type_ in ("string", "stringlist", "timestamp"):
            if self.editor_:
                ed_ = self.editor_
                if isinstance(ed_, fllineedit.FLLineEdit):
                    v = ed_.text()

        if type_ in ("int", "uint"):
            if self.editor_:
                ed_ = self.editor_
                if isinstance(ed_, fllineedit.FLLineEdit):
                    v = ed_.text()
                    if v == "":
                        v = 0
                    else:
                        v = int(v)

        if type_ == "double":
            if self.editor_:
                ed_ = self.editor_
                if isinstance(ed_, fllineedit.FLLineEdit):
                    v = ed_.text()
                    if v == "":
                        v = 0.00
                    else:
                        v = float(v)

        elif type_ == "serial":
            if self.editor_:
                ed_ = self.editor_
                if isinstance(ed_, flspinbox.FLSpinBox):
                    v = ed_.value()

        elif type_ == "pixmap":
            v = self.cursor_.valueBuffer(self.fieldName_)

        elif type_ == "date":
            if self.editor_:
                v = cast(fldateedit.FLDateEdit, self.editor_).date
                if v:

                    v = types.Date(v)

        elif type_ == "time":
            if self.editor_:
                v = cast(fltimeedit.FLTimeEdit, self.editor_).time

        elif type_ == "bool":
            if self.editor_:
                v = cast(flcheckbox.FLCheckBox, self.editor_).isChecked()

        # v.cast(fltype)
        return v

    def selectAll(self) -> None:
        """
        Mark the field content as selected.
        """
        if not self.cursor_:
            return

        if not self.cursor_.metadata():
            return

        field = self.cursor_.metadata().field(self.fieldName_)
        if field is None:
            return
        type_ = field.type()

        if type_ in ("double", "int", "uint", "string", "timestamp"):
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
        Return the value of the showAlias ​​property.

        This property is used to know if you have to show the alias when you are
        in related cursor mode.
        """

        return self.showAlias_

    def setShowAlias(self, value: bool) -> None:
        """
        Set the state of the showAlias ​​property.
        """

        if not self.showAlias_ == value:
            self.showAlias_ = value
            if self.textLabelDB:
                if self.showAlias_:
                    self.textLabelDB.show()
                else:
                    self.textLabelDB.hide()

    def insertAccel(self, key: str) -> bool:
        """
        Insert a key combination as a keyboard accelerator, returning its identifier.

        @param key Text string representing the key combination (eg "Ctrl + Shift + O")
        @return The identifier internally associated with the key combination acceleration inserted
        """

        if key not in self.accel_.keys():
            accel = QtWidgets.QShortcut(QtGui.QKeySequence(key), self)
            # accel.activated.connect(self.ActivatedAccel)
            self.accel_[key] = accel

        return True

    def removeAccel(self, key: str) -> bool:
        """
        Eliminate, deactivate, a combination of acceleration keys according to their identifier.

        @param identifier Accelerator key combination identifier
        """

        if key in self.accel_.keys():
            del self.accel_[key]

        return True

    def setKeepDisabled(self, keep: bool) -> None:
        """
        Set the ability to keep the component disabled ignoring possible ratings for refreshments.

        See FLFieldDB :: keepDisabled_.
        """

        self.keepDisabled_ = keep

    def showEditor(self) -> bool:
        """
        Return the value of the showEditor property.
        """
        return self.showEditor_

    def setShowEditor(self, show: bool) -> None:
        """
        Set the value of the showEditor property.
        """

        self.showEditor_ = show
        ed: Any = None
        if hasattr(self, "editor_"):
            ed = self.editor_
        elif hasattr(self, "editorImg_"):
            ed = self.editorImg_

        if ed:
            if show:
                ed.show()
            else:
                ed.hide()

    def setPartDecimal(self, d: int) -> None:
        """
        Set the number of decimals.
        """
        self._partDecimal = d
        self.refreshQuick(self.fieldName_)
        # self.editor_.setText(self.editor_.text(),False)

    def setAutoCompletionMode(self, m: str) -> None:
        """
        Set automatic completion assistant mode.
        """
        self.autoCompMode_ = m

    def autoCompletionMode(self) -> str:
        """
        Return automatic completion assistant mode.
        """
        return self.autoCompMode_

    @decorators.pyqtSlot()
    @decorators.pyqtSlot("QString")
    def refresh(self, fN: Optional[str] = None) -> None:
        """
        Refresh the content of the field with the cursor values ​​of the source table.

        If the name of a field is indicated it only "refreshes" if the indicated field
        matches the fieldRelation property, taking the field value as a filter
        fieldRelation of the related table. If no name of Field refreshment is always carried out.

        @param fN Name of a field
        """
        if not self.cursor_ or not isinstance(self.cursor_, pnsqlcursor.PNSqlCursor):
            self.logger.debug("FLField.refresh() Cancelado")
            return
        tMD = self.cursor_.metadata()
        if not tMD:
            return

        v = None
        nulo = False
        if not fN:
            v = self.cursor_.valueBuffer(self.fieldName_)
            if self.fieldRelation_ is not None:
                nulo = self.cursor_.bufferIsNull(self.fieldRelation_)

            # if self.cursor_.cursorRelation():
            # print(1)
            # if self.cursor_.cursorRelation().valueBuffer(self.fieldRelation_) in ("", None):
            # FIXME: Este código estaba provocando errores al cargar formRecord hijos
            # ... el problema es, que posiblemente el cursorRelation entrega información
            # ... errónea, y aunque comentar el código soluciona esto, seguramente esconde
            # ... otros errores en el cursorRelation. Pendiente de investigar más.
            # v = None
            # if DEBUG: print("FLFieldDB: valueBuffer padre vacío.")

        else:
            if not self.fieldRelation_:
                raise ValueError("fieldRelation_ is not defined!")

            if not self.cursorAux and fN.lower() == self.fieldRelation_.lower():
                if self.cursor_.bufferIsNull(self.fieldRelation_):
                    return

                field = tMD.field(self.fieldRelation_)
                if field is None:
                    return

                relation_m1 = field.relationM1()
                if relation_m1 is None:
                    return

                tmd = pnsqlcursor.PNSqlCursor(relation_m1.foreignTable()).metadata()
                if tmd is None:
                    return

                # if self.topWidget_ and not self.topWidget_.isShown() and not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Insert:
                #    return

                if field is None:
                    return

                if not field.relationM1():
                    self.logger.info(
                        "FLFieldDB :El campo de la relación debe estar relacionado en M1"
                    )
                    return

                v = self.cursor_.valueBuffer(self.fieldRelation_)
                q = pnsqlquery.PNSqlQuery()
                q.setForwardOnly(True)
                relation_m1 = field.relationM1()
                if relation_m1 is None:
                    raise ValueError("relationM1 does not exist!")

                q.setTablesList(relation_m1.foreignTable())
                q.setSelect("%s,%s" % (self.foreignField(), relation_m1.foreignField()))
                q.setFrom(relation_m1.foreignTable())
                where = field.formatAssignValue(relation_m1.foreignField(), v, True)
                filterAc = self.cursor_.filterAssoc(self.fieldRelation_, tmd)
                if filterAc:
                    if not where:
                        where = filterAc
                    else:
                        where += " AND %s" % filterAc

                # if not self.filter_:
                #    q.setWhere(where)
                # else:
                #    q.setWhere(str(self.filter_ + " AND " + where))
                if self.filter_:
                    where = "%s AND %s" % (self.filter_, where)

                q.setWhere(where)
                if q.exec_() and q.next():
                    v0 = q.value(0)
                    v1 = q.value(1)
                    if not v0 == self.value():
                        self.setValue(v0)
                    if not v1 == v:
                        self.cursor_.setValueBuffer(self.fieldRelation_, v1)

            return

        field = tMD.field(str(self.fieldName_))
        if field is None:
            return
        type_ = field.type()

        if not type_ == "pixmap" and not self.editor_ and fN is not None:
            self._refreshLaterEditor = fN
            return

        modeAcces = self.cursor_.modeAccess()
        partDecimal = None
        if self._partDecimal:
            partDecimal = self._partDecimal
        else:
            partDecimal = field.partDecimal() or 0
            self._partDecimal = field.partDecimal()

        ol = field.hasOptionsList()

        fDis = False

        # if isinstance(v , QString): #Para quitar
        # v = str(v)
        if self.DEBUG:
            self.logger.info(
                "FLFieldDB:: refresh fN:%r fieldName:%r v:%s" % (fN, self.fieldName_, repr(v)[:64])
            )

        if (
            self.keepDisabled_
            or self.cursor_.fieldDisabled(self.fieldName_)
            or (
                modeAcces == pnsqlcursor.PNSqlCursor.Edit
                and (field.isPrimaryKey() or tMD.fieldListOfCompoundKey(self.fieldName_))
            )
            or not field.editable()
            or modeAcces == pnsqlcursor.PNSqlCursor.Browse
        ):
            fDis = True

        self.setEnabled(not fDis)

        if type_ == "double":
            editor_dbl = cast(fllineedit.FLLineEdit, self.editor_)
            try:
                cast(QtCore.pyqtSignal, editor_dbl.textChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.debug("Error al desconectar señal textChanged", exc_info=True)
            s = None

            if nulo and v is None:
                dv = field.defaultValue()

                if field.allowNull():
                    editor_dbl.setText("" if dv is None else dv)
                else:
                    if dv is not None:
                        editor_dbl.setText(dv)

            else:
                if not v:
                    v = 0.0
                s = str(round(float(v), partDecimal))
                pos_dot = s.find(".")

                if pos_dot is not None and pos_dot > -1:
                    while len(s[pos_dot + 1 :]) < partDecimal:
                        s = "%s0" % s
                editor_dbl.setText(s)

            cast(QtCore.pyqtSignal, editor_dbl.textChanged).connect(self.updateValue)

            # if v == None and not nulo:
            #    self.editor_.setText("0.00")

        elif type_ == "string":

            doHome = False
            if not ol:
                editor_str = cast(fllineedit.FLLineEdit, self.editor_)
                try:
                    cast(QtCore.pyqtSignal, editor_str.textChanged).disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal textChanged")
            else:
                editor_cb = cast(qcombobox.QComboBox, self.editor_)

            if v is not None:
                if ol:
                    if v.find("QT_TRANSLATE") != -1:
                        v = utils_base.aqtt(v)
                    idx = field.getIndexOptionsList(v)
                    if idx is not None:
                        editor_cb.setCurrentIndex(idx)
                else:
                    editor_str.setText(v)
            else:
                if ol:
                    editor_cb.setCurrentIndex(0)
                else:
                    def_val = field.defaultValue() or ""
                    editor_str.setText(def_val if not nulo else "")

            if not ol:
                if doHome:
                    editor_str.home(False)

                cast(QtCore.pyqtSignal, editor_str.textChanged).connect(self.updateValue)

        elif type_ == "timestamp":

            doHome = False
            editor_str = cast(fllineedit.FLLineEdit, self.editor_)
            try:
                cast(QtCore.pyqtSignal, editor_str.textChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal textChanged")

            if v is not None:
                editor_str.setText(v)
            else:
                def_val = field.defaultValue() or ""
                editor_str.setText(def_val if not nulo else "")

            if doHome:
                editor_str.home(False)

            cast(QtCore.pyqtSignal, editor_str.textChanged).connect(self.updateValue)

        elif type_ in ("int", "uint"):
            editor_int = cast(fllineedit.FLLineEdit, self.editor_)
            try:
                cast(QtCore.pyqtSignal, editor_int.textChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal textChanged")

            if nulo and not v:
                dv = field.defaultValue()
                if field.allowNull():
                    if dv is None:
                        editor_int.setText("")
                    else:
                        editor_int.setText(dv)
                else:
                    if dv is not None:
                        editor_int.setText(dv)

            else:
                if not v:
                    editor_int.setText(str(0))
                else:
                    editor_int.setText(v)

            cast(QtCore.pyqtSignal, editor_int.textChanged).connect(self.updateValue)

        elif type_ == "serial":
            editor_serial = cast(fllineedit.FLLineEdit, self.editor_)
            try:
                cast(QtCore.pyqtSignal, editor_serial.textChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal textChanged")
            editor_serial.setText(str(0))

            cast(QtCore.pyqtSignal, editor_serial.textChanged).connect(self.updateValue)

        elif type_ == "pixmap":
            if not hasattr(self, "editorImg_"):

                self.editorImg_ = flpixmapview.FLPixmapView(self)
                self.editorImg_.setFocusPolicy(QtCore.Qt.NoFocus)
                self.editorImg_.setSizePolicy(self.sizePolicy())
                self.editorImg_.setMaximumSize(147, 24)
                # self.editorImg_.setMinimumSize(self.minimumSize())
                self.editorImg_.setAutoScaled(True)
                # self.FLWidgetFieldDBLayout.removeWidget(self.pushButtonDB)
                if self.FLWidgetFieldDBLayout is None:
                    raise Exception("FLWidgetFieldDBLayout is empty!")
                self.FLWidgetFieldDBLayout.addWidget(self.editorImg_)
                self.pushButtonDB.hide()

                if field.visible():
                    self.editorImg_.show()
                else:
                    return
                # else:
            # if modeAcces == pnsqlcursor.PNSqlCursor.Browse:
            if field.visible():
                # cs = QString()
                if not v:
                    self.editorImg_.clear()
                    return
                    # cs = v.toString()
                # if cs.isEmpty():
                #    self.editorImg_.clear()
                #    return
                if isinstance(v, str):
                    if v.find("static char") > -1:

                        v = xpm.cacheXPM(v)

                pix = QtGui.QPixmap(v)
                # if not QtGui.QPixmapCache.find(cs.left(100), pix):
                # pix.loadFromData()
                # QtGui.QPixmapCache.insert(cs.left(100), pix)

                if pix:
                    self.editorImg_.setPixmap(pix)
                else:
                    self.editorImg_.clear()

            # if modeAcces == pnsqlcursor.PNSqlCursor.Browse:
            # self.pushButtonDB.setVisible(False)

        elif type_ == "date":
            editor_date = cast(fldateedit.FLDateEdit, self.editor_)
            if self.cursor_.modeAccess() == self.cursor_.Insert and nulo and not field.allowNull():
                defVal = field.defaultValue()
                if defVal is not None:
                    defVal = QtCore.QDate.fromString(str(defVal))
                else:
                    defVal = QtCore.QDate.currentDate()

                editor_date.setDate(defVal)
                self.updateValue(defVal)

            else:
                try:
                    cast(QtCore.pyqtSignal, editor_date.dateChanged).disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal textChanged")

                if v:
                    util = flutil.FLUtil()
                    v = util.dateDMAtoAMD(v)
                    editor_date.setDate(v)
                else:
                    editor_date.setDate()

                cast(QtCore.pyqtSignal, editor_date.dateChanged).connect(self.updateValue)

        elif type_ == "time":
            editor_time = cast(fltimeedit.FLTimeEdit, self.editor_)
            if self.cursor_.modeAccess() == self.cursor_.Insert and nulo and not field.allowNull():
                defVal = field.defaultValue()
                if defVal is not None:
                    defVal = QtCore.QTime.fromString(str(defVal))
                else:
                    defVal = QtCore.QTime.currentTime()

                editor_time.setTime(defVal)
                self.updateValue(defVal)

            else:
                try:
                    cast(QtCore.pyqtSignal, editor_time.timeChanged).disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal timeChanged")

                if v is not None:
                    editor_time.setTime(v)

                cast(QtCore.pyqtSignal, editor_time.timeChanged).connect(self.updateValue)

        elif type_ == "stringlist":
            editor_sl = cast(qtextedit.QTextEdit, self.editor_)
            try:
                cast(QtCore.pyqtSignal, editor_sl.textChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal timeChanged")
            if v is not None:
                editor_sl.setText(v)
            else:
                def_val = field.defaultValue() or ""
                editor_sl.setText(str(def_val))
            cast(QtCore.pyqtSignal, editor_sl.textChanged).connect(self.updateValue)

        elif type_ == "bool":
            editor_bool = cast(flcheckbox.FLCheckBox, self.editor_)
            try:
                cast(QtCore.pyqtSignal, editor_bool.toggled).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal toggled")

            if v is not None:

                editor_bool.setChecked(v)
            else:
                dV = field.defaultValue()
                if dV is not None:
                    editor_bool.setChecked(dV)

            cast(QtCore.pyqtSignal, editor_bool.toggled).connect(self.updateValue)

        if not field.visible():
            if self.editor_:
                self.editor_.hide()
            elif self.editorImg_:
                self.editorImg_.hide()
            self.setEnabled(False)

    """
    Refresco rápido
    """

    @decorators.pyqtSlot("QString")
    def refreshQuick(self, fN: Optional[str] = None) -> None:
        """Refresh value quick."""
        if not fN or not fN == self.fieldName_ or not self.cursor_:
            return

        tMD = self.cursor_.metadata()
        field = tMD.field(self.fieldName_)

        if field is None:
            return

        if field.outTransaction():
            return

        type_ = field.type()

        if not type_ == "pixmap" and not self.editor_:
            return
        v = self.cursor_.valueBuffer(self.fieldName_)
        nulo = self.cursor_.bufferIsNull(self.fieldName_)

        if self._partDecimal < 0:
            self._partDecimal = field.partDecimal()

        ol = field.hasOptionsList()

        if type_ == "double":
            editor_le = cast(fllineedit.FLLineEdit, self.editor_)
            # part_decimal = self._partDecimal if self._partDecimal > -1 else field.partDecimal()

            e_text = editor_le.text() if editor_le.text() != "" else 0.0
            if float(str(e_text)) == float(v):
                return
            try:
                cast(QtCore.pyqtSignal, editor_le.textChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal textChanged")

            if not nulo:
                v = round(v, self._partDecimal)

            editor_le.setText(v, False)

            cast(QtCore.pyqtSignal, editor_le.textChanged).connect(self.updateValue)

        elif type_ == "string":
            doHome = False
            if ol:
                cb = cast(qcombobox.QComboBox, self.editor_)
                if str(v) == cb.currentText:
                    return
            else:
                ed = cast(fllineedit.FLLineEdit, self.editor_)
                if str(v) == ed.text():
                    return

                if not ed.text():
                    doHome = True

                cast(QtCore.pyqtSignal, ed.textChanged).disconnect(self.updateValue)

            if v:
                if ol:
                    cb.setCurrentText(v)

                else:
                    ed.setText(v, False)

            else:
                if ol:
                    cb.setCurrentIndex(0)

                else:
                    ed.setText("", False)

            if not ol:
                if doHome:
                    ed.home(False)

                cast(QtCore.pyqtSignal, ed.textChanged).connect(self.updateValue)

        elif type_ in ("uint", "int", "serial", "timestamp"):
            editor_le = cast(fllineedit.FLLineEdit, self.editor_)
            if v == editor_le.text():
                return
            try:
                cast(QtCore.pyqtSignal, editor_le.textChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal textChanged")

            if not nulo:
                editor_le.setText(v)

            cast(QtCore.pyqtSignal, editor_le.textChanged).connect(self.updateValue)

        elif type_ == "pixmap":
            if not self.editorImg_:
                self.editorImg_ = flpixmapview.FLPixmapView(self)
                self.editorImg_.setFocusPolicy(QtCore.Qt.NoFocus)
                self.editorImg_.setSizePolicy(self.sizePolicy())
                self.editorImg_.setMaximumSize(147, 24)
                # self.editorImg_.setMinimumSize(self.minimumSize())
                self.editorImg_.setAutoScaled(True)
                if self.FLWidgetFieldDBLayout is None:
                    raise Exception("FLWidgetFieldDBLayout is empty!")
                self.FLWidgetFieldDBLayout.addWidget(self.editorImg_)
                if field.visible():
                    self.editorImg_.show()

            if not nulo:
                if not v:
                    self.editorImg_.clear()
                    return

            if isinstance(v, str):
                if v.find("static char") > -1:

                    v = xpm.cacheXPM(v)

            pix = QtGui.QPixmap(v)
            # pix.loadFromData(v)

            if pix.isNull():
                self.editorImg_.clear()
            else:
                self.editorImg_.setPixmap(pix)

        elif type_ == "date":
            editor_d = cast(fldateedit.FLDateEdit, self.editor_)
            if v == editor_d.date:
                return

            try:
                cast(QtCore.pyqtSignal, editor_d.dateChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal dateChanged")
            editor_d.setDate(v)
            cast(QtCore.pyqtSignal, editor_d.dateChanged).connect(self.updateValue)

        elif type_ == "time":
            editor_t = cast(fltimeedit.FLTimeEdit, self.editor_)
            if v == str(editor_t.time()):
                return

            try:
                cast(QtCore.pyqtSignal, editor_t.timeChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal")

            if v is None:
                v = "00:00:00"

            editor_t.setTime(v)
            cast(QtCore.pyqtSignal, editor_t.timeChanged).connect(self.updateValue)

        elif type_ == "stringlist":
            editor_sl = cast(qtextedit.QTextEdit, self.editor_)
            if v == str(editor_sl.toPlainText()):
                return

            try:
                cast(QtCore.pyqtSignal, editor_sl.textChanged).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal")

            editor_sl.setText(v)
            cast(QtCore.pyqtSignal, editor_sl.textChanged).connect(self.updateValue)

        elif type_ == "bool":
            editor_b = cast(flcheckbox.FLCheckBox, self.editor_)
            if v == editor_b.isChecked():
                return

            try:
                cast(QtCore.pyqtSignal, editor_b.toggled).disconnect(self.updateValue)
            except Exception:
                self.logger.exception("Error al desconectar señal")

            editor_b.setChecked(v)
            cast(QtCore.pyqtSignal, editor_b.toggled).connect(self.updateValue)

    def initCursor(self) -> None:
        """
        Start the cursor according to this field either from the source table or from a related table.
        """
        if application.project.conn_manager is None:
            raise Exception("Project is not connected yet")

        if self.tableName_ and not self.foreignField_ and not self.fieldRelation_:
            self.cursorBackup_ = self.cursor_
            if self.cursor_:
                self.cursor_ = pnsqlcursor.PNSqlCursor(
                    self.tableName_,
                    True,
                    application.project.conn_manager.useConn("default").connectionName(),
                    None,
                    None,
                    self,
                )
            else:
                if not self.topWidget_:
                    return
                self.cursor_ = pnsqlcursor.PNSqlCursor(
                    self.tableName_,
                    True,
                    application.project.conn_manager.useConn("default").connectionName(),
                    None,
                    None,
                    self,
                )
            self.cursor_.setModeAccess(pnsqlcursor.PNSqlCursor.Browse)
            if self.showed:
                try:
                    self.cursor_.cursorUpdated.disconnect(self.refresh)
                except Exception:
                    self.logger.exception("Error al desconectar señal")
            self.cursor_.cursorUpdated.connect(self.refresh)
            return
        else:
            if self.cursorBackup_:
                try:
                    if self.cursor_ is not None:
                        self.cursor_.cursorUpdated.disconnect(self.refresh)
                except Exception:
                    self.logger.exception("Error al desconectar señal")
                self.cursor_ = self.cursorBackup_
                self.cursorBackup_ = None

        if not self.cursor_:
            return

        if not self.tableName_ or not self.foreignField_ or not self.fieldRelation_:
            if self.foreignField_ and self.fieldRelation_:
                if self.showed:
                    try:
                        self.cursor_.bufferChanged.disconnect(self.refresh)
                    except Exception:
                        self.logger.exception("Error al desconectar señal")
                self.cursor_.bufferChanged.connect(self.refresh)

            if self.showed:
                try:
                    self.cursor_.newBuffer.disconnect(self.refresh)
                except Exception:
                    self.logger.exception("Error al desconectar señal")

                try:
                    self.cursor_.bufferChanged.disconnect(self.refreshQuick)
                except Exception:
                    self.logger.exception("Error al desconectar señal")

            self.cursor_.newBuffer.connect(self.refresh)
            self.cursor_.bufferChanged.connect(self.refreshQuick)
            return

        tMD = self.cursor_.db().connManager().manager().metadata(self.tableName_)
        if not tMD:
            return

        try:
            self.cursor_.newBuffer.disconnect(self.refresh)
        except TypeError:
            pass

        try:
            self.cursor_.bufferChanged.disconnect(self.refreshQuick)
        except TypeError:
            pass

        self.cursorAux = self.cursor()
        if not self.cursor().metadata():
            return

        curName = self.cursor().metadata().name()

        rMD = tMD.relation(self.fieldRelation_, self.foreignField_, curName)
        if not rMD:
            checkIntegrity = False
            testM1 = self.cursor_.metadata().relation(
                self.foreignField_, self.fieldRelation_, self.tableName_
            )
            if testM1:
                if testM1.cardinality() == pnrelationmetadata.PNRelationMetaData.RELATION_1M:
                    checkIntegrity = True
            fMD = tMD.field(self.fieldRelation_)

            if fMD is not None:
                rMD = pnrelationmetadata.PNRelationMetaData(
                    curName,
                    self.foreignField_,
                    pnrelationmetadata.PNRelationMetaData.RELATION_1M,
                    False,
                    False,
                    checkIntegrity,
                )

                fMD.addRelationMD(rMD)
                self.logger.trace(
                    "FLFieldDB : La relación entre la tabla del formulario ( %s ) y la tabla ( %s ) de este campo ( %s ) no existe, "
                    "pero sin embargo se han indicado los campos de relación( %s, %s)",
                    curName,
                    self.tableName_,
                    self.fieldName_,
                    self.fieldRelation_,
                    self.foreignField_,
                )
                self.logger.trace(
                    "FLFieldDB : Creando automáticamente %s.%s --1M--> %s.%s",
                    self.tableName_,
                    self.fieldRelation_,
                    curName,
                    self.foreignField_,
                )
            else:
                self.logger.trace(
                    "FLFieldDB : El campo ( %s ) indicado en la propiedad fieldRelation no se encuentra en la tabla ( %s )",
                    self.fieldRelation_,
                    self.tableName_,
                )

        if self.tableName_:
            # self.cursor_ = pnsqlcursor.PNSqlCursor(self.tableName_)
            self.cursor_ = pnsqlcursor.PNSqlCursor(
                self.tableName_, False, self.cursor_.connectionName(), self.cursorAux, rMD, self
            )

        if not self.cursor_:
            self.cursor_ = self.cursorAux
            if self.showed:
                try:
                    self.cursor_.newBuffer.disconnect(self.refresh)
                except Exception:
                    self.logger.exception("Error al desconectar señal")

                try:
                    self.cursor_.bufferChanged.disconnect(self.refreshQuick)
                except Exception:
                    self.logger.exception("Error al desconectar señal")

            self.cursor_.newBuffer.connect(self.refresh)
            self.cursor_.bufferChanged.connect(self.refreshQuick)
            self.cursorAux = None
            return
        else:
            if self.showed:
                try:
                    self.cursor_.newBuffer.disconnect(self.setNoShowed)
                except Exception:
                    self.logger.exception("Error al desconectar señal")
            self.cursor_.newBuffer.connect(self.setNoShowed)

        self.cursor_.setModeAccess(pnsqlcursor.PNSqlCursor.Browse)
        if self.showed:
            try:
                self.cursor_.newBuffer.disconnect(self.refresh)
            except Exception:
                self.logger.exception("Error al desconectar señal")

            try:
                self.cursor_.bufferChanged.disconnect(self.refreshQuick)
            except Exception:
                self.logger.exception("Error al desconectar señal")

        self.cursor_.newBuffer.connect(self.refresh)
        self.cursor_.bufferChanged.connect(self.refreshQuick)

        # self.cursor_.append(self.cursor_.db().db().recordInfo(self.tableName_).find(self.fieldName_)) #FIXME
        # self.cursor_.append(self.cursor_.db().db().recordInfo(self.tableName_).find(self.fieldRelation_))
        # #FIXME

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

        # if self.editorImg_:
        #    del self.editorImg_
        #    self.editorImg_ = None

        tMD = self.cursor_.metadata()
        if not tMD:
            return

        field = tMD.field(self.fieldName_)
        if field is None:
            return

        type_ = field.type()
        len_ = field.length()
        partInteger = field.partInteger()
        partDecimal = None
        if type_ == "double":
            if self._partDecimal:
                partDecimal = self._partDecimal
            else:
                partDecimal = field.partDecimal()
                self._partDecimal = field.partDecimal()

        rX = field.regExpValidator()
        ol = field.hasOptionsList()

        rt = None
        field_relation = field.relationM1()
        if field_relation is not None:
            if not field_relation.foreignTable() == tMD.name():
                rt = field_relation.foreignTable()

        hasPushButtonDB = False
        self.fieldAlias_ = field.alias()

        if self.fieldAlias_ is None:
            raise Exception(
                "alias from %s.%s is not defined!" % (field.metadata().name(), field.name())
            )

        if self.textLabelDB:
            self.textLabelDB.setFont(self.font())
            if type_ not in ["pixmap", "bool"]:
                if not field.allowNull() and field.editable():
                    self.textLabelDB.setText("%s*" % self.fieldAlias_)
                else:
                    self.textLabelDB.setText(self.fieldAlias_)
            else:
                self.textLabelDB.hide()

        if rt:
            hasPushButtonDB = True
            tmd = self.cursor_.db().connManager().manager().metadata(rt)
            if not tmd and self.pushButtonDB:
                self.pushButtonDB.setDisabled(True)
                field.setEditable(False)

            if tmd and not tmd.inCache():
                del tmd

        self.initMaxSize_ = self.maximumSize()
        self.initMinSize_ = self.minimumSize()

        if type_ in ("uint", "int", "double", "string", "timestamp"):
            self.initEditorControlForNumber(
                has_option_list=ol,
                field=field,
                type_=type_,
                partDecimal=partDecimal,
                partInteger=partInteger,
                len_=len_,
                rX=rX,
                hasPushButtonDB=hasPushButtonDB,
            )
        elif type_ == "serial":
            self.editor_ = fllineedit.FLLineEdit(self, "editor")
            self.editor_.setFont(self.font())
            self.editor_.setMaxValue(pow(10, field.partInteger()) - 1)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy(7), QtWidgets.QSizePolicy.Policy(0)
            )
            sizePolicy.setHeightForWidth(True)
            self.editor_.setSizePolicy(sizePolicy)
            if self.FLWidgetFieldDBLayout:
                self.FLWidgetFieldDBLayout.addWidget(self.editor_)
            self.editor_.installEventFilter(self)
            self.editor_.setDisabled(True)
            self.editor_.setAlignment(QtCore.Qt.AlignRight)
            if self.pushButtonDB:
                self.pushButtonDB.hide()

            if self.showed:
                try:
                    self.editor_.textChanged.disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal")
            self.editor_.textChanged.connect(self.updateValue)

        elif type_ == "pixmap":
            # if not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
            if not self.tableName():
                if not hasattr(self, "editorImg_") and self.FLWidgetFieldDBLayout:
                    self.FLWidgetFieldDBLayout.setDirection(QtWidgets.QBoxLayout.Down)
                    self.editorImg_ = flpixmapview.FLPixmapView(self)
                    self.editorImg_.setFocusPolicy(QtCore.Qt.NoFocus)
                    self.editorImg_.setSizePolicy(self.sizePolicy())
                    self.editorImg_.setMaximumSize(self.maximumSize())
                    self.editorImg_.setMinimumSize(self.minimumSize())
                    if self.iconSize:
                        self.setMinimumHeight(self.iconSize.height() + self.minimumHeight() + 1)
                        self.setMinimumWidth(self.iconSize.width() * 4)
                    self.editorImg_.setAutoScaled(True)
                    self.FLWidgetFieldDBLayout.removeWidget(self.pushButtonDB)
                    self.FLWidgetFieldDBLayout.addWidget(self.editorImg_)

                if self.textLabelDB:
                    self.textLabelDB.hide()

                sizePolicy = QtWidgets.QSizePolicy(
                    QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
                )
                # sizePolicy.setHeightForWidth(True)

                if not self.pbAux3_:
                    spcBut = QtWidgets.QSpacerItem(
                        20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
                    )
                    self.lytButtons.addItem(spcBut)
                    self.pbAux3_ = qpushbutton.QPushButton(self)
                    if self.pbAux3_:
                        self.pbAux3_.setSizePolicy(sizePolicy)
                        self.pbAux3_.setMinimumSize(self.iconSize)
                        self.pbAux3_.setFocusPolicy(QtCore.Qt.NoFocus)
                        self.pbAux3_.setIcon(
                            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-open.png"))
                        )
                        self.pbAux3_.setText("")
                        self.pbAux3_.setToolTip("Abrir fichero de imagen")
                        self.pbAux3_.setWhatsThis("Abrir fichero de imagen")
                        self.lytButtons.addWidget(self.pbAux3_)
                        # if self.showed:
                        #    try:
                        #        self.pbAux3_.clicked.disconnect(self.searchPixmap)
                        #    except Exception:
                        #        self.logger.exception("Error al desconectar señal")
                        self.pbAux3_.clicked.connect(self.searchPixmap)
                        if not hasPushButtonDB:
                            if self.showed:
                                try:
                                    self.keyF2Pressed.disconnect(self.pbAux3_.animateClick)
                                except Exception:
                                    self.logger.exception("Error al desconectar señal")
                            try:
                                self.keyF2Pressed.connect(self.pbAux3_.animateClick)
                            except Exception:
                                self.logger.exception("Error al desconectar señal")

                        self.pbAux3_.setFocusPolicy(QtCore.Qt.StrongFocus)
                        self.pbAux3_.installEventFilter(self)

                if not self.pbAux4_:
                    self.pbAux4_ = qpushbutton.QPushButton(self)
                    if self.pbAux4_:
                        self.pbAux4_.setSizePolicy(sizePolicy)
                        self.pbAux4_.setMinimumSize(self.iconSize)
                        self.pbAux4_.setFocusPolicy(QtCore.Qt.NoFocus)
                        self.pbAux4_.setIcon(
                            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-paste.png"))
                        )
                        self.pbAux4_.setText("")
                        self.pbAux4_.setToolTip("Pegar imagen desde el portapapeles")
                        self.pbAux4_.setWhatsThis("Pegar imagen desde el portapapeles")
                        self.lytButtons.addWidget(self.pbAux4_)
                        # if self.showed:
                        #    try:
                        #        self.pbAux4_.clicked.disconnect(self.setPixmapFromClipboard)
                        #    except Exception:
                        #        self.logger.exception("Error al desconectar señal")
                        self.pbAux4_.clicked.connect(self.setPixmapFromClipboard)

                if not self.pbAux_:
                    self.pbAux_ = qpushbutton.QPushButton(self)
                    if self.pbAux_:
                        self.pbAux_.setSizePolicy(sizePolicy)
                        self.pbAux_.setMinimumSize(self.iconSize)
                        self.pbAux_.setFocusPolicy(QtCore.Qt.NoFocus)
                        self.pbAux_.setIcon(
                            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-clear.png"))
                        )
                        self.pbAux_.setText("")
                        self.pbAux_.setToolTip("Borrar imagen")
                        self.pbAux_.setWhatsThis("Borrar imagen")
                        self.lytButtons.addWidget(self.pbAux_)
                        # if self.showed:
                        #    try:
                        #        self.pbAux_.clicked.disconnect(self.clearPixmap)
                        #    except Exception:
                        #        self.logger.exception("Error al desconectar señal")
                        self.pbAux_.clicked.connect(self.clearPixmap)

                if not self.pbAux2_:
                    self.pbAux2_ = qpushbutton.QPushButton(self)
                    if self.pbAux2_:
                        savepixmap_ = QtWidgets.QMenu(self.pbAux2_)
                        savepixmap_.addAction("JPG")
                        savepixmap_.addAction("XPM")
                        savepixmap_.addAction("PNG")
                        savepixmap_.addAction("BMP")

                        self.pbAux2_.setMenu(savepixmap_)
                        self.pbAux2_.setSizePolicy(sizePolicy)
                        self.pbAux2_.setMinimumSize(self.iconSize)
                        self.pbAux2_.setFocusPolicy(QtCore.Qt.NoFocus)
                        self.pbAux2_.setIcon(
                            QtGui.QIcon(utils_base.filedir("./core/images/icons", "gtk-save.png"))
                        )
                        self.pbAux2_.setText("")
                        self.pbAux2_.setToolTip("Guardar imagen como...")
                        self.pbAux2_.setWhatsThis("Guardar imagen como...")
                        self.lytButtons.addWidget(self.pbAux2_)
                        # if self.showed:
                        #    try:
                        #        savepixmap_.triggered.disconnect(self.savePixmap)
                        #    except Exception:
                        #        self.logger.exception("Error al desconectar señal")
                        triggered = cast(QtCore.pyqtSignal, savepixmap_.triggered)
                        triggered.connect(self.savePixmap)

                    if self.pushButtonDB:
                        if hasPushButtonDB:
                            self.pushButtonDB.installEventFilter(self)
                        else:
                            self.pushButtonDB.setDisabled(True)

        elif type_ == "date":
            self.editor_ = fldateedit.FLDateEdit(self, "editor")
            self.editor_.setFont(self.font())
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
            )
            sizePolicy.setHeightForWidth(True)
            self.editor_.setSizePolicy(sizePolicy)
            if self.FLWidgetFieldDBLayout:
                self.FLWidgetFieldDBLayout.insertWidget(1, self.editor_)

            # self.editor_.setOrder(QtGui.QDateEdit.DMY)
            # self.editor_.setAutoAdvance(True)
            # self.editor_.setSeparator("-")
            self.editor_.installEventFilter(self)
            if self.pushButtonDB:
                self.pushButtonDB.hide()

            if not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
                # if not self.pbAux_:
                #    #self.pbAux_ = qpushbutton.QPushButton(self)
                #    # self.pbAux_.setFlat(True)
                #    #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7) ,QtGui.QSizePolicy.Policy(0))
                #    # sizePolicy.setHeightForWidth(True)
                #    # self.pbAux_.setSizePolicy(sizePolicy)
                #    #self.pbAux_.setMinimumSize(25, 25)
                #    #self.pbAux_.setMaximumSize(25, 25)
                #    # self.pbAux_.setFocusPolicy(QtCore.Qt.NoFocus)
                #    # self.pbAux_.setIcon(QtGui.QIcon(utils_base.filedir("./core/images/icons","date.png")))
                #    # self.pbAux_.setText("")
                #    #self.pbAux_.setToolTip("Seleccionar fecha (F2)")
                #    #self.pbAux_.setWhatsThis("Seleccionar fecha (F2)")
                #    # self.lytButtons.addWidget(self.pbAux_) FIXME
                #    # self.FLWidgetFieldDBLayout.addWidget(self.pbAux_)
                #    # if self.showed:
                #        # self.pbAux_.clicked.disconnect(self.toggleDatePicker)
                #        # self.KeyF2Pressed_.disconnect(self.pbAux_.animateClick)
                #    # self.pbAux_.clicked.connect(self.toggleDatePicker)
                #    # self.keyF2Pressed_.connect(self.pbAux_.animateClick) #FIXME
                self.editor_.setCalendarPopup(True)

            if self.showed:
                try:
                    cast(QtCore.pyqtSignal, self.editor_.dateChanged).disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal")

            cast(QtCore.pyqtSignal, self.editor_.dateChanged).connect(self.updateValue)
            if (
                self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Insert
                and not field.allowNull()
            ):
                defVal = field.defaultValue()
                if defVal is None:
                    self.editor_.setDate(QtCore.QDate.currentDate().toString("dd-MM-yyyy"))
                else:
                    self.editor_.setDate(defVal.toDate())

        elif type_ == "time":
            self.editor_ = fltimeedit.FLTimeEdit(self)
            self.editor_.setFont(self.font())
            # self.editor_.setAutoAdvance(True)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
            )
            sizePolicy.setHeightForWidth(True)
            self.editor_.setSizePolicy(sizePolicy)
            if self.FLWidgetFieldDBLayout:
                self.FLWidgetFieldDBLayout.addWidget(self.editor_)
            self.editor_.installEventFilter(self)
            if self.pushButtonDB:
                self.pushButtonDB.hide()
            if self.showed:
                try:
                    cast(QtCore.pyqtSignal, self.editor_.timeChanged).disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal")

            cast(QtCore.pyqtSignal, self.editor_.timeChanged).connect(self.updateValue)
            if (
                self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Insert
                and not field.allowNull()
            ):
                defVal = field.defaultValue()
                # if not defVal.isValid() or defVal.isNull():
                if defVal is None:
                    self.editor_.setTime(QtCore.QTime.currentTime())
                else:
                    self.editor_.setTime(defVal.toTime())

        elif type_ == "stringlist":

            self.editor_ = qtextedit.QTextEdit(self)
            self.editor_.setFont(self.font())
            self.editor_.setTabChangesFocus(True)
            self.setMinimumHeight(100)
            # self.editor_.setMinimumHeight(100)
            # self.editor_.setMaximumHeight(120)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding
            )
            sizePolicy.setHeightForWidth(True)
            self.editor_.setSizePolicy(sizePolicy)
            # ted.setTexFormat(self.textFormat_)
            # if isinstance(self.textFormat_, QtCore.Qt.RichText) and not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
            # self.FLWidgetFieldDBLayout.setDirection(QtGui.QBoxLayout.Down)
            # self.FLWidgetFieldDBLayout.remove(self.textLabelDB)
            # textEditTab_ = AQTextEditBar(self, "extEditTab_", self.textLabelDB) #FIXME
            # textEditTab_.doConnections(ted)
            # self.FLWidgetFieldDBLayout.addWidget(textEditTab_)
            # self.setMinimumHeight(120)
            if self.FLWidgetFieldDBLayout:
                self.FLWidgetFieldDBLayout.addWidget(self.editor_)
            # verticalSpacer = QtWidgets.QSpacerItem(
            #    20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            # )
            # self.FLLayoutH.addItem(verticalSpacer)
            self.editor_.installEventFilter(self)

            if self.showed:
                try:
                    cast(QtCore.pyqtSignal, self.editor_.textChanged).disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal")

            cast(QtCore.pyqtSignal, self.editor_.textChanged).connect(self.updateValue)

            self.keyF4Pressed.connect(self.toggleAutoCompletion)
            if self.autoCompMode_ == "OnDemandF4":
                self.editor_.setToolTip("Para completado automático pulsar F4")
                self.editor_.setWhatsThis("Para completado automático pulsar F4")
            elif self.autoCompMode_ == "AlwaysAuto":
                self.editor_.setToolTip("Completado automático permanente activado")
                self.editor_.setWhatsThis("Completado automático permanente activado")
            else:
                self.editor_.setToolTip("Completado automático desactivado")
                self.editor_.setWhatsThis("Completado automático desactivado")

        elif type_ == "bool":

            alias = tMD.fieldNameToAlias(self.fieldName_)
            if not alias:
                raise Exception("alias is empty!")

            self.editor_ = flcheckbox.FLCheckBox(self)
            # self.editor_.setName("editor")
            self.editor_.setText(alias)
            self.editor_.setFont(self.font())
            self.editor_.installEventFilter(self)

            self.editor_.setMinimumWidth(
                self.fontMetrics().width(alias) + self.fontMetrics().maxWidth() * 2
            )
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy(7), QtWidgets.QSizePolicy.Policy(0)
            )
            sizePolicy.setHeightForWidth(True)
            self.editor_.setSizePolicy(sizePolicy)
            if self.FLWidgetFieldDBLayout:
                self.FLWidgetFieldDBLayout.addWidget(self.editor_)

            if self.showed:
                try:
                    self.editor_.toggled.disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal")
            self.editor_.toggled.connect(self.updateValue)

        if hasattr(self, "editor_"):
            self.editor_.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.setFocusProxy(self.editor_)

            if hasPushButtonDB:
                if self.pushButtonDB:
                    self.setTabOrder(self.pushButtonDB, self.editor_)
                    self.pushButtonDB.setFocusPolicy(QtCore.Qt.NoFocus)
                self.editor_.setToolTip("Para buscar un valor en la tabla relacionada pulsar F2")
                self.editor_.setWhatsThis("Para buscar un valor en la tabla relacionada pulsar F2")

        elif hasattr(self, "editorImg_"):
            self.editorImg_.setFocusPolicy(QtCore.Qt.NoFocus)
            if hasPushButtonDB:
                if self.pushButtonDB:
                    self.pushButtonDB.setFocusPolicy(QtCore.Qt.StrongFocus)

        if not hasPushButtonDB:
            if self.pushButtonDB:
                self.pushButtonDB.hide()

        if self.initMaxSize_.width() < 80:
            self.setShowEditor(False)
        else:
            self.setShowEditor(self.showEditor_)

        if self._refreshLaterEditor is not None:
            self.refresh(self._refreshLaterEditor)
            self._refreshLaterEditor = None

    def initEditorControlForNumber(
        self,
        has_option_list: bool,
        field,
        type_,
        partDecimal,
        partInteger,
        len_,
        rX,
        hasPushButtonDB,
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
            self.editor_.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            self.editor_.setMinimumSize(self.iconSize)
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

            olTranslated = []
            olNoTranslated = field.optionsList()
            for olN in olNoTranslated:
                olTranslated.append(olN)
            self.editor_.addItems(olTranslated)
            self.editor_.installEventFilter(self)
            if self.showed:
                try:
                    cast(QtCore.pyqtSignal, self.editor_.activated).disconnect(self.updateValue)
                except Exception:
                    self.logger.exception("Error al desconectar señal")
            cast(QtCore.pyqtSignal, self.editor_.activated).connect(self.updateValue)

        else:

            self.editor_ = fllineedit.FLLineEdit(self, "editor")
            self.editor_.setFont(self.font())
            if self.iconSize and self.font().pointSize() < 10:
                self.editor_.setMinimumSize(self.iconSize)
                self.editor_.setMaximumHeight(self.iconSize.height())

            self.editor_._tipo = type_
            self.editor_._part_decimal = partDecimal
            if not self.cursor_.modeAccess() == pnsqlcursor.PNSqlCursor.Browse:
                if not field.allowNull() and field.editable() and type_ not in ("time", "date"):
                    # self.editor_.palette().setColor(self.editor_.backgroundRole(), self.notNullColor())
                    self.editor_.setStyleSheet(
                        "background-color:%s; color:%s"
                        % (self.notNullColor(), QtGui.QColor(QtCore.Qt.black).name())
                    )
                self.editor_.installEventFilter(self)

            if type_ == "double":

                self.editor_.setValidator(
                    fldoublevalidator.FLDoubleValidator(
                        ((pow(10, partInteger) - 1) * -1),
                        pow(10, partInteger) - 1,
                        self.editor_._part_decimal,
                        self.editor_,
                    )
                )
                self.editor_.setAlignment(QtCore.Qt.AlignRight)
            else:
                if type_ == "uint":

                    self.editor_.setValidator(
                        fluintvalidator.FLUIntValidator(0, pow(10, partInteger), self.editor_)
                    )
                    pass
                elif type_ == "int":

                    self.editor_.setValidator(
                        flintvalidator.FLIntValidator(
                            ((pow(10, partInteger) - 1) * -1),
                            pow(10, partInteger) - 1,
                            self.editor_,
                        )
                    )
                    self.editor_.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.editor_.setMaxValue(len_)
                    if rX:
                        self.editor_.setValidator(
                            QtGui.QRegExpValidator(QtCore.QRegExp(rX), self.editor_)
                        )

                    self.editor_.setAlignment(QtCore.Qt.AlignLeft)

                    self.keyF4Pressed.connect(self.toggleAutoCompletion)
                    if self.autoCompMode_ == "OnDemandF4":
                        self.editor_.setToolTip("Para completado automático pulsar F4")
                        self.editor_.setWhatsThis("Para completado automático pulsar F4")
                    elif self.autoCompMode_ == "AlwaysAuto":
                        self.editor_.setToolTip("Completado automático permanente activado")
                        self.editor_.setWhatsThis("Completado automático permanente activado")
                    else:
                        self.editor_.setToolTip("Completado automático desactivado")
                        self.editor_.setWhatsThis("Completado automático desactivado")

            self.editor_.installEventFilter(self)

            if self.showed:
                try:
                    self.editor_.lostFocus.disconnect(self.emitLostFocus)
                    self.editor_.textChanged.disconnect(self.updateValue)
                    self.editor_.textChanged.disconnect(self.emitTextChanged)
                except Exception:
                    self.logger.exception("Error al desconectar señal")

            self.editor_.lostFocus.connect(self.emitLostFocus)
            self.editor_.textChanged.connect(self.updateValue)
            self.editor_.textChanged.connect(self.emitTextChanged)

            if hasPushButtonDB and self.pushButtonDB:
                if self.showed:
                    try:
                        self.keyF2Pressed.disconnect(self.pushButtonDB.animateClick)
                        self.labelClicked.disconnect(self.openFormRecordRelation)
                    except Exception:
                        self.logger.exception("Error al desconectar señal")

                self.keyF2Pressed.connect(self.pushButtonDB.animateClick)  # FIXME
                self.labelClicked.connect(self.openFormRecordRelation)
                if not self.textLabelDB:
                    raise ValueError("textLabelDB is not defined!")

                self.textLabelDB.installEventFilter(self)
                tlf = self.textLabelDB.font()
                tlf.setUnderline(True)
                self.textLabelDB.setFont(tlf)
                cB = QtGui.QColor(QtCore.Qt.darkBlue)
                # self.textLabelDB.palette().setColor(self.textLabelDB.foregroundRole(), cB)
                self.textLabelDB.setStyleSheet("color:" + cB.name())
                self.textLabelDB.setCursor(QtCore.Qt.PointingHandCursor)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy(7), QtWidgets.QSizePolicy.Policy(0)
        )
        sizePolicy.setHeightForWidth(True)
        self.editor_.setSizePolicy(sizePolicy)
        if self.FLWidgetFieldDBLayout is not None:
            self.FLWidgetFieldDBLayout.addWidget(self.pushButtonDB)
            self.FLWidgetFieldDBLayout.addWidget(self.editor_)

    def clearPixmap(self) -> None:
        """
        Delete image in Pixmap type fields.
        """
        if self.editorImg_:
            self.editorImg_.clear()
            if self.cursor_ is None:
                raise Exception("cursor_ is empty!.")

            self.cursor_.setValueBuffer(self.fieldName_, None)

    @decorators.pyqtSlot(QtWidgets.QAction)
    def savePixmap(self, f: QtWidgets.QAction) -> None:
        """
        Save image in Pixmap type fields.

        @param fmt Indicates the format in which to save the image
        """
        if self.editorImg_:
            ext = f.text().lower()
            filename = "imagen.%s" % ext
            ext = "*.%s" % ext
            util = flutil.FLUtil()
            savefilename = QtWidgets.QFileDialog.getSaveFileName(
                self, util.translate("Pineboo", "Guardar imagen como"), filename, ext
            )
            if savefilename:
                pix = QtGui.QPixmap(self.editorImg_.pixmap())
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                if pix:
                    if not pix.save(savefilename[0]):
                        QtWidgets.QMessageBox.warning(
                            self,
                            util.translate("Pineboo", "Error"),
                            util.translate("Pineboo", "Error guardando fichero"),
                        )

            QtWidgets.QApplication.restoreOverrideCursor()

    @decorators.pyqtSlot()
    def toggleAutoCompletion(self) -> None:
        """
        Show / Hide the auto-completion wizard.
        """
        if self.autoCompMode_ == "NeverAuto":
            return

        if not self.autoComFrame_ and self.cursor_ is not None:
            self.autoComFrame_ = QtWidgets.QWidget(self, QtCore.Qt.Popup)
            lay = QtWidgets.QVBoxLayout()
            self.autoComFrame_.setLayout(lay)
            self.autoComFrame_.setWindowTitle("autoComFrame")
            # self.autoComFrame_->setFrameStyle(QFrame::PopupPanel | QFrame::Raised);
            # self.autoComFrame_->setLineWidth(1);
            self.autoComFrame_.hide()

            if not self.autoComPopup_:
                tMD = self.cursor_.metadata()
                field = tMD.field(self.fieldName_) if tMD else None

                if field is not None:
                    self.autoComPopup_ = fldatatable.FLDataTable(None, "autoComPopup", True)
                    lay.addWidget(self.autoComPopup_)
                    cur: Optional["isqlcursor.ISqlCursor"] = None
                    field_relation = field.relationM1()

                    if field_relation is None:
                        if self.fieldRelation_ is not None and self.foreignField_ is not None:
                            self.autoComFieldName_ = self.foreignField_

                            fRel = tMD.field(self.fieldRelation_) if tMD else None

                            if fRel is None:
                                return

                            field_relation_frel = fRel.relationM1()

                            if field_relation_frel is None:
                                raise Exception("fRel.relationM1 is empty!.")

                            self.autoComFieldRelation_ = field_relation_frel.foreignField()
                            cur = pnsqlcursor.PNSqlCursor(
                                field_relation_frel.foreignTable(),
                                False,
                                self.cursor_.db().connectionName(),
                                None,
                                None,
                                self.autoComFrame_,
                            )
                            tMD = cur.metadata()
                            field = tMD.field(self.autoComFieldName_) if tMD else field
                        else:
                            self.autoComFieldName_ = self.fieldName_
                            self.autoComFieldRelation_ = None
                            cur = pnsqlcursor.PNSqlCursor(
                                tMD.name(),
                                False,
                                self.cursor_.db().connectionName(),
                                None,
                                None,
                                self.autoComFrame_,
                            )

                    else:

                        self.autoComFieldName_ = field_relation.foreignField()
                        self.autoComFieldRelation_ = None
                        cur = pnsqlcursor.PNSqlCursor(
                            field_relation.foreignTable(),
                            False,
                            self.cursor_.db().connectionName(),
                            None,
                            None,
                            self.autoComFrame_,
                        )
                        tMD = cur.metadata()
                        field = tMD.field(self.autoComFieldName_) if tMD else field

                    # Añade campo al cursor ...    FIXME!!
                    # cur.append(self.autoComFieldName_, field.type(), -1, field.length(), -1)

                    # for fieldNames in tMD.fieldNames().split(","):
                    #    field = tMD.field(fieldNames)
                    #    if field:
                    # cur.append(field.name(), field.type(), -1, field.length(), -1,
                    # "Variant", None, True) #qvariant,0,true

                    if self.autoComFieldRelation_ is not None and self.topWidget_:
                        list1 = cast(List[FLFieldDB], self.topWidget_.findChildren(FLFieldDB))
                        for itf in list1:
                            if itf.fieldName() == self.autoComFieldRelation_:
                                filter = itf.filter()
                                if filter is not None:
                                    cur.setMainFilter(filter)
                                break

                    self.autoComPopup_.setFLSqlCursor(cur)
                    # FIXME
                    # self.autoComPopup_.setTopMargin(0)
                    # self.autoComPopup_.setLeftMargin(0)
                    self.autoComPopup_.horizontalHeader().hide()
                    self.autoComPopup_.verticalHeader().hide()

                    cur.newBuffer.connect(self.autoCompletionUpdateValue)
                    self.autoComPopup_.recordChoosed.connect(self.autoCompletionUpdateValue)

        if self.autoComPopup_:
            cur = cast(pnsqlcursor.PNSqlCursor, self.autoComPopup_.cursor())
            if cur is None:
                raise Exception("Unexpected: No cursor could be obtained")
            tMD = cur.metadata()
            field = tMD.field(self.autoComFieldName_) if tMD else None

            if field:
                filter_ = (
                    self.cursor()
                    .db()
                    .connManager()
                    .manager()
                    .formatAssignValueLike(field, self.value(), True)
                )
                self.autoComPopup_.setFilter(filter_)
                self.autoComPopup_.setSort("%s ASC" % self.autoComFieldName_)
                self.autoComPopup_.refresh()

            if self.autoComFrame_ is None:
                raise Exception("autoComFrame_ is empty")

            if not self.autoComFrame_.isVisible() and cur.size() > 1:
                tmpPoint = None
                if self.showAlias_ and self.textLabelDB:
                    tmpPoint = self.mapToGlobal(self.textLabelDB.geometry().bottomLeft())
                elif self.pushButtonDB and not self.pushButtonDB.isHidden():
                    tmpPoint = self.mapToGlobal(self.pushButtonDB.geometry().bottomLeft())
                else:
                    tmpPoint = self.mapToGlobal(self.editor_.geometry().bottomLeft())

                frameWidth = self.width()
                if frameWidth < self.autoComPopup_.width():
                    frameWidth = self.autoComPopup_.width()

                if frameWidth < self.autoComFrame_.width():
                    frameWidth = self.autoComFrame_.width()

                self.autoComFrame_.setGeometry(tmpPoint.x(), tmpPoint.y(), frameWidth, 300)
                self.autoComFrame_.show()
                self.autoComFrame_.setFocus()
            elif self.autoComFrame_.isVisible() and cur.size() == 1:
                self.autoComFrame_.hide()

            cur.first()
            del cur

    def autoCompletionUpdateValue(self) -> None:
        """
        Update the value of the field from the content that offers the auto completion wizard.
        """
        if not self.autoComPopup_ or not self.autoComFrame_:
            return

        cur = cast(pnsqlcursor.PNSqlCursor, self.autoComPopup_.cursor())
        if not cur or not cur.isValid():
            return

        if isinstance(self.sender(), fldatatable.FLDataTable):
            self.setValue(cur.valueBuffer(self.autoComFieldName_))
            self.autoComFrame_.hide()
            # ifdef Q_OS_WIN32
            # if (editor_)
            #    editor_->releaseKeyboard();
            # if (autoComPopup_)
            #    autoComPopup_->releaseKeyboard();
            # endif
        elif isinstance(self.editor_, qtextedit.QTextEdit):
            self.setValue(self.autoComFieldName_)
        else:
            ed = cast(qlineedit.QLineEdit, self.editor_)
            if self.autoComFrame_.isVisible() and not ed.hasFocus():
                if not self.autoComPopup_.hasFocus():
                    cval = str(cur.valueBuffer(self.autoComFieldName_))
                    val = ed.text
                    ed.autoSelect = False
                    ed.setText(cval)
                    ed.setFocus()
                    ed.setCursorPosition(len(cval))
                    ed.cursorBackward(True, len(cval) - len(val))
                    # ifdef Q_OS_WIN32
                    # ed->grabKeyboard();
                    # endif
                else:
                    self.setValue(cur.valueBuffer(self.autoComFieldName_))

            elif not self.autoComFrame_.isVisible():
                cval = str(cur.valueBuffer(self.autoComFieldName_))
                val = ed.text
                ed.autoSelect = False
                ed.setText(cval)
                ed.setFocus()
                ed.setCursorPosition(len(cval))
                ed.cursorBackward(True, len(cval) - len(val))

        if self.autoComFieldRelation_ is not None and not self.autoComFrame_.isVisible():
            if self.cursor_ is not None and self.fieldRelation_ is not None:
                self.cursor_.setValueBuffer(
                    self.fieldRelation_, cur.valueBuffer(self.autoComFieldRelation_)
                )

    @decorators.pyqtSlot()
    def openFormRecordRelation(self) -> None:
        """
        Open an edit form for the value selected in its corresponding action.
        """
        if not self.cursor_:
            return

        if not self.fieldName_:
            return

        tMD = self.cursor_.metadata()
        if not tMD:
            return

        field = tMD.field(self.fieldName_)
        if field is None:
            return

        field_relation = field.relationM1()

        if field_relation is None:
            self.logger.info("FLFieldDB : El campo de búsqueda debe tener una relación M1")
            return

        fMD = field.associatedField()
        a = None
        v = self.cursor_.valueBuffer(field.name())
        if v in [None, ""] or (fMD is not None and self.cursor_.bufferIsNull(fMD.name())):
            QtWidgets.QMessageBox.warning(
                QtWidgets.QApplication.focusWidget(),
                "Aviso",
                "Debe indicar un valor para %s" % field.alias(),
                QtWidgets.QMessageBox.Ok,
            )
            return

        self.cursor_.db().connManager().manager()
        c = pnsqlcursor.PNSqlCursor(
            field_relation.foreignTable(), True, self.cursor_.db().connectionName()
        )
        # c = pnsqlcursor.PNSqlCursor(field.relationM1().foreignTable())
        c.select(
            self.cursor_.db()
            .connManager()
            .manager()
            .formatAssignValue(field_relation.foreignField(), field, v, True)
        )
        # if c.size() <= 0:
        #    return

        if c.size() <= 0:
            return

        c.next()

        if self.actionName_:
            a = self.actionName_
            if a is None:
                raise Exception("action is empty!")
            c.setAction(a)

        self.modeAccess = self.cursor_.modeAccess()
        if (
            self.modeAccess == pnsqlcursor.PNSqlCursor.Insert
            or self.modeAccess == pnsqlcursor.PNSqlCursor.Del
        ):
            self.modeAccess = pnsqlcursor.PNSqlCursor.Edit

        c.openFormInMode(self.modeAccess, False)

    @decorators.pyqtSlot()
    @decorators.pyqtSlot(int)
    def searchValue(self) -> None:
        """
        Open a dialog to search the related table.
        """
        if not self.cursor_:
            return

        if not self.fieldName_:
            return
        tMD = self.cursor_.metadata()
        if not tMD:
            return

        field = tMD.field(self.fieldName_)
        if field is None:
            return

        field_relation = field.relationM1()

        if not field_relation:
            self.logger.info("FLFieldDB : El campo de búsqueda debe tener una relación M1")
            return

        fMD = field.associatedField()

        form_search: flformsearchdb.FLFormSearchDB

        if fMD is not None:
            fmd_relation = fMD.relationM1()

            if fmd_relation is None:
                self.logger.info("FLFieldDB : El campo asociado debe tener una relación M1")
                return
            v = self.cursor_.valueBuffer(fMD.name())
            if v is None or self.cursor_.bufferIsNull(fMD.name()):
                QtWidgets.QMessageBox.warning(
                    QtWidgets.QApplication.focusWidget(),
                    "Aviso",
                    "Debe indicar un valor para %s" % fMD.alias(),
                )
                return

            mng = self.cursor_.db().connManager().manager()
            c = pnsqlcursor.PNSqlCursor(
                fmd_relation.foreignTable(), True, self.cursor_.db().connectionName()
            )
            c.select(mng.formatAssignValue(fmd_relation.foreignField(), fMD, v, True))
            if c.size() > 0:
                c.first()

            c2 = pnsqlcursor.PNSqlCursor(
                field_relation.foreignTable(),
                True,
                self.cursor_.db().connectionName(),
                c,
                fmd_relation,
            )

            # if self.actionName_ is None:
            #    a = mng.action(field.relationM1().foreignTable())
            # else:
            #    a = mng.action(self.actionName_)
            #    if not a:
            #        return
            #    a.setTable(field.relationM1().foreignField())

            form_search = flformsearchdb.FLFormSearchDB(c2, self.topWidget_)

            form_search.setFilter(mng.formatAssignValue(fmd_relation.foreignField(), fMD, v, True))
        else:
            mng = self.cursor_.db().connManager().manager()
            if not self.actionName_:
                a = mng.action(field_relation.foreignTable())
                if not a:
                    return
            else:
                a = mng.action(self.actionName_)
                if not a:
                    return
                a.setTable(field_relation.foreignTable())
            c = pnsqlcursor.PNSqlCursor(a.table(), True, self.cursor_.db().connectionName())
            # f = flformsearchdb.FLFormSearchDB(c, a.name(), self.topWidget_)
            form_search = flformsearchdb.FLFormSearchDB(c, self.topWidget_)

        form_search.setMainWidget()

        list_objs = form_search.findChildren(fltabledb.FLTableDB)
        obj_tdb = None

        if list_objs:
            obj_tdb = cast(fltabledb.FLTableDB, list_objs[0])
        if fMD is not None and obj_tdb is not None:
            # obj_tdb.setTableName(field.relationM1().foreignTable())
            # obj_tdb.setFieldRelation(field.associatedFieldFilterTo())
            # obj_tdb.setForeignField(fMD.relationM1().foreignField())
            if fmd_relation is not None:
                if fmd_relation.foreignTable() == tMD.name():
                    obj_tdb.setReadOnly(True)

        if self.filter_:
            form_search.setFilter(self.filter_)
        if form_search.mainWidget():
            if obj_tdb:
                cur_value = self.value()
                if field.type() == "string" and cur_value:
                    obj_tdb.setInitSearch(cur_value)
                    obj_tdb.putFirstCol(field_relation.foreignField())

                QtCore.QTimer.singleShot(0, obj_tdb.lineEditSearch.setFocus)

        v = form_search.exec_(field_relation.foreignField())
        form_search.close()
        if c:
            del c
        if v:
            # self.setValue("")
            self.setValue(v)

    @decorators.pyqtSlot()
    def searchPixmap(self) -> None:
        """
        Open a dialog to search for an image file.

        If the field is not of the Pixmap type it does nothing.
        """
        if not self.cursor_ or not self.editorImg_:
            return

        if not self.fieldName_:
            return

        table_metadata = self.cursor_.metadata()
        if not table_metadata:
            return

        field = table_metadata.field(self.fieldName_)

        if field is None:
            return
        util = flutil.FLUtil()
        if field.type() == "pixmap":
            fd = QtWidgets.QFileDialog(
                self.parentWidget(), util.translate("pineboo", "Elegir archivo"), "", "*"
            )
            fd.setViewMode(QtWidgets.QFileDialog.Detail)
            filename = None
            if fd.exec_() == QtWidgets.QDialog.Accepted:
                filename = fd.selectedFiles()

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

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        pix = QtGui.QPixmap()
        buffer = QtCore.QBuffer()

        if img.width() <= self.maxPixImages_ and img.height() <= self.maxPixImages_:
            pix.convertFromImage(img)
        else:
            newWidth = 0
            newHeight = 0
            if img.width() < img.height():
                newHeight = self.maxPixImages_
                newWidth = round(newHeight * img.width() / img.height())
            else:
                newWidth = self.maxPixImages_
                newHeight = round(newWidth * img.height() / img.width())
            pix.convertFromImage(img.scaled(newWidth, newHeight))

        QtWidgets.QApplication.restoreOverrideCursor()

        if not pix:
            return

        if self.editorImg_ is None:
            raise Exception("editorImg_ is empty!")

        self.editorImg_.setPixmap(pix)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        buffer.open(QtCore.QBuffer.ReadWrite)
        pix.save(buffer, "XPM")

        QtWidgets.QApplication.restoreOverrideCursor()

        if not buffer:
            return

        s = buffer.data().data().decode("utf8")

        if s.find("*dummy") > -1:
            s = s.replace(
                "*dummy",
                "%s_%s_%s"
                % (
                    self.cursor().metadata().name(),
                    self.fieldName_,
                    QtCore.QDateTime().currentDateTime().toString("ddhhmmssz"),
                ),
            )
        self.updateValue(s)

    def setPixmapFromPixmap(self, pixmap: QtGui.QPixmap, w: int = 0, h: int = 0) -> None:
        """
        Set an image into the pixmap type field with the preferred width and height.

        @param pixmap: pixmap to load in the field
        @param w: preferred width of the image
        @param h: preferred height of the image
        @author Silix
        """

        if pixmap.isNull():
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        pix = QtGui.QPixmap()
        buffer = QtCore.QBuffer()

        img = pixmap.toImage()

        if w and h:
            pix.convertFromImage(img.scaled(w, h))
        else:
            pix.convertFromImage(img)

        QtWidgets.QApplication.restoreOverrideCursor()
        if not pix:
            return

        if self.editorImg_ is None:
            raise Exception("editorImg_ is empty!")

        self.editorImg_.setPixmap(pix)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        buffer.open(QtCore.QBuffer.ReadWrite)
        pix.save(buffer, "XPM")

        QtWidgets.QApplication.restoreOverrideCursor()

        if not buffer:
            return
        s = None

        s = buffer.data().data().decode("utf8")

        # if not QtGui.QPixmapCache.find(s.left(100)):
        #    QtGui.QPixmapCache.insert(s.left(100), pix)
        self.updateValue(s)

    @decorators.pyqtSlot(bool)
    def setPixmapFromClipboard(self) -> None:
        """
        Upload an image from the clipboard into the pixmap type field.

        @author Silix
        """
        clb = QtWidgets.QApplication.clipboard()
        img = clb.image()

        if not isinstance(img, QtGui.QImage):
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        pix = QtGui.QPixmap()
        buffer = QtCore.QBuffer()

        if img.width() <= self.maxPixImages_ and img.height() <= self.maxPixImages_:
            pix.convertFromImage(img)
        else:
            newWidth = 0
            newHeight = 0
            if img.width() < img.height():
                newHeight = self.maxPixImages_
                newWidth = round(newHeight * img.width() / img.height())
            else:
                newWidth = self.maxPixImages_
                newHeight = round(newWidth * img.height() / img.width())

            pix.convertFromImage(img.scaled(newWidth, newHeight))

        QtWidgets.QApplication.restoreOverrideCursor()

        if not pix:
            return

        if self.editorImg_ is None:
            raise Exception("editorImg_ is empty!")

        self.editorImg_.setPixmap(pix)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        buffer.open(QtCore.QBuffer.ReadWrite)
        pix.save(buffer, "XPM")

        QtWidgets.QApplication.restoreOverrideCursor()

        if not buffer:
            return

        s = buffer.data().data().decode("utf8")

        # if not QtGui.QPixmapCache.find(s.left(100)):
        #    QtGui.QPixmapCache.insert(s.left(100), pix)
        self.updateValue(s)

    @decorators.NotImplementedWarn
    def pixmap(self) -> QtGui.QPixmap:
        """
        Return the image object associated with the field.

        @return image associated to the field.
        @author Silix
        """
        pix = QtGui.QPixmap()
        pix.loadFromData(self.value().toCString())
        return pix

    def emitLostFocus(self) -> None:
        """
        Emit the lost focus signal.
        """
        self.lostFocus.emit()

    @decorators.pyqtSlot()
    def setNoShowed(self) -> None:
        """Set the control is not shown."""

        if self.foreignField_ and self.fieldRelation_:
            self.showed = False
            if self.isVisible():
                self.showWidget()

    @decorators.pyqtSlot(str)
    def setMapValue(self, v: Optional[str] = None) -> None:
        """
        Set the value of this field based on the result of the query.

        Whose clause 'where' is; field name of the object that sends the same signal
        to the value indicated as parameter.

        Only FLFielDB type objects can be connected, and their normal use is to connect
        the FLFieldDB :: textChanged (cons QString &) signal to this slot.

        @param v Value
        """

        if v is not None:
            self.field_map_value_ = cast(FLFieldDB, self.sender())
            self.mapValue_ = v
            self.setMapValue()
        else:
            if not self.field_map_value_:
                return

            if not self.cursor_:
                return

            tMD = self.cursor_.metadata()
            if not tMD:
                return

            fSN = self.field_map_value_.fieldName()
            field = tMD.field(self.fieldName_)
            fieldSender = tMD.field(fSN)

            if field is None or not fieldSender:
                return

            field_relation = field.relationM1()

            if field_relation is not None:
                if not field_relation.foreignTable() == tMD.name():
                    mng = self.cursor_.db().connManager().manager()
                    relation_table = field_relation.foreignTable()
                    foreign_field = self.field_map_value_.foreignField()
                    if foreign_field is None:
                        raise Exception("foreign field not found.")

                    q = pnsqlquery.PNSqlQuery(None, self.cursor_.db().connectionName())
                    q.setForwardOnly(True)
                    q.setTablesList(relation_table)
                    q.setSelect("%s,%s" % (field_relation.foreignField(), foreign_field))
                    q.setFrom(relation_table)

                    where = mng.formatAssignValue(foreign_field, fieldSender, self.mapValue_, True)
                    assocTmd = mng.metadata(relation_table)
                    filterAc = self.cursor_.filterAssoc(foreign_field, assocTmd)
                    if assocTmd and not assocTmd.inCache():
                        del assocTmd

                    if filterAc:
                        if not where:
                            where = filterAc
                        else:
                            where = "%s AND %s" % (where, filterAc)

                    if not self.filter_:
                        q.setWhere(where)
                    else:
                        q.setWhere("%s AND %s" % (self.filter_, where))

                    if q.exec_() and q.next():
                        # self.setValue("")
                        self.setValue(q.value(0))

    @decorators.pyqtSlot()
    def emitKeyF2Pressed(self) -> None:
        """
        Emit the keyF2Pressed signal.

        The publisher's key_F2_Pressed signal (only if the editor is fllineedit.FLLineEdit)
        It is connected to this slot.
        """
        self.keyF2Pressed.emit()

    @decorators.pyqtSlot()
    def emitLabelClicked(self) -> None:
        """
        Emit the labelClicked signal. It is used in the M1 fields to edit the edition form of the selected value.
        """
        self.labelClicked.emit()

    @decorators.pyqtSlot(str)
    def emitTextChanged(self, t: str) -> None:
        """
        Emit the textChanged signal.

        The textChanged signal from the editor (only if the editor is fllineedit.FLLineEdit)
        It is connected to this slot.
        """
        self.textChanged.emit(t)

    # @decorators.pyqtSlot(int)
    # def ActivatedAccel(self, identifier: int) -> None:
    #    """
    #    Emit the activatedAccel (int) signal.
    #    """
    #    if self.editor_ and self.editor_.hasFocus:
    #        self.accel_.activated.emit(identifier)

    def setDisabled(self, disable: bool) -> None:
        """Set if the control is disbled."""
        self.setEnabled(not disable)
        self.setKeepDisabled(disable)

    def setEnabled(self, enable: bool) -> None:
        """Set if the control is enabled."""

        # print("FLFieldDB: %r setEnabled: %r" % (self.fieldName_, enable))

        if hasattr(self, "editor_"):
            if self.cursor_ is None:
                self.editor_.setDisabled(True)
                self.editor_.setStyleSheet("background-color: #f0f0f0")
            else:

                read_only = getattr(self.editor_, "setReadOnly", None)

                if read_only is not None:
                    tMD = self.cursor_.metadata()
                    field = tMD.field(self.fieldName_)

                    if field is None:
                        raise Exception("field is empty!.")

                    read_only(not enable)
                    if not enable or not field.editable():
                        self.editor_.setStyleSheet("background-color: #f0f0f0")
                    else:
                        if (
                            not field.allowNull()
                            and not (field.type() in ["date", "time"])
                            and (self.cursor_ and self.cursor_.modeAccess() != self.cursor_.Browse)
                        ):
                            if not isinstance(self.editor_, qcombobox.QComboBox):
                                self.editor_.setStyleSheet(
                                    "background-color:%s; color:%s"
                                    % (self.notNullColor(), QtGui.QColor(QtCore.Qt.black).name())
                                )
                            else:
                                self.editor_.setEditable(False)
                                self.editor_.setStyleSheet(self.styleSheet())
                        else:
                            self.editor_.setStyleSheet(self.styleSheet())

                else:
                    self.editor_.setEnabled(enable)
        if self.pushButtonDB:
            self.pushButtonDB.setEnabled(enable)
        return  # Mirar esto!! FIXME
        if enable:
            self.setAttribute(QtCore.Qt.WA_ForceDisabled, False)
        else:
            self.setAttribute(QtCore.Qt.WA_ForceDisabled, True)

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
                    for w in self.children():
                        if not w.testAttribute(QtCore.Qt.WA_ForceDisabled):
                            le = w
                            if isinstance(le, qlineedit.QLineEdit):
                                allowNull = True
                                tMD = self.cursor_.metadata()
                                if tMD:
                                    field = tMD.field(self.fieldName_)
                                    if field and not field.allowNull():
                                        allowNull = False

                                if allowNull:
                                    cBg = QtGui.QColor.blue()
                                    cBg = (
                                        QtWidgets.QApplication()
                                        .palette()
                                        .color(QtGui.QPalette.Active, QtGui.QPalette.Base)
                                    )
                                else:
                                    cBg = self.NotNullColor()

                                le.setDisabled(False)
                                le.setReadOnly(False)
                                le.palette().setColor(QtGui.QPalette.Base, cBg)
                                le.setCursor(QtCore.Qt.IBeamCursor)
                                le.setFocusPolicy(QtCore.Qt.StrongFocus)
                                continue
                            w.setEnabled(True)

            else:
                if not self.testAttribute(QtCore.Qt.WA_Disabled):
                    if self.focusWidget() == self:
                        parentIsEnabled = False
                        if not self.parentWidget() or self.parentWidget().isEnabled():
                            parentIsEnabled = True
                        if not parentIsEnabled or not self.focusNextPrevChild(True):
                            self.clearFocus()
                    self.setAttribute(QtCore.Qt.WA_Disabled)
                    self.enabledChange(not enable)

                    if self.children():
                        for w in self.children():
                            if isinstance(w, qlineedit.QLineEdit):
                                le = w
                                if le:
                                    le.setDisabled(False)
                                    le.setReadOnly(True)
                                    le.setCursor(QtCore.Qt.IBeamCursor)
                                    le.setFocusPolicy(QtCore.Qt.NoFocus)
                                    continue

                            if isinstance(w, qtextedit.QTextEdit):
                                te = w
                                te.setDisabled(False)
                                te.setReadOnly(True)
                                te.viewPort().setCursor(QtCore.Qt.IBeamCursor)
                                te.setFocusPolicy(QtCore.Qt.NoFocus)
                                continue

                            if w == self.textLabelDB and self.pushButtonDB:
                                w.setDisabled(False)
                                continue

                            w.setEnabled(False)
                            w.setAttribute(QtCore.Qt.WA_ForceDisabled, False)

    def showEvent(self, e: Any) -> None:
        """Process event show."""
        self.load()
        if self._loaded:
            self.showWidget()
        super(FLFieldDB, self).showEvent(e)

    def showWidget(self) -> None:
        """
        Show the widget.
        """
        if self._loaded:
            if not self.showed:
                if self.topWidget_:
                    self.showed = True
                    if not self.firstRefresh:
                        self.refresh()
                        self.firstRefresh = True

                    # if self.cursorAux:
                    # print("Cursor auxiliar a ", self.tableName_)
                    if (
                        self.cursorAux
                        and self.cursor_
                        and self.cursor_.bufferIsNull(self.fieldName_)
                    ):

                        if (
                            self.foreignField_ is not None
                            and self.fieldRelation_ is not None
                            and not self.cursorAux.bufferIsNull(self.foreignField_)
                        ):
                            mng = self.cursor_.db().connManager().manager()
                            tMD = self.cursor_.metadata()
                            if tMD:
                                v = self.cursorAux.valueBuffer(self.foreignField_)
                                # print("El valor de %s.%s es %s" % (tMD.name(), self.foreignField_, v))
                                if not self.tableName_:
                                    raise ValueError("tableName_ no puede ser Nulo")

                                if not self.fieldName_:
                                    raise ValueError("fieldName_ no puede ser Nulo")
                                # FIXME q = pnsqlquery.PNSqlQuery(False,
                                # self.cursor_.db().connectionName())
                                q = pnsqlquery.PNSqlQuery(None, self.cursor_.db().connectionName())
                                q.setForwardOnly(True)
                                q.setTablesList(self.tableName_)
                                q.setSelect(self.fieldName_)
                                q.setFrom(self.tableName_)
                                where = mng.formatAssignValue(
                                    tMD.field(self.fieldRelation_), v, True
                                )
                                filterAc = self.cursorAux.filterAssoc(self.foreignField_, tMD)

                                if filterAc:
                                    # print("FilterAC == ", filterAc)
                                    if where not in (None, ""):
                                        where = filterAc
                                    else:
                                        where = "%s AND %s" % (where, filterAc)

                                if not self.filter_:
                                    q.setWhere(where)
                                else:
                                    q.setWhere("%s AND %s" % (self.filter_, where))

                                # print("where tipo", type(where))
                                # print("Consulta = %s" % q.sql())
                                if q.exec_() and q.first():
                                    value = q.value(0)
                                    if isinstance(value, str):
                                        if value[0:3] == "RK@":
                                            value = self.cursor_.fetchLargeValue(value)
                                    if isinstance(value, datetime.date):
                                        value = value.strftime("%d-%m-%Y")
                                    self.setValue(value)
                                if not tMD.inCache():
                                    del tMD
                    else:
                        if (
                            self.cursor_ is None
                            or self.cursor_.metadata().field(self.fieldName_) is None
                            and not self.foreignField_
                        ):
                            self.initFakeEditor()

                else:
                    self.initFakeEditor()

                self.showed = True

    def editor(self) -> QtWidgets.QWidget:
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

        hasPushButtonDB = None
        if not self.tableName_ and not self.foreignField_ and not self.fieldRelation_:
            hasPushButtonDB = True
        else:
            hasPushButtonDB = False

        if not self.fieldName_:
            self.fieldAlias_ = self.tr("Error: fieldName vacio")
        else:
            self.fieldAlias_ = self.fieldName_

        self.editor_ = qlineedit.QLineEdit(self)
        self.editor_.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        if self.textLabelDB:
            self.textLabelDB.setSizePolicy(
                QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed
            )
        # self.editor_.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.editor_.setMinimumWidth(100)
        # if application.project.DGI.mobilePlatform():
        #    self.editor_.setMinimumHeight(60)

        if self.FLWidgetFieldDBLayout:
            self.FLWidgetFieldDBLayout.addWidget(self.editor_)
        self.editor_.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocusProxy(self.editor_)

        if not self.tableName():
            self.showEditor_ = False
            self.textLabelDB = None

        if self.textLabelDB:
            self.textLabelDB.setText(self.fieldAlias_)
            if self.showAlias_:
                self.textLabelDB.show()
            else:
                self.textLabelDB.hide()

        if hasPushButtonDB:
            if self.pushButtonDB:
                self.setTabOrder(self.pushButtonDB, self.editor_)
                self.pushButtonDB.setFocusPolicy(QtCore.Qt.NoFocus)
                self.pushButtonDB.show()
        else:
            if self.pushButtonDB:
                self.pushButtonDB.hide()

        prty = ""
        if self.tableName_:
            prty += "tN:" + str(self.tableName_).upper() + ","
        if self.foreignField_:
            prty += "fF:" + str(self.foreignField_).upper() + ","
        if self.fieldRelation_:
            prty += "fR:" + str(self.fieldRelation_).upper() + ","
        if self.actionName_:
            prty += "aN:" + str(self.actionName_).upper() + ","

        if prty != "":
            self.editor_.setText(prty)
            self.setEnabled(False)
            self.editor_.home(False)

        if self.maximumSize().width() < 80:
            self.setShowEditor(False)
        else:
            self.setShowEditor(self.showEditor_)

    def notNullColor(self) -> QtGui.QColor:
        """
        Require Field Color.
        """
        if not self.initNotNullColor_:
            self.initNotNullColor_ = True
        self.notNullColor_ = settings.config.value(
            "ebcomportamiento/colorObligatorio", QtGui.QColor(255, 233, 173).name()
        )

        return self.notNullColor_
