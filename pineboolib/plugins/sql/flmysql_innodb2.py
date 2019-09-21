"""Flmysql_innodb2 module."""
from .flmysql_myisam2 import FLMYSQL_MYISAM2


class FLMYSQL_INNODB2(FLMYSQL_MYISAM2):
    """FLMSQL_INNODB2 class."""

    def __init__(self):
        """Inicialize."""
        super().__init__()
        self.name_ = "FLMYSQL_INNODB2"
        self.alias_ = "MySQL INNODB (PyMySQL)"
        self.noInnoDB = False
