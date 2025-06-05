"""
Core package for utilities.

This package holds all functions and classes that are like side utilities that don't require
any dependency from other folders. So they're safe to import.
"""

from typing import Dict, List

DISABLE_CHECK_MEMORY_LEAKS: bool = True  # Disabled memory leaks checking.
PROXY_ACTIONS_DICT: Dict[int, List[str]] = {}
