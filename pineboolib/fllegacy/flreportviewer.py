from PyQt5 import QtWidgets  # type: ignore
from PyQt5 import QtCore  # type: ignore
from PyQt5 import QtXml  # type: ignore
from PyQt5.QtCore import Qt, QObject  # type: ignore
from PyQt5.Qt import QFileDialog, QMessageBox  # type: ignore

from pineboolib.core import decorators

from pineboolib.fllegacy.flutil import FLUtil

# from pineboolib.fllegacy.flpicture import FLPicture
from pineboolib.fllegacy.flsqlquery import FLSqlQuery
from pineboolib.fllegacy.flsqlcursor import FLSqlCursor
from pineboolib.fllegacy.flstylepainter import FLStylePainter
from pineboolib.fllegacy.flreportengine import FLReportEngine
from pineboolib import logging

from typing import Any, List, Mapping, Sized, Union, Dict


AQ_USRHOME = "."  # FIXME


class internalReportViewer(QObject):

    rptEngine_: Any
    dpi_ = 0
    report_: List[Any]
    num_copies = 1

    def __init__(self, parent) -> None:
        super(internalReportViewer, self).__init__(parent)
        self.dpi_ = 300
        self.report_ = []
        self.num_copies = 1

    def setReportEngine(self, rptEngine) -> None:
        self.rptEngine_ = rptEngine

    def resolution(self) -> int:
        return self.dpi_

    def reportPages(self) -> List[Any]:
        return self.report_

    def renderReport(self, init_row, init_col, flags) -> Any:
        if self.rptEngine_ is None:
            raise Exception("renderReport. self.rptEngine_ is empty!")

        return self.rptEngine_.renderReport(init_row, init_col, flags)

    def setNumCopies(self, num_copies) -> None:
        self.num_copies = num_copies

    def __getattr__(self, name: str) -> Any:
        return getattr(self.rptEngine_, name, None)


