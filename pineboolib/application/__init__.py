"""
Application package for resources.

This package holds all functions and classes that are like side resources.
"""

from .projectmodule import Project
from typing import Dict, List, Any

PROJECT = Project()

SERIALIZE_LIST: Dict[int, List[str]] = {}
FILE_CLASSES: Dict[str, str] = {}
ID_SESSION: str = ""

PINEBOO_VER = "0.99.48.1"

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
USE_REPORT_VIEWER: bool = True  # Enable internal report viewer.
ENABLE_ACLS: bool = True  # Enable acls usage.
USE_INTERACTIVE_GUI: bool = True  # Enable interactiveGUI value.
ENABLE_CALL_EXCEPTIONS: bool = True  # Enable QSA calls exceptions.
PARSE_PROJECT_ON_INIT: bool = True  # Parse all projects on init.
USE_ALTER_TABLE_LEGACY: bool = True
PERSISTENT: Dict[str, Any] = {}
USE_FLFILES_FOLDER_AS_STATIC_LOAD: bool = True
