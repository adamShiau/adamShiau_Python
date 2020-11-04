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
# MST_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./MST "
MST1_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./MST_CH1 "
MST2_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./MST_CH2 "
#ADC_MV_SCAN_READ = "LD_LIBRARY_PATH=/opt/quantaser/lib ./ADC_MV "
ADC_MV_CH1_READ = "LD_LIBRARY_PATH=/opt/quantaser/lib ./ADC_MV_CH1 "
ADC_MV_CH2_READ = "LD_LIBRARY_PATH=/opt/quantaser/lib ./ADC_MV_CH2 "

MV_Number_str = "50 "
# ADC_SCAN_READ_gain = '1'
SAVE_FILE_CMD = " 1 "

QIT_ADC_FILE = "QIT_adc_data.bin"
VDC_FILE = "vdc.bin"
VRF_FILE = "vrf.bin"
MST_FILE = "MST.txt"

RFGain = 1000.0
DCGain = 5000.0/6.0
optdtp = np.dtype([('cdc', float),('crf', float),('mass', float)])

TEST_MODE = False

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
		self.calib_offset = 0

	def send_DC_Cmd(self, freq, cdc, crf, mass):
		ch1_amp = crf * mass
		ch1_cmd = CH1_CMD + str(freq) + " " + str(ch1_amp) #+ " 0"

		if TEST_MODE:
			# print(ch1_cmd)
			pass
		else:
			# print(ch1_cmd)
			self.port.sendCmd(ch1_cmd)
			time.sleep(0.1)

		dac8_amp = cdc * mass
		dac8_cmd = DAC8_CMD + str(dac8_amp)
		if TEST_MODE:
			# print(dac8_cmd)
			pass
		else:
			# print(dac8_cmd)
			self.port.sendCmd(dac8_cmd)

	def send_stop_Cmd(self):
		ch1_cmd = CH1_CMD + "0 0"

		if TEST_MODE:
			# print(ch1_cmd)
			pass
		else:
			# print(ch1_cmd)
			self.port.sendCmd(ch1_cmd)
			time.sleep(0.1)

		dac8_cmd = DAC8_CMD + "0"
		if TEST_MODE:
			# print(dac8_cmd)
			pass
		else:
			# print(dac8_cmd)
			self.port.sendCmd(dac8_cmd)

	def setAdcCmd(self, sample_time, channel, engData):
		self.sampleTime = sample_time
		adc_offset = engData[0]
		adc_gain_p = engData[1]
		adc_gain_n = engData[2]
		# print(self.sampleTime)
		# self.cmd = ADC_MV_SCAN_READ + str(channel) + MV_Number_str + ADC_SCAN_READ_gain
		if (channel == 0):
			self.cmd = ADC_MV_CH1_READ
		else:
			self.cmd = ADC_MV_CH2_READ
		self.cmd = self.cmd + MV_Number_str + adc_offset  + ' ' + adc_gain_p + ' ' + adc_gain_n
		print(self.cmd)
		stdout = self.port.sendQuerry(self.cmd, getpty = False, timedelay = 0)

	def readData(self):
		data = np.empty(0)

		while self.runFlag:
			SR_read = 0.0
			if TEST_MODE:
				SR_read = np.random.rand()
			else:
				stdout = self.port.sendQuerry(self.cmd, getpty = False, timedelay = 0)
				output = stdout.readline()
				SR_read = float(output) + self.calib_offset
			data = np.append(data, SR_read)
			self.update_data.emit(data)
			time.sleep(self.sampleTime)
		# while end
		self.send_stop_Cmd()
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
		self.calib_offset = 0

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
			if (i == 4):
				self.port.sendCmd(self.mst_cmd)
				i = 0
			else:
				sleeptime = float(self.pts) * 0.2 / 1234
				if (sleeptime < 0.2):
					sleeptime = 0.2

				print("sleeptime = " + str(sleeptime))
				time.sleep(sleeptime)
				


		if (TIC_PASS_FLAG):
			#time.sleep(0.1)
			self.port.getFtpFile(filename)

		return TIC_PASS_FLAG

	def checkAndGetFile2(self, filename, sleeptime):
		cat_cmd = "cat write_done.txt"
		echo_wr0 = "echo \"0\" > write_done.txt"
		echo_rd1 = "echo \"1\" > read_done.txt"
		counter =0;
		while self.ticFlag:
			stdout = self.port.sendQuerry(cat_cmd, getpty = False, timedelay=0)
			output = stdout.readline()
			if output.find("1") >= 0:
				TIC_PASS_FLAG = True
				self.port.sendCmd(echo_wr0)
				self.port.getFtpFile(filename)
				self.port.sendCmd(echo_rd1)
				stdout = self.port.sendQuerry("ps", getpty = False, timedelay = 0)
				for line in stdout:
					print(line)
			else:
				time.sleep(sleeptime)
				counter = counter +1
				if counter == 4:
					self.port.sendCmd(self.mst_cmd)
					counter = 0
		
		return TIC_PASS_FLAG

	def ticInit(self, optData, minMass, maxMass, dcOffset, rfOffset, optimized, cdc, crf):
		self.data = np.zeros([3, self.pts])
		self.avg = np.zeros([self.rolling, self.pts])
		self.all = np.zeros(self.pts)
		self.time_array = np.zeros(0)
		self.singleData = np.empty(0)
		self.generateMass(optData, minMass, maxMass, dcOffset, rfOffset, optimized, cdc, crf)

	def setParam(self, freq, pts, rolling, delay, threshold, width, polarity, mass_start, mass_stop, channel, engData, saveRawPath, header):
		self.pts = pts
		self.rolling = rolling
		self.threshold = threshold
		self.width = width
		self.polarity = polarity
		self.mass_start = mass_start
		self.mass_stop = mass_stop 
		adc_offset = engData[0]
		adc_gain_p = engData[1]
		adc_gain_n = engData[2]
		self.saveRawPath = saveRawPath
		self.header = header

		# MST_CMD
		if (channel == 0):
			self.mst_cmd = MST1_CMD
		else:
			self.mst_cmd = MST2_CMD

		self.mst_cmd = self.mst_cmd \
				+ str(freq) + " " \
				+ str(self.pts) + " " \
				+ VDC_FILE + " " \
				+ VRF_FILE + " " \
				+ str(delay) \
				+ SAVE_FILE_CMD \
				+ str(adc_offset) + " " \
				+ str(adc_gain_p) + " " \
				+ str(adc_gain_n)

	def ticSendCmd(self):
		self.port.putFtpFile(VDC_FILE)
		self.port.putFtpFile(VRF_FILE)
		# rm ADC file
		rm_cmd = "rm " + QIT_ADC_FILE
		self.port.sendCmd(rm_cmd)
		# write MST.txt "0" to run
		echo_cmd = "echo \"0\" > " + MST_FILE
		# print(echo_cmd)
		self.port.sendCmd(echo_cmd)
		# send start Cmd
		if TEST_MODE:
			# print(self.mst_cmd)
			pass
		else:
			# print(self.mst_cmd)
			self.port.sendCmd(self.mst_cmd)

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
			self.checkAndGetFile(QIT_ADC_FILE,16)
			# sleeptime = 0.5
			# time.sleep(0.5)
			# self.checkAndGetFile2(QIT_ADC_FILE, sleeptime)
			self.ADCfiletoData()
		# rm ADC file
		rm_cmd = "rm " + QIT_ADC_FILE
		self.port.sendCmd(rm_cmd)

	def ADCfiletoData(self):
		self.singleData = fil2a.BinFiletoArray2(QIT_ADC_FILE, 4, 'f', self.loggername)
		# print("before = " + str(self.singleData[0]))
		self.singleData = (self.singleData + self.calib_offset) * self.polarity
		# print("after = " + str(self.singleData[0]))
		if len(self.singleData) > 0:
			pass
		else:
			self.logger.error("ADC File Empty")

	def saveSingleFile(self, index):
		if (self.saveRawPath != ''):
			curr_time = datetime.datetime.now()
			fname = self.saveRawPath + "/" + curr_time.strftime("%Y_%m_%d_%H_%M_%S") + "_" + str(index) + ".txt"
			tempdata = np.array([self.mass_array, self.singleData], np.float64)
			tempdata = np.transpose(tempdata)
			header = self.header + "\n" + str(curr_time) + "\n" + "mass, signal"
			fil2a.list2DtoTextFile(fname, tempdata, ",", self.loggername, header = header)

	def sendStopCmd(self):
		# write MST.txt "1" to stop
		echo_cmd = "echo \"1\" > " + MST_FILE
		# print(echo_cmd)
		self.port.sendCmd(echo_cmd)

	def ticRun(self):
		tic_array = np.zeros(0)
		xic_array = np.zeros(0)
		start_time = time.time()
		index = 0
		self.ticSendCmd()
		while(self.ticFlag):
			self.ticGetData()
			# print("len = " + str(len(self.singleData)))	
			if len(self.singleData) == self.pts:
			#print(len(self.data[0]))
				self.data[0] = self.singleData
				inner_index = index % self.rolling
				self.avg[inner_index] = self.data[0]
				self.all = self.all + self.data[0]
				self.saveSingleFile(index)
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
		self.optimizeCurve(optDataOut)
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
			if optindex < len(optDataOut):
				if (mass > optDataOut[optindex][2]):
					optindex = optindex + 1
			# print(optindex)
			if (optimized):
				cdc = self.cdc_param[optindex][0]*mass + self.cdc_param[optindex][1]
				vdc = max(cdc*mass + dcOffset, 0)
				crf = self.crf_param[optindex][0]*mass + self.crf_param[optindex][1]
				vrf = max(crf*mass + rfOffset, 0)
			else:
				vdc = max(ui_cdc*mass + dcOffset, 0)
				vrf = max(ui_crf*mass + rfOffset, 0)
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

	def optimizeCurve(self, optData):
		#optData must comein as list in order [cdc, crf, mass]
		self.cdc_param = []
		self.crf_param = []
		if optData[0][2] > self.mass_start:
			# print("optData > mass_start")
			self.cdc_param.append([0, optData[0][0], optData[0][2]])
			self.crf_param.append([0, optData[0][1], optData[0][2]])
		for i in range(len(optData)-1):
			# print("optimizecurve, i="+str(i))
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
		if optData[len(optData)-1][2]< self.mass_stop:
			# print("optData < mass_stop")
			#self.cdc_param.append([0, optData[len(optData)-1][0], optData[len(optData)-1][2]])
			#self.crf_param.append([0, optData[len(optData)-1][1], optData[len(optData)-1][2]])
			self.cdc_param.append([0, optData[len(optData)-1][0], self.mass_stop])
			self.crf_param.append([0, optData[len(optData)-1][1], self.mass_stop])
		# print(self.cdc_param)
		# print(self.crf_param)

if __name__ == '__main__':
	import matplotlib.pyplot as plt
	port = net.NetSSH("test")
	act = TicAction(port,"test")
	act.pts = 100
	act.rolling = 1
	act.mass_start = 30
	act.mass_stop = 500
	minMass	= 30
	maxMass = 500
	dcoffset = 1
	rfoffset = 2

	d1 = [3.33, 3.33, 31]
	d2 = [15, 2.5, 200]
	d3 = [20, 2, 499]
	optData =[]
	optData.append(d1)
	optData.append(d2)
	optData.append(d3)
	print(optData)
	act.ticInit(optData, minMass, maxMass, dcoffset, rfoffset, True, 5e-4, 6e-4)
	plt.plot(act.mass_array, act.vrf_array)
	plt.plot(act.mass_array, act.vdc_array)
	plt.show()


