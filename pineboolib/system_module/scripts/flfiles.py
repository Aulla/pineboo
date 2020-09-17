"""Flfiles module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa


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

        # deshabilitado
        botonEditar.setEnabled(False)
        pbXMLEditor.setEnabled(False)


form = None
