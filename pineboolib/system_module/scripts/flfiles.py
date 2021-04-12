"""Flfiles module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def init(self) -> None:
        """Init function."""
        fdb_contenido = self.child("contenido")
        fdb_nombre = self.child("nombre")
        fdb_sha = self.child("sha")

        if fdb_contenido is None:
            raise Exception("contenido control not found!.")

        fdb_contenido.setText(self.cursor().valueBuffer("contenido"))
        fdb_nombre.setValue(self.cursor().valueBuffer("nombre"))
        fdb_sha.setValue(self.cursor().valueBuffer("sha"))

        edit_button = self.child("botonEditar")
        edit_pb_xml = self.child("pbXMLEditor")

        if edit_button:
            edit_button.setEnabled(False)

        if edit_pb_xml:
            edit_pb_xml.setEnabled(False)
