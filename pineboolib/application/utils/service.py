"""Service module."""

import os
import sys

from typing import List


def main() -> None:
    """Service manager."""

    if os.geteuid() != 0:
        exit(
            "You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting."
        )

    option = "--help"
    if len(sys.argv) > 1:
        option = sys.argv[1]

    if option in ["-h", "--help"]:
        print(
            "options:\n\t --install : Install service.\n\t --remove  : Remove service.\n\t -h --help : This help."
        )
    elif option in ["--install"]:
        path_initd = _resolve_path()
        if _remove_service(path_initd):
            print("Ok" if _install_service(path_initd) else "Fail")

    elif option in ["--remove"]:
        path_initd = _resolve_path()
        print("Ok" if _remove_service(path_initd) else "Fail")


def _install_service(path_initd: str) -> bool:
    """Remove neew service file."""

    pineboo_service_file_name = os.path.join(path_initd, "pineboo_service")
    try:
        file_ = open(pineboo_service_file_name, "w", encoding="UTF-8")
        file_.writelines(["%s\n" % linea for linea in _script_lines()])
        file_.close()
    except Exception as error:
        print("Error writing file %s : %s" % (pineboo_service_file_name, error))
        return False

    return True


def _remove_service(path_initd: str) -> bool:
    """Remove old service file."""

    pineboo_service_file_name = os.path.join(path_initd, "pineboo_service")
    print("Checking for %s" % pineboo_service_file_name)
    if os.path.exists(pineboo_service_file_name):
        print("Removing older file %s" % pineboo_service_file_name)
        try:
            os.remove(pineboo_service_file_name)
        except Exception as error:
            print("Error deleting file %s : %s" % (pineboo_service_file_name, error))
            return False

    return True


def _resolve_path() -> str:
    """Resolve initd path."""

    path_initd = sys.argv[2] if len(sys.argv) == 3 else None
    if not path_initd:
        for test_path in ["/etc/init.d"]:
            if os.path.exists(test_path):
                path_initd = test_path
                break

    if path_initd:
        if not os.path.exists(path_initd):
            exit("Invalid initd path (%s)" % path_initd)
    else:
        exit("Initd path not found")

    return path_initd


def _script_lines() -> List[str]:
    """Return script lines."""
    from pineboolib.application import PINEBOO_VER

    data: List[str] = []
    data.append("#!/usr/bin/python")
    data.append("")
    data.append("Build by Pineboo %s" % PINEBOO_VER)
    data.append("")
    data.append("from daemon import runner")
    data.append("from pineboolib import application as pineboolib_app")
    data.append("from pineboolib.application.parsers import parser_qsa as qsaparser")
    data.append("from pineboolib.core.settings import CONFIG")
    data.append("from pineboolib.loader.projectconfig import ProjectConfig")
    data.append("")
    data.append("temp_dir=/opt/pineboo_cache")
    data.append("prj_name=None # Path to file project (.xml)")
    data.append(
        "SQL_CONN=None # ProjectConfig(database=_database_, host=_host_,"
        + " port=_port_, type='PostgreSQL (PSYCOPG2)', username=_user_name_, password=_pass_)"
    )
    data.append("")
    data.append("")
    data.append("class App():")
    data.append("    def __init__(self):")
    data.append("        self.stdin_path = '/dev/null'")
    data.append("        self.stdout_path = '/dev/tty'")
    data.append("        self.stderr_path = '/dev/tty'")
    data.append("        self.pidfile_path = '/tmp/pineboo_service.pid'")
    data.append("        # self.pidfile_timeout = 5")
    data.append("    def run(self):")
    data.append("")
    data.append("        qsaparser.USE_THREADS = False")
    data.append("        prj = pineboolib_app.PROJECT")
    data.append("        prj.tmpdir = temp_dir")
    data.append("        prj.conn_manager.REMOVE_CONNECTIONS_AFTER_ATOMIC = True")
    data.append("        prj.conn_manager.set_max_connections_limit(100)")
    data.append("        prj.conn_manager.set_safe_mode(2)")
    data.append("        if prj_name:")
    data.append("            SQL_CONN=ProjectConfig(load_xml=prj_name)")
    data.append("")
    data.append("        if SQL_CONN:")
    data.append("            main.startup_framework(SQL_CONN)")
    data.append("")
    data.append("        prj.no_python_cache = False")
    data.append("        pineboolib_app.SHOW_CURSOR_EVENTS = False")
    data.append("")
    data.append("app = App()")
    data.append("daemon_runner = runner.DaemonRunner(app)")
    data.append("daemon_runner.do_action()")

    return data
