"""
ModuleActions module.
"""

from pineboolib.core import exceptions
from pineboolib.core.utils import utils_base, logging
from pineboolib.application import xmlaction
from pineboolib import application

from typing import Any, TYPE_CHECKING, NoReturn

LOGGER = logging.getLogger(__name__)


class ModuleActions(object):
    """
    Generate tree with actions from modules.
    """

    def __init__(self, module: Any, path: str, modulename: str) -> None:
        """
        Constructor.

        @param module. Identificador del módulo
        @param path. Ruta del módulo
        @param modulename. Nombre del módulo
        """
        if TYPE_CHECKING:
            # To avoid circular dependency on pytype
            self.project = module
        else:
            self.project = application.PROJECT

        self.mod = module  # application.Module
        self.path = path
        self.module_name = modulename
        if not self.path:
            LOGGER.error("El módulo no tiene un path válido %s", self.module_name)

    def load(self) -> None:
        """Load module actions into project."""
        # Ojo: Almacena un arbol con los módulos cargados
        from pineboolib.application.qsadictmodules import QSADictModules

        tree = utils_base.load2xml(self.path)
        self.root = tree.getroot()

        action = xmlaction.XMLAction(project=self.project, name=self.mod.name)
        if action is None:
            raise Exception("action is empty!")

        action.mod = self
        action.alias = self.mod.name
        # action.form = self.mod.name
        action.form = None
        action.table = None
        action.scriptform = self.mod.name
        self.project.actions[
            action.name
        ] = action  # FIXME: Actions should be loaded to their parent, not the singleton
        QSADictModules.save_action_for_root_module(action)

        for xmlaction_item in self.root:
            action_xml = xmlaction.XMLAction(xmlaction_item, project=self.project)
            action_xml.mod = self
            name = action_xml.name
            if not name or name == "unnamed":
                continue

            if QSADictModules.save_action_for_mainform(action_xml):

                self.project.actions[
                    name
                ] = action_xml  # FIXME: Actions should be loaded to their parent, not the singleton

            QSADictModules.save_action_for_formrecord(action_xml)

    def __contains__(self, k) -> bool:
        """Determine if it is the owner of an action."""
        return (
            k in self.project.actions
        )  # FIXME: Actions should be loaded to their parent, not the singleton

    def __getitem__(self, name) -> Any:
        """
        Retrieve particular action by name.

        @param name. Nombre de la action
        @return Retorna el XMLAction de la action dada
        """
        return self.project.actions[
            name
        ]  # FIXME: Actions should be loaded to their parent, not the singleton

    def __setitem__(self, name, action_) -> NoReturn:
        """
        Add action to a module property.

        @param name. Nombre de la action
        @param action_. Action a añadir a la propiedad del módulo
        """
        raise exceptions.ForbiddenError("Actions are not writable!")
        # self.project.actions[name] = action_
