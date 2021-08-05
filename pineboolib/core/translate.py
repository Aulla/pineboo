"""Translate module."""

from PyQt6 import QtWidgets


def translate(group: str, context: str) -> str:
    """Return the translation if it exists."""

    return QtWidgets.QApplication.translate(group, context)
