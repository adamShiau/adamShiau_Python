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

WIDTH = 8 
TOPBIT = (1 << (WIDTH - 1))
POLYNOMIAL = 0x07
HEADER = np.array([0xFE, 0x81, 0xFF, 0x55])

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
	fake_time = 0
	''' for err corrention'''
	old_err = 0
	old_time = 0
	old_step = 0
	old_PD_temp = 0
	crc_fail_cnt = 0
	
	old_data_flag = 0
	flag1_errtime = 0
	valid_cnt_num = 5
	def __init__(self, parent = None):	
		# super().__init__()
		QThread.__init__(self)
		self.COM = UART()
		# self.logger = logging.getLogger(loggername)
		# MAIN.mainWindow.Kal_update.emit.connect(self.test)
		# self.SaveFileName = ''
	
	def checkHeader(self, HEADER) :
		headerArr = bytearray(self.COM.read4Binary())
		hold = 1
		while(hold):
			if(	(headerArr[0] == HEADER[0]) and 
				(headerArr[1] == HEADER[1]) and 
				(headerArr[2] == HEADER[2]) and 
				(headerArr[3] == HEADER[3]) 
				):
					hold = 0
					return headerArr
			else:
				headerArr[0] = headerArr[1]
				headerArr[1] = headerArr[2]
				headerArr[2] = headerArr[3]
				headerArr[3] = self.COM.read1Binary()[0]
	
	def crcSlow(self, message, nBytes):
		remainder = 0;
		byte = 0
		bit = 8
		for byte in range(0, nBytes):
			# print("byte: ", byte, end=', ');
			# print(hex(message[byte]))
			remainder = remainder ^ (message[byte] << (WIDTH - 8));
			# print("\nbyte: ", byte, end=', ');
			# print("remainder start = ", hex(remainder));
			
			for bit in range(8, 0, -1):
				# print("bit: ", bit, end=', ');
				# print(hex(remainder), end=', ');
				
				if (remainder & TOPBIT):
					remainder = ((remainder << 1) & 0xFF) ^ POLYNOMIAL;
				else :
					remainder = (remainder << 1);
				# print(hex(remainder));
		return remainder
	
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
	
			
	def readPIG(self, EN=1):
		if(EN):
			temp_header = self.checkHeader(HEADER)
			temp_time = bytearray(self.COM.read4Binary())
			temp_err = bytearray(self.COM.read4Binary())
			temp_step = bytearray(self.COM.read4Binary())
			temp_PD_temperature = bytearray(self.COM.read4Binary())
			temp_crc = self.COM.read1Binary()
			msg =  temp_header + temp_time + temp_err + temp_step + temp_PD_temperature
			crc = self.crcSlow(msg, 20)
			# print('calculate CRC: ', crc)
			# print('read CRC: ', temp_crc[0])
			if(temp_crc[0] == crc):
				temp_time = self.convert2Unsign_4B(temp_time)
				temp_err = self.convert2Sign_4B(temp_err)
				temp_step = self.convert2Sign_4B(temp_step)
				temp_PD_temperature = self.convert2Unsign_4B(temp_PD_temperature)/2
				self.old_err = temp_err
				self.old_step = temp_step
				self.old_PD_temp = temp_PD_temperature
			else :
				self.crc_fail_cnt = self.crc_fail_cnt + 1
				print('crc fail : ', self.crc_fail_cnt)
				temp_err = self.old_err
				temp_step = self.old_step
				temp_PD_temperature = self.old_PD_temp
		else:
			temp_time = self.fake_time
			temp_err = 0
			temp_step = 0
			temp_PD_temperature = 0
			self.fake_time = self.fake_time + 100
			time.sleep(0.001)
		return temp_time, temp_err, temp_step, temp_PD_temperature
	
	def readADXL355(self, EN, SF, PRINT=0):
		if(EN): 
			temp_adxl355_x = self.COM.read3Binary()
			temp_adxl355_y = self.COM.read3Binary()
			temp_adxl355_z = self.COM.read3Binary()
			temp_adxl355_x = self.convert2Sign_adxl355(temp_adxl355_x)*SF
			temp_adxl355_y = self.convert2Sign_adxl355(temp_adxl355_y)*SF
			temp_adxl355_z = self.convert2Sign_adxl355(temp_adxl355_z)*SF
		else: 
			temp_adxl355_x = 0
			temp_adxl355_y = 0
			temp_adxl355_z = 0
		
		if(PRINT): 
			print(round(temp_adxl355_x,4), end='\t\t')
			print(round(temp_adxl355_y,4), end='\t\t')
			print(round(temp_adxl355_z,4))
			
		return temp_adxl355_x, temp_adxl355_y, temp_adxl355_z
	
	def readNANO33(self, EN, SF_XLM, SF_GYRO, PRINT=0):
		if(EN):
			temp_nano33_wx = self.COM.read2Binary()
			temp_nano33_wy = self.COM.read2Binary()
			temp_nano33_wz = self.COM.read2Binary()
			temp_nano33_ax = self.COM.read2Binary()
			temp_nano33_ay = self.COM.read2Binary()
			temp_nano33_az = self.COM.read2Binary()
			temp_nano33_wx = self.convert2Sign_nano33(temp_nano33_wx)*SF_GYRO
			temp_nano33_wy = self.convert2Sign_nano33(temp_nano33_wy)*SF_GYRO
			temp_nano33_wz = self.convert2Sign_nano33(temp_nano33_wz)*SF_GYRO
			temp_nano33_ax = self.convert2Sign_nano33(temp_nano33_ax)*SF_XLM
			temp_nano33_ay = self.convert2Sign_nano33(temp_nano33_ay)*SF_XLM
			temp_nano33_az = self.convert2Sign_nano33(temp_nano33_az)*SF_XLM
		else:
			temp_nano33_wx = 0
			temp_nano33_wy = 0
			temp_nano33_wz = 0.2
			temp_nano33_ax = 0
			temp_nano33_ay = 0
			temp_nano33_az = 0
			
		if(PRINT): 
			print(round(temp_nano33_ax,4), end='\t\t')
			print(round(temp_nano33_ay,4), end='\t\t')
			print(round(temp_nano33_az,4), end='\t\t')
			print(round(temp_nano33_wx,4), end='\t\t')
			print(round(temp_nano33_wy,4), end='\t\t')
			print(round(temp_nano33_wz,4))
			
		return [temp_nano33_wx, temp_nano33_wy, temp_nano33_wz, 
				temp_nano33_ax, temp_nano33_ay, temp_nano33_az]
	
	def run(self):
		err = np.zeros(self.data_frame_update_point)
		time_s = np.zeros(self.data_frame_update_point)
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
			if(globals.TEST_MODE==0):
				self.COM.port.flushInput()
			print('crc fail : ', self.crc_fail_cnt)
			start_time = time.time()
			while (self.runFlag):
				if(globals.TEST_MODE==0):
					while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*10))): 
						# print(self.COM.port.inWaiting())
						pass
				x_p[0] = x_p[self.data_frame_update_point]
				y_p[0] = y_p[self.data_frame_update_point]
				p_p[0] = p_p[self.data_frame_update_point]
				
				# self.COM.port.flushInput()
				for i in range(0,self.data_frame_update_point): 
					if(globals.TEST_MODE==0):
						self.bufferSize = self.COM.port.inWaiting()
					pc_time = time.time() - start_time
					# print(pc_time)
					[temp_time, 
					temp_err, 
					temp_step, 
					temp_PD_temperature] = self.readPIG(EN=0)
					
					[temp_adxl355_x,
					temp_adxl355_y,
					temp_adxl355_z] = self.readADXL355(EN=0, SF=SENS_ADXL355_8G
														,PRINT=0)

					[temp_nano33_wx,
					temp_nano33_wy,
					temp_nano33_wz,
					temp_nano33_ax,
					temp_nano33_ay,
					temp_nano33_az] = self.readNANO33(EN=0, SF_XLM=SENS_AXLM_4G
														,SF_GYRO=SENS_GYRO_250
														,PRINT=0)
					
					if(DEBUG):
						print("time:", temp_time, end='\t');
						print("err:", temp_err, end='\t\t');
						print("step:", temp_step, end='\t');
						print("PD_T:", temp_PD_temperature);
						
					
					self.kal_flag = globals.kal_status
					''' Kalmman filter'''
					'''------update------'''
					k[i] = p_p[i]/(p_p[i] + globals.kal_R) #k_n
					# x[i] = x_p[i] + k[i]*(temp_err - x_p[i])  #x_nn
					x[i] = x_p[i] + k[i]*(temp_nano33_wz - x_p[i])  #x_nn
					y[i] = y_p[i] + k[i]*(temp_step - y_p[i])  #y_nn
					p[i] = (1 - k[i])*p_p[i] #p_nn

					'''------predict------'''
					x_p[i+1] = x[i]
					y_p[i+1] = y[i]
					p_p[i+1] = p[i] + globals.kal_Q
					
					''' end of kalmman filter'''
					
					
					time_s = np.append(time_s[1:], temp_time)
					PD_temperature = np.append(PD_temperature[1:], temp_PD_temperature)
					if(self.kal_flag == True):
						err = np.append(err[1:], x[i]) #kalmman filter
						step = np.append(step[1:], y[i]) #kalmman filter
					else:
						# err = np.append(err[1:], temp_err) 
						err = np.append(err[1:], temp_nano33_wz) 
						step = np.append(step[1:], temp_step)
				#end of for
				print('action: ', end='\t')
				print(len(time_s), end='\t')
				print(len(err), end='\t')
				print(len(step), end='\t')
				print(len(PD_temperature))
				self.openLoop_updata4.emit(time_s, err, step, PD_temperature)
				# self.openLoop_updata4.emit(time, nano33_ax*SENS_AXLM_4G, nano33_ay*SENS_AXLM_4G, PD_temperature)
				# self.openLoop_updata4.emit(time, nano33_wz*SENS_GYRO_250, step, PD_temperature)
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
		self.crc_fail_cnt = 0
		self.fake_time = 0
		self.valid_flag = 0
		self.valid_cnt = 0
		# self.fog_finished.emit()
		
	def printNano33Gyro(self, x, y, z, eol):
		print('%.6f'% (x), end='\t')
		print('%.6f'% (y), end='\t')
		print('%.6f'% (z), end=eol)
	
	def printNano33Acc(self, x, y, z, eol):
		print('%.6f'% (x), end='\t')
		print('%.6f'% (y), end='\t')
		print('%.6f'% (z), end=eol)
	
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
