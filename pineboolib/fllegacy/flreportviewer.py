"""Flreportviewer module."""
from PyQt6 import QtWidgets, QtCore, QtXml

from pineboolib.core import decorators, settings
from pineboolib import application
from pineboolib.core.utils import utils_base
from pineboolib.application import qsatypes
from . import flsqlquery
from . import flsqlcursor
from . import flmanagermodules

from pdf2image import convert_from_path

from .flreportengine import FLReportEngine
from pineboolib import logging

from typing import Any, List, Mapping, Sized, Union, Dict, Optional, Callable, TYPE_CHECKING
from PyQt6.QtGui import QPalette, QPixmap

from PIL.ImageQt import ImageQt

import shutil
import pathlib

if TYPE_CHECKING:
    from pineboolib.q3widgets import qmainwindow  # noqa: F401
    from PyQt6.QtGui import QImage  # noqa: F401


LOGGER = logging.get_logger(__name__)

AQ_USRHOME = "."  # FIXME


class FLReportViewer(QtWidgets.QWidget):
    """FLReportViewer class."""

    pdfFile: str
    Append: int
    Display: int
    PageBreak: int

    qry_: Any
    xml_data_: Any
    template_: Any
    _auto_close: bool
    slot_print_disabled: bool
    slot_exported_disabled: bool
    _style_name: str
    _report_engine: "FLReportEngine"

    PrintGrayScale = 0
    PrintColor = 1
    _w: QtWidgets.QWidget

    _report_engine: Optional[FLReportEngine]
    dpi_: int
    report_: List[Any]
    _num_copies: int
    _printer_name: str
    _color_mode: int  # 1 color, 0 gray_scale

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        name: Optional[str] = None,
        embed_in_parent: bool = False,
        report_engine: Optional["FLReportEngine"] = None,
    ) -> None:
        """Inicialize."""

        super().__init__(parent)

        # self.loop_ = False
        # self.eventloop = QtCore.QEventLoop()

        self.report_printed = False
        self.slot_print_disabled = False
        self.slot_exported_disabled = False
        self.printing_ = False
        self.embed_in_parent = True if parent and embed_in_parent else False
        self.ui_: Dict[str, QtCore.QObject] = {}

        self.Display = 1  # pylint: disable=invalid-name
        self.Append = 1  # pylint: disable=invalid-name
        self.PageBreak = 1  # pylint: disable=invalid-name
        self._report_engine = report_engine or FLReportEngine(self)
        self._w = None

        self.dpi_ = int(settings.SETTINGS.value("rptViewer/dpi", 300))
        self.report_ = []
        self._num_copies = 1
        self._printer_name = ""
        self._color_mode = 1
        self._page_count = -1

    def resolution(self) -> int:
        """Return resolution."""

        return self.dpi_

    def reportPages(self) -> List[Any]:
        """Return report pages."""
        return self.report_

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
        """Positioning first page."""
        self._w.set_page(0)

    def slotLastPage(self):
        """Positioning last page."""
        cnt = len(self.report_)
        self._w.set_page(cnt - 1)

    def slotNextPage(self):
        """Positioning next page."""

        cnt = len(self.report_)
        current_page = self._w._current_page
        next_page = (current_page + 1) if current_page < cnt - 1 else current_page
        self._w.set_page(next_page)

    def slotPrevPage(self):
        """Positioning prev page."""

        current_page = self._w._current_page
        prev_page = (current_page - 1) if current_page > 0 else current_page
        self._w.set_page(prev_page)

    def slotPrintReport(self):
        """Print report."""
        if self.slot_print_disabled:
            return

        from PyQt6 import QtPrintSupport

        dialog = QtPrintSupport.QPrintDialog()
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.report_printed = self._report_engine.printReport(dialog)
            if self._auto_close and self.report_printed:
                self._w.close()

    def slotZoomUp(self):
        """ZoomUp."""

        self._w._scale_factor += 0.5
        current_page = self._w._current_page
        self._w._current_page = -1
        self._w.set_page(current_page)

    def slotZoomDown(self):
        """ZoomDown."""

        if self._w._scale_factor <= 0:
            return

        self._w._scale_factor -= 0.5
        current_page = self._w._current_page
        self._w._current_page = -1
        self._w.set_page(current_page)

    @decorators.not_implemented_warn
    def exportFileCSVData(self):
        """exportFileCSVData."""

        if self.slot_exported_disabled:
            return

    def exportToPDF(self):
        """exportToPDF."""

        if self.slot_exported_disabled:
            return

        data = QtWidgets.QFileDialog.getSaveFileName(
            self, "Seleccione fichero", str(pathlib.Path.home()), "*.pdf"
        )
        file_name = data[0]
        if file_name:
            if not file_name.endswith(".pdf"):
                file_name += ".pdf"
            shutil.copy(self._report_engine._parser.get_file_name(), file_name)

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

    def report_engine(self) -> "FLReportEngine":
        """Return report engine."""

        if self._report_engine is None:
            raise Exception("_report_engine is not defined!")
        return self._report_engine

    def setReportEngine(self, report_engine: Optional[FLReportEngine] = None) -> None:
        """Set report engine."""

        if self._report_engine is report_engine:
            return

        self._report_engine = report_engine
        if self._report_engine is not None:
            self.template_ = self._report_engine.rptNameTemplate()
            self.qry_ = self._report_engine.rptQueryData()

    def exec_(self) -> str:
        """Show report."""
        # if self.loop_:
        #    print("FLReportViewer::exec(): Se ha detectado una llamada recursiva")
        #    return

        if self._report_engine and hasattr(self._report_engine, "_parser"):
            pdf_file = self._report_engine._parser.get_file_name()

        if not utils_base.is_library():
            if application.USE_REPORT_VIEWER:
                self._w = FLWidgetReportViewer(self)
                self._w.show()
                self._w._file_name = pdf_file
                self._w.refresh()
                self.slotFirstPage()
            else:
                qsatypes.SysBaseType.openUrl(pdf_file)

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
        if self._report_engine is None:
            LOGGER.warning("report_engine is mepty!")
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

        result = self._report_engine.renderReport(init_row, init_col, flags)
        self.report_ = self._report_engine._parser._document.pages
        return result

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
        return self.sizeHint()

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

        printer_name = self._printer_name
        num_copies = self._num_copies
        color_mode = self._color_mode

        self.report_printed = self._report_engine.printReport(printer_name, num_copies, color_mode)

    def printReportToPDF(self, file_name: str = "") -> None:
        """Print report to pdf."""

        if self.slot_print_disabled:
            return

        pdf_file = self._report_engine._parser.get_file_name()
        if pdf_file and file_name:
            shutil.copyfile(pdf_file, file_name)
            self.report_printed = True

    @decorators.pyqt_slot(int)
    def setResolution(self, dpi: int) -> None:
        """Set resolution."""
        settings.SETTINGS.set_value("rptViewer/dpi", dpi)
        self.dpi_ = dpi
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
            self._w.setDefaults()

    @decorators.not_implemented_warn
    def updateReport(self) -> None:
        """Update report."""

        pass

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
        self.slotUpdateDisplay()

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

        if self._w:
            return self._w._current_page or -1

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
        if self._report_engine and hasattr(self._report_engine, "_parser"):
            return self._report_engine._parser._page_size
        return -1

    def pageCount(self) -> int:
        """Return number of pages."""
        if self._report_engine:
            return self._report_engine.number_pages()
        return -1

    @decorators.not_implemented_warn
    def setStyleName(self, style: str) -> None:
        """Set style name."""
        # self._style_name = style

    # @decorators.beta_implementation
    # def setReportPages(self, pgs: Any) -> None:
    #    """Add pages to actual report."""
    #    self.setReportEngine(None)
    #    self.qry_ = None
    #    self.xml_data_ = QtXml.QDomNode()
    #    self.report_viewer.setReportPages(pgs.pageCollection() if pgs else 0)
    #    self.report_ = self.report_viewer.reportPages()

    @decorators.beta_implementation
    def setName(self, name: str) -> None:
        """Set report name."""
        self.name_ = name

    @decorators.beta_implementation
    def name(self) -> str:
        """Return report name."""
        return self.name_


