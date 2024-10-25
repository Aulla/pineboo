from pineboolib import application, logging
import os

LOGGER = logging.get_logger(__name__)


def load_project_config_file(external: str = "/external") -> None:
    """Load project config."""
    if application.PROJECT_NAME:

        from pineboolib.application.load_script import import_path

        if application.EXTERNAL_FOLDER:
            external = application.EXTERNAL_FOLDER
        path_config = os.path.abspath(
            os.path.join(external, "apps", application.PROJECT_NAME, "config.py")
        )
        LOGGER.info("PROJECT_NAME: %s, CONFIG: %s" % (application.PROJECT_NAME, path_config))
        if os.path.exists(path_config):
            import_path("config_project", path_config)
        else:
            LOGGER.warning("Config file not found: %s", path_config)
