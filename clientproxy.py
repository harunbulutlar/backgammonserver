__author__ = 'tr1b2669'
from statemachine import ThreadedStateMachine
import Queue
import select




class ClientProxy(ThreadedStateMachine):
    def __init__(self, client_ip, client_port, client_socket):
        ThreadedStateMachine.__init__(self)
        self.ip = client_ip
        self.port = client_port
        self.socket = client_socket
        self.msgQueue = Queue
        self.message = messages.EMPTY()
        print "[+] New thread started for " + self.ip + ":" + str(client_port)

    def __run__(self):
        inputs = [self.socket, self.msgQueue]
        while True:
            input_ready, output_ready, except_ready = select.select(inputs, [], [], 0)
            for ready in input_ready:

                if ready == self.socket:
                    # parse message from raw data
                    data = self.socket.recv(1024)

                elif ready == self.msgQueue:
                    pass
                    # handle incoming messages from another client proxy



