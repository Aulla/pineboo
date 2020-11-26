"""
Application package for resources.

This package holds all functions and classes that are like side resources.
"""

from .projectmodule import Project
from typing import Dict, List

PROJECT = Project()

SERIALIZE_LIST: Dict[int, List[str]] = {}
FILE_CLASSES: Dict[str, str] = {}

PINEBOO_VER = "0.76.26.1"

SHOW_CURSOR_EVENTS: bool = False  # Enable show pnsqlcursor actions debug.
SHOW_CONNECTION_EVENTS: bool = False  # Enable show debug when connection is closed.
SHOW_NESTED_WARNING: bool = False  # Enable show nested debug.
VIRTUAL_DB: bool = True  # Enable :memory: database on pytest.
LOG_SQL: bool = False  # Enable sqlalchemy logs.
USE_WEBSOCKET_CHANNEL: bool = False  # Enable websockets features.
USE_MISMATCHED_VIEWS: bool = False  # Enable mismatched views.
RECOVERING_CONNECTIONS: bool = False  # Recovering state.
AUTO_RELOAD_BAD_CONNECTIONS: bool = False  # Auto reload bad conecctions.
DEVELOPER_MODE: bool = True  # Skip some bugs, critical in production.
