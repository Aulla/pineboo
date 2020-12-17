"""Flreportviewer module."""
from PyQt5 import QtWidgets, QtCore, QtXml

from pineboolib.core import decorators
from pineboolib.core.utils import utils_base
from pineboolib.application.qsatypes.sysbasetype import SysBaseType
from . import flutil
from . import flsqlquery
from . import flsqlcursor

from .flreportengine import FLReportEngine
from pineboolib import logging

from typing import Any, List, Mapping, Sized, Union, Dict, Optional, Callable
from PyQt5.QtGui import QColor

import shutil

LOGGER = logging.get_logger(__name__)

AQ_USRHOME = "."  # FIXME


class InternalReportViewer(QtWidgets.QWidget):
    """InternalReportViewer class."""

    report_engine_: Optional[FLReportEngine]
    dpi_: int
    report_: List[Any]
    num_copies: int

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """Inicialize."""
        super().__init__(parent)
        self.report_engine_ = None
        self.dpi_ = 300
        self.report_ = []
        self.num_copies = 1

    def setReportEngine(self, report_engine: FLReportEngine) -> None:
        """Set report engine."""

        self.report_engine_ = report_engine

    def resolution(self) -> int:
        """Return resolution."""

        return self.dpi_

    def reportPages(self) -> List[Any]:
        """Return report pages."""

        return self.report_

    def renderReport(self, init_row: int, init_col: int, flags: List[int]) -> Any:
        """Render report."""

        if self.report_engine_ is None:
            raise Exception("renderReport. self.report_engine_ is empty!")

        return self.report_engine_.renderReport(init_row, init_col, flags)

    def setNumCopies(self, num_copies: int) -> None:
        """Set number of copies."""
        self.num_copies = num_copies

    def __getattr__(self, name: str) -> Callable:
        """Return attributes from report engine."""
        return getattr(self.report_engine_, name, None)


