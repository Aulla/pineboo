"""Flreportviewer module."""
from PyQt5 import QtWidgets, QtCore, QtXml

from pineboolib.core import decorators, settings
from pineboolib import application
from pineboolib.core.utils import utils_base
from pineboolib.application.qsatypes.sysbasetype import SysBaseType
from . import flutil
from . import flsqlquery
from . import flsqlcursor
from . import flmanagermodules

from pdf2image import convert_from_path

from .flreportengine import FLReportEngine
from pineboolib import logging

from typing import Any, List, Mapping, Sized, Union, Dict, Optional, Callable, TYPE_CHECKING
from PyQt5.QtGui import QColor, QImage, QPalette, QPixmap, QPainter

from PIL.ImageQt import ImageQt

import shutil

if TYPE_CHECKING:
    from pineboolib.q3widgets import qmainwindow  # noqa: F401


LOGGER = logging.get_logger(__name__)

AQ_USRHOME = "."  # FIXME


class InternalReportViewer(QtWidgets.QWidget):
    """InternalReportViewer class."""

    _report_engine: Optional[FLReportEngine]
    dpi_: int
    report_: List[Any]
    _num_copies: int
    _printer_name: str
    _color_mode: int  # 1 color, 0 gray_scale
    _parent: "QtWidgets.QWidget"

    def __init__(self, parent: "QtWidgets.QWidget") -> None:
        """Inicialize."""
        super().__init__(parent)
        self._report_engine = None
        self.dpi_ = int(settings.SETTINGS.value("rptViewer/dpi", 300))
        self.report_ = []
        self._num_copies = 1
        self._printer_name = ""
        self._color_mode = 1
        self._parent = parent
        self._page_count = -1

    def setReportEngine(self, report_engine: FLReportEngine) -> None:
        """Set report engine."""

        self._report_engine = report_engine

    def resolution(self) -> int:
        """Return resolution."""

        return self.dpi_

    def reportPages(self) -> List[Any]:
        """Return report pages."""
        return self.report_

    def renderReport(self, init_row: int, init_col: int, flags: List[int]) -> Any:
        """Render report."""

        if self._report_engine is None:
            raise Exception("renderReport. self._report_engine is empty!")

        result = self._report_engine.renderReport(init_row, init_col, flags)
        self.report_ = self._report_engine._parser._document.pages
        return result

    def setNumCopies(self, num_copies: int) -> None:
        """Set number of copies."""
        self._num_copies = num_copies

    def setPrinterName(self, name: str) -> None:
        """Set printer name."""
        self._printer_name = name

    def setColorMode(self, color_mode: int) -> None:
        """Set color mode."""

        self._color_mode = color_mode

    def slotFirstPage(self):
        """positioning first page."""
        self._parent._w.set_page(0)

    def slotLastPage(self):
        """positioning last page."""
        cnt = len(self.report_)
        self._parent._w.set_page(cnt - 1)

    def slotNextPage(self):
        """positioning next page."""

        cnt = len(self.report_)
        current_page = self._parent._w._current_page
        next_page = (current_page + 1) if current_page < cnt - 1 else current_page
        self._parent._w.set_page(next_page)

    def slotPrevPage(self):
        """positioning prev page."""

        cnt = len(self.report_)
        current_page = self._parent._w._current_page
        prev_page = (current_page - 1) if current_page > 0 else current_page
        self._parent._w.set_page(prev_page)

    def slotPrintReport(self):
        """Print report."""
        if self.slot_print_disabled:
            return

        from PyQt5 import QtPrintSupport

        dialog = QtPrintSupport.QPrintDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.report_printed = self._report_engine.printReport(dialog)

    def slotZoomUp(self):
        """ZoomUp."""

        self._parent._w._scale_factor += 0.5
        current_page = self._parent._w._current_page
        self._parent._w._current_page = -1
        self._parent._w.set_page(current_page)

    def slotZoomDown(self):
        """ZoomDown."""

        self._parent._w._scale_factor -= 0.5
        current_page = self._parent._w._current_page
        self._parent._w._current_page = -1
        self._parent._w.set_page(current_page)

    @decorators.not_implemented_warn
    def exportFileCSVData(self):
        """exportFileCSVData."""

    @decorators.not_implemented_warn
    def exportToPDF(self):
        """exportToPDF."""

    @decorators.not_implemented_warn
    def sendEMailPDF(self):
        """sendEMailPDF."""

    @decorators.not_implemented_warn
    def showInitCentralWidget(self, value: bool):
        """showInitCentralWidget."""

    @decorators.not_implemented_warn
    def saveSVGStyle(self):
        """saveSVGStyle."""

    @decorators.not_implemented_warn
    def saveSimpleSVGStyle(self):
        """saveSimpleSVGStyle."""

    @decorators.not_implemented_warn
    def loadSVGStyle(self):
        """loadSVGStyle."""

    def __getattr__(self, name: str) -> Callable:
        """Return attributes from report engine."""
        return getattr(self._report_engine, name, None)


