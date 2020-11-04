import os
import sys
sys.path.append("../")
import time
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.COMPort as usb
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging

PRSETFILE = "set/setting.txt"
SETTING_FILEPATH = "set"

TEST_MODE = False
ADC_DATALEN = 200

class qss011Action():
	def __init__(self, loggername):	
		self.loggername = loggername
		self.COM = usb.FT232(loggername)
		self.logger = logging.getLogger(loggername)
		#self.paramInit()
		#self.loadPreset()

	def usbConnect(self):
		if (TEST_MODE):
			status = True
		else:
			status = self.COM.connect(baudrate = 115200, timeout = 1)
		return status

	def paramInit(self):
		self.freq = 10
		self.phase = 0
		self.paralist = ["" for i in range(0, Max_Para_Index)]

	def loadPreset(self):
		if not os.path.isdir(SETTING_FILEPATH):
			os.mkdir(SETTING_FILEPATH)
			self.writePreset()
			self.logger.warning("preseet file dir not exist")
		elif not os.path.exists(PRSETFILE):
			self.writePreset()
			self.logger.warning("preseet file load failed")
		else:
			paralist = fil2a.TexTFileto1DList(PRSETFILE, self.loggername)
			if (len(paralist) != Max_Para_Index):
				self.writePreset()
				self.logger.warning("preseet file formate error")
			else:
				self.paralist = paralist
				# list your preset param table here
				self.freq = int(self.paralist[INDEX_freq])
				self.phase = int(self.paralist[INDEX_phase])

	def writePreset(self):
		# list your preset param table here
		
		fil2a.array1DtoTextFile(PRSETFILE, self.paralist, self.loggername)

	def getADC(self):
		self.COM.writeLine("GetADC")
		data =np.empty(0)
		for i in range(0, ADC_DATALEN):
			high= self.COM.readBinary()
			low = self.COM.readBinary()
			temp = high << 8
			data = np.append(data, high <<8 | low)
		return data



