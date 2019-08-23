"""Flreloadbatch module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
import os


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""

    def init(self) -> None:
        """Init function."""
        pass

    def main(self) -> None:
        """Entry function."""
        util = qsa.FLUtil()
        setting = "scripts/sys/modLastDirModules_%s" % qsa.sys.nameBD()
        dirAnt = util.readSettingEntry(setting)
        dirMods = qsa.FileDialog.getExistingDirectory(
            dirAnt, util.translate(u"scripts", u"Directorio de Módulos")
        )

        if not dirMods:
            return
        qsa.Dir().setCurrent(dirMods)

        resComando = qsa.Array()
        if util.getOS() == u"WIN32":
            resComando = self.ejecutarComando("cmd.exe /C dir /B /S *.mod")
        else:
            resComando = self.ejecutarComando("find . -name *.mod")

        if not resComando.ok:
            qsa.MessageBox.warning(
                util.translate(u"scripts", u"Error al buscar los módulos en el directorio:\n")
                + dirMods,
                qsa.MessageBox.Ok,
                qsa.MessageBox.NoButton,
                qsa.MessageBox.NoButton,
            )
            return

        opciones = resComando.salida.split(u"\n")
        opciones.pop()
        modulos = self.elegirOpcion(opciones)
        if not modulos:
            return
        i = 0
        while_pass = True
        while i < len(modulos):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            qsa.sys.processEvents()
            if not self.cargarModulo(modulos[i]):
                qsa.MessageBox.warning(
                    util.translate(u"scripts", u"Error al cargar el módulo:\n") + modulos[i],
                    qsa.MessageBox.Ok,
                    qsa.MessageBox.NoButton,
                    qsa.MessageBox.NoButton,
                )
                return
            i += 1
            while_pass = True
            try:
                i < len(modulos)
            except Exception:
                break

        util.writeSettingEntry(setting, dirMods)
        app_ = qsa.aqApp
        if app_ is None:
            return

        app_.reinit()

    def ejecutarComando(self, comando: str) -> qsa.Array:
        """Execute a command and return a value."""
        res = qsa.Array()
        qsa.ProcessStatic.execute(comando)
        if qsa.ProcessStatic.stderr != u"":
            res[u"ok"] = False
            res[u"salida"] = qsa.ProcessStatic.stderr
            if self.pub_log:
                self.pub_log.child(u"log").append(
                    qsa.ustr(
                        u"Error al ejecutar el comando: ", comando, u"\n", qsa.ProcessStatic.stderr
                    )
                )
                self.pub_log.child(u"log").append(res.salida)

        else:
            res[u"ok"] = True
            res[u"salida"] = qsa.ProcessStatic.stdout

        return res

    def cargarModulo(self, nombreFichero: str) -> bool:
        """Load a module and return True if loaded."""
        util = qsa.FLUtil()
        if util.getOS() == u"WIN32":
            nombreFichero = nombreFichero[0 : len(nombreFichero) - 1]

        if not isinstance(nombreFichero, str):
            nombreFichero = nombreFichero.data().decode("utf-8")

        fichero = qsa.File(nombreFichero, "iso-8859-15")
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
                raise Exception("f must be str, not bytes!.")
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
        qsa.from_project("formRecordflmodules").cargarDeDisco(u"%s/" % fichero.path, False)
        qsa.from_project("formRecordflmodules").accept()
        setting = "scripts/sys/modLastModule_%s" % qsa.sys.nameBD()
        nombreFichero = "%s" % os.path.abspath(nombreFichero)
        util.writeSettingEntry(setting, nombreFichero)
        qsa.sys.processEvents()
        return True

    def compararVersiones(self, v1: str, v2: str) -> int:
        """Compare two versions and return the highest."""
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

    def traducirCadena(self, cadena: str, path: str, modulo: str) -> str:
        """Translate a string."""
        util = qsa.FLUtil()
        if cadena.find(u"QT_TRANSLATE_NOOP") == -1:
            return cadena
        # cadena2 = cadena
        cadena = qsa.QString(cadena).mid(41, len(cadena) - 43)
        nombreFichero = None
        try:
            nombreFichero = qsa.ustr(
                path, u"/translations/", modulo, u".", util.getIdioma(), u".ts"
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

    def elegirOpcion(self, opciones: qsa.Array) -> qsa.Array:
        """Show a choose option dialog and return selected values."""
        util = qsa.FLUtil()
        dialog = qsa.Dialog()
        dialog.okButtonText = util.translate(u"scripts", u"Aceptar")
        dialog.cancelButtonText = util.translate(u"scripts", u"Cancelar")
        bgroup = qsa.GroupBox()
        bgroup.setTitle(util.translate(u"scripts", u"Seleccione módulos a cargar"))
        dialog.add(bgroup)
        resultado = qsa.Array()
        cB = qsa.Array()
        i = 0
        while_pass = True
        while i < len(opciones):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            cB[i] = qsa.CheckBox()
            bgroup.add(cB[i])
            cB[i].text = opciones[i]
            cB[i].checked = True
            i += 1
            while_pass = True
            try:
                i < len(opciones)
            except Exception:
                break

        indice = 0
        if dialog.exec_():
            i = 0
            while_pass = True
            while i < len(opciones):
                if not while_pass:
                    i += 1
                    while_pass = True
                    continue
                while_pass = False
                if cB[i].checked:
                    resultado[indice] = opciones[i]
                    indice += 1
                i += 1
                while_pass = True
                try:
                    i < len(opciones)
                except Exception:
                    break

        else:
            return qsa.Array()

        if len(resultado) == 0:
            return qsa.Array()
        return resultado


form = None
