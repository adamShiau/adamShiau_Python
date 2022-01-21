import os
import sys
sys.path.append("../../")
import time
import numpy as np 
import scipy as sp
from scipy import signal
from py3lib.COMPort import UART
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import py3lib
from py3lib import *
import math
import time 
import datetime
import gyro_Globals as globals

DEBUG = 0
SENS_GYRO_250 		= 0.00875
SENS_AXLM_4G 		= 0.000122
SENS_ADXL355_8G 	= 0.0000156

class gyro_Action(QThread):
	update_COMArray = pyqtSignal(object)
	fog_update = pyqtSignal(object,object)
	fog_update2 = pyqtSignal(object,object, object)
	fog_update4 = pyqtSignal(object, object, object, object, object)
	fog_update7 = pyqtSignal(object, object, object, object, object, object, object)
	fog_update8 = pyqtSignal(object, object, object, object, object, object, object, object)
	imu_update10 = pyqtSignal(object, object, object, object, object, object, object, object, object, object)
	fog_update12 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object)
	fog_update13 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object, object)
	openLoop_updata1 = pyqtSignal(object)
	openLoop_updata2 = pyqtSignal(object, object)
	openLoop_updata3 = pyqtSignal(object, object, object)
	openLoop_updata4 = pyqtSignal(object, object, object, object)
	fog_finished = pyqtSignal()
	valid_flag = 0
	valid_cnt = 0
	TIME_PERIOD = 0.01
	if(globals.PRINT_MODE):
		data_frame_update_point = 1
	else: 
		data_frame_update_point = 30
	runFlag = 0
	stopFlag = 0
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
	''' check byte '''
	check_byte = 170
	check_byte2 = 171
	check_byte3 = 172
	bufferSize = 0
	pd_temperature = 0
	dt_init_flag = 1
	kal_flag = 0
	''' for err corrention'''
	old_data = 0
	old_time = 0
	old_step = 0
	old_data_flag = 0
	flag1_errtime = 0
	valid_cnt_num = 5
	def __init__(self, parent = None):	
		super().__init__()
		# QThread.__init__(self)
		self.COM = UART()
		# self.logger = logging.getLogger(loggername)
		# MAIN.mainWindow.Kal_update.emit.connect(self.test)
		# self.SaveFileName = ''
		
	def startRun(self):
		self.runFlag = 1
		self.stopFlag = 0
		print('startRun')
	
	def stopRun(self):
		self.stopFlag = 1
		print('stopRun')
		
	def printData(self, data):
		print(hex(data[0]), end='\t')
		print(hex(data[1]), end='\t')
		print(hex(data[2]), end='\t')
		print(hex(data[3]))
		
	def errCorrection(self, data):
		pass
	
	def run123(self):
		while(1):
			if(self.COM.port.inWaiting()>0):
				print(self.COM.port.inWaiting(), end=', ')
				var = self.COM.read1Binary()
				print(var[0])
			
			
	
	def run(self):
		err = np.zeros(self.data_frame_update_point)
		time = np.zeros(self.data_frame_update_point)
		step = np.zeros(self.data_frame_update_point)
		PD_temperature = np.zeros(self.data_frame_update_point)
		nano33_wx = np.zeros(self.data_frame_update_point)
		nano33_wy = np.zeros(self.data_frame_update_point)
		nano33_wz = np.zeros(self.data_frame_update_point)
		nano33_ax = np.zeros(self.data_frame_update_point)
		nano33_ay = np.zeros(self.data_frame_update_point)
		nano33_az = np.zeros(self.data_frame_update_point)
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

		# print("runFlag=", self.runFlag)
		if (self.runFlag):
			self.COM.port.flushInput()
			
			while (self.runFlag):
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*10))) : #rx buffer 不到 (self.data_frame_update_point*9) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
				x_p[0] = x_p[self.data_frame_update_point]
				y_p[0] = y_p[self.data_frame_update_point]
				p_p[0] = p_p[self.data_frame_update_point]
				
				for i in range(0,self.data_frame_update_point): 
					# if(not self.runFlag):
						# break
					# print('runFlag:', self.runFlag)
					val = self.COM.read1Binary()
					val3 = self.COM.read1Binary()
					while(val[0] != self.check_byte or val3[0] != self.check_byte3):
						val = val3
						val3 = self.COM.read1Binary()
						print("val:", val[0], end=', ')
						print(val3[0])
						
					self.bufferSize = self.COM.port.inWaiting()
					
					# for j in temp_time:
						# byte_temp_time = np.append(byte_temp_time, j).astype(int)
					# if(i==5):
						# self.old_data_flag = 1
					# temp_time = 0
					# temp_time = self.convert2Unsign_4B(byte_temp_time)
					
					# print('old_time: ', self.old_time)
					temp_time = 			self.COM.read4Binary()
					temp_err = 				self.COM.read4Binary()
					temp_step = 			self.COM.read4Binary()
					temp_PD_temperature = 	self.COM.read4Binary()
					temp_adxl355_x = 		self.COM.read3Binary()
					temp_adxl355_y = 		self.COM.read3Binary()
					temp_adxl355_z = 		self.COM.read3Binary()
					temp_nano33_wx = 		self.COM.read2Binary()
					temp_nano33_wy = 		self.COM.read2Binary()
					temp_nano33_wz = 		self.COM.read2Binary()
					temp_nano33_ax = 		self.COM.read2Binary()
					temp_nano33_ay = 		self.COM.read2Binary()
					temp_nano33_az = 		self.COM.read2Binary()
					
					
					val2 = self.COM.read1Binary()
					if(val2[0] != self.check_byte2):
						valid_flag = 0
						self.valid_cnt = (self.valid_cnt_num-2)
						break #b
							
					temp_time = 			self.convert2Unsign_4B(temp_time)
					temp_err = 				self.convert2Sign_4B(temp_err)
					temp_step = 			self.convert2Sign_4B(temp_step)
					temp_PD_temperature = 	self.convert2Unsign_4B(temp_PD_temperature)/2
					temp_adxl355_x = 		self.convert2Sign_adxl355(temp_adxl355_x)
					temp_adxl355_y = 		self.convert2Sign_adxl355(temp_adxl355_y)
					temp_adxl355_z = 		self.convert2Sign_adxl355(temp_adxl355_z)
					temp_nano33_wx = 		self.convert2Sign_nano33(temp_nano33_wx)
					temp_nano33_wy = 		self.convert2Sign_nano33(temp_nano33_wy)
					temp_nano33_wz = 		self.convert2Sign_nano33(temp_nano33_wz)
					temp_nano33_ax = 		self.convert2Sign_nano33(temp_nano33_ax)
					temp_nano33_ay = 		self.convert2Sign_nano33(temp_nano33_ay)
					temp_nano33_az = 		self.convert2Sign_nano33(temp_nano33_az)
					if(DEBUG):
						# print("time:", temp_time, end='\t');
						# print("err:", temp_err, end='\t\t');
						# print("step:", temp_step, end='\t');
						# print("PD_T:", temp_PD_temperature);
						# print("adxl355_x:", temp_adxl355_x*SENS_ADXL355_8G);
						# print("adxl355_y:", temp_adxl355_y*SENS_ADXL355_8G);
						# print("adxl355_z:", temp_adxl355_z*SENS_ADXL355_8G);
						# print("temp_nano33_ax:", temp_nano33_ax*SENS_AXLM_4G);
						# print("temp_nano33_ay:", temp_nano33_ay*SENS_AXLM_4G);
						# print("temp_nano33_az:", temp_nano33_az*SENS_AXLM_4G);
						# print("temp_nano33_wx:", temp_nano33_wx*SENS_GYRO_250);
						# print("temp_nano33_wy:", temp_nano33_wy*SENS_GYRO_250);
						self.printNano33Acc(temp_nano33_ax, temp_nano33_ay, temp_nano33_az, '\n')
					
					self.kal_flag = globals.kal_status
					''' Kalmman filter'''
					'''------update------'''
					k[i] = p_p[i]/(p_p[i] + globals.kal_R) #k_n
					x[i] = x_p[i] + k[i]*(temp_err - x_p[i])  #x_nn
					y[i] = y_p[i] + k[i]*(temp_step - y_p[i])  #y_nn
					p[i] = (1 - k[i])*p_p[i] #p_nn

					'''------predict------'''
					x_p[i+1] = x[i]
					y_p[i+1] = y[i]
					p_p[i+1] = p[i] + globals.kal_Q
					
					''' end of kalmman filter'''
					
					
					time = np.append(time[1:], temp_time)
					PD_temperature = np.append(PD_temperature[1:], temp_PD_temperature)
					if(self.kal_flag == True):
						err = np.append(err[1:], x[i]) #kalmman filter
						step = np.append(step[1:], y[i]) #kalmman filter
					else:
						err = np.append(err[1:], temp_err)
						step = np.append(step[1:], temp_step)
					nano33_wx = np.append(nano33_wx[1:], temp_nano33_wx)
					nano33_wy = np.append(nano33_wx[1:], temp_nano33_wy)
					nano33_wz = np.append(nano33_wz[1:], temp_nano33_wz)
					nano33_ax = np.append(nano33_ax[1:], temp_nano33_ax)
					nano33_ay = np.append(nano33_ay[1:], temp_nano33_ay)
					nano33_az = np.append(nano33_az[1:], temp_nano33_az)
				#end of for
				# self.openLoop_updata4.emit(time, err, step, PD_temperature)
				# self.openLoop_updata4.emit(time, nano33_ax*SENS_AXLM_4G, nano33_ay*SENS_AXLM_4G, PD_temperature)
				self.openLoop_updata4.emit(time, nano33_wz*SENS_GYRO_250, step, PD_temperature)
				if(self.stopFlag):
					self.runFlag = 0
					print('stopFlag')
				self.valid_cnt = self.valid_cnt + 1
				if(self.valid_cnt == 1):
					self.valid_flag = 1
				# if(self.valid_flag):
					# self.openLoop_updata4.emit(time, data, step, PD_temperature)
					# if(self.stopFlag):
						# self.runFlag = 0
						# print('stopFlag')
			#end of while
		#end of if	
		print('ready to stop')
		self.fog_finished.emit()
			
		self.valid_flag = 0
		self.valid_cnt = 0
		# self.fog_finished.emit()
		
		
	def run456(self):
		err = np.zeros(self.data_frame_update_point)
		time = np.zeros(self.data_frame_update_point)
		step = np.zeros(self.data_frame_update_point)
		PD_temperature = np.zeros(self.data_frame_update_point)
		nano33_wx = np.zeros(self.data_frame_update_point)
		nano33_wy = np.zeros(self.data_frame_update_point)
		nano33_wz = np.zeros(self.data_frame_update_point)
		nano33_ax = np.zeros(self.data_frame_update_point)
		nano33_ay = np.zeros(self.data_frame_update_point)
		nano33_az = np.zeros(self.data_frame_update_point)
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

		# print("runFlag=", self.runFlag)
		if (self.runFlag):
			self.COM.port.flushInput()
			
			while (self.runFlag):
				while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*40))) : #rx buffer 不到 (self.data_frame_update_point*9) byte數目時不做任何事
					# print(self.COM.port.inWaiting())
					pass
				x_p[0] = x_p[self.data_frame_update_point]
				y_p[0] = y_p[self.data_frame_update_point]
				p_p[0] = p_p[self.data_frame_update_point]
				
				for i in range(0,self.data_frame_update_point): 
					# if(not self.runFlag):
						# break
					# print('runFlag:', self.runFlag)
					val = self.COM.read1Binary()
					val3 = self.COM.read1Binary()
					while(val[0] != self.check_byte or val3[0] != self.check_byte3):
						val = val3
						val3 = self.COM.read1Binary()
						print("val:", val[0], end=', ')
						print(val3[0])
						
					self.bufferSize = self.COM.port.inWaiting()
					
					# for j in temp_time:
						# byte_temp_time = np.append(byte_temp_time, j).astype(int)
					# if(i==5):
						# self.old_data_flag = 1
					# temp_time = 0
					# temp_time = self.convert2Unsign_4B(byte_temp_time)
					
					# print('old_time: ', self.old_time)
					temp_time = 			self.COM.read4Binary()
					temp_err = 				self.COM.read4Binary()
					temp_step = 			self.COM.read4Binary()
					temp_PD_temperature = 	self.COM.read4Binary()
					temp_adxl355_x = 		self.COM.read3Binary()
					temp_adxl355_y = 		self.COM.read3Binary()
					temp_adxl355_z = 		self.COM.read3Binary()
					temp_nano33_wx = 		self.COM.read2Binary()
					temp_nano33_wy = 		self.COM.read2Binary()
					temp_nano33_wz = 		self.COM.read2Binary()
					temp_nano33_ax = 		self.COM.read2Binary()
					temp_nano33_ay = 		self.COM.read2Binary()
					temp_nano33_az = 		self.COM.read2Binary()
					
					
					val2 = self.COM.read1Binary()
					if(val2[0] != self.check_byte2):
						valid_flag = 0
						self.valid_cnt = (self.valid_cnt_num-2)
						break #b
							
					temp_time = 			self.convert2Unsign_4B(temp_time)
					temp_err = 				self.convert2Sign_4B(temp_err)
					temp_step = 			self.convert2Sign_4B(temp_step)
					temp_PD_temperature = 	self.convert2Unsign_4B(temp_PD_temperature)/2
					temp_adxl355_x = 		self.convert2Sign_adxl355(temp_adxl355_x)
					temp_adxl355_y = 		self.convert2Sign_adxl355(temp_adxl355_y)
					temp_adxl355_z = 		self.convert2Sign_adxl355(temp_adxl355_z)
					temp_nano33_wx = 		self.convert2Sign_nano33(temp_nano33_wx)
					temp_nano33_wy = 		self.convert2Sign_nano33(temp_nano33_wy)
					temp_nano33_wz = 		self.convert2Sign_nano33(temp_nano33_wz)
					temp_nano33_ax = 		self.convert2Sign_nano33(temp_nano33_ax)
					temp_nano33_ay = 		self.convert2Sign_nano33(temp_nano33_ay)
					temp_nano33_az = 		self.convert2Sign_nano33(temp_nano33_az)
					if(DEBUG):
						# print("time:", temp_time, end='\t');
						# print("err:", temp_err, end='\t\t');
						# print("step:", temp_step, end='\t');
						# print("PD_T:", temp_PD_temperature);
						# print("adxl355_x:", temp_adxl355_x*SENS_ADXL355_8G);
						# print("adxl355_y:", temp_adxl355_y*SENS_ADXL355_8G);
						# print("adxl355_z:", temp_adxl355_z*SENS_ADXL355_8G);
						# print("temp_nano33_ax:", temp_nano33_ax*SENS_AXLM_4G);
						# print("temp_nano33_ay:", temp_nano33_ay*SENS_AXLM_4G);
						# print("temp_nano33_az:", temp_nano33_az*SENS_AXLM_4G);
						# print("temp_nano33_wx:", temp_nano33_wx*SENS_GYRO_250);
						# print("temp_nano33_wy:", temp_nano33_wy*SENS_GYRO_250);
						self.printNano33Acc(temp_nano33_ax, temp_nano33_ay, temp_nano33_az, '\n')
					
					self.kal_flag = globals.kal_status
					''' Kalmman filter'''
					'''------update------'''
					k[i] = p_p[i]/(p_p[i] + globals.kal_R) #k_n
					x[i] = x_p[i] + k[i]*(temp_err - x_p[i])  #x_nn
					y[i] = y_p[i] + k[i]*(temp_step - y_p[i])  #y_nn
					p[i] = (1 - k[i])*p_p[i] #p_nn

					'''------predict------'''
					x_p[i+1] = x[i]
					y_p[i+1] = y[i]
					p_p[i+1] = p[i] + globals.kal_Q
					
					''' end of kalmman filter'''
					
					
					time = np.append(time[1:], temp_time)
					PD_temperature = np.append(PD_temperature[1:], temp_PD_temperature)
					if(self.kal_flag == True):
						err = np.append(err[1:], x[i]) #kalmman filter
						step = np.append(step[1:], y[i]) #kalmman filter
					else:
						err = np.append(err[1:], temp_err)
						step = np.append(step[1:], temp_step)
					nano33_wx = np.append(nano33_wx[1:], temp_nano33_wx)
					nano33_wy = np.append(nano33_wx[1:], temp_nano33_wy)
					nano33_wz = np.append(nano33_wz[1:], temp_nano33_wz)
					nano33_ax = np.append(nano33_ax[1:], temp_nano33_ax)
					nano33_ay = np.append(nano33_ay[1:], temp_nano33_ay)
					nano33_az = np.append(nano33_az[1:], temp_nano33_az)
				#end of for
				self.imu_update10.emit(
				time, err, step, PD_temperature,
				nano33_wx, nano33_wy, nano33_wz,
				nano33_ax, nano33_ay, nano33_az
				)
				# self.openLoop_updata4.emit(time, nano33_ax*SENS_AXLM_4G, nano33_ay*SENS_AXLM_4G, PD_temperature)
				# self.imu_update10.emit(time, nano33_wz*SENS_GYRO_250, step, PD_temperature)
				if(self.stopFlag):
					self.runFlag = 0
					print('stopFlag')
				self.valid_cnt = self.valid_cnt + 1
				if(self.valid_cnt == 1):
					self.valid_flag = 1
				# if(self.valid_flag):
					# self.openLoop_updata4.emit(time, data, step, PD_temperature)
					# if(self.stopFlag):
						# self.runFlag = 0
						# print('stopFlag')
			#end of while
		#end of if	
		print('ready to stop')
		self.fog_finished.emit()
			
		self.valid_flag = 0
		self.valid_cnt = 0
		# self.fog_finished.emit()
	
	def printNano33Gyro(self, x, y, z, eol):
		print('%.6f'% (x*SENS_GYRO_250), end='\t')
		print('%.6f'% (y*SENS_GYRO_250), end='\t')
		print('%.6f'% (z*SENS_GYRO_250), end=eol)
	
	def printNano33Acc(self, x, y, z, eol):
		print('%.6f'% (x*SENS_AXLM_4G), end='\t')
		print('%.6f'% (y*SENS_AXLM_4G), end='\t')
		print('%.6f'% (z*SENS_AXLM_4G), end=eol)
	
	def convert2Sign_4BS(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		if((datain[2]>>7) == 1):
			# return (shift_data - (1<<32))
			return (shift_data - (1<<16))
		else :
			return shift_data
			
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
	
	def convert2Sign_PD(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		if((datain[2]>>7) == 1):
			return (shift_data - 512)
		else :
			return shift_data
	
	def convert2Sign_xlm(self, datain) :
		if((datain>>15) == 1):
			return (datain - (1<<16))
		else :
			return datain
			
	def convert2Sign_adxl355(self, datain) :
		shift_data = (datain[0]<<12|datain[1]<<4|datain[2]>>4)
		if((datain[0]>>7) == 1):
			return (shift_data - (1<<20))
		else :
			return shift_data
			
	def convert2Sign_nano33(self, datain) :
		shift_data = (datain[1]<<8|datain[0])
		if((datain[1]>>7) == 1):
			return (shift_data - (1<<16))
		else :
			return shift_data
