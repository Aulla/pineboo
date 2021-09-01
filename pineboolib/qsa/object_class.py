"""Object_class module."""

from PyQt6 import QtCore  # type: ignore[import]

from typing import Set, Tuple, Any
from pineboolib.application import connections


class ObjectClass(object):
    """ObjectClass class."""

    _class_connections: Set[Tuple]
    signal_test = QtCore.pyqtSignal(str, QtCore.QObject)

    def module_connect(self, sender: Any, signal: str, receiver: Any, slot: str) -> None:
        """Connect two objects."""

        signal_slot = connections.connect(sender, signal, receiver, slot, caller=self)
        if not signal_slot:
            return

        if not hasattr(self, "_class_connections"):
            self._class_connections = set([])

        self._class_connections.add(signal_slot)

    def module_disconnect(self, sender: Any, signal: str, receiver: Any, slot: str) -> None:
        """Disconnect two objects."""

        # print(" > > > disconnect:", self)

        signal_slot = connections.disconnect(sender, signal, receiver, slot)
        if not signal_slot:
            return

        if hasattr(self, "_class_connections"):
            for conn_ in self._class_connections:
                # PyQt6-Stubs misses signal.signal
                if (
                    conn_[0].signal == getattr(signal_slot[0], "signal")
                    and conn_[1].__name__ == signal_slot[1].__name__
                ):
                    self._class_connections.remove(conn_)
                    break
