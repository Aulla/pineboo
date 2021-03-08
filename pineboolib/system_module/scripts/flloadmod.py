"""Flloadmod module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
from typing import Any


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

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
                qsa.aqApp.reinit()

    def dameValor(self, linea: str) -> str:
        """Return value."""
        return linea


def valorPorClave(tabla: str, campo: str, where: str) -> Any:
    """Return a value from database."""
    return qsa.util.sqlSelect(tabla, campo, where)


def compararVersiones(ver1: str, ver2: str) -> int:
    """Compare two versions and return the hightest."""
    return qsa.from_project("formflreloadlast").compararVersiones(ver1, ver2)


def evaluarDependencias(deps: qsa.Array) -> bool:
    """Evaluate dependencies."""

    for dep in deps:
        if not qsa.sys.isLoadedModule(dep):
            res = qsa.MessageBox.warning(
                qsa.util.translate(u"scripts", u"Este módulo depende del módulo ")
                + dep
                + qsa.util.translate(
                    u"scripts",
                    u", que no está instalado.\nFacturaLUX puede fallar por esta causa.\n¿Desea continuar la carga?",
                ),
                qsa.MessageBox.Yes,
                qsa.MessageBox.No,
            )
            if res == qsa.MessageBox.No:
                return False

    return True


def traducirCadena(cadena: str, path: str, modulo: str) -> str:
    """Translate string."""
    return qsa.from_project("formflreloadlast").traducirCadena(cadena, path, modulo)


form = None
