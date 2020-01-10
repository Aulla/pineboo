# -*- coding: utf-8 -*-
"""Manage a parameters from a Query instance."""

from typing import Any


class PNParameterQuery(object):
    """Class that manages each parameter of a query."""

    name_: str
    alias_: str
    type_: int
    value_: Any

    def __init__(self, name: str, alias: str, type_: int) -> None:
        """Specify the name alias and type."""
        self.name_ = name
        self.alias_ = alias
        self.type_ = type_
        self.value_ = None

    def name(self) -> str:
        """Return parameter name."""

        return self.name_

    def alias(self) -> str:
        """Return parameter alias."""
        return self.alias_

    def type(self) -> int:
        """Return parameter type."""
        return self.type_

    def value(self) -> Any:
        """Return the value contained in the parameter."""

        return self.value_

    def setValue(self, value: Any) -> None:
        """Set a value for the parameter."""
        self.value_ = value
