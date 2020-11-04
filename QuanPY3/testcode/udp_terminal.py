import socket
import time


server_ip ="192.168.0.14"
source_ip = "0.0.0.0"
port = 5000
address=(server_ip,port)
bufsize = 1024

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((source_ip, port))
data ="TEST"
a = time.time()
udp_socket.sendto(data.encode(), address)
indata, addr = udp_socket.recvfrom(bufsize)
b = time.time()
print ("time consume ="+str(b-a))
print ("hearing from address:")
print (addr)
print (indata.decode('utf-8'))
