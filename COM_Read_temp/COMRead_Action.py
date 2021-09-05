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

'''宣告parameter'''
TEST_MODE = 0 #TEST MODE時自動產生測試data
CHECK_BYTE_VAL = 171
DEBUG_COM_BIN = 0
DEBUG_COM_DEC = 0
THREAD_DELY = sys.float_info.min
TIME_PERIOD = 0.0

'''-------------------------------'''

'''繼承QThread'''
class COMRead_Action(QThread):
	'''宣告pyqtSignal'''
	update1 = pyqtSignal(object)
	update2 = pyqtSignal(object, object)
	finished = pyqtSignal()
	'''宣告類別變數'''
	runFlag = 0 #thread開始運行flag
	data_frame_point = 400 #每一個data frame有多少數目的data
	test_mode_flag = 0
	bufferSize = 0
	'''-------------------------------'''
	
	
	
	'''當valid_cnt累加到valid_cnt_num時valid_flag會變1，此時才會送數據到main，目的為了避開程式一開始亂跳的情形 '''
	valid_flag = 0
	valid_cnt = 0
	valid_cnt_num = 3
	
	dt_init_flag = 1
	def __init__(self):	
		super().__init__()
		self.COM = UART()
		
	def run(self):
		''' local variable'''
		cnt = 0 #TEST MODE 產生時間用
		t = np.empty(0)
		data1 = np.empty(0)
		'''-------------------------------'''
		# self.COM.port.flushInput() #清除com port buffer
		
		while self.runFlag:
			t1 = float(datetime.datetime.now().strftime('%S.%f'))
			for i in range(0, self.data_frame_point):
				if(TEST_MODE):
					# print('TEST_MODE')
					self.test_mode_flag = 1
					com_time = cnt
					# com_data1 = np.random.randn()
					com_data1 = cnt
					cnt += 1
					time.sleep(TIME_PERIOD)
				else:
					# print('NON TEST_MODE')
					self.test_mode_flag = 0
					self.bufferSize = self.COM.port.inWaiting()
					# while(not (self.COM.port.inWaiting()>(self.data_frame_point))) : #rx buffer 不到n*data_frame_update_point時不做任何事
						# pass
					'''read check byte, 當不等於CHECK_BYTE_VAL時重複讀取到符合為止 '''
					checkByte = self.COM.read1Binary()
					while(checkByte[0] != CHECK_BYTE_VAL):
						checkByte = self.COM.read1Binary()
					'''--------------------------------------------------------- '''
					# com_time = self.COM.read4Binary()
					com_data1 = self.COM.read4Binary()
					
					if(DEBUG_COM_BIN):
						print('incoming com port BIN data: ')
						# print('com_time: ', end='\t')
						# print(com_time[0], end='\t')
						# print(com_time[1], end='\t')
						# print(com_time[2], end='\t')
						# print(com_time[3])
						print('com_data1: ', end='\t')
						print(hex(com_data1[0]), end='\t')
						print(hex(com_data1[1]), end='\t')
						print(hex(com_data1[2]), end='\t')
						print(hex(com_data1[3]))
						
					# com_time = self.convert2Unsign_4B(com_time)
					com_data1 = self.convert2Sign_4B(com_data1)
					
					if(DEBUG_COM_DEC):
						print('incoming com port DEC data: ')
						# print('com_time: ', end='\t')
						# print(com_time)
						print('com_data1: ', end='\t')
						print(com_data1)
				# t = np.append(t, com_time)
				data1 = np.append(data1, com_data1)
			
			self.update2.emit(data1, data1)
			t2 = float(datetime.datetime.now().strftime('%S.%f'))
			print('\nAction dt= (s)', (t2 - t1)*1)
			t = np.empty(0)
			data1 = np.empty(0)
			# time.sleep(THREAD_DELY)
			
		self.finished.emit() #當self.runFlag=0時發送
		
	def convert2Sign_4B(self, datain) :
		shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
		# print('shift_data:', shift_data)
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

# if __name__ == '__main__':
	# COM = UART()
	# print(COM.read1Binary())
