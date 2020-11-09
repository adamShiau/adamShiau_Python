import os
import sys
sys.path.append("../")
import time
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.COMPort as usb

COM = usb.FT232('123')
status = COM.connect(baudrate = 115200, timeout = 1)
print(status)
while(1):
	# count = COM.port.inWaiting() 
	while(not COM.port.inWaiting()):
		dum=0
	# if(count>0) :
		# print(count)
	temp = COM.read4Binary()
	print(COM.port.inWaiting(), end=', ')
	print(temp[0]<<24|temp[1]<<16|temp[2]<<8|temp[3])

# print(COM.readBinary())