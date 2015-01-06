__author__ = 'tr1b2669'

import json
import random

initial_setup = {1: ('WHITE', 2), 6: ('BLACK', 5),
                 8: ('BLACK', 3), 12: ('WHITE', 5),
                 13: ('BLACK', 5), 17: ('WHITE', 3),
                 19: ('WHITE', 5), 24: ('BLACK', 2)}


class Body:
    def __init__(self):
        pass

    def supports_json(self):
        return self.__dict__


def json_handler(obj):
    if hasattr(obj, 'supports_json'):
        return obj.supports_json()
    else:
        return None


class Message:
    def __init__(self):
        self.seq_id = 0
        self.request = self.__class__.__name__
        self.body = None
        pass

    def validate_message(self, json_message):
        if len(self.__dict__) != len(json_message):
            return False
        is_valid = True
        for var_name, value in json_message.iteritems():
            if var_name == 'body' and self.body is not None and not self.validate_body(value):
                is_valid = False
                break
            elif var_name in self.__dict__:
                self.__dict__[var_name] = value
            else:
                is_valid = False
                break
        return is_valid

    def validate_body(self, value):
        body_is_valid = True
        if len(self.body.__dict__) != len(value):
            return False

        for body_var_name, body_var_value in value.iteritems():
            if body_var_name in self.body.__dict__:
                self.body.__dict__[body_var_name] = body_var_value
            else:
                body_is_valid = False
                break
        return body_is_valid

    def supports_json(self):
        return self.__dict__

    def deserialize(self):
        return json.dumps(self, default=json_handler)


class MessageWithBody(Message):
    def __init__(self):
        Message.__init__(self)
        self.body = Body()
        pass


class EMPTY(Message):
    pass


class CONNECT(MessageWithBody):
    def __init__(self):
        MessageWithBody.__init__(self)
        self.body.username = ''


class DISCONNECT(Message):
    pass


class FINDMATCH(MessageWithBody):
    def __init__(self):
        MessageWithBody.__init__(self)
        self.body.mode = ''


class MOVE(MessageWithBody):
    def __init__(self):
        MessageWithBody.__init__(self)
        self.body.wrong_move = False
        self.body.board = []
        self.body.move = []


class PING(Message):
    pass


class RSPOK(Message):
    pass


class RSPINVALID(Message):
    pass


class RSPERROR(Message):
    pass


class RSPMATCHSTART(MessageWithBody):
    def __init__(self):
        MessageWithBody.__init__(self)
        self.body.opponent = ''
        self.body.dice = ''
        self.body.first_player = 'HARUN'
        self.body.is_white = False
        self.body.board = initial_setup

    def randomize(self):
        self.body.first_player = bool(random.getrandbits(1))
        self.body.is_white = bool(random.getrandbits(1))
        self.body.dice = (random.randint(0, 6), random.randint(0, 6))


class RSPMATCHOVER(MessageWithBody):
    def __init__(self):
        MessageWithBody.__init__(self)
        self.body.opponent = ''
        self.body.dice = ''
        self.body.first_player = False
        self.body.is_white = False
        self.body.board = []


class RSPNOMATCH(Message):
    pass


class RSPMOVE(MOVE):
    def __init__(self):
        MOVE.__init__(self)
        self.body.dice = []
