"""
To resolve file and folder paths.
"""

from pineboolib.core.utils import logging
from pineboolib import application

import os
from typing import Optional, List

LOGGER = logging.get_logger(__name__)


def _dir(*x) -> str:
    """
    Calculate the path of a folder.

    @param x. str or array with the folder path.
    @return str with absolute path to a folder.
    """

    list_: List[str] = list(x)
    if os.name == "nt":
        list_ = [item.replace("/", "\\") for item in list_]

    return os.path.join(application.PROJECT.tmpdir, *list_)


def coalesce_path(*filenames) -> Optional[str]:
    """
    Return the first existing file in a group of files.

    @return path to the first file found.
    """
    for filename in filenames:
        if filename is None:
            # When the caller specifies None as the last item means that its OK to return None
            return None

        if filename in application.PROJECT.files:

            return application.PROJECT.files[filename].path()
    LOGGER.error(
        "coalesce_path: Ninguno de los ficheros especificados ha sido encontrado en el proyecto: %s",
        repr(filenames),
        stack_info=False,
    )
    return None


def _path(filename: str, show_not_found: bool = True) -> Optional[str]:
    """
    Return the first existing file in a group of files.

    @return path to file.
    """
    if filename not in application.PROJECT.files:
        if show_not_found:
            LOGGER.error("Fichero %s no encontrado en el proyecto.", filename, stack_info=False)
        return None
    return application.PROJECT.files[filename].path()
