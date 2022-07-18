"""Flinvalidator module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtGui  # type: ignore
from typing import Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6 import QtWidgets  # pragma: no cover


class FLIntValidator(QtGui.QIntValidator):
    """FLIntValidator Class."""

    _formatting: bool

    def __init__(self, minimum: int, maximum: int, parent: "QtWidgets.QWidget") -> None:
        """Inicialize."""

        super().__init__(minimum, maximum, parent)
        self._formatting = False

    def validate(self, input_: str, pos_cursor: int) -> Tuple[Any, str, int]:
        """Return validate result."""

        if not input_ or self._formatting:
            return (self.State.Acceptable, input_, pos_cursor)

        state = super().validate(input_, pos_cursor)

        ret_0 = None
        ret_1 = state[1]
        ret_2 = state[2]

        if state[0] in (self.State.Invalid, self.State.Intermediate) and len(input_) > 0:
            text_ = input_[1:]
            if (
                input_[0] == "-"
                and super().validate(text_, pos_cursor)[0] == self.State.Acceptable
                or not text_
            ):
                ret_0 = self.State.Acceptable
            else:
                ret_0 = self.State.Invalid
        else:
            ret_0 = self.State.Acceptable

        return (ret_0, ret_1, ret_2)
