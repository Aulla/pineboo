"""Flreloadlast module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
import os


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        self = self

    def init(self) -> None:
        """Init function."""
        pass

    def main(self) -> None:
        """Entry function."""
        util = qsa.FLUtil()
        setting = "scripts/sys/modLastModule_%s" % qsa.sys.nameBD()
        fichMod = util.readSettingEntry(setting)
        if not fichMod:
            fichMod = qsa.FileDialog.getOpenFileName(
                util.translate(u"scripts", u"Módulo a cargar (*.mod)"),
                util.translate(u"scripts", u"Módulo a cargar"),
            )
            if not fichMod:
                return
            util.writeSettingEntry(setting, fichMod)

        qsa.sys.processEvents()
        self.cargarModulo(fichMod)
        qsa.sys.reinit()

    def cargarModulo(self, nombre_fichero: str) -> bool:
        """Load modules."""
        util = qsa.FLUtil()
        fichero = qsa.File(nombre_fichero, "iso-8859-15")
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
            if nodeModule is None:
                qsa.MessageBox.critical(
                    util.translate(u"scripts", u"Error en la carga del fichero xml .mod"),
                    qsa.MessageBox.Ok,
                    qsa.MessageBox.NoButton,
                )
            modulo = nodeModule.namedItem(u"name").toElement().text()
            descripcion = nodeModule.namedItem(u"alias").toElement().text()
            area = nodeModule.namedItem(u"area").toElement().text()
            desArea = nodeModule.namedItem(u"areaname").toElement().text()
            version = nodeModule.namedItem(u"version").toElement().text()
            nombreIcono = nodeModule.namedItem(u"icon").toElement().text()
            # if nodeModule.namedItem(u"flversion"):
            #    versionMinimaFL = nodeModule.namedItem(u"flversion").toElement().text()
            if nodeModule.namedItem(u"dependencies") is not None:
                nodeDepend = xmlModule.elementsByTagName(u"dependency")
                i = 0
                while i < len(nodeDepend):
                    dependencias[i] = nodeDepend.item(i).toElement().text()
                    i += 1
        else:
            if not isinstance(f, str):
                raise Exception("data must be str, not bytes!!")
            aF = f.split(u"\n")
            modulo = self.dameValor(aF[0])
            descripcion = self.dameValor(aF[1])
            area = self.dameValor(aF[2]) or ""
            desArea = self.dameValor(aF[3])
            version = self.dameValor(aF[4])
            nombreIcono = self.dameValor(aF[5])

        descripcion = self.traducirCadena(descripcion or "", fichero.path or "", modulo or "")
        desArea = self.traducirCadena(desArea or "", fichero.path or "", modulo or "")
        fichIcono = qsa.File(qsa.ustr(fichero.path, u"/", nombreIcono))
        fichIcono.open(qsa.File.ReadOnly)
        icono = fichIcono.read()

        if not util.sqlSelect(u"flareas", u"idarea", qsa.ustr(u"idarea = '", area, u"'")):
            if not util.sqlInsert(u"flareas", u"idarea,descripcion", qsa.ustr(area, u",", desArea)):
                qsa.MessageBox.warning(
                    util.translate(u"scripts", u"Error al crear el área:\n") + area,
                    qsa.MessageBox.Ok,
                    qsa.MessageBox.NoButton,
                )
                return False
        recargar = util.sqlSelect(
            u"flmodules", u"idmodulo", qsa.ustr(u"idmodulo = '", modulo, u"'")
        )
        curModulo = qsa.FLSqlCursor(u"flmodules")
        if recargar:
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
        qsa.from_project("formRecordflmodules").cargarDeDisco(qsa.ustr(fichero.path, u"/"), False)
        qsa.from_project("formRecordflmodules").accept()
        setting = "scripts/sys/modLastModule_%s" % qsa.sys.nameBD()
        nombre_fichero = "%s" % os.path.abspath(nombre_fichero)
        qsa.util.writeSettingEntry(setting, nombre_fichero)
        qsa.sys.processEvents()

        return True

    def compararVersiones(self, ver_1: str = "", ver_2: str = "") -> int:
        """Compare versions."""

        if ver_1 and ver_2:

            list_1 = ver_1.split(u".")
            list_2 = ver_2.split(u".")

            for num, item in enumerate(list_1):
                if qsa.parseInt(item) > qsa.parseInt(list_2[num]):
                    return 1
                if qsa.parseInt(item) < qsa.parseInt(list_2[num]):
                    return 2
        return 0

    def traducirCadena(self, cadena: str, path: str, modulo: str) -> str:
        """Translate string."""
        util = qsa.FLUtil()
        if cadena.find(u"QT_TRANSLATE_NOOP") == -1:
            return cadena
        cadena_list = qsa.QString(cadena)[18:-1].split(",")
        cadena = cadena_list[1][1:-1]
        nombre_fichero = None
        try:
            nombre_fichero = "%s/translations/%s.%s.ts" % (path, modulo, util.getIdioma())
        except Exception as error:
            qsa.debug(str(error))
            return cadena

        if not qsa.FileStatic.exists(nombre_fichero):
            qsa.debug("flreloadlast.traducirCadena: No se encuentra el fichero %s" % nombre_fichero)
            return cadena

        fichero = qsa.File(nombre_fichero)
        fichero.open(qsa.File.ReadOnly)
        f = fichero.read()
        xmlTranslations = qsa.FLDomDocument()
        if xmlTranslations.setContent(f):
            nodeMess = xmlTranslations.elementsByTagName(u"message")
            for item in range(len(nodeMess)):
                if nodeMess.item(item).namedItem(u"source").toElement().text() == cadena:
                    traduccion = nodeMess.item(item).namedItem(u"translation").toElement().text()
                    if traduccion:
                        cadena = traduccion
                        break

        return cadena

    def dameValor(self, linea: str) -> str:
        """Return value."""
        return linea


form = None
