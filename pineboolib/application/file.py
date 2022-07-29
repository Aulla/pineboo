"""
File module.
"""
import os
from pineboolib import logging
from typing import Optional

from .utils import path

LOGGER = logging.get_logger(__name__)


class File(object):
    """
    Manage files from a module.
    """

    module: str
    filename: str
    basedir: Optional[str]
    sha: Optional[str]
    name: str
    ext: str

    def __init__(
        self,
        module: str,
        filename: str,
        sha: Optional[str] = None,
        basedir: Optional[str] = None,
        db_name: Optional[str] = None,
    ) -> None:
        """
        Initialize.

        @param module. Identificador del módulo propietario
        @param filename. Nombre del fichero
        @param sha. Código sha1 del contenido del fichero
        @param basedir. Ruta al fichero en cache
        """
        self.module = module
        self.filename = filename
        self.sha = sha
        self.name, self.ext = os.path.splitext(filename)

        self.filekey = (
            "%s/%s/file%s/%s/%s%s" % (db_name, module, self.ext, self.name, sha, self.ext)
            if self.sha
            else filename
        )

        self.basedir = basedir

    def path(self) -> str:
        """
        Return absolute path to file.

        @return Ruta absoluta del fichero
        """
        return (
            path._dir(self.basedir, self.filename)
            if self.basedir
            else path._dir("cache", *(self.filekey.split("/")))
        )
