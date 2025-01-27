import os
import sys
sys.path.append("../")
import time
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.NetSSH as net 
import py3lib.COMPort as com
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import datetime

BitFilePath = "cat /root/bit_run/"
BitFileTarget = " > /dev/xdevcfg"

BitFile_Open = "fog_v1"
BitFile_Close = "kal.bit" 
BitFile_Check = "fog_v3.bit"
OpenNameList = [".bit", "_1.bit", "_2.bit", "_3.bit", "_4.bit", "_5.bit", "_6.bit", "_7.bit", "_8.bit", "_9.bit", "_10.bit"]

Monitor_cmd = "/opt/redpitaya/bin/monitor "

Fog_OPEN_cmd = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./FOG_OPEN"
Fog_CLOSE_cmd = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./FOG_CLOSE"
Fog_OFF_cmd = "2"
Fog_Data_cmd = "1\n"

Before_fog_1 = "0x4000014C 1"
Before_fog_0 = "0x4000014C 0"

GAIN1_ADD = "0x40000110 "
GAIN1PWR_ADD = "0x40000170 "
GAIN2PWR_ADD = "0x40000150 "

MOD_HIGH_ADD = "0x40000100 "
MOD_LOW_ADD = "0x40000104 "
MOD_FREQ_ADD = "0x40000108 "
MOD_PiVth_ADD = "0x40000114 "
Polarity_ADD = "0x4000011C "

IGNOR_ADD = "0x40000138 "
OFFSET_ADD = "0x4000013C "
StepVth_ADD = "0x40000160 "
AVG_ADD = "0x40000140 "

MOD_Q_ADD = "0x40000188 "
MOD_R_ADD = "0x4000018C "
MOD_Q2_ADD = "0x400001D8 "
MOD_R2_ADD = "0x400001DC "

GET_DATA_ADD = "0X400001D4 "

UPPER_BAND_ADD = "0x400001C0 "
LOWER_BAND_ADD = "0x400001C4 "

PRSETFILE = "set/setting.txt"
SETTING_FILEPATH = "set"

PARA_MODHIGH_INDEX = 0
PARA_MODLOW_INDEX = 1
PARA_MODFREQ_INDEX = 2
PARA_PIVTH_INDEX = 3
PARA_POLARITY_INDEX = 4

PARA_IGNOR_INDEX = 5
PARA_OFFSET_INDEX = 6
PARA_STEPVTH_INDEX = 7
PARA_INPUTAVG_INDEX = 8
PARA_MODEOPEN_INDEX = 9

PARA_HOST_INDEX = 10
PARA_MODE_INDEX = 11
PARA_GAIN1_INDEX = 12
PARA_GAIN1PWR_INDEX = 13 
PARA_GAIN2PWR_INDEX = 14

PARA_COEFF_INDEX = 15
PARA_MODQ_INDEX = 16
PARA_MODR_INDEX = 17
PARA_MODQ2_INDEX = 18
PARA_MODR2_INDEX = 19
PARA_UPPER_BAND_INDEX = 20
PARA_LOWER_BAND_INDEX = 21

Max_Para_Index = 22
SAMPLEING_RATE = 100

#The folling define should be input from GUI
LOW_PASS_FILTER_FCUT = 1 #min 0.01 max 50 default = 1
FILTER_LEVEL = 5 #min = 1 max = 10 default = 5


