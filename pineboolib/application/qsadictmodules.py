"""
QSADictModules.

Manages read and writting QSA dynamic properties that are loaded during project startup.
"""


from . import xmlaction, proxy, safeqsa
from pineboolib import logging, application

import sqlalchemy
import gc

from typing import Any, Optional, Union, TYPE_CHECKING

LOGGER = logging.get_logger(__name__)

if TYPE_CHECKING:
    from pineboolib.application.database.orm import basemodel


class QSADictModules:
    """
    Manage read and write dynamic properties for QSA.
    """

    _qsa_dict_modules = None

    @classmethod
    def qsa_dict_modules(cls) -> Any:
        """Retrieve QSA module, hidding it from MyPy."""
        if cls._qsa_dict_modules is None:
            if TYPE_CHECKING:
                qsa_dict_modules_tree: Any = None  # pragma: no cover
            else:
                from . import modules_tree as qsa_dict_modules_tree

            cls._qsa_dict_modules = qsa_dict_modules_tree
        return cls._qsa_dict_modules

    @classmethod
    def from_project(cls, script_name: str) -> Any:
        """
        Return project object for given name.
        """
        module_name = "sys_module" if script_name == "sys" else script_name

        ret_ = getattr(cls.qsa_dict_modules(), module_name, None)
        if ret_ is None and not module_name.endswith("orm"):
            LOGGER.warning("Module %s not found!", module_name)

        return ret_

    @classmethod
    def orm_(cls, action_name: str = "") -> Any:
        """Return orm instance."""

        table_name = (
            application.PROJECT.actions[action_name]._table
            if action_name in application.PROJECT.actions.keys()
            else action_name
        )

        if table_name:
            orm = cls.from_project("%s_orm" % (table_name))
            if orm is not None:
                init_fn = getattr(orm, "_qsa_init", None)
                if init_fn:
                    sqlalchemy.event.listen(orm, "init", init_fn)

                return orm
            else:
                LOGGER.error("Model %s not found!", table_name, stack_info=True)

        return None

    @classmethod
    def action_exists(cls, scriptname: str) -> bool:
        """
        Check if action is already loaded.
        """
        return hasattr(cls.qsa_dict_modules(), scriptname)

    @classmethod
    def set_qsa_tree(
        cls,
        script_name: str,
        action_or_model: Optional[Union["proxy.DelayedObjectProxyLoader", "basemodel.BaseModel"]],
    ) -> None:
        """
        Save action or other objects for QSA.
        """
        setattr(cls.qsa_dict_modules(), script_name, action_or_model)

    @classmethod
    def save_action_for_root_module(cls, action: "xmlaction.XMLAction") -> bool:
        """Save a new module as an action."""

        module_name = action._name if action._name != "sys" else "sys_module"
        if cls.action_exists(module_name):
            if module_name != "sys_module":
                LOGGER.info("Module found twice, will not be overriden: %s", module_name)
            return False

        # Se crea la action del módulo
        delayed_action = proxy.DelayedObjectProxyLoader(
            action.load_master_widget, name="QSA.Module.%s" % module_name
        )
        cls.set_qsa_tree(module_name, delayed_action)
        safeqsa.SafeQSA.save_root_module(module_name, delayed_action)
        return True

    @classmethod
    def save_action_for_mainform(cls, action: "xmlaction.XMLAction"):
        """Save a new mainform."""

        name = action._name
        module = action._mod
        if module is None:
            raise ValueError("Action.module must be set before calling")

        actionname = "form%s" % name
        if cls.action_exists(actionname):
            LOGGER.info(
                "No se sobreescribe variable de entorno %s. Hay una definición previa.",
                "%s.form%s" % (module.module_name, name),
            )
            return False
        # Se crea la action del form
        delayed_action = proxy.DelayedObjectProxyLoader(
            action.load_master_widget, name="QSA.Module.%s.Action.form%s" % (module.mod.name, name)
        )
        cls.set_qsa_tree(actionname, delayed_action)
        safeqsa.SafeQSA.save_mainform(actionname, delayed_action)
        return True

    @classmethod
    def save_action_for_formrecord(cls, action: "xmlaction.XMLAction"):
        """Save a new formrecord."""
        name = action._name
        module = action._mod
        if module is None:
            raise ValueError("Action.module must be set before calling")
        actionname = "formRecord" + name
        if cls.action_exists(actionname):
            LOGGER.info(
                "No se sobreescribe variable de entorno %s. Hay una definición previa.",
                "%s.formRecord%s" % (module.module_name, name),
            )
            return False
        # Se crea la action del formRecord
        delayed_action = proxy.DelayedObjectProxyLoader(
            action.load_record_widget,
            name="QSA.Module.%s.Action.formRecord%s" % (module.mod.name, name),
        )

        cls.set_qsa_tree(actionname, delayed_action)
        safeqsa.SafeQSA.save_formrecord(actionname, delayed_action)
        return True

    @classmethod
    def save_action_for_class(cls, action: "xmlaction.XMLAction"):
        """Save action class action."""

        class_name = action._class_script
        module = action._mod
        if module is None:
            raise ValueError("Action.module must be set before calling")

        if class_name:
            if cls.action_exists(class_name):
                LOGGER.info(
                    "No se sobreescribe variable de entorno %s. Hay una definición previa.",
                    "%s.%s" % (module.module_name, class_name),
                )
                return False

            delayed_action = proxy.DelayedObjectProxyLoader(
                action.load_class,
                name="QSA.Module.%s.Action.class_%s" % (module.mod.name, class_name),
            )
            cls.set_qsa_tree(action._name, delayed_action)

    @classmethod
    def clean_all(cls):
        """Clean all saved data."""
        qsa_dict_modules = cls.qsa_dict_modules()

        safeqsa.SafeQSA.clean_all()
        for name in [attr for attr in dir(qsa_dict_modules) if not attr[0] == "_"]:
            att = getattr(qsa_dict_modules, name)
            if isinstance(att, proxy.DelayedObjectProxyLoader) or (
                name.endswith(("_orm", "_class"))
                and (not name.startswith("fl") and name not in ("flusers", "flgroups"))
            ):
                delattr(qsa_dict_modules, name)

        gc.collect()


from_project = QSADictModules.from_project
orm_ = QSADictModules.orm_
