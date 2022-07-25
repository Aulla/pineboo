"""
To detect if we are in mobile mode.
"""

from PyQt6 import QtCore  # type: ignore[import]

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
    Return if you are working in mobile mode, searching local settings or check QtCore.QSysInfo().productType().

    @return True or False.
    """
    from pineboolib.core import settings

    return (
        True
        if QtCore.QSysInfo().productType() in ("android", "ios")
        else settings.CONFIG.value("ebcomportamiento/mobileMode", False)
    )


# def grand_storage_access():
#    """Grand storage permissions."""

#    sys_info = QtCore.QSysInfo()
#    product_type = sys_info.productType()

#    if product_type == "android":
#        import jnius
# from PyQt6 import QtAndroidExtras  # type: ignore #noqa: F821
# import sys

# android_jni = QtAndroidExtras.QAndroidJniObject("android/content/Context")
# get_system_service = android_jni.callStaticMethod(
#    "android/content/Context", "getSystemService"
# )
# result = QtAndroidExtras.QAndroidJniObject.callStaticMethod(
#    "android/content/Context", "getSystemService"
# )

# else:
#    if not android_jni.callStaticMethod("getSystemService"):
#        sys.exit(32)
# storage_service = get_system_service("android.context.Context.STORAGE_SERVICE")
# storage_service = get_system_service("STORAGE_SERVICE")
# get_system_service = android_jni.callStaticMethod("Context", "getSystemService")
# start_activity = android_jni.callStaticMethod("Context", "startActivity")
# storage_service = get_system_service("STORAGE_SERVICE")

# storage_list = storage_service.getStorageVolumes()
# for storage in storage_list:
#    intent = storage.createAccessIntent()
#    start_activity(intent)
