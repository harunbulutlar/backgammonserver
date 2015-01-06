__author__ = 'tr1b2669'
import socket
import errno
from clientproxy import ClientProxy
from messagedispatcher import *

dispatcher = Dispatcher()

host = socket.gethostname()
port = 9991
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcp_sock.bind((host, port))
tcp_sock.setblocking(0)

while True:
    try:
        tcp_sock.listen(4)
        print "\nListening for incoming connections..."
        (client_sock, (ip, port)) = tcp_sock.accept()
        proxy = ClientProxy(ip, port, client_sock, dispatcher)
        dispatcher.register(proxy)
        proxy.start()
    except socket.error, e:
        if e.args[0] == errno.EWOULDBLOCK:
            done = True
        else:
            print e
    dispatcher.dispatch()

