"""Alembic tools module."""

from pineboolib.application.utils import path
from pineboolib import logging
from alembic import config, migration
import configparser
import os


from typing import List, Dict, Any, TYPE_CHECKING

LOGGER = logging.get_logger(__name__)

if TYPE_CHECKING:

    from pineboolib.interfaces import iconnection, itablemetadata


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

    def upgrade(self, metadata: "itablemetadata.ITableMetaData") -> bool:
        """Launch migration."""

        if not metadata.isQuery():
            self.create()

            # self.update_env()
            file_name = self.buildFile(metadata.name())
            if file_name:
                changes_dict = self._conn.driver().calculateChanges(metadata)

                if changes_dict and self.applyChangesInFile(file_name, changes_dict):
                    LOGGER.warning("APLICANDO CAMBIOS!!")
                    config.main(argv=["upgrade", "head"])
                else:
                    LOGGER.warning("Eliminando %s" % file_name)
                    os.remove(file_name)
            else:
                LOGGER.warning("no se encuentra el fichero de revisión a modificar")

            os.chdir(self._current_dir)

        return True

    def applyChangesInFile(self, file_name: str, changes_dict: Dict[str, List[Any]]):
        """Apply changes in file."""
        try:
            file_ = open(file_name, "r", encoding="UTF-8")
            data: str = file_.read()
            file_.close()

            def_upgrade = (
                "def upgrade() -> None:\n\n    %s" % (("\n    ").join(changes_dict["upgrade"]))
                if changes_dict["upgrade"]
                else None
            )

            def_downgrade = (
                "def downgrade() -> None:\n\n    %s" % (("\n    ").join(changes_dict["downgrade"]))
                if changes_dict["downgrade"]
                else None
            )

            if def_upgrade:
                data = data.replace("def upgrade() -> None:\n    pass", def_upgrade)
            if def_downgrade:
                data = data.replace("def downgrade() -> None:\n    pass", def_downgrade)

            file_ = open(file_name, "w", encoding="UTF-8")
            file_.write(data)
            file_.close()

        except Exception as error:
            LOGGER.warning("applyChangesInFile: %s (%s)" % (file_name, str(error)))
            return False

        return True

    def buildFile(self, table_name: str) -> str:
        """Build file for migration."""
        result = ""
        try:
            os.chdir(self._alembic_folder)
            config.main(argv=["revision", "-m", "alter_table_%s" % table_name])
            result = self.getNewFileName()
        except Exception as error:
            LOGGER.warning("Error building file: %s" % (str(error)))

        return result

    def getNewFileName(self) -> str:
        """Return new file name."""

        current_revision = self.getCurrentRev()
        if current_revision:
            current_revision = "'%s'" % current_revision

        folder_path = os.path.join(self._alembic_folder, "alembic", "versions")
        last = None
        for file_name in os.listdir(folder_path):

            if file_name.startswith("_"):
                continue

            file_path = os.path.join(folder_path, file_name)
            file_time = os.path.getctime(file_path)

            if last is None:
                last = [file_time, file_path]
                continue

            if file_time > last[0]:  # type: ignore [unreachable]
                last = [file_time, file_path]

        return "" if last is None else str(last[1])

    def getCurrentRev(self):
        """Return current revision stored in database."""

        context = migration.MigrationContext.configure(self._conn.connection())
        return context.get_current_revision()

    def update_enviroment(self):
        """Update enviroment."""

        pass

    def create(self):
        """Create structure."""

        if not os.path.exists(self._alembic_folder):
            # borrar alembic_version
            os.mkdir(self._alembic_folder)
            os.chdir(self._alembic_folder)

            config.main(argv=["init", "alembic"])

            alembic_ini = os.path.join(self._alembic_folder, "alembic.ini")

            config_ = configparser.ConfigParser()
            config_.read(alembic_ini)
            config_["alembic"]["script_location"] = "alembic"
            config_["alembic"]["sqlalchemy.url"] = self._conn.resolve_dsn()

            with open(alembic_ini, "w") as configfile:  # save
                config_.write(configfile)

            os.chdir(self._current_dir)
