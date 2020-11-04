import os
import sys
sys.path.append("../")
import time
import numpy as np 
import py3lib.COMPort as com
import py3lib.FileToArray as fil2a
import logging
import py3lib.QuLogger
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

START_NUM = 6 #85
READ_BYTES = 12

TEST_MODE = False

class qst006Action():
	def __init__(self, loggername):
		self.usb = com.FT232(loggername)

	def usbConnect(self, baudrate = 115200, timeout = 0.4):
		if (TEST_MODE):
			status = True
		else:
			status = self.usb.connect(baudrate,timeout)
		return status

class qst006Thread(QObject):
	update_count = pyqtSignal(int,int,int,float)
	finished = pyqtSignal()

	def __init__(self, usbport, loggername, paraent = None):
		super(QObject, self).__init__(paraent)
		self.logger = logging.getLogger(loggername)
		self.usb = usbport
		self.countingFlag = False

	def readCount(self):
		if (TEST_MODE):
			j = 0
		else:
			self.usb.port.flush()
		# print("Start thread flag = " + str(self.countingFlag))
		num = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		t0 = time.time()
		while (self.countingFlag):
			if (TEST_MODE):
				num[0] = int(np.random.rand()*100)
				num[4] = int(np.random.rand()*100)
				num[8] = int(np.random.rand()*100)
				j = j + 1
			else:
				self.usb.writeBinary(START_NUM)
				# print("send to usb")
				for i in range(0, 12):
					if (i == 0):
						temp = self.usb.readBinaryMust()
						if (temp != ''):
							num[0] = int(temp)
						else:
							num[0] = 0
					else:
						temp = self.usb.readBinary()
						if (temp != ''):
							num[i] = int(temp)
						else:
							num[i] = 0
			# print(num)
			A_value = num[3]<<24 | num[2]<<16 | num[1]<<8 | num[0]
			B_value = num[7]<<24 | num[6]<<16 | num[5]<<8 | num[4]
			AB_value = num[11]<<24 | num[10]<<16 | num[9]<<8 | num[8]
			dt = time.time() - t0
			self.update_count.emit(A_value, B_value, AB_value, dt)
			time.sleep(0.3)
		self.finished.emit()

