"""Flloadmod module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def main(self) -> None:
        """Entry function."""
        continuar = qsa.MessageBox.warning(
            qsa.util.translate(
                "scripts",
                "Antes de cargar un módulo asegúrese de tener una copia de seguridad de todos los datos,\n"
                + "y de que no hay ningun otro usuario conectado a la base de datos mientras se realiza la carga.\n\n¿Desea continuar?",
            ),
            qsa.MessageBox.Yes,
            qsa.MessageBox.No,
        )
        if continuar == qsa.MessageBox.No:
            return
        nombre_fichero = qsa.FileDialog.getOpenFileName(
            "modfiles(*.mod)", qsa.util.translate("scripts", "Elegir Fichero")
        )
        if nombre_fichero:
            fichero = qsa.File(nombre_fichero)
            if not qsa.from_project("formRecordflmodules").aceptarLicenciaDelModulo(
                qsa.ustr(fichero.path, "/")
            ):
                qsa.MessageBox.critical(
                    qsa.util.translate(
                        "scripts", "Imposible cargar el módulo.\nLicencia del módulo no aceptada."
                    ),
                    qsa.MessageBox.Ok,
                )
                return

            if qsa.from_project("formflreloadlast").load_module(nombre_fichero):
                qsa.aqApp.reinit()

    def get_value(self, linea: str) -> str:
        """Return value."""
        return linea


def version_compare(ver1: str, ver2: str) -> int:
    """Compare two versions and return the hightest."""
    return qsa.from_project("formflreloadlast").version_compare(ver1, ver2)


def deps_evaluate(deps: qsa.Array) -> bool:
    """Evaluate dependencies."""

    for dep in deps:
        if not qsa.sys.isLoadedModule(dep):
            res = qsa.MessageBox.warning(
                qsa.util.translate("scripts", "Este módulo depende del módulo ")
                + dep
                + qsa.util.translate(
                    "scripts",
                    ", que no está instalado.\nFacturaLUX puede fallar por esta causa.\n¿Desea continuar la carga?",
                ),
                qsa.MessageBox.Yes,
                qsa.MessageBox.No,
            )
            if res == qsa.MessageBox.No:
                return False

    return True
