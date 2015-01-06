from unittest import TestCase
from messages import *
import random
import util
initial_setup = {1: ('WHITE', 2), 6: ('BLACK', 5),
                 8: ('BLACK', 3), 12: ('WHITE', 5),
                 13: ('BLACK', 5), 17: ('WHITE', 3),
                 19: ('WHITE', 5), 24: ('BLACK', 2)}
__author__ = 'tr1b2669'


class TestMessage(TestCase):
    def test_validate_message(self):
        self.fail()

    def test_validate_body(self):
        self.fail()

    def test_support_json(self):

        match_start = RSPMATCHSTART()
        match_start.body.first_player = bool(random.getrandbits(1))
        match_start.body.is_white = bool(random.getrandbits(1))
        match_start.body.dice = (random.randint(0, 6), random.randint(0, 6))
        match_start.body.board = initial_setup
        msg = match_start.deserialize()
        parsed_again_message = util.parse(msg)
        self.assertTrue(isinstance(parsed_again_message, RSPMATCHSTART))
        print msg
        self.assertIsNotNone(msg)

    def test_deserialize(self):
        self.fail()