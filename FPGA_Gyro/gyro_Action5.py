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
# import gyro_Main3 as MAIN 
import gyro_Globals as globals

TEST_MODE = False
DEBUG = 1
DEBUG2 = 1
FAKE_DATA = 0
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
	data_frame_update_point = 10
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
	kal_flag = 0
	''' for err corrention'''
	old_data = 0
	old_time = 0
	old_step = 0
	old_data_flag = 0
	flag1_errtime = 0
	def __init__(self, loggername):	
		super().__init__()
		self.COM = usb.FT232(loggername)
		self.logger = logging.getLogger(loggername)
		# MAIN.mainWindow.Kal_update.emit.connect(self.test)
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
		
	def printData(self, data):
		print(hex(data[0]), end='\t')
		print(hex(data[1]), end='\t')
		print(hex(data[2]), end='\t')
		print(hex(data[3]))
		
	def errCorrection(self, data):
		pass
		
	def updateOpenLoop(self):
		data = np.zeros(self.data_frame_update_point)
		time = np.zeros(self.data_frame_update_point)
		step = np.zeros(self.data_frame_update_point)
		data_sum = 0
		step_sum = 0
		byte_temp_time = np.empty(0)
		''' for kalmman filter'''
		#initial guess value
		x0 = 0
		y0 = 0
		p0 = 0
		#Q:process variance
		#R:measure variance
		# Q = 1
		# R = 100
		print('action kal_Q:', globals.kal_Q)
		print('action kal_R:', globals.kal_R)
		x_p = np.zeros(self.data_frame_update_point+1)
		y_p = np.zeros(self.data_frame_update_point+1)
		p_p = np.zeros(self.data_frame_update_point+1)
		x = np.zeros(self.data_frame_update_point)
		y = np.zeros(self.data_frame_update_point)
		p = np.zeros(self.data_frame_update_point)
		k = np.zeros(self.data_frame_update_point)
		p0 = p0^2
		x_p[self.data_frame_update_point] = x0
		y_p[self.data_frame_update_point] = y0
		p_p[self.data_frame_update_point] = p0 + globals.kal_Q
		''' '''
		print("runFlag=", self.runFlag)
		if self.runFlag:
			self.COM.port.flushInput()
			
			while self.runFlag:
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*14))) : #rx buffer 不到 (self.data_frame_update_point*9) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
				x_p[0] = x_p[self.data_frame_update_point]
				y_p[0] = y_p[self.data_frame_update_point]
				p_p[0] = p_p[self.data_frame_update_point]
				
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					val = self.COM.read1Binary()
					while(val[0] != self.check_byte):
						val = self.COM.read1Binary()
						print('val[0]: ', val[0])
					
					temp_time = self.COM.read4Binary()
					# for j in temp_time:
						# byte_temp_time = np.append(byte_temp_time, j).astype(int)
					if(i==5):
						self.old_data_flag = 1
					
					# temp_time = self.convert2Unsign_4B(byte_temp_time)
					temp_time = self.convert2Unsign_4B(temp_time)
					print('temp_time: ', temp_time)
					print('old_time: ', self.old_time)
					
					
							
					
					temp_data = self.COM.read4Binary()
					# self.printData(temp_data)
					temp_data = self.convert2Sign_4B(temp_data)
					# if(self.old_data_flag==1):
						# print('diff_time:', abs(self.old_time-temp_time))
						# if(abs(self.old_time-temp_time)>200): 
							# temp_time = self.old_time + 100
					
					print('temp_data: ', temp_data, end='\n\n')
					
					
					
					# byte_temp_time = np.empty(0)
					# flag0_errtime = 0
					# flag1_errtime = 0
					
					if(FAKE_DATA):
						if(i<7):
							temp_data = 100
						else:
							temp_data = 0
					
					
					temp_step = self.COM.read4Binary()
					
					temp_step = self.convert2Sign_4B(temp_step)
					
					
					temp_step_SM = self.COM.read1Binary()
					
					if(self.old_data_flag==1):
						print('diff_time:', abs(self.old_time-temp_time))
						if(abs(self.old_time-temp_time)>200): 
							temp_time = self.old_time + 100
						print('diff_err: ', abs(self.old_data-temp_data))
						if(abs(self.old_data-temp_data)>10000): 
							temp_data = self.old_data + 0
						print('diff_step: ', abs(self.old_step-temp_step))
						if(abs(self.old_step-temp_step)>10000): 
							temp_step = self.old_step + 0
					
					self.old_time = temp_time
					self.old_data = temp_data
					self.old_step = temp_step
					
					
					# print('time:', temp_time)
					# print('ERR:', temp_data)
					
					
					# print('STEP:', temp_step, end=', ')
					# print('SM:', temp_step_SM[0], end=', ')
					# print('i: ', i)
					
					# print('i: ', i, end=', ')
					# print('p_p: ', p_p[i], end=', ')
					# print('x_p: ', x_p[i])
					# print('Kal_status:', Kal_status)
					self.kal_flag = globals.kal_status
					
					# ''' Kalmman filter'''
					#update
					k[i] = p_p[i]/(p_p[i] + globals.kal_R) #k_n
					x[i] = x_p[i] + k[i]*(temp_data - x_p[i])  #x_nn
					y[i] = y_p[i] + k[i]*(temp_step - y_p[i])  #y_nn
					p[i] = (1 - k[i])*p_p[i] #p_nn

					#predict
					x_p[i+1] = x[i]
					y_p[i+1] = y[i]
					p_p[i+1] = p[i] + globals.kal_Q
					
					''' end of kalmman filter'''
					
					data_sum = data_sum - data[0]
					data_sum = data_sum + temp_data
					data_MV = data_sum/self.data_frame_update_point
					val_data = data_MV
					
					step_sum = step_sum - step[0]
					step_sum = step_sum + temp_step
					step_MV = step_sum/self.data_frame_update_point
					val_step = step_MV
					
					time = np.append(time[1:], temp_time)
					# data = np.append(data[1:], temp_data)
					# step = np.append(step[1:], temp_step)
					# data = np.append(data[1:], val_data) #MV
					# step = np.append(step[1:], val_step) #MV
					if(self.kal_flag == True):
						data = np.append(data[1:], x[i]) #kalmman filter
						step = np.append(step[1:], y[i]) #kalmman filter
					else:
						data = np.append(data[1:], temp_data)
						step = np.append(step[1:], temp_step)
				self.valid_cnt = self.valid_cnt + 1
				print('buffer: ', self.COM.port.inWaiting())
				# print(data)
				# print(time)
				if(self.valid_cnt == 1):
					self.valid_flag = 1
				if(self.valid_flag):
					self.openLoop_updata3.emit(time, data, step)
					# self.openLoop_updata1.emit(data)
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
			
