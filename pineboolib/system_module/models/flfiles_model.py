# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""Flfiles_model module."""

from pineboolib.application.database.orm import basemodel

import sqlalchemy

from pineboolib.qsa import qsa

from typing import Optional


class Flfiles(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """Flfiles class."""

    __tablename__ = "flfiles"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flfiles",
        "alias": "Ficheros de Texto",
        "fields": [
            {
                "name": "nombre",
                "alias": "Nombre",
                "pk": True,
                "type": "string",
                "length": 255,
                "null": False,
            },
            {
                "name": "bloqueo",
                "alias": "Bloqueo",
                "type": "unlock",
                "null": False,
                "default": True,
            },
            {
                "name": "idmodulo",
                "alias": "Módulo",
                "type": "string",
                "length": 15,
                "relations": [
                    {"card": "M1", "table": "flmodules", "field": "idmodulo", "delC": True}
                ],
                "null": False,
            },
            {
                "name": "sha",
                "alias": "SHA1",
                "type": "string",
                "length": 255,
                "calculated": True,
                "editable": False,
            },
            {"name": "contenido", "alias": "Contenido", "type": "stringlist", "visiblegrid": False},
            {"name": "binario", "alias": "Binario", "type": "bytearray", "visiblegrid": False},
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    nombre = sqlalchemy.Column("nombre", sqlalchemy.String(255), primary_key=True)
    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)
    idmodulo = sqlalchemy.Column("idmodulo", sqlalchemy.String(15))
    sha = sqlalchemy.Column("sha", sqlalchemy.String(255))
    contenido = sqlalchemy.Column("contenido", sqlalchemy.String)
    binario = sqlalchemy.Column("binario", sqlalchemy.LargeBinary)

    # <--- Fields ---

    def before_flush(self) -> Optional[bool]:
        """Before flush."""

        pass

    def after_flush(self) -> bool:
        """After flush."""

        session = self.session
        flfiles_class = qsa.from_project("flfiles_orm")
        flserial_class = qsa.from_project("flserial_orm")

        value = self.sha
        util = qsa.FLUtil()
        result_query = session.query(flfiles_class).all()
        value_tmp = ""
        for file_ in result_query:
            value_tmp = util.sha1(file_.sha if not value_tmp else (value_tmp + file_.sha))

        if value_tmp:
            value = value_tmp

        # session_dbaux = qsa.session("dbaux")
        session_dbaux = qsa.session()
        data_query = session_dbaux.query(flserial_class)

        if data_query.count():
            data_query.update({flserial_class.sha: value})
        else:

            obj_flserial = flserial_class()
            obj_flserial.sha = value
            session_dbaux.add(obj_flserial)

        return True
