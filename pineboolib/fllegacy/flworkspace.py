"""Flworkspace module."""
# -*- coding: utf-8 -*-
from pineboolib.fllegacy.flwidget import FLWidget
from typing import Any


class FLWorkSpace(FLWidget):
    """FLWorkSpace class."""

    def __getattr__(self, name: str) -> Any:
        """Return a parent attribute."""

        return getattr(self.parent(), name)
