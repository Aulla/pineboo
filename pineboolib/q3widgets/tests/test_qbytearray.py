"""Test_qbytearray module."""

import unittest


class TestQByteArray(unittest.TestCase):
    """TestQByteArray Class."""

    def test_all(self) -> None:
        """Test qbytearray."""
        import base64
        from pineboolib.qsa import qsa

        text_64 = base64.b64encode("hola holita!".encode("UTF-8"))

        ba = qsa.QByteArray(len(text_64))
        i = 0
        for s in text_64:
            ba.set(i, s)
            i += 1

        ba2 = qsa.QByteArray(ba.fromBase64())

        self.assertEqual(ba.data(), text_64)
        self.assertEqual(ba2.data(), b"hola holita!")
        self.assertEqual(chr(ba2.get(3)), "a")
