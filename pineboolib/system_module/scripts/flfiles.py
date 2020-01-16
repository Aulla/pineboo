"""Flfiles module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa
from typing import Any


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        pass

    def init(self) -> None:
        """Init function."""
        fdb_contenido = self.child("contenido")
        if fdb_contenido is None:
            raise Exception("contenido control not found!.")

        fdb_contenido.setText(self.cursor().valueBuffer("contenido"))
        botonEditar = self.child("botonEditar")
        pbXMLEditor = self.child("pbXMLEditor")

        if botonEditar is None:
            raise Exception("botonEditar control not found!.")

        if pbXMLEditor is None:
            raise Exception("pbXMLEditor control not found!.")

        cursor = self.cursor()
        if cursor.modeAccess() == cursor.Browse:
            botonEditar.setEnabled(False)
            pbXMLEditor.setEnabled(False)
        else:
            self.module_connect(botonEditar, "clicked()", self, "editarFichero")
            nombre = cursor.valueBuffer("nombre")
            tipo = self.tipoDeFichero(nombre)
            if tipo in (".ui", ".ts", ".qs", ".py"):
                pbXMLEditor.setEnabled(False)
            else:
                self.module_connect(pbXMLEditor, "clicked()", self, "editarFicheroXML")

    def acceptedForm(self) -> None:
        """Accept form fuction."""
        self.cursor().setValueBuffer("contenido", self.child("contenido").toPlainText())

    def tipoDeFichero(self, nombre: str) -> str:
        """Return file type."""
        posPunto = nombre.rfind(".")
        return nombre[(len(nombre) - (len(nombre) - posPunto)) :]

    def editarFichero(self) -> None:
        """Edit a file."""
        qsa.MessageBox.warning(
            qsa.util.translate("scripts", "Opción no disponible"),
            qsa.MessageBox.Yes,
            qsa.MessageBox.NoButton,
        )
        return
        cursor = self.cursor()
        util = qsa.FLUtil()
        if cursor.checkIntegrity():
            self.child("nombre").setDisabled(True)
            nombre = cursor.valueBuffer("nombre")
            tipo = self.tipoDeFichero(nombre)
            temporal = qsa.System.getenv("TMP")
            if temporal == "":
                temporal = qsa.System.getenv("TMPDIR")
            if temporal == "":
                temporal = qsa.System.getenv("HOME")
            if temporal == "":
                from pineboolib.core.settings import config

                temporal = config.value("ebcomportamiento/temp_dir")

            temporal = qsa.ustr(temporal, "/", cursor.valueBuffer("nombre"))
            contenido = self.child("contenido").toPlainText()
            comando = ""
            if tipo == ".ui":
                if util.getOS() == "MACX":
                    qsa.FileStatic.write(
                        temporal, qsa.ustr(contenido, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    )
                    comando = qsa.ustr(
                        qsa.sys.installPrefix(), "/bin/designer.app/Contents/MacOS/designer"
                    )
                else:
                    qsa.FileStatic.write(temporal, contenido)
                    comando = qsa.ustr(qsa.sys.installPrefix(), "/bin/designer")

                self.setDisabled(True)
                qsa.ProcessStatic.execute(qsa.Array([comando, temporal]))
                self.child(u"contenido").setText(qsa.FileStatic.read(temporal))
                self.setDisabled(False)
            elif tipo == ".ts":
                if util.getOS() == "MACX":
                    qsa.FileStatic.write(
                        temporal, qsa.ustr(contenido, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    )
                    comando = qsa.ustr(
                        qsa.sys.installPrefix(), "/bin/linguist.app/Contents/MacOS/linguist"
                    )
                else:
                    qsa.FileStatic.write(temporal, contenido)
                    comando = qsa.ustr(qsa.sys.installPrefix(), "/bin/linguist")

                self.setDisabled(True)
                qsa.ProcessStatic.execute(qsa.Array([comando, temporal]))
                self.child("contenido").setText(qsa.FileStatic.read(temporal))
                self.setDisabled(False)
            elif tipo == ".kut":
                if util.getOS() == "MACX":
                    qsa.FileStatic.write(
                        temporal, qsa.ustr(contenido, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    )
                    comando = qsa.ustr(
                        qsa.sys.installPrefix(), "/bin/kudesigner.app/Contents/MacOS/kudesigner"
                    )
                else:
                    qsa.FileStatic.write(temporal, contenido)
                    comando = qsa.ustr(qsa.sys.installPrefix(), "/bin/kudesigner")

                self.setDisabled(True)
                qsa.ProcessStatic.execute(qsa.Array([comando, temporal]))
                self.child("contenido").setText(qsa.FileStatic.read(temporal))
                self.setDisabled(False)

            elif tipo in (".qs", ".py"):
                self.setDisabled(True)
                editor_ = qsa.FLScriptEditor(nombre)
                editor_.exec_()
                self.child("contenido").setText(editor_.code())
                self.setDisabled(False)
            else:
                self.setDisabled(True)
                dialog = qsa.Dialog()
                dialog.setWidth(600)
                dialog.cancelButtonText = ""
                editor = qsa.TextEdit()
                if editor is None:
                    raise Exception("editor is empty!")
                editor.textFormat = editor.PlainText
                editor.text = contenido
                dialog.add(editor)
                dialog.exec_()
                self.child("contenido").setText(editor.text)
                self.setDisabled(False)

    def editarFicheroXML(self) -> None:
        """Edit xml file."""
        cursor = self.cursor()
        util = qsa.FLUtil()
        if cursor.checkIntegrity():
            temporal = qsa.System.getenv(u"TMP")
            if temporal == "":
                temporal = qsa.System.getenv(u"TMPDIR")
            if temporal == "":
                temporal = qsa.System.getenv(u"HOME")
            if temporal == "":
                from pineboolib.core.settings import config

                temporal = config.value("ebcomportamiento/temp_dir")
            temporal = qsa.ustr(temporal, "/", cursor.valueBuffer(u"nombre"))
            comando = ""
            contenido = self.child("contenido").toPlainText()
            if util.getOS() == "MACX":
                qsa.FileStatic.write(temporal, qsa.ustr(contenido, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n"))
                comando = qsa.ustr(qsa.sys.installPrefix(), "/bin/teddy.app/Contents/MacOS/teddy")
            else:
                qsa.FileStatic.write(temporal, contenido)
                comando = qsa.ustr(qsa.sys.installPrefix(), "/bin/teddy")

            self.setDisabled(True)
            qsa.ProcessStatic.execute([comando, temporal])
            self.child("contenido").setText(qsa.FileStatic.read(temporal))
            self.setDisabled(False)

    def calculateField(self, fN: str) -> Any:
        """Return a value."""
        if fN == "sha":
            util = qsa.FLUtil()
            return util.sha1(self.cursor().valueBuffer("contenido"))


form = None
