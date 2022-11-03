# -*- coding: utf-8 -*-
"""
QSA Emulation module.

This file should be imported at top of QS converted files.
"""

import re  # noqa: F401

from pineboolib.core.utils.utils_base import ustr, filedir  # noqa: F401
from pineboolib.application.types import QString, String  # noqa: F401
from pineboolib.application.types import boolean as Boolean  # noqa: F401
from pineboolib.application.types import function as Function  # noqa: F401
from pineboolib.application.types import object_ as Object  # noqa: F401

from pineboolib.application.types import File, Dir, Array, Date, AttributeDict  # noqa: F401
from pineboolib.application.types import FileStatic, DirStatic  # noqa: F401

from pineboolib.qsa.input import Input  # noqa: F401
from pineboolib.qsa.utils import reg_exp as RegExp  # noqa: F401
from pineboolib.qsa.utils import parse_float as parseFloat  # noqa: F401
from pineboolib.qsa.utils import parse_string as parseString  # noqa: F401
from pineboolib.qsa.utils import parse_int as parseInt  # noqa: F401
from pineboolib.qsa.utils import start_timer as startTimer  # noqa: F401
from pineboolib.qsa.utils import kill_timer as killTimer  # noqa: F401
from pineboolib.qsa.utils import kill_timers as killTimers  # noqa: F401
from pineboolib.qsa.utils import is_nan as isNaN  # noqa: F401
from pineboolib.qsa.utils import debug, isnan, replace, length, text  # noqa: F401
from pineboolib.qsa.utils import format_exc, Sort, splice, typeof_  # noqa: F401
from pineboolib.qsa.utils import Switch as switch  # noqa: F401
from pineboolib.qsa.utils import QsaRegExp as qsaRegExp  # noqa: F401
from pineboolib.qsa.utils import (  # noqa: F401
    ws_channel_send,
    thread,
    user_id,
    session_atomic,
    session,
    _super,
)
from pineboolib.qsa.utils import (  # noqa: F401
    thread_session_new,
    thread_session_current,
    thread_session_free,
)
from pineboolib.qsa.utils import (  # noqa: F401
    pool_status,
    set_user_id,
    memory_status,
    qt_translate_noop,
)
from pineboolib.qsa.utils import ws_channel_send_type, is_valid_session  # noqa: F401
from pineboolib.qsa.decorators import atomic, serialize  # noqa: F401

from pineboolib.qsa.pncontrolsfactory import from_project, orm_, Application  # noqa: F401


# QT
from pineboolib.qsa.pncontrolsfactory import QS_PROJECT, QSA_SYS, MATH, NUMBER_ATT
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QComboBox,
    QTable,
    QLayoutWidget,
    QToolButton,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QTabWidget,
    QLabel,
    QGroupBox,
    QListView,
    QImage,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QTextEdit,
    QLineEdit,
    QDateEdit,
    QTimeEdit,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QCheckBox,
    QWidget,
    QMessageBox,
    QDialog,
    QDateTime,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMainWindow,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QMenu,
    QToolBar,
    QAction,
    QDataView,
    QByteArray,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QMdiArea,
    QEventLoop,
    QActionGroup,
    QInputDialog,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QApplication,
    QStyleFactory,
    QFontDialog,
    QTextStream,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QMdiSubWindow,
    QSizePolicy,
    QProgressDialog,
)
from pineboolib.qsa.pncontrolsfactory import QFileDialog, QTreeWidget, QTreeWidgetItem  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QTreeWidgetItemIterator,
    QListWidgetItem,
    QObject,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QListViewWidget,
    QSignalMapper,
    QPainter,
    QBrush,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QKeySequence,
    QIcon,
    QColor,
    QDomDocument,
    QIconSet,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QPushButton,
    QSpinBox,
    QRadioButton,
    QPixmap,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QButtonGroup,
    QToolBox,
    QSize,
    QDockWidget,
    QDir,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QPopupMenu,
    QBuffer,
    QHButtonGroup,
    QVButtonGroup,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    QHttp,
    QHttpResponseHeader,
    QHttpRequestHeader,
)

# FL
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FLDomDocument,
    FLDomElement,
    FLDomNode,
    FLFastCgi,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FLDomNodeList,
    FLLineEdit,
    FLTimeEdit,
    FLDateEdit,
)
from pineboolib.qsa.pncontrolsfactory import FLPixmapView, FLDataTable, FLCheckBox  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FLTextEditOutput,
    FLSpinBox,
    FLTableDB,
    FLFieldDB,
)
from pineboolib.qsa.pncontrolsfactory import FLFormDB, FLFormRecordDB, FLFormSearchDB  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FLDoubleValidator,
    FLIntValidator,
    FLUIntValidator,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FLCodBar,
    FLWidget,
    FLWorkSpace,
    FLPosPrinter,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FLSqlQuery,
    FLSqlCursor,
    FLNetwork,
    FLSerialPort,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FLApplication,
    FLVar,
    FLSmtpClient,
    FLTable,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FLListViewItem,
    FLReportViewer,
    FLUtil,
    FLSettings,
)
from pineboolib.qsa.pncontrolsfactory import FLScriptEditor, FLReportEngine  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import FLJasperEngine, FLJasperViewer  # noqa: F401

# QSA
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    FileDialog,
    Color,
    Label,
    Line,
    CheckBox,
    Dialog,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    ComboBox,
    TextEdit,
    LineEdit,
    MessageBox,
    RadioButton,
)
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    GroupBox,
    SpinBox,
    NumberEdit,
    DateEdit,
    TimeEdit,
)
from pineboolib.qsa.pncontrolsfactory import Picture, Rect, Size, Pixmap, Font  # noqa: F401


# AQS
from pineboolib.qsa.pncontrolsfactory import AQS, AQUnpacker, AQSettings, AQSqlQuery  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import AQSqlCursor, AQUtil, AQSql, AQSmtpClient  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
    AQSignalMapper,
    AQSSProject,
    AQObjectQueryList,
)
from pineboolib.qsa.pncontrolsfactory import AQSButtonGroup  # noqa: F401

from pineboolib.core.utils.utils_base import is_deployed as __is_deployed

if not __is_deployed():
    # FIXME: No module named 'xml.sax.expatreader' in deploy
    from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
        AQOdsGenerator,
        AQOdsSpreadSheet,
        AQOdsSheet,
    )
    from pineboolib.qsa.pncontrolsfactory import (  # noqa: F401
        AQOdsRow,
        AQOdsColor,
        AQOdsStyle,
        AQOdsImage,
    )

from pineboolib.qsa.pncontrolsfactory import AQBoolFlagState, AQBoolFlagStateList  # noqa: F401


from pineboolib.qsa.pncontrolsfactory import FormDBWidget, ObjectClass  # noqa: F401
from pineboolib.application.process import Process, ProcessStatic  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import SysType, System  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import AQ_APP as aqApp  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import ORM_MANAGER as orm  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import CLASS_MANAGER as class_  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import XmlDigest, PdfDigest  # noqa: F401
from pineboolib.qsa.pncontrolsfactory import PdfQr  # noqa: F401

QSProject = QS_PROJECT
sys = QSA_SYS
Math = MATH
Number = NUMBER_ATT


QFile = File
util = FLUtil  # pylint: disable=invalid-name
print_ = print


undefined = None  # pylint: disable=invalid-name
LogText = 0  # pylint: disable=invalid-name
RichText = 1  # pylint: disable=invalid-name
