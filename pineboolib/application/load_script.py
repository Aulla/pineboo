"""Load_script module."""

from pineboolib.core.utils import logging
from .utils.path import _path


from typing import Optional, Any
from pineboolib.core.utils.struct import ActionStruct
import shutil
import os

logger = logging.getLogger("load_script")


def load_script(scriptname: Optional[str], action_: ActionStruct) -> Any:  # returns loaded script
    """
    Transform QS script into Python and starts it up.

    @param scriptname. Nombre del script a convertir
    @param parent. Objecto al que carga el script, si no se especifica es a self.script
    """

    from pineboolib import application

    project = application.project

    if scriptname:
        scriptname = scriptname.replace(".qs", "")
        logger.debug("Loading script %s for action %s", scriptname, action_.name)
    else:
        logger.info("No script to load for action %s", action_.name)

    from pineboolib.qsa import emptyscript  # type: ignore

    script_loaded: Any = emptyscript

    script_path_py: Optional[str] = None
    script_path_py_static: Optional[str] = None
    script_path_qs: Optional[str] = None
    script_path_qs_static: Optional[str] = None

    if scriptname is not None:

        from importlib import machinery

        # if project.alternative_folder:
        #    import glob

        #    for file_name in glob.iglob(
        #        "%s/legacy/**/%s" % (project.alternative_folder, scriptname), recursive=True
        #    ):
        #        if file_name.endswith(scriptname):
        #            script_path_py = file_name
        #            break

        script_path_qs = _path("%s.qs" % scriptname, False)
        script_path_py = _path("%s.py" % scriptname, False)

        mng_modules = project.conn.managerModules()
        if mng_modules.staticBdInfo_ and mng_modules.staticBdInfo_.enabled_:
            from pineboolib.application.staticloader.pnmodulesstaticloader import PNStaticLoader

            script_path_py_static = PNStaticLoader.content(
                "%s.py" % scriptname, mng_modules.staticBdInfo_, True
            )  # Con True solo devuelve el path

            if script_path_py_static is None:
                script_path_qs_static = PNStaticLoader.content(
                    "%s.qs" % scriptname, mng_modules.staticBdInfo_, True
                )  # Con True solo devuelve el path

        if script_path_py is not None or script_path_py_static:
            if script_path_py_static:
                script_path_py = script_path_py_static

            logger.info("Loading script PY %s . . . ", scriptname)
            if not os.path.isfile(script_path_py):
                raise IOError
            try:
                loader = machinery.SourceFileLoader(scriptname, script_path_py)
                script_loaded = loader.load_module()  # type: ignore
            except Exception:
                logger.exception("ERROR al cargar script PY para la accion %s:", action_.name)

        elif script_path_qs:
            script_path_py = "%s.py" % script_path_qs[:-3]
            folder_path = os.path.dirname(script_path_qs)
            static_flag = "%s/STATIC" % folder_path
            if script_path_qs_static:
                # Recogemos el .qs de carga estática.
                shutil.copy(script_path_qs_static, script_path_qs)  # Lo copiamos en tempdata
                if script_path_py and os.path.exists(
                    script_path_py
                ):  # Si existe el py en tempdata se elimina
                    os.remove(script_path_py)

                if not os.path.exists(static_flag):  # Marcamos que se ha hecho carga estática.
                    f = open(static_flag, "w")
                    f.write(".")
                    f.close()

            if not os.path.exists(script_path_py):
                project.parse_script_list([script_path_qs])

            logger.info("Loading script QS %s . . . ", scriptname)
            # python_script_path = "%s.py" % script_path_qs[:-3]
            try:
                loader = machinery.SourceFileLoader(scriptname, script_path_py)
                script_loaded = loader.load_module()  # type: ignore
            except Exception:
                logger.exception("ERROR al cargar script QS para la accion %s:", action_.name)
                if os.path.exists(script_path_py):
                    os.remove(script_path_py)

    script_loaded.form = script_loaded.FormInternalObj(action_)

    return script_loaded
