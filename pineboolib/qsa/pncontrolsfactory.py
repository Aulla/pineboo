# -*- coding: utf-8 -*-
"""
Collection of controls used on Pineboo.

Those are loaded from selected DGI.
"""
from PyQt6 import QtCore, QtWidgets, QtGui, QtXml  # type: ignore[import] # noqa: F401

from typing import Any

from pineboolib.core.system import System  # noqa: F401

from .utils import MathClass, NumberAttr, user_id, session  # noqa: F401
from pineboolib import application
from pineboolib.application.packager.pnunpacker import PNUnpacker as AQUnpacker  # noqa: F401
from pineboolib.application.packager.pnpackager import PNPackager as AQPackager  # noqa: F401

from pineboolib.fllegacy.systype import SysType

from pineboolib.q3widgets.qcombobox import QComboBox  # noqa: F401
from pineboolib.q3widgets.qtable import QTable  # noqa: F401
from pineboolib.q3widgets.qlayoutwidget import QLayoutWidget  # noqa: F401
from pineboolib.q3widgets.qtoolbutton import QToolButton  # noqa: F401
from pineboolib.q3widgets.qtabwidget import QTabWidget  # noqa: F401
from pineboolib.q3widgets.qlabel import QLabel  # noqa: F401
from pineboolib.q3widgets.qgroupbox import QGroupBox  # noqa: F401
from pineboolib.q3widgets.qlistview import QListView  # noqa: F401
from pineboolib.q3widgets.qpushbutton import QPushButton  # noqa: F401
from pineboolib.q3widgets.qtextedit import QTextEdit  # noqa: F401
from pineboolib.q3widgets.qlineedit import QLineEdit  # noqa: F401
from pineboolib.q3widgets.qdateedit import QDateEdit  # noqa: F401
from pineboolib.q3widgets.qtimeedit import QTimeEdit  # noqa: F401
from pineboolib.q3widgets.qcheckbox import QCheckBox  # noqa: F401
from pineboolib.q3widgets.qwidget import QWidget  # noqa: F401

# from pineboolib.q3widgets.messagebox import QMessageBox  # noqa: F401
from pineboolib.q3widgets.qbuttongroup import QButtonGroup  # noqa: F401
from pineboolib.q3widgets.qdialog import QDialog  # noqa: F401
from pineboolib.q3widgets.qvboxlayout import QVBoxLayout  # noqa: F401
from pineboolib.q3widgets.qhboxlayout import QHBoxLayout  # noqa: F401
from pineboolib.q3widgets.qframe import QFrame  # noqa: F401
from pineboolib.q3widgets.qmainwindow import QMainWindow  # noqa: F401
from pineboolib.q3widgets.qmenu import QMenu  # noqa: F401
from pineboolib.q3widgets.qtoolbar import QToolBar  # noqa: F401
from pineboolib.q3widgets.qaction import QAction  # noqa: F401
from pineboolib.q3widgets.qdataview import QDataView  # noqa: F401
from pineboolib.q3widgets.qbytearray import QByteArray  # noqa: F401
from pineboolib.q3widgets.qradiobutton import QRadioButton  # noqa: F401
from pineboolib.q3widgets.qspinbox import QSpinBox  # noqa: F401
from pineboolib.q3widgets.qtextstream import QTextStream  # noqa: F401
from pineboolib.q3widgets.qpopupmenu import QPopupMenu  # noqa: F401
from pineboolib.q3widgets.qiconset import QIconSet  # noqa: F401
from pineboolib.q3widgets.qhbuttongroup import QHButtonGroup  # noqa: F401
from pineboolib.q3widgets.qvbuttongroup import QVButtonGroup  # noqa: F401
from pineboolib.q3widgets.qobject import QObject  # noqa: F401

from pineboolib.q3widgets.qeventloop import QEventLoop  # noqa: F401
from pineboolib.q3widgets.qlistviewwidget import QListViewWidget  # noqa: F401
from pineboolib.q3widgets.qdatetime import QDateTime  # noqa: F401
from pineboolib.q3widgets.qdir import QDir  # noqa: F401

from pineboolib.q3widgets.qhttp import QHttp, QHttpResponseHeader, QHttpRequestHeader  # noqa: F401

from PyQt6.QtGui import QActionGroup  # type: ignore[import] # noqa: F401
from PyQt6.QtWidgets import QInputDialog  # type: ignore[import] # noqa: F401
from PyQt6.QtWidgets import QApplication  # noqa: F401