class FLReportViewer(QtWidgets.QWidget):
    """FLReportViewer class."""

    pdfFile: str
    Append: int
    Display: int
    PageBreak: int
    _spn_resolution: int

    qry_: Any
    xml_data_: Any
    template_: Any
    autoClose_: bool
    slot_print_disabled: bool
    slot_exported_disabled: bool
    _style_name: str
    _report_engine: "FLReportEngine"

    PrintGrayScale = 0
    PrintColor = 1
    _w: QtWidgets.QWidget

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        name: Optional[str] = None,
        embed_in_parent: bool = False,
        report_engine: Optional["FLReportEngine"] = None,
    ) -> None:
        """Inicialize."""

        super().__init__(parent)

        self.loop_ = False
        self.eventloop = QtCore.QEventLoop()
        self.report_printed = False
        self._report_engine: Optional[Any] = None

        self.slot_print_disabled = False
        self.slot_exported_disabled = False
        self.printing_ = False
        self.embed_in_parent = True if parent and embed_in_parent else False
        self.ui_: Dict[str, QtCore.QObject] = {}

        self.Display = 1
        self.Append = 1
        self.PageBreak = 1

        self.report_viewer = InternalReportViewer(self)
        self.setReportEngine(FLReportEngine(self) if report_engine is None else report_engine)
        self._w = None

        if self.report_viewer is None:
            raise Exception("self.report_viewer is empty!")

    def rptViewer(self) -> "InternalReportViewer":
        """Return report viewer."""
        return self.report_viewer

    def report_engine(self) -> "FLReportEngine":
        """Return report engine."""

        if self._report_engine is None:
            raise Exception("_report_engine is not defined!")
        return self._report_engine

    def setReportEngine(self, report_engine: Optional[FLReportEngine] = None) -> None:
        """Set report engine."""

        if self._report_engine == report_engine:
            return

        sender = self.sender()
        no_destroy = not (sender and sender == self._report_engine)

        self._report_engine = report_engine
        if self._report_engine is not None:
            self.template_ = self._report_engine.rptNameTemplate()
            self.qry_ = self._report_engine.rptQueryData()

            if no_destroy:
                self.report_viewer.setReportEngine(self._report_engine)

    def exec_(self) -> str:
        """Show report."""
        # if self.loop_:
        #    print("FLReportViewer::exec(): Se ha detectado una llamada recursiva")
        #    return

        if self.report_viewer._report_engine and hasattr(
            self.report_viewer._report_engine, "_parser"
        ):
            pdf_file = self.report_viewer._report_engine._parser.get_file_name()

        if not utils_base.is_library():
            if application.USE_REPORT_VIEWER:
                self._w = FLWidgetReportViewer(self)
                self._w.show()
                self._w._file_name = pdf_file
                self._w.refresh()
                self.slotFirstPage()

            # SysBaseType.openUrl(pdf_file)

        return pdf_file

    @decorators.beta_implementation
    def csvData(self) -> str:
        """Return csv data."""

        return self._report_engine.csvData() if self._report_engine else ""

    def renderReport(
        self,
        init_row: int = 0,
        init_col: int = 0,
        append_or_flags: Union[bool, Sized, Mapping[int, Any]] = None,
        display_report: bool = False,
    ) -> bool:
        """Render report."""
        if not self._report_engine:
            return False

        flags = [self.Append, self.Display]

        if isinstance(append_or_flags, bool):
            flags[0] = append_or_flags

            if display_report is not None:
                flags[0] = display_report
        elif isinstance(append_or_flags, list):
            if len(append_or_flags) > 0:
                flags[0] = append_or_flags[0]  # display
            if len(append_or_flags) > 1:
                flags[1] = append_or_flags[1]  # append
            if len(append_or_flags) > 2:
                flags.append(append_or_flags[2])  # page_break

        ret = self.report_viewer.renderReport(init_row, init_col, flags)
        return ret

    def renderReport2(
        self,
        init_row: int = 0,
        init_col: int = 0,
        append_or_flags: Union[bool, Sized, Mapping[int, Any]] = None,
        display_report: bool = False,
    ) -> bool:
        """Render report."""

        return self.renderReport(init_row, init_col, append_or_flags, display_report)

    def setReportData(
        self, data: Union["flsqlcursor.FLSqlCursor", "flsqlquery.FLSqlQuery", "QtXml.QDomNode"]
    ) -> bool:
        """Set data to report."""
        if isinstance(data, flsqlquery.FLSqlQuery):
            self.qry_ = data
            if self._report_engine and self._report_engine.setReportData(data):
                self.xml_data_ = self._report_engine.rptXmlData()
                return True
            return False
        elif isinstance(data, flsqlcursor.FLSqlCursor):
            if not self._report_engine:
                return False
            return self._report_engine.setReportData(data)
        elif isinstance(data, QtXml.QDomNode):
            self.xml_data_ = data
            self.qry_ = None
            if not self._report_engine:
                return False
            return self._report_engine.setReportData(data)
        return False

    def setReportTemplate(
        self, template: Union["QtXml.QDomNode", str], style: Optional[str] = None
    ) -> bool:
        """Set template to report."""
        if isinstance(template, QtXml.QDomNode):
            self._xml_template = template
            self.template_ = ""

            if not self._report_engine:
                return False

            if style is not None:
                self.setStyleName(style)

            self._report_engine.setFLReportTemplate(template)

            return True
        else:
            self.template_ = template
            self._style_name = style
            if self._report_engine and self._report_engine.setFLReportTemplate(template):
                # self.setStyleName(style)
                self._xml_template = self._report_engine.rptXmlTemplate()
                return True

        return False

    @decorators.beta_implementation
    def sizeHint(self) -> QtCore.QSize:
        """Return sizeHint."""
        return self.report_viewer.sizeHint()

    @decorators.beta_implementation
    def setNumCopies(self, num: int) -> None:
        """Set number of copies."""
        self.report_viewer.setNumCopies(num)

    @decorators.beta_implementation
    def setPrinterName(self, name: str) -> None:
        """Set printer name."""
        self.report_viewer.setPrinterName(name)

    @decorators.beta_implementation
    def reportPrinted(self) -> bool:
        """Return if report was printed."""
        return self.report_printed

    def disableSlotsPrintExports(self, disable_print: bool = False, disable_export: bool = False):
        """Disable export and print slots."""

        self.slot_print_disabled = disable_print
        self.slot_exported_disabled = disable_export

    def printReport(self) -> None:
        """Print a report."""

        if self.slot_print_disabled:
            return

        printer_name = self.report_viewer._printer_name
        num_copies = self.report_viewer._num_copies
        color_mode = self.report_viewer._color_mode

        self.report_printed = self._report_engine.printReport(printer_name, num_copies, color_mode)

    def printReportToPDF(self, file_name: str = "") -> None:
        """Print report to pdf."""

        if self.slot_print_disabled:
            return

        pdf_file = self.report_viewer._report_engine._parser.get_file_name()
        if pdf_file and file_name:
            shutil.copyfile(pdf_file, file_name)
            self.report_printed = True

    @decorators.pyqt_slot(int)
    def setResolution(self, dpi: int) -> None:
        """Set resolution."""
        settings.SETTINGS.set_value("rptViewer/dpi", dpi)
        self.report_viewer.dpi_ = dpi
        current = self._w._current_page if self._w._current_page > -1 else 0
        self._w.refresh()
        self._w.set_page(current)

    @decorators.pyqt_slot(int)
    def setPixel(self, rel_dpi: int) -> None:
        """Set pixel size."""
        settings.SETTINGS.set_value("rptViewer/pixel", rel_dpi)
        self._report_engine._rel_dpi = rel_dpi

    def setDefaults(self) -> None:
        """Set default values."""

        if self._w is not None:
            self._w._pixel_control.setValue(780)
            self._w._resolution_control.setValue(300)

    @decorators.beta_implementation
    def updateReport(self) -> None:
        """Update report."""
        self.requestUpdateReport.emit()

        if self.qry_ or (self.xml_data_ and self.xml_data_ != ""):
            if not self._report_engine:
                self.setReportEngine(FLReportEngine(self))

            self.setResolution(self._spn_resolution)
            self.setPixel(self.spnPixel_)

            if self.template_ and self.template_ != "":
                self.setReportTemplate(self.template_, self._style_name)
            else:
                self.setReportTemplate(self._xml_template, self._style_name)

            if self.qry_:
                self.setReportData(self.qry_)
            else:
                self.setReportData(self.xml_data_)

            self.renderReport(0, 0, False, False)

        self.updateDisplay()

    @decorators.not_implemented_warn
    def getCurrentPage(self) -> Any:
        """Return curent page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getCurrentPage(), self)
        return 0

    @decorators.not_implemented_warn
    def getFirstPage(self) -> Any:
        """Return first page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getFirstPage(), self)
        return 0

    @decorators.not_implemented_warn
    def getPreviousPage(self) -> Any:
        """Return previous page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getPreviousPage(), self)
        return 0

    @decorators.not_implemented_warn
    def getNextPage(self) -> Any:
        """Return next page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getNextPage(), self)
        return 0

    @decorators.not_implemented_warn
    def getLastPage(self) -> Any:
        """Return last page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getLastPage(), self)
        return 0

    @decorators.not_implemented_warn
    def getPageAt(self, num: int) -> Any:
        """Return actual page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getPageAt(i), self)
        return 0

    @decorators.not_implemented_warn
    def updateDisplay(self) -> None:
        """Update display."""
        self.report_viewer.slotUpdateDisplay()

    @decorators.not_implemented_warn
    def clearPages(self) -> None:
        """Clear report pages."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.clear()
        pass

    @decorators.not_implemented_warn
    def appendPage(self) -> None:
        """Add a new page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.appendPage()
        pass

    @decorators.not_implemented_warn
    def getCurrentIndex(self) -> int:
        """Return current index position."""

        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.getCurrentIndex()
        return -1

    @decorators.not_implemented_warn
    def setCurrentPage(self, idx: int) -> None:
        """Set current page index."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setCurrentPage(idx)
        pass

    @decorators.not_implemented_warn
    def setPageSize(
        self, size: Union[QtCore.QSize, int], orientation: Optional[int] = None
    ) -> None:
        """Set page size."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageSize(s)
        pass

    @decorators.not_implemented_warn
    def setPageOrientation(self, orientation: int) -> None:
        """Set page orientation."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageOrientation(o)
        pass

    @decorators.not_implemented_warn
    def setPageDimensions(self, dim: QtCore.QSize) -> None:
        """Set page dimensions."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageDimensions(dim)
        pass

    @decorators.not_implemented_warn
    def pageSize(self) -> QtCore.QSize:
        """Return page size."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.pageSize()
        return -1

    @decorators.not_implemented_warn
    def pageOrientation(self) -> int:
        """Return page orientation."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.pageOrientation()
        return -1

    def pageDimensions(self) -> QtCore.QSize:
        """Return page dimensions."""
        if self.report_viewer._report_engine and hasattr(
            self.report_viewer._report_engine, "_parser"
        ):
            return self.report_viewer._report_engine._parser._page_size
        return -1

    def pageCount(self) -> int:
        """Return number of pages."""
        if self.report_viewer._report_engine:
            return self.report_viewer._report_engine.number_pages()
        return -1

    @decorators.beta_implementation
    def setStyleName(self, style: str) -> None:
        """Set style name."""
        self._style_name = style

    @decorators.beta_implementation
    def setReportPages(self, pgs: Any) -> None:
        """Add pages to actual report."""
        self.setReportEngine(None)
        self.qry_ = None
        self.xml_data_ = QtXml.QDomNode()
        self.report_viewer.setReportPages(pgs.pageCollection() if pgs else 0)
        self.report_ = self.report_viewer.reportPages()

    @decorators.beta_implementation
    def setColorMode(self, color: QColor) -> None:
        """Set color mode."""

        self.report_viewer.setColorMode(color)

    @decorators.beta_implementation
    def colorMode(self) -> QColor:
        """Return color mode."""
        return self.report_viewer.colorMode()

    @decorators.beta_implementation
    def setName(self, name: str) -> None:
        """Set report name."""
        self.name_ = name

    @decorators.beta_implementation
    def name(self) -> str:
        """Return report name."""
        return self.name_

    def __getattr__(self, name: str) -> Any:
        """Return attribute from inernal object."""
        return getattr(self.report_viewer, name, None)


