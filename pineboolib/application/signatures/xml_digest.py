"""Xml_digest module."""

from pineboolib.core.utils import logging

import os
import xmlsig  # type: ignore[import] # noqa: F821
from lxml import etree  # type: ignore[import] # noqa: F821
from cryptography.hazmat import backends  # type: ignore[import] # noqa: F821
from cryptography.hazmat.primitives.serialization import pkcs12  # type: ignore[import] # noqa: F821
from xades import policy, utils, template, XAdESContext  # type: ignore[import] # noqa: F821


from typing import List, Optional, Any, Union

LOGGER = logging.get_logger(__name__)


class XmlDigest:
    """XmlDigest class."""

    _root: "etree"
    _pass: str
    _policy_list: List[str]
    _cert_path: str
    _certificate: Any
    _policy: Optional["policy.GenericPolicyId"]
    _signature: str
    _is_signed: bool
    _sha: Optional[int]
    _rsa: Optional[int]
    _use_algorithm: str

    def __init__(
        self, file_path_or_xml: Union[str, "etree.Element"], cert_path: str, pwsd_: str = ""
    ) -> None:
        """Initialize."""

        for path in [file_path_or_xml, cert_path]:
            if isinstance(path, str):
                if not os.path.exists(path):
                    raise Exception("%s doesn't exists!" % path)

        self._root = (
            etree.parse(file_path_or_xml).getroot()
            if isinstance(file_path_or_xml, str)
            else file_path_or_xml
        )
        self._cert_path = cert_path
        self._pass = pwsd_
        self._policy_list = [
            "http://www.facturae.gob.es/politica_de_firma_formato_facturae/politica_de_firma_formato_facturae_v3_1.pdf",
            "Politica de Firma FacturaE v3.1",
            "xmlsig.constants.TransformSha1",
        ]
        self._certificate = None
        self._policy = None
        self._signature = ""
        self._is_signed = False
        self._use_algorithm = "sha256"
        self._sha = None
        self._rsa = None

    def set_password(self, pwds_: str = "") -> None:
        """Set password."""

        self._pass = pwds_

    def _load_certificate(self) -> bool:
        """Load certificate."""

        if not self._pass:
            LOGGER.warning("Password is empty!")
            return False
        try:

            with open(self._cert_path, "rb") as cert_file:
                self._certificate = tuple(
                    pkcs12.load_key_and_certificates(
                        cert_file.read(), self._pass.encode(), backends.default_backend()
                    )
                )
        except Exception as error:
            LOGGER.warning("Error loading certificate: %s", str(error))
            return False

        return True

    def _load_policy(self) -> bool:
        """Load policy."""

        if not self._policy_list:
            LOGGER.warning("Policy is empty!")
            return False

        custom_policy: List[Any] = list(self._policy_list)
        if len(custom_policy) == 1:
            custom_policy += ["Policy description"]
        custom_policy.append(self._sha)

        try:
            self._policy = policy.GenericPolicyId(*custom_policy)
        except Exception as error:
            LOGGER.warning("Error loading policies: %s", str(error))
            return False

        return True

    def _load_signature(self) -> bool:
        """Load signature."""

        try:
            unique_id = utils.get_unique_id()
            signature_id = "Signature-%s" % unique_id
            qualifing_id = "QualifyingProperties-%s" % unique_id
            reference_id = "Reference-%s" % unique_id

            self._signature = xmlsig.template.create(
                xmlsig.constants.TransformInclC14N, self._rsa, signature_id
            )

            reference = xmlsig.template.add_reference(
                self._signature, self._sha, uri="", name="Reference-%s" % reference_id
            )
            xmlsig.template.add_transform(reference, xmlsig.constants.TransformEnveloped)

            xmlsig.template.add_reference(
                self._signature,
                self._sha,
                uri="#KeyInfoId-%s" % signature_id,
                name="ReferenceKeyInfo",
            )
            xmlsig.template.add_reference(
                self._signature,
                self._sha,
                uri="#SignedProperties-%s" % signature_id,
                uri_type="http://uri.etsi.org/01903#SignedProperties",
            )
            key_info = xmlsig.template.ensure_key_info(
                self._signature, name="KeyInfoId-%s" % signature_id
            )

            data = xmlsig.template.add_x509_data(key_info)

            xmlsig.template.x509_data_add_certificate(data)

            # serial = xmlsig.template.x509_data_add_issuer_serial(data)
            # xmlsig.template.x509_issuer_serial_add_issuer_name(serial)
            # xmlsig.template.x509_issuer_serial_add_serial_number(serial)

            xmlsig.template.add_key_value(key_info)

            qualifying = template.create_qualifying_properties(
                self._signature, name=qualifing_id, etsi="xades"
            )
            utils.ensure_id(qualifying)

            props = template.create_signed_properties(
                qualifying, name="SignedProperties-%s" % signature_id
            )

            signed_do = template.ensure_signed_data_object_properties(props)

            template.add_data_object_format(
                signed_do,
                "#%s" % reference_id,
                description="",
                mime_type="application/xml",
                encoding="UTF-8",
            )

        except Exception as error:
            LOGGER.warning("Error loading signature: %s", str(error))
            return False

        return True

    def set_policy(self, policy_list: List[str]) -> None:
        """Set policy."""

        self._policy_list = policy_list

    def set_algorithm(self, name: str = "sha1") -> None:
        """Set algorithm type."""

        self._use_algorithm = name.lower()

    def sign(self) -> bool:
        """Sign data."""

        self._sha = None
        self._rsa = None

        if self._use_algorithm == "sha1":
            self._sha = xmlsig.constants.TransformSha1
            self._rsa = xmlsig.constants.TransformRsaSha1
        elif self._use_algorithm == "sha256":
            self._sha = xmlsig.constants.TransformSha256
            self._rsa = xmlsig.constants.TransformRsaSha256
        elif self._use_algorithm == "sha512":
            self._sha = xmlsig.constants.TransformSha512
            self._rsa = xmlsig.constants.TransformRsaSha512
        else:
            LOGGER.warning("UNKNOWN algorithm %s", self._use_algorithm)
            return False

        if not self._load_certificate():
            LOGGER.warning("certificate not loaded!")
            return False

        if not self._load_policy():
            LOGGER.warning("policy not loaded!")
            return False

        if not self._load_signature():
            LOGGER.warning("signature not loaded!")
            return False

        self._root.append(self._signature)

        try:
            if self._policy is None:
                raise Exception("Policy is empty!")
            context = XAdESContext(self._policy)
            if self._certificate is None:
                raise Exception("Certificate is empty!")
            context.load_pkcs12(self._certificate)

            LOGGER.warning("Starting signing")
            # LOGGER.info(
            #    "Policy : %s --> %s --> %s"
            #    % (self._policy, self._policy.identifier, context.policies)
            # )

            # LOGGER.info("Certificate : %s" % str(self._certificate))
            # LOGGER.info("Signature : %s" % self._signature)

            context.sign(self._signature)
            LOGGER.warning("Signing finished sucefully!")
        except Exception as error:
            LOGGER.warning("Error signing: %s" % str(error))
            return False

        self._is_signed = True
        return True

    def signature_value(self) -> str:
        """Return SisgnatureValue field value."""

        if not self._is_signed:
            LOGGER.warning("xml is not signed yet")
            return ""

        for child in self._root:
            if str(child.get("Id")).startswith("Signature"):
                for child_elem in child:
                    if "SignatureValue" in child_elem.tag:
                        return child_elem.text

        LOGGER.warning("SignatureValue not found!")
        return ""

    def save_file(self, file_path: str) -> bool:
        """Save signed xml into a file."""

        if not file_path:
            LOGGER.warning("file_path is empty!")
        elif not self._is_signed:
            LOGGER.warning("the xml is not signed")
        else:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)

                element_tree = etree.ElementTree(self._root)
                element_tree.write(
                    file_path, pretty_print=False, xml_declaration=True, encoding="UTF-8"
                )
                return True
            except Exception as error:
                LOGGER.warning("Error saving file %s: %s", file_path, str(error))

        return False
