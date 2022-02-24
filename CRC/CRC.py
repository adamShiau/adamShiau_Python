import sys
sys.path.append("../")
import numpy as np
from py3lib.COMPort import UART
import time

COM = UART()

DLY_CMD = 0.05
WIDTH = 8 
TOPBIT = (1 << (WIDTH - 1))
POLYNOMIAL = 0x07

msg = np.zeros(2).astype(int)

msg[0] = 0xFE
msg[1] = 0xFE

HEADER = np.array([0xFE, 0x81, 0xFF, 0x55])
# print(hex(HEADER[0]))
# print(hex(HEADER[1]))
# print(hex(HEADER[2]))
# print(hex(HEADER[3]))

def send32BitCmd(value):
	if(value < 0):
		value = (1<<32) + value
	COM.writeBinary(value>>24 & 0xFF)
	COM.writeBinary(value>>16 & 0xFF)
	COM.writeBinary(value>>8 & 0xFF)
	COM.writeBinary(value & 0xFF)
	time.sleep(DLY_CMD)

def crcSlow(message, nBytes):
	remainder = 0;
	byte = 0
	bit = 8
	for byte in range(0, nBytes):
		# print("byte: ", byte, end=', ');
		# print(hex(message[byte]))
		remainder = remainder ^ (message[byte] << (WIDTH - 8));
		print("\nbyte: ", byte, end=', ');
		print("remainder start = ", hex(remainder));
		
		for bit in range(8, 0, -1):
			print("bit: ", bit, end=', ');
			print(hex(remainder), end=', ');
			
			if (remainder & TOPBIT):
				remainder = ((remainder << 1) & 0xFF) ^ POLYNOMIAL;
			else :
				remainder = (remainder << 1);
			print(hex(remainder));
	return remainder

def checkHeader(HEADER, nbyte) :
	headerArr = np.zeros(nbyte)
	headerArr = COM.read4Binary()
	hold = 1
	while(hold):
		
		if(	(headerArr[0]==HEADER[0]) 	and 
			(headerArr[1] == HEADER[1]) and 
			(headerArr[2] == HEADER[2]) and 
			(headerArr[3] == HEADER[3]) 
			):
				# print('\n', hex(headerArr[0]))
				# print(hex(headerArr[1]))
				# print(hex(headerArr[2]))
				# print(hex(headerArr[3]))
				hold = 0
				print("pass")
				return headerArr
		else:
			tempArr = np.zeros(nbyte).astype(int)
			tempArr[0] = headerArr[1]
			tempArr[1] = headerArr[2]
			tempArr[2] = headerArr[3]
			x =  int.from_bytes(COM.read1Binary(), 'big')
			tempArr[3] = x
			headerArr = tempArr
	
COM.printCom()
COM.manualConnect(115200, 1, 'COM5')
	
i = 0	

COM.writeBinary(99)
send32BitCmd(1)
for i in range(110):
	tt = checkHeader(HEADER, 4)
	print('\n', hex(tt[0]))
	print(hex(tt[1]))
	print(hex(tt[2]))
	print(hex(tt[3]))
	# headerArr = COM.read4Binary()
	# print(hex(headerArr[0]))
	# print(hex(headerArr[1]))
	# print(hex(headerArr[2]))
	# print(hex(headerArr[3]))
	# if(headerArr[0] == HEADER[0]):
		# print('yes!!!!!!!!!!')
COM.writeBinary(99)
send32BitCmd(0)
# print("crc = ", hex(crcSlow(msg, 2)))