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

SETCOUNT =1
READCOUNT =2
SETEXP1 =3
READMEM  =7
RST_MEM  =8

DATA_COUNT = 256

class qst006Action():
	def __init__(self, loggername):
		self.usb = com.FT232(loggername)

	def usbConnect(self, baudrate = 115200, timeout = 0.4):
		return self.usb.connect(baudrate,timeout)


class qst006Thread(QObject):
	update_histo = pyqtSignal(object)
	update_count = pyqtSignal(int)
	finished = pyqtSignal()
	
	def __init__(self, usbport, loggername, paraent = None):
		super(QObject, self).__init__(paraent)
		self.logger = logging.getLogger(loggername)
		self.usb = usbport
		self.comStatus = False
		self.countingFlag = False
		self.histoFlag = False
		self.channel = 0
		self.interval = 100
		self.totalTime = 1.0

	def setInterval(self, channel, interval):
		interval = interval*100
		d0 = interval >>16
		d1 = (interval &0xFF00) >>8
		d2 = interval&0xFF
		if (channel):
			d3 = 1
		else:
			d3 = 0
		data = [SETEXP1,d0,d1,d2,d3]

		self.logger.debug(str(data))
		
		for i in range(0,5):
			self.usb.writeBinary(data[i])

	def readData(self):
		array = np.zeros(DATA_COUNT)
		low = self.usb.readBinaryMust()
		high = self.usb.readBinary()
		value = high<<8 | low
		array[0] = value
		for i in range(1, DATA_COUNT):
			low = self.usb.readBinary()
			high = self.usb.readBinary()
			value = high<<8 | low
			array[i] = value
		self.update_histo.emit(array)
		self.usb.writeBinary(READMEM)
	

	def readMemory(self):
		self.histoFlag = True
		self.setInterval(self.channel,self.interval)
		self.usb.port.flushInput()
		self.usb.writeBinary(RST_MEM)
		time.sleep(1)
		self.usb.writeBinary(READMEM)
		startTime = time.time()
		#print(self.totalTime)
		if (self.totalTime < 1):
			#print(self.totalTime)
			time.sleep(self.totalTime)
			self.readData()
			self.finished.emit()
		else:
			time.sleep(0.1)	
			while (self.histoFlag and ( (time.time()-startTime) < self.totalTime ) ):
				self.readData()
				time.sleep(0.8)
			self.usb.writeBinary(RST_MEM)
			self.usb.port.flushInput()
			self.finished.emit()

	def counting(self):
		self.countingFlag = True
		self.setInterval(self.channel,self.interval)
		time.sleep(0.1)
		self.usb.port.flushInput()
		while(self.countingFlag):
			self.usb.writeBinary(READ_MEM)
			time.sleep(0.1)
			counting = 0
			low = self.usb.readBinaryMust()
			high = self.usb.readBinary()
			for i in range(1, DATA_COUNT):
				low = int(self.usb.readBinary())
				high = int(self.usb.readBinary())
				value = high<<8 | low
				counting = counting+value*i;
				self.logger.error(str(value))
			self.update_count.emit(counting*3)
			self.usb.writeBinary(RESET_MEM)
			time.sleep(0.33333)
		self.finished.emit()

	def setExp0(self):
		self.usb.writeBinary(SETCOUNT)
		self.usb.writeBinary(self.channel)

	def readCount(self):
		self.setExp0()
		self.countingFlag = True
		self.usb.port.flushInput()
		while(self.countingFlag):
			self.usb.writeBinary(READCOUNT)
			d1 = int(self.usb.readBinaryMust())
			d2 = int(self.usb.readBinary())
			d3 = int(self.usb.readBinary())
			d4 = int(self.usb.readBinary())
			count = (d1<<24|d2<<16|d3<<8|d4)*5
			print ("count="+str(count))
			print("d4="+str(d4))
			self.update_count.emit(count)
			time.sleep(0.3)
		self.finished.emit()











		


		



