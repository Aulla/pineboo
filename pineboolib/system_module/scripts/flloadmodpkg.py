"""Floadmodpkg module."""
# -*- coding: utf-8 -*-
from pineboolib.qsa import qsa


class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    def main(self) -> None:
        """Entry function."""
        qsa.sys.loadModules()
