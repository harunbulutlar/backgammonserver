__author__ = 'tr1b2669'
import json
import messages
import logging
import sys
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(thread)d\%(threadName)s: %(message)s")

ch.setFormatter(formatter)


def parse(raw_message):
    if raw_message is None:
        return None
    try:
        json_message = json.loads(raw_message)
    except ValueError:
        return None
    if 'request' in json_message:
        message_class = getattr(messages, json_message['request'])
        if message_class:
            message = message_class()
            if message.validate_message(json_message):
                return message
    return None


class LogMixin(object):
    def __init__(self):
        self.name = '.'.join([__name__, self.__class__.__name__])
        self.logger = logging.getLogger(self.name)
        for handler in self.logger.handlers:
            if handler == ch:
                break
        else:
            self.logger.addHandler(ch)
        self.logger.setLevel(logging.DEBUG)
