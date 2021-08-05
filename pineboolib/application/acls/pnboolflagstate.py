# -*- coding: utf-8 -*-
"""
PNBoolFlagState package.

Save cursor states.
"""
from typing import List, Optional


class PNBoolFlagState(object):
    """PNBollFlagState Class."""

    modifier_: str
    prev_value_: bool


class PNBoolFlagStateList(object):
    """PNBoolFlagStateList Class."""

    data_list_: List["PNBoolFlagState"]

    def __init__(self):
        """Initialize the list."""

        self.data_list_ = []

    def append(self, data: "PNBoolFlagState") -> None:
        """
        Add a state to the list.

        @param data. Flag state.
        """

        self.data_list_.append(data)

    def pushOnTop(self, data: "PNBoolFlagState") -> None:
        """
        Add a state to the list first.

        @param data. Flag state.
        """

        self.data_list_.insert(0, data)

    def erase(self, data: "PNBoolFlagState") -> None:
        """
        Erase a state to the list first.

        @param data. Flag state.
        """
        self.data_list_.remove(data)

    def find(self, data: str) -> Optional["PNBoolFlagState"]:
        """
        Search for a state in the list from a value.

        @param data. Value to search.
        @return Flag state.
        """

        for child in self.data_list_:
            if child.modifier_ == data:
                return child

        return None

    def current(self) -> Optional["PNBoolFlagState"]:
        """
        Return the first state of the list.

        @return Flag state.
        """

        return None if not self.data_list_ else self.data_list_[0]
