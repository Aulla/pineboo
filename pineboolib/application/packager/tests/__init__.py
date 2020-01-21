"""Tests for packager package."""

import os


def fixture_path(*path: str) -> str:
    """
    Get fixture path for this test folder.
    """
    basedir = os.path.realpath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, "fixtures", *path)
    return filepath
