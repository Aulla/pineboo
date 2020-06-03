"""
Application package for resources.

This package holds all functions and classes that are like side resources.
"""
from .projectmodule import Project

PROJECT = Project()
SHOW_CURSOR_EVENTS: bool = False
VIRTUAL_DB: bool = True  # Enable :memory: database on pytest
LOG_SQL = False
PINEBOO_VER = "0.72.1"
