"""Aqobjectquerylist module."""

from PyQt5 import QtCore, QtWidgets

from typing import List, Union, Optional


def AQObjectQueryList(
    obj_: Union[QtCore.QObject, int],
    inherits_class: Optional[str] = None,
    object_name: Optional[str] = None,
    reg_ext_match: bool = False,
    recursirve_search: bool = False,
) -> List:
    """Return a list with objects."""

    if isinstance(obj_, int):
        obj_ = QtWidgets.QApplication.topLevelWidgets()

    if inherits_class is None:
        inherits_class = "QWidgets"

    class_ = getattr(QtWidgets, inherits_class, QtWidgets.QWidget)

    args_ = []

    if not reg_ext_match:
        args_.append(class_)

    if object_name is not None:
        args_.append(object_name)

    if recursirve_search:
        args_.append(QtCore.Qt.FindChildrenRecursively)

    return obj_.findChildren(*args_)
