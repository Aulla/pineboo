"""Flmysql_innodb module."""
from pineboolib.plugins.sql.flmysql_myisam import FLMYSQL_MYISAM


class FLMYSQL_INNODB(FLMYSQL_MYISAM):
    """FLMYSQL_INNODB class."""

    def __init__(self):
        """Inicialize."""

        super().__init__()
        self.name_ = "FLMYSQL_INNODB"
        self.alias_ = "MySQL INNODB (MYSQLDB)"
        self.noInnoDB = False
