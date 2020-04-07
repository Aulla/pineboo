"""Test_sysbasetype module."""

import unittest

from pineboolib import application

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.core import settings


class TestMtdParserGeneral(unittest.TestCase):
    """TestMtdParserGeneral Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        init_testing()

    def test_basic_1(self) -> None:
        """Test basic functions."""
        from pineboolib.application.parsers.mtdparser import pnmtdparser
        from pineboolib.core.utils.utils_base import filedir
        import os

        file = filedir(
            "%s/cache/temp_db/sys/file.mtd/flmodules_model.py"
            % settings.CONFIG.value("ebcomportamiento/temp_dir")
        )
        if os.path.exists(file):
            os.remove(file)
        action_xml = application.PROJECT.actions["flmodules"]
        self.assertTrue(action_xml)
        pnmtdparser.mtd_parse(action_xml)
        self.assertTrue(os.path.exists(file))

    def test_basic_2(self) -> None:
        """Test ORM parser."""

        from pineboolib.application.parsers.mtdparser import pnmtdparser, pnormmodelsfactory

        import os

        for action_name in application.PROJECT.actions:
            file_path = pnmtdparser.mtd_parse(application.PROJECT.actions[action_name])
            if file_path:
                self.assertTrue(os.path.exists(file_path))

        pnormmodelsfactory.load_models()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
