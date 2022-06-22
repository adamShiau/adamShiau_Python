import os
import sys
sys.path.append("../")
sys.path.append('../../py3lib/EncoderConnector')
from myLib.EncoderConnector.EncoderConnector import myEncoderReader
import time
import numpy as np 
from py3lib.COMPort import UART
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
HEADER_PIG = np.array([0xFE, 0x81, 0xFF, 0x55])
HEADER_SRS = np.array([0xC0, 0xC0])

class gyro_Action(QThread):
	update_COMArray = pyqtSignal(object)
	data_update6 = pyqtSignal(object, object, object, object, object, object)
	data_update9 = pyqtSignal(object, object, object, object, object, object, object, object, object)
	data_update4 = pyqtSignal(object, object, object, object)
	fog_finished = pyqtSignal()
	valid_flag = 0
	valid_cnt = 0
	TIME_PERIOD = 0.01
	kal_Q = 1
	kal_R = 6
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
	timer_rst_succeed = 0
	old_data_flag = 0
	flag1_errtime = 0
	valid_cnt_num = 5
	encoderSpeed = 0
	def __init__(self, parent = None):	
		QThread.__init__(self)
		self.COM = UART()
		self.oReader = myEncoderReader()
		self.oReader.setCallback(self.getStatus)
		self.oReader.connectServer()
		self.oReader.start()
	
	def getStatus(self, dctStatus:dict):
		# strSequence = dctStatus["Sequence"]
		# iStep = dctStatus["Step"]
		# fDistance = dctStatus["Distance"]
		# fEncoderSpeed = dctStatus["EncoderSpeed"]
		self.encoderSpeed = dctStatus["VehicleSpeed"]
		# fVehicleAcceleration = dctStatus["VehicleAcceleration"]
		

	
	def checkHeader_4B(self, HEADER) :
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
				
	def checkHeader_2B(self, HEADER) :
		headerArr = bytearray(self.COM.read2Binary())
		hold = 1
		while(hold):
			if(	(headerArr[0] == HEADER[0]) and 
				(headerArr[1] == HEADER[1]) 
				):
					hold = 0
					return headerArr
			else:
				headerArr[0] = headerArr[1]
				headerArr[1] = self.COM.read1Binary()[0]
	
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
	
			
	def readPIG(self, EN=1, FAKE=0, PRINT=0):
		if(EN):
			temp_header = self.checkHeader_4B(HEADER_PIG)
			temp_time = bytearray(self.COM.read4Binary())
			temp_err = bytearray(self.COM.read4Binary())
			temp_step = bytearray(self.COM.read4Binary())
			temp_PD_temperature = bytearray(self.COM.read4Binary())
			temp_crc = self.COM.read1Binary()
			msg =  temp_header + temp_time + temp_err + temp_step + temp_PD_temperature
			if(FAKE):
				crc = 255
				# print('FAKE MODE!!!')
			else: 
				crc = self.crcSlow(msg, 20)
			# print('calculate CRC: ', crc)
			# print('read CRC: ', temp_crc[0])
			if(temp_crc[0] == crc):
				temp_time = self.convert2Unsign_4B(temp_time)
				temp_err = self.convert2Sign_4B(temp_err)
				temp_step = self.convert2Sign_4B(temp_step)
				temp_PD_temperature = self.convert2Unsign_4B(temp_PD_temperature)/2
				self.old_time = temp_time
				self.old_err = temp_err
				self.old_step = temp_step
				self.old_PD_temp = temp_PD_temperature
			else :
				self.crc_fail_cnt = self.crc_fail_cnt + 1
				print('crc fail : ', self.crc_fail_cnt)
				temp_time = self.old_time + 0.005
				temp_err = self.old_err
				temp_step = self.old_step
				temp_PD_temperature = self.old_PD_temp
		else:
			temp_time = self.fake_time
			temp_err = 0
			temp_step = 0
			temp_PD_temperature = 0
			self.fake_time = self.fake_time + 100
			time.sleep(0.1)
			
		if(PRINT): 
			print(round(temp_time,3), end='\t\t')
			print(round(temp_err,3), end='\t\t')
			print(round(temp_step,3), end='\t\t') 
			print(round(temp_PD_temperature,3), end='\t\t')
			print(temp_crc[0], end='\t\t')
			print(self.crc_fail_cnt)
			
		return temp_time, temp_err, temp_step, temp_PD_temperature
		
	def readSRS200(self, EN=0, SF=0.01, PRINT=0):
		if(EN): 
			temp_header = self.checkHeader_2B(HEADER_SRS)
			temp_srs200 = bytearray(self.COM.read4Binary())
			# temp_srs200 = bytearray(self.COM.read15Binary())
			w_srs200 = self.convert2Sign_srs200(temp_srs200)*SF
		else: 
			w_srs200 = 123
		
		if(PRINT): 
			print(temp_header[0], end='\t')
			print(temp_header[1], end='\t')
			for i in temp_srs200:
				print(i, end='\t')
			print(round(w_srs200, 2))
			
		return w_srs200
	
	
	def readADXL355(self, EN, SF, PRINT=0):
		if(EN): 
			temp_adxl355_x = self.COM.read3Binary()
			temp_adxl355_y = self.COM.read3Binary()
			temp_adxl355_z = self.COM.read3Binary()
			temp_adxl355_x = self.convert2Sign_adxl355(temp_adxl355_x)*SF
			temp_adxl355_y = self.convert2Sign_adxl355(temp_adxl355_y)*SF
			temp_adxl355_z = self.convert2Sign_adxl355(temp_adxl355_z)*SF
		else: 
			temp_adxl355_x = 9.8
			temp_adxl355_y = 9.8
			temp_adxl355_z = 9.8
		
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
			temp_nano33_wx = 0.2
			temp_nano33_wy = 0.2
			temp_nano33_wz = 0.2
			temp_nano33_ax = 10
			temp_nano33_ay = 10
			temp_nano33_az = 10
			
		if(PRINT): 
			print(round(temp_nano33_ax,4), end='\t\t')
			print(round(temp_nano33_ay,4), end='\t\t')
			print(round(temp_nano33_az,4), end='\t\t')
			print(round(temp_nano33_wx,4), end='\t\t')
			print(round(temp_nano33_wy,4), end='\t\t')
			print(round(temp_nano33_wz,4))
			
		return [temp_nano33_wx, temp_nano33_wy, temp_nano33_wz, 
				temp_nano33_ax, temp_nano33_ay, temp_nano33_az]
	
	def readSpeedEncoder(self, EN=0, PRINT=0):
		if(EN): 
			fVehicleSpeed = self.encoderSpeed
		else:
			fVehicleSpeed = 0
		if(PRINT): 
			print(fVehicleSpeed)
			
		return fVehicleSpeed
		
	def run(self):
		
		err = np.zeros(self.data_frame_update_point)
		time_s = np.zeros(self.data_frame_update_point)
		step = np.zeros(self.data_frame_update_point)
		PD_temperature = np.zeros(self.data_frame_update_point)
		nano33_wz = np.zeros(self.data_frame_update_point)
		speed = np.zeros(self.data_frame_update_point)
		ax = np.zeros(self.data_frame_update_point)
		ay = np.zeros(self.data_frame_update_point)
		az = np.zeros(self.data_frame_update_point)
		srs200 = np.zeros(self.data_frame_update_point)
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
		# print('action kal_Q:', globals.kal_Q)
		# print('action kal_R:', globals.kal_R)
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
		p_p[self.data_frame_update_point] = p0 + self.kal_Q
		''' '''

		# print("runFlag=", self.runFlag)
		if (self.runFlag):
			# self.oReader.start()
			# self.oReader.join()
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
					temp_PD_temperature] = self.readPIG(EN=1, FAKE=0, PRINT=0)
					
					if(not self.timer_rst_succeed):
						if(temp_time < 10000):
							self.timer_rst_succeed = 1
						else:
							break;
							
					[temp_adxl355_x,
					temp_adxl355_y,
					temp_adxl355_z] = self.readADXL355(EN=1, SF=SENS_ADXL355_8G
														,PRINT=0)

					[temp_nano33_wx,
					temp_nano33_wy,
					temp_nano33_wz,
					temp_nano33_ax,
					temp_nano33_ay,
					temp_nano33_az] = self.readNANO33(EN=1, SF_XLM=SENS_AXLM_4G
														,SF_GYRO=SENS_GYRO_250
														,PRINT=0)
														
					temp_srs200 = self.readSRS200(EN=1, SF=0.01, PRINT=0)
					temp_speed = self.readSpeedEncoder(EN=1, PRINT=0)
					if(DEBUG):
						print("time:", temp_time, end='\t');
						print("err:", temp_err, end='\t\t');
						print("step:", temp_step, end='\t');
						print("PD_T:", temp_PD_temperature);
						
					
					self.kal_flag = globals.kal_status
					''' Kalmman filter'''
					'''------update------'''
					k[i] = p_p[i]/(p_p[i] + self.kal_R) #k_n
					x[i] = x_p[i] + k[i]*(temp_err - x_p[i])  #x_nn
					# x[i] = x_p[i] + k[i]*(temp_nano33_wz - x_p[i])  #x_nn
					y[i] = y_p[i] + k[i]*(temp_step - y_p[i])  #y_nn
					p[i] = (1 - k[i])*p_p[i] #p_nn

					'''------predict------'''
					x_p[i+1] = x[i]
					y_p[i+1] = y[i]
					p_p[i+1] = p[i] + self.kal_Q
					
					''' end of kalmman filter'''
					
					
					time_s = np.append(time_s[1:], temp_time)
					srs200 = np.append(srs200[1:], temp_srs200)
					nano33_wz = np.append(nano33_wz[1:], temp_nano33_wz)
					speed = np.append(speed[1:], temp_speed)
					ax = np.append(ax[1:], temp_adxl355_x)
					ay = np.append(ay[1:], temp_adxl355_y)
					az = np.append(az[1:], temp_adxl355_z)
					PD_temperature = np.append(PD_temperature[1:], temp_PD_temperature)
					if(self.kal_flag == True):
						step = np.append(step[1:], y[i]) #kalmman filter
					else:
						step = np.append(step[1:], temp_step)
				#end of for
				# print('action: ', end='\t')
				# print(len(time_s), end='\t')
				# print(len(err), end='\t')
				# print(len(step), end='\t')
				# print(len(PD_temperature), end='\t')
				# print(self.crc_fail_cnt)
				if(globals.PRINT_MODE):
					self.data_update6.emit(temp_nano33_wx, temp_nano33_wy, temp_nano33_wz, 
											   temp_nano33_ax, temp_nano33_ay, temp_nano33_az)
				else:
					# print('self.timer_rst_succeed:', self.timer_rst_succeed)
					if(self.timer_rst_succeed):
						
						self.data_update9.emit(time_s, srs200, step, PD_temperature, nano33_wz, speed,
						ax, ay, az
						)
				if(self.stopFlag):
					self.runFlag = 0
					print('stopFlag')
				# self.valid_cnt = self.valid_cnt + 1
				# if(self.valid_cnt == 1):
					# self.valid_flag = 1
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
		self.timer_rst_succeed = 0
		# self.oReader.isRun = False
		# self.oReader.join()
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
			
	def convert2Sign_srs200(self, datain) :
		shift_data = (datain[3]<<24|datain[2]<<16|datain[1]<<8|datain[0])
		if((datain[3]>>7) == 1):
			return (shift_data - (1<<32))
		else :
			return shift_data
			
# if "__main__" == __name__:
