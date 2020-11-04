import os
import sys
sys.path.append("../")
import time
import datetime
import logging
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.NetSSH as net 
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import py3lib.fakeData as fakeData

CH1_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./CH1 "
DAC8_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./DAC 8 "
MST_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./MST "

ADC_MV_SCAN_READ = "LD_LIBRARY_PATH=/opt/quantaser/lib ./ADC_MV "
MV_Number_str = "50 "
ADC_SCAN_READ_gain = '1'

Save_Flag = " 1"
Adc_Offset = " 76"
Adc_Gain_P = " 30"
Adc_Gain_N = " 25"

ADC_FILE = "adc_data.bin"
VDC_FILE = "vdc.bin"
VRF_FILE = "vrf.bin"
MST_FILE = "MST.txt"

RFGain = 1000.0
DCGain = 5000.0/6.0
optdtp = np.dtype([('cdc', float),('crf', float),('mass', float)])

TEST_MODE = True

# start the function define for all QSS005
class qss005Action():
	def __init__(self, loggername, paraent = None):	
		self.loggername = loggername
		self.ssh = net.NetSSH(loggername)
		
	def sshConnect(self, ch, ip, port, usr, psswd):
		sshresult = self.ssh.connectSSH(ip, port, usr, psswd)
		ftpresult = self.ssh.connectFTP()
		if TEST_MODE:
			return True
		else:
			return (sshresult and ftpresult)


class DC_Action(QObject):
	update_data = pyqtSignal(object)
	finished = pyqtSignal()
	def __init__(self, port, loggername, paraent=None):
		super(QObject, self).__init__(paraent)
		self.port = port
		self.runFlag = False
		self.cmd = ""
		self.sampleTime = 0

	def sendCmd(self, freq, cdc, crf, mass):
		ch1_amp = crf * mass
		ch1_cmd = CH1_CMD + str(freq) + " " + str(ch1_amp) + " 0"
		if TEST_MODE:
			# print(ch1_cmd)
			pass
		else:
			self.port.sendCmd(ch1_cmd, True)

		dac8_amp = cdc * mass
		dac8_cmd = DAC8_CMD + str(dac8_amp)
		if TEST_MODE:
			# print(dac8_cmd)
			pass
		else:
			self.port.sendCmd(dac8_cmd, True)

	def setAdcCmd(self, sample_time, Channel_str):
		self.sampleTime = sample_time
		print(self.sampleTime)
		self.cmd = ADC_MV_SCAN_READ + Channel_str + MV_Number_str + ADC_SCAN_READ_gain
		print(self.cmd)

	def readData(self):
		data = np.empty(0)

		while self.runFlag:
			SR_read = 0.0
			if TEST_MODE:
				SR_read = np.random.rand()
			else:
				stdout = self.port.sendQuerry(self.cmd, getpty = False, timedelay = 0)
				output = stdout.readline()
				SR_read = float(output)
			data = np.append(data, SR_read)
			self.update_data.emit(data)
			time.sleep(self.sampleTime)
		# while end
		self.finished.emit()


