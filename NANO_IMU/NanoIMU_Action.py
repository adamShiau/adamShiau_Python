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

TEST_MODE = False
DEBUG = 1
TIME_PERIOD = 0.01

class COMRead_Action(QObject):
	update_COMArray = pyqtSignal(object)
	fog_update = pyqtSignal(object,object)
	fog_update2 = pyqtSignal(object,object, object)
	fog_update4 = pyqtSignal(object, object, object, object, object)
	fog_update7 = pyqtSignal(object, object, object, object, object, object, object)
	fog_finished = pyqtSignal()
	valid_flag = 0
	valid_cnt = 0
	data_frame_update_point = 15
	check_byte = 170
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
		
	def updateTwoData(self):
		if self.runFlag:
			self.COM.port.flushInput()
			dt_old = 0
			data = np.empty(0)
			dt = np.empty(0)
			temp = np.empty(0)
			while self.runFlag:
				data = np.empty(0)
				
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*4))) : #rx buffer 不到 (self.data_frame_update_point*4) byte數目時不做任何事
					pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					temp = self.COM.read4Binary()
					temp =self.convert2Sign_4B(temp)
					# temp = temp[0]<<24|temp[1]<<16|temp[2]<<8|temp[3] #4 byte data
					data = np.append(data, temp)
					dt_new = dt_old + i*TIME_PERIOD
					dt = np.append(dt, dt_new)
				
				if(DEBUG):
					print(len(data), end=', ')
					print(len(dt), end=', ')
					print(self.COM.port.inWaiting())
				self.fog_update.emit(data,dt)
				dt_old = dt_new + TIME_PERIOD
				data = np.empty(0)
				dt = np.empty(0)
			#end of while loop
			self.fog_finished.emit()
			
	def updateThreeData(self):
		if self.runFlag:
			self.COM.port.flushInput()
			dt_old = 0
			data1 = np.empty(0)
			data2 = np.empty(0)
			dt = np.empty(0)
			temp1 = np.empty(0)
			temp2 = np.empty(0)
			while self.runFlag:
				data1 = np.empty(0)
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*8))) : #rx buffer 不到 (self.data_frame_update_point*8) byte數目時不做任何事
					pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					temp1 = self.COM.read4Binary()
					temp1 =self.convert2Sign_4B(temp1)
					
					temp2 = self.COM.read4Binary()
					temp2 =self.convert2Sign_4B(temp2)
					
					data1 = np.append(data1, temp1)
					data2 = np.append(data2, temp2)
					dt_new = dt_old + i*TIME_PERIOD
					dt = np.append(dt, dt_new)
				if(DEBUG):
					# print(temp1, end=', ')
					# print(temp2, end=', ')
					# print(len(data1), end=', ')
					# print(len(dt), end=', ')
					print(self.COM.port.inWaiting())
				self.fog_update2.emit(data1,data2,dt)
				dt_old = dt_new + TIME_PERIOD
				data1 = np.empty(0)
				data2 = np.empty(0)
				dt = np.empty(0)
			#end of while loop
			self.fog_finished.emit()
			
	def updateFOG(self):
		if self.runFlag:
			self.COM.port.flushInput()
			dt_old = 0
			data1 = np.empty(0)
			# data2 = np.empty(0)
			dt = np.empty(0)
			temp  = np.empty(0)
			temp1 = np.empty(0)
			temp2 = np.empty(0)
			temp3 = np.empty(0)
			# a = 0
			while self.runFlag:
				
				
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*12))) : #rx buffer 不到 (self.data_frame_update_point*8) byte數目時不做任何事
					pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					temp1 = self.COM.read4Binary()
					temp2 = self.COM.read4Binary()
					temp3 = self.COM.read4Binary()
					fog_data = temp2[1]<<24 | temp2[0]<<16 | temp1[3]<<8 | temp1[2]
					header = temp1[0]<<8 | temp1[1]
					temp =self.convert2Sign_fog(fog_data) #convert to degree/h
					# a = a + 1
					
					data1 = np.append(data1, temp)
					# data1 = np.append(data1, a)

					# data2 = np.append(data2, temp2)
					dt_new = dt_old + i*TIME_PERIOD
					dt = np.append(dt, dt_new)
				if(DEBUG):
					# print(data1, end=', ')
					print(hex(header), end=', ')
					print(len(data1), end=', ')
					print(len(dt), end=', ')
					print(self.COM.port.inWaiting())
					# print(data1)
				self.fog_update.emit(data1,dt)
				dt_old = dt_new + TIME_PERIOD
				data1 = np.empty(0)
				# data2 = np.empty(0)
				dt = np.empty(0)
			#end of while loop
			self.fog_finished.emit()
			
			
	
				
	def updateFOGnXLMD(self):
		if self.runFlag:
			self.COM.port.flushInput()
			dt_old = 0
			data = np.empty(0)
			data_ax = np.empty(0)
			data_ay = np.empty(0)
			data_az = np.empty(0)
			dt = np.empty(0)
			temp_fog = np.empty(0)
			temp_ax = np.empty(0)
			temp_ay = np.empty(0)
			temp_az = np.empty(0)
			while self.runFlag:
				data = np.empty(0)
				data_ax = np.empty(0)
				data_ay = np.empty(0)
				data_az = np.empty(0)
				val = np.empty(0)
				dt = np.empty(0)
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*11))) : #rx buffer 不到 (self.data_frame_update_point*4) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					val = self.COM.read1Binary()
					while(val[0] != self.check_byte):
						val = self.COM.read1Binary()
					temp_fog = self.COM.read4Binary()
					temp_ax = self.COM.read2Binary()
					temp_ay = self.COM.read2Binary()
					temp_az = self.COM.read2Binary()
					
					# print(val[0], end=', ')
					# print(temp_fog[0], end=', ')
					# print(temp_fog[1], end=', ')
					# print(temp_fog[2], end=', ')
					# print(temp_fog[3], end=', ')
					# print(temp_ax[0], end=', ')
					# print(temp_ax[1], end=', ')
					# print(temp_ay[0], end=', ')
					# print(temp_ay[1], end=', ')
					# print(temp_az[0], end=', ')
					# print(temp_az[1])
					
					temp_fog =self.convert2Sign_4B(temp_fog)
					temp_ax =self.convert2Sign_2B(temp_ax)
					temp_ay =self.convert2Sign_2B(temp_ay)
					temp_az =self.convert2Sign_2B(temp_az)
					
					
					data = np.append(data, temp_fog)
					data_ax = np.append(data_ax, temp_ax)
					data_ay = np.append(data_ay, temp_ay)
					data_az = np.append(data_az, temp_az)
					dt_new = dt_old + i*TIME_PERIOD
					dt = np.append(dt, dt_new)
					
				self.valid_cnt = self.valid_cnt + 1
				if(DEBUG):
					# print(data, end=', ')
					# print(data_ax, end=', ')
					# print(data_ay, end=', ')
					# print(data_az, end=', ')
					# print('len(data): ', len(data), end=', ')
					# print('len(data_ax): ', len(data_ax), end=', ')
					# print('len(data_ay): ', len(data_ay), end=', ')
					# print('len(data_az): ', len(data_az), end=', ')
					# print('len(dt): ', len(dt), end=', ')
					print(self.COM.port.inWaiting())
				if(self.valid_cnt == 5):
					self.valid_flag = 1
				if(self.valid_flag):
					self.fog_update4.emit(data, data_ax, data_ay, data_az, dt)
					dt_old = dt_new + TIME_PERIOD
			#end of while loop
			self.fog_finished.emit()
			self.valid_flag = 0
			self.valid_cnt = 0
			
	def updateXLMDnGYRO(self):
		if self.runFlag:
			self.COM.port.flushInput()
			dt_old = 0
			
			data_ax = np.empty(0)
			data_ay = np.empty(0)
			data_az = np.empty(0)
			data_wx = np.empty(0)
			data_wy = np.empty(0)
			data_wz = np.empty(0)
			dt = np.empty(0)
			
			temp_ax = np.empty(0)
			temp_ay = np.empty(0)
			temp_az = np.empty(0)
			temp_wx = np.empty(0)
			temp_wy = np.empty(0)
			temp_wz = np.empty(0)
			
			while self.runFlag:
				data_ax = np.empty(0)
				data_ay = np.empty(0)
				data_az = np.empty(0)
				data_wx = np.empty(0)
				data_wy = np.empty(0)
				data_wz = np.empty(0)
				val = np.empty(0)
				dt = np.empty(0)
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*13))) : #rx buffer 不到 (self.data_frame_update_point*4) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					val = self.COM.read1Binary()
					while(val[0] != self.check_byte):
						val = self.COM.read1Binary()
					temp_ax = self.COM.read2Binary()
					temp_ay = self.COM.read2Binary()
					temp_az = self.COM.read2Binary()
					temp_wx = self.COM.read2Binary()
					temp_wy = self.COM.read2Binary()
					temp_wz = self.COM.read2Binary()
					
					
					# print(val[0], end=', ')
					# print(temp_fog[0], end=', ')
					# print(temp_fog[1], end=', ')
					# print(temp_fog[2], end=', ')
					# print(temp_fog[3], end=', ')
					# print(temp_ax[0], end=', ')
					# print(temp_ax[1], end=', ')
					# print(temp_ay[0], end=', ')
					# print(temp_ay[1], end=', ')
					# print(temp_az[0], end=', ')
					# print(temp_az[1])
					
					temp_ax =self.convert2Sign_2B(temp_ax)
					temp_ay =self.convert2Sign_2B(temp_ay)
					temp_az =self.convert2Sign_2B(temp_az)
					temp_wx =self.convert2Sign_2B(temp_wx)
					temp_wy =self.convert2Sign_2B(temp_wy)
					temp_wz =self.convert2Sign_2B(temp_wz)
					
					
					data_ax = np.append(data_ax, temp_ax)
					data_ay = np.append(data_ay, temp_ay)
					data_az = np.append(data_az, temp_az)
					data_wx = np.append(data_wx, temp_wx)
					data_wy = np.append(data_wy, temp_wy)
					data_wz = np.append(data_wz, temp_wz)
					dt_new = dt_old + i*TIME_PERIOD
					dt = np.append(dt, dt_new)
					
				self.valid_cnt = self.valid_cnt + 1
				if(DEBUG):
					# print('ax: ', data_ax)
					# print('ay: ', data_ay)
					# print('az: ', data_az)
					# print('wx: ', data_wx)
					# print('wy: ', data_wy)
					# print('wz: ', data_wz)
					# print('len(data): ', len(data), end=', ')
					# print('len(data_ax): ', len(data_ax), end=', ')
					# print('len(data_ay): ', len(data_ay), end=', ')
					# print('len(data_az): ', len(data_az), end=', ')
					# print('len(dt): ', len(dt), end=', ')
					print(self.COM.port.inWaiting())
				if(self.valid_cnt == 5):
					self.valid_flag = 1
				if(self.valid_flag):
					self.fog_update7.emit(data_ax, data_ay, data_az, data_wx, data_wy, data_wz, dt)
					dt_old = dt_new + TIME_PERIOD
			#end of while loop
			self.fog_finished.emit()
			self.valid_flag = 0
			self.valid_cnt = 0
			
	def convert2Sign_4B(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		if((datain[0]>>7) == 1):
			return (shift_data - (1<<32))
		else :
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
			
