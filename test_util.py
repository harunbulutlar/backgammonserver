from unittest import TestCase
import util
import messages

__author__ = 'tr1b2669'


class TestClientProxy(TestCase):
    def test_parse(self):
        message = util.parse('CONNECT 1234 {"harun":"bulutlar"}')

        self.assertTrue(isinstance(message, messages.CONNECT))

        # TODO add negative test cases for parsing