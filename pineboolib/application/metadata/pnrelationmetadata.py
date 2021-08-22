# -*- coding: utf-8 -*-
"""PNRelationMetaData manages relations between tables."""

from typing import Union


class PNRelationMetaData:
    """PNRelationMetaData Class."""

    """
    Constantes de tipos de cardinalidades de una relacion
    """

    RELATION_1M = "1M"
    RELATION_M1 = "M1"

    count_ = 0

    private: "PNRelationMetaDataPrivate"

    def __init__(
        self,
        other_or_foreign_table: Union["PNRelationMetaData", str],
        foreign_field: str = "",
        cardinality: str = "",
        delete_cascade: bool = False,
        update_cascade: bool = False,
        check_integrity: bool = True,
    ) -> None:
        """
        Initialize the relation.

        @param other_or_relation.  Related foreign table or other PNRelationMetaData.
        @param foreign_field Related foreign field.
        @param cardinality Cardinality of the relation.
        @param delete_cascade Deleted in cascade, only taken into account in M1 cardinalities. Defaul False
        @param update_cascade Cascade updates, only taken into account in M1 cardinalities. Default False
        @param check_integrity Integrity checks on the relation. Default True
        """
        if isinstance(other_or_foreign_table, str):
            foreign_table: str = other_or_foreign_table
            self.inicializeNewFLRelationMetaData(
                foreign_table,
                foreign_field,
                cardinality,
                delete_cascade,
                update_cascade,
                check_integrity,
            )
        else:
            self.inicializeFromFLRelationMetaData(other_or_foreign_table)

        ++self.count_

    def inicializeNewFLRelationMetaData(
        self,
        foreign_table: str,
        foreign_field: str,
        relation_cardinality: str,
        delete_cascade: bool,
        update_cascade: bool,
        check_integrity: bool,
    ) -> None:
        """
        Fill in the relation data.

        @param foreign_table Related foreign table.
        @param foreign_field Related foreign field.
        @param relation_cardinality Cardinality of the relation.
        @param delete_cascade Deleted in cascade, only taken into account in M1 cardinalities.
        @param update_cascade Cascade updates, only taken into account in M1 cardinalities.
        @param check_integrity Integrity checks on the relation.
        """

        self.private = PNRelationMetaDataPrivate(
            foreign_table,
            foreign_field,
            relation_cardinality,
            delete_cascade,
            update_cascade,
            check_integrity,
        )

    def inicializeFromFLRelationMetaData(self, other: "PNRelationMetaData"):
        """
        Fill in the data from another relation.

        @param other. original PNRelationMetaData.
        """

        self.private = PNRelationMetaDataPrivate()
        self.copy(other)

    def setField(self, field_name: str) -> None:
        """
        Set the name of the related field.

        @param fN Related field name.
        """

        self.private.field_ = field_name.lower()

    def field(self) -> str:
        """
        Get in the name of the related field.

        @return Returns the name of the related field
        """

        return self.private.field_

    def foreignTable(self) -> str:
        """
        Get the name of the foreign table.

        @return Returns the name of the database table with which it is related
        """

        return self.private._foreign_table

    def foreignField(self) -> str:
        """
        Get the name of the foreign field.

        @return Returns the name of the foreign table field with which it is related
        """

        return self.private._foreign_field

    def cardinality(self) -> str:
        """
        Get the cardinality of the relationship.

        @return Returns the cardinality of the relationship, looking from the table where define this object towards the outside
        """

        return self.private._cardinality

    def deleteCascade(self) -> bool:
        """
        Get if the relationship implies cascaded deletions, it is only taken into account in M1 cardinalities.

        @return Returns TRUE if the relationship implies cascaded deletions, FALSE otherwise
        """

        return self.private._delete_cascade and self.private._cardinality == self.RELATION_M1

    def updateCascade(self) -> bool:
        """
        Get if the relationship involves cascade modifications, it is only taken into account in M1 cardinalities.

        @return Returns TRUE if the relationship implies cascading modifications, FALSE otherwise
        """

        return self.private._update_cascade and self.private._cardinality == self.RELATION_M1

    def checkIn(self) -> bool:
        """
        Get if the integrity rules on the relationship should be applied.
        """

        return self.private._check_integrity

    def copy(self, other: "PNRelationMetaData") -> None:
        """Copy a PNRelationMetaData to another."""

        if other is not self and isinstance(other, PNRelationMetaData):
            self.private.field_ = other.private.field_
            self.private._foreign_table = other.private._foreign_table
            self.private._foreign_field = other.private._foreign_field
            self.private._cardinality = other.private._cardinality
            self.private._delete_cascade = other.private._delete_cascade
            self.private._update_cascade = other.private._update_cascade
            self.private._check_integrity = other.private._check_integrity


class PNRelationMetaDataPrivate:
    """PNRelationMetaDataPrivate Class."""

    """
    Nombre del campo a relacionar
    """

    field_: str

    """
    Nombre de la tabla foránea a relacionar
    """
    _foreign_table: str

    """
    Nombre del campo foráneo relacionado
    """
    _foreign_field: str

    """
    Cardinalidad de la relación
    """
    _cardinality: str

    """
    Indica si los borrados serán en cascada, en relaciones M1
    """
    _delete_cascade: bool

    """
    Indica si las modificaciones serán en cascada, en relaciones M1
    """
    _update_cascade: bool

    """
    Indica si se deben aplicar la reglas de integridad en esta relación
    """
    _check_integrity: bool

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the class."""

        self.field_ = ""

        if len(args) == 0:
            self.inicializeFLRelationMetaDataPrivate()
        else:
            self.inicializeNewFLRelationMetaDataPrivate(*args)

    def inicializeNewFLRelationMetaDataPrivate(
        self,
        foreign_table: str,
        foreign_field: str,
        relation_cardinality: str,
        delete_cascade: bool,
        update_cascade: bool,
        check_integrity: bool,
    ) -> None:
        """Fill initial values ​​with given values."""

        self._foreign_table = foreign_table.lower()
        self._foreign_field = foreign_field.lower()
        self._cardinality = relation_cardinality
        self._delete_cascade = delete_cascade
        self._update_cascade = update_cascade
        self._check_integrity = check_integrity

    def inicializeFLRelationMetaDataPrivate(self) -> None:
        """Initialize the empty class."""

        pass
