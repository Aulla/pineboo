"""Fltable module."""

# -*- coding: utf-8 -*-
from pineboolib.q3widgets import qtable
from pineboolib.core import decorators
from typing import Any


class FLTable(qtable.QTable):
    """FLTable class."""

    AlwaysOff: bool

    @decorators.not_implemented_warn
    def setColumnMovingEnabled(self, value: bool) -> None:
        """Set that columns can be moved."""
        pass

    @decorators.not_implemented_warn
    def setVScrollBarMode(self, mode: Any) -> None:
        """Set the vertical scroll bar mode."""
        pass

    @decorators.not_implemented_warn
    def setHScrollBarMode(self, mode: Any) -> None:
        """Set the horizontal scroll bar mode."""
        pass
