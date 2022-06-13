"""Translate module."""


def translate(group: str, context: str) -> str:
    """Return the translation if it exists."""
    from PyQt5 import QtWidgets

    return QtWidgets.qApp.translate(group, context)
