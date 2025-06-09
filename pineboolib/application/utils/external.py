"""External module."""

from pineboolib import application, logging
import os
import importlib

from typing import Callable, Optional

LOGGER = logging.get_logger(__name__)


def load_project_config_file() -> None:
    """Load project config."""
    if application.EXTERNAL_FOLDER and application.PROJECT_NAME:
        path_config = os.path.abspath(
            os.path.join(
                application.EXTERNAL_FOLDER, "apps", application.PROJECT_NAME, "config.py"
            )  # Carga ruta
        )
        LOGGER.info("PROJECT_NAME: %s, CONFIG: %s" % (application.PROJECT_NAME, path_config))
        if os.path.exists(path_config):
            from pineboolib.application.load_script import import_path

            mod_ = import_path("config_project", path_config)
            launch_function(mod_, "cargar_dependencias")  # type: ignore [arg-type]
        else:
            LOGGER.warning("Config file not found: %s", path_config)


def reload_project_config() -> None:
    """Reload project config."""
    if application.EXTERNAL_FOLDER and application.PROJECT_NAME:
        LOGGER.warning("STATIC LOADER: Reinitializing project config file...")
        module_name = "apps.%s.config" % (application.PROJECT_NAME)
        try:
            mod_ = importlib.import_module(module_name)
            launch_function(mod_, "cargar_dependencias")  # type: ignore [arg-type]

        except Exception as error:
            LOGGER.warning(
                "STATIC LOADER: Error reloading project config file %s, Error: %s"
                % (module_name, str(error))
            )


def launch_function(mod_: "Callable", func_name: Optional[str] = None) -> None:
    """Launch function."""

    func_ = getattr(mod_, func_name, None) if func_name else None
    if func_:
        LOGGER.info("EXTERNAL: %s function found in %s" % (func_name, mod_.__name__))
        func_()
    else:
        LOGGER.warning("STATIC LOADER: No %s function found in %s" % (func_name, mod_.__name__))
