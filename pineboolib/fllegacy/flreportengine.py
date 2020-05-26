"""Flreportengine module."""
from typing import List
from PyQt5 import QtXml, QtWidgets, QtCore  # type: ignore
from PyQt5.QtXml import QDomNode as FLDomNodeInterface  # type: ignore # FIXME

from pineboolib.core import decorators
from pineboolib import logging
from pineboolib.application.database.pnsqlquery import PNSqlQuery
from typing import Any, Optional, Dict, Union

LOGGER = logging.get_logger(__name__)


class FLReportEngine(QtCore.QObject):
    """FLReportEngine class."""

    report_: Any
    rt_: Optional[str]

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Inicialize."""

        super().__init__(parent)
        self.private_ = FLReportEngine.FLReportEnginePrivate(self)
        self.rel_dpi_ = 78.0
        self.report_ = None
        self.rt_ = ""
        self.rd_: Optional[QtXml.QDomDocument] = None

        from pineboolib.application.parsers.parser_kut import kut2fpdf

        self.parser_: "kut2fpdf.Kut2FPDF" = kut2fpdf.Kut2FPDF()

    class FLReportEnginePrivate(object):
        """FLReportEnginePrivate."""

        rows_: Any
        q_field_mtd_list_: List[Any]
        q_field_list_: List[str]
        q_double_field_list_: List[str]
        q_group_dict_: Dict[int, str]
        q_img_fields_: List[int]
        qry_: Optional[PNSqlQuery]

        def __init__(self, q: "FLReportEngine") -> None:
            """Inicialize."""
            self.qry_ = None
            self.q_field_mtd_list_ = []
            self.q_group_dict_ = {}
            self.q_ = q
            self.template_ = ""
            self.rows_ = []
            self.q_field_list_ = []
            self.q_double_field_list_ = []
            self.q_img_fields_ = []
            self.report_ = None

        def addRowToReportData(self, level: int) -> None:
            """Add row to report data."""
            if not self.qry_ or not self.qry_.isValid():
                return

            row = self.q_.rptXmlData().createElement("Row")
            row.setAttribute("level", level)

            for i, it in enumerate(self.q_field_list_):
                strVal = str(self.qry_.value(it, False))
                if self.q_img_fields_:
                    if self.q_img_fields_[-1] == i:
                        self.q_img_fields_.append(self.q_img_fields_.pop())
                        if strVal in ["", "None"]:
                            row.setAttribute(it, strVal)
                            continue

                    key = self.qry_.value(i, False)
                    row.setAttribute(it, key)

                else:
                    row.setAttribute(it, strVal)

            self.rows_.appendChild(row)

        def groupBy(self, levelMax: int, va_: List[Any]) -> None:
            """Add a group by."""
            if not self.qry_ or not self.qry_.isValid():
                return

            # self.q_group_dict_
            lev = 0

            while lev < levelMax and str(self.qry_.value(self.q_group_dict_[lev])) == str(va_[lev]):
                lev += 1

            for i in range(lev, levelMax):
                self.addRowToReportData(i)
                va_[i] = str(self.qry_.value(self.q_group_dict_[i]))

            self.addRowToReportData(levelMax)

        def setQuery(self, qry: Optional[PNSqlQuery]) -> None:
            """Set query to the report."""
            self.qry_ = qry

            if self.qry_:
                self.q_field_list_ = self.qry_.fieldList()
                self.q_field_mtd_list_ = self.qry_.fieldMetaDataList()
                self.q_group_dict_ = self.qry_.groupDict()
                self.q_double_field_list_.clear()
                self.q_img_fields_.clear()

                if not self.q_field_mtd_list_:
                    return

                i = len(self.q_field_list_) - 1
                while i >= 0:
                    it = self.q_field_list_[i]
                    key = it[it.find(".") + 1 :].lower()
                    for f in self.q_field_mtd_list_:
                        if f.name() == key:
                            fmtd = f
                            if fmtd.type() == "pixmap":
                                self.q_img_fields_.append(i)
                            elif fmtd.type() == "double":
                                self.q_double_field_list_.append(it)
                            break
                    i -= 1
            else:
                self.q_field_list_.clear()
                self.q_double_field_list_.clear()
                self.q_img_fields_.clear()
                self.q_field_mtd_list_ = []
                self.q_group_dict_ = {}

    def rptXmlData(self) -> Any:
        """Return report Xml Data."""
        return self.rd_

    def rptXmlTemplate(self) -> Optional[str]:
        """Return report Xml Template."""
        return self.rt_

    def relDpi(self) -> float:
        """Return dpi size."""
        return self.rel_dpi_

    def setReportData(
        self, q: Optional[Union[FLDomNodeInterface, PNSqlQuery]] = None
    ) -> Optional[bool]:
        """Set data source to report."""

        if isinstance(q, FLDomNodeInterface):
            return self.setFLReportData(q)
        if q is None:
            return None

        self.rd_ = QtXml.QDomDocument("KugarData")

        self.private_.rows_ = (
            self.rd_.createDocumentFragment()
        )  # FIXME: Don't set the private from the public.
        self.private_.setQuery(q)
        q.setForwardOnly(True)
        if q.exec_() and q.next():
            g = self.private_.q_group_dict_
            if not g:
                while True:
                    self.private_.addRowToReportData(0)
                    if not q.next():
                        break
            else:
                vA: List[None] = []
                for i in range(10):
                    vA.append(None)

                ok = True
                while ok:
                    self.private_.groupBy(len(g), vA)
                    if not q.next():
                        ok = False

        data = self.rd_.createElement("KugarData")
        data.appendChild(self.private_.rows_)
        self.rd_.appendChild(data)
        self.private_.rows_.clear()

        self.initData()
        return True

    def setFLReportData(self, n: Any) -> bool:
        """Set data to report."""
        self.private_.setQuery(None)
        tmp_doc = QtXml.QDomDocument("KugarData")
        tmp_doc.appendChild(n)
        self.rd_ = tmp_doc
        return True
        # return super(FLReportEngine, self).setReportData(n)

    def setFLReportTemplate(self, t: Any) -> bool:
        """Set template to report."""
        # buscamos el .kut o el .rlab

        self.private_.template_ = t

        if not self.private_.qry_:
            from pineboolib import application

            if application.PROJECT.conn_manager is None:
                raise Exception("Project is not connected yet")
            mgr = application.PROJECT.conn_manager.managerModules()

        else:
            mgr = self.private_.qry_.db().connManager().managerModules()

        self.rt_ = mgr.contentCached("%s.kut" % t)

        if not self.rt_:
            LOGGER.error("FLReportEngine::No se ha podido cargar %s.kut", t)
            return False

        return True

    def rptQueryData(self) -> Optional[PNSqlQuery]:
        """Return report query data."""
        return self.private_.qry_

    def rptNameTemplate(self) -> str:
        """Return report template name."""
        return self.private_.template_

    @decorators.beta_implementation
    def setReportTemplate(self, t: Any):
        """Set template to report."""

        if isinstance(t, FLDomNodeInterface):
            return self.setFLReportData(t)

        return self.setFLReportData(t)

    def reportData(self) -> Any:
        """Return report data."""
        return self.rd_ if self.rd_ else QtXml.QDomDocument()

    def reportTemplate(self) -> Any:
        """Return report template."""
        return self.rt_ if self.rt_ else QtXml.QDomDocument()

    @decorators.not_implemented_warn
    def csvData(self) -> str:
        """Return csv data."""
        # FIXME: Should return the report converted to CSV
        return ""

    @decorators.not_implemented_warn
    def exportToOds(self, pages: Any):
        """Return report exported to odf."""
        if not pages or not pages.pageCollection():
            return
        # FIXME: exportToOds not defined in superclass
        # super(FLReportEngine, self).exportToOds(pages.pageCollection())

    def renderReport(
        self, init_row: int = 0, init_col: int = 0, flags: List[int] = [], pages: Any = None
    ) -> "QtCore.QObject":
        """Render report."""
        if self.rd_ and self.rt_ and self.rt_.find("KugarTemplate") > -1:
            data = self.rd_.toString(1)
            self.report_ = self.parser_.parse(
                self.private_.template_, self.rt_, data, self.report_, flags
            )

        return QtCore.QObject()  # return self.pages!

        # # print(self.rd_.toString(1))
        # """
        # fr = MReportEngine.RenderReportFlags.FillRecords.value
        #
        # pgs = FLReportPages()
        # if pages:
        #     pgs.setPageCollection(pages)
        #
        # pgc = super(FLReportEngine, self).renderReport(
        #     initRow,
        #     initCol,
        #     pgs,
        #     fr if fRec else 0
        # )
        #
        # pgs.setPageCollection(pgc)
        # if not fRec or not self.private_.qry_ or not self.private_.q_field_mtd_list_ or not self.private_.q_double_field_list_:
        #     return pgs
        #
        # nl = QtXml.QDomNodeList(self.rd_.elementsByTagName("Row"))
        # for i in range(nl.count()):
        #     itm = nl.item(i)
        #     if itm.isNull():
        #         continue
        #     nm = itm.attributes()
        #
        #     for it in self.private_.q_double_field_list_:
        #         ita = nm.namedItem(it)
        #         if ita.isNull():
        #             continue
        #         sVal = ita.nodeValue()
        #         if not sVal or sVal == "" or sVal.upper() == "NAN":
        #             continue
        #         dVal = float(sVal)
        #         if not dVal:
        #             dVal = 0
        #         decimals = self.private_.q_field_mtd_list_.find(
        #             it.section('.', 1, 1).lower()).partDecimal()
        #         ita.setNodeValue(FLUtil.formatoMiles(round(dVal, decimals)))
        # return pgs
        # """

    def initData(self) -> None:
        """Inialize data."""
        if not self.rd_:
            raise Exception("RD is missing. Initialize properly before calling initData")
        n = self.rd_.firstChild()
        while not n.isNull():
            if n.nodeName() == "KugarData":
                self.records_ = n.childNodes()
                attr = n.attributes()
                tempattr = attr.namedItem("Template")
                tempname = tempattr.nodeValue() or None
                if tempname is not None:
                    # FIXME: We need to add a signal:
                    # self.preferedTemplate.emit(tempname)
                    break
            n = n.nextSibling()

    def number_pages(self) -> int:
        """Return page numbers."""
        return self.parser_.number_pages() if self.parser_ else 0
