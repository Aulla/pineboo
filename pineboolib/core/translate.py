"""Translate module."""


def translate(group: str, context: str) -> str:
    """Return the translation if it exists."""
    from PyQt6 import QtWidgets

    return QtWidgets.QApplication.translate(group.encode(), context.encode())
