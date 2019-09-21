"""Flremoteclient module."""

import json

from pineboolib.application.utils.check_dependencies import check_dependencies
from pineboolib import logging
from . import pnsqlschema

from typing import Any, Callable, Dict, List, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.application.metadata import pntablemetadata  # noqa: F401


logger = logging.getLogger(__name__)


def base_create_dict(
    method: str, fun: str, id: str, arguments: List[Any] = []
) -> Dict[str, Union[str, int, List[Any], Dict[str, Any]]]:
    """Return a formated query dict."""
    data = [{"function": fun, "arguments": arguments, "id": id}]
    return {"method": method, "params": data, "jsonrpc": "2.0", "id": id}


class FLREMOTECLIENT(pnsqlschema.PNSqlSchema):
    """FLREMOTECLIENT class."""

    version_: str
    conn_: Any
    name_: str
    alias_: str
    errorList: List[str]
    lastError_: Optional[str]
    db_: Any
    mobile_: bool
    _dbname: str
    pure_python_: bool
    defaultPort_: int
    id_: str

    def __init__(self) -> None:
        """Inicialize."""
        self.version_ = "0.6"
        self.conn_ = None
        self.name_ = "REMOTECLIENT"
        self.open_ = False
        self.errorList = []
        self.alias_ = "Pineboo Server"
        self.mobile_ = False
        self.pure_python_ = False
        self.defaultPort_ = 4000
        self.id_ = "0"
        self.url: Optional[str] = None
        check_dependencies({"requests": "requests"}, False)
        self.lastError_ = None

    def safe_load(self) -> bool:
        """Return if the driver can loads dependencies safely."""
        return True

    def create_dict(self, fun, data: Any = []) -> Dict[str, Any]:
        """Return a formated dict."""
        fun = "%s__%s" % (self.id_, fun)
        return base_create_dict("dbdata", fun, str(self.id_), data)

    def send_to_server(self, js) -> Any:
        """Send data to server and retur result."""
        import requests

        headers = {"content-type": "application/json"}
        if self.url is None:
            raise Exception("send_to_server. self.url is None")
        req = requests.post(self.url, data=json.dumps(js), headers=headers).json()
        res_ = req["result"] if "result" in req.keys() else None
        # if res_ is None:
        #    print("FAIL %s --> %s\n%s" % (js, self.url, req))

        if res_ == "Desconocido":
            print("%s -> %s\nresult: %s" % (js, self.url, res_))
        return res_

    def connect(
        self, db_name: str, db_host: str, db_port: int, db_user_name: str, db_password: str
    ) -> Any:
        """Connec to to database."""
        self._dbname = db_name
        self.id_ = db_user_name
        self.url = "http://%s:%s/jsonrpc" % (db_host, db_port)
        dict_ = self.create_dict("hello")
        try:
            ret = self.send_to_server(dict_)
        except Exception as exc:
            print(exc)
            return False

        server_found = False

        if ret[0:7] == "Welcome":
            server_found = True

        if server_found:
            self.conn_ = Connection(db_name, self)

            if not self.conn_.is_valid():
                return False

        return self.conn_

    def __getattr__(self, name) -> Callable:
        """Return attribute from server."""
        return VirtualFunction(name, self).virtual

    def refreshQuery(
        self, curname: str, fields: str, table: str, where: str, cursor: Any, conn: Any
    ) -> None:
        """Set a refresh query for database."""
        self.send_to_server(
            self.create_dict(
                "refreshQuery",
                {
                    "cursor_id": cursor.id_,
                    "curname": "%s_%s" % (self.id_, curname),
                    "fields": fields,
                    "table": table,
                    "where": where,
                },
            )
        )

    def refreshFetch(
        self, number: int, curname: str, table: str, cursor: Any, fields: str, where_filter: str
    ) -> None:
        """Return data fetched."""
        self.send_to_server(
            self.create_dict(
                "refreshFetch",
                {
                    "cursor_id": cursor.id_,
                    "curname": "%s_%s" % (self.id_, curname),
                    "fields": fields,
                    "table": table,
                    "where_filter": where_filter,
                    "number": number,
                },
            )
        )

    def fetchAll(
        self, cursor: Any, tablename: str, where_filter: str, fields: str, curname: str
    ) -> List:
        """Return all fetched data from a query."""
        return self.send_to_server(
            self.create_dict(
                "fetchAll",
                {
                    "cursor_id": cursor.id_,
                    "tablename": tablename,
                    "where_filter": where_filter,
                    "fields": fields,
                    "curname": "%s_%s" % (self.id_, curname),
                },
            )
        )


