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

        for modulo in modulos:
            qsa.sys.processEvents()
            if not self.cargarModulo(modulo):
                qsa.MessageBox.warning(
                    util.translate(u"scripts", u"Error al cargar el módulo:\n") + modulo,
                    qsa.MessageBox.Ok,
                    qsa.MessageBox.NoButton,
                    qsa.MessageBox.NoButton,
                )
                return

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
        check_box_list = qsa.Array()
        for num, opcion in enumerate(opciones):
            check_box_list[num] = qsa.CheckBox()
            bgroup.add(check_box_list[num])
            check_box_list[num].text = opcion
            check_box_list[num].checked = True

        if dialog.exec_():
            for num, opcion in enumerate(opciones):
                if check_box_list[num].checked:
                    resultado[len(resultado)] = opciones[num]

        return resultado if len(resultado) else qsa.Array()


form = None
