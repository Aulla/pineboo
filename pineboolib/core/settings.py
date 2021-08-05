# -*- coding: utf-8 -*-
"""
Main interface with INI-Style settings.

Contains 2 global variables:

  - config: for pinebooConfig.ini
  - settings: for pinebooSettings.ini

*It's a config or a setting?*

If it's meant to be changed before Pineboo runs, it's a config.

If it's meant to be changed while running Pineboo, inside QS code, it's a setting.
"""
import json
import time
from .utils import logging

from PyQt6 import QtCore  # type: ignore[import]

from typing import Dict, List, Any, Union, Tuple, Type

LOGGER = logging.get_logger(__name__)


class PinebooSettings(QtCore.QSettings):
    """Manipulate settings for the specified file."""

    CACHE_TIME_SEC = 30

    def __init__(self, name: str = "") -> None:
        """
        Build a new settings for the specified "name".

        "name" will be used for creating/opening the INI file.
        Values are saved in JSON oposed to plain text.
        """
        format_ = (
            QtCore.QSettings.Format.IniFormat
        )  # QtCore.QSettings.NativeFormat - usar solo ficheros ini.
        scope_ = QtCore.QSettings.Scope.UserScope
        self.organization = "Eneboo"
        self.application = "Pineboo%s" % name
        self.cache: Dict[str, Tuple[float, Any]] = {}
        super().__init__(format_, scope_, self.organization, self.application)

    @staticmethod
    def dump_qsize(value: "QtCore.QSize") -> Dict[str, Union[str, int]]:
        """Convert QtCore.QSize into a Dict suitable to be converted to JSON."""
        return {"__class__": "QtCore.QSize", "width": value.width(), "height": value.height()}

    def dump_value(
        self, value: Union["QtCore.QSize", str, bool, int, List[str], Dict[Any, Any]]
    ) -> str:
        """Convert Any value into JSON to be used for saving in INI."""
        if isinstance(value, QtCore.QSize):
            value = self.dump_qsize(value)
        return json.dumps(value)

    def load_value(self, value_text: str) -> Any:
        """Parse INI text values into proper Python variables."""
        value: Any = json.loads(value_text)
        if (
            isinstance(value, dict)
            and "__class__" in value.keys()
            and value["__class__"] == "QtCore.QSize"
        ):
            value = QtCore.QSize(value["width"], value["height"])

        return value

    def value(self, key: str, def_value: Any = None, type: Type = None) -> Any:
        """Get a value from INI for the specified key."""
        curtime = time.time()
        cached_value = self.cache.get(key, None)

        if cached_value is not None:  # Si tengo valor cacheado
            if curtime - cached_value[0] > self.CACHE_TIME_SEC:  # y he caducado
                del self.cache[key]
            else:
                if cached_value[1] is not None:  # Si es bueno el valor cacheado
                    return cached_value[1]

        val = self._value(key)  # repgunto por valor

        if val is not None:  # Si hay valor, lo cacheo
            self.cache[key] = (curtime, val)
        else:  # si no devuelvo default
            val = def_value
        return val

    def _value(self, key: str, default: Any = None) -> Any:
        value = super().value(key, None)
        if value is None:
            LOGGER.debug(
                "%s.value(%s) -> Default: %s %r", self.application, key, type(default), default
            )
            return default
        try:
            ret = self.load_value(value)
            LOGGER.debug("%s.value(%s) -> Loaded: %s %r", self.application, key, type(ret), ret)
            return ret
        except Exception as exc:
            # No format, just string
            LOGGER.debug("Error trying to parse json for %s: %s (%s)", key, exc, value)
            return value

    def set_value(self, key: str, value: Union["QtCore.QSize", str, bool, int, List[Any]]) -> None:
        """Set a value into INI file for specified key."""
        LOGGER.debug("%s.set_value(%s) <- %s %r", self.application, key, type(value), value)
        curtime = time.time()
        self.cache[key] = (curtime, value)
        return super().setValue(key, self.dump_value(value))

    setValue = set_value


CONFIG = PinebooSettings("Config")
SETTINGS = PinebooSettings("Settings")
