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
import py3lib
from py3lib import *
import math

TEST_MODE = False
DEBUG = 1
DEBUG2 = 1
# MV_MODE = 1

class gyro_Action(QObject):
	update_COMArray = pyqtSignal(object)
	fog_update = pyqtSignal(object,object)
	fog_update2 = pyqtSignal(object,object, object)
	fog_update4 = pyqtSignal(object, object, object, object, object)
	fog_update7 = pyqtSignal(object, object, object, object, object, object, object)
	fog_update8 = pyqtSignal(object, object, object, object, object, object, object, object)
	fog_update12 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object)
	fog_update13 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object, object)
	openLoop_updata1 = pyqtSignal(object)
	openLoop_updata2 = pyqtSignal(object, object)
	openLoop_updata3 = pyqtSignal(object, object, object)
	fog_finished = pyqtSignal()
	valid_flag = 0
	valid_cnt = 0
	TIME_PERIOD = 0.01
	data_frame_update_point = 15
	runFlag = 0
	#IMU 靜止時之offset
	offset_wx = 0
	wxVth = 0
	offset_wy = 0
	wyVth = 0
	offset_wz = 0
	offset_wz200 = 0
	wzVth = 0
	offset_ax = 0
	axVth = 0
	offset_ay = 0
	ayVth = 0
	check_byte = 170
	check_byte2 = 171
	bufferSize = 0
	dt_init_flag = 1
	def __init__(self, loggername):	
		super().__init__()
		self.COM = usb.FT232(loggername)
		self.logger = logging.getLogger(loggername)
		# self.SaveFileName = ''

	def usbConnect(self):
		if (TEST_MODE):
			status = True
		else:
			status = self.COM.connect(baudrate = 115200, timeout = 1)
			print(status)
		return status
		
	def usbConnect_comboBox(self, cp):
		if (TEST_MODE):
			status = True
		else:
			status = self.COM.connect_comboBox(baudrate = 115200, timeout = 1, port_name=cp)
			# print(status)
		return status
		
	def comport_select(self):
		self.COM.checkCom()
		
	def updateOpenLoop(self):
		data = np.zeros(self.data_frame_update_point)
		time = np.zeros(self.data_frame_update_point)
		step = np.zeros(self.data_frame_update_point)
		print("runFlag=", self.runFlag)
		if self.runFlag:
			self.COM.port.flushInput()
			
			while self.runFlag:
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*9))) : #rx buffer 不到 (self.data_frame_update_point*9) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
					
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					val = self.COM.read1Binary()
					while(val[0] != self.check_byte):
						val = self.COM.read1Binary()
					
					temp_time = self.COM.read4Binary()
					# print(temp_time[0], end=', ')
					# print(temp_time[1], end=', ')
					# print(temp_time[2], end=', ')
					# print(temp_time[3])
					temp_time = self.convert2Unsign_4B(temp_time)
					time = np.append(time[1:], temp_time)
					
					temp_data = self.COM.read4Binary()
					# print(temp_data[0], end=', ')
					# print(temp_data[1], end=', ')
					# print(temp_data[2], end=', ')
					# print(temp_data[3])
					temp_data = self.convert2Sign_4B(temp_data)
					data = np.append(data[1:], temp_data)
					
					temp_step = self.COM.read4Binary()
					temp_step = self.convert2Sign_4B(temp_step)
					step = np.append(step[1:], temp_step)
					
				self.valid_cnt = self.valid_cnt + 1
				print(self.COM.port.inWaiting(), end=', ')
				print(data)
				# print(time)
				if(self.valid_cnt == 1):
					self.valid_flag = 1
				if(self.valid_flag):
					self.openLoop_updata3.emit(time, data, step)
					# self.openLoop_updata1.emit(data)
		self.valid_flag = 0
		self.valid_cnt = 0
		self.fog_finished.emit()
		
	def updateOpenLoop_old(self):
		data = np.zeros(self.data_frame_update_point)
		# time = np.zeros(self.data_frame_update_point)
		print("runFlag=", self.runFlag)
		if self.runFlag:
			self.COM.port.flushInput()
			
			while self.runFlag:
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*9))) : #rx buffer 不到 (self.data_frame_update_point*9) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
					
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					# val = self.COM.read1Binary()
					# while(val[0] != self.check_byte):
						# val = self.COM.read1Binary()
					
					# temp_time = self.COM.read4Binary()
					# print(temp_time[0], end=', ')
					# print(temp_time[1], end=', ')
					# print(temp_time[2], end=', ')
					# print(temp_time[3])
					# temp_time = self.convert2Unsign_4B(temp_time)
					# time = np.append(time[1:], temp_time)
					
					temp_data = self.COM.read4Binary()
					# print(temp_data[0], end=', ')
					# print(temp_data[1], end=', ')
					# print(temp_data[2], end=', ')
					# print(temp_data[3])
					temp_data = self.convert2Sign_4B(temp_data)
					data = np.append(data[1:], temp_data)
					
				self.valid_cnt = self.valid_cnt + 1
				print(self.COM.port.inWaiting(), end=', ')
				print(data)
				# print(time)
				if(self.valid_cnt == 2):
					self.valid_flag = 1
				if(self.valid_flag):
					# self.openLoop_updata2.emit(time, data)
					self.openLoop_updata1.emit(data)
		self.valid_flag = 0
		self.valid_cnt = 0
		self.fog_finished.emit()
			
	def convert2Sign_4B(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		if((datain[0]>>7) == 1):
			return (shift_data - (1<<32))
		else :
			return shift_data
			
	def convert2Unsign_4B(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		return shift_data
			
	def convert2Sign_2B(self, datain) :
		shift_data = (datain[0]<<8|datain[1])
		if((datain[0]>>7) == 1):
			return (shift_data - (1<<16))
		else :
			return shift_data
			
	def convert2Sign_fog(self, datain) :
		# shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		if((datain>>31) == 1):
			return (datain - (1<<32))
		else :
			return datain
			
	def convert2Sign_xlm(self, datain) :
		if((datain>>15) == 1):
			return (datain - (1<<16))
		else :
			return datain
			
