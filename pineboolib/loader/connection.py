"""Connection Module."""

import optparse
from . import projectconfig

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.database import pnconnection

DEFAULT_SQLITE_CONN = projectconfig.ProjectConfig(
    database="pineboo.sqlite3", type="SQLite3 (SQLITE3)"
)
IN_MEMORY_SQLITE_CONN = projectconfig.ProjectConfig(
    database=":memory:", type="SQLite3 (SQLITE3)", username="memory_user"
)


def config_dbconn(options: "optparse.Values") -> Optional["projectconfig.ProjectConfig"]:
    """Obtain a config connection from a file."""

    if options.project:  # FIXME: --project debería ser capaz de sobreescribir algunas opciones
        if not options.project.endswith(".xml"):
            options.project += ".xml"
        prj_name = options.project
        try:
            return projectconfig.ProjectConfig(load_xml=prj_name)
        except projectconfig.PasswordMismatchError:
            # If fails without password, ignore the exception so the stack is cleaned.
            # This avoids seeing two exceptions if password is wrong.
            pass

        import getpass

        password = getpass.getpass()
        return projectconfig.ProjectConfig(load_xml=prj_name, project_password=password)

    if options.connection:
        return projectconfig.ProjectConfig(connstring=options.connection)

    return None


def connect_to_db(config: "projectconfig.ProjectConfig") -> "pnconnection.PNConnection":
    """Try connect a database with projectConfig data."""
    if config.database is None:
        raise ValueError("database not set")
    if config.type is None:
        raise ValueError("type not set")

    from pineboolib.application.database import pnconnection

    port = int(config.port) if config.port else None
    connection = pnconnection.PNConnection(
        config.database,
        config.host or "",
        port or 0,
        config.username or "",
        config.password or "",
        config.type,
    )
    return connection
