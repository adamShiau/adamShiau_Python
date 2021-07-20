import os
import sys
sys.path.append("../")
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
# import IMU_Globals as globals

'''sensor conversion factor '''
SENS_ADXL355		= 0.0000156 #8g
SENS_NANO33_XLM 	= 0.000122 #+/- 4g
SENS_NANO33_GYRO 	= 0.00763 #+/- 250dps

THREAD_DELY = sys.float_info.min
DEBUG = 0
DEBUG_COM = 0
TEST_MODE = 0
DISABLE_PP = 0
DISABLE_VBOX = 0
DISABLE_NANO33_W = 0
DISABLE_NANO33_A = 0
DISABLE_SRS200 = 0
DISABLE_ADXL355 = 0
SRS_HEADER = 192
SRS_OFFSET_7 = 13
class IMU_Action(QThread):
	update_COMArray = pyqtSignal(object)
	fog_update = pyqtSignal(object,object)
	fog_update2 = pyqtSignal(object,object, object)
	fog_update4 = pyqtSignal(object, object, object, object, object)
	fog_update6 = pyqtSignal(object, object, object, object, object, object)
	fog_update7 = pyqtSignal(object, object, object, object, object, object, object)
	fog_update8 = pyqtSignal(object, object, object, object, object, object, object, object)
	fog_update9 = pyqtSignal(object, object, object, object, object, object, object, object, object)
	fog_update10 = pyqtSignal(object, object, object, object, object, object, object, object, object, object)
	fog_update11 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object)
	fog_update12 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object)
	fog_update13 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object, object)
	fog_update20 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object )
	fog_finished = pyqtSignal()
	'''當valid_cnt累加到valid_cnt_num時valid_flag會變1，此時才會送數據到main，目的為了避開程式一開始亂跳的情形 '''
	valid_flag = 0
	drop_cnt=0
	valid_cnt = 0
	valid_cnt_num = 5
	TIME_PERIOD = 0.01
	''' 計算一定的點數後再傳到main作圖，點數太小的話buffer會累積造成lag'''
	data_frame_update_point = 1
	''' run glag 初始值'''
	runFlag = 0
	runFlag_cali = 0
	''' check byte '''
	check_byte = 170
	check_byte2 = 171
	''' buffer size 會傳到main做monitor'''
	bufferSize = 0
	dt_init_flag = 1
	MV_MODE = 0
	dt_old = 0
	dt_offset = 0
	def __init__(self, loggername):	
		super().__init__()
		self.COM = UART()
		self.logger = logging.getLogger(loggername)
		# self.SaveFileName = ''
		
	# def updateADXL_IMUnGYRO(self, MV_MODE=1):
	def run(self):
		print('---------------------')
		print('start run!')
		data_Nano33_ax = np.zeros(self.data_frame_update_point)
		data_Nano33_ay = np.zeros(self.data_frame_update_point)
		data_Nano33_az = np.zeros(self.data_frame_update_point)
		data_Adxl355_ax = np.zeros(self.data_frame_update_point)
		data_Adxl355_ay = np.zeros(self.data_frame_update_point)
		data_Adxl355_az = np.zeros(self.data_frame_update_point)
		data_Nano33_wx = np.zeros(self.data_frame_update_point)
		data_Nano33_wy = np.zeros(self.data_frame_update_point)
		data_Nano33_wz = np.zeros(self.data_frame_update_point)
		data_SRS200_wz = np.zeros(self.data_frame_update_point)
		data_PP_wz = np.zeros(self.data_frame_update_point)
		data_IMU_speed = np.zeros(self.data_frame_update_point)
		# data_VBOX_temp = np.zeros(146)
		# data_VBOX_temp = np.empty
		data_T = np.zeros(self.data_frame_update_point)
		dt = np.zeros(self.data_frame_update_point)
		data_Nano33_ax_sum = 0
		data_Nano33_ay_sum = 0
		data_Nano33_az_sum = 0
		data_Adxl355_ax_sum = 0
		data_Adxl355_ay_sum = 0
		data_Adxl355_az_sum = 0
		data_Nano33_wx_sum = 0
		data_Nano33_wy_sum = 0
		data_Nano33_wz_sum = 0
		data_SRS200_wz_sum = 0
		data_PP_wz_sum = 0
		temp_dt_before = 0
		temp_offset = 0
		drop_flag = 0
		dt_init = 0
		cnt = 0
		''' for kalmman filter'''
		#initial guess value
		kal_init_SRS200_wz = 0
		kal_init_Adxl355_ax = 0
		kal_init_Adxl355_ay = 0
		kal_init_Adxl355_az = 0
		kal_init_PP_wz = 0
		kal_init_Nano33_wx = 0
		kal_init_Nano33_wy = 0
		kal_init_Nano33_wz = 0
		kal_init_IMU_speed = 0
		p0 = 0
		#Q:process variance
		#R:measure variance
		# print('action kal_Q:', globals.kal_Q)
		# print('action kal_R:', globals.kal_R)
		# kal_p_SRS200_wz = np.zeros(self.data_frame_update_point+1)
		# kal_p_Adxl355_ax = np.zeros(self.data_frame_update_point+1)
		# kal_p_Adxl355_ay = np.zeros(self.data_frame_update_point+1)
		# kal_p_Adxl355_az = np.zeros(self.data_frame_update_point+1)
		# kal_p_PP_wz = np.zeros(self.data_frame_update_point+1)
		# kal_p_Nano33_wx = np.zeros(self.data_frame_update_point+1)
		# kal_p_Nano33_wy = np.zeros(self.data_frame_update_point+1)
		# kal_p_Nano33_wz = np.zeros(self.data_frame_update_point+1)
		# kal_p_IMU_speed = np.zeros(self.data_frame_update_point+1)
		# p_p = np.zeros(self.data_frame_update_point+1)
		
		# kal_SRS200_wz = np.zeros(self.data_frame_update_point)
		# kal_PP_wz = np.zeros(self.data_frame_update_point)
		# kal_Nano33_wx = np.zeros(self.data_frame_update_point)
		# kal_Nano33_wy = np.zeros(self.data_frame_update_point)
		# kal_Nano33_wz = np.zeros(self.data_frame_update_point)
		# kal_IMU_speed = np.zeros(self.data_frame_update_point)
		# kal_Adxl355_ax = np.zeros(self.data_frame_update_point)
		# kal_Adxl355_ay = np.zeros(self.data_frame_update_point)
		# kal_Adxl355_az = np.zeros(self.data_frame_update_point)
		# p = np.zeros(self.data_frame_update_point)
		# k = np.zeros(self.data_frame_update_point)
		
		# p0 = p0^2
		# kal_p_SRS200_wz[self.data_frame_update_point] = kal_init_SRS200_wz
		# kal_p_PP_wz[self.data_frame_update_point] = kal_init_PP_wz
		# kal_p_Nano33_wx[self.data_frame_update_point] = kal_init_Nano33_wx
		# kal_p_Nano33_wy[self.data_frame_update_point] = kal_init_Nano33_wy
		# kal_p_Nano33_wz[self.data_frame_update_point] = kal_init_Nano33_wz
		# kal_p_IMU_speed[self.data_frame_update_point] = kal_init_IMU_speed
		# kal_p_Adxl355_ax[self.data_frame_update_point] = kal_init_Adxl355_ax
		# kal_p_Adxl355_ay[self.data_frame_update_point] = kal_init_Adxl355_ay
		# kal_p_Adxl355_az[self.data_frame_update_point] = kal_init_Adxl355_az
		# p_p[self.data_frame_update_point] = p0 + globals.kal_Q
		# ''' '''
		
		if self.runFlag or self.runFlag_cali:
			self.COM.port.flushInput()
			while self.runFlag or self.runFlag_cali:
				valid_byte = 1
				# if(drop_flag):
					# drop_flag = 0
					# print("drop occurred!")
					# self.drop_cnt = self.drop_cnt+1
					# self.COM.port.flushInput()
				# if(not TEST_MODE):
					# while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*34))) : #rx buffer 不到 arduino傳來的總byte數*data_frame_update_point時不做任何事
						# print(self.COM.port.inWaiting())
						# pass
						
				# for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					# ''' 當arduino送來的第一個check byte不符合時則檢查到對時才往下'''
				SRS200 = np.empty(0)
				data_SRS200 = np.empty(0)
				VBOX = np.empty(0)
				
				#1st check byte 
				val = self.COM.read1Binary()
				
				while(val[0] != self.check_byte):
					val = self.COM.read1Binary()
				# print('val[0]: ', val[0], end='\t')
				'''--------------------------------------------------------- '''
				#read new value
				temp_dt = self.COM.read4Binary()
				
				temp_Adxl355_ax = self.COM.read3Binary()
				temp_Adxl355_ay = self.COM.read3Binary()
				temp_Adxl355_az = self.COM.read3Binary()
				temp_T = self.COM.read2Binary()

				temp_Nano33_ax = self.COM.read2Binary()
				temp_Nano33_ay = self.COM.read2Binary()
				temp_Nano33_az = self.COM.read2Binary()
					
				temp_Nano33_wx = self.COM.read2Binary()
				temp_Nano33_wy = self.COM.read2Binary()
				temp_Nano33_wz = self.COM.read2Binary()
						
				#2nd check byte
				val2 = self.COM.read1Binary()
				# print('val2[0]: ', val2[0])
				if(val2[0] != self.check_byte2):
					valid_byte = 0
					
				if(DEBUG_COM):
					# print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
					# print('buffer: ',end=', ' )
					# print(self.bufferSize)
					print('temp_dt: ', end='\t')
					print(temp_dt[0], end='\t')
					print(temp_dt[1], end='\t')
					print(temp_dt[2], end='\t')
					print(temp_dt[3], end='\t')
					
				if(valid_byte): 
					#conversion
					temp_dt = self.convert2Unsign_4B(temp_dt)
					
					temp_Adxl355_ax =self.convert2Sign_3B(temp_Adxl355_ax)*SENS_ADXL355
					temp_Adxl355_ay =self.convert2Sign_3B(temp_Adxl355_ay)*SENS_ADXL355
					temp_Adxl355_az =self.convert2Sign_3B(temp_Adxl355_az)*SENS_ADXL355
					temp_T = self.convert2Unsign_2B(temp_T)
					
					temp_Nano33_ax = self.convert2Sign_2B(temp_Nano33_ax)*SENS_NANO33_XLM
					temp_Nano33_ay = self.convert2Sign_2B(temp_Nano33_ay)*SENS_NANO33_XLM
					temp_Nano33_az = self.convert2Sign_2B(temp_Nano33_az)*SENS_NANO33_XLM
					
					temp_Nano33_wx = self.convert2Sign_2B(temp_Nano33_wx)*SENS_NANO33_GYRO
					temp_Nano33_wy = self.convert2Sign_2B(temp_Nano33_wy)*SENS_NANO33_GYRO
					temp_Nano33_wz = self.convert2Sign_2B(temp_Nano33_wz)*SENS_NANO33_GYRO
					
					if(DEBUG):
						print('bufferSize: ', self.bufferSize, end='\n\n')
						print('temp_dt: ', temp_dt, end='\n\n')
						print('data_Adxl355: ', round(temp_Adxl355_ax,3), end='\t')
						print(round(temp_Adxl355_ay,3), end='\t')
						print(round(temp_Adxl355_az,3), end='\n\n')
						print('data_Nano33: ', round(temp_Nano33_ax,3), end='\t')
						print(round(temp_Nano33_ay,3), end='\t')
						print(round(temp_Nano33_az,3), end='\n\n')
						print('data_Nano33_w: ', round(temp_Nano33_wx,3), end='\t')
						print(round(temp_Nano33_wy,3), end='\t')
						print(round(temp_Nano33_wz,3), end='\n\n')
						pass
					
				self.bufferSize = self.COM.port.inWaiting()
				
				# if(self.valid_cnt == 1):
					# temp_dt_before = dt[0]
					
				# if(self.valid_cnt == self.valid_cnt_num):
					# self.valid_flag = 1
				
				# if(self.valid_flag):
					# if(self.dt_init_flag):
						# self.dt_init_flag = 0
						# dt_init = dt[0]
						
						
				if(self.runFlag) :
					self.fog_update10.emit(	temp_dt, temp_Adxl355_ax, temp_Adxl355_ay, temp_Adxl355_az,
											temp_Nano33_ax, temp_Nano33_ay, temp_Nano33_az,
											temp_Nano33_wx, temp_Nano33_wy, temp_Nano33_wz) 
					# time.sleep(THREAD_DELY)
				# elif(self.runFlag_cali):
					# self.fog_update13.emit(0, 0, 0, 0, 0, 0, 0,
										# 0, 0, 0, 0, 0, 0)
					# time.sleep(THREAD_DELY)
			#end of while self.runFlag:
			self.fog_finished.emit()
			temp_dt_before = 0
			self.valid_flag = 0
			self.valid_cnt = 0
			self.dt_init_flag = 1
			self.dt_old = 0
			self.dt_offset = 0
			
	def convert2Sign_4B(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		if((datain[0]>>7) == 1):
			return (shift_data - (1<<32))
		else :
			return shift_data
		
	def convert2Sign_3B(self, datain) :
		shift_data = (datain[0]<<12|datain[1]<<4|datain[2]>>4)
		if((datain[0]>>7) == 1):
			return (shift_data - (1<<20))
		else :
			return shift_data
		
	def convert2Unsign_4B(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		return shift_data
		
	def convert2Unsign_3B(self, datain) :
		shift_data = (datain[0]<<16|datain[1]<<8|datain[2])
		return shift_data
			
	def convert2Unsign_2B(self, datain) :
		shift_data = (datain[0]<<8|datain[1])
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
			
