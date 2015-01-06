__author__ = 'tr1b2669'
from statemachine import ThreadedStateMachine
import messages
import errno
import socket
import sockethandler
import threading


class ClientProxy(ThreadedStateMachine, sockethandler.CommonSocketHandler):

    def __init__(self, client_ip, client_port, client_socket, dispatcher):
        ThreadedStateMachine.__init__(self)
        sockethandler.CommonSocketHandler.__init__(self, client_socket)
        self.ip = client_ip
        self.port = client_port
        self.socket.setblocking(0)
        self.message = messages.EMPTY()
        self.partner_name = None
        self.board_info = None
        self.wrong_move_flag = False
        self.dispatcher = dispatcher

    def internal_run(self):
        try:
            message = self.receive_msg()
            if message:
                self.process_message(message)
            else:
                self.logger.debug('connection closed')
                self.socket.close()
                self.currentState.disconnected()
                self.done = True
        except socket.error, e:
            if e.args[0] == errno.EWOULDBLOCK:
                self.logger.debug('No data yet')
            else:
                print e
                self.done = True
                self.currentState.disconnected()

    def message_received(self, message):
        self.process_message(message)

    def process_message(self, message):
        if not message:
            self.logger.info('message is None')
            return

        self.logger.info('message received: ' + message.__class__.__name__)
        self.change_state(message)
        if isinstance(message, messages.RSPMessage):
            try:
                self.send_message(message)
            except socket.error, e:
                print e
                self.currentState.disconnected()
                self.done = True
        self.currentState.handle()
    def send_message_to_partner(self,message):
        internal_message = messages.InterThreadMessage()
        internal_message.sender_name = self.name
        internal_message.receiver_name = self.partner_name
        internal_message.message = message
        self.dispatcher.queue_message(internal_message)

    def change_state(self, message):
        self.message = message
        next_state = self.currentState.next()
        self.logger.info(
            'changing state from ' + self.currentState.__class__.__name__ + ' to ' + next_state.__class__.__name__)
        self.currentState = next_state
