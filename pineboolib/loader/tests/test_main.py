"""
Tests for loader.main.
"""
import unittest
from unittest.mock import patch, Mock
from pineboolib.loader.options import parse_options
from pineboolib.loader import main


class TestMain(unittest.TestCase):
    """Test Main load."""

    @patch("pineboolib.loader.main.sys.exit")
    @patch("pineboolib.loader.main.exec_main")
    @patch("pineboolib.loader.main.parse_options")
    def test_startup(
        self, mock_parse_options: Mock, mock_exec_main: Mock, mock_sys_exit: Mock
    ) -> None:
        """Test bug where logging tries to get incorrect options."""
        options = parse_options(custom_argv=[])
        mock_parse_options.return_value = options
        main.startup()
        mock_parse_options.assert_called_once()
        mock_exec_main.assert_called_once()
        mock_sys_exit.assert_called_once()

    # def test_framework(self) -> None:
    #    """Test startup_framework."""

    #    from pineboolib.loader.connection import IN_MEMORY_SQLITE_CONN
    #    from pineboolib import application

    #    main.startup_framework(IN_MEMORY_SQLITE_CONN)
    #    self.assertEqual(application.PROJECT.conn_manager.db().connectionName(), "default")


if __name__ == "__main__":
    unittest.main()
