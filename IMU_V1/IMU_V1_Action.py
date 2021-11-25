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
import IMU_Globals as globals

THREAD_DELY = sys.float_info.min
DEBUG = 0
DEBUG_COM = 1
TEST_MODE = 0
DISABLE_PP = 0
DISABLE_VBOX = 1
DISABLE_NANO33 = 1
DISABLE_SRS200 = 0
DISABLE_ADXL355 = 1
SRS_HEADER = 192
SRS_OFFSET_7 = 13
PRINT_VBOX_BAD_FLAG = 0
PRINT_VBOX_ACT = 0
class IMU_Action(QThread):
	update_COMArray = pyqtSignal(object)
	fog_update = pyqtSignal(object,object)
	fog_update2 = pyqtSignal(object,object, object)
	fog_update4 = pyqtSignal(object, object, object, object, object)
	fog_update6 = pyqtSignal(object, object, object, object, object, object)
	fog_update7 = pyqtSignal(object, object, object, object, object, object, object)
	fog_update8 = pyqtSignal(object, object, object, object, object, object, object, object)
	fog_update9 = pyqtSignal(object, object, object, object, object, object, object, object, object)
	fog_update11 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object)
	fog_update12 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object)
	fog_update13 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object, object)
	fog_update20 = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object )
	fog_finished = pyqtSignal()
	''' VBOX global variable'''
	gpssat = 0
	latitude = 0
	longitude = 0
	velocity = 0
	altitude = 0
	v_velocity = 0
	pitch = 0
	roll = 0
	heading = 0
	vbox_init_flag = 1
	vbox_bad_flag_arr = np.zeros(3)
	vbox_bad_flag = 0
	bf_idx = 0
	'''當valid_cnt累加到valid_cnt_num時valid_flag會變1，此時才會送數據到main，目的為了避開程式一開始亂跳的情形 '''
	valid_flag = 0
	drop_cnt=0
	valid_cnt = 0
	valid_cnt_num = 5
	TIME_PERIOD = 0.01
	g_temp_dt = 0
	''' 計算一定的點數後再傳到main作圖，點數太小的話buffer會累積造成lag'''
	data_frame_update_point = 1
	''' run glag 初始值'''
	runFlag = 0
	runFlag_cali = 0
	''' check byte '''
	check_byte = 170
	check_byte2 = 171
	check_byte3 = 172
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
		print('action kal_Q:', globals.kal_Q)
		print('action kal_R:', globals.kal_R)
		kal_p_SRS200_wz = np.zeros(self.data_frame_update_point+1)
		kal_p_Adxl355_ax = np.zeros(self.data_frame_update_point+1)
		kal_p_Adxl355_ay = np.zeros(self.data_frame_update_point+1)
		kal_p_Adxl355_az = np.zeros(self.data_frame_update_point+1)
		kal_p_PP_wz = np.zeros(self.data_frame_update_point+1)
		kal_p_Nano33_wx = np.zeros(self.data_frame_update_point+1)
		kal_p_Nano33_wy = np.zeros(self.data_frame_update_point+1)
		kal_p_Nano33_wz = np.zeros(self.data_frame_update_point+1)
		kal_p_IMU_speed = np.zeros(self.data_frame_update_point+1)
		p_p = np.zeros(self.data_frame_update_point+1)
		
		kal_SRS200_wz = np.zeros(self.data_frame_update_point)
		kal_PP_wz = np.zeros(self.data_frame_update_point)
		kal_Nano33_wx = np.zeros(self.data_frame_update_point)
		kal_Nano33_wy = np.zeros(self.data_frame_update_point)
		kal_Nano33_wz = np.zeros(self.data_frame_update_point)
		kal_IMU_speed = np.zeros(self.data_frame_update_point)
		kal_Adxl355_ax = np.zeros(self.data_frame_update_point)
		kal_Adxl355_ay = np.zeros(self.data_frame_update_point)
		kal_Adxl355_az = np.zeros(self.data_frame_update_point)
		p = np.zeros(self.data_frame_update_point)
		k = np.zeros(self.data_frame_update_point)
		
		p0 = p0^2
		kal_p_SRS200_wz[self.data_frame_update_point] = kal_init_SRS200_wz
		kal_p_PP_wz[self.data_frame_update_point] = kal_init_PP_wz
		kal_p_Nano33_wx[self.data_frame_update_point] = kal_init_Nano33_wx
		kal_p_Nano33_wy[self.data_frame_update_point] = kal_init_Nano33_wy
		kal_p_Nano33_wz[self.data_frame_update_point] = kal_init_Nano33_wz
		kal_p_IMU_speed[self.data_frame_update_point] = kal_init_IMU_speed
		kal_p_Adxl355_ax[self.data_frame_update_point] = kal_init_Adxl355_ax
		kal_p_Adxl355_ay[self.data_frame_update_point] = kal_init_Adxl355_ay
		kal_p_Adxl355_az[self.data_frame_update_point] = kal_init_Adxl355_az
		p_p[self.data_frame_update_point] = p0 + globals.kal_Q
		''' '''
		
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
					while(not (self.COM.port.inWaiting()>(self.data_frame_update_point*16))) : #rx buffer 不到 arduino傳來的總byte數*data_frame_update_point時不做任何事
						# print(self.COM.port.inWaiting())
						pass
						
				kal_p_SRS200_wz[0] = kal_p_SRS200_wz[self.data_frame_update_point]
				kal_p_PP_wz[0] = kal_p_PP_wz[self.data_frame_update_point]
				kal_p_Nano33_wx[0] = kal_p_Nano33_wx[self.data_frame_update_point]
				kal_p_Nano33_wy[0] = kal_p_Nano33_wy[self.data_frame_update_point]
				kal_p_Nano33_wz[0] = kal_p_Nano33_wz[self.data_frame_update_point]
				kal_p_IMU_speed[0] = kal_p_IMU_speed[self.data_frame_update_point]
				kal_p_Adxl355_ax[0] = kal_p_Adxl355_ax[self.data_frame_update_point]
				kal_p_Adxl355_ay[0] = kal_p_Adxl355_ay[self.data_frame_update_point]
				kal_p_Adxl355_az[0] = kal_p_Adxl355_az[self.data_frame_update_point]
				p_p[0] = p_p[self.data_frame_update_point]
				for i in range(0,self.data_frame_update_point): #更新data_frame_update_point筆資料到data and dt array
					''' 當arduino送來的第一個check byte不符合時則檢查到對時才往下'''
					SRS200 = np.empty(0)
					data_SRS200 = np.empty(0)
					VBOX = np.empty(0)
					if(not TEST_MODE): 
						val = self.COM.read1Binary()
						val3 = self.COM.read1Binary()
						# while(val[0] != self.check_byte or val3[0] != self.check_byte3):
							# val = self.COM.read1Binary()
							# val3 = self.COM.read1Binary()
							# print("val:", val[0], end=', ')
							# print(val3[0])
						# while(1):
						while(val[0] != self.check_byte or val3[0] != self.check_byte3):
							val = val3
							val3 = self.COM.read1Binary()
							print("val:", val[0], end=', ')
							print(val3[0])
							# self.COM.read4Binary()
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
						time.sleep(0.01)
						# for i in range(100):
							# print(i, end=', ')
							# print(self.COM.read1Binary()[0])
					else:
						# data_VBOX_temp = np.empty
						# temp_Nano33_ax = self.COM.read2Binary()
						# temp_Nano33_ay = self.COM.read2Binary()
						# temp_Nano33_az = self.COM.read2Binary()
						
						temp_Nano33_ax = np.random.randn()
						temp_Nano33_ay = np.random.randn()
						temp_Nano33_az = np.random.randn()
						# temp_Nano33_wx = np.random.randn()*100
						# temp_Nano33_wy = np.random.randn()*100
						# temp_Nano33_wz = np.random.randn()*100
						
						temp_dt = self.COM.read4Binary()
						
						if(not DISABLE_SRS200):
							temp_SRS200_wz = self.COM.read4Binary()
							# temp_SRS200_wz = self.COM.read12Binary()
							SRS200_buffer = self.COM.read1Binary()
							
						# print('SRS200_buffer: ', SRS200_buffer[0])
						''' *******read SRS200********** '''
						'''
						for j in temp_SRS200_wz:
							SRS200 = np.append(SRS200, j).astype(int)
							# print(hex(i), end='\t')
						# print('')
						print('SRS200_buffer: ', SRS200_buffer[0])
						# print('SRS200: ', SRS200)
						while(1):
							for idx_k in range(0, len(SRS200)):
								if( (SRS200[idx_k]==SRS_HEADER)and(SRS200[idx_k+1]==SRS_HEADER) ):
									if(SRS200[idx_k+7]==SRS_OFFSET_7):
										break
									
									elif( (SRS200[idx_k+1]==SRS_HEADER)and(SRS200[idx_k+2]==SRS_HEADER) ):
										idx_k = idx_k + 1
										break
									# print('idx_k: ', idx_k)
							break
						for l in range(idx_k+5, idx_k+1, -1):
							data_SRS200 = np.append(data_SRS200, SRS200[l]).astype(int)
						# print('data_SRS200: ', data_SRS200)
						# w_SRS200 = self.convert2Unsign_4B(data_SRS200)/100
						# print('w_SRS200: ', w_SRS200)
						'''
							
						if(not DISABLE_PP):
							temp_PP_wz = self.COM.read4Binary()
						
						if(not DISABLE_ADXL355):
							temp_Adxl355_ax = self.COM.read3Binary()
							temp_Adxl355_ay = self.COM.read3Binary()
							temp_Adxl355_az = self.COM.read3Binary()
							temp_T = self.COM.read2Binary()

							
						if(not DISABLE_NANO33):
							temp_Nano33_wx = self.COM.read2Binary()
							temp_Nano33_wy = self.COM.read2Binary()
							temp_Nano33_wz = self.COM.read2Binary()
							
						if(not DISABLE_VBOX):
							data_VBOX_temp = self.COM.read26Binary()
							for idx_VBOX in data_VBOX_temp:
								VBOX = np.append(VBOX, idx_VBOX).astype(int)
							# print('VBOX: ', end='')
							# print(VBOX)
							''' read VBOX serial data'''
							gpssat = VBOX[0]
							latitude = self.convert2Sign_4B([VBOX[1], VBOX[2], VBOX[3], VBOX[4]])
							longitude = self.convert2Sign_4B([VBOX[5], VBOX[6], VBOX[7], VBOX[8]])
							velocity = self.convert2Sign_3B([VBOX[9], VBOX[10], VBOX[11]]) 
							altitude = self.convert2Sign_3B([VBOX[12], VBOX[13], VBOX[14]]) 
							v_velocity = self.convert2Sign_3B([VBOX[15], VBOX[16], VBOX[17]]) 
							pitch = self.convert2Sign_2B([VBOX[18], VBOX[19]])
							roll = self.convert2Sign_2B([VBOX[20], VBOX[21]])
							heading = self.convert2Sign_2B([VBOX[22], VBOX[23]])
							accz = self.convert2Sign_2B([VBOX[24], VBOX[25]])
							''' ----------------------- '''
							print()
							if(self.vbox_init_flag):
								self.vbox_init_flag = 0
								self.accz = accz
								self.gpssat = gpssat
								self.latitude = latitude
								self.longitude = longitude
								self.velocity = velocity
								self.altitude = altitude
								self.v_velocity = v_velocity
								self.pitch = pitch
								self.roll = roll
								self.heading = heading
							else:
								if( (self.accz-accz)>200 or (self.accz-accz)<-200 ):
									self.vbox_bad_flag_arr[self.bf_idx] = 1;
								else: 
									self.vbox_bad_flag_arr[self.bf_idx] = 0;
								self.vbox_bad_flag = self.vbox_bad_flag_arr[self.bf_idx];
								self.bf_idx = self.bf_idx + 1
								if(self.bf_idx==3):
									self.bf_idx = 0;
								if( self.vbox_bad_flag_arr[0] and self.vbox_bad_flag_arr[1] and self.vbox_bad_flag_arr[2] ): 
									self.vbox_bad_flag = 0;
								
								if(PRINT_VBOX_BAD_FLAG):
									print(self.accz, end='\t');
									print(accz, end='\t');
									print(self.vbox_bad_flag, end='\t');
									print(self.vbox_bad_flag_arr[0], end='\t');
									print(self.vbox_bad_flag_arr[1], end='\t');
									print(self.vbox_bad_flag_arr[2]);
									print("\n");
								
								if(not self.vbox_bad_flag):
									self.accz = accz
									self.gpssat = gpssat
									self.latitude = latitude
									self.longitude = longitude
									self.velocity = velocity
									self.altitude = altitude
									self.v_velocity = v_velocity
									self.pitch = pitch
									self.roll = roll
									self.heading = heading
								if(PRINT_VBOX_ACT):
									print('gpssat: ', gpssat)
									print('latitude: ', latitude)
									print('longitude: ', longitude)
									print('velocity: ', velocity)
									print('altitude: ', altitude)
									print('v_velocity: ', v_velocity)
									# print('pitch: ', pitch)
									# print('roll: ', roll)
									# print('heading: ', heading)
									print('accz: ', accz)
						else:
							self.gpssat = 0
							self.latitude = 0
							self.longitude = 0
							self.velocity = 0
							self.altitude = 0
							self.v_velocity = 0
							self.pitch = 0
							self.roll = 0
							self.heading = 0
							self.accz = 0
					
					# print(self.COM.port.inWaiting())
						
					# if(DEBUG_COM):
						# print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
						# print('buffer: ',end=', ' )
						# print(self.bufferSize)
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
						# print('temp_dt: ', end='\t')
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
						val2 = self.COM.read1Binary()
						# print('val2[0]: ', val2[0])
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
							# print(temp_dt)
							
							# if((temp_dt-self.dt_old)>100000 and self.valid_flag == 1):
								# print(temp_dt, end=', ')
								# print(self.dt_old, end=', ')
								# print(temp_dt-self.dt_old)
								# break
							
							if(DISABLE_SRS200):
								temp_SRS200_wz = 0
							else:
								temp_SRS200_wz = self.convert2Sign_4B(temp_SRS200_wz)
								# temp_SRS200_wz = self.convert2Unsign_4B(data_SRS200)
								# print('1. temp_SRS200_wz: ', temp_SRS200_wz)
							
							
							if(DISABLE_PP):
								temp_PP_wz = 0
							else:
								temp_PP_wz = self.convert2Sign_4B(temp_PP_wz)
								
							# if(DISABLE_VBOX):
								# temp_IMU_speed = 0
							# else:
								# temp_IMU_speed = self.convert2Unsign_3B(temp_IMU_speed)
							temp_IMU_speed = 0
								
							# print('temp_IMU_speed 2: ', temp_IMU_speed)
							if(not DISABLE_ADXL355):
								temp_Adxl355_ax =self.convert2Sign_ADXL355(temp_Adxl355_ax)
								temp_Adxl355_ay =self.convert2Sign_ADXL355(temp_Adxl355_ay)
								temp_Adxl355_az =self.convert2Sign_ADXL355(temp_Adxl355_az)
								temp_T = self.convert2Unsign_2B(temp_T)
							else:
								temp_Adxl355_ax =0
								temp_Adxl355_ay =0
								temp_Adxl355_az =0
								temp_T = 0
							if(not DISABLE_NANO33):
								temp_Nano33_wx = self.convert2Sign_2B(temp_Nano33_wx)
								temp_Nano33_wy = self.convert2Sign_2B(temp_Nano33_wy)
								temp_Nano33_wz = self.convert2Sign_2B(temp_Nano33_wz)
							else:
								temp_Nano33_wx = 0
								temp_Nano33_wy = 0
								temp_Nano33_wz = 0
							# print(temp_T)
						
						if(DEBUG_COM):
							
							print(temp_dt - self.g_temp_dt);
						self.g_temp_dt = temp_dt
						self.kal_flag = globals.kal_status
						''' Kalmman filter'''
						#update
						# print('i: ', i)
						# print('p_p[i]: ', p_p[i])
						# print('globals.kal_R: ', globals.kal_R)
						k[i] = p_p[i]/(p_p[i] + globals.kal_R) #k_n
						# print('k[i]: ', k[i])
						kal_SRS200_wz[i] = kal_p_SRS200_wz[i] + k[i]*(temp_SRS200_wz - kal_p_SRS200_wz[i])
						kal_PP_wz[i] = kal_p_PP_wz[i] + k[i]*(temp_PP_wz - kal_p_PP_wz[i])
						kal_Nano33_wx[i] = kal_p_Nano33_wx[i] + k[i]*(temp_Nano33_wx - kal_p_Nano33_wx[i])
						kal_Nano33_wy[i] = kal_p_Nano33_wy[i] + k[i]*(temp_Nano33_wy - kal_p_Nano33_wy[i])
						kal_Nano33_wz[i] = kal_p_Nano33_wz[i] + k[i]*(temp_Nano33_wz - kal_p_Nano33_wz[i])
						kal_IMU_speed[i] = kal_p_IMU_speed[i] + k[i]*(temp_IMU_speed - kal_p_IMU_speed[i])
						kal_Adxl355_ax[i] = kal_p_Adxl355_ax[i] + k[i]*(temp_Adxl355_ax - kal_p_Adxl355_ax[i])
						kal_Adxl355_ay[i] = kal_p_Adxl355_ay[i] + k[i]*(temp_Adxl355_ay - kal_p_Adxl355_ay[i])
						kal_Adxl355_az[i] = kal_p_Adxl355_az[i] + k[i]*(temp_Adxl355_az - kal_p_Adxl355_az[i])
						p[i] = (1 - k[i])*p_p[i] 
						
						#predict
						kal_p_SRS200_wz[i+1] = kal_SRS200_wz[i]
						kal_p_PP_wz[i+1] = kal_PP_wz[i]
						kal_p_Nano33_wx[i+1] = kal_Nano33_wx[i]
						kal_p_Nano33_wy[i+1] = kal_Nano33_wy[i]
						kal_p_Nano33_wz[i+1] = kal_Nano33_wz[i]
						kal_p_IMU_speed[i+1] = kal_IMU_speed[i]
						kal_p_Adxl355_ax[i+1] = kal_Adxl355_ax[i]
						kal_p_Adxl355_ay[i+1] = kal_Adxl355_ay[i]
						kal_p_Adxl355_az[i+1] = kal_Adxl355_az[i]
						p_p[i+1] = p[i] + globals.kal_Q
					
						''' end of kalmman filter'''
					
						if(temp_dt < temp_dt_before):
							temp_offset = math.ceil(abs(temp_dt - temp_dt_before)/(1<<32))*(1<<32)
							temp_dt = temp_dt + temp_offset
							temp_dt_before = temp_dt
						
							
						
						val_Nano33_ax = temp_Nano33_ax
						val_Nano33_ay = temp_Nano33_ay
						val_Nano33_az = temp_Nano33_az
						
						
						if(self.kal_flag):
							val_SRS200_wz = kal_SRS200_wz[i]
							val_Adxl355_ax = kal_Adxl355_ax[i]
							val_Adxl355_ay = kal_Adxl355_ay[i]
							val_Adxl355_az = kal_Adxl355_az[i]
							val_PP_wz = kal_PP_wz[i]
							val_Nano33_wx = kal_Nano33_wx[i]
							val_Nano33_wy = kal_Nano33_wy[i]
							val_Nano33_wz = kal_Nano33_wz[i]
							val_IMU_speed = kal_IMU_speed[i]
						else:
							val_SRS200_wz = temp_SRS200_wz
							val_Adxl355_ax = temp_Adxl355_ax
							val_Adxl355_ay = temp_Adxl355_ay
							val_Adxl355_az = temp_Adxl355_az
							val_PP_wz = temp_PP_wz
							val_Nano33_wx = temp_Nano33_wx
							val_Nano33_wy = temp_Nano33_wy
							val_Nano33_wz = temp_Nano33_wz
							val_IMU_speed = temp_IMU_speed
						
						
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
						data_IMU_speed = np.append(data_IMU_speed[1:], val_IMU_speed)
						data_T = np.append(data_T[1:], temp_T)
						
						# dt_new = dt_old + i*self.TIME_PERIOD
						dt = np.append(dt[1:], temp_dt)
						# print(temp_dt, end=', ')
						# print(dt_init, end=', ')
						# print(dt)
						# print('valid_cnt:', self.valid_cnt)
				#end of for loop
				# print(data_IMU_speed)
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
						
						
					if(self.runFlag) :
						# print(dt-self.dt_old)
						self.fog_update20.emit(dt-dt_init, data_SRS200_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay, data_Adxl355_az, data_T, 
							data_Nano33_wx, data_Nano33_wy, data_Nano33_wz, self.gpssat, self.latitude, self.longitude, self.velocity, self.altitude, self.v_velocity, 
							self.pitch, self.roll, self.heading, self.accz)
						# if((dt-self.dt_old)<200):
							# self.fog_update11.emit(dt-dt_init, data_SRS200_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay, data_Adxl355_az, data_T, data_IMU_speed, 
													# data_Nano33_wx, data_Nano33_wy, data_Nano33_wz)
						# else: 
							# print('shit1')
							# print(dt, end=', ')
							# print(dt_init, end=', ')
							# print((dt-dt_init)*1e-3, end=', ')
							# print((self.dt_old-dt_init)*1e-3)
							# break
							# self.dt_offset = self.dt_old - dt_init
						self.dt_old = dt
						# time.sleep(THREAD_DELY)
					elif(self.runFlag_cali):
						self.fog_update13.emit(data_SRS200_wz, data_Nano33_wx, data_Nano33_wy, data_Nano33_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay,
											data_Adxl355_az, data_Nano33_ax, data_Nano33_ay, data_Nano33_az, data_T, data_IMU_speed)
						# self.dt_old = dt
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
		shift_data = (datain[0]<<16|datain[1]<<8|datain[2])
		if((datain[0]>>7) == 1):
			return (shift_data - (1<<24))
		else :
			return shift_data
		
	def convert2Sign_ADXL355(self, datain) :
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
			
