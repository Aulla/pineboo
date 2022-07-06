"""pdf_digest module."""

from pineboolib.core.utils import logging
from pineboolib.core import fonts, images as core_images
import os
from pyhanko import stamp  # type: ignore[import]
from pyhanko.pdf_utils import text, images  # type: ignore[import]
from pyhanko.pdf_utils.font import opentype  # type: ignore[import]
from pyhanko.sign import signers, fields  # type: ignore[import]
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter  # type: ignore[import]
from pyhanko.sign.fields import SigSeedSubFilter  # type: ignore[import]
from pyhanko_certvalidator import ValidationContext  # type: ignore[import]

from typing import Tuple, Dict, Any

LOGGER = logging.get_logger(__name__)


class PdfDigest:
    """PdfDigest class."""

    _pass: str
    _certificate: Any
    _cert_path: str
    _unsigned_pdf_path: str
    _signer: "signers.PdfSigner"
    _writer: "IncrementalPdfFileWriter"
    _stamp: Dict[str, Any]

    def __init__(self, file_path: str, cert_path: str, pass_: str = "") -> None:
        """Initialize."""
        self._cert_path = cert_path
        self._certificate = None
        self._pass = pass_
        self._unsigned_pdf_path = file_path
        self._writer = None
        self._signer = None
        self._stamp = {}

    def set_password(self, pass_: str = "") -> None:
        """Set password."""

        self._pass = pass_

    def _load_certificate(self) -> bool:
        """Load certificate."""

        if not self._pass:
            LOGGER.warning("Password is empty!")
            return False
        try:
            LOGGER.warning("Loading certificate %s with psw %s" % (self._cert_path, self._pass))
            self._certificate = signers.SimpleSigner.load_pkcs12(
                pfx_file=self._cert_path, passphrase=self._pass.encode()
            )
        except Exception as error:
            LOGGER.warning("Error loading certificate: %s", str(error))
            return False

        return True

    def _load_signature(self) -> bool:
        """Load signature."""

    def _load_unsigned_document(self, load_writer: bool = False) -> bool:
        """Load unsigned document."""

        if not os.path.exists(self._unsigned_pdf_path):
            raise Exception("%s not exits!" % self._unsigned_pdf_path)

        return True

    def set_stamp(
        self,
        label_text: str,
        url: str = "",
        coords: Tuple[int, int, int, int] = (200, 50, 400, 110),
        background_image_path: str = os.path.join(
            os.path.dirname(core_images.__file__), "icons", "signed_stamp.png"
        ),
        font: str = os.path.join(
            os.path.dirname(fonts.__file__), "noto_sans", "NotoSans-Regular.ttf"
        ),
    ) -> bool:
        """Generate stamp."""

        self._stamp = {
            "text": label_text,
            "coords": coords,
            "background": background_image_path,
            "font": font,
            "url": url,
        }

        return True

    def signature_value(self) -> str:
        """Return SisgnatureValue field value."""

        pass

    def sign(self, dest_file_path: str = "") -> bool:
        """Sign file."""
        self._load_certificate()

        if dest_file_path and os.path.exists(dest_file_path):
            LOGGER.warning("deleting %s" % dest_file_path)
            os.remove(dest_file_path)

        with open(self._unsigned_pdf_path, "rb") as inf:
            self._writer = IncrementalPdfFileWriter(inf)
            if self._stamp:
                fields.append_signature_field(
                    self._writer,
                    sig_field_spec=fields.SigFieldSpec("Signature1", box=self._stamp["coords"]),
                )

            signature_meta = signers.PdfSignatureMetadata(
                field_name="Signature1",
                md_algorithm="sha256",
                # Mark the signature as a PAdES signature
                subfilter=SigSeedSubFilter.PADES,
                # We'll also need a validation context
                # to fetch & embed revocation info.
                validation_context=ValidationContext(allow_fetching=True),
                # Embed relevant OCSP responses / CRLs (PAdES-LT)
                embed_validation_info=False,
                # Tell pyHanko to put in an extra DocumentTimeStamp
                # to kick off the PAdES-LTA timestamp chain.
                use_pades_lta=False,  # True para timestamp
            )

            kwargs = {"signature_meta": signature_meta, "signer": self._certificate}

            if self._stamp:

                if not os.path.exists(self._stamp["font"]):
                    LOGGER.warning("font file %s not found!" % self._stamp["font"])

                if self._stamp["url"]:
                    LOGGER.warning("QR_MODE!")
                    kwargs["stamp_style"] = stamp.QRStampStyle(
                        stamp_text="%(label)s.\nSigned by:%(signer)s",
                        text_box_style=text.TextBoxStyle(
                            font=opentype.GlyphAccumulatorFactory(self._stamp["font"])
                        ),
                    )

                else:
                    LOGGER.warning("IMAGE_MODE!")
                    kwargs["stamp_style"] = stamp.TextStampStyle(
                        stamp_text="%(label)s.\nSigned by:%(signer)s",
                        text_box_style=text.TextBoxStyle(
                            font=opentype.GlyphAccumulatorFactory(self._stamp["font"])
                        ),
                        background=images.PdfImage(self._stamp["background"]),
                    )

                self._signer = signers.PdfSigner(**kwargs)

            pdf_signer = signers.PdfSigner(
                signature_meta, signer=self._certificate, stamp_style=kwargs["stamp_style"]
            )
            if dest_file_path:
                with open(dest_file_path, "wb") as outf:
                    dict_params = {
                        "url": self._stamp["url"] if "url" in self._stamp.keys() else "",
                        "label": self._stamp["text"] if "text" in self._stamp.keys() else "",
                    }
                    pdf_signer.sign_pdf(
                        self._writer, output=outf, appearance_text_params=dict_params
                    )

            return True
