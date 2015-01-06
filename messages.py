__author__ = 'tr1b2669'

import json
import random

initial_setup = {}
for i in range(1, 25):
    initial_setup[i] = ['EMPTY', 0]
initial_setup[1] = ['WHITE', 2]
initial_setup[6] = ['BLACK', 5]
initial_setup[8] = ['BLACK', 3]
initial_setup[12] = ['WHITE', 5]
initial_setup[13] = ['BLACK', 5]
initial_setup[17] = ['WHITE', 3]
initial_setup[19] = ['WHITE', 5]
initial_setup[24] = ['BLACK', 2]


class Body:
    def __init__(self):
        pass

    def supports_json(self):
        return self.__dict__

    def validate(self, value):
        is_valid = False
        if len(self.__dict__) != len(value):
            return False

        for var_name, var_value in value.iteritems():
            if var_name in self.__dict__:
                self.__dict__[var_name] = var_value
            else:
                break
        else:
            is_valid = True
        return is_valid


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
        is_valid = False
        for var_name, value in json_message.iteritems():
            if var_name == 'body' and self.body is not None:
                if not self.body.validate(value):
                    break
            elif var_name in self.__dict__:
                self.__dict__[var_name.encode('utf-8')] = value
            else:
                break
        else:
            is_valid = True
        return is_valid

    def supports_json(self):
        return self.__dict__

    def deserialize(self):
        return json.dumps(self, default=json_handler)


class InterThreadMessage():
    def __init__(self):
        self.message = EMPTY()
        self.receiver_name = None
        self.sender_name = None



class RSPMessage(Message):
    pass


class RSPMessageWithBody(RSPMessage):
    def __init__(self):
        RSPMessage.__init__(self)
        self.body = Body()
        pass


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


class WRONGMOVE(Message):
    pass


class MOVE(MessageWithBody):
    def __init__(self):
        MessageWithBody.__init__(self)
        self.body.move = []


class PING(Message):
    pass


class RSPOK(RSPMessage):
    pass


class RSPINVALID(RSPMessage):
    pass


class RSPERROR(RSPMessage):
    pass


class RSPOPDISCON(RSPMessage):
    pass


class RSPTIMEOUT(RSPMessage):
    pass

class RSPFIRST(RSPMessageWithBody):
    def __init__(self):
        RSPMessageWithBody.__init__(self)
        self.body.opponent = ''
        self.body.dice = (random.randint(0, 6), random.randint(0, 6))
        self.body.is_white = True
        self.body.board = initial_setup

class RSPSECOND(RSPFIRST):
    def __init__(self):
        RSPFIRST.__init__(self)
        self.body.is_white = False



class RSPMATCHOVER(RSPMessageWithBody):
    def __init__(self):
        RSPMessageWithBody.__init__(self)
        self.body.opponent = ''
        self.body.dice = ''
        self.body.first_player = False
        self.body.is_white = False
        self.body.board = []


class RSPNOMATCH(RSPMessage):
    pass


class RSPMOVE(RSPMessageWithBody):
    def __init__(self):
        RSPMessageWithBody.__init__(self)
        self.body.board = []
        self.body.move = []
        self.body.dice = (random.randrange(0, 6), random.randrange(0, 6))

    def update_from_move(self, move):
        self.body.move = move.body.move
        self.randomize()

    def randomize(self):
        self.body.dice = (random.randint(0, 6), random.randint(0, 6))

class RSPWRONGMOVE(RSPMessageWithBody):
    def __init__(self):
        RSPMessageWithBody.__init__(self)
        self.body.board = []



class RSPDICE(RSPMessageWithBody):
    def __init__(self):
        RSPMessageWithBody.__init__(self)
        self.body.dice = ()