"""
ModuleActions module.
"""

from pineboolib.core import exceptions
from pineboolib.core.utils import utils_base
from . import xmlaction
from pineboolib import application, logging

from typing import Any, TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from . import module
    from . import projectmodule

LOGGER = logging.get_logger(__name__)


class ModuleActions(object):
    """
    Generate tree with actions from modules.
    """

    module_name: str
    path: str
    mod: "module.Module"
    project: "projectmodule.Project"

    def __init__(self, module_: "module.Module", path: str, modulename: str) -> None:
        """
        Initialize.

        @param module. Identificador del módulo
        @param path. Ruta del módulo
        @param modulename. Nombre del módulo
        """

        self.project = (
            module_  # type: ignore [assignment] # noqa: F821
            if TYPE_CHECKING
            else application.PROJECT
        )

        self.mod = module_
        self.path = path
        self.module_name = modulename
        if not self.path:
            LOGGER.error("El módulo no tiene un path válido %s", self.module_name)

    def load(self) -> None:
        """Load module actions into project."""
        # Ojo: Almacena un arbol con los módulos cargados
        from .qsadictmodules import QSADictModules

        tree = utils_base.load2xml(self.path)
        self.root = tree.getroot()

        action = xmlaction.XMLAction(self, self.mod.name)
        if action is None:
            raise Exception("action is empty!")

        # action._mod = self
        # action.alias = self.mod.name
        # action.form = self.mod.name
        # action._form = None
        # action.table = None
        # action.scriptform = self.mod.name
        self.project.actions[
            action._name
        ] = action  # FIXME: Actions should be loaded to their parent, not the singleton
        QSADictModules.save_action_for_root_module(action)

        for xmlaction_item in self.root:
            action_xml = xmlaction.XMLAction(self, xmlaction_item)
            name = action_xml._name
            if name in ("unnamed", ""):
                continue

            if QSADictModules.save_action_for_mainform(action_xml):
                self.project.actions[
                    name
                ] = action_xml  # FIXME: Actions should be loaded to their parent, not the singleton
            QSADictModules.save_action_for_formrecord(action_xml)
            QSADictModules.save_action_for_class(action_xml)

        if [
            file_.name
            for file_ in self.project.files.values()
            if file_.name.startswith("plus_sys") and file_.module == self.module_name
        ]:
            action_xml_plus = xmlaction.XMLAction(self, "plus_sys")
            if QSADictModules.save_action_for_mainform(action_xml_plus):
                LOGGER.warning("plus_sys loaded!")
                self.project.actions["plus_sys"] = action_xml_plus

    def __contains__(self, name: str) -> bool:
        """Determine if it is the owner of an action."""
        return (
            name in self.project.actions
        )  # FIXME: Actions should be loaded to their parent, not the singleton

    def __getitem__(self, name: str) -> Any:
        """
        Retrieve particular action by name.

        @param name. Nombre de la action
        @return Retorna el XMLAction de la action dada
        """
        return self.project.actions[
            name
        ]  # FIXME: Actions should be loaded to their parent, not the singleton

    def __setitem__(self, name: str, action_: "xmlaction.XMLAction") -> "NoReturn":
        """
        Add action to a module property.

        @param name. Nombre de la action
        @param action_. Action a añadir a la propiedad del módulo
        """
        raise exceptions.ForbiddenError("Actions are not writable!")
        # self.project.actions[name] = action_
