"""Flloadmod module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
from typing import Any


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        self.util = qsa.FLUtil()

    def main(self) -> None:
        """Entry function."""
        continuar = qsa.MessageBox.warning(
            qsa.util.translate(
                u"scripts",
                u"Antes de cargar un módulo asegúrese de tener una copia de seguridad de todos los datos,\n"
                + "y de que no hay ningun otro usuario conectado a la base de datos mientras se realiza la carga.\n\n¿Desea continuar?",
            ),
            qsa.MessageBox.Yes,
            qsa.MessageBox.No,
        )
        if continuar == qsa.MessageBox.No:
            return
        nombre_fichero = qsa.FileDialog.getOpenFileName(
            u"modfiles(*.mod)", qsa.util.translate(u"scripts", u"Elegir Fichero")
        )
        if nombre_fichero:
            fichero = qsa.File(nombre_fichero)
            if not qsa.from_project("formRecordflmodules").aceptarLicenciaDelModulo(
                qsa.ustr(fichero.path, u"/")
            ):
                qsa.MessageBox.critical(
                    qsa.util.translate(
                        u"scripts", u"Imposible cargar el módulo.\nLicencia del módulo no aceptada."
                    ),
                    qsa.MessageBox.Ok,
                )
                return

            if qsa.from_project("formflreloadlast").cargarModulo(nombre_fichero):
                app_ = qsa.aqApp
                if app_ is None:
                    return
                app_.reinit()

    def dameValor(self, linea: str) -> str:
        """Return value."""
        return linea


def valorPorClave(tabla: str, campo: str, where: str) -> Any:
    """Return a value from database."""
    valor = None
    query = qsa.FLSqlQuery()
    query.setTablesList(tabla)
    query.setSelect(campo)
    query.setFrom(tabla)
    query.setWhere(qsa.ustr(where, u";"))
    query.exec_()
    if query.next():
        valor = query.value(0)
    return valor


def compararVersiones(v1: str, v2: str) -> int:
    """Compare two versions and return the hightest."""
    return qsa.from_project("formflreloadlast").compararVersiones(v1, v2)


def evaluarDependencias(dependencias: qsa.Array) -> bool:
    """Evaluate dependencies."""
    res = None
    if not dependencias:
        return True
    i = 0
    while_pass = True
    while i < len(dependencias):
        if not while_pass:
            i += 1
            while_pass = True
            continue
        while_pass = False
        if dependencias[i] == "":
            continue
        if not qsa.sys.isLoadedModule(dependencias[i]):
            res = qsa.MessageBox.warning(
                qsa.util.translate(u"scripts", u"Este módulo depende del módulo ")
                + dependencias[i]
                + qsa.util.translate(
                    u"scripts",
                    u", que no está instalado.\nFacturaLUX puede fallar por esta causa.\n¿Desea continuar la carga?",
                ),
                qsa.MessageBox.Yes,
                qsa.MessageBox.No,
            )
            if res == qsa.MessageBox.No:
                return False
        i += 1
        while_pass = True
        try:
            i < len(dependencias)
        except Exception:
            break

    return True


def traducirCadena(cadena: str, path: str, modulo: str) -> str:
    """Translate string."""
    return qsa.from_project("formflreloadlast").traducirCadena(cadena, path, modulo)


form = None