#Quadrupole Mass Filter
class TicAction(QObject):
	update_data = pyqtSignal(object, object, object, int)
	finished = pyqtSignal()

	def __init__(self, port, loggername, paraent=None):
		super(QObject, self).__init__(paraent)
		self.port = port
		self.loggername = loggername
		self.ticFlag = False
		self.logger = logging.getLogger(loggername)
		self.polarity = 1

	def checkAndGetFile(self, filename, len):
		data = np.empty(0)
		ls_cmd = "ls " + filename
		TIC_PASS_FLAG = False
		i = 0
		while (TIC_PASS_FLAG == False) and (self.ticFlag):
			stdout = self.port.sendQuerry(ls_cmd, getpty = False, timedelay = 0)
			output = stdout.readline()
			#print(str(i) + ',' + str(output))
			if output.find(filename, 0, len) == 0:
				TIC_PASS_FLAG = True
			i = i + 1
			time.sleep(0.1)

		if (TIC_PASS_FLAG):
			time.sleep(0.1)
			self.port.getFtpFile(filename)

		return TIC_PASS_FLAG

	def ticInit(self, optData, minMass, maxMass, dcOffset, rfOffset, optimized, cdc, crf):
		self.data = np.zeros([3, self.pts])
		self.avg = np.zeros([self.rolling, self.pts])
		self.all = np.zeros(self.pts)
		self.time_array = np.zeros(0)
		self.singleData = np.empty(0)
		self.generateMass(optData, minMass, maxMass, dcOffset, rfOffset, optimized, cdc, crf)

	def setParam(self, freq, pts, rolling, delay, threshold, width, negative, mass_start, mass_stop, saveRawPath, header):
		self.freq = freq
		self.pts = pts
		self.rolling = rolling
		self.delay = delay
		self.threshold = threshold
		self.width = width
		if negative:
			self.polarity = -1
		else:
			self.polarity = 1
		self.mass_start = mass_start
		self.mass_stop = mass_stop 
		self.saveRawPath = saveRawPath
		self.header = header

	def ticSendCmd(self):
		self.port.putFtpFile(VDC_FILE)
		self.port.putFtpFile(VRF_FILE)
		# write MST.txt "0" to run
		fp = open(MST_FILE,"w")
		fp.writelines("0")
		fp.close
		self.port.putFtpFile(MST_FILE)
		# send start Cmd
		# MST_CMD
		mst_cmd = MST_CMD + str(self.freq) + " " + str(self.pts) + " " + str(self.delay) + " " + VDC_FILE + " " + VRF_FILE
		if TEST_MODE:
			print(mst_cmd)
			pass
		else:
			self.port.sendCmd(mst_cmd, True)

	def ticGetData(self):
		if TEST_MODE:
			# print("action : " + str(self.pts))
			fakeD = fakeData.QSS005MSData(self.pts)
			define = fakeD.genRandDefine(5, 6)
			fakeD.genPeak(define, 4)
			fakeD.genNoise(1)
			self.singleData = fakeD.data*self.polarity
			time.sleep(0.5)
		else:
			self.checkAndGetFile(ADC_FILE,12)
			self.ADCfiletoData()
		# rm ADC file
		rm_cmd = "rm " + ADC_FILE
		self.port.sendCmd(rm_cmd)

	def ADCfiletoData(self):
		self.singleData = fil2a.BinFiletoArray(ADC_DATA_FILE, 4, 'f', self.loggername)*self.polarity
		if len(self.singleData) > 0:
			self.singleData = np.delete(self.singleData, 0)
			if (self.ms1noisefilter):
				self.singleData = sp.signal.medfilt(self.singleData, self.ms1filterLevel*2+1)
		else:
			self.logger.error("ADC File Empty")

	def saveSingleFile(self):
		if (self.saveRawPath != ''):
			curr_time = datetime.datetime.now()
			fname = self.saveRawPath + "/" + curr_time.strftime("%Y_%m_%d_%H_%M_%S") + "_" + str(index) + ".txt"
			tempdata = np.array([self.mass_array, self.singleData], np.float64)
			tempdata = np.transpose(tempdata)
			header = self.header + "\n" + str(curr_time) + "\n" + "mass, signal"
			fil2a.list2DtoTextFile(fname, tempdata, ",", self.loggername, header = header)

	def sendStopCmd(self):
		# write MST.txt "1" to stop
		fp = open(MST_FILE,"w")
		fp.writelines("1")
		fp.close
		self.port.putFtpFile(MST_FILE)

	def ticRun(self):
		tic_array = np.zeros(0)
		xic_array = np.zeros(0)
		start_time = time.time()
		index = 0
		self.ticSendCmd()
		while(self.ticFlag):
			self.ticGetData()
			# print(self.singleData)
			self.data[0] = self.singleData
			inner_index = index % self.rolling
			self.avg[inner_index] = self.data[0]
			self.all = self.all + self.data[0]
			self.saveSingleFile()
			index = index+1
			if (index < self.rolling):
				self.data[1] = sum(self.avg)/index 
			else:
				self.data[1] = sum(self.avg)/self.rolling
			self.data[2] = self.all/index 
			temp = self.findPeak()
			self.time_array = np.append(self.time_array, time.time()-start_time)
			tic_array = np.append(tic_array, temp[0])
			xic_array = np.append(xic_array, temp[1])
			self.update_data.emit(self.data, tic_array, xic_array, index)
		self.sendStopCmd()
		self.finished.emit()

	def generateMass(self, optData, minMass, maxMass, dcOffset, rfOffset, optimized, ui_cdc, ui_crf):
		optDataOut = np.array(optData)
		optDataOut = optDataOut[np.argsort(optDataOut[:,2])]
		self.optimizeCurve(optDataOut, minMass, maxMass)
		self.mass_array = np.empty(0)
		self.vdc_array = np.empty(0)
		self.vrf_array = np.empty(0)
		dm = (self.mass_stop - self.mass_start)/float(self.pts-1)
		self.index_min = int((minMass - self.mass_start)/dm)
		self.index_max = int((maxMass - self.mass_start)/dm)
		optindex = 0
		for i in range(0, self.pts):
			mass = self.mass_start + dm*i
			self.mass_array = np.append(self.mass_array, mass)
			if (mass > optDataOut[optindex][2]) and ((optindex+1) < len(self.cdc_param)):
				optindex = optindex + 1
			if (optimized):
				cdc = self.cdc_param[optindex][0]*mass + self.cdc_param[optindex][1]
				vdc = cdc*mass
				crf = self.crf_param[optindex][0]*mass + self.crf_param[optindex][1]
				vrf = crf*mass
			else:
				vdc = ui_cdc*mass
				vrf = ui_crf*mass
			#self.vdc_array = np.append(self.vdc_array, cdc*mass + dcOffset)
			#self.vrf_array = np.append(self.vrf_array, crf*mass + rfOffset)
			self.vdc_array = np.append(self.vdc_array, vdc)
			self.vrf_array = np.append(self.vrf_array, vrf)

		fil2a.ArraytoBinFile(VDC_FILE, self.vdc_array,'f')
		fil2a.ArraytoBinFile(VRF_FILE, self.vrf_array,'f')

	def findPeak(self):
		self.peaks, _ = sp.signal.find_peaks(self.data[0], height =self.threshold, width=self.width)
		peak_num = len(self.peaks)
		ticsum = 0
		xicsum = 0
		for index  in self.peaks:
			ticsum = ticsum + self.data[0][index]
			if index > self.index_min and index < self.index_max:
				xicsum = xicsum + self.data[0][index]

		return [ticsum, xicsum]

	def optimizeCurve(self, optData, minMass, maxMass):
		#optData must comein as list in order [cdc, crf, mass]
		self.cdc_param = []
		self.crf_param = []
		if optData[0][2] > minMass:
			self.cdc_param.append([0, optData[0][0], optData[0][2]])
			self.crf_param.append([0, optData[0][1], optData[0][2]])
		for i in range(len(optData)-1):
			x0 = optData[i][2]
			y0 = optData[i][0]
			z0 = optData[i][1]
			x1 = optData[i+1][2]
			y1 = optData[i+1][0]
			z1 = optData[i+1][1]
			a_cdc = (y0-y1)/(x0-x1)
			b_cdc = y0 - a_cdc*x0
			a_crf = (z0-z1)/(x0-x1)
			b_crf = z0 -a_crf*x0
			self.cdc_param.append([a_cdc, b_cdc, x1])
			self.crf_param.append([a_crf, b_crf, x1])
		if optData[len(optData-1)][2]< maxMass:
			self.cdc_param.append([0, optData[len(optData-1)][0], optData[len(optData-1)][2]])
			self.crf_param.append([0, optData[len(optData-1)][1], optData[len(optData-1)][2]])


