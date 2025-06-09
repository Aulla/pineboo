"""
Replacement for Python logging that adds trace and other methods.

It allows MyPy/PyType to properly keep track of the new message types
"""

import logging as python_logging
from logging import handlers
from logging import basicConfig  # noqa: F401
from typing import Any, Set, Optional
import os
import sys
import gzip

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
MESSAGE = 25  # NEW
INFO = 20
HINT = 18  # NEW
NOTICE = 15  # NEW
DEBUG = 10
TRACE = 5  # NEW
NOTSET = 0

log_file_dir = (
    "/var/log" if not sys.platform.startswith("win") else os.path.join(os.environ["ProgramFiles"])
)


if not os.access(log_file_dir, os.W_OK):
    log_file_dir = os.path.join(os.path.expanduser("~"), "Pineboo", "log")
else:
    log_file_dir = os.path.join(log_file_dir, "Pineboo")

file_dir: Optional[str] = os.environ.get("PINEBOODIR")
if file_dir:
    log_file_dir = os.path.join("/pineboo/pineboo", "log")

LOG_FILE_PATH: str = os.path.join(log_file_dir, "pineboo.log")
LOG_FILE_BACKUP_COUNTS: int = 30  # ficheros de backup
LOG_FILE_FORMAT: str = "%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s"


class GZipRotator:
    """GZipRotator class."""

    def __call__(self, source: str, dest: str) -> None:
        """Call function."""

        os.rename(source, dest)
        f_in = open(dest, "rb")
        f_out = gzip.open("%s.gz" % dest, "wb")
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(dest)


class Logger(python_logging.Logger):
    """
    Replaced Logger object.

    Adds message, hint, notice  and trace
    """

    PINEBOO_DEFAULT_LEVEL = 0
    PINEBOO_LOGGERS: Set["Logger"] = set()

    @classmethod
    def set_pineboo_default_level(cls, level: int) -> None:
        """Set the default logging level for the whole app."""
        cls.PINEBOO_DEFAULT_LEVEL = level
        for logger in cls.PINEBOO_LOGGERS:
            logger.setLevel(level)

    def message(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a message."""
        self.log(MESSAGE, message, *args, **kwargs)

    def hint(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a hint."""
        self.log(HINT, message, *args, **kwargs)

    def notice(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a notice."""
        self.log(NOTICE, message, *args, **kwargs)

    def trace(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a trace."""
        self.log(TRACE, message, *args, **kwargs)


python_logging.Logger.manager.loggerClass = Logger  # type: ignore


def get_logger(name: Optional[str] = None) -> Logger:
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """

    if name:
        # print(name)
        # if not name.startswith("pineboolib."):
        #     raise ValueError("Invalid logger name %r, should be the module path.")
        logger: Logger = python_logging.Logger.manager.getLogger(name)  # type: ignore
        Logger.PINEBOO_LOGGERS.add(logger)
        if Logger.PINEBOO_DEFAULT_LEVEL != 0 and logger.level == 0:
            logger.setLevel(Logger.PINEBOO_DEFAULT_LEVEL)

        can_log_to_file = True
        base_dir = os.path.dirname(LOG_FILE_PATH)
        if not os.path.exists(base_dir):
            try:
                os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
            except Exception:
                can_log_to_file = False
        if can_log_to_file:
            can_log_to_file = os.access(base_dir, os.W_OK)

        if not can_log_to_file:
            logger.error("* Cannot write to log file %s (%s)" % (LOG_FILE_PATH, name))
        else:
            file_handler = handlers.TimedRotatingFileHandler(
                LOG_FILE_PATH, backupCount=LOG_FILE_BACKUP_COUNTS, when="midnight"
            )
            file_handler.setLevel(INFO)
            file_handler.setFormatter(python_logging.Formatter(LOG_FILE_FORMAT))
            file_handler.rotator = (
                GZipRotator()
            )  # https://stackoverflow.com/questions/8467978/python-want-logging-with-log-rotation-and-compression
            logger.addHandler(file_handler)

        return logger
    else:
        raise Exception("Pineboo getLogger does not allow for root logger")


def _add_logging_level(level_name: str, level_num: int) -> None:
    method_name = level_name.lower()

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def log_for_level(self: Any, message: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    python_logging.addLevelName(level_num, level_name)
    setattr(python_logging, level_name, level_num)
    if not hasattr(python_logging.getLoggerClass(), method_name):
        setattr(python_logging.getLoggerClass(), method_name, log_for_level)


_add_logging_level("TRACE", TRACE)
_add_logging_level("NOTICE", NOTICE)
_add_logging_level("HINT", HINT)
_add_logging_level("MESSAGE", MESSAGE)
