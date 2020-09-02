"""Flsettings module."""
# -*- coding: utf-8 -*-
from pineboolib.core import settings
from pineboolib.core.utils import utils_base


from typing import List, Union, Any
from typing import SupportsFloat


class FLSettings(object):
    """FLSettings class."""

    _settings = settings.SETTINGS

    def readListEntry(self, key: str) -> List[str]:
        """Return a value list."""
        ret_ = self._settings.value(key, [])
        if not isinstance(ret_, list):
            ret_ = ret_.split(",")

        return ret_

    def readEntry(self, _key: str, _def: Any = None) -> Any:
        """Return a value."""

        return self._settings.value(_key, _def)

    def readNumEntry(self, key: str, _def: int = 0) -> int:
        """Return a int value."""

        return int(self._settings.value(key, _def))

    def readDoubleEntry(self, key: str, _def: Union[bytes, str, SupportsFloat] = 0.00) -> float:
        """Return a float value."""

        return float(self._settings.value(key, _def))

    def readBoolEntry(self, key: str, _def: bool = False) -> bool:
        """Return a bool value."""

        return utils_base.text2bool(str(self._settings.value(key, _def)))

    def writeEntry(self, key: str, value: Any) -> None:
        """Set a value."""

        self._settings.setValue(key, value)

    def writeEntryList(self, key: str, value: List[str]) -> None:
        """Set a value list."""
        # FIXME: This function flattens the array when saving in some cases. Should always save an array.

        self._settings.setValue(key, ",".join(value))
