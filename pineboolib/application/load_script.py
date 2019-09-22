"""Load_script module."""

from pineboolib.core.utils import logging
from .utils.path import _path, coalesce_path


from typing import Optional, Any
from pineboolib.core.utils.struct import ActionStruct

import os

logger = logging.getLogger("load_script")


def load_script(script_name: Optional[str], action_: ActionStruct) -> Any:  # returns loaded script
    """
    Transform QS script into Python and starts it up.

    @param script_name. Nombre del script a convertir
    @param parent. Objecto al que carga el script, si no se especifica es a self.script
    """

    from pineboolib import application

    project = application.project

    if script_name:
        script_name = script_name.replace(".qs", "")
        logger.debug("Loading script %s for action %s", script_name, action_.name)
    else:
        logger.info("No script to load for action %s", action_.name)

    script_loaded: Any = None
    script_path_py: Optional[str] = None
    if script_name is not None:

        from importlib import machinery

        if project.alternative_folder_:
            import glob

            for file_name in glob.iglob(
                "%s/legacy/**/%s" % (project.alternative_folder_, script_name), recursive=True
            ):
                if file_name.endswith(script_name):
                    script_path_py = file_name
                    break

        if script_path_py is None:
            script_path_qs = _path("%s.qs" % script_name, False)
            script_path_py = coalesce_path("%s.py" % script_name, "%s.qs.py" % script_name, None)

        mng_modules = project.conn.managerModules()
        if mng_modules.staticBdInfo_ and mng_modules.staticBdInfo_.enabled_:
            from pineboolib.fllegacy.flmodulesstaticloader import FLStaticLoader  # FIXME

            ret_py = FLStaticLoader.content(
                "%s.qs.py" % script_name, mng_modules.staticBdInfo_, True
            )  # Con True solo devuelve el path
            if ret_py:
                script_path_py = ret_py
            else:
                ret_qs = FLStaticLoader.content(
                    "%s.qs" % script_name, mng_modules.staticBdInfo_, True
                )  # Con True solo devuelve el path
                if ret_qs:
                    script_path_qs = ret_qs

        if script_path_py is not None:  # Si hay .py se carga
            script_path = script_path_py
            logger.info("Loading script PY %s . . . ", script_name)
            if not os.path.isfile(script_path):
                raise IOError
            try:
                logger.debug(
                    "Cargando %s : %s ",
                    script_name,
                    script_path.replace(project.tmpdir, "tempdata"),
                )
                loader = machinery.SourceFileLoader(script_name, script_path)
                script_loaded = loader.load_module()  # type: ignore
            except Exception:
                logger.exception("ERROR al cargar script PY para la accion %s:", action_.name)

        elif script_path_qs is not None:  # Si no hay .py , pero si hay .qs se carga
            script_path_py = "%s.py" % script_path_qs
            if not os.path.exists(script_path_py):
                project.parse_script_list([script_path_qs])

            logger.info("Loading script QS %s . . . ", script_name)
            python_script_path: str = "%s.py" % script_path_qs
            try:
                logger.debug(
                    "Cargando %s : %s ",
                    script_name,
                    python_script_path.replace(project.tmpdir, "tempdata"),
                )
                loader = machinery.SourceFileLoader(script_name, python_script_path)
                script_loaded = loader.load_module()  # type: ignore
            except Exception:
                logger.exception("ERROR al cargar script QS para la accion %s:", action_.name)
                if os.path.exists(script_path_py):
                    os.remove(script_path_py)
    else:
        from pineboolib.qsa import emptyscript  # type: ignore

        script_loaded = emptyscript

    script_loaded.form = script_loaded.FormInternalObj(action_)

    return script_loaded
