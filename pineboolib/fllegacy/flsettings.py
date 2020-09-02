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
        ret = self._settings.value(key, [])
        return ret.split(",")

    def readEntry(self, _key: str, _def: Any = None) -> Any:
        """Return a value."""

        return self._settings.value(_key, _def)

    def readNumEntry(self, key: str, _def: int = 0) -> int:
        """Return a int value."""

        ret = self._settings.value(key, _def)
        if isinstance(ret, (int, float, str)):
            return int(ret)

        raise ValueError("Configuration key %s cannot be converted to integer" % key)

    def readDoubleEntry(self, key: str, _def: Union[bytes, str, SupportsFloat] = 0.00) -> float:
        """Return a float value."""

        ret = self._settings.value(key, _def)
        return float(ret)

    def readBoolEntry(self, key: str, _def: bool = False) -> bool:
        """Return a bool value."""

        ret = self._settings.value(key, _def)
        return utils_base.text2bool(str(ret))

    def writeEntry(self, key: str, value: Any) -> None:
        """Set a value."""

        self._settings.setValue(key, value)

    def writeEntryList(self, key: str, value: List[str]) -> None:
        """Set a value list."""
        # FIXME: This function flattens the array when saving in some cases. Should always save an array.

        self._settings.setValue(key, ",".join(value))
