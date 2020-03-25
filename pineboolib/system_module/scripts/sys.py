"""Sys module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
import traceback
from pineboolib import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor

logger = logging.get_logger(__name__)


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        # self.form = self
        self.iface = self

    def init(self) -> None:
        """Init function."""
        settings = qsa.AQSettings()
        app_ = qsa.aqApp
        if not app_:
            return

        if qsa.SysType().isLoadedModule("flfactppal"):
            codEjercicio = None
            try:
                codEjercicio = qsa.from_project("flfactppal").iface.pub_ejercicioActual()
            except Exception as e:
                logger.error(
                    "Module flfactppal was loaded but not able to execute <flfactppal.iface.pub_ejercicioActual()>"
                )
                logger.error(
                    "... this usually means that flfactppal has failed translation to python"
                )
                logger.exception(e)

            if codEjercicio:
                util = qsa.FLUtil()
                nombreEjercicio = util.sqlSelect(
                    u"ejercicios", u"nombre", qsa.ustr(u"codejercicio='", codEjercicio, u"'")
                )
                if qsa.AQUtil.sqlSelect(u"flsettings", u"valor", u"flkey='PosInfo'") == "True":
                    texto = ""
                    if nombreEjercicio:
                        texto = qsa.ustr(u"[ ", nombreEjercicio, u" ]")
                    texto = qsa.ustr(
                        texto,
                        u" [ ",
                        app_.db().driverNameToDriverAlias(app_.db().driverName()),
                        u" ] * [ ",
                        qsa.SysType().nameBD(),
                        u" ] * [ ",
                        qsa.SysType().nameUser(),
                        u" ] ",
                    )
                    app_.setCaptionMainWidget(texto)

                else:
                    if nombreEjercicio:
                        app_.setCaptionMainWidget(nombreEjercicio)

                if not settings.readBoolEntry(u"application/oldApi", False):
                    valor = util.readSettingEntry(u"ebcomportamiento/ebCallFunction")
                    if valor:
                        funcion = qsa.Function(valor)
                        try:
                            funcion()
                        except Exception:
                            qsa.debug(traceback.format_exc())

        if settings.readBoolEntry("ebcomportamiento/git_updates_enabled", False):
            qsa.sys.AQTimer.singleShot(2000, qsa.SysType.search_git_updates)

    def afterCommit_flfiles(self, cur_files_: "isqlcursor.ISqlCursor") -> bool:
        """After commit flfiles."""

        if cur_files_.modeAccess() != cur_files_.Browse:
            _qry = qsa.FLSqlQuery()
            _qry.setTablesList(u"flserial")
            _qry.setSelect(u"sha")
            _qry.setFrom(u"flfiles")
            _qry.setForwardOnly(True)
            _serial_value = cur_files_.valueBuffer(u"sha")
            if _qry.exec_():
                if _qry.first():
                    util = qsa.FLUtil()
                    _v = util.sha1(_qry.value(0))
                    while _qry.next():
                        if _qry.value(0) is not None:
                            _v = util.sha1(_v + _qry.value(0))

                    _serial_value = _v

            _cur_serial = qsa.FLSqlCursor(u"flserial")
            _cur_serial.select()
            if _cur_serial.first():
                _cur_serial.setModeAccess(_cur_serial.Edit)
            else:
                _cur_serial.setModeAccess(_cur_serial.Insert)
            _cur_serial.refreshBuffer()
            _cur_serial.setValueBuffer(u"sha", _serial_value)
            _cur_serial.commitBuffer()

        return True


form = None
