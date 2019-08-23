"""Floadmodpkg module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize."""
        pass

    def main(self) -> None:
        """Entry function."""
        qsa.sys.loadModules()


form = None
