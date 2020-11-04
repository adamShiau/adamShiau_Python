import os
import sys
sys.path.append("../")
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.COMPort as usb

cmd_getSepctrum = [0x09, 0x4F, 0x53, 0x51]
cmd_getWavelength =[0x09, 0x4F, 0x57, 0x51]
cmd_setIntTime =[0x09, 0x4F, 0x69, 0x74]
cmd_getIntTime =[0x09, 0x4F, 0x49, 0x54]




def COMopen():
	com = usb.FT232("test")
	status =com.connect(baudrate = 9600, timeout =10)
	return com

#def intTimetoBytes(intTime_us):

def readDataList(com):
	keeprun = True
	dataout = []
	while(keeprun):
		try:
			data=ord(com.port.read())
			dataout.append(data)

		except:
			keeprun=False
	return dataout

def getIntTime(com):
	com.writeList(cmd_getIntTime)
	data =readDataList(com)
	print (data)









if __name__ == '__main__':
	com =COMopen()
	getIntTime(com)


