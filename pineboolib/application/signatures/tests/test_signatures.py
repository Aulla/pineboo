"""Test_signatures module."""

import unittest
from pineboolib.qsa import qsa
from pineboolib.loader.main import init_testing, finish_testing
from . import fixture_path
import os


class TestSignatures(unittest.TestCase):
    """TestSignatures class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_qr(self) -> None:
        """test pdf_qr."""

        test_file = fixture_path("test.pdf")
        dest_file = fixture_path("test_result.pdf")

        self.assertTrue(os.path.exists(test_file))
        if os.path.exists(dest_file):
            os.remove(dest_file)

        obj_ = qsa.PdfQr(test_file)
        obj_.set_size(5)
        obj_.set_extension("PNG")
        obj_.set_dpi()
        obj_.set_text("textoa", "textob")
        obj_.set_font("Arial", 8)
        obj_.set_position(100, 100)
        self.assertTrue(obj_.sign(True))
        self.assertTrue(obj_.save_file(dest_file))
        self.assertTrue(obj_.get_qr())

    def test_xml_digest(self) -> None:
        """Test xml_digest."""

        xml_unsigned_file = fixture_path("xml_sin.xml")
        xml_signed_file = fixture_path("xml_con.xml")
        if os.path.exists(xml_signed_file):
            os.remove(xml_signed_file)

        cert_file = fixture_path("cert.p12")

        obj_ = qsa.XmlDigest(xml_unsigned_file, cert_file)
        obj_.set_password("123456")
        obj_.set_policy(
            [
                "http://www.facturae.gob.es/politica_de_firma_formato_facturae/politica_de_firma_formato_facturae_v3_1.pdf",
                "Politica de Firma FacturaE v3.1",
            ]
        )
        obj_.set_algorithm("sha1")
        self.assertTrue(obj_.sign())
        self.assertTrue(obj_._policy is not None)
        self.assertTrue(obj_.signature_value())

    """     def test_pdf_digest(self) -> None:
        """ "Test pdf_digest." """

        pdf_unsigned_file = fixture_path("pdf_unsigned.pdf")
        pdf_signed_file = fixture_path("pdf_signed.pdf")
        if os.path.exists(pdf_signed_file):
            os.remove(pdf_signed_file)

        cert_file = fixture_path("cert.p12")

        obj_ = qsa.PdfDigest(pdf_unsigned_file, cert_file)
        obj_.set_password("123456")
        obj_.set_stamp("stamp test")
        self.assertTrue(obj_.sign(pdf_signed_file))
        self.assertTrue(os.path.exists(pdf_signed_file))

        self.assertTrue(os.path.exists(pdf_signed_file)) """

    def test_xml_digest_512(self) -> None:
        """Test xml_digest."""

        xml_unsigned_file = fixture_path("xml_sin.xml")
        xml_signed_file = fixture_path("xml_con.xml")
        if os.path.exists(xml_signed_file):
            os.remove(xml_signed_file)

        cert_file = fixture_path("cert.p12")

        obj_ = qsa.XmlDigest(xml_unsigned_file, cert_file)
        obj_.set_password("123456")
        obj_.set_policy(
            [
                "http://www.facturae.gob.es/politica_de_firma_formato_facturae/politica_de_firma_formato_facturae_v3_1.pdf",
                "Politica de Firma FacturaE v3.1",
            ]
        )
        obj_.set_algorithm("sha512")
        self.assertTrue(obj_.sign())
        self.assertTrue(obj_.signature_value())

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
