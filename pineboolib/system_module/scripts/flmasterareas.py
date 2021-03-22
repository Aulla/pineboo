"""Flmasterareas module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa

sys = qsa.SysType()


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def init(self) -> None:
        """Init function."""
        self.module_connect(self.cursor(), "cursorUpdated()", self, "areas_update")

    def areas_update(self) -> None:
        """Update avaliable areas."""
        qsa.sys.updateAreas()
