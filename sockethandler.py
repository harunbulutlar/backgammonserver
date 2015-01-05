__author__ = 'tr1b2669'
import socket
import struct
import util

class CommonSocketHandler(util.LogMixin):

    def __init__(self, common_socket):
        util.LogMixin.__init__(self)
        self.socket = common_socket

    def receive_msg(self):
        # Read message length and unpack it into an integer
        raw_msg_len = self.receive_all(4)
        if not raw_msg_len:
            return None
        msg_len = struct.unpack('>I', raw_msg_len)[0]
        # Read the message data
        data = self.receive_all(msg_len)
        self.logger.info('Received')
        self.logger.info("%d bytes: '%s'" % (len(data), data))
        return util.parse(data)

    def receive_all(self, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = ''
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def send_message(self, message):
        msg = message.deserialize()
        msg = struct.pack('>I', len(msg)) + msg
        self.socket.sendall(msg)