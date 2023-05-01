"""Test require module."""

from pineboolib.application import qsadictmodules
from pineboolib.application.parsers import parser_qsa
from importlib import util
from pineboolib.qsa.tests import fixture_path
from pineboolib.loader.main import init_testing, finish_testing
import os

import unittest


class TestRequire(unittest.TestCase):
    """Test Require."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        parser_qsa.STRICT_MODE = True
        util_path = fixture_path("Import.py")
        spec = util.spec_from_file_location("Import", util_path)
        if spec and spec.loader is not None:
            module_instance = util.module_from_spec(spec)
            spec.loader.exec_module(module_instance)  # type: ignore [attr-defined]
            main_class = module_instance.FormInternalObj()  # type: ignore [attr-defined]
            qsadictmodules.QSADictModules.set_qsa_tree("formImport", main_class)  # type: ignore [arg-type]

    def test_basic_1(self) -> None:
        """Require test."""

        # print("*", dir(qsadictmodules.QSADictModules.qsa_dict_modules()))

        # req = qsa.require("test_require.qs")
        req = qsadictmodules.from_project("formImport").from_(
            os.path.join(os.path.dirname(__file__), "fixtures", "test_require.qs")
        )
        self.assertTrue(hasattr(req, "get"))

        instance_ = req(None)
        instance_.push("1")
        instance_.push("2")
        self.assertTrue(instance_.at(0), "1")
        self.assertTrue(instance_.at(1), "2")

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
