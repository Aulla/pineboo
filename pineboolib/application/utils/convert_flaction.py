"""Converter to and from action_."""

from pineboolib.core.utils import logging

from typing import Union, cast, TYPE_CHECKING
from pineboolib import application
from pineboolib.application.metadata import pnaction

if TYPE_CHECKING:
    from pineboolib.application import xmlaction  # pragma: no cover


LOGGER = logging.get_logger(__name__)


def convert_from_flaction(action: "pnaction.PNAction") -> "xmlaction.XMLAction":
    """
    Convert a PNAction to XMLAction.

    @param action. action_ object.
    @return XMLAction object.
    """

    if action.name() not in application.PROJECT.actions.keys():
        raise KeyError("Action %s not loaded in current project" % action.name())
    return cast("xmlaction.XMLAction", application.PROJECT.actions[action.name()])


def convert_to_flaction(action: Union[str, "xmlaction.XMLAction"]) -> "pnaction.PNAction":
    """
    Convert a XMLAction to action_.

    @param action. XMLAction object.
    @return PNAction object.
    """

    action_name = action if isinstance(action, str) else action._name

    if application.PROJECT.conn_manager is None:
        raise Exception("Project is not connected yet")

    # LOGGER.trace("convert2action: Load action from db manager")

    cached_actions = application.PROJECT.conn_manager.manager()._cache_action
    if action_name in cached_actions.keys():
        return cached_actions[action_name]
    else:
        action_: "pnaction.PNAction" = pnaction.PNAction(action_name)
        if action_name in application.PROJECT.actions.keys():
            xml_action = application.PROJECT.actions[action_name]
            action_.setName(xml_action._name)
            action_.setTable(xml_action._table)
            action_.setForm(xml_action._master_form)
            action_.setFormRecord(xml_action._record_form)
            action_.setScriptForm(xml_action._master_script)
            action_.setScriptFormRecord(xml_action._record_script)
            action_.setDescription(xml_action._description)
            action_.setCaption(xml_action._alias or xml_action._caption)
            action_.setClass_(xml_action._class_script)

        cached_actions[action_name] = action_
        # LOGGER.trace("convert2FLAction: done")

    return action_
