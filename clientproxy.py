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

    def run(self):
        while True:
            try:
                data = self.receive_msg()
                if data:
                    self.logger.info('Received')
                    self.logger.debug( "%d bytes: '%s'" % (len(data), data))
                    self.process_message(data)
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
            self.currentState.handle(self)
            time.sleep(1)

    def process_message(self, data):
        if data:
            self.logger.info('data received: ' + data)
            message = util.parse(data)
            if message:
                self.message = message
                next_state = self.currentState.next(self)
                self.logger.info(
                    'changing state from ' + self.currentState.__class__.__name__ + ' to ' + next_state.__class__.__name__)
                self.currentState = next_state
            else:
                self.logger.info(' message is None')
        else:
            self.logger.info(' data is None')

