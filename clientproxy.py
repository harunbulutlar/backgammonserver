__author__ = 'tr1b2669'
from statemachine import ThreadedStateMachine
import Queue
import messages
import util
import errno
import time
import socket
import sockethandler


class ClientProxy(ThreadedStateMachine, sockethandler.CommonSocketHandler):
    def __init__(self, client_ip, client_port, client_socket, proxies):
        ThreadedStateMachine.__init__(self)
        sockethandler.CommonSocketHandler.__init__(self, client_socket)
        self.ip = client_ip
        self.port = client_port
        self.socket.setblocking(0)
        self.msgQueue = Queue.Queue()
        self.message = messages.EMPTY()
        self.proxies = proxies
        self.matching_proxy = None
        self.is_white = False
        self.board = {}
        self.wrong_move_flag = False

    def run(self):
        while True:
            try:
                message = self.receive_msg()
                if message:

                    self.process_message(message)
                else:
                    self.logger.debug('connection closed')
                    self.socket.close()
                    break
            except socket.error, e:
                if e.args[0] == errno.EWOULDBLOCK:
                    self.logger.debug('No data yet')
                else:
                    print e
                    break

            try:
                message = self.msgQueue.get_nowait()
                self.process_message(message)
            except Queue.Empty:
                self.logger.debug('Queue empty')
                # short delay, no tight loops
            self.currentState.handle()
            time.sleep(1)

    def process_message(self, message):
        if not message:
            self.logger.info('message is None')
            return
        self.change_state(message)

        if isinstance(message, messages.RSPMessage):
            self.logger.info('message received: ' + message.__class__.__name__)
            self.send_message(message)

    def change_state(self, message):
        self.message = message
        next_state = self.currentState.next()
        self.logger.info(
            'changing state from ' + self.currentState.__class__.__name__ + ' to ' + next_state.__class__.__name__)
        self.currentState = next_state