class FLWidgetReportViewer(QtWidgets.QMainWindow):
    """FLWidgetReportViewer."""

    _internal: "FLReportViewer"
    _fr_mail: "QtWidgets.QFrame"
    _auto_close: bool
    _auto_widget: "QtWidgets.QCheckBox"
    _pages: List["QImage"]
    _file_name: str
    _image_label: "QtWidgets.QLabel"
    _scroll_area: "QtWidgets.QScrollArea"
    _scale_factor: int
    _current_page: int
    _default_pix: int = 780
    _default_res: int = 300

    def __init__(self, report_viewer: "FLReportViewer") -> None:
        """Initialize."""

        super().__init__()
        self.setObjectName("FLWidgetReportViewer")

        from pineboolib.q3widgets import qframe, qcheckbox, qspinbox

        self._internal = report_viewer
        self._internal._auto_close = settings.SETTINGS.value("rptViewer/autoClose", False)
        form_path = utils_base.filedir("fllegacy/forms/FLWidgetReportViewer.ui")
        self = flmanagermodules.FLManagerModules.createUI(form_path, None, self)
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self._fr_mail = self.findChild(qframe.QFrame, "frEMail")
        self._auto_widget = self.findChild(qcheckbox.QCheckBox, "chkAutoClose")
        self._pixel_control = self.findChild(qspinbox.QSpinBox, "spnPixel")
        self._resolution_control = self.findChild(qspinbox.QSpinBox, "spnResolution")

        self._pixel_control.setValue(self._internal._report_engine._rel_dpi)
        self._resolution_control.setValue(self._internal.dpi_)

        self._auto_widget.setChecked(self._auto_close)
        self._fr_mail.hide()
        self._image_label = QtWidgets.QLabel()
        self._image_label.setBackgroundRole(QPalette.ColorRole.Base)
        self._image_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored
        )
        self._image_label.setScaledContents(True)
        self._scroll_area = QtWidgets.QScrollArea()
        self._scroll_area.setBackgroundRole(QPalette.ColorRole.Dark)
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
        return getattr(self._internal, name, None)

    def setAutoClose(self) -> None:
        """Set autoclose."""

        self._internal._auto_close = self._auto_widget.isChecked()
        settings.SETTINGS.set_value("rptViewer/autoClose", self._internal._auto_close)

    def close(self) -> None:
        """Close form."""

        super().close()

    def refresh(self) -> None:
        """Set page to centralWidget."""
        self._pages = convert_from_path(
            self._file_name, dpi=self._internal.dpi_, output_folder=application.PROJECT.tmpdir
        )
        self._current_page = -1
        self.clear()

    def setDefaults(self) -> None:
        """Set defaults values."""

        self._pixel_control.setValue(self._default_pix)
        self._resolution_control.setValue(self._default_res)
        self._scale_factor = 1
        self.refresh()
        self.set_page(0)

    def set_page(self, num) -> None:
        """Set page."""
        if self._current_page == num:
            return
        image = self._pages[num] if self._pages else None
        if image is not None:
            self._image_label.clear()
            self._current_page = num
            image_qt = ImageQt(image)
            width_ = 780
            height_ = 591
            scaled_size = QtCore.QSize(width_ * self._scale_factor, height_ * self._scale_factor)
            scaled = image_qt.scaled(
                scaled_size,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            pix = QPixmap.fromImage(scaled)
            self._image_label.setPixmap(pix)
            self._image_label.adjustSize()
            self._scroll_area.setVisible(True)

    def clear(self) -> None:
        """Clear current page."""
        self._scroll_area.setVisible(False)
        self._current_page = None
        # print("Borra centralwidget")
