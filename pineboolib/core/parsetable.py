"""Module for parseTable function."""
from .utils import logging
from .utils.get_table_obj import get_table_object
from .utils.struct import TableStruct

from io import StringIO
from xml.etree import ElementTree as ET

LOGGER = logging.get_logger(__name__)


def parse_table(nombre: str, contenido: str) -> TableStruct:
    """Parse MTD and convert to table object."""

    file_alike = StringIO(contenido)
    try:
        tree = ET.parse(file_alike)
    except Exception:
        LOGGER.exception("Error al procesar tabla: %s", nombre)
        raise

    root = tree.getroot()
    obj_name = root.find("name")
    query = root.find("query")
    if query:
        if query.text != nombre:
            LOGGER.warning(
                "WARN: Nombre de query %s no coincide con el nombre declarado en el XML %s (se prioriza el nombre de query)"
                % (query.text, nombre)
            )
            query.text = nombre
    elif obj_name and obj_name.text != nombre:
        LOGGER.warning(
            "WARN: Nombre de tabla %s no coincide con el nombre declarado en el XML %s (se prioriza el nombre de tabla)"
            % (obj_name.text, nombre)
        )
        obj_name.text = nombre
    return get_table_object(tree, root)
