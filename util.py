__author__ = 'tr1b2669'
import re
import json
import messages


def parse(raw_message):
    split_value = re.split('(\{.*\})', str(raw_message))
    first_part = split_value[0].split()
    json_part = split_value[1]
    message_class = getattr(messages, first_part[0])
    message_instance = message_class([first_part[1], json.loads(json_part)])
    return message_instance

