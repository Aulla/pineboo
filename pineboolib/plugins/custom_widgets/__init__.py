"""Custom widgets package."""

from typing import Tuple, Any

try:
    MODULE: Any
    pluginType = MODULE  # noqa : F821
except Exception:
    pass


def moduleInformation() -> Tuple[str, str]:  # pylint: disable=invalid-name
    """Return module inormation."""

    return "", ""
