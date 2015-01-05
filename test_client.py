__author__ = 'tr1b2669'
from unittest import TestCase
import socket
import struct
import sockethandler
import time
import threading
import messages
class TestClient(TestCase):
    def test_asd_connection(self, name):
        s = socket.socket()
        host = socket.gethostname()
        port = 9990
        try:
            s.connect((host, port))
        except Exception, e:
            assert('something\'s wrong with %s:%d. Exception type is %s' % (host, port,`e`))
        msg = '{"request": "CONNECT", "seq_id": 1234,"body": {"username": "'+name + '"}}'
        msg = struct.pack('>I', len(msg)) + msg
        s.sendall(msg)

        msg = '{"request": "FINDMATCH", "seq_id": 1234,"body": {"mode": "match"}}'
        msg = struct.pack('>I', len(msg)) + msg
        s.sendall(msg)
        while True:
            time.sleep(1)
            pass
    # def test_connect_message(self):
    #     my_socket = self.test_raw_connection()

    def test_asd_connection2(self):
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



class ThreadedClient(threading.Thread, sockethandler.CommonSocketHandler):
    def __init__(self,name):
        threading.Thread.__init__(self)
        sockethandler.CommonSocketHandler.__init__(self, None)
        self.name = name

    def run(self):
        self.socket = socket.socket()
        host = socket.gethostname()
        port = 9991
        try:
            self.socket.connect((host, port))
        except Exception, e:
            assert('something\'s wrong with %s:%d. Exception type is %s' % (host, port,`e`))
        msg = messages.CONNECT()
        msg.body.username = self.name
        self.send_message(msg)
        message = self.receive_msg()
        if isinstance(message, messages.RSPOK):
            msg = messages.FINDMATCH()
            msg.body.mode = "match"
            self.send_message(msg)
            msg=self.receive_msg()
            if isinstance(msg,messages.RSPMATCHSTART):
                print 'match starting'
                if msg.body.first_player:
                    msg = messages.MOVE()
                    msg.body.move = ((8, 4), (6, 4))
                    self.send_message(msg)
                    msg=self.receive_msg()
        else:
            print 'not unique name' + message.__class__.__name__


        while True:
            time.sleep(1)
            pass
