"""
Application package for resources.

This package holds all functions and classes that are like side resources.
"""

from .projectmodule import Project
from typing import Dict

PROJECT = Project()
SHOW_CURSOR_EVENTS: bool = False
SHOW_CLOSED_CONNECTION_WARNING: bool = False
VIRTUAL_DB: bool = True  # Enable :memory: database on pytest
LOG_SQL = False
USE_WEBSOCKET_CHANNEL = False
PINEBOO_VER = "0.73.16.4"
FILE_CLASSES: Dict[str, str] = {}
