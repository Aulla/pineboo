"""Test_sysbasetype module."""

import unittest
from pineboolib.loader.main import init_testing


class TestMtdParserGeneral(unittest.TestCase):
    """TestMtdParserGeneral Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test basic functions."""
        from pineboolib.application.parsers.mtdparser import pnmtdparser
        from pineboolib.core.utils.utils_base import filedir
        import os

        file = filedir("../tempdata/cache/:memory:/sys/file.mtd/flmodules_model.py")
        os.remove(file)
        pnmtdparser.mtd_parse("flmodules")
        self.assertTrue(os.path.exists(file))
