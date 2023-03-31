"""Test require module."""

from pineboolib.qsa import qsa
from pineboolib.application import qsadictmodules, load_script
from importlib import util
from pineboolib.qsa.tests import fixture_read, fixture_path
from pineboolib.loader.main import init_testing, finish_testing

import unittest


class TestRequire(unittest.TestCase):
    """Test Require."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

        util_path = fixture_path("UTIL.py")
        spec = util.spec_from_file_location("UTIL", util_path)
        if spec and spec.loader is not None:
            module_instance = util.module_from_spec(spec)
            spec.loader.exec_module(module_instance)

        qsadictmodules.QSADictModules.set_qsa_tree("formUTIL", module_instance)

    def test_basic(self) -> None:
        """Require test."""

        req = qsa.require("test")
        self.assertTrue(hasattr(req, "get"))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
