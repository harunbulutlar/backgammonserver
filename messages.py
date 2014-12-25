__author__ = 'tr1b2669'

import json


class Message:
    def __init__(self, variables):
        self.sequence_id = variables[0]
        self.__dict__ = variables[1]

    # def __str__(self):
    #     return self.type
    #
    # def __cmp__(self, other):
    #     return cmp(self.type, other.type)
    #
    # # Necessary when __cmp__ or __eq__ is defined
    # # in order to make this class usable as a
    # # dictionary key:
    # def __hash__(self):
    #     return hash(self.type)


class CONNECT(Message): pass


class MOVE(Message): pass


class EMPTY(Message): pass

