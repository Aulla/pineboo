"""Ebcomportamiento module."""
# -*- coding: utf-8 -*-
from pineboolib import application
from pineboolib.qsa import qsa
from pineboolib.core import settings
from pineboolib.core.utils.utils_base import filedir

from PyQt5 import QtWidgets, QtCore

import os

from typing import Any, Union


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        pass

    def main(self) -> None:
        """Entry function."""

        mng = qsa.aqApp.db().managerModules()
        self.ui_ = mng.createUI(u"ebcomportamiento.ui")
        btn_accept = self.ui_.findChild(QtWidgets.QWidget, u"pbnAceptar")
        btn_accept_tmp = self.ui_.findChild(QtWidgets.QWidget, u"pbn_temporales")
        btn_cancel = self.ui_.findChild(QtWidgets.QWidget, u"pbnCancelar")
        btn_color = self.ui_.findChild(QtWidgets.QWidget, u"pbnCO")
        self.module_connect(btn_accept, u"clicked()", self, u"guardar_clicked")
        self.module_connect(btn_cancel, u"clicked()", self, u"cerrar_clicked")
        self.module_connect(btn_color, u"clicked()", self, u"seleccionarColor_clicked")
        self.module_connect(btn_accept_tmp, u"clicked()", self, u"cambiar_temporales_clicked")
        self.cargarConfiguracion()
        self.initEventFilter()
        if qsa.sys.interactiveGUI() == "Pineboo":
            self.ui_.show()

    def cargarConfiguracion(self) -> None:
        """Load configuration."""

        self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableDC").setChecked(
            self.leerValorLocal("FLTableDoubleClick")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableSC").setChecked(
            self.leerValorLocal("FLTableShortCut")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableCalc").setChecked(
            self.leerValorLocal("FLTableExport2Calc")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbDebuggerMode").setChecked(
            self.leerValorLocal("isDebuggerMode")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbSLConsola").setChecked(
            self.leerValorLocal("SLConsola")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"leCallFunction").setText(
            self.leerValorLocal("ebCallFunction")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"leMaxPixImages").setText(
            self.leerValorLocal("maxPixImages")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"leNombreVertical").setText(
            self.leerValorGlobal("verticalName")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbFLLarge").setChecked(
            self.leerValorGlobal("FLLargeMode") == "True"
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbPosInfo").setChecked(
            self.leerValorGlobal("PosInfo") == "True"
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbMobile").setChecked(
            self.leerValorLocal("mobileMode")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbDeleteCache").setChecked(
            self.leerValorLocal("deleteCache")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbParseProject").setChecked(
            self.leerValorLocal("parseProject")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbNoPythonCache").setChecked(
            self.leerValorLocal("noPythonCache")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbActionsMenuRed").setChecked(
            self.leerValorLocal("ActionsMenuRed")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbSpacerLegacy").setChecked(
            self.leerValorLocal("spacerLegacy")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cbParseModulesOnLoad").setChecked(
            self.leerValorLocal("parseModulesOnLoad")
        )
        self.ui_.findChild(QtWidgets.QWidget, u"cb_traducciones").setChecked(
            self.leerValorLocal("translations_from_qm")
        )
        self.ui_.findChild(QtWidgets.QWidget, "le_temporales").setText(
            self.leerValorLocal("temp_dir")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_kut_debug").setChecked(
            self.leerValorLocal("kugar_debug_mode")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_no_borrar_cache").setChecked(
            self.leerValorLocal("keep_general_cache")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_snapshot").setChecked(
            self.leerValorLocal("show_snaptshop_button")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_imagenes").setChecked(
            self.leerValorLocal("no_img_cached")
        )
        self.ui_.findChild(QtWidgets.QWidget, "cb_dbadmin").setChecked(
            self.leerValorLocal("dbadmin_enabled")
        )
        valor = self.leerValorLocal("autoComp")
        auto_complete = "Siempre"
        if not valor or valor == "OnDemandF4":
            auto_complete = "Bajo Demanda (F4)"
        elif valor == "NeverAuto":
            auto_complete = "Nunca"

        self.ui_.findChild(QtWidgets.QWidget, u"cbAutoComp").setCurrentText = auto_complete

        self.ui_.findChild(QtWidgets.QWidget, u"leCO").hide()
        self.colorActual_ = self.leerValorLocal("colorObligatorio")
        if not self.colorActual_:
            self.colorActual_ = "#FFE9AD"

        self.ui_.findChild(QtWidgets.QWidget, u"leCO").setStyleSheet(
            "background-color:" + self.colorActual_
        )

        if os.path.exists(filedir("../.git")):
            self.ui_.findChild(QtWidgets.QWidget, "cb_git_activar").setChecked(
                self.leerValorLocal("git_updates_enabled")
            )
            ruta = self.leerValorLocal("git_updates_repo")
            if ruta is False:
                ruta = "https://github.com/Aulla/pineboo.git"
            self.ui_.findChild(QtWidgets.QWidget, "le_git_ruta").setText(ruta)
            self.module_connect(
                self.ui_.findChild(QtWidgets.QWidget, "pb_git_test"),
                u"clicked()",
                self,
                "search_git_updates",
            )
        else:
            self.ui_.findChild(QtWidgets.QWidget, "tbwLocales").setTabEnabled(5, False)

        self.ui_.findChild(QtWidgets.QWidget, u"leCO").show()

    def search_git_updates(self) -> None:
        """Searh for pineboo updates."""
        url = self.ui_.findChild(QtWidgets.QWidget, "le_git_ruta").text
        qsa.sys.search_git_updates(url)

    def leerValorGlobal(self, valor_name: str = None) -> Any:
        """Return global value."""
        util = qsa.FLUtil()
        value = util.sqlSelect("flsettings", "valor", "flkey='%s'" % valor_name)

        if value is None or valor_name == "verticalName" and isinstance(value, bool):
            value = ""

        return value

    def grabarValorGlobal(self, valor_name: str, value: Union[str, bool]) -> None:
        """Set global value."""
        util = qsa.FLUtil()
        if not util.sqlSelect("flsettings", "flkey", "flkey='%s'" % valor_name):
            util.sqlInsert("flsettings", "flkey,valor", "%s,%s" % (valor_name, value))
        else:
            util.sqlUpdate("flsettings", u"valor", str(value), "flkey = '%s'" % valor_name)

    def leerValorLocal(self, valor_name: str) -> Any:
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
                "git_updates_repo",
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

    def grabarValorLocal(self, valor_name: str, value: Union[str, bool]) -> None:
        """Set local value."""

        if valor_name in ("isDebuggerMode", "dbadmin_enabled"):
            settings.CONFIG.set_value("application/%s" % valor_name, value)
        else:
            if valor_name == "maxPixImages" and value is None:
                value = 600
            settings.CONFIG.set_value("ebcomportamiento/%s" % valor_name, value)

    def initEventFilter(self) -> None:
        """Inicialize event filter."""

        self.ui_.eventFilterFunction = qsa.ustr(self.ui_.objectName(), u".eventFilter")
        self.ui_.allowedEvents = qsa.Array([qsa.AQS.Close])
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

        self.grabarValorGlobal(
            "verticalName", self.ui_.findChild(QtWidgets.QWidget, u"leNombreVertical").text()
        )
        self.grabarValorLocal(
            "FLTableDoubleClick", self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableDC").isChecked()
        )
        self.grabarValorLocal(
            "FLTableShortCut", self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableSC").isChecked()
        )
        self.grabarValorLocal(
            "FLTableExport2Calc",
            self.ui_.findChild(QtWidgets.QWidget, u"cbFLTableCalc").isChecked(),
        )
        self.grabarValorLocal(
            "isDebuggerMode", self.ui_.findChild(QtWidgets.QWidget, u"cbDebuggerMode").isChecked()
        )
        self.grabarValorLocal(
            "SLConsola", self.ui_.findChild(QtWidgets.QWidget, u"cbSLConsola").isChecked()
        )
        self.grabarValorLocal(
            "ebCallFunction", self.ui_.findChild(QtWidgets.QWidget, u"leCallFunction").text()
        )
        self.grabarValorLocal(
            "maxPixImages", self.ui_.findChild(QtWidgets.QWidget, u"leMaxPixImages").text()
        )
        self.grabarValorLocal("colorObligatorio", self.colorActual_)
        self.grabarValorLocal(
            "ActionsMenuRed", self.ui_.findChild(QtWidgets.QWidget, u"cbActionsMenuRed").isChecked()
        )
        self.grabarValorGlobal(
            "FLLargeMode", self.ui_.findChild(QtWidgets.QWidget, u"cbFLLarge").isChecked()
        )
        self.grabarValorGlobal(
            "PosInfo", self.ui_.findChild(QtWidgets.QWidget, u"cbPosInfo").isChecked()
        )
        self.grabarValorLocal(
            "deleteCache", self.ui_.findChild(QtWidgets.QWidget, u"cbDeleteCache").isChecked()
        )
        self.grabarValorLocal(
            "parseProject", self.ui_.findChild(QtWidgets.QWidget, u"cbParseProject").isChecked()
        )
        self.grabarValorLocal(
            "noPythonCache", self.ui_.findChild(QtWidgets.QWidget, u"cbNoPythonCache").isChecked()
        )
        self.grabarValorLocal(
            "mobileMode", self.ui_.findChild(QtWidgets.QWidget, u"cbMobile").isChecked()
        )
        self.grabarValorLocal(
            "spacerLegacy", self.ui_.findChild(QtWidgets.QWidget, u"cbSpacerLegacy").isChecked()
        )
        self.grabarValorLocal(
            "parseModulesOnLoad",
            self.ui_.findChild(QtWidgets.QWidget, u"cbParseModulesOnLoad").isChecked(),
        )
        self.grabarValorLocal(
            "translations_from_qm",
            self.ui_.findChild(QtWidgets.QWidget, u"cb_traducciones").isChecked(),
        )
        self.grabarValorLocal(
            "temp_dir", self.ui_.findChild(QtWidgets.QWidget, "le_temporales").text()
        )
        self.grabarValorLocal(
            "kugar_debug_mode", self.ui_.findChild(QtWidgets.QWidget, "cb_kut_debug").isChecked()
        )
        self.grabarValorLocal(
            "keep_general_cache",
            self.ui_.findChild(QtWidgets.QWidget, "cb_no_borrar_cache").isChecked(),
        )
        self.grabarValorLocal(
            "git_updates_enabled",
            self.ui_.findChild(QtWidgets.QWidget, "cb_git_activar").isChecked(),
        )
        self.grabarValorLocal(
            "git_updates_repo", self.ui_.findChild(QtWidgets.QWidget, "le_git_ruta").text()
        )
        self.grabarValorLocal(
            "show_snaptshop_button",
            self.ui_.findChild(QtWidgets.QWidget, "cb_snapshot").isChecked(),
        )
        self.grabarValorLocal(
            "no_img_cached", self.ui_.findChild(QtWidgets.QWidget, "cb_imagenes").isChecked()
        )
        self.grabarValorLocal(
            "dbadmin_enabled", self.ui_.findChild(QtWidgets.QWidget, "cb_dbadmin").isChecked()
        )

        valor = self.ui_.findChild(QtWidgets.QWidget, u"cbAutoComp").currentText()
        auto_complete = "AlwaysAuto"
        if valor == "Nunca":
            auto_complete = "NeverAuto"
        elif valor == "Bajo Demanda (F4)":
            auto_complete = "OnDemandF4"

        self.grabarValorLocal("autoComp", auto_complete)
        self.cerrar_clicked()

    def seleccionarColor_clicked(self) -> None:
        """Set mandatory color."""
        self.colorActual_ = qsa.AQS.ColorDialog_getColor(self.colorActual_, self.ui_).name()
        self.ui_.findChild(QtWidgets.QWidget, u"leCO").setStyleSheet(
            "background-color:" + self.colorActual_
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


form = None
