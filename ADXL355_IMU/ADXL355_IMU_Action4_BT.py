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

THREAD_DELY = sys.float_info.min
DEBUG = 0
DEBUG_COM = 1
TEST_MODE = 0
# MV_MODE = 1

class IMU_Action(QThread):
	update_COMArray = pyqtSignal(object)
	fog_update = pyqtSignal(object,object)
	fog_update2 = pyqtSignal(object,object, object)
	fog_update4 = pyqtSignal(object, object, object, object, object)
	fog_update7 = pyqtSignal(object, object, object, object, object, object, object)
	fog_update8 = pyqtSignal(object, object, object, object, object, object, object, object)
	fog_update9 = pyqtSignal(object, object, object, object, object, object, object, object, object)
	fog_update11 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object)
	fog_update12 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object)
	fog_update13 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object, object)
	fog_finished = pyqtSignal()
	'''當valid_cnt累加到valid_cnt_num時valid_flag會變1，此時才會送數據到main，目的為了避開程式一開始亂跳的情形 '''
	valid_flag = 0
	drop_cnt=0
	valid_cnt = 0
	valid_cnt_num = 5
	TIME_PERIOD = 0.01
	''' 計算一定的點數後再傳到main作圖，點數太小的話buffer會累積造成lag'''
	data_frame_update_point = 20
	''' run glag 初始值'''
	runFlag = 0
	runFlag_cali = 0
	''' check byte '''
	check_byte = 170
	check_byte2 = 171
	# wxVth = 0
	# offset_wy = 0
	# wyVth = 0
	# offset_wz = 0
	# offset_wz200 = 0
	# wzVth = 0
	# offset_ax = 0
	# offset_ADax = 0
	# axVth = 0
	# offset_ay = 0
	# offset_ADay = 0
	# ayVth = 0
	''' buffer size 會傳到main做monitor'''
	bufferSize = 0
	dt_init_flag = 1
	MV_MODE = 0
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
		
		if self.runFlag or self.runFlag_cali:
			self.COM.port.flushInput()
			while self.runFlag or self.runFlag_cali:
				valid_byte = 1
				if(drop_flag):
					drop_flag = 0
					print("drop occurred!")
					self.drop_cnt = self.drop_cnt+1
					self.COM.port.flushInput()
				if(not TEST_MODE):
					while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*23))) : #rx buffer 不到 arduino傳來的總byte數*data_frame_update_point時不做任何事
						# print(self.COM.port.inWaiting())
						pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					''' 當arduino送來的第一個check byte不符合時則檢查到對時才往下'''
					if(not TEST_MODE): 
						val = self.COM.read1Binary()
						while(val[0] != self.check_byte):
							val = self.COM.read1Binary()
					'''--------------------------------------------------------- '''
					#read new value
					if(TEST_MODE):
						temp_Nano33_ax = np.random.randn()
						temp_Nano33_ay = np.random.randn()
						temp_Nano33_az = np.random.randn()
						temp_Nano33_wx = np.random.randn()*100
						temp_Nano33_wy = np.random.randn()*100
						temp_Nano33_wz = np.random.randn()*100
						temp_dt = cnt
						temp_SRS200_wz = np.random.randn()*100
						temp_PP_wz = np.random.randn()
						temp_Adxl355_ax = np.random.randn()
						temp_Adxl355_ay = np.random.randn()
						temp_Adxl355_az = np.random.randn()
						cnt += 10000
						# time.sleep(0.01)
						# for i in range(100):
							# print(i, end=', ')
							# print(self.COM.read1Binary()[0])
					else:
						# temp_Nano33_ax = self.COM.read2Binary()
						# temp_Nano33_ay = self.COM.read2Binary()
						# temp_Nano33_az = self.COM.read2Binary()
						# temp_Nano33_wx = self.COM.read2Binary()
						# temp_Nano33_wy = self.COM.read2Binary()
						# temp_Nano33_wz = self.COM.read2Binary()
						temp_Nano33_ax = np.random.randn()
						temp_Nano33_ay = np.random.randn()
						temp_Nano33_az = np.random.randn()
						temp_Nano33_wx = np.random.randn()*100
						temp_Nano33_wy = np.random.randn()*100
						temp_Nano33_wz = np.random.randn()*100
						
						temp_dt = self.COM.read4Binary()
						temp_SRS200_wz = self.COM.read5Binary()
						if(temp_SRS200_wz[0] != 192):
								temp_SRS200_wz = np.array([0,0,0,0])
						else:
							temp_SRS200_wz = temp_SRS200_wz[1:]
						temp_PP_wz = self.COM.read5Binary()
						if(temp_PP_wz[0] != 193):
								temp_PP_wz = np.array([0,0,0,0])
						else:
							temp_PP_wz = temp_PP_wz[1:]
						temp_Adxl355_ax = self.COM.read4Binary()
						if(temp_Adxl355_ax[0] != 194):
								temp_Adxl355_ax = np.array([0,0,0])
						else:
							temp_Adxl355_ax = temp_Adxl355_ax[1:]
						temp_Adxl355_ay = self.COM.read4Binary()
						if(temp_Adxl355_ay[0] != 195):
								temp_Adxl355_ay = np.array([0,0,0])
						else:
							temp_Adxl355_ay = temp_Adxl355_ay[1:]
						temp_Adxl355_az = self.COM.read4Binary()
						if(temp_Adxl355_az[0] != 196):
								temp_Adxl355_az = np.array([0,0,0])
						else:
							temp_Adxl355_az = temp_Adxl355_az[1:]
						val2 = self.COM.read1Binary()
					
					# print(self.COM.port.inWaiting())
						
					if(DEBUG_COM):
						# print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
						# print('buffer: ',end=', ' )
						# print(self.bufferSize)
						if(not TEST_MODE):
							print('val[0]: ',end=' ' )
							print(val[0],end=' ' )
							print('va2[0]: ',end=' ' ) 
							print(val2[0],end=' ')
							print('drop_cnt: ',end=' ' )
							print(self.drop_cnt)
						# print('temp_Nano33_a: ');
						# print(temp_Nano33_ax[0], end='\t')
						# print(temp_Nano33_ax[1], end='\t')
						# print(temp_Nano33_ay[0], end='\t')
						# print(temp_Nano33_ay[1], end='\t')
						# print(temp_Nano33_az[0], end='\t')
						# print(temp_Nano33_az[1])
						# print('temp_Nano33_w: ');
						# print(temp_Nano33_wx[0], end='\t')
						# print(temp_Nano33_wx[1], end='\t')
						# print(temp_Nano33_wy[0], end='\t')
						# print(temp_Nano33_wy[1], end='\t')
						# print(temp_Nano33_wz[0], end='\t')
						# print(temp_Nano33_wz[1])
						# print('temp_dt: ');
						# print(temp_dt[0], end='\t')
						# print(temp_dt[1], end='\t')
						# print(temp_dt[2], end='\t')
						# print(temp_dt[3], end='\t')
						# print(temp_dt[0]<<24 | temp_dt[1]<<16 |temp_dt[2]<<8 | temp_dt[3])
						# print('temp_PP_wz: ');
						# print(temp_PP_wz[0], end='\t')
						# print(temp_PP_wz[1], end='\t')
						# print(temp_PP_wz[2], end='\t')
						# print(temp_PP_wz[3], end='\t')
						# print(temp_PP_wz[0]<<24 | temp_PP_wz[1]<<16 |temp_PP_wz[2]<<8 | temp_PP_wz[3])
						# print('temp_SRS200_w: ');
						# print(temp_SRS200_wz[0], end='\t')
						# print(temp_SRS200_wz[1], end='\t')
						# print(temp_SRS200_wz[2], end='\t')
						# print(temp_SRS200_wz[3])
						# print('temp_Adxl355_ax: ');
						# print(temp_Adxl355_ax[0], end='\t')
						# print(temp_Adxl355_ax[1], end='\t')
						# print(temp_Adxl355_ax[2])
						# print('temp_Adxl355_ay: ');
						# print(temp_Adxl355_ay[0], end='\t')
						# print(temp_Adxl355_ay[1], end='\t')
						# print(temp_Adxl355_ay[2])
						# print(temp_Adxl355_az[0], end='\t')
						# print(temp_Adxl355_az[1], end='\t')
						# print(temp_Adxl355_az[2])
						
					''' 當arduino送來的第一個check byte不符合時則跳出for loop，發生在arduino傳來的時間爆掉時'''
					if(not TEST_MODE):
						if(val2[0] != self.check_byte2):
							valid_byte = 0
							valid_flag = 0
							self.valid_cnt = (self.valid_cnt_num-2)
							drop_flag = 1
							break #break for loop
						
					if(valid_byte): 
						if(not TEST_MODE):
							#conversion
							# temp_Nano33_ax = self.convert2Sign_2B(temp_Nano33_ax)
							# temp_Nano33_ay = self.convert2Sign_2B(temp_Nano33_ay)
							# temp_Nano33_az = self.convert2Sign_2B(temp_Nano33_az)
							# temp_Nano33_wx = self.convert2Sign_2B(temp_Nano33_wx)
							# temp_Nano33_wy = self.convert2Sign_2B(temp_Nano33_wy)
							# temp_Nano33_wz = self.convert2Sign_2B(temp_Nano33_wz)
							temp_dt = self.convert2Unsign_4B(temp_dt)
							temp_SRS200_wz = self.convert2Sign_4B(temp_SRS200_wz)
							
							temp_PP_wz = self.convert2Unsign_4B(temp_PP_wz)
							temp_Adxl355_ax =self.convert2Sign_3B(temp_Adxl355_ax)
							temp_Adxl355_ay =self.convert2Sign_3B(temp_Adxl355_ay)
							temp_Adxl355_az =self.convert2Sign_3B(temp_Adxl355_az)
						
						# if(DEBUG_COM):
							# print(temp_dt);
						
						if(temp_dt < temp_dt_before):
							temp_offset = math.ceil(abs(temp_dt - temp_dt_before)/(1<<32))*(1<<32)
							temp_dt = temp_dt + temp_offset
							temp_dt_before = temp_dt
						
						#calaculate MV value
						if(self.MV_MODE):
							data_Nano33_ax_sum = data_Nano33_ax_sum - data_Nano33_ax[0]
							data_Nano33_ax_sum = data_Nano33_ax_sum + temp_Nano33_ax
							data_Nano33_ax_MV = data_Nano33_ax_sum/self.data_frame_update_point
							
							data_Nano33_ay_sum = data_Nano33_ay_sum - data_Nano33_ay[0]
							data_Nano33_ay_sum = data_Nano33_ay_sum + temp_Nano33_ay
							data_Nano33_ay_MV = data_Nano33_ay_sum/self.data_frame_update_point
							
							data_Nano33_az_sum = data_Nano33_az_sum - data_Nano33_az[0]
							data_Nano33_az_sum = data_Nano33_az_sum + temp_Nano33_az
							data_Nano33_az_MV = data_Nano33_az_sum/self.data_frame_update_point
							
							data_Nano33_wx_sum = data_Nano33_wx_sum - data_Nano33_wx[0]
							data_Nano33_wx_sum = data_Nano33_wx_sum + temp_Nano33_wx
							data_Nano33_wx_MV = data_Nano33_wx_sum/self.data_frame_update_point
							
							data_Nano33_wy_sum = data_Nano33_wy_sum - data_Nano33_wy[0]
							data_Nano33_wy_sum = data_Nano33_wy_sum + temp_Nano33_wy
							data_Nano33_wy_MV = data_Nano33_wy_sum/self.data_frame_update_point
							
							data_Nano33_wz_sum = data_Nano33_wz_sum - data_Nano33_wz[0]
							data_Nano33_wz_sum = data_Nano33_wz_sum + temp_Nano33_wz
							data_Nano33_wz_MV = data_Nano33_wz_sum/self.data_frame_update_point
							
							data_SRS200_wz_sum = data_SRS200_wz_sum - data_SRS200_wz[0]
							data_SRS200_wz_sum = data_SRS200_wz_sum + temp_SRS200_wz
							data_SRS200_wz_MV = data_SRS200_wz_sum/self.data_frame_update_point
							
							data_PP_wz_sum = data_PP_wz_sum - data_PP_wz[0]
							data_PP_wz_sum = data_PP_wz_sum + temp_PP_wz
							data_PP_wz_MV = data_PP_wz_sum/self.data_frame_update_point
							
							data_Adxl355_ax_sum = data_Adxl355_ax_sum - data_Adxl355_ax[0]
							data_Adxl355_ax_sum = data_Adxl355_ax_sum + temp_Adxl355_ax
							data_Adxl355_ax_MV = data_Adxl355_ax_sum/self.data_frame_update_point
							
							data_Adxl355_ay_sum = data_Adxl355_ay_sum - data_Adxl355_ay[0]
							data_Adxl355_ay_sum = data_Adxl355_ay_sum + temp_Adxl355_ay
							data_Adxl355_ay_MV = data_Adxl355_ay_sum/self.data_frame_update_point
							
							data_Adxl355_az_sum = data_Adxl355_az_sum - data_Adxl355_az[0]
							data_Adxl355_az_sum = data_Adxl355_az_sum + temp_Adxl355_az
							data_Adxl355_az_MV = data_Adxl355_az_sum/self.data_frame_update_point
							
							val_Nano33_ax = data_Nano33_ax_MV
							val_Nano33_ay = data_Nano33_ay_MV
							val_Nano33_az = data_Nano33_az_MV
							val_Adxl355_ax = data_Adxl355_ax_MV
							val_Adxl355_ay = data_Adxl355_ay_MV
							val_Adxl355_az = data_Adxl355_az_MV
							val_Nano33_wx = data_Nano33_wx_MV
							val_Nano33_wy = data_Nano33_wy_MV
							val_Nano33_wz = data_Nano33_wz_MV
							val_SRS200_wz = data_SRS200_wz_MV
							val_PP_wz = data_PP_wz_MV
							
						else: 
							val_Nano33_ax = temp_Nano33_ax
							val_Nano33_ay = temp_Nano33_ay
							val_Nano33_az = temp_Nano33_az
							val_Adxl355_ax = temp_Adxl355_ax
							val_Adxl355_ay = temp_Adxl355_ay
							val_Adxl355_az = temp_Adxl355_az
							val_Nano33_wx = temp_Nano33_wx
							val_Nano33_wy = temp_Nano33_wy
							val_Nano33_wz = temp_Nano33_wz
							val_SRS200_wz = temp_SRS200_wz
							val_PP_wz = temp_PP_wz
						
						
						data_Nano33_ax = np.append(data_Nano33_ax[1:], val_Nano33_ax)
						data_Nano33_ay = np.append(data_Nano33_ay[1:], val_Nano33_ay)
						data_Nano33_az = np.append(data_Nano33_az[1:], val_Nano33_az)
						data_Adxl355_ax = np.append(data_Adxl355_ax[1:], val_Adxl355_ax)
						data_Adxl355_ay = np.append(data_Adxl355_ay[1:], val_Adxl355_ay)
						data_Adxl355_az = np.append(data_Adxl355_az[1:], val_Adxl355_az)
						data_Nano33_wx = np.append(data_Nano33_wx[1:], val_Nano33_wx)
						data_Nano33_wy = np.append(data_Nano33_wy[1:], val_Nano33_wy)
						data_Nano33_wz = np.append(data_Nano33_wz[1:], val_Nano33_wz)
						data_SRS200_wz = np.append(data_SRS200_wz[1:], val_SRS200_wz)
						data_PP_wz = np.append(data_PP_wz[1:], val_PP_wz)
						
						# dt_new = dt_old + i*self.TIME_PERIOD
						dt = np.append(dt[1:], temp_dt)
						# print(temp_dt, end=', ')
						# print(dt_init, end=', ')
						# print(dt)
				#end of for loop
				self.valid_cnt = self.valid_cnt + 1
				self.bufferSize = self.COM.port.inWaiting()
				if(DEBUG):
					print('bufferSize: ', self.bufferSize)
					# print('len(data): ', len(data_SRS200_wz))
					# print('data_Nano33_ax: ', data_Nano33_ax)
					# print('data_Nano33_ay: ', data_Nano33_ay)
					# print('data_Nano33_az: ', data_Nano33_az)
					# print('data_Nano33_wx: ', data_Nano33_wx)
					# print('data_Nano33_wy: ', data_Nano33_wy)
					# print('data_Nano33_wz: ', data_Nano33_wz)
					# print('data_Adxl355_ax: ', data_Adxl355_ax)
					# print('data_Adxl355_ay: ', data_Adxl355_ay)
					# print('data_Adxl355_az: ', data_Adxl355_az)
					# print('data_SRS200_wz: ', data_SRS200_wz)	
					# print('data_PP_wz: ', data_PP_wz)					
					pass
				if(self.valid_cnt == 1):
					temp_dt_before = dt[0]
					
				if(self.valid_cnt == self.valid_cnt_num):
					self.valid_flag = 1
				
				if(self.valid_flag):
					if(self.dt_init_flag):
						self.dt_init_flag = 0
						dt_init = dt[0]
					if(self.runFlag):
						self.fog_update8.emit(dt-dt_init, data_SRS200_wz, data_Nano33_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay,
											data_Nano33_ax, data_Nano33_ay)
						time.sleep(THREAD_DELY)
					elif(self.runFlag_cali):
						self.fog_update11.emit(data_SRS200_wz, data_Nano33_wx, data_Nano33_wy, data_Nano33_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay,
											data_Adxl355_az, data_Nano33_ax, data_Nano33_ay, data_Nano33_az)
						time.sleep(THREAD_DELY)
			#end of while self.runFlag:
			self.fog_finished.emit()
			temp_dt_before = 0
			self.valid_flag = 0
			self.valid_cnt = 0
			self.dt_init_flag = 1
			
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
			