class qss008Act(QObject):
	fog_update = pyqtSignal(object,object)
	fog_finished = pyqtSignal()
	def __init__(self, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.ssh = net.NetSSH(loggername)
		self.usb = com.FT232(loggername)
		self.logger = logging.getLogger(loggername)
		self.runFlag = False
		self.SaveFileName = ''
		self.paramInit()
		self.loadPreset()

	def usbConnect(self):
		status = self.usb.connect(baudrate = 9600, timeout = 1)
		return status

	def sendComCmd(self, cmd):
		self.usb.writeLine(cmd)

	def paramInit(self):
		self.modHigh = 4096
		self.modLow = 4096
		self.modFreq = 125
		self.piVth = 8191
		self.polarity = 1
		
		self.ignor = 32
		self.offset = 0
		self.stepVth = 0
		self.inavg = 4
		self.mode_open = 6

		self.host = "host name"
		self.mode = "close"
		self.gain1 = 1
		self.gain1pwr = 6
		self.gain2pwr = 6

		self.coeff = 1
		self.modQ = 1
		self.modR = 1
		self.modQ2 = 1
		self.modR2 = 1
		self.upperBand = 1
		self.lowerBand = -1
		self.paralist = ["" for i in range(0, Max_Para_Index)]

	def loadPreset(self):
		if not os.path.isdir(SETTING_FILEPATH):
			os.mkdir(SETTING_FILEPATH)
			self.writePreset()
			self.logger.warning("preseet file dir not exist")
		elif not os.path.exists(PRSETFILE):
			self.writePreset()
			self.logger.warning("preseet file load failed")
		else:
			paralist = fil2a.TexTFileto1DList(PRSETFILE, self.loggername)
			if (len(paralist) != Max_Para_Index):
				self.writePreset()
				self.logger.warning("preseet file formate error")
			else:
				self.paralist = paralist

				self.modHigh = int(self.paralist[PARA_MODHIGH_INDEX])
				self.modLow = int(self.paralist[PARA_MODLOW_INDEX])
				self.modFreq = int(self.paralist[PARA_MODFREQ_INDEX])
				self.piVth = int(self.paralist[PARA_PIVTH_INDEX])
				self.polarity = int(self.paralist[PARA_POLARITY_INDEX])
				
				self.ignor = int(self.paralist[PARA_IGNOR_INDEX])
				self.offset = int(self.paralist[PARA_OFFSET_INDEX])
				self.stepVth = int(self.paralist[PARA_STEPVTH_INDEX])
				self.inavg = int(self.paralist[PARA_INPUTAVG_INDEX])
				self.mode_open = int(self.paralist[PARA_MODEOPEN_INDEX])

				self.host = self.paralist[PARA_HOST_INDEX]
				self.mode = self.paralist[PARA_MODE_INDEX]
				self.gain1 = int(self.paralist[PARA_GAIN1_INDEX])
				self.gain1pwr = int(self.paralist[PARA_GAIN1PWR_INDEX])
				self.gain2pwr = int(self.paralist[PARA_GAIN2PWR_INDEX])

				self.coeff = float(self.paralist[PARA_COEFF_INDEX])
				self.modQ = int(self.paralist[PARA_MODQ_INDEX])
				self.modR = int(self.paralist[PARA_MODR_INDEX])
				self.modQ2 = int(self.paralist[PARA_MODQ2_INDEX])
				self.modR2 = int(self.paralist[PARA_MODR2_INDEX])
				self.upperBand = int(self.paralist[PARA_UPPER_BAND_INDEX])
				self.lowerBand = float(self.paralist[PARA_LOWER_BAND_INDEX])

	def writePreset(self):
		self.paralist[PARA_MODHIGH_INDEX] = self.modHigh
		self.paralist[PARA_MODLOW_INDEX] = self.modLow
		self.paralist[PARA_MODFREQ_INDEX] = self.modFreq
		self.paralist[PARA_PIVTH_INDEX] = self.piVth
		self.paralist[PARA_POLARITY_INDEX] = self.polarity
		
		self.paralist[PARA_IGNOR_INDEX] = self.ignor
		self.paralist[PARA_OFFSET_INDEX] = self.offset
		self.paralist[PARA_STEPVTH_INDEX] = self.stepVth
		self.paralist[PARA_INPUTAVG_INDEX] = self.inavg
		self.paralist[PARA_MODEOPEN_INDEX] = self.mode_open

		self.paralist[PARA_HOST_INDEX] = self.host
		self.paralist[PARA_MODE_INDEX] = self.mode
		self.paralist[PARA_GAIN1_INDEX] = self.gain1
		self.paralist[PARA_GAIN1PWR_INDEX] = self.gain1pwr
		self.paralist[PARA_GAIN2PWR_INDEX] = self.gain2pwr

		self.paralist[PARA_COEFF_INDEX] = self.coeff
		self.paralist[PARA_MODQ_INDEX] = self.modQ
		self.paralist[PARA_MODR_INDEX] = self.modR
		self.paralist[PARA_MODQ2_INDEX] = self.modQ2
		self.paralist[PARA_MODR2_INDEX] = self.modR2
		self.paralist[PARA_UPPER_BAND_INDEX] = self.upperBand
		self.paralist[PARA_LOWER_BAND_INDEX] = self.lowerBand
		fil2a.array1DtoTextFile(PRSETFILE, self.paralist, self.loggername)

	def setBitFile(self):
		if self.mode == "open":
			bitFileName = BitFile_Open + OpenNameList[self.mode_open]
		else:
			bitFileName = BitFile_Close

		cmd = BitFilePath + bitFileName + BitFileTarget
		
		try:
			#print(cmd)
			self.ssh.sendCmd(cmd, False, 1)
		except:
			return 0
		
		self.setModHigh()
		self.setModLow()
		self.setModFreq()
		self.setPiVth()
		self.setPolarity()
		self.setIgnor()
		self.setOffset()
		self.setStepVth()
		self.setAVG()
		self.setGain1()
		self.setGain2()
		self.setModQ()
		self.setModR()
		self.setModQ2()
		self.setModR2()
		self.setUpperBand()
		self.setLowerBand()
		return 1

	def setModHigh(self):
		cmd = Monitor_cmd + MOD_HIGH_ADD + str(self.modHigh)
		self.ssh.sendCmd(cmd, True, 0)
		return self.modHigh*0.2442

	def setModLow(self):
		cmd = Monitor_cmd + MOD_LOW_ADD + str(self.modLow)
		self.ssh.sendCmd(cmd, True, 0)
		return self.modLow*0.2442

	def setModFreq(self):
		cmd = Monitor_cmd + MOD_FREQ_ADD + str(self.modFreq)
		self.ssh.sendCmd(cmd, True, 0)
		return 62500.0/float(self.modFreq)

	def setPiVth(self):
		cmd = Monitor_cmd + MOD_PiVth_ADD + str(self.piVth)
		self.ssh.sendCmd(cmd, True, 0)
		return 0.2442*float(self.piVth)

	def setPolarity(self):
		cmd = Monitor_cmd + Polarity_ADD + str(self.polarity)
		self.ssh.sendCmd(cmd, True, 0)

	def setIgnor(self):
		cmd = Monitor_cmd + IGNOR_ADD+str(self.ignor)
		self.ssh.sendCmd(cmd, True, 0)
		return self.ignor

	def setOffset(self):
		cmd = Monitor_cmd + OFFSET_ADD+str(self.offset)
		self.ssh.sendCmd(cmd, True, 0)
		return float(self.offset)*0.2442

	def setStepVth(self):
		cmd = Monitor_cmd + StepVth_ADD + str(self.stepVth)
		self.ssh.sendCmd(cmd, True, 0)
		return float(self.stepVth) * 0.2442

	def setAVG(self):
		cmd = Monitor_cmd + AVG_ADD +str(self.inavg)
		self.ssh.sendCmd(cmd, True, 0)

	def setGain1(self):
		cmd = Monitor_cmd + GAIN1_ADD + str(self.gain1)
		self.ssh.sendCmd(cmd, True, 0)
		cmd = Monitor_cmd + GAIN1PWR_ADD + str(self.gain1pwr)
		self.ssh.sendCmd(cmd, True, 0)
		Gain1 = float(self.gain1)/float(2**self.gain1pwr)
		return Gain1

	def setGain2(self):
		cmd = Monitor_cmd + GAIN2PWR_ADD + str(self.gain2pwr)
		self.ssh.sendCmd(cmd, True, 0)
		Gain2 = 1/float(2**self.gain2pwr)
		return Gain2
	
	def getData(self):
		self.sendComCmd(Fog_Data_cmd)
		#print ("send command")
		cmd = Monitor_cmd + GET_DATA_ADD + "1"
		self.ssh.sendCmd(cmd, True, 0)
		time.sleep(2)
		filename = "data.bin"
		self.ssh.getFtpFile(filename)
		return fil2a.BinFiletoArray(filename,4, "i", self.loggername)

	def runFog(self):
		# crticalF= 2*LOW_PASS_FILTER_FCUT/SAMPLEING_RATE
		# b, a = sp.singnal.butter(FILTER_LEVEL, critalF, 'low', analog= False)

		if self.runFlag:
			# j = 0 # for TEST
			dt_old = 0
			self.setBitFile()

			# 2020.2.11 add by sherry , request by adam
			cmd = Monitor_cmd + Before_fog_1
			self.ssh.sendCmd(cmd, True, 0.05)
			cmd = Monitor_cmd + Before_fog_0
			self.ssh.sendCmd(cmd, True, 0)

			self.usb.port.flushInput()
			if self.mode == "open":
				self.ssh.sendCmd(Fog_OPEN_cmd)
			else:
				self.ssh.sendCmd(Fog_CLOSE_cmd)

			self.usb.port.flushInput()
			save = False
			if self.SaveFileName != "":
				fo = open(self.SaveFileName, "w+")
				save = True
			while self.runFlag:
				data = np.empty(0)
				dt = np.empty(0)
				for i in range(0,40): #更新40筆資料到data and dt array
					# print("before")
					temp = self.usb.readLine()
					if (temp != "") and (temp != "ERROR"):
						temp = int(temp)
						# temp = i + j # for TEST
						data = np.append(data, temp)
						dt_new = dt_old + i*0.01
						dt = np.append(dt, dt_new)
						if save:
							fo.write("%3.4f" % dt_new + '\t' + "%3.4f" % temp + '\n')
					# print("after")
				self.fog_update.emit(data,dt)
				# j = j + 1 # for TEST
				dt_old = dt_new + 0.01
			if save:
				fo.close()
			#self.sendComCmd(Fog_OFF_cmd)
			self.usb.port.flushInput()
			self.fog_finished.emit()
	
	def setStop(self):
		#print(Fog_OFF_cmd)
		self.sendComCmd(Fog_OFF_cmd)
		self.usb.port.flushInput()

	def setModQ(self):
		cmd = Monitor_cmd + MOD_Q_ADD + str(self.modQ)
		#print(cmd)
		self.ssh.sendCmd(cmd, True, 0)

	def setModR(self):
		cmd = Monitor_cmd + MOD_R_ADD + str(self.modR)
		#print(cmd)
		self.ssh.sendCmd(cmd, True, 0)

	def setModQ2(self):
		cmd = Monitor_cmd + MOD_Q2_ADD + str(self.modQ2)
		#print(cmd)
		self.ssh.sendCmd(cmd, True, 0)

	def setModR2(self):
		cmd = Monitor_cmd + MOD_R2_ADD + str(self.modR2)
		#print(cmd)
		self.ssh.sendCmd(cmd, True, 0)

	def setUpperBand(self):
		cmd = Monitor_cmd + UPPER_BAND_ADD + str(self.upperBand)
		# print(cmd)
		self.ssh.sendCmd(cmd, True, 0)

	def setLowerBand(self):
		cmd = Monitor_cmd + LOWER_BAND_ADD + str(self.lowerBand)
		#print(cmd)
		self.ssh.sendCmd(cmd, True, 0)
