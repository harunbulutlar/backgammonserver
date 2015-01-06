__author__ = 'tr1b2669'
from unittest import TestCase
import socket
import sockethandler
import time
import threading
import messages


class TestClient(TestCase):
    def test_connection(self):
        clients = []
        for i in range(0, 7):
            clients.append(ThreadedClient("Client---->" + str(i)))
        for client in clients:
            client.start()
        for client in clients:
            client.join()

    def test_asd_connection3(self):
        clients = []
        for i in range(8, 10):
            clients.append(ThreadedClient("Client---->" + str(i)))
        for client in clients:
            client.start()
        for client in clients:
            client.join()
    def test_asd_connection4(self):
        clients = []
        for i in range(8, 9):
            clients.append(ThreadedClient("Client---->" + str(i)))
        for client in clients:
            client.start()
        for client in clients:
            client.join()


class ThreadedClient(threading.Thread, sockethandler.CommonSocketHandler):
    def __init__(self, name):
        threading.Thread.__init__(self)
        sockethandler.CommonSocketHandler.__init__(self, None)
        self.name = name
        self.msg = None

    def run(self):
        self.socket = socket.socket()
        host = socket.gethostname()
        port = 9991
        try:
            self.socket.connect((host, port))
        except Exception, e:
            assert ('something\'s wrong with %s:%d. Exception type is %s' % (host, port, repr(e)))
        self.msg = messages.CONNECT()
        self.msg.body.username = self.name
        self.send_message(self.msg)
        message = self.receive_msg()
        if isinstance(message, messages.RSPOK):
            self.msg = messages.FINDMATCH()
            self.msg.body.mode = "match"
            self.send_message(self.msg)

            while True:
                self.msg = self.receive_msg()
                if isinstance(self.msg, messages.RSPFIRST):
                    self.msg = messages.MOVE()
                    self.msg.body.move = ((8, 4), (6, 4))
                    self.send_message(self.msg)
                if isinstance(self.msg, messages.RSPSECOND):
                    self.msg = self.receive_msg()
                    if isinstance(self.msg, messages.RSPMOVE):
                        self.send_message(messages.WRONGMOVE())
                        print self.msg.deserialize()

        else:
            print 'not unique name' + message.__class__.__name__

        while True:
            time.sleep(1)
            pass
