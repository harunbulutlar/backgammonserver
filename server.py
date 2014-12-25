__author__ = 'tr1b2669'
import socket

from clientproxy import ClientProxy

host = "0.0.0.0"
port = 9999
tcp_sock = socket.socket()

tcp_sock.bind((host,port))
proxies = []


while True:
    tcp_sock.listen(4)
    print "\nListening for incoming connections..."
    (client_sock, (ip, port)) = tcp_sock.accept()
    proxy = ClientProxy(ip, port)
    proxy.start()
    proxies.append(proxy)

for t in proxies:
    t.join()