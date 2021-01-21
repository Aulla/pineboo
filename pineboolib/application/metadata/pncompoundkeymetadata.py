# -*- coding: utf-8 -*-
"""
Class to define compound keys.

This class is used to create objects that contain
a list with the fields that make up a key.
The metadata of these is saved in the list of fields,
that is FLFieldMetaData objects.
"""


from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .pnfieldmetadata import PNFieldMetaData  # pragma: no cover


class PNCompoundKeyMetaData(object):
    """PNCompoundKeyMetaData class."""

    """
    Lista de con los metadatos de los campos que componen la clave
    """

    _field_list: List["PNFieldMetaData"] = []

    def __init__(self, other: "PNCompoundKeyMetaData" = None) -> None:
        """Initialize the empty compound key or is copied from another."""

        super().__init__()
        self._field_list = []
        if other:
            self.copy(other)

    def addFieldMD(self, field_metadata: "PNFieldMetaData") -> None:
        """
        Add the description of a field to the list of fields that make up the key.

        @param f PNFieldMetaData object with the description of the field to add
        """

        self._field_list.append(field_metadata)

    """
    Obtiene si una campo pertenece a la clave compuesta.

    @param fN Nombre del campo del que se desea saber si pertenece o no a la clave compuesta
    @return TRUE si el campo forma parte de la clave compuesta, FALSE en caso contrario
    """

    def hasField(self, field_name: str) -> bool:
        """
        Get if a field belongs to the composite key.

        @param field_name Name of the field you want to know if it belongs or not to the compound key.
        @return TRUE if the field is part of the composite key, FALSE otherwise.
        """

        return field_name in [item.name() for item in self._field_list]

    def fieldList(self) -> List["PNFieldMetaData"]:
        """
        To get the list of fields that make up the key.

        @return Object with the list of field deficits of the composite key.
        """

        return self._field_list

    def copy(self, other: "PNCompoundKeyMetaData") -> None:
        """
        Copy a composite key from another.

        @param other original compound key.
        """

        if self is other:
            return
        self._field_list = other._field_list[:]
