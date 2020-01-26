"""
To detect if we are in mobile mode.
"""

from PyQt5 import QtCore

MOBILE_MODE = None


def is_mobile_mode() -> bool:
    """
    Return if you are working in mobile mode.

    @return True or False
    """

    global MOBILE_MODE
    if MOBILE_MODE is None:
        MOBILE_MODE = check_mobile_mode()
    return MOBILE_MODE


def check_mobile_mode() -> bool:
    """
    Return if you are working in mobile mode, searching local settings or importing Android library.

    @return True or False.
    """
    is_mobile = False
    sys_info = QtCore.QSysInfo()
    product_type = sys_info.productType()

    if product_type in ("android", "ios"):
        is_mobile = True

    else:
        from pineboolib.core import settings

        is_mobile = settings.config.value(u"ebcomportamiento/mobileMode", False)

    return is_mobile
