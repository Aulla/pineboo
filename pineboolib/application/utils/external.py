from pineboolib import application, logging
import os
import importlib

LOGGER = logging.get_logger(__name__)


def load_project_config_file() -> None:
    """Load project config."""
    if application.EXTERNAL_FOLDER and application.PROJECT_NAME:

        path_config = os.path.abspath(
            os.path.join(application.EXTERNAL_FOLDER, "apps", application.PROJECT_NAME, "config.py")
        )
        LOGGER.info("PROJECT_NAME: %s, CONFIG: %s" % (application.PROJECT_NAME, path_config))
        if os.path.exists(path_config):
            from pineboolib.application.load_script import import_path

            import_path("config_project", path_config)
        else:
            LOGGER.warning("Config file not found: %s", path_config)


def reload_project_config() -> None:
    """Reload project config."""
    if application.EXTERNAL_FOLDER and application.PROJECT_NAME:
        LOGGER.warning("STATIC LOADER: Reinitializing project config file...")
        module_name = "apps.%s.config" % (application.PROJECT_NAME)
        try:
            importlib.import_module(module_name)
        except Exception as error:
            LOGGER.warning(
                "STATIC LOADER: Error reloading project config file %s, Error: %s"
                % (module_name, str(error))
            )
