# -*- coding: utf-8 -*-
# Translated with pineboolib 0.75.30.6
"""Clientes_model module."""

from pineboolib.application.database.orm import basemodel
from pineboolib.qsa import qsa

import sqlalchemy


# @class_declaration Oficial
class Oficial(basemodel.BaseModel):  # type: ignore [misc] # noqa: F821
    """ Oficial class."""

    __tablename__ = "clientes"


# @class_declaration Clientes
class Clientes(Oficial):  # type: ignore [misc] # noqa: F821
    """ Clientes class."""

    pass
