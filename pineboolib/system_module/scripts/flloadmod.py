"""Flloadmod module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
import os
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
        nombreFichero = qsa.FileDialog.getOpenFileName(
            u"modfiles(*.mod)", qsa.util.translate(u"scripts", u"Elegir Fichero")
        )
        if nombreFichero:
            fichero = qsa.File(nombreFichero)
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
            modulo = None
            descripcion = None
            area = None
            desArea = None
            version = None
            nombreIcono = None
            # versionMinimaFL = None
            dependencias = qsa.Array()
            fichero.open(qsa.File.ReadOnly)
            f = fichero.read()
            xmlModule = qsa.FLDomDocument()
            if xmlModule.setContent(f):
                nodeModule = xmlModule.namedItem(u"MODULE")
                if not nodeModule:
                    qsa.MessageBox.critical(
                        qsa.util.translate(u"scripts", u"Error en la carga del fichero xml .mod"),
                        qsa.MessageBox.Ok,
                        qsa.MessageBox.NoButton,
                    )
                modulo = nodeModule.namedItem(u"name").toElement().text() or ""
                descripcion = nodeModule.namedItem(u"alias").toElement().text()
                area = nodeModule.namedItem(u"area").toElement().text() or ""
                desArea = nodeModule.namedItem(u"areaname").toElement().text()
                version = nodeModule.namedItem(u"version").toElement().text()
                nombreIcono = nodeModule.namedItem(u"icon").toElement().text()
                # if nodeModule.namedItem(u"flversion"):
                #    versionMinimaFL = nodeModule.namedItem(u"flversion").toElement().text()
                if nodeModule.namedItem(u"dependencies"):
                    nodeDepend = xmlModule.elementsByTagName(u"dependency")
                    i = 0
                    while_pass = True
                    while i < len(nodeDepend):
                        if not while_pass:
                            i += 1
                            while_pass = True
                            continue
                        while_pass = False
                        dependencias[i] = nodeDepend.item(i).toElement().text()
                        i += 1
                        while_pass = True
                        try:
                            i < len(nodeDepend)
                        except Exception:
                            break

            else:
                if not isinstance(f, str):
                    raise Exception("f must be sting not bytes!")
                aF = f.split(u"\n")
                modulo = self.dameValor(aF[0]) or ""
                descripcion = self.dameValor(aF[1])
                area = self.dameValor(aF[2]) or ""
                desArea = self.dameValor(aF[3])
                version = self.dameValor(aF[4])
                nombreIcono = self.dameValor(aF[5])

            descripcion = traducirCadena(descripcion or "", fichero.path or "", modulo)
            desArea = traducirCadena(desArea or "", fichero.path or "", modulo)
            fichIcono = qsa.File(qsa.ustr(fichero.path, u"/", nombreIcono))
            fichIcono.open(qsa.File.ReadOnly)
            icono = fichIcono.read()

            if not evaluarDependencias(dependencias):
                return
            if not valorPorClave(u"flareas", u"idarea", qsa.ustr(u"idarea = '", area, u"'")):
                crearArea = qsa.MessageBox.warning(
                    qsa.util.translate(u"scripts", u"El área con el identificador ")
                    + area
                    + qsa.util.translate(u"scripts", u" no existe. ¿Desea crearla?"),
                    qsa.MessageBox.Yes,
                    qsa.MessageBox.No,
                )
                if crearArea == qsa.MessageBox.No:
                    return
                dialogo = qsa.Dialog()
                dialogo.setWidth(400)
                dialogo.caption = qsa.ustr(
                    qsa.util.translate(u"scripts", u"Crear área "), area, u":"
                )
                dialogo.okButtonText = qsa.util.translate(u"scripts", u"Aceptar")
                dialogo.cancelButtonText = qsa.util.translate(u"scripts", u"Cancelar")
                leDesArea = qsa.LineEdit()
                leDesArea.text = desArea
                leDesArea.label = qsa.util.translate(u"scripts", u"Descripción: ")
                dialogo.add(leDesArea)
                if dialogo.exec_():
                    curArea = qsa.FLSqlCursor(u"flareas")
                    curArea.setModeAccess(curArea.Insert)
                    curArea.refreshBuffer()
                    curArea.setValueBuffer(u"idarea", area)
                    curArea.setValueBuffer(u"descripcion", leDesArea.text)
                    curArea.commitBuffer()

                else:
                    return

            recargar = None
            if valorPorClave(u"flmodules", u"idmodulo", qsa.ustr(u"idmodulo = '", modulo, u"'")):
                recargar = qsa.MessageBox.warning(
                    qsa.util.translate(u"scripts", u"El módulo ")
                    + modulo
                    + qsa.util.translate(u"scripts", u" ya existe. ¿Desea recargarlo?"),
                    qsa.MessageBox.Yes,
                    qsa.MessageBox.No,
                )
                if recargar == qsa.MessageBox.No:
                    return
            curModulo = qsa.FLSqlCursor(u"flmodules")
            if recargar == qsa.MessageBox.Yes:
                # WITH_START
                curModulo.select(qsa.ustr(u"idmodulo = '", modulo, u"'"))
                curModulo.first()
                curModulo.setModeAccess(curModulo.Edit)
                # WITH_END

            else:
                curModulo.setModeAccess(curModulo.Insert)

            # WITH_START
            curModulo.refreshBuffer()
            curModulo.setValueBuffer(u"idmodulo", modulo)
            curModulo.setValueBuffer(u"descripcion", descripcion)
            curModulo.setValueBuffer(u"idarea", area)
            curModulo.setValueBuffer(u"version", version)
            curModulo.setValueBuffer(u"icono", icono)
            curModulo.commitBuffer()
            # WITH_END
            # curSeleccion = qsa.FLSqlCursor(u"flmodules")
            curModulo.setMainFilter(qsa.ustr(u"idmodulo = '", modulo, u"'"))
            curModulo.editRecord(False)
            qsa.from_project("formRecordflmodules").cargarDeDisco(
                qsa.ustr(fichero.path, u"/"), False
            )
            qsa.from_project("formRecordflmodules").accept()
            setting = "scripts/sys/modLastModule_%s" % qsa.sys.nameBD()
            nombreFichero = "%s" % os.path.abspath(nombreFichero)
            qsa.util.writeSettingEntry(setting, nombreFichero)
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
    a1 = None
    a2 = None
    if v1 and v2:
        a1 = v1.split(u".")
        a2 = v2.split(u".")
        i = 0
        while_pass = True
        while i < len(a1):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            if qsa.parseInt(a1[i]) > qsa.parseInt(a2[i]):
                return 1
            if qsa.parseInt(a1[i]) < qsa.parseInt(a2[i]):
                return 2
            i += 1
            while_pass = True
            try:
                i < len(a1)
            except Exception:
                break

    return 0


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
    if cadena.find(u"QT_TRANSLATE_NOOP") == -1:
        return cadena
    cadena = qsa.QString(cadena).mid(41, len(cadena) - 43)
    nombreFichero = None
    try:
        nombreFichero = qsa.ustr(
            path, u"/translations/", modulo, u".", qsa.util.getIdioma(), u".ts"
        )
    except Exception as e:
        qsa.debug(str(e))
        return cadena

    if not qsa.File.exists(nombreFichero):
        return cadena
    fichero = qsa.File(nombreFichero)
    fichero.open(qsa.File.ReadOnly)
    f = fichero.read()
    xmlTranslations = qsa.FLDomDocument()
    if xmlTranslations.setContent(f):
        nodeMess = xmlTranslations.elementsByTagName(u"message")
        i = 0
        while_pass = True
        while i < len(nodeMess):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            if nodeMess.item(i).namedItem(u"source").toElement().text() == cadena:
                traduccion = nodeMess.item(i).namedItem(u"translation").toElement().text()
                if traduccion:
                    cadena = traduccion
            i += 1
            while_pass = True
            try:
                i < len(nodeMess)
            except Exception:
                break

    return cadena


form = None
