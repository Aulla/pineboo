"""Flposprinter module."""

# -*- coding: utf-8 -*-
from pineboolib.core import decorators
from typing import Any, List

P76MM = 76
P57_5MM = 57
P69_5MM = 69


class FLPosPrinter(object):
    """FLPosPrinter Class."""

    _printer_name: str
    _str_buffer: List[str]
    _esc_buffer: List[str]
    _idx_buffer: List[str]
    _papers_width: List[int]
    _paper_width: int
    server_: str
    _queue_name: str

    def __init__(self) -> None:
        """Inicialize."""

        self._str_buffer = []
        self._esc_buffer = []
        self._idx_buffer = []

        self._papers_width = [P57_5MM, P69_5MM, P76MM]
        self._paper_width = P76MM

    def __del__(self) -> None:
        """Destroyer."""

        self.cleanup()

    def paperWidths(self) -> List[int]:
        """Return page widths."""

        return self._papers_width

    def paperWidth(self) -> int:
        """Return the current page width."""

        return self._paper_width

    def setPaperWidth(self, paper_width: int) -> None:
        """Set the paper width."""

        self._paper_width = paper_width

    def printerName(self) -> str:
        """Return the name of the printer."""

        return self._printer_name

    @decorators.not_implemented_warn
    def metric(self, metric: Any):
        """Not implemented."""

        pass

    def setPrinterName(self, name: str) -> None:
        """Set the name of the printer."""

        self._printer_name = name

    @decorators.beta_implementation
    def cleanup(self) -> None:
        """Clean buffer values."""

        if self._str_buffer:
            self._str_buffer = []

        if self._idx_buffer:
            self._idx_buffer = []

        self._idx_buffer = []

    @decorators.not_implemented_warn
    def flush(self):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def send(self, str_: str, col: int = -1, row: int = -1):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def sendStr(self, text_: str, col: int, row: int):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def sendEsc(self, esc_: str, col: int, row: int):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def cmd(self, command_: str, paint: Any, params: List[Any]):
        """Not implemented."""
        pass

    @decorators.beta_implementation
    def paperWidthToCols(self) -> int:
        """Return the number of columns from the paper width."""

        ret = -1
        if self._paper_width is P76MM:
            ret = 80
        elif self._paper_width is P69_5MM:
            ret = 65
        elif self._paper_width is P57_5MM:
            ret = 55
        return ret

    @decorators.not_implemented_warn
    def initFile(self):
        """Not implemented."""
        pass

    @decorators.beta_implementation
    def initStrBuffer(self) -> None:
        """Initialize the _str_buffer buffer."""

        if not self._str_buffer:
            self._str_buffer = []
        else:
            self._str_buffer.clear()

    @decorators.beta_implementation
    def initEscBuffer(self) -> None:
        """Initialize the _esc_buffer buffer."""
        if not self._esc_buffer:
            self._esc_buffer = []
        else:
            self._esc_buffer.clear()

    @decorators.beta_implementation
    def parsePrinterName(self) -> None:
        """Resolve values ​​from the printer name."""

        posdots = self._printer_name.find(":")
        self.server_ = self._printer_name[:posdots]
        self._queue_name = self._printer_name[posdots:]
        print("FLPosPrinter:parsePinterName", self.server_, self._queue_name)