class Cursor(object):
    """Cursor class."""

    driver_: FLREMOTECLIENT
    id_: int
    data_: Any
    current_: Optional[int]
    last_sql: Optional[str]
    description: Optional[str]

    def __init__(self, driver: FLREMOTECLIENT, n: int) -> None:
        """Inicialize."""
        self.driver_ = driver
        self.id_ = n
        self.current_ = None
        self.last_sql = None
        self.description = None

    def __getattr__(self, name: str) -> None:
        """Capture orphaned attributes."""

        logger.info("Cursor: cursor(%s).%s !!", self.id_, name)
        logger.trace("Detalle:", stack_info=True)

    def execute(self, sql: str) -> None:
        """Exceute a query on the server an return the value."""
        self.last_sql = sql
        self.data_ = self.driver_.send_to_server(
            self.driver_.create_dict("execute", {"cursor_id": self.id_, "sql": sql})
        )
        self.current_ = 0

    def close(self) -> None:
        """Close connection."""
        self.driver_.send_to_server(self.driver_.create_dict("close", {"cursor_id": self.id_}))

    def fetchone(self) -> Any:
        """Return a Dict with a data fetched."""
        ret_ = self.driver_.send_to_server(
            self.driver_.create_dict("fetchone", {"cursor_id": self.id_})
        )
        # print(self.id_, "**", self.last_sql, ret_)
        return ret_

    def fetchall(self) -> Any:
        """Fetch All data from a server cursor."""
        ret_ = self.driver_.send_to_server(
            self.driver_.create_dict("fetchall", {"cursor_id": self.id_})
        )
        # print(self.id_, "**", self.last_sql, ret_)
        return ret_

    def __iter__(self) -> "Cursor":
        """Iterate function."""
        return self

    def __next__(self) -> Any:
        """Next iterator function."""

        ret = self.driver_.send_to_server(
            self.driver_.create_dict("fetchone", {"cursor_id": self.id_})
        )
        if ret is None:
            raise StopIteration
        return ret


class Connection(object):
    """Connection class."""

    db_name_: str
    driver_: FLREMOTECLIENT
    list_cursor: List[Cursor]

    def __init__(self, db_name: str, driver: FLREMOTECLIENT) -> None:
        """Inicialize."""
        self.db_name_ = db_name
        self.driver_ = driver
        self.list_cursor = []

    def is_valid(self) -> bool:
        """Return if the connection is valid."""
        db_name_server = self.driver_.send_to_server(self.driver_.create_dict("db_name"))
        return self.db_name_ == db_name_server

    def cursor(self) -> Cursor:
        """Return a Cursor."""
        cur = Cursor(self.driver_, len(self.list_cursor))
        self.list_cursor.append(cur)
        return cur


class VirtualFunction(object):
    """VirtualFunction class."""

    name_: str
    driver_: FLREMOTECLIENT

    def __init__(self, name: str, driver: FLREMOTECLIENT) -> None:
        """Inicialize."""
        self.name_ = name
        self.driver_ = driver

    def virtual(self, *args) -> Any:
        """Return values from a server function."""
        # return self.driver_.send_to_server(self.driver_.create_dict("%s_%s" % (self.driver_.conn_.user_name_, self.name_), args))
        return self.driver_.send_to_server(self.driver_.create_dict(self.name_, args))
