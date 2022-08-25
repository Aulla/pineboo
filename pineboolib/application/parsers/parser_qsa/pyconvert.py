"""
PyConvert module.

Converts QS projects into Python packages that can be parsed with MyPy
"""
import sys
import os
import os.path
import codecs

import multiprocessing
from typing import List, Tuple, TypeVar, cast, Dict, Optional
from xml import etree
from pineboolib import logging
from pineboolib.core.utils import struct
from . import postparse, pytnyzer, USE_THREADS

LOGGER = logging.get_logger(__name__)


class Action(struct.ActionStruct):
    """Represent actions from XML."""

    modname: str = ""


ModPath = TypeVar("ModPath", bound=str)
ModName = TypeVar("ModName", bound=str)
ModList = List[Tuple[ModPath, ModName]]

CPU_COUNT: int = os.cpu_count() or 1


def _touch(path: str) -> bool:
    """Create a file if does not exist."""
    if not os.path.exists(path):
        LOGGER.info("Creating empty file %r", path)
        open(path, "a").close()
        return True
    return False


def _touch_dir(path: str) -> bool:
    """Create a folder if does not exist."""
    if not os.path.exists(path):
        LOGGER.info("Creating folder %r", path)
        os.mkdir(path)
        return True
    return False


def get_modules(from_path: str = ".") -> ModList:
    """Read folders ignoring anything suspiciuos."""
    rootdir: str = os.path.abspath(from_path)
    module_files: ModList = []
    for root, sub_folders, files in os.walk(rootdir):
        for number, subf in reversed(list(enumerate(sub_folders))):
            if subf[0] < "a" or subf[0] > "z":
                del sub_folders[number]
        root = root.replace(rootdir, "")
        if root.startswith("/"):
            root = root[1:]
        # qs_files = [fname for fname in files if fname.endswith(".qs")]
        modlist = [(root, fname.replace(".mod", "")) for fname in files if fname.endswith(".mod")]
        module_files += cast(ModList, modlist)
    return module_files


def mod_xml_parse(path: str, mod_name: str) -> Optional[Dict[str, Action]]:
    """Parse Module XML and retrieve actions."""
    try:
        tree = etree.ElementTree.parse(source=codecs.open(path, "r", encoding="iso-8859-15"))
    except Exception:
        LOGGER.exception("Error trying to parse %r", path)
        return None
    root = tree.getroot()
    actions: Dict[str, Action] = {}
    for xmlaction in root:
        action = Action(xmlaction)
        action.modname = mod_name
        if action._name in actions:
            LOGGER.warning(
                "Found duplicate action in %r for %r. Will override.", path, action._name
            )
        actions[action._name] = action
    return actions


class PythonifyItem(object):
    """Give multiprocessing something to pickle."""

    src_path: str = ""
    dst_path: str = ""
    number: int = 0
    len: int = 1
    known: Dict[str, Tuple[str, str]] = {}

    def __init__(
        self, src: str, dst: str, number: int, len: int, known: Dict[str, Tuple[str, str]]
    ):
        """Create object just from args."""
        self.src_path = src
        self.dst_path = dst
        self.number = number
        self.len = len
        self.known = known


def pythonify_item(item: PythonifyItem) -> bool:
    """Parse QS into Python. For multiprocessing.map."""
    if USE_THREADS:
        LOGGER.info("(%.2f%%) Parsing QS %r", 100 * item.number / item.len, item.src_path)
    try:
        pycode = postparse.pythonify2(item.src_path, known_refs=item.known)
    except Exception:
        LOGGER.exception("El fichero %s no se ha podido convertir", item.src_path)
        return False

    file_ = codecs.open(item.dst_path, "w", encoding="UTF-8")
    file_.write(pycode)
    file_.close()

    if not os.path.exists(item.dst_path):
        LOGGER.error("The file %s was generated but doesn't exists!", item.dst_path)
        return False

    return True


