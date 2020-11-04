import sys
import time
sys.path.append("../")
import py3lib.NetSSH as net 
import logging
import py3lib.QuLogger as Qlogger
import socket


#loggername ="TEST"




ip ="127.0.0.1"
port =5000

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((source_ip, port))
address = (ip, port)
bufsize=1024
output ="12345678"
output1 = output.encode()

while 1:
	data, addr = udp_socket.recvfrom(bufsize)

	if not data:
		break

	if data.decode('utf-8') == "Test":
		udp_socket.sendto(output1,address)

udp_socket.close()








# ssh = net.NetSSH(loggername)
# Qlogger.QuConsolelogger(loggername, logging.ERROR)
# logger = logging.getLogger(loggername)
# sshresult =ssh.connectSSH(IP,22,"tinahsing","ys06hsing")
# print ("connection result:"+str(sshresult))
# tstart = time.time()
# out=ssh.sendQuerry("ls")
# tend = time.time()
# print ("time ="+str(tend-tstart))
# print ("size = "+str(sys.getsizeof(out)))