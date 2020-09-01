"""Dummy signal module."""

from typing import List, Callable
from pineboolib.application import connections


class FakeSignal(object):
    """FakeSignal class."""

    _remote_funcs: List[Callable]

    def __init__(self):
        """Initialice."""

        self._remote_funcs = []

    def connect(self, func_: Callable) -> None:
        """Set a function to connect."""

        if func_ not in self._remote_funcs:
            self._remote_funcs.append(func_)

    def disconnect(self, func_: Callable) -> None:
        """Set a function to disconnect."""

        if func_ in self._remote_funcs:
            self._remote_funcs.remove(func_)

    def emit(self, text: str) -> None:
        """Call all conected functions."""
        for func_ in self._remote_funcs:
            if connections.get_expected_args_num(func_) > 0:
                func_(text)
            else:
                func_()