from PyQt6.QtWidgets import QStyleFactory  # noqa: F401
from PyQt6.QtWidgets import QFontDialog  # noqa: F401
from PyQt6.QtWidgets import QDockWidget  # noqa: F401
from PyQt6.QtWidgets import QMdiSubWindow  # noqa: F401
from PyQt6.QtWidgets import QSizePolicy  # noqa: F401
from PyQt6.QtWidgets import QToolBox  # noqa: F401
from PyQt6.QtWidgets import QProgressDialog  # noqa: F401
from PyQt6.QtWidgets import QFileDialog  # noqa: F401
from PyQt6.QtWidgets import QTreeWidget  # noqa: F401
from PyQt6.QtWidgets import QTreeWidgetItem  # noqa: F401
from PyQt6.QtWidgets import QTreeWidgetItemIterator  # noqa: F401
from PyQt6.QtWidgets import QListWidgetItem  # noqa: F401
from PyQt6.QtWidgets import QMdiArea  # noqa: F401
from PyQt6.QtWidgets import QMessageBox  # noqa: F401

from PyQt6.QtCore import QSignalMapper  # type: ignore[import] # noqa: F401
from PyQt6.QtCore import QSize  # noqa: F401

from PyQt6.QtCore import QBuffer  # noqa: F401

from PyQt6.QtGui import QPainter  # noqa: F401
from PyQt6.QtGui import QBrush  # noqa: F401
from PyQt6.QtGui import QKeySequence  # noqa: F401
from PyQt6.QtGui import QPixmap  # noqa: F401
from PyQt6.QtGui import QImage  # noqa: F401
from PyQt6.QtGui import QIcon  # noqa: F401
from PyQt6.QtGui import QColor  # noqa: F401


from PyQt6.QtXml import QDomDocument  # type: ignore[import] # noqa: F401

# Clases FL
from PyQt6.QtXml import QDomDocument as FLDomDocument  # noqa: F401
from PyQt6.QtXml import QDomElement as FLDomElement  # noqa: F401
from PyQt6.QtXml import QDomNode as FLDomNode  # noqa: F401
from PyQt6.QtXml import QDomNodeList as FLDomNodeList  # noqa: F401

from .formdbwidget import FormDBWidget  # noqa: F401
from .object_class import ObjectClass  # noqa: F401

from pineboolib.fllegacy.fltable import FLTable  # noqa: F401
from pineboolib.fllegacy.fllineedit import FLLineEdit  # noqa: F401
from pineboolib.fllegacy.fltimeedit import FLTimeEdit  # noqa: F401
from pineboolib.fllegacy.fldateedit import FLDateEdit  # noqa: F401
from pineboolib.fllegacy.flpixmapview import FLPixmapView  # noqa: F401
from pineboolib.fllegacy.fllistviewitem import FLListViewItem  # noqa: F401
from pineboolib.fllegacy.fldatatable import FLDataTable  # noqa: F401
from pineboolib.fllegacy.flcheckbox import FLCheckBox  # noqa: F401
from pineboolib.application.pnapplication import TextEditOutput as FLTextEditOutput  # noqa: F401
from pineboolib.fllegacy.flspinbox import FLSpinBox  # noqa: F401
from pineboolib.fllegacy.fltabledb import FLTableDB  # noqa: F401
from pineboolib.fllegacy.flfielddb import FLFieldDB  # noqa: F401
from pineboolib.fllegacy.flformdb import FLFormDB  # noqa: F401
from pineboolib.fllegacy.flformrecorddb import FLFormRecordDB  # noqa: F401
from pineboolib.fllegacy.flformsearchdb import FLFormSearchDB  # noqa: F401
from pineboolib.fllegacy.fldoublevalidator import FLDoubleValidator  # noqa: F401
from pineboolib.fllegacy.flintvalidator import FLIntValidator  # noqa: F401
from pineboolib.fllegacy.fluintvalidator import FLUIntValidator  # noqa: F401
from pineboolib.fllegacy.flcodbar import FLCodBar  # noqa: F401
from pineboolib.fllegacy.flwidget import FLWidget  # noqa: F401
from pineboolib.fllegacy.flworkspace import FLWorkSpace  # noqa: F401
from pineboolib.fllegacy.flutil import FLUtil  # noqa: F401
from pineboolib.fllegacy.flsettings import FLSettings  # noqa: F401
from pineboolib.fllegacy.flposprinter import FLPosPrinter  # noqa: F401
from pineboolib.fllegacy.flsqlquery import FLSqlQuery  # noqa: F401
from pineboolib.fllegacy.flserialport import FLSerialPort  # noqa: F401
from pineboolib.fllegacy.flsqlcursor import FLSqlCursor  # noqa: F401
from pineboolib.fllegacy.flnetwork import FLNetwork  # noqa: F401
from pineboolib.fllegacy.flreportviewer import FLReportViewer  # noqa: F401
from pineboolib.fllegacy.flreportengine import FLReportEngine  # noqa: F401
from pineboolib.fllegacy.fljasperengine import FLJasperEngine  # noqa: F401
from pineboolib.fllegacy.fljasperviewer import FLJasperViewer  # noqa: F401
from pineboolib.fllegacy.flfastcgi import FLFastCgi  # noqa: F401

