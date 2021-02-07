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
TEST_MODE = 0
DEBUG = 0
DEBUG_COM = 1
TIME_PERIOD = 0.01

class COMRead_Action(QThread):
	update1 = pyqtSignal(object)
	update2 = pyqtSignal(object, object)
	finished = pyqtSignal()
	data_frame_update_point = 10
	bufferSize = 0
	check_byte = 170
	'''當valid_cnt累加到valid_cnt_num時valid_flag會變1，此時才會送數據到main，目的為了避開程式一開始亂跳的情形 '''
	valid_flag = 0
	valid_cnt = 0
	valid_cnt_num = 3
	
	dt_init_flag = 1
	def __init__(self):	
		super().__init__()
		self.COM = UART()
		
	def run(self):
		data = np.zeros(self.data_frame_update_point)
		dt = np.zeros(self.data_frame_update_point)
		cnt = 0
		dt_init = 0
		temp_dt_before = 0
		temp_offset = 0
		if self.runFlag :
			self.COM.port.flushInput()
			while self.runFlag:
				if(not TEST_MODE):
					while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*9))) : #rx buffer 不到 arduino傳來的總byte數*data_frame_update_point時不做任何事
						# print(self.COM.port.inWaiting())
						pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					if(not TEST_MODE): 
						val = self.COM.read1Binary()
						while(val[0] != self.check_byte):
							val = self.COM.read1Binary()
					'''--------------------------------------------------------- '''
					#read new value
					if(TEST_MODE):
						temp_data = np.random.randn()
						temp_dt = cnt
						cnt += 10000
						time.sleep(0.01)
					else:
						temp_dt = self.COM.read4Binary()
						temp_data = self.COM.read4Binary()
						
					
						
					print(self.COM.port.inWaiting())
						
					if(DEBUG_COM):
						print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
						print('buffer: ',end=', ' )
						print(self.bufferSize)
						if(not TEST_MODE):
							print('val[0]: ',end=', ' )
							print(val[0])
						print('temp_data: ', end='\t')
						print(temp_data[0], end='\t')
						print(temp_data[1], end='\t')
						print(temp_data[2], end='\t')
						print(temp_data[3])
						print('temp_dt: ', end='\t')
						print(temp_dt[0], end='\t')
						print(temp_dt[1], end='\t')
						print(temp_dt[2], end='\t')
						print(temp_dt[3])
						
					if(not TEST_MODE):
						#conversion
						temp_data = self.convert2Sign_4B(temp_data)
						temp_dt = self.convert2Unsign_4B(temp_dt)
						
					if(temp_dt < temp_dt_before):
						temp_offset = math.ceil(abs(temp_dt - temp_dt_before)/(1<<32))*(1<<32)
						temp_dt = temp_dt + temp_offset
						temp_dt_before = temp_dt
						
					if(DEBUG_COM):
						print('temp_data: ', end='\t')
						print(temp_data)
						print('temp_dt: ', end='\t')
						print(temp_dt)
					data = np.append(data[1:], temp_data)
					dt = np.append(dt[1:], temp_dt)
				#end of for loop
				self.valid_cnt = self.valid_cnt + 1
				
				if(self.valid_cnt == self.valid_cnt_num):
					self.valid_flag = 1
				
				self.bufferSize = self.COM.port.inWaiting()
				
				if(DEBUG):
					print('bufferSize: ', self.bufferSize)
					print('len(data): ', len(data))
					pass
				if(self.valid_cnt == 1):
					temp_dt_before = dt[0]
					
				if(self.valid_flag):
					if(self.dt_init_flag):
						self.dt_init_flag = 0
						dt_init = dt[0]
				
					if(self.runFlag):
						self.update2.emit(dt-dt_init, data)
						time.sleep(THREAD_DELY)
			#end of while self.runFlag:
			self.valid_cnt = 0
			self.valid_flag = 0
			temp_dt_before = 0
			self.dt_init_flag = 1
			self.finished.emit()
		
	def convert2Sign_4B(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		# print(shift_data)
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

			
