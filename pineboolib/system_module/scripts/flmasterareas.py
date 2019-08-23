"""Flmasterareas module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa

sys = qsa.SysType()


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        pass

    def init(self) -> None:
        """Init function."""
        self.module_connect(self.cursor(), u"cursorUpdated()", self, u"actualizarAreas")

    def actualizarAreas(self) -> None:
        """Update avaliable areas."""
        qsa.sys.updateAreas()


form = None
