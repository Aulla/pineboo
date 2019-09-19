"""Converter to and from action_."""

from pineboolib.core.utils import logging

from typing import Union, cast, TYPE_CHECKING
from pineboolib.application.metadata import pnaction

if TYPE_CHECKING:
    from pineboolib.application.xmlaction import XMLAction


logger = logging.getLogger("application.utils.convert_action_")


def convertFLAction(action: pnaction.PNAction) -> "XMLAction":
    """
    Convert a PNAction to XMLAction.

    @param action. action_ object.
    @return XMLAction object.
    """

    from pineboolib.application import project

    if action.name() not in project.actions.keys():
        raise KeyError("Action %s not loaded in current project" % action.name())
    return cast("XMLAction", project.actions[action.name()])


def convert2FLAction(action: Union[str, "XMLAction"]) -> pnaction.PNAction:
    """
    Convert a XMLAction to action_.

    @param action. XMLAction object.
    @return PNAction object.
    """

    if isinstance(action, str):
        action_name = action
    else:
        action_name = action.name

    from pineboolib.application import project

    if project.conn is None:
        raise Exception("Project is not connected yet")

    logger.trace("convert2action: Load action from db manager")

    action_ = None

    cached_actions = project.conn.manager().cacheAction_
    if action_name in cached_actions.keys():
        action_ = cached_actions[action_name]
    else:
        action_ = pnaction.PNAction(action_name)
        if action_name in project.actions.keys():
            xml_action = project.actions[action_name]
            if xml_action.name:
                action_.setName(xml_action.name)
            if xml_action.table:
                action_.setTable(xml_action.table)
            if xml_action.form:
                action_.setForm(xml_action.form)
            if xml_action.formrecord:
                action_.setFormRecord(xml_action.formrecord)
            if xml_action.scriptform:
                action_.setScriptForm(xml_action.scriptform)
            if xml_action.scriptformrecord:
                action_.setScriptFormRecord(xml_action.scriptformrecord)
            if xml_action.description:
                action_.setDescription(xml_action.description)
            if xml_action.alias:
                action_.setCaption(xml_action.alias)
            elif xml_action.caption:
                action_.setCaption(xml_action.caption)

        cached_actions[action_name] = action_
        logger.trace("convert2FLAction: done")

    return action_
