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
    report_template_: Optional[str]

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """Inicialize."""

        super().__init__(parent)
        self.private_ = FLReportEngine.FLReportEnginePrivate(self)
        self.rel_dpi_ = 78.0
        self.report_ = None
        self.report_template_ = ""
        self.report_data_: Optional[QtXml.QDomDocument] = None

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

        def __init__(self, report_engine: "FLReportEngine") -> None:
            """Inicialize."""
            self.qry_ = None
            self.q_field_mtd_list_ = []
            self.q_group_dict_ = {}
            self.report_engine = report_engine
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

            row = self.report_engine.rptXmlData().createElement("Row")
            row.setAttribute("level", level)

            for num, item in enumerate(self.q_field_list_):
                str_val = str(self.qry_.value(item, False))
                if self.q_img_fields_:
                    if self.q_img_fields_[-1] == num:
                        self.q_img_fields_.append(self.q_img_fields_.pop())
                        if str_val in ["", "None"]:
                            row.setAttribute(item, str_val)
                            continue

                    key = self.qry_.value(num, False)
                    row.setAttribute(item, key)

                else:
                    row.setAttribute(item, str_val)

            self.rows_.appendChild(row)

        def groupBy(self, level_max: int, va_: List[Any]) -> None:
            """Add a group by."""
            if not self.qry_ or not self.qry_.isValid():
                return

            # self.q_group_dict_
            lev = 0

            while lev < level_max and str(self.qry_.value(self.q_group_dict_[lev])) == str(
                va_[lev]
            ):
                lev += 1

            for num in range(lev, level_max):
                self.addRowToReportData(num)
                va_[num] = str(self.qry_.value(self.q_group_dict_[num]))

            self.addRowToReportData(level_max)

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

                size = len(self.q_field_list_) - 1
                while size >= 0:
                    item = self.q_field_list_[size]
                    key = item[item.find(".") + 1 :].lower()
                    for field in self.q_field_mtd_list_:
                        if field.name() == key:
                            if field.type() == "pixmap":
                                self.q_img_fields_.append(size)
                            elif field.type() == "double":
                                self.q_double_field_list_.append(item)
                            break
                    size -= 1
            else:
                self.q_field_list_.clear()
                self.q_double_field_list_.clear()
                self.q_img_fields_.clear()
                self.q_field_mtd_list_ = []
                self.q_group_dict_ = {}

    def rptXmlData(self) -> Any:
        """Return report Xml Data."""
        return self.report_data_

    def rptXmlTemplate(self) -> Optional[str]:
        """Return report Xml Template."""
        return self.report_template_

    def relDpi(self) -> float:
        """Return dpi size."""
        return self.rel_dpi_

    def setReportData(
        self, qry: Optional[Union[FLDomNodeInterface, PNSqlQuery]] = None
    ) -> Optional[bool]:
        """Set data source to report."""

        if isinstance(qry, FLDomNodeInterface):
            return self.setFLReportData(qry)
        if qry is None:
            return None

        self.report_data_ = QtXml.QDomDocument("KugarData")

        self.private_.rows_ = (
            self.report_data_.createDocumentFragment()
        )  # FIXME: Don't set the private from the public.
        self.private_.setQuery(qry)
        qry.setForwardOnly(True)
        if qry.exec_() and qry.next():
            group = self.private_.q_group_dict_
            if not group:
                while True:
                    self.private_.addRowToReportData(0)
                    if not qry.next():
                        break
            else:
                values_: List[None] = []
                for item in range(10):
                    values_.append(None)

                ok_ = True
                while ok_:
                    self.private_.groupBy(len(group), values_)
                    if not qry.next():
                        ok_ = False

        data = self.report_data_.createElement("KugarData")
        data.appendChild(self.private_.rows_)
        self.report_data_.appendChild(data)
        self.private_.rows_.clear()

        self.initData()
        return True

    def setFLReportData(self, data: Any) -> bool:
        """Set data to report."""
        self.private_.setQuery(None)
        tmp_doc = QtXml.QDomDocument("KugarData")
        tmp_doc.appendChild(data)
        self.report_data_ = tmp_doc
        return True
        # return super(FLReportEngine, self).setReportData(n)

    def setFLReportTemplate(self, template: Any) -> bool:
        """Set template to report."""
        # buscamos el .kut o el .rlab

        self.private_.template_ = template

        if not self.private_.qry_:
            from pineboolib import application

            if application.PROJECT.conn_manager is None:
                raise Exception("Project is not connected yet")
            mgr = application.PROJECT.conn_manager.managerModules()

        else:
            mgr = self.private_.qry_.db().connManager().managerModules()

        self.report_template_ = mgr.contentCached("%s.kut" % template)

        if not self.report_template_:
            LOGGER.error("FLReportEngine::No se ha podido cargar %s.kut", template)
            return False

        return True

    def rptQueryData(self) -> Optional[PNSqlQuery]:
        """Return report query data."""
        return self.private_.qry_

    def rptNameTemplate(self) -> str:
        """Return report template name."""
        return self.private_.template_

    @decorators.beta_implementation
    def setReportTemplate(self, template: Any):
        """Set template to report."""

        if isinstance(template, FLDomNodeInterface):
            return self.setFLReportData(template)

        return self.setFLReportData(template)

    def reportData(self) -> Any:
        """Return report data."""
        return self.report_data_ if self.report_data_ else QtXml.QDomDocument()

    def reportTemplate(self) -> Any:
        """Return report template."""
        return self.report_template_ if self.report_template_ else QtXml.QDomDocument()

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
        if (
            self.report_data_
            and self.report_template_
            and self.report_template_.find("KugarTemplate") > -1
        ):
            data = self.report_data_.toString(1)
            self.report_ = self.parser_.parse(
                self.private_.template_, self.report_template_, data, self.report_, flags
            )

        return QtCore.QObject()  # return self.pages!

        # # print(self.report_data_.toString(1))
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
        # nl = QtXml.QDomNodeList(self.report_data_.elementsByTagName("Row"))
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
        if not self.report_data_:
            raise Exception("RD is missing. Initialize properly before calling initData")
        child = self.report_data_.firstChild()
        while not child.isNull():
            if child.nodeName() == "KugarData":
                self.records_ = child.childNodes()
                attr = child.attributes()
                tempattr = attr.namedItem("Template")
                tempname = tempattr.nodeValue() or None
                if tempname is not None:
                    # FIXME: We need to add a signal:
                    # self.preferedTemplate.emit(tempname)
                    break
            child = child.nextSibling()

    def number_pages(self) -> int:
        """Return page numbers."""
        return self.parser_.number_pages() if self.parser_ else 0
