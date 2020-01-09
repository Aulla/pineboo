"""Test projectmodule module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from . import fixture_path


class TestProjectModule(unittest.TestCase):
    """TestProjectModule Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_parse_script(self) -> None:
        """Test parse_script function."""

        from pineboolib import application
        import os
        import shutil

        path = fixture_path("flfacturac.qs")
        tmp_path = "%s/%s" % (application.PROJECT.tmpdir, "temp_qs_projectmodule.qs")
        path_py = "%s.qs.py" % tmp_path[:-3]
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        if os.path.exists(path_py):
            os.remove(path_py)

        shutil.copy(path, tmp_path)
        application.PROJECT.parse_script(tmp_path)

        self.assertTrue(os.path.exists(path_py))

        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        if os.path.exists(path_py):
            os.remove(path_py)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
