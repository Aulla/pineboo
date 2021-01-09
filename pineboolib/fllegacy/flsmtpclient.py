"""Flsmtpclient module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtGui  # type: ignore
from os.path import basename
from pineboolib import logging

import smtplib
import socket

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

from typing import List, Optional, Any, Dict

LOGGER = logging.get_logger(__name__)


class State(object):
    """State class."""

    Init: int = 0
    Mail: int = 1
    Rcpt: int = 2
    Data: int = 3
    Body: int = 4
    Quit: int = 5
    Close: int = 6
    SmtpError: int = 7
    Connecting: int = 8
    Connected: int = 9
    MxDnsError: int = 10
    SendOk: int = 11
    SockedError: int = 12
    Composing: int = 13
    Attach: int = 14
    AttachError: int = 15
    ServerError: int = 16
    ClientError: int = 17
    StartTTLS: int = 18
    WaitingForSTARTTLS: int = 19
    SendAuthPlain: int = 20
    SendAuthLogin: int = 21
    WaitingForAuthPlain: int = 22
    WaitingForAuthLogin: int = 23
    WaitingForUser: int = 24
    WaitingForPass: int = 25


class AuthMethod(object):
    """AuthMethod class."""

    NoAuth: int = 0
    AuthPlain: int = 1
    AuthLogin: int = 2


class ConnectionType(object):
    """ConnectionType class."""

    TcpConnection: int = 0
    SslConnection: int = 1
    TlsConnection: int = 2


class FLSmtpClient(QtCore.QObject, AuthMethod, ConnectionType, State):
    """FLSmtpClient class."""

    from_value_: Optional[str]
    reply_to_: Optional[str]
    to_: Optional[str]
    cc_: Optional[str]
    bcc_: Optional[str]
    organization_: Optional[str]
    priority_: int
    subject_: Optional[str]
    body_: Optional[str]

    attachments_: List[str]

    mail_server_: Optional[str]
    mime_type_: Optional[str]
    port_: Optional[int]

    text_parts_: List[str]
    map_attach_cid_: Dict[str, Any]

    status_msg_: Optional[str]
    state_code_: int

    user_: Optional[str]
    password_: Optional[str]
    connection_type_: int
    auth_method_: int

    status = QtCore.pyqtSignal(str)
    sendStarted = QtCore.pyqtSignal()
    sendEnded = QtCore.pyqtSignal()
    sendTotalSteps = QtCore.pyqtSignal(int)
    sendStepNumber = QtCore.pyqtSignal(int)
    statusChanged = QtCore.pyqtSignal(str, int)

    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        """Inicialize."""
        super(FLSmtpClient, self).__init__(parent)
        self.state_code_ = State.Init
        self.status_msg_ = None
        self.priority_ = 0
        self.port_ = 25
        self.connection_type_ = ConnectionType.TcpConnection
        self.auth_method_ = AuthMethod.NoAuth
        self.from_value_ = None
        self.reply_to_ = None
        self.to_ = None
        self.cc_ = None
        self.bcc_ = None
        self.organization_ = None
        self.priority_ = 0
        self.subject_ = None
        self.body_ = None
        self.attachments_ = []
        self.mail_server_ = None
        self.mime_type_ = None
        self.port_ = None
        self.text_parts_ = []
        self.map_attach_cid_ = {}
        self.user_ = None
        self.password_ = None
        self.connection_type_ = 0
        self.auth_method_ = 0

    def setFrom(self, from_: str) -> None:
        """Set from."""
        self.from_value_ = from_

    def from_(self) -> Optional[str]:
        """Return from."""

        return self.from_value_

    def setReplyTo(self, reply_to: str) -> None:
        """Set reply to."""

        self.reply_to_ = reply_to

    def replyTo(self) -> Optional[str]:
        """Return reply to."""

        return self.reply_to_

    def setTo(self, to_: str) -> None:
        """Set to."""
        self.to_ = to_

    def to(self) -> Optional[str]:
        """Return to."""
        return self.to_

    def setCC(self, cc_: str) -> None:
        """Set cc."""
        self.cc_ = cc_

    def CC(self) -> Optional[str]:
        """Return cc."""
        return self.cc_

    def setBCC(self, cc_: str) -> None:
        """Set bcc."""

        self.bcc_ = cc_

    def BCC(self) -> Optional[str]:
        """Return bcc."""

        return self.bcc_

    def setOrganization(self, org: str) -> None:
        """Set organization."""

        self.organization_ = org

    def organization(self) -> Optional[str]:
        """Return organization."""

        return self.organization_

    def setPriority(self, prio: int) -> None:
        """Set priority."""

        self.priority_ = prio

    def priority(self) -> int:
        """Return priority."""
        return self.priority_

    def setSubject(self, subject: str) -> None:
        """Set subject."""
        self.subject_ = subject

    def subject(self) -> Optional[str]:
        """Return subject."""

        return self.subject_

    def setBody(self, body: str) -> None:
        """Set body."""
        self.body_ = body

    def body(self) -> Optional[str]:
        """Return body."""
        return self.body_

    def addAttachment(self, attach: str, cid: Optional[Any] = None) -> None:
        """Add attachment file to mail."""
        if QtCore.QFile.exists(attach) and QtCore.QFileInfo(attach).isReadable():
            if attach and attach not in self.attachments_:
                self.attachments_.append(attach)
                if cid:
                    self.map_attach_cid_[attach] = cid
        else:
            err_msg_ = self.tr("El fichero %s no existe o no se puede leer\n\n" % attach)
            LOGGER.warning(err_msg_)
            self.changeStatus(err_msg_, State.AttachError)

    def addTextPart(self, text: Optional[str], mime_type: str = "text/plain") -> None:
        """Add text part to mail."""
        if text is not None:
            self.text_parts_.append(text)
            self.text_parts_.append(mime_type)

    def setMailServer(self, mail_server: str) -> None:
        """Set mail server."""
        self.mail_server_ = mail_server

    def mailServer(self) -> Optional[str]:
        """Return mail server."""
        return self.mail_server_

    def setMimeType(self, mine_type: str) -> None:
        """Set mine type."""
        self.mime_type_ = mine_type

    def mimeType(self) -> Optional[str]:
        """Return mine type."""

        return self.mime_type_

    def setPort(self, port: int) -> None:
        """Set port."""
        self.port_ = port

    def port(self) -> Optional[int]:
        """Return port."""
        return self.port_

    def lastStatusMsg(self) -> Optional[str]:
        """Return last status message."""

        return self.status_msg_

    def lastStateCode(self) -> int:
        """Return last state code."""
        return self.state_code_

    def setUser(self, user: str) -> None:
        """Set user name."""
        self.user_ = user

    def user(self) -> Optional[str]:
        """Return user name."""
        return self.user_

    def setPassword(self, password: str) -> None:
        """Set password."""
        self.password_ = password

    def password(self) -> Optional[str]:
        """Return password."""
        return self.password_

    def setConnectionType(self, conn: int) -> None:
        """Set connection type."""
        self.connection_type_ = conn

    def connectionType(self) -> int:
        """Return connection type."""

        return self.connection_type_

    def setAuthMethod(self, method: int) -> None:
        """Set authentication method."""
        self.auth_method_ = method

    def authMethod(self) -> int:
        """Return authentication method."""
        return self.auth_method_

    def startSend(self) -> bool:
        """Start send mail."""

        from pineboolib.core.utils import utils_base
        from pineboolib.core import settings
        from pineboolib import application

        self.sendStarted.emit()
        self.sendTotalSteps.emit(len(self.attachments_) + 3)

        step = 0

        self.changeStatus(self.tr("Componiendo mensaje"), State.Composing)

        outer = MIMEMultipart()
        outer["From"] = self.from_value_ or ""
        outer["To"] = self.to_ or ""
        if self.cc_ is not None:
            outer["Cc"] = self.cc_
        if self.bcc_ is not None:
            outer["Bcc"] = self.bcc_
        if self.organization_ is not None:
            outer["Organization"] = self.organization_
        if self.priority_ > 0:
            outer["Priority"] = str(self.priority_)
        outer["Subject"] = self.subject_ or ""
        outer.preamble = "You will not see this in a MIME-aware mail reader.\n"
        mime_type_ = "text/plain"

        if self.mime_type_ is not None:
            mime_type_ = self.mime_type_

        outer.add_header("Content-Type", mime_type_)

        outer.attach(MIMEText(self.body_ or "", mime_type_.split("/")[1], "utf-8"))

        step += 1
        self.sendStepNumber.emit(step)
        # Adjuntar logo
        if settings.SETTINGS.value("email/sendMailLogo", True):
            logo = settings.SETTINGS.value(
                "email/mailLogo", "%s/logo_mail.png" % application.PROJECT.tmpdir
            )
            if not QtCore.QFile.exists(logo):
                logo = "%s/logo.png" % application.PROJECT.tmpdir
                QtGui.QPixmap(utils_base.pixmap_from_mime_source("pineboo-logo.png")).save(
                    logo, "PNG"
                )

            fp_ = open(logo, "rb")
            logo_part = MIMEImage(fp_.read())
            fp_.close()

            logo_part.add_header("Content-ID", "<image>")
            outer.attach(logo_part)

        # Ficheros Adjuntos
        for att in self.attachments_:
            try:
                with open(att, "rb") as fil:
                    part = MIMEApplication(fil.read(), Name=basename(att))
                    part["Content-Disposition"] = 'attachment; filename="%s"' % basename(att)
                    outer.attach(part)
            except IOError:
                LOGGER.warning("Error al adjuntar el fichero %s." % att)
                return False

        # Envio mail
        composed = outer.as_string()

        step += 1
        self.sendStepNumber.emit(step)

        try:
            smtp = smtplib.SMTP("%s:%s" % (self.mail_server_ or "", self.port_ or 25))
            if self.connection_type_ == ConnectionType.TlsConnection:
                smtp.starttls()
                self.changeStatus("StartTTLS", State.StartTTLS)

            if self.user_ and self.password_:
                status_msg = "login."
                if self.auth_method_ == State.SendAuthLogin:
                    self.changeStatus(status_msg, State.SendAuthLogin)
                elif self.auth_method_ == State.SendAuthPlain:
                    self.changeStatus(status_msg, State.SendAuthPlain)

                smtp.login(self.user_, self.password_)

                self.changeStatus(
                    status_msg,
                    State.WaitingForAuthLogin
                    if self.auth_method_ == State.SendAuthLogin
                    else State.WaitingForAuthPlain,
                )

            smtp.sendmail(self.from_value_ or "", self.to_ or "", composed)
            self.changeStatus("Correo enviado", State.SendOk)
            smtp.quit()
            return True

        except smtplib.SMTPHeloError:
            status_msg = "El servidor no ha respondido correctamente al saludo."
            self.changeStatus(status_msg, State.ClientError)
            return False
        # except smtplib.SMTPNotSupportedError:
        #     status_msg = "El tipo de autenticación no está soportada por el servidor."
        #     self.changeStatus(status_msg, State.ClientError)
        #     return False
        except smtplib.SMTPConnectError:
            status_msg = "No se puede conectar al servidor SMTP."
            self.changeStatus(status_msg, State.ServerError)
            return False
        except smtplib.SMTPAuthenticationError:
            status_msg = "Error de autenticación SMTP."
            self.changeStatus(status_msg, State.ClientError)
            return False
        except smtplib.SMTPSenderRefused:
            status_msg = "Dirección de remitente rechazada."
            self.changeStatus(status_msg, State.ClientError)
            return False
        except smtplib.SMTPRecipientsRefused:
            status_msg = "Todas las direcciones de destinatarios se rechazaron."
            self.changeStatus(status_msg, State.ClientError)
            return False
        except smtplib.SMTPServerDisconnected:
            status_msg = "El servidor se desconecta inesperadamente."
            self.changeStatus(status_msg, State.ServerError)
            return False
        except smtplib.SMTPException:
            status_msg = "Error desconocido"
            self.changeStatus(status_msg, State.ClientError)
            return False
        except socket.gaierror:
            status_msg = (
                "Servidor SMTP no encontrado.Verifique el nombre de host de su servidor SMTP."
            )
            self.changeStatus(status_msg, State.SmtpError)
            return False
        except Exception as error:
            status_msg = "Error sending mail %s." % error
            return False

    def changeStatus(self, status_msg: str, state_code: int) -> None:
        """Change send mail status."""
        self.status_msg_ = status_msg
        self.state_code_ = state_code
        self.statusChanged.emit(self.status_msg_, self.state_code_)
        self.status.emit(self.status_msg_)
