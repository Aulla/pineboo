"""Test_flutil module."""

import unittest

from pineboolib.fllegacy import flsmtpclient
from pineboolib import application


class TestSmtp(unittest.TestCase):
    """TestSmtp class."""

    cli: flsmtpclient.FLSmtpClient

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        cls.cli = flsmtpclient.FLSmtpClient()

    def test_smtp(self) -> None:
        """Test smtp functions."""
        self.cli.status.connect(self.cambio)
        mail_ = "aaa@aaa.aa"
        password_ = "bbbbbbb"

        self.cli.setUser(mail_)
        self.cli.setPassword(password_)

        self.cli.setMailServer("smtp.gmail.com")
        self.cli.setPort(587)
        self.cli.setAuthMethod(self.cli.SendAuthLogin)
        self.cli.setConnectionType(self.cli.TlsConnection)

        self.cli.setFrom(mail_)
        self.cli.setTo(mail_)
        self.cli.setSubject("prueba de correo")
        self.cli.setBody("Esto es una prueba de Pineboo %s" % application.PROJECT.load_version())

        res: bool = self.cli.startSend()
        self.assertFalse(res)  # assertTrue when login is ok

    def cambio(self):
        print(self.cli.lastStatusMsg())
