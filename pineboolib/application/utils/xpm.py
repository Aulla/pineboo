"""Manage cached xpm."""

import os
import os.path

from pineboolib.core import settings
from pineboolib import logging, application

LOGGER = logging.get_logger(__name__)


def cache_xpm(value: str, xpm_name: str = "") -> str:
    """
    Return a path to a file with the content of the specified string.

    @param value. text string with the xpm or path to this.
    @return file path contains Xpm
    """

    if not value:
        LOGGER.warning("the value is empty!")
        return ""

    if not xpm_name:
        xpm_name = value[: value.find("[]")]
        xpm_name = xpm_name[xpm_name.rfind(" ") + 1 :]

    conn = application.PROJECT.conn_manager.mainConn()
    if conn is None:
        raise Exception("Project is not connected yet")

    cache_dir = "%s/cache/%s/cacheXPM" % (application.PROJECT.tmpdir, conn.DBName())
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    file_name = (
        "%s/%s" % (cache_dir, value[value.find("cacheXPM") + 9 :])
        if value.find("cacheXPM") > -1
        else "%s/%s.xpm" % (cache_dir, xpm_name)
    )

    if not os.path.exists(file_name) or settings.CONFIG.value(
        "ebcomportamiento/no_img_cached", False
    ):
        file_ = open(file_name, "w")
        file_.write(value)
        file_.close()

    return file_name
