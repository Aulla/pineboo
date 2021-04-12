"""Test_pnaccesscontrol module."""

from PyQt6 import QtXml  # type: ignore[import]

import unittest
from pineboolib.loader.main import init_testing, finish_testing


from .. import pnaccesscontrol


class TestPNAccessControl(unittest.TestCase):
    """TestPNAccessControl Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_missing_lines(self) -> None:
        """Test missing lines."""

        ac_ = pnaccesscontrol.PNAccessControl()
        ac_._acos_perms["uno"] = "uno:dos:tres"
        self.assertFalse(ac_.type())
        ac_.set(None)  # type: ignore [arg-type] # noqa: F821
        ac_.set(QtXml.QDomElement())
        ac_.get(None)  # type: ignore [arg-type] # noqa: F821
        ac_.get(QtXml.QDomDocument())

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
