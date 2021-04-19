"""projectconfig module."""


import base64
import hashlib
import os
import pathlib
import fernet  # type: ignore [import] # noqa: F821

from xml.etree import ElementTree as ELT
from typing import Tuple, Optional, Any

from pineboolib import logging
from pineboolib.core.utils import utils_base
from pineboolib.core.utils import version as utils_version
from pineboolib.core import settings

VERSION_1_0 = utils_version.VersionNumber("1.0")
VERSION_1_1 = utils_version.VersionNumber("1.1")
VERSION_1_2 = utils_version.VersionNumber("1.2")

LOGGER = logging.get_logger(__name__)


class ProjectConfig:
    """
    Read and write XML on profiles. Represents a database connection configuration.
    """

    SAVE_VERSION = VERSION_1_2  #: Version for saving

    #: Folder where to read/write project configs.
    profile_dir: str = utils_base.filedir(
        settings.CONFIG.value(
            "ebcomportamiento/profiles_folder", "%s/Pineboo/profiles" % pathlib.Path.home()
        )
    )

    version: "utils_version.VersionNumber"  #: Version number for the profile read.
    fernet: Optional["fernet.Fernet"]  #: Cipher used, if any.

    database: str  #: Database Name, file path to store it, or :memory:
    host: Optional[str]  #: DB server Hostname. None for local files.
    port: Optional[int]  #: DB server port. None for local files.
    username: Optional[str]  #: Database User login name.
    password: Optional[str]  #: Database User login password.
    type: str  #: Driver Type name to use when connecting
    project_password: str  #: Password to cipher when load/saving. Empty string for no ciphering.
    password_required: bool  #: True if a password is required to read data. (Was partially loaded.)
    description: str  #: Project name in GUI
    filename: str  #: File path to read / write this project from / to

    def __init__(
        self,
        database: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        type: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        load_xml: Optional[str] = None,
        connstring: Optional[str] = None,
        description: Optional[str] = None,
        filename: Optional[str] = None,
        project_password: str = "",
    ) -> None:
        """Initialize."""
        self.project_password = project_password
        self.password_required = False
        self.version = self.SAVE_VERSION
        self.fernet = None

        if connstring:
            username, password, type, host, port, database = self.translate_connstring(connstring)
        elif load_xml:
            self.filename = os.path.join(
                self.profile_dir, load_xml if load_xml.endswith("xml") else "%s.xml" % load_xml
            )
            self.load_projectxml()
            return
        if database is None:
            raise ValueError("Database is mandatory. Or use load_xml / connstring params")
        if type is None:
            raise ValueError("Type is mandatory. Or use load_xml / connstring params")
        self.database = database
        self.host = host
        self.port = port
        self.type = type
        self.username = username
        self.password = password
        self.description = description if description else "unnamed"
        if filename is None:
            file_basename = self.description.lower().replace(" ", "_")
            self.filename = os.path.join(self.profile_dir, "%s.xml" % file_basename)
        else:
            self.filename = os.path.join(self.profile_dir, filename)

    def get_uri(self, show_password: bool = False) -> str:
        """Get connection as an URI."""
        host_port = ""
        if self.host:
            host_port += self.host
        if self.port:
            host_port += ":%d" % self.port

        user_pass = ""
        if self.username:
            user_pass += self.username
        if self.password:
            if show_password:
                user_pass += ":%s" % self.password
            else:
                pass_bytes: bytes = hashlib.sha256(self.password.encode()).digest()
                user_pass += ":*" + base64.b64encode(pass_bytes).decode()[:4]

        if user_pass:
            user_pass = "@%s" % user_pass

        uri = host_port + user_pass

        if self.database:
            if uri:
                uri += "/"
            uri += self.database

        return "[%s]://%s" % (self.type, uri)

    def __repr__(self) -> str:
        """Display the information in text mode."""
        if self.project_password:
            # 4 chars in base-64 is 3 bytes. 256**3 should be enough to know if you have the wrong
            # password.
            pass_bytes: bytes = hashlib.sha256(self.project_password.encode()).digest()
            passwd = "-" + base64.b64encode(pass_bytes).decode()[:4]
        else:
            passwd = ""
        return "<ProjectConfig%s name=%r uri=%r>" % (
            passwd,
            self.description,
            self.get_uri(show_password=False),
        )

    def __eq__(self, other: Any) -> bool:
        """Test for equality."""
        if not isinstance(other, ProjectConfig):
            return False
        if other.type != self.type:
            return False
        if other.get_uri(show_password=True) != self.get_uri(show_password=True):
            return False
        if other.description != self.description:
            return False
        if other.project_password != self.project_password:
            return False
        return True

    def load_projectxml(self) -> bool:
        """Collect the connection information from an xml file."""

        file_name = self.filename
        if not os.path.isfile(file_name):
            raise ValueError("El proyecto %r no existe." % file_name)

        tree = ELT.parse(file_name)
        root = tree.getroot()
        version = utils_version.VersionNumber(root.get("Version"), default="1.0")
        self.version = version
        self.description = ""
        for xmldescription in root.findall("name"):
            self.description = xmldescription.text or ""
        profile_pwd = ""
        for profile in root.findall("profile-data"):
            profile_pwd = getattr(profile.find("password"), "text", "")
            if profile_pwd:
                break

        self.password_required = True
        self.checkProfilePasswordForVersion(self.project_password, profile_pwd, version)

        self.fernet = None
        if self.project_password and self.version > VERSION_1_1:
            key_salt = hashlib.sha256(profile_pwd.encode()).digest()
            key = hashlib.pbkdf2_hmac("sha256", self.project_password.encode(), key_salt, 10000)
            key64 = base64.urlsafe_b64encode(key)
            self.fernet = fernet.Fernet(key64)

        from pineboolib.application.database import pnsqldriversmanager

        sql_drivers_manager = pnsqldriversmanager.PNSqlDriversManager()
        self.database = self.retrieveCipherSubElement(root, "database-name")
        for item in root.findall("database-server"):
            self.host = self.retrieveCipherSubElement(item, "host")
            port_text = self.retrieveCipherSubElement(item, "port")
            self.port = int(port_text) if port_text else None
            self.type = self.retrieveCipherSubElement(item, "type")

            # FIXME: Move this to project, or to the connection handler.
            if self.type not in sql_drivers_manager.aliasList():
                LOGGER.warning("Esta versión de pineboo no soporta el driver '%s'" % self.type)

        for credentials in root.findall("database-credentials"):
            self.username = self.retrieveCipherSubElement(credentials, "username")
            self.password = self.retrieveCipherSubElement(credentials, "password")
            if self.password and self.fernet is None:
                self.password = base64.b64decode(self.password).decode()
        self.password_required = False

        return True

    @classmethod
    def encodeProfilePasswordForVersion(
        cls,
        password: str,
        version_: "utils_version.VersionNumber",  # type: ignore [name-defined] # noqa: F821
    ) -> str:
        """
        Hash a password for a profile/projectconfig using the protocol for specified version.
        """
        if password == "":
            return ""
        if version_ < VERSION_1_1:
            return password

        if version_ < VERSION_1_2:
            return hashlib.sha256(password.encode()).hexdigest()
        # Minimum salt size recommended is 8 bytes
        # multiple of 3 bytes as it is shorter in base64
        salt = os.urandom(9)
        hmac = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 10000)
        dict_passwd = {
            # Algorithm:
            # .. pbkdf2: short algorithm name
            # .. sha256: hash function used
            # .. 4: number of zeroes used on iterations
            "algorithm": "pbkdf2-sha256-4",
            "salt": base64.b64encode(salt).decode(),
            "hash": base64.b64encode(hmac).decode(),
        }
        hashed_password = "%(algorithm)s:%(salt)s:%(hash)s" % dict_passwd

        return hashed_password

    @classmethod
    def checkProfilePasswordForVersion(
        cls,
        user_pwd: str,
        profile_pwd: str,
        version_: "utils_version.VersionNumber",  # type: ignore [name-defined] # noqa: F821
    ) -> None:
        """
        Check a saved password against a user-supplied one.

        user_pwd: User-supplied password in clear text.
        profile_pwd: Raw data saved as password in projectconfig file.
        version: Version number used for checks.

        This function returns None and raises PasswordMismatchError if the password is wrong.
        We can only check if it is good. It's not a good idea to check if two encoded passwords
        are the same, because most secure methods will store different encoded versions every
        time we try to encode again.
        """
        if not profile_pwd:
            return

        if version_ < VERSION_1_1:
            if user_pwd == profile_pwd:
                return
            raise PasswordMismatchError("La contraseña es errónea")

        if version_ < VERSION_1_2:
            user_hash = hashlib.sha256(user_pwd.encode()).hexdigest()
            if profile_pwd == user_hash:
                return
            raise PasswordMismatchError("La contraseña es errónea")

        algo, *algo_extra = profile_pwd.split(":")
        if algo != "pbkdf2-sha256-4":
            raise Exception("Unsupported password algorithm %r" % algo)

        salt64, hash64 = algo_extra

        salt = base64.b64decode(salt64.encode())

        user_hash2 = hashlib.pbkdf2_hmac("sha256", user_pwd.encode(), salt, 10000)
        user_hash64 = base64.b64encode(user_hash2).decode()
        if user_hash64 == hash64:
            return

        raise PasswordMismatchError("La contraseña es errónea")

    def createCipherSubElement(
        self, parent: "ELT.Element", tagname: str, text: str
    ) -> "ELT.Element":
        """Create a XML SubElement ciphered if self.fernet is present."""
        child = ELT.SubElement(parent, tagname)
        if self.fernet is None:
            child.text = text
            return child
        # NOTE: This method returns ciphertext even for empty strings! This is intended.
        # ... this is to avoid anyone knowing if a field is empty or not.
        if len(text) < 64:
            # Right Pad with new line at least up to 64 bytes. Avoid giving out field size.
            text = text.ljust(64, "\n")
        encoded_bytes = self.fernet.encrypt(text.encode())
        encoded_text = base64.b64encode(encoded_bytes).decode()
        child.set("cipher-method", "cryptography.Fernet")
        child.set("cipher-text", encoded_text)
        return child

    def retrieveCipherSubElement(self, parent: "ELT.Element", tagname: str) -> str:
        """Get a XML SubElement ciphered if self.fernet is present."""
        child = parent.find(tagname)
        if child is None:
            raise ValueError("Tag %r not present" % tagname)

        cipher_method = child.get("cipher-method")
        if cipher_method is None:
            return child.text or ""
        if self.fernet is None:
            raise Exception("Tried to load ciphered tag %r with no loaded cipher" % tagname)
        cipher_text = child.get("cipher-text")
        if cipher_method != "cryptography.Fernet":
            raise ValueError("Cipher method %r not supported." % cipher_method)

        if not cipher_text:
            raise ValueError("Missing ciphertext for %r" % tagname)

        cipher_bytes = base64.b64decode(cipher_text.encode())
        text = self.fernet.decrypt(cipher_bytes).decode()
        text = text.rstrip("\n")
        return text

    def save_projectxml(self, overwrite_existing: bool = True) -> None:
        """
        Save the connection.
        """
        profile = ELT.Element("Profile")
        profile.set("Version", str(self.SAVE_VERSION))
        description = self.description
        filename = self.filename
        if not os.path.exists(self.profile_dir):
            os.mkdir(self.profile_dir)

        if not overwrite_existing and os.path.exists(filename):
            raise ProfileAlreadyExistsError

        passw_db = self.password or ""

        profile_user = ELT.SubElement(profile, "profile-data")
        profile_password = ELT.SubElement(profile_user, "password")
        profile_password.text = self.encodeProfilePasswordForVersion(
            self.project_password, self.SAVE_VERSION
        )

        self.fernet = None
        if self.project_password and self.SAVE_VERSION > VERSION_1_1:
            key_salt = hashlib.sha256(profile_password.text.encode()).digest()
            key = hashlib.pbkdf2_hmac("sha256", self.project_password.encode(), key_salt, 10000)
            key64 = base64.urlsafe_b64encode(key)
            self.fernet = fernet.Fernet(key64)
        else:
            # Mask the password if no cipher is used!
            passw_db = base64.b64encode(passw_db.encode()).decode()

        name = ELT.SubElement(profile, "name")
        name.text = description
        dbs = ELT.SubElement(profile, "database-server")
        self.createCipherSubElement(dbs, "type", text=self.type)
        self.createCipherSubElement(dbs, "host", text=self.host or "")
        self.createCipherSubElement(dbs, "port", text=str(self.port) if self.port else "")

        dbc = ELT.SubElement(profile, "database-credentials")
        self.createCipherSubElement(dbc, "username", text=self.username or "")
        self.createCipherSubElement(dbc, "password", text=passw_db)

        self.createCipherSubElement(profile, "database-name", text=self.database)

        utils_base.pretty_print_xml(profile)

        tree = ELT.ElementTree(profile)

        tree.write(filename, xml_declaration=True, encoding="utf-8")
        self.version = self.SAVE_VERSION

    @classmethod
    def translate_connstring(cls, connstring: str) -> Tuple[str, str, str, str, int, str]:
        """
        Translate a DSN connection string into user, pass, etc.

        Accept a "connstring" parameter that has the form user @ host / dbname
        and returns all parameters separately. It takes into account the
        default values ​​and the different abbreviations that exist.
        """
        user = "postgres"
        passwd = ""
        host = "127.0.0.1"
        port = "5432"
        driver_alias = "PostgreSQL (PSYCOPG2)"
        user_pass = None
        host_port = None

        import re

        if "/" not in connstring:
            dbname = connstring
            if not re.match(r"\w+", dbname):
                raise ValueError("base de datos no valida")
            return user, passwd, driver_alias, host, int(port), dbname

        uphpstring = connstring[: connstring.rindex("/")]
        dbname = connstring[connstring.rindex("/") + 1 :]
        up_, hp_ = uphpstring.split("@")
        conn_list = [None, None, up_, hp_]
        _user_pass, _host_port = conn_list[-2], conn_list[-1]

        if _user_pass:
            user_pass = _user_pass.split(":") + ["", "", ""]
            user, passwd, driver_alias = (
                user_pass[0],
                user_pass[1] or passwd,
                user_pass[2] or driver_alias,
            )
            if user_pass[3]:
                raise ValueError("La cadena de usuario debe tener el formato user:pass:driver.")

        if _host_port:
            host_port = _host_port.split(":") + [""]
            host, port = host_port[0], host_port[1] or port
            if host_port[2]:
                raise ValueError("La cadena de host debe ser host:port.")

        if not re.match(r"\w+", user):
            raise ValueError("Usuario no valido")
        if not re.match(r"\w+", dbname):
            raise ValueError("base de datos no valida")
        if not re.match(r"\d+", port):
            raise ValueError("puerto no valido")
        LOGGER.debug(
            "user:%s, passwd:%s, driver_alias:%s, host:%s, port:%s, dbname:%s",
            user,
            "*" * len(passwd),
            driver_alias,
            host,
            port,
            dbname,
        )
        return user, passwd, driver_alias, host, int(port), dbname


class ProfileAlreadyExistsError(Exception):
    """Report that project will not be overwritten."""


class PasswordMismatchError(Exception):
    """Provided password is wrong."""
