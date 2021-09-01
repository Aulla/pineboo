"""Flmysql_innodb module."""
from .flmysql_myisam import FLMYSQL_MYISAM


class FLMYSQL_INNODB(FLMYSQL_MYISAM):  # pylint: disable=invalid-name
    """FLMYSQL_INNODB class."""

    def __init__(self):
        """Inicialize."""

        super().__init__()
        self.name_ = "FLMYSQL_INNODB"
        self.alias_ = "MySQL InnoDB (MYSQLDB)"
        self._no_inno_db = False
        self._default_charset = "DEFAULT CHARACTER SET = UTF8MB4 COLLATE = UTF8MB4_BIN"
