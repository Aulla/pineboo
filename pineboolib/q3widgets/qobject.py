"""Qmenu module."""
from PyQt6 import QtCore  # type: ignore[import]

from typing import List, Optional, Any
from pineboolib import application


class QObject(QtCore.QObject):
    """QObject class."""

    _event_filter_function: str
    _allowed_events: List[Any]

    def __ini__(self) -> None:
        """Initialize."""

        super().__init__()

        self._event_filter_function = ""
        self._allowed_events = []

    def eventFilter(
        self, obj: Optional["QtCore.QObject"], event: Optional["QtCore.QEvent"]
    ) -> bool:
        """Return event filter result."""

        result: Any = False
        if self._event_filter_function:
            if event in self._allowed_events:
                result = application.PROJECT.call(self._event_filter_function, [obj, event])
                if not isinstance(result, bool):
                    result = False
        else:
            if event in self._allowed_events:
                result = super().eventFilter(obj, event)  # type: ignore [arg-type]

        return result

    def set_event_filter_function(self, func_name: str) -> None:
        """Set envent finter function name."""

        self._event_filter_function = func_name

    def set_allowed_events(self, allowed_events: List[Any]) -> None:
        """Set allowed events."""

        self._allowed_events = allowed_events

    def get_allowed_events(self) -> List[Any]:
        """Return allowed events lists."""

        return self._allowed_events

    def get_event_filter_function(self) -> str:
        """Return event filter function."""

        return self._event_filter_function

    eventFilterFunction = property(get_event_filter_function, set_event_filter_function)
    allowedEvents = property(get_allowed_events, set_allowed_events)
