# -*- coding: utf-8 -*-
"""
Utilities for more descriptive errors.

This module contains a set of functions aimed to reduce the amount of verbosity
so error and tracebacks are easy to follow and fit better on GUI
"""

import re
from .utils import logging
from . import exceptions, translate

LOGGER = logging.getLogger(__name__)

RAISE_QSA_ERRORS = False


def error_manager(error_str: str) -> str:
    """Process an error text and return a better version for GUI."""
    from pineboolib.core import settings

    global RAISE_QSA_ERRORS

    tmpdir = settings.CONFIG.value("ebcomportamiento/temp_dir")
    error_str = error_str.replace(tmpdir, "...")
    error_str = re.sub(r"/[0-9a-f]{35,60}\.qs\.py", ".qs.py", error_str)

    text = translate.translate("scripts", "Error ejecutando un script")
    text += ":\n%s" % error_str
    text += process_error(error_str)
    LOGGER.error(text)
    if RAISE_QSA_ERRORS:
        raise exceptions.QSAError("QSA script error detected.")

    return text


def process_error(error_str: str) -> str:
    """Retrieve hints for a given error string."""
    ret = "\n=========== Error Manager =============\n\n"

    if "AttributeError: 'dict' object has no attribute" in error_str:
        error = "AttributeError: 'dict' object has no attribute"
        var = error_str[error_str.find(error) + len(error) + 1 :]
        var = var.replace("\n", "")
        ret += translate.translate("scripts", "La forma correcta de acceder a .%%s es [%%s].") % (
            var,
            var,
        )

    elif "'builtin_function_or_method' object has no attribute" in error_str:
        error = "'builtin_function_or_method' object has no attribute"
        var = error_str[error_str.find(error) + len(error) + 1 :]
        var = var.replace("\n", "")
        var = var.replace("'", "")
        ret += translate.translate("scripts", "La forma correcta de acceder a .%%s es ().%%s.") % (
            var,
            var,
        )

    elif "AttributeError: 'ifaceCtx' object has no attribute" in error_str:
        error = "AttributeError: 'ifaceCtx' object has no attribute"
        var = error_str[error_str.find(error) + len(error) + 1 :]
        var = var.replace("\n", "")
        var = var.replace("'", "")
        ret += translate.translate(
            "scripts", "No se ha traducido el script o el script está vacio."
        )
    elif "object is not callable" in error_str:
        error = "object is not callable"
        var = error_str[error_str.find("TypeError") + 10 : error_str.find(error)]
        ret += (
            translate.translate(
                "scripts",
                "Estas llamando a un objeto %%s .Los parentesis finales hay que quitarlos.",
            )
            % var
        )
    elif "unsupported operand type(s) for" in error_str:
        error = "unsupported operand type(s) for"
        ret += translate.translate(
            "scripts",
            "No puedes hacer operaciones entre dos 'Nones' o dos tipos diferentes. Revisa el script y controla esto.",
        )
    elif "'QDomElement' object has no attribute 'toString'" in error_str:
        error = "'QDomElement' object has no attribute 'toString'"
        ret += translate.translate("scripts", "toString() ya no está disponible , usa otro método")
    elif "can only concatenate" in error_str:
        error = "can only concatenate"
        ret += translate.translate(
            "scripts", "Estas intentado añadir a una cadena de texto un tipo de dato no str."
        )

    else:
        ret += translate.translate("scripts", "Información no disponible.")

    return ret
