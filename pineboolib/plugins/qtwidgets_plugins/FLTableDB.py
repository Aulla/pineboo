"""FLTableDB Module."""

# -*- coding: utf-8 -*-
# pytype: skip-file
# type: ignore
from typing import Tuple, Any

MODULE: Any

pluginType = (
    MODULE
)  # noqa: F281  # La constante MODULE es parte de cómo PyQt carga los plugins. Es insertada por el loader en el namespace local


def moduleInformation() -> Tuple[str, str]:
    """Return module inormation."""

    return "pineboolib.fllegacy.fltabledb", ("FLTableDB")