class FLWidgetReportViewer(QtWidgets.QMainWindow):
    """FLWidgetReportViewer."""

    _report_viewer: "FLReportViewer"
    _fr_mail: "QtWidgets.QFrame"
    _auto_close: bool
    _auto_widget: "QtWidget.QcheckBox"
    _pages: List["QImage"]
    _file_name: str
    _image_label: "QtWidgets.QLabel"
    _scroll_area: "QtWidgets.QScrollArea"
    _scale_factor: int
    _current_page: int

    def __init__(self, report_viewer: "FLReportViewer") -> None:
        """Initialize."""

        super().__init__()
        self.setObjectName("FLWidgetReportViewer")

        from pineboolib.q3widgets import qframe, qcheckbox, qspinbox

        self._auto_close = settings.SETTINGS.value("rptViewer/autoClose", False)
        self._report_viewer = report_viewer
        form_path = utils_base.filedir("fllegacy/forms/FLWidgetReportViewer.ui")
        self = flmanagermodules.FLManagerModules.createUI(form_path, None, self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self._fr_mail = self.findChild(qframe.QFrame, "frEMail")
        self._auto_widget = self.findChild(qcheckbox.QCheckBox, "chkAutoClose")
        self._pixel_control = self.findChild(qspinbox.QSpinBox, "spnPixel")
        self._resolution_control = self.findChild(qspinbox.QSpinBox, "spnResolution")

        self._pixel_control.setValue(self._report_engine._rel_dpi)
        self._resolution_control.setValue(self._report_viewer.dpi_)

        self._auto_widget.setChecked(self._auto_close)
        self._fr_mail.hide()
        self._image_label = QtWidgets.QLabel()
        self._image_label.setBackgroundRole(QPalette.Base)
        self._image_label.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored
        )
        self._image_label.setScaledContents(True)
        self._scroll_area = QtWidgets.QScrollArea()
        self._scroll_area.setBackgroundRole(QPalette.Dark)
        self._scroll_area.setWidget(self._image_label)
        self._scroll_area.setVisible(False)

        self.setCentralWidget(self._scroll_area)
        self._scale_factor = 1
        self._current_page = -1

        self.hide()
        self._pages = []
        self._file_name = ""
        self.clear()

    def __getattr__(self, name: str) -> Any:
        """Return FLReportViewer attributes."""
        return getattr(self._report_viewer, name, None)

    def setAutoClose(self) -> None:
        """Set autoclose."""

        self._auto_close = self._auto_widget.isChecked()
        settings.SETTINGS.set_value("rptViewer/autoClose", self._auto_close)

    def close(self) -> None:
        """Close form."""

        super().close()

    def refresh(self) -> None:
        """Set page to centralWidget."""
        self._pages = convert_from_path(
            self._file_name,
            dpi=self._report_viewer.report_viewer.dpi_,
            output_folder=application.PROJECT.tmpdir,
        )
        self._current_page = -1
        self.clear()

    def set_page(self, num) -> None:
        if self._current_page == num:
            return
        image = self._pages[num] if self._pages else None
        if image is not None:
            self._image_label.clear()
            self._current_page = num
            image_qt = ImageQt(image)
            scaled_size = QtCore.QSize(780 * self._scale_factor, 591 * self._scale_factor)
            scaled = image_qt.scaled(
                scaled_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
            pix = QPixmap.fromImage(scaled)
            self._image_label.setPixmap(pix)
            self._image_label.adjustSize()
            self._scroll_area.setVisible(True)

    def clear(self) -> None:
        self._scroll_area.setVisible(False)
        self._current_page = None
        # print("Borra centralwidget")