from pineboolib.fllegacy.flapplication import FLApplication  # noqa: F401
from pineboolib.fllegacy.flvar import FLVar  # noqa: F401
from pineboolib.fllegacy.flsmtpclient import FLSmtpClient  # noqa: F401
from pineboolib.fllegacy.flscripteditor import FLScriptEditor  # noqa: F401

# Clases QSA

from PyQt6.QtGui import QColor as Color  # noqa: F401
from PyQt6.QtWidgets import QLabel as Label  # noqa: F401
from PyQt6.QtGui import QFont as Font  # noqa: F401


from pineboolib.q3widgets.line import Line  # noqa: F401
from pineboolib.q3widgets.checkbox import CheckBox  # noqa: F401
from pineboolib.q3widgets.combobox import ComboBox  # noqa: F401
from pineboolib.q3widgets.textedit import TextEdit  # noqa: F401
from pineboolib.q3widgets.lineedit import LineEdit  # noqa: F401
from pineboolib.q3widgets.messagebox import MessageBox  # noqa: F401
from pineboolib.q3widgets.radiobutton import RadioButton  # noqa: F401
from pineboolib.q3widgets.filedialog import FileDialog  # noqa: F401
from pineboolib.q3widgets.spinbox import SpinBox  # noqa: F401

from pineboolib.q3widgets.dialog import Dialog  # noqa: F401
from pineboolib.q3widgets.groupbox import GroupBox  # noqa: F401

from pineboolib.q3widgets.numberedit import NumberEdit  # noqa: F401
from pineboolib.q3widgets.dateedit import DateEdit  # noqa: F401
from pineboolib.q3widgets.timeedit import TimeEdit  # noqa: F401
from pineboolib.q3widgets.picture import Picture  # noqa: F401
from pineboolib.q3widgets.rect import Rect  # noqa: F401
from pineboolib.q3widgets.size import Size  # noqa: F401
from pineboolib.q3widgets.pixmap import Pixmap  # noqa: F401

from pineboolib.fllegacy.aqsobjects.aqsettings import AQSettings  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsqlquery import AQSqlQuery  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsqlcursor import AQSqlCursor  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqutil import AQUtil  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsql import AQSql  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsmtpclient import AQSmtpClient  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqs import AQS  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsignalmapper import AQSignalMapper  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqssproject import AQSSProject  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqobjectquerylist import (  # noqa: F401
    aq_object_query_list as AQObjectQueryList,
)


from pineboolib.core.utils.utils_base import is_deployed as __is_deployed
from pineboolib.application.database.orm.utils import OrmManager
from pineboolib.application.database.utils import ClassManager

from pineboolib.application.qsadictmodules import from_project, orm_  # noqa: F401


from pineboolib.fllegacy.aqsobjects.aqboolflagstate import AQBoolFlagState  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqboolflagstate import AQBoolFlagStateList  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsbuttongroup import AQSButtonGroup  # noqa: F401

from pineboolib.application.signatures.xml_digest import XmlDigest  # noqa: F401
from pineboolib.application.signatures.pdf_digest import PdfDigest  # noqa: F401
from pineboolib.application.signatures.pdf_qr import PdfQr  # noqa: F401

if not __is_deployed():
    from pineboolib.fllegacy.aqsobjects.aqods import AQOdsGenerator, AQOdsSpreadSheet  # noqa: F401
    from pineboolib.fllegacy.aqsobjects.aqods import AQOdsSheet, AQOdsRow  # noqa: F401
    from pineboolib.fllegacy.aqsobjects.aqods import AQOdsStyle  # noqa: F401
    from pineboolib.fllegacy.aqsobjects.aqods import AQOdsImage  # noqa: F401
    from pineboolib.fllegacy.aqsobjects.aqods import aq_ods_color as AQOdsColor  # noqa: F401

qApp = QApplication  # noqa: F401
ORM_MANAGER = OrmManager()
CLASS_MANAGER = ClassManager()

QSA_SYS = SysType()

QS_PROJECT = AQSSProject()
MATH = MathClass()
NUMBER_ATT = NumberAttr()
AQ_APP = application.PROJECT.aq_app


class Application:
    """
    Emulate QS Application class.

    The "Data" module uses "Application.formRecorddat_processes" to read the module.
    """

    def __getattr__(self, name: str) -> Any:
        """Emulate any method and retrieve application action module specified."""

        from_project(name)