class FLReportViewer(QtWidgets.QWidget):

    pdfFile: str
    Append: int
    Display: int
    PageBreak: int
    report_: List[Any]
    qry_: Any
    xmlData_: Any
    template_: Any

    def __init__(self, parent=None, name=0, embedInParent=False, rptEngine=None) -> None:
        # pParam = 0 if parent and embedInParent else 0
        # pParam = pParam | Qt.WindowMaximizeButtonHint | Qt.WindowTitleHint
        # pParam = pParam | 0 | Qt.Dialog | Qt.WindowModal
        # pParam = pParam | Qt.WindowSystemMenuHint

        super(FLReportViewer, self).__init__(parent)
        self.logger = logging.getLogger("FLReportViewer")
        self.loop_ = False
        self.eventloop = QtCore.QEventLoop()
        self.reportPrinted_ = False
        self.rptEngine_ = None
        self.report_ = []
        self.slotsPrintDisabled_ = False
        self.slotsExportedDisabled_ = False
        self.printing_ = False
        self.embedInParent_ = True if parent and embedInParent else False
        self.ui_: Dict[str, QtCore.QObject] = {}

        self.Display = 1
        self.Append = 1
        self.PageBreak = 1
        self.stylepainter: FLStylePainter = FLStylePainter()
        from pineboolib.plugins.dgi.dgi_qt.dgi_qt3ui import loadUi
        from pineboolib.core.utils.utils_base import filedir

        loadUi(filedir("forms/FLWidgetReportViewer.ui"), self)
        self.ui_["FLWidgetReportViewer"] = self.child("FLWidgetReportViewer")
        self.ui_["frEMail"] = self.child("frEMail")
        self.ui_["ledStyle"] = self.child("ledStyle")

        # if not name:
        #    self.setName("FLReportViewer")

        # if self.embedInParent_:
        #    self.autoClose_ = False
        #    self.ui_["menubar"].hide()
        #    self.ui_["chkAutoClose"].hide()
        #    self.ui_["spnResolution"].hide()
        #    self.ui_["spnPixel"].hide()
        #    self.ui_["salir"].setVisible(False)

        #   if not parent.layout():
        #        lay = QtCore.QVBoxLayout(parent)
        #        lay.addWidget(self)
        #    else:
        #        parent.layout().add(self)
        # else:
        #    self.autoClose_ = bool(FLUtil().readSettingEntry(
        #        "rptViewer/autoClose", "false"))
        #    self.ui_["chkAutoClose"].setChecked(self.autoClose_)

        self.rptViewer_ = internalReportViewer(self)
        self.setReportEngine(FLReportEngine(self) if rptEngine is None else rptEngine)

        # self.setFont(QtWidgets.QApplication.font())
        # self.setFocusPolicy(Qt.StrongFocus)

        # util = FLUtil()

        # self.ui_["lePara"].setText(str(util.readSettingEntry("email/to")))
        # self.ui_["leDe"].setText(str(util.readSettingEntry("email/from")))
        # self.ui_["leMailServer"].setText(
        #    str(util.readSettingEntry("email/mailserver")))

        # wrv = self.ui_["FLWidgetReportViewer"]
        # self.initCentralWidget_ = wrv.centralWidget()

        # self.smtpClient_ = FLSmtpClient(self)
        # self.smtpClient_.status.connect(self.ui_["lblEstado"].setText)

        # wrv.setCentralWidget(self.rptViewer_)
        # self.ui_["frEMail"].hide()
        # if self.initCentralWidget_:
        #    self.initCentralWidget_.hide()
        # if not self.embedInParent_:
        #    self.ui_["spnResolution"].setValue(int(util.readSettingEntry(
        #        "rptViewer/dpi", str(self.rptViewer_.resolution()))))
        #    self.ui_["spnPixel"].setValue(float(util.readSettingEntry(
        #        "rptViewer/pixel", float(self.rptEngine_.relDpi()))) * 10.)
        if self.rptViewer_ is None:
            raise Exception("self.rptViewer_ is empty!")

        self.report_ = self.rptViewer_.reportPages()

    def rptViewer(self) -> internalReportViewer:
        return self.rptViewer_

    def rptEngine(self) -> Any:
        return self.rptEngine_

    def setReportEngine(self, r=None) -> None:
        if self.rptEngine_ == r:
            return

        sender = self.sender()
        noSigDestroy = not (sender and sender == self.rptEngine_)

        self.rptEngine_ = r
        if self.rptEngine_:
            self.template_ = self.rptEngine_.rptNameTemplate()
            self.qry_ = self.rptEngine_.rptQueryData()
            # if self.rptEngine_.rptXmlTemplate():
            #    self.xmlTemplate_ = self.rptEngine_.rptXmlTemplate()
            # if self.rptEngine_.rptXmlTemplate():
            #    self.xmlData_ = self.rptEngine_.rptXmlTemplate()
            # self.rptEngine_.destroyed.connect(self.setReportEngine)

            # self.ui_["ledStyle"].setDisabled(False)
            # self.ui_["save_page_SVG"].setDisabled(False)
            # self.ui_["save_page_tpl_SVG"].setDisabled(False)
            # self.ui_["load_tpl_SVG"].setDisabled(False)
        # else:
        # self.ui_["ledStyle"].setDisabled(True)
        # self.ui_["save_page_SVG"].setDisabled(True)
        # self.ui_["save_page_tpl_SVG"].setDisabled(True)
        # self.ui_["load_tpl_SVG"].setDisabled(True)

        if noSigDestroy:
            self.rptViewer_.setReportEngine(self.rptEngine_)

    def exec_(self) -> None:
        # if self.loop_:
        #    print("FLReportViewer::exec(): Se ha detectado una llamada recursiva")
        #    return
        if hasattr(self.rptViewer_.rptEngine_, "parser_"):
            pdf_file = self.rptViewer_.rptEngine_.parser_.get_file_name()
            from pineboolib.application import project

            project.call("sys.openUrl", [pdf_file], None, True)
        # self.eventloop.exec_()

        # if self.embedInParent_:
        #    return

        # self.loop_ = True
        # self.clearWFlags(Qt.WShowModal) # FIXME

    @decorators.BetaImplementation
    def csvData(self):
        return self.rptEngine_.csvData() if self.rptEngine_ else ""

    @decorators.BetaImplementation
    def closeEvent(self, e):
        from pineboolib.application.utils.geometry import saveGeometryForm

        if self.printing_:
            return

        self.show()
        self.frameGeometry()
        self.hide()

        if not self.embedInParent_:
            geo = QtCore.QRect(self.x(), self.y(), self.width(), self.height())
            saveGeometryForm(self.name(), geo)

        if self.loop_ and not self.embedInParent_:
            self.loop_ = False

        self.eventloop.exit()

        super(FLReportViewer, self).closeEvent(e)
        self.deleteLater()

    @decorators.BetaImplementation
    def showEvent(self, e):
        super(FLReportViewer, self).showEvent(e)

        if not self.embedInParent_:
            geo = QtCore.QRect(self.geometry())
            if geo and geo.isValid():
                desk = QtWidgets.QApplication.desktop().availableGeometry(self)
                inter = desk.intersected(geo)
                self.resize(geo.size())
                geodim = geo.width() * geo.height()
                if inter.width() * inter.height() > (geodim / 20):
                    self.move(geo.topLeft())

    def renderReport(self, init_row=0, init_col=0, append_or_flags: Union[Sized, Mapping[int, Any]] = None, display_report=None) -> Any:

        if not self.rptEngine_:
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

        ret = self.rptViewer_.renderReport(init_row, init_col, flags)
        self.report_ = self.rptViewer_.reportPages()
        return ret

    @decorators.BetaImplementation
    def slotFirstPage(self):
        self.rptViewer_.slotFirstPage()

    @decorators.BetaImplementation
    def slotLastPage(self):
        self.rptViewer_.slotLastPage()

    @decorators.BetaImplementation
    def slotNextPage(self):
        self.rptViewer_.slotNextPage()

    @decorators.BetaImplementation
    def slotPrevPage(self):
        self.rptViewer_.slotPrevPage()

    @decorators.BetaImplementation
    def slotZoomUp(self):
        self.rptViewer_.slotZoomUp()

    @decorators.BetaImplementation
    def slotZoomDown(self):
        self.rptViewer_.slotZoomDown()

    @decorators.BetaImplementation
    def exportFileCSVData(self):
        if self.slotsExportedDisabled_:
            return

        util = FLUtil()
        fileName = QFileDialog.getSaveFileName(
            self, util.translate("app", "Exportar a CSV"), "", util.translate("app", "Fichero CSV (*.csv *.txt)")
        )

        if not fileName or fileName == "":
            return

        if not fileName.upper().contains(".CSV"):
            fileName = fileName + ".csv"

        q = QtCore.QMessageBox.question(
            self,
            util.translate("app", "Sobreescribir {}").format(fileName),
            util.translate("app", "Ya existe un fichero llamado {}. ¿Desea sobreescribirlo?").format(fileName),
            util.translate("app", "&Sí"),
            util.translate("app", "&No"),
            "",
            0,
            1,
        )

        if QtCore.QFile.exists(fileName) and q:
            return

        file = QtCore.QFile(fileName)

        if file.open(Qt.IO_WriteOnly):
            stream = QtCore.QTextStream(file)
            stream << self.csvData() << "\n"
            file.close()
        else:
            QtCore.QMessageBox.critical(
                self,
                util.translate("app", "Error abriendo fichero"),
                util.translate("app", "No se pudo abrir el fichero {} para escribir: {}").format(
                    fileName, QtWidgets.QApplication.translate("QFile", file.errorString())
                ),
            )

    @decorators.BetaImplementation
    @QtCore.pyqtSlot()
    def exportToPDF(self):
        if self.slotsExportedDisabled_:
            return

        util = FLUtil()
        fileName = QFileDialog.getSaveFileName(
            self, util.translate("app", "Exportar a PDF"), "", util.translate("app", "Fichero PDF (*.pdf)")
        )

        if fileName[0] == "":
            return

        if fileName[0].upper().find(".PDF") == -1:
            fileName = fileName[0] + ".pdf"

        if QtCore.QFile.exists(fileName):

            q = QMessageBox.question(
                self,
                util.translate("app", "Sobreescribir {}").format(fileName),
                util.translate("app", "Ya existe un fichero llamado {}. ¿Desea sobreescribirlo?").format(fileName),
                util.translate("app", "&Sí"),
                util.translate("app", "&No"),
                "",
                0,
                1,
            )
            if q:
                return

        self.slotPrintReportToPdf(fileName)

    @decorators.BetaImplementation
    @QtCore.pyqtSlot()
    def sendEMailPDF(self):
        t = self.ui_["leDocumento"].text()
        util = FLUtil()
        name = "informe.pdf" if not t or t == "" else t
        fileName = QtCore.QFileDialog.getSaveFileName(
            AQ_USRHOME + "/" + name + ".pdf",
            util.translate("app", "Fichero PDF a enviar (*.pdf)"),
            self,
            util.translate("app", "Exportar a PDF para enviar"),
            util.translate("app", "Exportar a PDF para enviar"),
        )

        if not fileName or fileName == "":
            return

        if not fileName.upper().contains(".PDF"):
            fileName = fileName + ".pdf"

        q = QtCore.QMessageBox.question(
            self,
            util.translate("app", "Sobreescribir {}").format(fileName),
            util.translate("app", "Ya existe un fichero llamado {}. ¿Desea sobreescribirlo?").format(fileName),
            util.translate("app", "&Sí"),
            util.translate("app", "&No"),
            "",
            0,
            1,
        )

        if QtCore.QFile.exists(fileName) and q:
            return

        autoCloseSave = self.autoClose_
        self.slotPrintReportToPdf(fileName)
        self.autoClose_ = autoCloseSave

        util.writeSettingEntry("email/to", self.ui_["lePara"].text())
        util.writeSettingEntry("email/from", self.ui_["leDe"].text())
        util.writeSettingEntry("email/mailserver", self.ui_["leMailServer"].text())

        fi = QtCore.QFileInfo(fileName)
        name = fi.fileName()

        self.smtpClient_.setMailServer(self.ui_["leMailServer"].text())
        self.smtpClient_.setTo(self.ui_["lePara"].text())
        self.smtpClient_.setFrom(self.ui_["leDe"].text())
        asutxt = self.ui_["leAsunto"].text()
        self.smtpClient_.setSubject(name if asutxt == "" else asutxt)
        self.smtpClient_.setBody(self.ui_["leCuerpo"].text() + "\n\n")

        html = '<html><body><a href="http://abanq.org/">'
        html += '<img src="cid:logo.png@3d8b627b6292"/>'
        html += "</a><br/><br/></body></html>"
        self.smtpClient_.addTextPart(html, "text/html")
        self.smtpClient_.addAttachment(fileName)
        self.smtpClient_.startSend()

    @decorators.BetaImplementation
    def showInitCentralWidget(self, show):
        wrv = self.ui_["FLWidgetReportViewer"]
        if show:
            self.rptViewer_.hide()
            wrv.setCentralWidget(self.initCentralWidget_)
            self.ui["leDocumento"].setText("doc-" + str(QtCore.QDateTime.currentDateTime()).replace(":", ",").replace(" ", ""))
            self.ui_["frEMail"].show()
            self.initCentralWidget_.show()
        else:
            self.initCentralWidget_.hide()
            self.ui_["frEMail"].hide()
            wrv.setCentralWidget(self.rptViewer_)
            self.rptViewer_.show()

    @decorators.BetaImplementation
    def saveSVGStyle(self):
        util = FLUtil()
        if self.report_:
            fileName = QtCore.QFileDialog.getSaveFileName(
                "",
                util.translate("app", "Fichero SVG (*.svg)"),
                self,
                util.translate("app", "Guardar en SVG"),
                util.translate("app", "Guardar en SVG"),
            )

            if not fileName or fileName == "":
                return

            if not fileName.upper().contains(".SVG"):
                fileName = fileName + ".svg"

            q = QtCore.QMessageBox.question(
                self,
                util.translate("app", "Sobreescribir {}").format(fileName),
                util.translate("app", "Ya existe un fichero llamado {}. ¿Desea sobreescribirlo?").format(fileName),
                util.translate("app", "&Sí"),
                util.translate("app", "&No"),
                "",
                0,
                1,
            )

            if QtCore.QFile.exists(fileName) and q:
                return

            self.stylepainter.setSVGMode(True)
            self.updateReport()
            self.stylepainter.setSVGMode(False)

            fileNames: List[str] = []
            # FIXME: self.report_ is just a List[]
            # for i in range(self.report_.pageCount()):
            #     fname = fileName + str(i)
            #     fileNames.append(fname)
            #     page = self.report_.getPageAt(i)
            #     psize = self.report_.pageDimensions()
            #     page.setBoundingRect(QtCore.QRect(QtCore.QPoint(0, 0), psize))
            #     page.save(fname, "svg")

            self.stylepainter.normalizeSVGFile(fileName, fileNames)

            self.updateReport()

    @decorators.BetaImplementation
    def saveSimpleSVGStyle(self):
        backStyleName = self.styleName_
        self.styleName_ = "_simple"
        self.saveSVGStyle()
        self.styleName_ = backStyleName
        self.updateReport()

    @decorators.BetaImplementation
    def loadSVGStyle(self):
        util = FLUtil()
        fileName = QtCore.QFileDialog.getOpenFileName(
            "",
            util.translate("app", "Fichero SVG (*.svg)"),
            self,
            util.translate("app", "Cargar estilo SVG"),
            util.translate("app", "Cargar estilo SVG"),
        )

        if not fileName or fileName == "":
            return

        self.ui_["ledStyle"].setText("file:" + fileName)
        self.updateReport()

    @decorators.BetaImplementation
    def slotExit(self):
        self.close()

    @decorators.BetaImplementation
    def slotPrintReportToPs(self, outPsFile):
        if self.slotsPrintDisabled_:
            return

        self.setDisabled(True)
        self.printing_ = True
        self.reportPrinted_ = self.rptViewer_.printReportToPs(outPsFile)
        if self.reportPrinted_ and self.autoClose_:
            QtCore.QTimer.singleShot(0, self.slotExit)
        self.printing_ = False
        self.setDisabled(False)

    @decorators.BetaImplementation
    def slotPrintReportToPdf(self, outPdfFile):
        if self.slotsPrintDisabled_:
            return

        self.setDisabled(True)
        self.printing_ = True
        self.reportPrinted_ = self.rptViewer_.printReportToPdf(outPdfFile)
        if self.reportPrinted_ and self.autoClose_:
            QtCore.QTimer.singleShot(0, self.slotExit)
        self.printing_ = False
        self.setDisabled(False)

    @decorators.BetaImplementation
    def slotPrintReport(self):
        if self.slotsPrintDisabled_:
            return

        self.setDisabled(True)
        self.printing_ = True
        self.reportPrinted_ = self.rptViewer_.printReport()
        if self.reportPrinted_ and self.autoClose_:
            QtCore.QTimer.singleShot(0, self.slotExit)
        self.printing_ = False
        self.setDisabled(False)

    def setReportData(self, d) -> Any:
        if isinstance(d, FLSqlQuery):
            self.qry_ = d
            if self.rptEngine_ and self.rptEngine_.setReportData(d):
                self.xmlData_ = self.rptEngine_.rptXmlData()
                return True
            return False
        elif isinstance(d, FLSqlCursor):
            if not self.rptEngine_:
                return False
            return self.rptEngine_.setReportData(d)
        elif isinstance(d, QtXml.QDomNode):
            self.xmlData_ = d
            self.qry_ = None
            if not self.rptEngine_:
                return False
            return self.rptEngine_.setReportData(d)
        return False

    def setReportTemplate(self, t, style=None) -> bool:
        if isinstance(t, QtXml.QDomNode):
            self.xmlTemplate_ = t
            self.template_ = ""
            self.styleName_ = style
            if not self.rptEngine_:
                return False

            self.rptEngine_.setFLReportTemplate(t)
            self.setStyleName(style)
            return True
        else:
            self.template_ = t
            self.styleName_ = style
            if self.rptEngine_ and self.rptEngine_.setFLReportTemplate(t):
                # self.setStyleName(style)
                self.xmlTemplate_ = self.rptEngine_.rptXmlTemplate()
                return True

        return False

    @decorators.BetaImplementation
    def sizeHint(self):
        return self.rptViewer_.sizeHint()

    @decorators.BetaImplementation
    def setNumCopies(self, numCopies):
        self.rptViewer_.setNumCopies(numCopies)

    @decorators.BetaImplementation
    def setPrintToPos(self, ptp):
        self.rptViewer_.setPrintToPos(ptp)

    @decorators.BetaImplementation
    def setPrinterName(self, pName):
        self.rptViewer_.setPrinterName(pName)

    @decorators.BetaImplementation
    def reportPrinted(self):
        return self.reportPrinted_

    @decorators.BetaImplementation
    def setAutoClose(self, b):
        if self.embedInParent_:
            self.autoClose_ = False
        else:
            self.autoClose_ = b

    @QtCore.pyqtSlot(int)
    @decorators.BetaImplementation
    def setResolution(self, dpi):
        util = FLUtil()
        util.writeSettingEntry("rptViewer/dpi", str(dpi))
        self.rptViewer_.setResolution(dpi)

    @QtCore.pyqtSlot(int)
    @decorators.BetaImplementation
    def setPixel(self, relDpi):
        util = FLUtil()
        util.writeSettingEntry("rptViewer/pixel", str(float(relDpi / 10.0)))
        if self.rptEngine_:
            self.rptEngine_.setRelDpi(relDpi / 10.0)

    @decorators.BetaImplementation
    def setDefaults(self):
        self.spnResolution_.setValue(300)

        if True:
            # Linux
            self.spnPixel_.setValue(780)
        elif False:
            # WIN32 #FIXME
            pass
        else:
            # MAC #FIXME
            pass

    @decorators.BetaImplementation
    def updateReport(self):
        self.requestUpdateReport.emit()

        if self.qry_ or (self.xmlData_ and self.xmlData_ != ""):
            if not self.rptEngine_:
                self.setReportEngine(FLReportEngine(self))

            self.setResolution(self.spnResolution_.value())
            self.setPixel(self.spnPixel_.value())

            if self.template_ and self.template_ != "":
                self.setReportTemplate(self.template_, self.styleName_)
            else:
                self.setReportTemplate(self.xmlTemplate_, self.styleName_)

            if self.qry_:
                self.setReportData(self.qry_)
            else:
                self.setReportData(self.xmlData_)

            self.renderReport(0, 0, False, False)

        self.updateDisplay()

    @decorators.BetaImplementation
    def getCurrentPage(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getCurrentPage(), self)
        return 0

    @decorators.BetaImplementation
    def getFirstPage(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getFirstPage(), self)
        return 0

    @decorators.BetaImplementation
    def getPreviousPage(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getPreviousPage(), self)
        return 0

    @decorators.BetaImplementation
    def getNextPage(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getNextPage(), self)
        return 0

    @decorators.BetaImplementation
    def getLastPage(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getLastPage(), self)
        return 0

    @decorators.BetaImplementation
    def getPageAt(self, i):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return FLPicture(self.report_.getPageAt(i), self)
        return 0

    @decorators.BetaImplementation
    def updateDisplay(self):
        self.rptViewer_.slotUpdateDisplay()

    @decorators.BetaImplementation
    def clearPages(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.clear()
        pass

    @decorators.BetaImplementation
    def appendPage(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.appendPage()
        pass

    @decorators.BetaImplementation
    def getCurrentIndex(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.getCurrentIndex()
        return -1

    @decorators.BetaImplementation
    def setCurrentPage(self, idx):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setCurrentPage(idx)
        pass

    @decorators.BetaImplementation
    def setPageSize(self, s):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageSize(s)
        pass

    @decorators.BetaImplementation
    def setPageOrientation(self, o):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageOrientation(o)
        pass

    @decorators.BetaImplementation
    def setPageDimensions(self, dim):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     self.report_.setPageDimensions(dim)
        pass

    @decorators.BetaImplementation
    def pageSize(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.pageSize()
        return -1

    @decorators.BetaImplementation
    def pageOrientation(self):
        # FIXME: self.report_ is just a List[]
        # if self.report_:
        #     return self.report_.pageOrientation()
        return -1

    def pageDimensions(self) -> Any:
        if hasattr(self.rptViewer_.rptEngine_, "parser_"):
            return self.rptViewer_.rptEngine_.parser_._page_size
        return -1

    def pageCount(self) -> Any:
        if hasattr(self.rptViewer_, "rptEngine_"):
            return self.rptViewer_.rptEngine_.number_pages()
        return -1

    @decorators.BetaImplementation
    def setStyleName(self, style):
        self.styleName_ = style

    @decorators.BetaImplementation
    def rptViewerEmbedInParent(self, parentFrame):
        if not parentFrame:
            return

        self.ui_["FLWidgetReportViewer"].setCentralWidget(0)
        self.rptViewer_.reparent(parentFrame, 0, QtCore.QPoint(0, 0))

        if not parentFrame.layout():
            lay = QtCore.QVBoxLayout(parentFrame)
            lay.addWidget(self.rptViewer_)
        else:
            parentFrame.layout().add(self.rptViewer_)

        self.rptViewer_.show()

    @decorators.BetaImplementation
    def rptViewerReparent(self, parentFrame):
        if not parentFrame:
            return

        actExit = QtCore.QAction(self.child("salir", "QAction"))
        if actExit:
            actExit.setVisible(False)

        self.reparent(parentFrame, 0, QtCore.QPoint(0, 0))

        if not parentFrame.layout():
            lay = QtCore.QVBoxLayout(parentFrame)
            lay.addWidget(self)
        else:
            parentFrame.layout().add(self)

        self.show()

    @decorators.BetaImplementation
    def setReportPages(self, pgs):
        self.setReportEngine(0)
        self.qry_ = 0
        self.xmlData_ = QtXml.QDomNode()
        self.rptViewer_.setReportPages(pgs.pageCollection() if pgs else 0)
        self.report_ = self.rptViewer_.reportPages()

    @decorators.BetaImplementation
    def setColorMode(self, c):
        self.rptViewer_.setColorMode(c)

    @decorators.BetaImplementation
    def colorMode(self):
        return self.rptViewer_.colorMode()

    @decorators.BetaImplementation
    def disableSlotsPrintExports(self, dPrints=True, dExports=True):
        self.slotsPrintDisabled_ = dPrints
        self.slotsExportedDisabled_ = dExports

    @decorators.BetaImplementation
    def exportToOds(self):
        if self.slotsExportedDisabled_:
            return

        self.rptViewer_.exportToOds()

    @decorators.BetaImplementation
    def setName(self, n):
        self.name_ = n

    @decorators.BetaImplementation
    def name(self):
        return self.name_

    def __getattr__(self, name: str) -> Any:
        return getattr(self.rptViewer_, name, None)
