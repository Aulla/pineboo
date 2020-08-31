"""Flreloadbatch module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa


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
        else:
            res[u"ok"] = True
            res[u"salida"] = qsa.ProcessStatic.stdout

        return res

    def cargarModulo(self, nombre_fichero: str) -> bool:
        """Load a module and return True if loaded."""
        util = qsa.FLUtil()
        if util.getOS() == u"WIN32":
            nombre_fichero = nombre_fichero[0 : len(nombre_fichero) - 1]

        return qsa.from_project("formflreloadlast").cargarModulo(nombre_fichero)

    def compararVersiones(self, v1: str, v2: str) -> int:
        """Compare two versions and return the highest."""

        return qsa.from_project("formflreloadlast").compararVersiones(v1, v2)

    def traducirCadena(self, cadena: str, path: str, modulo: str) -> str:
        """Translate a string."""
        return qsa.from_project("formflreloadlast").traducirCadena(cadena, path, modulo)

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

    def dameValor(self, linea: str) -> str:
        """Return value."""
        return qsa.from_project("formflreloadlast").dameValor(linea)


form = None