class FLReportViewer(QtWidgets.QWidget):
    """FLReportViewer class."""

    pdfFile: str
    Append: int
    Display: int
    PageBreak: int
    _spn_resolution: int
    report_: List[Any]
    qry_: Any
    xml_data_: Any
    template_: Any
    autoClose_: bool
    slot_print_disabled: bool
    slot_exported_disabled: bool
    _style_name: str

    PrintGrayScale = 0
    PrintColor = 1

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        name: Optional[str] = None,
        embed_in_parent: bool = False,
        report_engine: Optional[FLReportEngine] = None,
    ) -> None:
        """Inicialize."""

        super().__init__(parent)

        self.loop_ = False
        self.eventloop = QtCore.QEventLoop()
        self.report_printed = False
        self.report_engine_: Optional[Any] = None
        self.report_ = []
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

        if self.report_viewer is None:
            raise Exception("self.report_viewer is empty!")

        self.report_ = self.report_viewer.reportPages()

    def rptViewer(self) -> "InternalReportViewer":
        """Return report viewer."""
        return self.report_viewer

    def report_engine(self) -> FLReportEngine:
        """Return report engine."""

        if self.report_engine_ is None:
            raise Exception("report_engine_ is not defined!")
        return self.report_engine_

    def setReportEngine(self, report_engine: Optional[FLReportEngine] = None) -> None:
        """Set report engine."""

        if self.report_engine_ == report_engine:
            return

        sender = self.sender()
        no_destroy = not (sender and sender == self.report_engine_)

        self.report_engine_ = report_engine
        if self.report_engine_ is not None:
            self.template_ = self.report_engine_.rptNameTemplate()
            self.qry_ = self.report_engine_.rptQueryData()

            if no_destroy:
                self.report_viewer.setReportEngine(self.report_engine_)

    def exec_(self) -> str:
        """Show report."""
        # if self.loop_:
        #    print("FLReportViewer::exec(): Se ha detectado una llamada recursiva")
        #    return
        if self.report_viewer.report_engine_ and hasattr(
            self.report_viewer.report_engine_, "parser_"
        ):
            pdf_file = self.report_viewer.report_engine_.parser_.get_file_name()

        if not utils_base.is_library():

            SysBaseType.openUrl(pdf_file)

        return pdf_file

    @decorators.beta_implementation
    def csvData(self) -> str:
        """Return csv data."""

        return self.report_engine_.csvData() if self.report_engine_ else ""

    def renderReport(
        self,
        init_row: int = 0,
        init_col: int = 0,
        append_or_flags: Union[bool, Sized, Mapping[int, Any]] = None,
        display_report: bool = False,
    ) -> bool:
        """Render report."""
        if not self.report_engine_:
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
        self.report_ = self.report_viewer.reportPages()
        return ret

    def renderReport2(
        self,
        init_row: int = 0,
        init_col: int = 0,
        append_or_flags: Union[bool, Sized, Mapping[int, Any]] = None,
        display_report: bool = False,
    ) -> bool:
        """Render report."""
        if not self.report_engine_:
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
        self.report_ = self.report_viewer.reportPages()
        return ret

    def setReportData(
        self, data: Union["flsqlcursor.FLSqlCursor", "flsqlquery.FLSqlQuery", "QtXml.QDomNode"]
    ) -> bool:
        """Set data to report."""
        if isinstance(data, flsqlquery.FLSqlQuery):
            self.qry_ = data
            if self.report_engine_ and self.report_engine_.setReportData(data):
                self.xml_data_ = self.report_engine_.rptXmlData()
                return True
            return False
        elif isinstance(data, flsqlcursor.FLSqlCursor):
            if not self.report_engine_:
                return False
            return self.report_engine_.setReportData(data)
        elif isinstance(data, QtXml.QDomNode):
            self.xml_data_ = data
            self.qry_ = None
            if not self.report_engine_:
                return False
            return self.report_engine_.setReportData(data)
        return False

    def setReportTemplate(
        self, template: Union["QtXml.QDomNode", str], style: Optional[str] = None
    ) -> bool:
        """Set template to report."""
        if isinstance(template, QtXml.QDomNode):
            self._xml_template = template
            self.template_ = ""

            if not self.report_engine_:
                return False

            if style is not None:
                self.setStyleName(style)

            self.report_engine_.setFLReportTemplate(template)

            return True
        else:
            self.template_ = template
            self._style_name = style
            if self.report_engine_ and self.report_engine_.setFLReportTemplate(template):
                # self.setStyleName(style)
                self._xml_template = self.report_engine_.rptXmlTemplate()
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

    def disableSlotsPrintExports(disable_print: bool = False, disable_export: bool = False):
        """Disable export and print slots."""

        self.slot_print_disabled = disable_print
        self.slot_exported_disabled = disable_export

    @decorators.not_implemented_warn
    def printReport(self) -> None:
        """Print a report."""

        if self.slot_print_disabled:
            return

        # color
        # resolucion
        # copias

        self.report_printed = True

    @decorators.beta_implementation
    def printReportToPDF(self, file_name: str = "") -> None:
        """print report to pdf."""

        if self.slot_print_disabled:
            return

        if not file_name:
            raise Exception("invalid filename '%s'" % file_name)

        try:
            pdf_file = self.report_viewer.report_engine_.parser_.get_file_name()
            shutil.copyfile(pdf_file, file_name)
        except Exception as error:
            LOGGER.warning("Error printReportToPDF : %s", str(error))

    @decorators.pyqt_slot(int)
    @decorators.beta_implementation
    def setResolution(self, dpi: int) -> None:
        """Set resolution."""
        flutil.FLUtil.writeSettingEntry("rptViewer/dpi", str(dpi))
        self.report_viewer.setResolution(dpi)

    @decorators.pyqt_slot(int)
    @decorators.beta_implementation
    def setPixel(self, rel_dpi: int) -> None:
        """Set pixel size."""
        flutil.FLUtil.writeSettingEntry("rptViewer/pixel", str(float(rel_dpi / 10.0)))
        if self.report_engine_:
            self.report_engine_.setRelDpi(rel_dpi / 10.0)

    @decorators.beta_implementation
    def setDefaults(self) -> None:
        """Set default values."""
        import platform

        self._spn_resolution = 300
        system = platform.system()
        if system == "Linux":
            self._spn_pixel = 780
        elif system == "Windows":
            # FIXME
            pass
        elif system == "Darwin":
            # FIXME
            pass

    @decorators.beta_implementation
    def updateReport(self) -> None:
        """Update report."""
        self.requestUpdateReport.emit()

        if self.qry_ or (self.xml_data_ and self.xml_data_ != ""):
            if not self.report_engine_:
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

    @decorators.beta_implementation
    def getCurrentPage(self) -> Any:
        """Return curent page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getCurrentPage(), self)
        return 0

    @decorators.beta_implementation
    def getFirstPage(self) -> Any:
        """Return first page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getFirstPage(), self)
        return 0

    @decorators.beta_implementation
    def getPreviousPage(self) -> Any:
        """Return previous page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getPreviousPage(), self)
        return 0

    @decorators.beta_implementation
    def getNextPage(self) -> Any:
        """Return next page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getNextPage(), self)
        return 0

    @decorators.beta_implementation
    def getLastPage(self) -> Any:
        """Return last page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getLastPage(), self)
        return 0

    @decorators.beta_implementation
    def getPageAt(self, num: int) -> Any:
        """Return actual page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getPageAt(i), self)
        return 0

    @decorators.beta_implementation
    def updateDisplay(self) -> None:
        """Update display."""
        self.report_viewer.slotUpdateDisplay()

    @decorators.beta_implementation
    def clearPages(self) -> None:
        """Clear report pages."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.clear()
        pass

    @decorators.beta_implementation
    def appendPage(self) -> None:
        """Add a new page."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.appendPage()
        pass

    @decorators.beta_implementation
    def getCurrentIndex(self) -> int:
        """Return current index position."""

        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.getCurrentIndex()
        return -1

    @decorators.beta_implementation
    def setCurrentPage(self, idx: int) -> None:
        """Set current page index."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setCurrentPage(idx)
        pass

    @decorators.beta_implementation
    def setPageSize(
        self, size: Union[QtCore.QSize, int], orientation: Optional[int] = None
    ) -> None:
        """Set page size."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageSize(s)
        pass

    @decorators.beta_implementation
    def setPageOrientation(self, orientation: int) -> None:
        """Set page orientation."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageOrientation(o)
        pass

    @decorators.beta_implementation
    def setPageDimensions(self, dim: QtCore.QSize) -> None:
        """Set page dimensions."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageDimensions(dim)
        pass

    @decorators.beta_implementation
    def pageSize(self) -> QtCore.QSize:
        """Return page size."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.pageSize()
        return -1

    @decorators.beta_implementation
    def pageOrientation(self) -> int:
        """Return page orientation."""
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.pageOrientation()
        return -1

    def pageDimensions(self) -> QtCore.QSize:
        """Return page dimensions."""
        if self.report_viewer.report_engine_ and hasattr(
            self.report_viewer.report_engine_, "parser_"
        ):
            return self.report_viewer.report_engine_.parser_._page_size
        return -1

    def pageCount(self) -> int:
        """Return number of pages."""
        if self.report_viewer.report_engine_:
            return self.report_viewer.report_engine_.number_pages()
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
