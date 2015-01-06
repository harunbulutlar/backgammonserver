__author__ = 'tr1b2669'
from statemachine import ThreadedStateMachine, FindingMatch
import Queue
import messages
import errno
import time
import socket
import sockethandler
import threading
import util


class ClientProxy(ThreadedStateMachine, sockethandler.CommonSocketHandler):
    proxies_lock = threading.Lock()
    partner_lock = threading.Lock()

    def __init__(self, client_ip, client_port, client_socket, dispatcher):
        ThreadedStateMachine.__init__(self)
        sockethandler.CommonSocketHandler.__init__(self, client_socket)
        self.ip = client_ip
        self.port = client_port
        self.socket.setblocking(0)
        self.message = messages.EMPTY()
        self.dispatcher = dispatcher
        self.partner_name = None
        self.is_white = False
        self.board = {}
        self.wrong_move_flag = False

    def internal_run(self):
        try:
            message = self.receive_msg()
            if message:
                self.process_message(message)
            else:
                self.logger.debug('connection closed')
                self.socket.close()
                self.done = True
        except socket.error, e:
            if e.args[0] == errno.EWOULDBLOCK:
                self.logger.debug('No data yet')
            else:
                print e
                self.done = True
        time.sleep(1)

    def message_received(self, message):
        self.process_message(message)

    def process_message(self, message):
        if not message:
            self.logger.info('message is None')
            return

        self.logger.info('message received: ' + message.__class__.__name__)
        if isinstance(message, messages.RSPMessage):
            self.send_message(message)
        self.change_state(message)

    def change_state(self, message):
        self.message = message
        next_state = self.currentState.next()
        self.logger.info(
            'changing state from ' + self.currentState.__class__.__name__ + ' to ' + next_state.__class__.__name__)
        self.currentState = next_state
