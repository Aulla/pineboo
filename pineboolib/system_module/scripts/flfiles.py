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
        fdb_contenido = self.child(u"contenido")
        if fdb_contenido is None:
            raise Exception("contenido control not found!.")

        fdb_contenido.text = self.cursor().valueBuffer(u"contenido")
        botonEditar = self.child(u"botonEditar")
        pbXMLEditor = self.child(u"pbXMLEditor")

        if botonEditar is None:
            raise Exception("botonEditar control not found!.")

        if pbXMLEditor is None:
            raise Exception("pbXMLEditor control not found!.")

        cursor = self.cursor()
        if cursor.modeAccess() == cursor.Browse:
            botonEditar.setEnabled(False)
            pbXMLEditor.setEnabled(False)
        else:
            self.module_connect(botonEditar, u"clicked()", self, u"editarFichero")
            nombre = cursor.valueBuffer(u"nombre")
            tipo = self.tipoDeFichero(nombre)
            if tipo == u".ui" or tipo == u".ts" or tipo == u".qs":
                pbXMLEditor.setEnabled(False)
            else:
                self.module_connect(pbXMLEditor, u"clicked()", self, u"editarFicheroXML")

    def acceptedForm(self) -> None:
        """Accept form fuction."""
        self.cursor().setValueBuffer(u"contenido", self.child(u"contenido").text)

    def tipoDeFichero(self, nombre: str) -> str:
        """Return file type."""
        posPunto = nombre.rfind(u".")
        return nombre[(len(nombre) - (len(nombre) - posPunto)) :]

    def editarFichero(self) -> None:
        """Edit a file."""
        cursor = self.cursor()
        util = qsa.FLUtil()
        if cursor.checkIntegrity():
            self.child(u"nombre").setDisabled(True)
            nombre = cursor.valueBuffer(u"nombre")
            tipo = self.tipoDeFichero(nombre)
            temporal = qsa.System.getenv(u"TMP")
            if temporal == "":
                temporal = qsa.System.getenv(u"TMPDIR")
            if temporal == "":
                temporal = qsa.System.getenv(u"HOME")
            if temporal == "":
                from pineboolib.core.settings import config

                temporal = config.value("ebcomportamiento/temp_dir")

            temporal = qsa.ustr(temporal, u"/", cursor.valueBuffer(u"nombre"))
            contenido = self.child(u"contenido").text
            comando = ""
            s01_when = tipo
            s01_do_work, s01_work_done = False, False
            if s01_when == u".ui":
                s01_do_work, s01_work_done = True, True
            if s01_do_work:
                if util.getOS() == u"MACX":
                    qsa.FileStatic.write(
                        temporal, qsa.ustr(contenido, u"\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    )
                    comando = qsa.ustr(
                        qsa.sys.installPrefix(), u"/bin/designer.app/Contents/MacOS/designer"
                    )
                else:
                    qsa.FileStatic.write(temporal, contenido)
                    comando = qsa.ustr(qsa.sys.installPrefix(), u"/bin/designer")

                self.setDisabled(True)
                qsa.ProcessStatic.execute(qsa.Array([comando, temporal]))
                self.child(u"contenido").text = qsa.FileStatic.read(temporal)
                self.setDisabled(False)
                s01_do_work = False  # BREAK

            if s01_when == u".ts":
                s01_do_work, s01_work_done = True, True
            if s01_do_work:
                if util.getOS() == u"MACX":
                    qsa.FileStatic.write(
                        temporal, qsa.ustr(contenido, u"\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    )
                    comando = qsa.ustr(
                        qsa.sys.installPrefix(), u"/bin/linguist.app/Contents/MacOS/linguist"
                    )
                else:
                    qsa.FileStatic.write(temporal, contenido)
                    comando = qsa.ustr(qsa.sys.installPrefix(), u"/bin/linguist")

                self.setDisabled(True)
                qsa.ProcessStatic.execute(qsa.Array([comando, temporal]))
                self.child(u"contenido").text = qsa.FileStatic.read(temporal)
                self.setDisabled(False)
                s01_do_work = False  # BREAK

            if s01_when == u".kut":
                s01_do_work, s01_work_done = True, True
            if s01_do_work:
                if util.getOS() == u"MACX":
                    qsa.FileStatic.write(
                        temporal, qsa.ustr(contenido, u"\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    )
                    comando = qsa.ustr(
                        qsa.sys.installPrefix(), u"/bin/kudesigner.app/Contents/MacOS/kudesigner"
                    )
                else:
                    qsa.FileStatic.write(temporal, contenido)
                    comando = qsa.ustr(qsa.sys.installPrefix(), u"/bin/kudesigner")

                self.setDisabled(True)
                qsa.ProcessStatic.execute(qsa.Array([comando, temporal]))
                self.child(u"contenido").text = qsa.FileStatic.read(temporal)
                self.setDisabled(False)
                s01_do_work = False  # BREAK

            if s01_when == u".qs":
                s01_do_work, s01_work_done = True, True
            if s01_do_work:
                self.setDisabled(True)
                editor_ = qsa.FLScriptEditor(nombre)
                editor_.exec_()
                self.child(u"contenido").text = editor_.code()
                self.setDisabled(False)
                s01_do_work = False  # BREAK

            if not s01_work_done:
                s01_do_work, s01_work_done = True, True
            if s01_do_work:
                self.setDisabled(True)
                dialog = qsa.Dialog()
                dialog.setWidth(600)
                dialog.cancelButtonText = u""
                editor = qsa.TextEdit()
                if editor is None:
                    raise Exception("editor is empty!")
                editor.textFormat = editor.PlainText
                editor.text = contenido
                dialog.add(editor)
                dialog.exec_()
                self.child(u"contenido").text = editor.text
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
            temporal = qsa.ustr(temporal, u"/", cursor.valueBuffer(u"nombre"))
            comando = ""
            contenido = self.child(u"contenido").text
            if util.getOS() == u"MACX":
                qsa.FileStatic.write(temporal, qsa.ustr(contenido, u"\n\n\n\n\n\n\n\n\n\n\n\n\n\n"))
                comando = qsa.ustr(qsa.sys.installPrefix(), u"/bin/teddy.app/Contents/MacOS/teddy")
            else:
                qsa.FileStatic.write(temporal, contenido)
                comando = qsa.ustr(qsa.sys.installPrefix(), u"/bin/teddy")

            self.setDisabled(True)
            qsa.ProcessStatic.execute([comando, temporal])
            self.child(u"contenido").text = qsa.FileStatic.read(temporal)
            self.setDisabled(False)

    def calculateField(self, fN: str) -> Any:
        """Return a value."""
        if fN == u"sha":
            util = qsa.FLUtil()
            return util.sha1(self.cursor().valueBuffer(u"contenido"))


form = None
