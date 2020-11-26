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
DEBUG = 0
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
	TIME_PERIOD = 0.01
	data_frame_update_point = 10
	runFlag = 0
	#IMU 靜止時之offset
	offset_wx = 0
	wxVth = 0
	offset_wy = 0
	wyVth = 0
	offset_wz = 0
	wzVth = 0
	offset_ax = 0
	axVth = 0
	offset_ay = 0
	ayVth = 0
	check_byte = 170
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
		
	
	def updateXLMDnGYRO(self, MV_MODE=1):
		print('act . offset_wz: ', end=', ') 
		print(self.offset_wz)
		print('act . self.wzVth: ', end=', ') 
		print(self.wzVth)
		print('act . offset_wy: ', end=', ') 
		print(self.offset_wy)
		print('act . self.wyVth: ', end=', ') 
		print(self.wyVth)
		print('act . offset_wx: ', end=', ') 
		print(self.offset_wx)
		print('act . self.wxVth: ', end=', ') 
		print(self.wxVth)
		print('act . offset_ax: ', end=', ') 
		print(self.offset_ax)
		print('act . self.axVth: ', end=', ') 
		print(self.axVth)
		print('act . offset_ay: ', end=', ') 
		print(self.offset_ay)
		print('act . self.ayVth: ', end=', ') 
		print(self.ayVth)
		
		
		data_ax = np.zeros(self.data_frame_update_point)
		data_ay = np.zeros(self.data_frame_update_point)
		data_az = np.zeros(self.data_frame_update_point)
		data_wx = np.zeros(self.data_frame_update_point)
		data_wy = np.zeros(self.data_frame_update_point)
		data_wz = np.zeros(self.data_frame_update_point)
		data_ax_vth = np.zeros(self.data_frame_update_point)
		data_ay_vth = np.zeros(self.data_frame_update_point)
		data_wx_vth = np.zeros(self.data_frame_update_point)
		data_wy_vth = np.zeros(self.data_frame_update_point)
		data_wz_vth = np.zeros(self.data_frame_update_point)
		dt = np.zeros(self.data_frame_update_point)
		data_ax_sum = 0
		data_ay_sum = 0
		data_az_sum = 0
		data_wx_sum = 0
		data_wy_sum = 0
		data_wz_sum = 0
		temp_dt_before = 0
		
		if self.runFlag:
			self.COM.port.flushInput()
			# dt_old = 0
			
			while self.runFlag:
				# dt = np.empty(0)
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*17))) : #rx buffer 不到 (self.data_frame_update_point*4) byte數目時不做任何事
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
					temp_dt = self.COM.read4Binary()
					
					
					#conversion
					temp_ax = self.convert2Sign_2B(temp_ax)
					temp_ay = self.convert2Sign_2B(temp_ay)
					temp_az = self.convert2Sign_2B(temp_az)
					temp_wx = self.convert2Sign_2B(temp_wx)
					temp_wy = self.convert2Sign_2B(temp_wy)
					temp_wz = self.convert2Sign_2B(temp_wz)
					temp_dt = self.convert2Unsign_4B(temp_dt)
					
					print(temp_dt, end=', ')
					print(temp_dt_before)
					if(temp_dt < temp_dt_before):
						temp_dt = temp_dt + math.ceil(abs(temp_dt - temp_dt_before)/(1<<32))*(1<<32)
						temp_dt_before = temp_dt
					
					# if(self.dt_init_flag):
						# self.dt_init_flag = 0
						# dt_init = temp_dt
					
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
					
					if(abs(val_wz-data_wz[-1]) < self.wzVth):
						val_wz_vth = self.offset_wz
					else :
						val_wz_vth = val_wz
						
					if(abs(val_wx-data_wx[-1]) < self.wxVth):
						val_wx_vth = self.offset_wx
					else :
						val_wx_vth = val_wx
						
					if(abs(val_wy-data_wy[-1]) < self.wyVth):
						val_wy_vth = self.offset_wy
					else :
						val_wy_vth = val_wy
						
					# print(val_ax, end=', ')	
					# print(data_ax[-1], end=', ')
					# print(val_ax-data_ax[-1], end=', ')						
					
					if(abs(val_ax-data_ax[-1]) < self.axVth):
						val_ax_vth = self.offset_ax
					else :
						val_ax_vth = val_ax
						
					if(abs(val_ay-data_ay[-1]) < self.ayVth):
						val_ay_vth = self.offset_ay
					else :
						val_ay_vth = val_ay
					
					data_ax = np.append(data_ax[1:], val_ax)
					data_ay = np.append(data_ay[1:], val_ay)
					data_az = np.append(data_az[1:], val_az)
					data_wx = np.append(data_wx[1:], val_wx)
					data_wy = np.append(data_wy[1:], val_wy)
					data_wz = np.append(data_wz[1:], val_wz)
					
					data_wx_vth = np.append(data_wx_vth[1:], val_wx_vth)
					data_wy_vth = np.append(data_wy_vth[1:], val_wy_vth)
					data_wz_vth = np.append(data_wz_vth[1:], val_wz_vth)
					data_ax_vth = np.append(data_ax_vth[1:], val_ax_vth)
					data_ay_vth = np.append(data_ay_vth[1:], val_ay_vth)
					
					# dt_new = dt_old + i*self.TIME_PERIOD
					dt = np.append(dt[1:], temp_dt)
					# print(temp_dt, end=', ')
					# print(dt_init, end=', ')
					# print(dt)

				self.valid_cnt = self.valid_cnt + 1
				self.bufferSize = self.COM.port.inWaiting()
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
					# print('len(data_ax_vth): ', len(data_ax_vth), end=', ')
					# print('len(dt): ', len(dt))
					# print(self.bufferSize)
					pass
				if(self.valid_cnt == 1):
					temp_dt_before = dt[0]
					
				if(self.valid_cnt == 5):
					self.valid_flag = 1
				if(self.valid_flag):
					if(self.dt_init_flag):
						self.dt_init_flag = 0
						dt_init = dt[0]
					self.fog_update7.emit(data_ax_vth, data_ay_vth, data_az, data_wx_vth, data_wy_vth, data_wz_vth, dt-dt_init)
					# dt_old = dt_new + self.TIME_PERIOD
			#end of while loop
			self.fog_finished.emit()
			temp_dt_before = 0
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
				
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*17))) : #rx buffer 不到 (self.data_frame_update_point*4) byte數目時不做任何事
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
					temp_dt = self.COM.read4Binary()
					
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
			
