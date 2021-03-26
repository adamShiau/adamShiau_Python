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
DEBUG_COM = 0
TIME_PERIOD = 0.01

class COMRead_Action(QThread):
	update1 = pyqtSignal(object)
	update2 = pyqtSignal(object, object)
	finished = pyqtSignal()
	data_frame_update_point = 1
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
		dt_old = 0
		if self.runFlag :
			self.COM.port.flushInput()
			while self.runFlag:
				if(not TEST_MODE):
					while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*9))) : #rx buffer 不到 arduino傳來的總byte數*data_frame_update_point時不做任何事
						# print(self.COM.port.inWaiting())
						pass
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					# if(not TEST_MODE): 
						# val = self.COM.read1Binary()
						# while(val[0] != self.check_byte):
							# val = self.COM.read1Binary()
					'''--------------------------------------------------------- '''
					#read new value
					if(TEST_MODE):
						temp_data = np.random.randn()
						temp_dt = cnt
						cnt += 10000
						time.sleep(0.01)
					else:
						data_in = self.COM.read4Binary()
						temp = self.COM.read2Binary()
							
						data_in = self.convert2Sign_4B(data_in)
						temp = self.convert2Sign_2B(temp)
						
						# print('data_in:', data_in)
					# print(self.COM.port.inWaiting())
						
					# data = np.append(data, data_in)
					dt_new = dt_old + 0.01
					# dt = np.append(dt, dt_new)
					
					dt_old = dt_new
					
					data = np.append(data[1:], data_in)
					dt = np.append(dt[1:], dt_new)
					# print(dt)
				#end of for loop
				self.valid_cnt = self.valid_cnt + 1
				# print('len(data):', len(data))
				if(self.valid_cnt == self.valid_cnt_num):
					self.valid_flag = 1
				
				self.bufferSize = self.COM.port.inWaiting()
				
				
				if(self.runFlag):
					self.update2.emit(dt, data)
					# time.sleep(THREAD_DELY)
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

			
