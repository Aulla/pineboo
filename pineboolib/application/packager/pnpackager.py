# -*- coding: utf-8 -*-
"""
PNPackager package.

Build .eneboopkg packages.
"""
from PyQt5 import QtCore

from pineboolib.core import decorators
from pineboolib import application, logging

import os
import re
import hashlib
import fnmatch

from typing import List, Any, Set

LOGGER = logging.getLogger(__name__)


class PNPackager(object):
    """PNPAckager class."""

    _encode_utf8: bool
    _filter: str
    _log_messages: List[str]
    _error_messages: List[str]
    _output: str
    _dest_file: str
    _file_list: List[str]
    _file_folders: List[str]
    _modnames: List[str]
    _ignored_ext: Set[str]

    def __init__(self, dest_file: str) -> None:
        """Initialize."""
        self._encode_utf8 = True
        self._filter = ""
        self._log_messages = []
        self._error_messages = []
        self._output = ""
        self._dest_file = dest_file
        self._file_list = []
        self._file_folders = []
        self._modnames = []
        self._ignored_ext = set([])

    def _find_files(self, basedir, glob_pattern="*", abort_on_match=False) -> List[str]:
        ignored_files = [
            "*~",
            ".*",
            "*.bak",
            "*.bakup",
            "*.tar.gz",
            "*.tar.bz2",
            "*.BASE.*",
            "*.LOCAL.*",
            "*.REMOTE.*",
            "*.*.rej",
            "*.*.orig",
        ]
        retfiles: List[str] = []

        for root, dirs, files in os.walk(basedir):
            baseroot = os.path.relpath(root, basedir)
            for pattern in ignored_files:
                delfiles = fnmatch.filter(files, pattern)
                for f in delfiles:
                    files.remove(f)
                deldirs = fnmatch.filter(dirs, pattern)
                for f in deldirs:
                    dirs.remove(f)
            pass_files = [
                os.path.join(baseroot, filename) for filename in fnmatch.filter(files, glob_pattern)
            ]
            if pass_files and abort_on_match:
                dirs[:] = []
            retfiles += pass_files
        return retfiles

    def modulesDef(self, module_folder: str) -> bytes:
        """Return modules definition."""

        modules_list = self._find_files(module_folder, "*.mod", True)

        modlines = []
        for module in sorted(modules_list):
            self._file_folders.append(os.path.dirname(module))
            self._modnames.append(os.path.basename(module))
            inittag = False
            for line_iso in open(
                os.path.abspath(os.path.join(module_folder, module)), encoding="ISO-8859-15"
            ):
                line_unicode = line_iso
                line = line_unicode
                if line.find("<MODULE>") != -1:
                    inittag = True
                if inittag:
                    modlines.append(line)
                if line.find("</MODULE>") != -1:
                    inittag = False

        data = """<!DOCTYPE modules_def>
        <modules>
        %s
        </modules>""" % "".join(
            modlines
        )
        return data.encode("utf-8")

    def filesDef(self, module_folder: str) -> bytes:
        """Retrun files definitions."""

        filelines = []
        shasum = ""
        load_ext = set([".qs", ".mtd", ".ts", ".ar", ".kut", ".qry", ".ui", ".xml", ".xpm", ".py"])

        for folder, module in zip(self._file_folders, self._modnames):
            fpath = os.path.join(module_folder, folder)
            files = self._find_files(fpath)
            module_name: Any = re.search(r"^\w+", module)
            module_name = module_name.group(0) if module_name else ""
            self._addLog("%s -> %s" % (fpath, module_name))
            for filename in files:
                bname, ext = os.path.splitext(filename)
                if ext not in load_ext:
                    self._ignored_ext.add(ext)
                    continue

                file_basename = os.path.basename(filename)
                filepath = os.path.join(fpath, filename)
                data_ = open(filepath, "br").read()
                sha1text = hashlib.new("sha1", data_).hexdigest().upper()
                # sha1text = hashlib.sha1(open(filepath).read()).hexdigest()
                # sha1text = sha1text.upper()
                shasum += sha1text
                self._file_list.append(filepath)
                filelines.append(
                    """  <file>
        <module>%s</module>
        <name>%s</name>
        <text>%s</text>
        <shatext>%s</shatext>
      </file>
    """
                    % (module_name, file_basename, file_basename, sha1text)
                )

        data = """<!DOCTYPE files_def>
    <files>
    %s  <shasum>%s</shasum>
    </files>
    """ % (
            "".join(filelines),
            hashlib.sha1(shasum.encode()).hexdigest().upper(),
        )

        return data.encode("utf-8")

    def pack(self, module_folder: str) -> bool:
        """Add files to package."""
        if module_folder.endswith(("/", "\\")):
            module_folder = module_folder[:-1]

        self._addLog("Creando paquete de módulos de %s" % module_folder)

        modules_def = self.modulesDef(module_folder)
        files_def = self.filesDef(module_folder)

        file_ = QtCore.QFile(QtCore.QDir.cleanPath(self._dest_file))
        if not file_.open(QtCore.QIODevice.WriteOnly):
            error = "Error opening file %r" % self._dest_file
            self._addError("pack", error)
            raise Exception(error)

        stream = QtCore.QDataStream(file_)
        stream.writeBytes(application.PROJECT.load_version().encode("utf-8"))
        stream = stream.writeBytes(b"")
        stream = stream.writeBytes(b"")
        stream = stream.writeBytes(b"")
        stream = stream.writeBytes(QtCore.qCompress(modules_def).data())
        stream = stream.writeBytes(QtCore.qCompress(files_def).data())
        # FILE CONTENTS
        try:
            for filepath in self._file_list:
                stream = stream.writeBytes(QtCore.qCompress(open(filepath, "rb").read()).data())

        except Exception as exception:
            self._addError("pack (add files)", str(exception))

            return False

        file_modules_def = open("%s/modules.def" % os.path.dirname(self._dest_file), "bw")
        file_modules_def.write(modules_def)
        file_modules_def.close()

        file_files_def = open("%s/files.def" % os.path.dirname(self._dest_file), "bw")
        file_files_def.write(files_def)
        file_files_def.close()

        self._addLog("Paquete creado. Extensiones ignoradas: %s " % "".join(self._ignored_ext))
        return True

    @decorators.NotImplementedWarn
    def unpack(self, folder: str) -> bool:
        """Extract files from package."""
        return False

    @decorators.NotImplementedWarn
    def output(self) -> str:
        """Return output messages."""

        return self._output

    def outputPackage(self) -> str:
        """Return outptPackage."""

        return self._dest_file

    @decorators.NotImplementedWarn
    def setEncodeUtf8(self, enconde_bool: bool = True) -> None:
        """Encode data with Utf8 charset."""

        self._encode_utf8 = enconde_bool

    @decorators.NotImplementedWarn
    def setFilter(self, filter: str = "") -> None:
        """Set a filter."""

        self._filter = filter

    def filter(self) -> str:
        """Return filter."""

        return self._filter

    def _addLog(self, message: str) -> None:
        """Add message to log."""
        self._log_messages.append(message)
        LOGGER.warning(message)

    def _addError(self, fun: str, message: str) -> None:
        """Add error message to log."""
        text = "%s : %s" % (fun, message)

        self._error_messages.append(text)
        LOGGER.warning(text)

    def logMessages(self) -> List[str]:
        """Return logs messages."""
        return self._log_messages

    def errorMessages(self) -> List[str]:
        """Return errormessages."""
        return self._error_messages
