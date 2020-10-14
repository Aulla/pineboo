"""
Application package for resources.

This package holds all functions and classes that are like side resources.
"""

from .projectmodule import Project
from typing import Dict, List

PROJECT = Project()

ATOMIC_LIST: List[str] = []
FILE_CLASSES: Dict[str, str] = {}

PINEBOO_VER = "0.75.16.2"

SHOW_CURSOR_EVENTS: bool = False  # Enable show pnsqlcursor actions debug.
SHOW_CLOSED_CONNECTION_WARNING: bool = False  # Enable show debug when connection is closed.
SHOW_NESTED_WARNING: bool = False  # Enable show nested debug.
USE_ATOMIC_LIST: bool = False  # Enable process queue.
SQLALCHEMY_NULL_POOL: bool = False  # Disable conections pool. Use for minimize problems with concurrences threads and sessions.
VIRTUAL_DB: bool = True  # Enable :memory: database on pytest.
LOG_SQL = False  # Enable sqlalchemy logs.
USE_WEBSOCKET_CHANNEL = False  # Enable websockets features.
USE_MISMATCHED_VIEWS = True
SHOW_TRANSACTIONS_AFTER_ATOMIC = True
