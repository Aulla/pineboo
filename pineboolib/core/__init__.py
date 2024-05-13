"""
Core package for utilities.

This package holds all functions and classes that are like side utilities that don't require
any dependency from other folders. So they're safe to import.
"""

import os
import sys

DISABLE_CHECK_MEMORY_LEAKS: bool = True  # Disabled memory leaks checking.


log_file_dir = (
    "/var/log" if not sys.platform.startswith("win") else os.path.join(os.environ["ProgramFiles"])
)
if not os.access(log_file_dir, os.W_OK):
    log_file_dir = os.path.expanduser("~")

LOG_FILE_PATH: str = os.path.join(log_file_dir, "Pineboo", "pineboo.log")
LOG_FILE_BACKUP_COUNTS: int = 30  # ficheros de backup
LOG_FILE_FORMAT: str = "%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s"
