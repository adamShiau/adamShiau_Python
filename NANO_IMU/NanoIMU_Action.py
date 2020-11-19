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
# MV_MODE = 1

class COMRead_Action(QObject):
	update_COMArray = pyqtSignal(object)
	fog_update = pyqtSignal(object,object)
	fog_update2 = pyqtSignal(object,object, object)
	fog_update4 = pyqtSignal(object, object, object, object, object)
	fog_update7 = pyqtSignal(object, object, object, object, object, object, object)
	fog_update6 = pyqtSignal(object, object, object, object, object, object)
	fog_update12 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object)
	fog_finished = pyqtSignal()
	valid_flag = 0
	valid_cnt = 0
	data_frame_update_point = 15
	runFlag = 0
	#IMU 靜止時之offset
	offset_wz = 0
	# offset_ax =
	# offset_ay =
	#
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
			
	def updateXLMDnGYRO_MV(self):
		print('hello')
		print(self.offset_wz);
		if self.runFlag:
			self.COM.port.flushInput()
			dt_old = 0
			
			data_ax = np.empty(0)
			data_ay = np.empty(0)
			data_az = np.empty(0)
			data_wx = np.empty(0)
			data_wy = np.empty(0)
			data_wz = np.zeros(self.data_frame_update_point)
			data_wz_vth = np.zeros(self.data_frame_update_point)
			dt = np.empty(0)
			
			temp_ax = np.empty(0)
			temp_ay = np.empty(0)
			temp_az = np.empty(0)
			temp_wx = np.empty(0)
			temp_wy = np.empty(0)
			temp_wz = np.empty(0)
			
			data_wz_sum = 0
			
			while self.runFlag:
				data_ax = np.empty(0)
				data_ay = np.empty(0)
				data_az = np.empty(0)
				data_wx = np.empty(0)
				data_wy = np.empty(0)
				# data_wz = np.empty(0)
				val = np.empty(0)
				dt = np.empty(0)
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*13))) : #rx buffer 不到 (self.data_frame_update_point*4) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					val = self.COM.read1Binary()
					while(val[0] != self.check_byte):
						val = self.COM.read1Binary()
					#read new value
					temp_ax = self.COM.read2Binary()
					temp_ay = self.COM.read2Binary()
					temp_az = self.COM.read2Binary()
					temp_wx = self.COM.read2Binary()
					temp_wy = self.COM.read2Binary()
					temp_wz = self.COM.read2Binary()
					
					#conversion
					temp_ax =self.convert2Sign_2B(temp_ax)
					temp_ay =self.convert2Sign_2B(temp_ay)
					temp_az =self.convert2Sign_2B(temp_az)
					temp_wx =self.convert2Sign_2B(temp_wx)
					temp_wy =self.convert2Sign_2B(temp_wy)
					temp_wz =self.convert2Sign_2B(temp_wz)
					
					data_wz_sum = data_wz_sum - data_wz[0]
					data_wz_sum = data_wz_sum + temp_wz
					data_wz_MV = data_wz_sum/self.data_frame_update_point
					if(abs(data_wz_MV-data_wz[-1])<10):
						data_wz_MV_vth = self.offset_wz
					else :
						data_wz_MV_vth = data_wz_MV
					# print(temp_wz, end=', ')
					# print(data_wz_MV)
					# print(abs(data_wz_MV-data_wz[-1]))
					
					data_ax = np.append(data_ax, temp_ax)
					data_ay = np.append(data_ay, temp_ay)
					data_az = np.append(data_az, temp_az)
					data_wx = np.append(data_wx, temp_wx)
					data_wy = np.append(data_wy, temp_wy)
					data_wz = np.append(data_wz[1:], data_wz_MV)
					data_wz_vth = np.append(data_wz_vth[1:], data_wz_MV_vth)
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
					# print('len(data_wx): ', len(data_wx), end=', ')
					# print('len(data_wy): ', len(data_wy), end=', ')
					# print('len(data_wz): ', len(data_wz), end=', ')
					# print('len(dt): ', len(dt), end=', ')
					# print(self.COM.port.inWaiting())
					pass
				if(self.valid_cnt == 5):
					self.valid_flag = 1
				if(self.valid_flag):
					self.fog_update7.emit(data_ax, data_ay, data_az, data_wx, data_wy, data_wz_vth, dt)
					dt_old = dt_new + TIME_PERIOD
			#end of while loop
			self.fog_finished.emit()
			self.valid_flag = 0
			self.valid_cnt = 0
			
	def calibrationGYRO(self, MV_MODE=1):
		if self.runFlag:
			self.COM.port.flushInput()
			
			data_ax = np.zeros(self.data_frame_update_point)
			data_ay = np.zeros(self.data_frame_update_point)
			data_az = np.zeros(self.data_frame_update_point)
			data_wx = np.zeros(self.data_frame_update_point)
			data_wy = np.zeros(self.data_frame_update_point)
			data_wz = np.zeros(self.data_frame_update_point)
			diff_ax = np.zeros(self.data_frame_update_point)
			diff_ay = np.zeros(self.data_frame_update_point)
			diff_az = np.zeros(self.data_frame_update_point)
			diff_wx = np.zeros(self.data_frame_update_point)
			diff_wy = np.zeros(self.data_frame_update_point)
			diff_wz = np.zeros(self.data_frame_update_point)
			data_ax_sum = 0
			data_ay_sum = 0
			data_az_sum = 0
			data_wx_sum = 0
			data_wy_sum = 0
			data_wz_sum = 0
			
			while self.runFlag:
			
				# val = np.empty(0)
				
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*13))) : #rx buffer 不到 (self.data_frame_update_point*4) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
				
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					val = self.COM.read1Binary()
					while(val[0] != self.check_byte):
						val = self.COM.read1Binary()
					#read new value
					temp_ax = self.COM.read2Binary()
					temp_ay = self.COM.read2Binary()
					temp_az = self.COM.read2Binary()
					temp_wx = self.COM.read2Binary()
					temp_wy = self.COM.read2Binary()
					temp_wz = self.COM.read2Binary()
					
					#conversion
					temp_ax =self.convert2Sign_2B(temp_ax)
					temp_ay =self.convert2Sign_2B(temp_ay)
					temp_az =self.convert2Sign_2B(temp_az)
					temp_wx =self.convert2Sign_2B(temp_wx)
					temp_wy =self.convert2Sign_2B(temp_wy)
					temp_wz =self.convert2Sign_2B(temp_wz)
					
					#calaculate MV value
					if(MV_MODE):
						data_ax_sum = data_ax_sum - data_ax[0]
						data_ax_sum = data_ax_sum + temp_ax
						data_ax_MV = data_ax_sum/self.data_frame_update_point
						
						data_ay_sum = data_ay_sum - data_ay[0]
						data_ay_sum = data_ay_sum + temp_ay
						data_ay_MV = data_ay_sum/self.data_frame_update_point
						
						data_az_sum = data_az_sum - data_az[0]
						data_az_sum = data_az_sum + temp_az
						data_az_MV = data_az_sum/self.data_frame_update_point
						
						data_wx_sum = data_wx_sum - data_wx[0]
						data_wx_sum = data_wx_sum + temp_wx
						data_wx_MV = data_wx_sum/self.data_frame_update_point
						
						data_wy_sum = data_wy_sum - data_wy[0]
						data_wy_sum = data_wy_sum + temp_wy
						data_wy_MV = data_wy_sum/self.data_frame_update_point
						
						data_wz_sum = data_wz_sum - data_wz[0]
						data_wz_sum = data_wz_sum + temp_wz
						data_wz_MV = data_wz_sum/self.data_frame_update_point
						
						val_ax = data_ax_MV
						val_ay = data_ay_MV
						val_az = data_az_MV
						val_wx = data_wx_MV
						val_wy = data_wy_MV
						val_wz = data_wz_MV
						
					else: 
						val_ax = temp_ax
						val_ay = temp_ay
						val_az = temp_az
						val_wx = temp_wx
						val_wy = temp_wy
						val_wz = temp_wz
						
					diff_ax = np.append(diff_ax[1:], abs(val_ax - data_ax[-1]))
					diff_ay = np.append(diff_ay[1:], abs(val_ay - data_ay[-1]))
					diff_az = np.append(diff_az[1:], abs(val_az - data_az[-1]))
					diff_wx = np.append(diff_wx[1:], abs(val_wx - data_wx[-1]))
					diff_wy = np.append(diff_wy[1:], abs(val_wy - data_wy[-1]))
					diff_wz = np.append(diff_wz[1:], abs(val_wz - data_wz[-1]))
						
					data_ax = np.append(data_ax[1:], val_ax)
					data_ay = np.append(data_ay[1:], val_ay)
					data_az = np.append(data_az[1:], val_az)
					data_wx = np.append(data_wx[1:], val_wx)
					data_wy = np.append(data_wy[1:], val_wy)
					data_wz = np.append(data_wz[1:], val_wz)
					
					
					
					# if(abs(data_wz_MV-data_wz[-1])<10):
						# data_wz_MV_vth = self.offset_wz
					# else :
						# data_wz_MV_vth = data_wz_MV
					# print(temp_wz, end=', ')
					
					# print(abs(data_wz_MV-data_wz[-1]))
					
					
					# print(data_wz)
					# data_wz_vth = np.append(data_wz_vth[1:], data_wz_MV_vth)
					# dt_new = dt_old + i*TIME_PERIOD
					# dt = np.append(dt, dt_new)
					
				self.valid_cnt = self.valid_cnt + 1
				if(DEBUG):
					# print('ax: ', data_ax)
					# print('ay: ', data_ay)
					# print('az: ', data_az)
					# print('wx: ', data_wx)
					# print('wy: ', data_wy)
					# print('wz: ', data_wz)
					# print('len(data): ', len(data), end=', ')
					# print('len(data_wx): ', len(data_wx), end=', ')
					# print('len(data_wy): ', len(data_wy), end=', ')
					# print('len(data_wz): ', len(data_wz), end=', ')
					# print('len(dt): ', len(dt), end=', ')
					print(self.COM.port.inWaiting())
					pass
				if(self.valid_cnt == 1):
					self.valid_flag = 1
				if(self.valid_flag):
					self.fog_update12.emit(data_ax, data_ay, data_az, data_wx, data_wy, data_wz,
											diff_ax, diff_ay, diff_az ,diff_wx ,diff_wy ,diff_wz)
			#end of while loop
			# self.fog_finished.emit()
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
			
