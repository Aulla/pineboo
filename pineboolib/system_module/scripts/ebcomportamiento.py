"""Ebcomportamiento module."""
# -*- coding: utf-8 -*-
from pineboolib import application
from pineboolib.qsa import qsa
from pineboolib.core import settings
from PyQt6 import QtWidgets, QtCore  # type: ignore[import]

import os

from typing import Any, Union


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def main(self) -> None:
        """Entry function."""

        mng = qsa.aqApp.db().managerModules()
        self.ui_: "QtWidgets.QWidget" = mng.createUI(  # type: ignore [assignment]
            u"ebcomportamiento.ui"
        )
        btn_accept = self.ui_.findChild(QtWidgets.QWidget, u"pbnAceptar")
        btn_accept_tmp = self.ui_.findChild(QtWidgets.QWidget, u"pbn_temporales")
        btn_cancel = self.ui_.findChild(QtWidgets.QWidget, u"pbnCancelar")
        btn_color = self.ui_.findChild(QtWidgets.QWidget, u"pbnCO")
        self.module_connect(btn_accept, u"clicked()", self, u"guardar_clicked")
        self.module_connect(btn_cancel, u"clicked()", self, u"cerrar_clicked")
        self.module_connect(btn_color, u"clicked()", self, u"color_chooser_clicked")
        self.module_connect(btn_accept_tmp, u"clicked()", self, u"cambiar_temporales_clicked")
        self.load_config()
        self.initEventFilter()
        if qsa.sys.interactiveGUI() == "Pineboo":
            self.ui_.show()

    def load_config(self) -> None:
        """Load configuration."""

        self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableDC").setChecked(
            self.read_local_value("FLTableDoubleClick")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableSC").setChecked(
            self.read_local_value("FLTableShortCut")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableCalc").setChecked(
            self.read_local_value("FLTableExport2Calc")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbDebuggerMode").setChecked(
            self.read_local_value("isDebuggerMode")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbSLConsola").setChecked(
            self.read_local_value("SLConsola")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"leCallFunction").setText(
            self.read_local_value("ebCallFunction")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"leMaxPixImages").setText(
            self.read_local_value("maxPixImages")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"leNombreVertical").setText(
            self.read_db_value("verticalName")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbFLLarge").setChecked(
            self.read_db_value("FLLargeMode") == "True"
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbPosInfo").setChecked(
            self.read_db_value("PosInfo") == "True"
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbMobile").setChecked(
            self.read_local_value("mobileMode")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbDeleteCache").setChecked(
            self.read_local_value("deleteCache")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbParseProject").setChecked(
            self.read_local_value("parseProject")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbNoPythonCache").setChecked(
            self.read_local_value("noPythonCache")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbActionsMenuRed").setChecked(
            self.read_local_value("ActionsMenuRed")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbSpacerLegacy").setChecked(
            self.read_local_value("spacerLegacy")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbParseModulesOnLoad").setChecked(
            self.read_local_value("parseModulesOnLoad")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cb_traducciones").setChecked(
            self.read_local_value("translations_from_qm")
        )
        self.ui_.findChild(QtWidgets.QWidget, "le_temporales").setText(
            self.read_local_value("temp_dir")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_kut_debug").setChecked(
            self.read_local_value("kugar_debug_mode")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_no_borrar_cache").setChecked(
            self.read_local_value("keep_general_cache")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_snapshot").setChecked(
            self.read_local_value("show_snaptshop_button")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_imagenes").setChecked(
            self.read_local_value("no_img_cached")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_dbadmin").setChecked(
            self.read_local_value("dbadmin_enabled")
        )
        valor = self.read_local_value("autoComp")
        auto_complete = "Siempre"
        if not valor or valor == "OnDemandF4":
            auto_complete = "Bajo Demanda (F4)"
        elif valor == "NeverAuto":
            auto_complete = "Nunca"

        self.ui_.findChild(
            QtWidgets.QWidget, u"cbAutoComp"
        ).setCurrentText = auto_complete  # type: ignore [attr-defined]

        self.ui_.findChild(QtWidgets.QWidget, u"leCO").hide()
        self.color_actual = self.read_local_value("colorObligatorio")
        if not self.color_actual:
            self.color_actual = "#FFE9AD"

        self.ui_.findChild(QtWidgets.QWidget, u"leCO").setStyleSheet(
            "background-color:" + self.color_actual
        )

        self.ui_.findChild(QtWidgets.QWidget, "tbwLocales").setTabEnabled(5, False)

        self.ui_.findChild(QtWidgets.QWidget, u"leCO").show()

    def read_db_value(self, valor_name: str = None) -> Any:
        """Return global value."""
        util = qsa.FLUtil()
        value = util.sqlSelect("flsettings", "valor", "flkey='%s'" % valor_name)

        if value is None or valor_name == "verticalName" and isinstance(value, bool):
            value = ""

        return value

    def write_db_value(self, valor_name: str, value: Union[str, bool]) -> None:
        """Set global value."""
        util = qsa.FLUtil()
        if not util.sqlSelect("flsettings", "flkey", "flkey='%s'" % valor_name):
            util.sqlInsert("flsettings", "flkey,valor", "%s,%s" % (valor_name, value))
        else:
            util.sqlUpdate("flsettings", u"valor", str(value), "flkey = '%s'" % valor_name)

    def read_local_value(self, valor_name: str) -> Any:
        """Return local value."""

        if valor_name in ("isDebuggerMode", "dbadmin_enabled"):

            valor = settings.CONFIG.value("application/%s" % valor_name, False)
        else:
            if valor_name in (
                "ebCallFunction",
                "maxPixImages",
                "kugarParser",
                "colorObligatorio",
                "temp_dir",
            ):
                valor = settings.CONFIG.value("ebcomportamiento/%s" % valor_name, "")
                if valor_name == "temp_dir" and valor == "":
                    app_ = qsa.aqApp
                    if app_ is None:
                        return ""

                    valor = app_.tmp_dir()

            else:
                valor = settings.CONFIG.value("ebcomportamiento/%s" % valor_name, False)
        return valor

    def write_local_value(self, valor_name: str, value: Union[str, bool]) -> None:
        """Set local value."""

        if valor_name in ("isDebuggerMode", "dbadmin_enabled"):
            settings.CONFIG.set_value("application/%s" % valor_name, value)
        else:
            if valor_name == "maxPixImages" and value is None:
                value = 600
            settings.CONFIG.set_value("ebcomportamiento/%s" % valor_name, value)

    def initEventFilter(self) -> None:
        """Inicialize event filter."""

        self.ui_.eventFilterFunction = qsa.ustr(  # type: ignore [attr-defined]
            self.ui_.objectName(), u".eventFilter"
        )
        self.ui_.allowedEvents = qsa.Array([qsa.AQS.Close])  # type: ignore [attr-defined]
        self.ui_.installEventFilter(self.ui_)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Event filter."""
        if type(event) == qsa.AQS.Close:
            self.cerrar_clicked()

        return True

    def cerrar_clicked(self) -> None:
        """Close the widget."""
        self.ui_.close()

    def guardar_clicked(self) -> None:
        """Save actual configuration."""

        self.write_db_value(
            "verticalName", self.ui_.findChild(QtWidgets.QWidget, u"leNombreVertical").text()
        )
        self.write_local_value(
            "FLTableDoubleClick", self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableDC").isChecked()
        )
        self.write_local_value(
            "FLTableShortCut", self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableSC").isChecked()
        )
        self.write_local_value(
            "FLTableExport2Calc",
            self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableCalc").isChecked(),
        )
        self.write_local_value(
            "isDebuggerMode", self.ui_.findChild(QtWidgets.QWidget, u"cbDebuggerMode").isChecked()
        )
        self.write_local_value(
            "SLConsola", self.ui_.findChild(QtWidgets.QWidget, u"cbSLConsola").isChecked()
        )
        self.write_local_value(
            "ebCallFunction", self.ui_.findChild(QtWidgets.QWidget, u"leCallFunction").text()
        )
        self.write_local_value(
            "maxPixImages", self.ui_.findChild(QtWidgets.QWidget, u"leMaxPixImages").text()
        )
        self.write_local_value("colorObligatorio", self.color_actual)
        self.write_local_value(
            "ActionsMenuRed", self.ui_.findChild(QtWidgets.QWidget, u"cbActionsMenuRed").isChecked()
        )
        self.write_db_value(
            "FLLargeMode", self.ui_.findChild(QtWidgets.QWidget, u"cbFLLarge").isChecked()
        )
        self.write_db_value(
            "PosInfo", self.ui_.findChild(QtWidgets.QWidget, u"cbPosInfo").isChecked()
        )
        self.write_local_value(
            "deleteCache", self.ui_.findChild(QtWidgets.QWidget, u"cbDeleteCache").isChecked()
        )
        self.write_local_value(
            "parseProject", self.ui_.findChild(QtWidgets.QWidget, u"cbParseProject").isChecked()
        )
        self.write_local_value(
            "noPythonCache", self.ui_.findChild(QtWidgets.QWidget, u"cbNoPythonCache").isChecked()
        )
        self.write_local_value(
            "mobileMode", self.ui_.findChild(QtWidgets.QWidget, u"cbMobile").isChecked()
        )
        self.write_local_value(
            "spacerLegacy", self.ui_.findChild(QtWidgets.QWidget, u"cbSpacerLegacy").isChecked()
        )
        self.write_local_value(
            "parseModulesOnLoad",
            self.ui_.findChild(QtWidgets.QWidget, u"cbParseModulesOnLoad").isChecked(),
        )
        self.write_local_value(
            "translations_from_qm",
            self.ui_.findChild(QtWidgets.QWidget, u"cb_traducciones").isChecked(),
        )
        self.write_local_value(
            "temp_dir", self.ui_.findChild(QtWidgets.QWidget, "le_temporales").text()
        )
        self.write_local_value(
            "kugar_debug_mode", self.ui_.findChild(QtWidgets.QWidget, "cb_kut_debug").isChecked()
        )
        self.write_local_value(
            "keep_general_cache",
            self.ui_.findChild(QtWidgets.QWidget, "cb_no_borrar_cache").isChecked(),
        )
        self.write_local_value(
            "show_snaptshop_button",
            self.ui_.findChild(QtWidgets.QWidget, "cb_snapshot").isChecked(),
        )
        self.write_local_value(
            "no_img_cached", self.ui_.findChild(QtWidgets.QWidget, "cb_imagenes").isChecked()
        )
        self.write_local_value(
            "dbadmin_enabled", self.ui_.findChild(QtWidgets.QWidget, "cb_dbadmin").isChecked()
        )

        valor = self.ui_.findChild(QtWidgets.QWidget, u"cbAutoComp").currentText()
        auto_complete = "AlwaysAuto"
        if valor == "Nunca":
            auto_complete = "NeverAuto"
        elif valor == "Bajo Demanda (F4)":
            auto_complete = "OnDemandF4"

        self.write_local_value("autoComp", auto_complete)
        self.cerrar_clicked()

    def color_chooser_clicked(self) -> None:
        """Set mandatory color."""
        self.color_actual = qsa.AQS.ColorDialog_getColor(self.color_actual, self.ui_).name()
        self.ui_.findChild(QtWidgets.QWidget, u"leCO").setStyleSheet(
            "background-color:" + self.color_actual
        )

    def cambiar_temporales_clicked(self) -> None:
        """Change temp folder."""
        old_dir = self.ui_.findChild(QtWidgets.QWidget, "le_temporales").text()
        old_dir = os.path.normcase(old_dir)
        new_dir = qsa.FileDialog.getExistingDirectory(old_dir)
        if new_dir and new_dir is not old_dir:
            new_dir = new_dir[:-1]
            self.ui_.findChild(QtWidgets.QWidget, "le_temporales").setText(new_dir)

            application.PROJECT.tmpdir = new_dir
