"""Flposprinter module."""

# -*- coding: utf-8 -*-
from pineboolib.core import decorators
from typing import Any, List

P76MM = 76
P57_5MM = 57
P69_5MM = 69


class FLPosPrinter(object):
    """FLPosPrinter Class."""

    printerName_: str
    strBuffer: List[str]
    escBuffer: List[str]
    idxBuffer: List[str]
    PaperWidth: List[int]
    paperWidth_: int
    server_: str
    queueName_: str

    def __init__(self) -> None:
        """Inicialize."""

        self.strBuffer = []
        self.escBuffer = []
        self.idxBuffer = []

        self.PaperWidth = [P57_5MM, P69_5MM, P76MM]
        self.paperWidth_ = P76MM

    def __del__(self) -> None:
        """Destroyer."""

        self.cleanup()

    def paperWidths(self) -> List[int]:
        """Return page widths."""

        return self.PaperWidth

    def paperWidth(self) -> int:
        """Return the current page width."""

        return self.paperWidth_

    def setPaperWidth(self, pW: int) -> None:
        """Set the paper width."""

        self.paperWidth_ = pW

    def printerName(self) -> str:
        """Return the name of the printer."""

        return self.printerName_

    @decorators.not_implemented_warn
    def metric(self, m: Any):
        """Not implemented."""

        pass

    def setPrinterName(self, name: str) -> None:
        """Set the name of the printer."""

        self.printerName_ = name

    @decorators.beta_implementation
    def cleanup(self) -> None:
        """Clean buffer values."""

        if self.strBuffer:
            self.strBuffer = []

        if self.idxBuffer:
            self.idxBuffer = []

        self.idxBuffer = []

    @decorators.not_implemented_warn
    def flush(self):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def send(self, str_: str, col: int = -1, row: int = -1):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def sendStr(self, c: str, col: int, row: int):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def sendEsc(self, e: str, col: int, row: int):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def cmd(self, c: str, paint: Any, p: Any):
        """Not implemented."""
        pass

    @decorators.beta_implementation
    def paperWidthToCols(self) -> int:
        """Return the number of columns from the paper width."""

        ret = -1
        if self.paperWidth_ is P76MM:
            ret = 80
        elif self.paperWidth_ is P69_5MM:
            ret = 65
        elif self.paperWidth_ is P57_5MM:
            ret = 55
        return ret

    @decorators.not_implemented_warn
    def initFile(self):
        """Not implemented."""
        pass

    @decorators.beta_implementation
    def initStrBuffer(self) -> None:
        """Initialize the strBuffer buffer."""

        if not self.strBuffer:
            self.strBuffer = []
        else:
            self.strBuffer.clear()

    @decorators.beta_implementation
    def initEscBuffer(self) -> None:
        """Initialize the escBuffer buffer."""
        if not self.escBuffer:
            self.escBuffer = []
        else:
            self.escBuffer.clear()

    @decorators.beta_implementation
    def parsePrinterName(self) -> None:
        """Resolve values ​​from the printer name."""

        posdots = self.printerName_.find(":")
        self.server_ = self.printerName_[:posdots]
        self.queueName_ = self.printerName_[posdots:]
        print("FLPosPrinter:parsePinterName", self.server_, self.queueName_)
