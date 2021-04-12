"""Qeventloop module."""

from PyQt6 import QtCore  # type: ignore[import]


class QEventLoop(QtCore.QEventLoop):
    """QEventLoop class."""

    def exitLoop(self) -> None:
        """Call exit loop."""
        super().exit()

    def enterLoop(self) -> None:
        """Call exec_ loop."""
        super().exec()
