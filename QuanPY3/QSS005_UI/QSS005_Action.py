import os
import sys
sys.path.append("../")
import time
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.NetSSH as net 
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import datetime

SETTING_FILEPATH = "set"
MS1_PRESET_FILE_NAME = "set/ms1_setting.txt"
CAL_PRESET_FILE_NAME = "set/cal_setting.txt"
HK_PRESET_FILE_NAME = "set/hk_setting.txt"
ROW_FILEPATH = "./ms1rawdata/"

ms1param_start = 0
ms1param_end = 17
calibparam_start = 18
calibparam_end = 19

FAKE_DATA = "data.txt"
INIT_DATACOUNT = 10000

UART_CMD = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./UART "

ADC_DATA_FILE = "adc_data.bin"
ADC_CNT_FILE = "cnt.txt"
ADC_CMD = "/opt/redpitaya/bin/monitor 0x40200058"
ADC_TIMEOUT = 1000


class qss005Action(QObject):
	ms1_update_array = pyqtSignal(object)
	ms1_single_finished = pyqtSignal()

	ms1_update_total_array = pyqtSignal(object, object)
	ms1_finished = pyqtSignal()

	def __init__(self, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.Qss005header = ""
		self.ssh = net.NetSSH(loggername)
		self.logger = logging.getLogger(loggername)
		self.ms1init()
		self.calibra_init()
		self.loadPreset()
		self.updateCalMass()

# start the function define for all QSS005
	def sshConnect(self, ip, port, usr, psswd):
		sshresult = self.ssh.connectSSH(ip, port, usr, psswd)
		ftpresult = self.ssh.connectFTP()
		return (sshresult and ftpresult)

	def ftpFile(self, filename):
		self.ssh.getFtpFile(filename)

	def loadPreset(self):
		if not os.path.isdir(SETTING_FILEPATH):
			os.mkdir(SETTING_FILEPATH)

		if os.path.exists(MS1_PRESET_FILE_NAME):
			self.ms1Preset = fil2a.TexTFileto1DList(MS1_PRESET_FILE_NAME, self.loggername)
		else:
			self.logger.warning("ms1 file load failed")

		if os.path.exists(CAL_PRESET_FILE_NAME):
			self.calibPreset = fil2a.TexTFileto1DList(CAL_PRESET_FILE_NAME, self.loggername)
		else:
			self.logger.warning("cal file load failed")
		
		if os.path.exists(HK_PRESET_FILE_NAME):
			self.hkPreset = fil2a.TexTFileto1DList(HK_PRESET_FILE_NAME, self.loggername)
		else:
			self.logger.warning("hk file load failed")

	def savePreset(self, type):
		if (type == 2):
			paralist = self.calibPreset
			filename = CAL_PRESET_FILE_NAME
		elif (type == 1):
			paralist = self.ms1Preset
			filename = MS1_PRESET_FILE_NAME
		else:	#elif (type == 0):
			paralist = self.hkPreset
			filename = HK_PRESET_FILE_NAME

		fil2a.array1DtoTextFile(filename, paralist, self.loggername)

	def setQss005header(self, header):
		self.Qss005header = header

# start the function define for MS1
	def ms1init(self):
		self.ms1singleRunFlag = False
		self.singleData = np.empty(0)
		self.cmd = ""
		self.delay_time = 0
		self.ms1noisefilter = False
		self.ms1filterLevel = 1

		self.ms1runFlag = False
		self.ms1TotalData = np.zeros(INIT_DATACOUNT)
		#self.ms1saveRaw = False
		self.ms1saveRawPath = ROW_FILEPATH
		self.rawfileindex = 0
		self.ms1datalen = INIT_DATACOUNT
		self.runLoop = 1
		self.polarity = 1 

	def ms1_setCmdAndValue(self, cmd, delay_time):
		self.cmd = cmd
		self.delay_time = delay_time

	def ms1_setNoiseAndLevel(self, enable, level):
		self.ms1noisefilter = enable
		self.ms1filterLevel = level

	def ms1_setRowAndPath(self, row_path = ""):
		#self.ms1saveRaw = save_row
		#if (self.ms1saveRaw):
			#if (row_path != ''):
		self.ms1saveRawPath = row_path

	def resetIndex(self):
		self.rawfileindex = 0
		self.ms1TotalData = np.zeros(INIT_DATACOUNT)
		self.ms1datalen = INIT_DATACOUNT

	def ms1fakeData(self): # NOT use
		self.singleData = fil2a.TexTFileto1DList(FAKE_DATA, self.loggername)

	def checkAndGetFile(self, filename, len):
		data = np.empty(0)
		ls_cmd = "ls " + filename
		TRIG_PASS_FLAG = False
		i = 0
		while not TRIG_PASS_FLAG and i < ADC_TIMEOUT:
			stdout = self.ssh.sendQuerry(ls_cmd)
			output = stdout.readline()
			if output.find(filename, 0, len) == 0:
				TRIG_PASS_FLAG = True
			i = i + 1
		
		if not TRIG_PASS_FLAG:
			self.logger.error("ADC file time out")
		else:
			self.ftpFile(filename)
		return TRIG_PASS_FLAG

	def setPolarity(self, polarity):
		if polarity:
			self.polarity = -1
		else:
			self.polarity = 1

	def ADCfiletoData(self):
		self.singleData = fil2a.BinFiletoArray(ADC_DATA_FILE, 4, 'f', self.loggername)*self.polarity
		if len(self.singleData) > 0:
			self.singleData = np.delete(self.singleData, 0)
			if (self.ms1noisefilter):
				self.singleData = sp.signal.medfilt(self.singleData, self.ms1filterLevel*2+1)
		else:
			self.logger.error("ADC File Empty")

	def singleCmd(self):
		rm_cmd1 = "rm " + ADC_CNT_FILE
		rm_cmd2 = "rm " + ADC_DATA_FILE
		adc_cmd = ADC_CMD + " 0"
		self.ssh.sendCmd(rm_cmd1)
		self.ssh.sendCmd(rm_cmd2)
		self.ssh.sendCmd(self.cmd)
		self.ssh.sendCmd(adc_cmd, getpty = True, timedelay = self.delay_time)
		self.checkAndGetFile(ADC_DATA_FILE, 13)
		self.ADCfiletoData()

	def ms1single(self):
		time.sleep(0.1)
		if self.ms1singleRunFlag:
			self.singleCmd()
			self.ms1_update_array.emit(self.singleData)
		self.ms1_single_finished.emit()

	def ms1multiRun(self):
		
		while (self.ms1runFlag and self.rawfileindex < self.runLoop):
			self.singleCmd()
			newdatalen = len(self.singleData)
			outdata = self.singleData
			self.ms1datalen = min(newdatalen, self.ms1datalen)	
			self.ms1TotalData = self.ms1TotalData[0:self.ms1datalen]
			outdata = outdata[0:self.ms1datalen]
			self.ms1TotalData += outdata
			if (self.ms1saveRawPath != ''):
				curr_time = datetime.datetime.now()
				fname = self.ms1saveRawPath +"/"+curr_time.strftime("%Y_%m_%d_%H_%M_%S")+"_"+str(self.rawfileindex)+".txt"	
				tempdata = np.array([self.xplotdata[0:self.ms1datalen], outdata], np.float64)
				tempdata = np.transpose(tempdata)
				header = self.Qss005header+"\n"+str(curr_time)+"\n"+"mass, signal"
				fil2a.list2DtoTextFile(fname, tempdata,",",self.loggername, header = header)
			self.rawfileindex += 1
			totalDataOut = self.ms1TotalData / self.rawfileindex

			self.ms1_update_total_array.emit(self.singleData, totalDataOut)
		# while end
		self.ms1_finished.emit()

# start the function define for calibration
	def calibra_init(self):
		self.calibPreset = [1, 0]
		self.currData = np.zeros(INIT_DATACOUNT)
		self.xplotdata = np.zeros(INIT_DATACOUNT)

	def calibra_findPeak(self, minHeight, minWidth, calib):
		if calib:
			self.peaks, _= sp.signal.find_peaks(self.currData, height = minHeight, width = minWidth)
		else:
			self.peaks, _= sp.signal.find_peaks(self.singleData, height = minHeight, width = minWidth)
		
		self.logger.debug("lens of peak" + str(self.peaks))
		self.logger.debug(str(self.peaks))
		return self.peaks

	def calibra_curveFit(self, calbratedata) :
		num = len(calbratedata)
		fitIndex = []
		calbIndex = []
		for i in range(0, num):
			fitIndex.append(self.peaks[calbratedata[i][0]])
			calbIndex.append(calbratedata[i][1])
		calibPreset = np.polyfit(fitIndex, calbIndex, 1)
		self.calibPreset[0] = "%2.4f"%calibPreset[0]
		self.calibPreset[1] = "%2.4f"%calibPreset[1]
		self.logger.debug(str(self.calibPreset))

	def updateCalMass(self):
		for i in range(0, INIT_DATACOUNT):
			self.xplotdata[i] = i*float(self.calibPreset[0]) + float(self.calibPreset[1])


#gauge 
class qss005ActionHK(QObject):
	gauge_update_text = pyqtSignal(str)
	gauge_finished = pyqtSignal()

	def __init__(self, ssh, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.gauge_init()
		self.ssh = ssh

	def gauge_init(self):
		self.gauge_runFlag = False

	def gauge_readData(self):
		cmd = UART_CMD + "1 \"@254PR1?;FF\""
		#print(cmd)
		#i = 0
		ErrStr = ""
		while (self.gauge_runFlag):
			stdout, stderr = self.ssh.sendQuerryWithError(cmd)
			ErrStr = stderr.readline()
			#print("ErrStr="+ErrStr)
			if (ErrStr != ""):
				ErrStr = "ERROR"
				outlist = []
				self.gauge_update_text.emit(ErrStr)
				cmd = "ps aux | grep UART"
				stdout = self.ssh.sendQuerry(cmd)
				line = stdout.readline()
				#print(line)
				if (line != ""):
					subline = line.rstrip('\n')
					#print(subline)
					outlist.append(subline.split(' '))
					#print(outlist)
					cmd = "kill -9 " + outlist[0][6]
					#print(cmd)
					stdout = self.ssh.sendQuerry(cmd)
				self.gauge_runFlag = False
			else:
				output = stdout.readline()
				if (output != ""):
					output2 = output[7:-4]
					output = str(float(output2))
					self.gauge_update_text.emit(output)
				#print(i)
				#self.gauge_update_text.emit(str(i))
				#i = i + 1
				time.sleep(1)
		# while end
		self.gauge_finished.emit()

