# -*- coding: utf-8 -*-
"""
PNPackager package.

Build .eneboopkg packages.
"""
from PyQt6 import QtCore  # type: ignore[import]

from pineboolib.core import decorators
from pineboolib import logging
from pineboolib.application import PINEBOO_VER

import os
import re
import hashlib
import fnmatch
import sys

from typing import List, Any, Set

LOGGER = logging.get_logger(__name__)


def main() -> None:
    """Run main program."""

    option = sys.argv[1] if len(sys.argv) > 1 else None

    if option == "create":
        folders = sys.argv[2] if len(sys.argv) > 1 else ""

        dest_name = ""
        emulate_abanq = False

        if len(sys.argv) == 4:
            if sys.argv[3] == "-a":
                emulate_abanq = True
            else:
                dest_name = sys.argv[3]
        elif len(sys.argv) == 5:
            dest_name = sys.argv[3]
            emulate_abanq = sys.argv[4] == "-a"

        packager = PNPackager(dest_name)
        packager.pack(folders, emulate_abanq)
    else:
        print("Opción %s desconocida." % option)


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

    def __init__(self, dest_file: str = "") -> None:
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
                for delete_file in delfiles:
                    files.remove(delete_file)
                deldirs = fnmatch.filter(dirs, pattern)
                for delete_dir in deldirs:
                    dirs.remove(delete_dir)
            pass_files = [
                os.path.join(baseroot, filename) for filename in fnmatch.filter(files, glob_pattern)
            ]
            if pass_files and abort_on_match:
                dirs[:] = []
            retfiles += pass_files
        return retfiles

    def modulesDef(self, module_folder_list: List) -> bytes:
        """Return modules definition."""

        modules_list: List[str] = []
        for modulefolder in module_folder_list:
            modules_list = modules_list + self._find_files(modulefolder, "*.mod", True)

        modlines = []
        for module in modules_list:
            self._file_folders.append(os.path.dirname(module))
            self._modnames.append(os.path.basename(module))
            inittag = False
            for modulefolder in module_folder_list:
                if not os.path.exists(os.path.join(modulefolder, module)):
                    continue

                for line_iso in open(
                    os.path.abspath(os.path.join(modulefolder, module)), encoding="ISO-8859-15"
                ):
                    line_unicode = line_iso
                    line = line_unicode
                    if line.find("<MODULE>") != -1:
                        inittag = True
                    if inittag:
                        modlines.append(line)
                    if line.find("</MODULE>") != -1:
                        inittag = False
                break

        data = """<!DOCTYPE modules_def>
        <modules>
        %s
        </modules>""" % "".join(
            modlines
        )
        return data.encode("utf-8")

    def filesDef(self, module_folder_list: List) -> bytes:
        """Retrun files definitions."""
        list_modules: List[str] = []
        filelines: List[str] = []
        shasum = ""
        load_ext = set([".qs", ".mtd", ".ts", ".ar", ".kut", ".qry", ".ui", ".xml", ".xpm", ".py"])

        for folder, module in zip(self._file_folders, self._modnames):
            fpath = ""
            for modulefolder in module_folder_list:
                if not os.path.exists(modulefolder):
                    continue

                fpath = os.path.join(modulefolder, folder)

                if not os.path.exists(fpath):
                    continue

                break

            files = self._find_files(fpath)
            module_name: Any = re.search(r"^\w+", module)
            module_name = module_name.group(0) if module_name else ""
            if module_name in list_modules:
                self._addLog("módulo %s (%s) Duplicado. Ignorado." % (module_name, fpath))
                continue

            self._addLog("%s -> %s" % (fpath, module_name))
            list_modules.append(module_name)

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
        <skip>false</skip>
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

    def pack(self, module_folder: str, emulate=False) -> bool:
        """Add files to package."""

        module_folder_list = module_folder.split(",")

        current_list = list(module_folder_list)
        module_folder_list = []

        for current_folder in current_list:
            if current_folder.endswith(("/", "\\")):
                current_folder = current_folder[:-1]

            module_folder_list.append(current_folder)
        self._addLog("Creando paquete de módulos de %s . . ." % ", ".join(module_folder_list))
        outputfile = module_folder_list[0] + ".eneboopkg"
        if self._dest_file:
            outputfile = self._dest_file

        modules_def = self.modulesDef(module_folder_list)
        files_def = self.filesDef(module_folder_list)

        file_ = QtCore.QFile(QtCore.QDir.cleanPath(outputfile))
        if not file_.open(QtCore.QIODevice.OpenModeFlag.WriteOnly):
            error = "Error opening file %r" % outputfile
            self._addError("pack", error)
            raise Exception(error)

        stream = QtCore.QDataStream(file_)
        if emulate:
            package_name = "Pineboo %s " % PINEBOO_VER
        else:
            package_name = "AbanQ Packager (Pineboo %s)" % PINEBOO_VER

        stream.writeBytes(package_name.encode())
        stream.writeBytes(b"")
        stream.writeBytes(b"")
        stream.writeBytes(b"")
        stream.writeBytes(QtCore.qCompress(modules_def).data())  # type: ignore [call-overload]
        stream.writeBytes(QtCore.qCompress(files_def).data())  # type: ignore [call-overload]
        # FILE CONTENTS
        try:
            for filepath in self._file_list:
                sys.stdout.write(".")
                sys.stdout.flush()
                stream.writeBytes(QtCore.qCompress(open(filepath, "rb").read()).data())  # type: ignore [call-overload]

        except Exception as exception:
            self._addError("pack (add files)", str(exception))

            return False

        file_modules_def = open("%s/modules.def" % os.path.dirname(outputfile), "bw")
        file_modules_def.write(modules_def)
        file_modules_def.close()

        file_files_def = open("%s/files.def" % os.path.dirname(outputfile), "bw")
        file_files_def.write(files_def)
        file_files_def.close()

        sys.stdout.write("\n")
        sys.stdout.flush()
        self._addLog(
            "Paquete %s creado. Extensiones ignoradas: [%s] "
            % (outputfile, ", ".join(self._ignored_ext))
        )
        return True

    @decorators.not_implemented_warn
    def unpack(self, folder: str) -> bool:
        """Extract files from package."""
        return False

    @decorators.not_implemented_warn
    def output(self) -> str:
        """Return output messages."""

        return self._output

    def outputPackage(self) -> str:
        """Return outptPackage."""

        return self._dest_file

    @decorators.not_implemented_warn
    def setEncodeUtf8(self, enconde_bool: bool = True) -> None:
        """Encode data with Utf8 charset."""

        self._encode_utf8 = enconde_bool

    @decorators.not_implemented_warn
    def setFilter(self, filter: str = "") -> None:
        """Set a filter."""

        self._filter = filter

    def filter(self) -> str:
        """Return filter."""

        return self._filter

    def _addLog(self, message: str) -> None:
        """Add message to log."""
        self._log_messages.append(message)
        print(message)

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
