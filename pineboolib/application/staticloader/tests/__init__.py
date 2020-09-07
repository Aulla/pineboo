"""
Tests for static loader package.
"""

import os.path


def fixture_path(*path: str) -> str:
    """
    Get fixture path for this test folder.
    """
    basedir = os.path.realpath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, "fixtures", *path)
    return filepath
