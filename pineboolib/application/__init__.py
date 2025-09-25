"""
Application package for resources.

This package holds all functions and classes that are like side resources.
"""

from pineboolib.application.projectmodule import Project
from pineboolib.core import settings
from typing import Dict, List, Any, Optional

PROJECT = Project()

SERIALIZE_LIST: Dict[int, List[str]] = {}
FILE_CLASSES: Dict[str, str] = {}
ID_SESSION: str = ""

PINEBOO_VER = "0.99.94.1"

SHOW_CURSOR_EVENTS: bool = False  # Enable show pnsqlcursor actions debug.
SHOW_CONNECTION_EVENTS: bool = False  # Enable show debug when connection is closed.
SHOW_NESTED_WARNING: bool = False  # Enable show nested debug.
VIRTUAL_DB: bool = True  # Enable :memory: database on pytest.
LOG_SQL: bool = False  # Enable sqlalchemy logs.
USE_WEBSOCKET_CHANNEL: bool = False  # Enable websockets features.
USE_MISMATCHED_VIEWS: bool = False  # Enable mismatched views.
RECOVERING_CONNECTIONS: bool = False  # Recovering state.
AUTO_RELOAD_BAD_CONNECTIONS: bool = False  # Auto reload bad conecctions.
USE_REPORT_VIEWER: bool = False  # Enable internal report viewer.
ENABLE_ACLS: bool = True  # Enable acls usage.
USE_INTERACTIVE_GUI: bool = True  # Enable interactiveGUI value.
ENABLE_CALL_EXCEPTIONS: bool = True  # Enable QSA calls exceptions.
PARSE_PROJECT_ON_INIT: bool = settings.CONFIG.value("ebcomportamiento/parseProject", False)
USE_ALTER_TABLE_LEGACY: bool = True
PERSISTENT: Dict[str, Any] = {}
USE_FLFILES_FOLDER_AS_STATIC_LOAD: bool = True
TESTING_MODE: bool = False  # True when testing_mode else False
ALLOW_ALTER_TABLE: bool = True
PROJECT_NAME: Optional[str] = None  # Nombre del proyecto
EXTERNAL_FOLDER: Optional[str] = None  # Carpeta externa
UPDATE_FLFILES_FROM_FLFOLDER: bool = False  # Actualizar ficheros flfiles
FRAMEWORK_DEBUG_LEVEL: int = 20  # Nivel de debug 30 .... 0 en bloques de 5
