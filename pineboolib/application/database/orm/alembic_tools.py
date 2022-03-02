"""Alembic tools module."""

from sqlalchemy import engine_from_config, table
from pineboolib.application.utils import path
from pineboolib.application.parsers.parser_mtd import pnmtdparser
from pineboolib import logging
from alembic import config
import configparser


from typing import List, TYPE_CHECKING

LOGGER = logging.get_logger(__name__)

if TYPE_CHECKING:

    from pineboolib.interfaces import iconnection, itablemetadata

import os


class Migration:
    """Migration class."""

    _alembic_folder: str
    _current_dir: str
    _table_name: str

    def __init__(self, conn: "iconnection.IConnection"):
        """Initialize."""

        self._conn = conn
        self._current_dir = os.getcwd()
        self._alembic_folder = os.path.join(path._dir("cache"), conn.DBName(), "migrations")
        # self.generate_migration_file(metadata)

    def upgrade(self) -> bool:
        """Launch migration."""

        self.create()

        os.chdir(self._alembic_folder)

        config.main(argv=["revision", "-m", "'%s'" % ("prueba")])
        config.main(argv=["--raiseer", "upgrade", "head"])

        os.chdir(self._current_dir)

    def create(self):
        """Create structure."""

        if not os.path.exists(self._alembic_folder):
            os.mkdir(self._alembic_folder)
            init = True

            os.chdir(self._alembic_folder)

            config.main(argv=["init", "alembic"])

            dsn = self._conn.resolve_dsn()

            alembic_ini = os.path.join(self._alembic_folder, "alembic.ini")

            print("ALEMBIC.INI", alembic_ini)

            config_ = configparser.ConfigParser()
            config_.read(alembic_ini)
            config_["alembic"]["script_location"] = "alembic"
            config_["alembic"]["sqlalchemy.url"] = self._conn.resolve_dsn()

            with open(alembic_ini, "w") as configfile:  # save
                config_.write(configfile)

            os.chdir(self._current_dir)

