# -*- coding: utf-8 -*-
# Translated with pineboolib v0.71.18
"""FLareas_model module."""

from sqlalchemy.ext import declarative
import sqlalchemy


class Flareas(declarative.declarative_base()):  # type: ignore [misc] # noqa: F821
    """Flareas class."""

    __tablename__ = "flareas"

    # --- Metadata --->
    legacy_metadata = {
        "name": "flareas",
        "alias": "Áreas",
        "fields": [
            {
                "name": "bloqueo",
                "alias": "Bloqueo",
                "type": "unlock",
                "null": False,
                "default": True,
            },
            {
                "name": "idarea",
                "alias": "Área",
                "pk": True,
                "type": "string",
                "length": 15,
                "relations": [{"card": "1M", "table": "flmodules", "field": "idarea"}],
                "null": False,
            },
            {
                "name": "descripcion",
                "alias": "Descripción",
                "type": "string",
                "length": 100,
                "null": False,
            },
        ],
    }

    # <--- Metadata ---

    # --- Fields --->

    bloqueo = sqlalchemy.Column("bloqueo", sqlalchemy.Boolean)
    idarea = sqlalchemy.Column("idarea", sqlalchemy.String(15), primary_key=True)
    descripcion = sqlalchemy.Column("descripcion", sqlalchemy.String(100))

    def before_flush(self, session) -> bool:
        """Before flush."""
        # ===============================================================================
        #         print("before_flush")
        #
        #         if self in session.new:
        #             print("Estoy insertando")
        #         elif self in session.dirty:
        #             print("Estoy editando")
        #         elif self in session.deleted:
        #             print("Estoy borrando")
        # ===============================================================================

        return True

    def after_flush(self, session) -> bool:
        """After flush."""
        # ===============================================================================
        #         print("after_flush")
        #
        #         if self in session.new:
        #             print("Estoy insertando")
        #         elif self in session.dirty:
        #             print("Estoy editando")
        #         elif self in session.deleted:
        #             print("Estoy borrando")
        # ===============================================================================

        return True


# <--- Fields ---
