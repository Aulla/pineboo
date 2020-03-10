"""
Replacement for Python logging that adds trace and other methods.

It allows MyPy/PyType to properly keep track of the new message types
"""
import logging as python_logging
from logging import basicConfig  # noqa: F401
from typing import Any, Set

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


def get_logger(name: str = None) -> Logger:
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
