__author__ = 'tr1b2669'
import socket

from clientproxy import ClientProxy

host = socket.gethostname()
port = 9991
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcp_sock.bind((host,port))
proxies = []


while True:
    tcp_sock.listen(4)
    print "\nListening for incoming connections..."
    (client_sock, (ip, port)) = tcp_sock.accept()
    proxy = ClientProxy(ip, port, client_sock, proxies)
    proxy.start()
    proxies.append(proxy)

for t in proxies:
    t.join()