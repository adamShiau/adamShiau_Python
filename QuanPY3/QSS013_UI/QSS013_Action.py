import os
import sys
sys.path.append("../")
import time
import numpy as np 
import py3lib.FT232H as usb 
import py3lib.FileToArray as fil2a
import logging
import py3lib.QuLogger
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

SETTING_FILEPATH = "set"
PRESET_FILE_NAME = "set/setting.txt"
TIME_PRESET_FILE_NAME = "set/time_setting.txt"

CH_INDEX = 0
MODE_INDEX = 1
HEADER_INDEX = 2
TOTAL_INDEX = 3

READ_DATA_LEN = 500
DELAY_TIME = 0.01 #sleep
DELTA_TIME = 5e-3

ADC_ratio = 5.0 / 65535.0
ADC_REF = 3.3

TEST_MODE = False

READ_ADC1_ch0_START = 48
READ_ADC1_ch0_STOP = 49
READ_ADC1_ch1_START = 50
READ_ADC1_ch1_STOP = 51
READ_ADC2_ch0_START = 57
READ_ADC2_ch0_STOP = 58
READ_ADC2_ch1_START = 59
READ_ADC2_ch1_STOP = 60
INTEGRATOR_1_START = 61
INTEGRATOR_1_STOP = 62
INTEGRATOR_2_START = 63
INTEGRATOR_2_STOP = 64
INTEGRATOR_3_START = 65
INTEGRATOR_3_STOP = 66
INTEGRATOR_4_START = 67
INTEGRATOR_4_STOP = 68
MODE1 = 1
MODE2 = 2
MODE3 = 3
SET_T1 = 4
SET_T2 = 5
SET_T3 = 6
SET_T4 = 7

SET_Time_list = [SET_T1, SET_T2, SET_T3, SET_T4]
SET_MODE_list = [MODE1, MODE2, MODE3]
INTEGRATOR_START_list = [INTEGRATOR_1_START, INTEGRATOR_2_START, INTEGRATOR_3_START, INTEGRATOR_4_START]
INTEGRATOR_STOP_list =  [INTEGRATOR_1_STOP,  INTEGRATOR_2_STOP,  INTEGRATOR_3_STOP,  INTEGRATOR_4_STOP]
ADC_START_list = [READ_ADC1_ch0_START, READ_ADC1_ch1_START, READ_ADC2_ch0_START, READ_ADC2_ch1_START]
ADC_STOP_list =  [READ_ADC1_ch0_STOP,  READ_ADC1_ch1_STOP,  READ_ADC2_ch0_STOP,  READ_ADC2_ch1_STOP]

def setCmdValue(cmd_type, value):
	cmd = [0, 0, 0, 0, 0]
	value1 = value >> 24
	value2 = (value >> 16) & 255
	value3 = (value >> 8) & 255
	value4 = value & 255
	if(value1 == 0):
		value1 = 256
	if(value2 == 0):
		value2 = 256
	if(value3 == 0):
		value3 = 256
	if(value4 == 0):
		value4 = 256

	cmd = [cmd_type, value1, value2, value3, value4]
	# print (cmd)
	return cmd


