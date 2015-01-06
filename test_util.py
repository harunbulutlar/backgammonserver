from unittest import TestCase
import util
import messages

__author__ = 'tr1b2669'


class TestParser(TestCase):
    def test_connect_parse(self):
        message = util.parse('{"request": "CONNECT", "seq_id": 1234,"body": {"username": "Harun"}}')

        self.assertTrue(isinstance(message, messages.CONNECT))

    def test_connect_parse_n(self):
        message = util.parse('{"request": "CONNECT", "seq_id": 1234,"body": {}}')

        self.assertFalse(isinstance(message, messages.CONNECT))

    def test_connect_parse_n2(self):
        message = util.parse('{"request": "CONNECT", "body": {"username": "Harun"}}')

        self.assertFalse(isinstance(message, messages.CONNECT))

    def test_connect_parse_n3(self):
        message = util.parse('{"request": "CONNECT",  "seq_id": 1234, "body": {"harun": "Harun"}}')

        self.assertFalse(isinstance(message, messages.CONNECT))

    def test_parse_invalid_json(self):
        message = util.parse('   wrong message ')

        self.assertFalse(isinstance(message, messages.CONNECT))


