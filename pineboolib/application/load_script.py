"""Load_script module."""

from pineboolib.core.utils import logging
from .utils.path import _path, coalesce_path


from typing import Optional, Any
from pineboolib.core.utils.struct import ActionStruct

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

    python_script_path = None

    from pineboolib.qsa import emptyscript  # type: ignore

    script_loaded: Any = emptyscript

    script_path_py: Optional[str] = None
    if scriptname is not None:

        from importlib import machinery

        if project.alternative_folder:
            import glob

            for file_name in glob.iglob(
                "%s/legacy/**/%s" % (project.alternative_folder, scriptname), recursive=True
            ):
                if file_name.endswith(scriptname):
                    script_path_py = file_name
                    break

        if script_path_py is None:
            script_path_qs = _path("%s.qs" % scriptname, False)
            script_path_py = coalesce_path("%s.py" % scriptname, "%s.qs.py" % scriptname, None)

        mng_modules = project.conn.managerModules()
        if mng_modules.staticBdInfo_ and mng_modules.staticBdInfo_.enabled_:
            from pineboolib.application.staticloader.pnmodulesstaticloader import PNStaticLoader

            ret_py = PNStaticLoader.content(
                "%s.qs.py" % scriptname, mng_modules.staticBdInfo_, True
            )  # Con True solo devuelve el path
            if ret_py:
                script_path_py = ret_py
            else:
                ret_qs = PNStaticLoader.content(
                    "%s.qs" % scriptname, mng_modules.staticBdInfo_, True
                )  # Con True solo devuelve el path
                if ret_qs:
                    script_path_qs = ret_qs

        if script_path_py is not None:
            script_path = script_path_py
            logger.info("Loading script PY %s . . . ", scriptname)
            if not os.path.isfile(script_path):
                raise IOError
            try:
                logger.debug(
                    "Cargando %s : %s ", scriptname, script_path.replace(project.tmpdir, "tempdata")
                )
                loader = machinery.SourceFileLoader(scriptname, script_path)
                script_loaded = loader.load_module()  # type: ignore
            except Exception:
                logger.exception("ERROR al cargar script PY para la accion %s:", action_.name)

        elif script_path_qs:
            script_path_py = "%s.py" % script_path_qs
            if not os.path.exists(script_path_py):
                project.parse_script_list([script_path_qs])

            logger.info("Loading script QS %s . . . ", scriptname)
            python_script_path = "%s.py" % script_path_qs
            try:
                logger.debug(
                    "Cargando %s : %s ",
                    scriptname,
                    python_script_path.replace(project.tmpdir, "tempdata"),
                )
                loader = machinery.SourceFileLoader(scriptname, python_script_path)
                script_loaded = loader.load_module()  # type: ignore
            except Exception:
                logger.exception("ERROR al cargar script QS para la accion %s:", action_.name)
                if os.path.exists(script_path_py):
                    os.remove(script_path_py)

    script_loaded.form = script_loaded.FormInternalObj(action_)

    return script_loaded