class qss013Act(QObject):
	update = pyqtSignal(object, object)
	finished = pyqtSignal()

	def __init__(self, loggername, paraent = None):
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.logger = logging.getLogger(loggername)
		self.ft232 = usb.FT232H(loggername)
		self.runFlag = False

		self.loadPreset()

	def usbConnect(self):
		if (TEST_MODE):
			status = 0
		else:
			status = self.ft232.connect()
		# print("action connect status = " + str(status) )
		return status

	def loadPreset(self):
		if not os.path.isdir(SETTING_FILEPATH):
			os.mkdir(SETTING_FILEPATH)

		if os.path.exists(PRESET_FILE_NAME):
			self.preset = fil2a.TexTFileto1DList(PRESET_FILE_NAME, self.loggername)
			if (len(self.preset) != TOTAL_INDEX):
				self.logger.warning("preset file total index change")
				self.preset = [1, 1, ""]
				self.savePreset(0)
		else:
			self.logger.warning("preset file load failed")
			self.preset = [1, 1, ""]
			self.savePreset(0)

		if os.path.exists(TIME_PRESET_FILE_NAME):
			self.timePreset = fil2a.TexTFileto1DList(TIME_PRESET_FILE_NAME, self.loggername)
		else:
			self.logger.warning("time preset file load failed")
			self.timePreset = [1, 1, 1, 1]
			self.savePreset(1)

	def savePreset(self, type):
		if (type == 1):
			paralist = self.timePreset
			filename = TIME_PRESET_FILE_NAME
		else:
			paralist = self.preset
			filename = PRESET_FILE_NAME

		fil2a.array1DtoTextFile(filename, paralist, self.loggername)

	def sendUsbCmd(self):
		# print("----------")
		# SET Time
		for i in range(0, 4):
			# set_time_value = int(self.timePreset[i])
			set_time_value = int(int(self.timePreset[i])*1e5/2)
			if (TEST_MODE):
				print (set_time_value)
			cmd = setCmdValue(SET_Time_list[i], set_time_value)
			if (TEST_MODE):
				print (cmd)
			else:
				self.ft232.writeList(cmd)
		# SET MODE
		cmd = setCmdValue(SET_MODE_list[(self.preset[MODE_INDEX]-1)], 0)
		if (TEST_MODE):
			print (cmd)
		else:
			self.ft232.writeList(cmd)

	def initReadData(self):
		self.data = np.empty(0)
		self.total_size = 0
		self.time_array = np.empty(0)

	def readData(self):
		if (TEST_MODE == False):
			data = []
		else:
			data = np.zeros(READ_DATA_LEN)

		# print("START")
		t0 = 0.0
		# INTEGRATOR START before READ ADC START
		cmd = setCmdValue(INTEGRATOR_START_list[(self.preset[CH_INDEX]-1)], 0)
		if (TEST_MODE):
			print (cmd)
		else:
			self.ft232.writeList(cmd)
		# READ ADC START
		cmd = setCmdValue(ADC_START_list[(self.preset[CH_INDEX]-1)], 0)
		if (TEST_MODE):
			print (cmd)
		else:
			self.ft232.writeList(cmd)
			self.ft232.Flush()

		while (self.runFlag):
			self.initReadData()
			if (TEST_MODE):
				for i in range(0, READ_DATA_LEN):
					data[i] = t0 + i
				size = READ_DATA_LEN
			else:
				ori_size, val = self.ft232.ReadBuffer()
				print("ori size = " + str(ori_size))
				idx = 0
				data = []
				for i in range(0, ori_size, 2):
					if (i >= 2): #remove the first data
						temp_data = (val[i]*256 + val[i+1])*ADC_REF/65535
						data.append(temp_data)
						# print(idx, data[idx])
						idx = idx + 1
				size = idx
				print("size = " + str(size))
			self.data = np.append(self.data, data)
			for i in range(0, size):
				self.time_array = np.append(self.time_array, (t0 + i*DELTA_TIME) )
			t0 = t0 + size*DELTA_TIME
			self.total_size = self.total_size + size
			# print("act total = " + str(self.total_size) )
			self.update.emit(self.data, self.time_array)
			time.sleep(DELAY_TIME)
		self.finished.emit()
		# READ ADC STOP
		cmd = setCmdValue(ADC_STOP_list[(self.preset[CH_INDEX]-1)], 0)
		if (TEST_MODE):
			print (cmd)
		else:
			self.ft232.writeList(cmd)
		# INTEGRATOR STOP after READ ADC STOP
		cmd = setCmdValue(INTEGRATOR_STOP_list[(self.preset[CH_INDEX]-1)], 0)
		if (TEST_MODE):
			print (cmd)
		else:
			self.ft232.writeList(cmd)
		# print("STOP")

if __name__ == '__main__':
	a = qss013Act("test")
