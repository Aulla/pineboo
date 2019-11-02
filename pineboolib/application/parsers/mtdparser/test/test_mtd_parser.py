"""Test_sysbasetype module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.core.settings import config


class TestMtdParserGeneral(unittest.TestCase):
    """TestMtdParserGeneral Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        from pineboolib.core.settings import config

        config.set_value("ebcomportamiento/orm_parser_disabled", False)

        init_testing()

    def test_basic(self) -> None:
        """Test basic functions."""
        from pineboolib.application.parsers.mtdparser import pnmtdparser
        from pineboolib.core.utils.utils_base import filedir
        import os

        file = filedir(
            "%s/cache/temp_db/sys/file.mtd/flmodules_model.py"
            % config.value("ebcomportamiento/temp_dir")
        )
        if os.path.exists(file):
            os.remove(file)
        pnmtdparser.mtd_parse("flmodules")
        self.assertTrue(os.path.exists(file))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        from pineboolib.core.settings import config

        config.set_value("ebcomportamiento/orm_parser_disabled", True)
        finish_testing()