def main() -> None:
    """Get options and start conversion."""
    filter_mod = sys.argv[1] if len(sys.argv) > 1 else None
    filter_file = sys.argv[2] if len(sys.argv) > 2 else None

    pytnyzer.STRICT_MODE = False
    log_format = "%(levelname)s: %(name)s: %(message)s"
    logging.basicConfig(format=log_format, level=0)
    blib_logger = logging.get_logger("blib2to3.pgen2.driver")
    blib_logger.setLevel(logging.WARNING)
    LOGGER.info("Cpu count %d", CPU_COUNT)
    source_folder = "."
    package_name = "pymodules"
    src_path = os.path.abspath(source_folder)
    dst_path = os.path.abspath(os.path.join(src_path, package_name))
    # Step 1 - Create base package path
    _touch_dir(dst_path)
    _touch(os.path.join(dst_path, "__init__.py"))
    mypy_ini = os.path.join(src_path, "mypy.ini")
    if not os.path.exists(mypy_ini):
        with open(mypy_ini, "w", encoding="UTF-8") as file_:
            file_.write("[mypy]\n")
            file_.write("python_version = 3.7\n")
            file_.write("check_untyped_defs = True\n")

    # Step 2 - Create module folders
    module_files_in: ModList = get_modules(src_path)
    known_modules: Dict[str, Tuple[str, str]] = {}
    module_files_ok: ModList = []
    for mpath, mname in module_files_in:
        xml_name = os.path.join(mpath, "%s.xml" % mname)
        if not os.path.exists(os.path.join(src_path, xml_name)):
            LOGGER.warning("File not found %r. Ignoring module." % xml_name)
            continue
        if os.sep in mpath:
            mpath_list = mpath.split(os.sep)
            if len(mpath_list) > 2:
                LOGGER.warning("Path %r is not supported, maximum is depth 2" % mpath)
                continue
            mpath_parent = mpath_list[0]
            _touch_dir(os.path.join(dst_path, mpath_parent))
            _touch(os.path.join(dst_path, mpath_parent, "__init__.py"))

        _touch_dir(os.path.join(dst_path, mpath))
        _touch(os.path.join(dst_path, mpath, "__init__.py"))
        known_modules[mname] = (package_name + "." + mpath.replace(os.sep, "."), mname)
        module_files_ok.append((mpath, mname))

    # Step 3 - Read module XML and identify objects
    for mpath, mname in module_files_ok:
        xml_name = os.path.join(mpath, "%s.xml" % mname)
        actions = mod_xml_parse(os.path.join(src_path, xml_name), mname)
        if actions is None:
            continue
        for action in actions.values():
            if action._master_script:
                module_pubname = "form%s" % action._name
                known_modules[module_pubname] = (
                    package_name + "." + mpath.replace(os.sep, "."),
                    action._master_script,
                )
            if action._record_script:
                module_pubname = "formRecord%s" % action._name
                known_modules[module_pubname] = (
                    package_name + "." + mpath.replace(os.sep, "."),
                    action._record_script,
                )

    if filter_mod is not None:
        for alias, (path, name) in known_modules.items():
            if filter_mod not in path and filter_mod not in name:
                continue
            LOGGER.debug("from %s import %s as %s", path, name, alias)

    # Step 4 - Retrieve QS file list for conversion
    LOGGER.info("Retrieving QS File list...")
    qs_files: List[Tuple[str, str]] = []
    for mpath, mname in module_files_ok:
        if filter_mod is not None and filter_mod not in mpath and filter_mod not in mname:
            continue
        rootdir = os.path.join(src_path, mpath)
        for root, sub_folders, files in os.walk(rootdir):

            def get_fname_pair(fname: str) -> Tuple[str, str]:
                src_filename = os.path.join(root, fname)
                dst_filename = os.path.join(dst_path, mpath, fname.replace(".qs", ".py"))
                return src_filename, dst_filename

            if filter_file is not None:
                files = [fname for fname in files if filter_file in fname]
            qs_files += [get_fname_pair(fname) for fname in files if fname.endswith(".qs")]

    # Step 5 - Convert QS into Python
    LOGGER.info("Converting %d QS files...", len(qs_files))

    itemlist = [
        PythonifyItem(src=src, dst=dst, number=number, len=len(qs_files), known=known_modules)
        for number, (src, dst) in enumerate(qs_files)
    ]

    pycode_list: List[bool] = []

    if USE_THREADS:
        with multiprocessing.Pool(CPU_COUNT) as cpu:
            # TODO: Add proper signatures to Python files to avoid reparsing
            pycode_list = cpu.map(pythonify_item, itemlist, chunksize=2)
    else:
        for item in itemlist:
            pycode_list.append(pythonify_item(item))

    if not all(pycode_list):
        raise Exception("Conversion failed for some files")
