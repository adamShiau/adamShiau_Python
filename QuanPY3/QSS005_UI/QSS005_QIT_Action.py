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

WFM_Bin_File1 = "trig_data.bin"
WFM_Bin_File2 = "trig_data2.bin"

MST_PATH = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./MST"
Save_Flag = " 1"
Adc_Offset = " 76"
Adc_Gain_P = " 30"
Adc_Gain_N = " 25"

ADC_FILE = "adc_data.bin"

RFGain = 1000.0
DCGain = 5000.0/6.0

# start the function define for all QSS005
class qss005Action():
	def __init__(self, loggername, paraent = None):	
		self.loggername = loggername
		self.ssh1 = net.NetSSH(loggername)
		self.ssh2 = net.NetSSH(loggername)

	def sshConnect(self, ch, ip, port, usr, psswd):
		if ch == 2:
			sshresult = self.ssh2.connectSSH(ip, port, usr, psswd)
			ftpresult = self.ssh2.connectFTP()
		else:
			sshresult = self.ssh1.connectSSH(ip, port, usr, psswd)
			ftpresult = self.ssh1.connectFTP()
		return (sshresult and ftpresult)

	def ftpFile(self, ch, filename):
		if ch == 2:
			self.ssh2.getFtpFile(filename)
		else:
			self.ssh1.getFtpFile(filename)


#Waveform Output
class wfoAction(QObject):
	update_data = pyqtSignal(object)
	finished = pyqtSignal()

	def __init__(self, port, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.port = port
		self.WFO_runFlag = False
		self.sample_time = 1
		self.acqu_time = 1

	def WFO_setCmdAndValue(self, cmd, sample_time, acqu_time):
		self.cmd = cmd
		self.sample_time = sample_time
		self.acqu_time = acqu_time

	def WFO_readData(self):
		data = np.empty(0)
		start_time = time.time()

		while (self.WFO_runFlag and ( (time.time()-start_time) < self.acqu_time) ):
			now_time = time.time()
			SR_read = 0.0

			stdout = self.port.sendQuerry(self.cmd, getpty = False, timedelay = 0)
			output = stdout.readline()
			SR_read = float(output)
			data = np.append(data, SR_read)
			self.update_data.emit(data)
			time_diff = time.time() - now_time
			if (time_diff < self.sample_time):
				time.sleep(self.sample_time - time_diff)
			# while end
		if (self.WFO_runFlag):
			self.WFO_runFlag = False
		self.finished.emit()


#Waveform Monitor
class wfmAction(QObject):
	update_data = pyqtSignal(object, object)
	finished = pyqtSignal()

	def __init__(self, port, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.port = port
		self.loggername = loggername
		self.WFM_runFlag = False

	def WFM_setCmd(self, cmd):
		self.cmd = cmd

	def WFM_readBinData(self):
		#rm_cmd = "rm trig_pass"
		rm_cmd1 = "rm " + WFM_Bin_File1
		rm_cmd2 = "rm " + WFM_Bin_File2

		while (self.WFM_runFlag):
			WFM_Bin_Data1 = np.empty(0)
			WFM_Bin_Data2 = np.empty(0)
			TRIG_PASS_FLAG1 = False 
			TRIG_PASS_FLAG2 = False 

			self.port.sendCmd(rm_cmd1, getpty = False, timedelay = 0)
			self.port.sendCmd(rm_cmd2, getpty = False, timedelay = 0)
			self.port.sendCmd(self.cmd, getpty = False, timedelay = 0)

			TRIG_PASS_FLAG1 = self.checkAndGetFile(WFM_Bin_File1, 13) 
			if TRIG_PASS_FLAG1:
				WFM_Bin_Data1 = fil2a.BinFiletoArray(WFM_Bin_File1, 4, 'f', self.loggername)
				#print(WFM_Bin_Data1)

			TRIG_PASS_FLAG2 = self.checkAndGetFile(WFM_Bin_File2, 14)
			if TRIG_PASS_FLAG2:
				WFM_Bin_Data2 = fil2a.BinFiletoArray(WFM_Bin_File2, 4, 'f', self.loggername)
				#print(WFM_Bin_Data2)

			if TRIG_PASS_FLAG1 and TRIG_PASS_FLAG2:
				self.update_data.emit(WFM_Bin_Data1, WFM_Bin_Data2)
			# while end
		self.finished.emit()

	def checkAndGetFile(self, filename, len):
		data = np.empty(0)
		ls_cmd = "ls " + filename
		TRIG_PASS_FLAG = False
		i = 0
		while (TRIG_PASS_FLAG == False) and (self.WFM_runFlag):
			stdout = self.port.sendQuerry(ls_cmd, getpty = False, timedelay = 0)
			output = stdout.readline()
			#print(str(i) + ',' + str(output))
			if output.find(filename, 0, len) == 0:
				TRIG_PASS_FLAG = True
			i = i + 1
			time.sleep(0.1)

		if (TRIG_PASS_FLAG):
			time.sleep(0.1)
			self.port.getFtpFile(filename)

		return TRIG_PASS_FLAG


#Quadrupole Mass Filter
class ticAction(QObject):
	update_data = pyqtSignal(object, object, object, int)
	finished = pyqtSignal()

	def __init__(self, port, loggername, paraent=None):
		super(QObject, self).__init__(paraent)
		self.port = port
		self.loggername = loggername
		self.ticFlag = False
		self.logger = logging.getLogger(loggername)

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

	def ticGetData(self, cmd, pts):
		#print(cmd)
		#print("pst = "+ str(pts))
		rm_cmd = "rm " + ADC_FILE
		self.port.sendCmd(rm_cmd)
		sleeptime = pts*0.0002
		self.port.sendCmd(cmd)
		time.sleep(sleeptime)
		TIC_PASS_FLAG = self.checkAndGetFile(ADC_FILE, 12) 
		tic_data = np.zeros(pts)
		if TIC_PASS_FLAG:
			tic_data = fil2a.BinFiletoArray(ADC_FILE, 4, 'f', self.loggername)
		return tic_data

	def ticRun(self):
		self.data = np.zeros([3, self.pts])
		self.avg = np.zeros([self.rolling, self.pts])
		self.all = np.zeros(self.pts)
		tic_array = np.zeros(0)
		xic_array = np.zeros(0)
		self.time_array = np.zeros(0)
		start_time = time.time()
		index = 0
		while (self.ticFlag):
			tic_data = self.ticGetData(self.cmd,self.pts)
			data_len = len(tic_data)
			if (data_len < self.pts):
				self.pts = data_len
				#print(self.pts)

				datatemp = np.zeros([3, data_len])
				for i in range(0,3):
					datatemp[i] = self.data[i][0:data_len]
				self.data = datatemp
				#print(len(self.data[0]))

				avgtemp = np.zeros([self.rolling, data_len])
				for i in range(0,self.rolling):
					avgtemp[i] = self.avg[i][0:data_len]
				self.avg = avgtemp
				#print(len(self.avg[0]))

				self.all = np.delete(self.all, data_len)
				#print(len(self.all))

				self.mass_array = np.delete(self.mass_array, data_len)
				#print(len(self.mass_array))
			else:
				self.data[0] = tic_data[0:self.pts]


			inner_index = index % self.rolling
			self.avg[inner_index] = self.data[0]
			self.all = self.all + self.data[0]
			if (self.saveRawPath != ''):
				curr_time = datetime.datetime.now()
				fname = self.saveRawPath + "/" + curr_time.strftime("%Y_%m_%d_%H_%M_%S") + "_" + str(index) + ".txt"
				tempdata = np.array([self.mass_array, self.data[0]], np.float64)
				tempdata = np.transpose(tempdata)
				header = self.header + "\n" + str(curr_time) + "\n" + "mass, signal"
				fil2a.list2DtoTextFile(fname, tempdata,",",self.loggername, header = header)
			
			index = index + 1
			
			if (index < self.rolling):
				self.data[1] = sum(self.avg)/index
			else:
				self.data[1] = sum(self.avg)/self.rolling

			self.data[2] = self.all/index

			temp = self.findPeak()
			tic_array = np.append(tic_array, temp[0])
			xic_array = np.append(xic_array, temp[1])
			self.time_array = np.append(self.time_array, time.time()-start_time)
			self.update_data.emit(self.data, tic_array, xic_array, index)
			# while end
		self.finished.emit()
	
	def genrateMass(self, minMass, maxMass):
		self.mass_array = np.empty(0)
		dm = (self.mass_stop - self.mass_start)/float(self.pts-1)
		self.index_min = int((minMass - self.mass_start)/dm)
		self.index_max = int((maxMass - self.mass_start)/dm)
		for i in range(0, self.pts):
			self.mass_array = np.append(self.mass_array, self.mass_start + dm*i)

	def calVolt(self, radius, freq):
		# print("calVolt")
		r2f2 = radius*radius*freq*freq
		ur2f2 = 1.212033e-8*r2f2
		vr2f2 = 7.2225e-8*r2f2
		ustart = self.mass_start*ur2f2/RFGain #AC
		uend = self.mass_stop*ur2f2/RFGain #AC
		ustep = (uend - ustart) / (self.pts - 1) #AC
		vstart = self.mass_start*vr2f2/DCGain #DC
		vend = self.mass_stop*vr2f2/DCGain #DC
		vstep = (vend - vstart) / (self.pts - 1) #DC
		self.logger.debug("r2f2 = " + str(r2f2))
		self.logger.debug("ustart = " + str(ustart) + ", uend = " + str(uend))
		self.logger.debug("vstart = " + str(vstart) + ", vend = " + str(vend))
		self.cmd = MST_PATH + " " + str(freq) + " " + str(self.pts) + " " \
				+ str(ustart) + " " + str(ustep) + " " + str(vstart) + " " + str(vstep) \
				+ Save_Flag + Adc_Offset + Adc_Gain_P + Adc_Gain_N
		# print(self.cmd)
		# print([ustart, uend, ustep, vstart, vend, vstep])
		return [ustart, uend, vstart, vend]

	def calVolt2(self, freq, cdc, crf):
		# print("calVolt2")
		ustart = self.mass_start*cdc #AC
		uend = self.mass_stop*cdc #AC
		ustep = (uend - ustart) / (self.pts - 1) #AC
		vstart = self.mass_start*crf #DC
		vend = self.mass_stop*crf #DC
		vstep = (vend - vstart) / (self.pts - 1) #DC
		self.logger.debug("ustart = " + str(ustart) + ", uend = " + str(uend))
		self.logger.debug("vstart = " + str(vstart) + ", vend = " + str(vend))
		self.cmd = MST_PATH + " " + str(freq) + " " + str(self.pts) + " " \
				+ str(ustart) + " " + str(ustep) + " " + str(vstart) + " " + str(vstep) \
				+ Save_Flag + Adc_Offset + Adc_Gain_P + Adc_Gain_N
		# print(self.cmd)
		# print([ustart, uend, ustep, vstart, vend, vstep])
		return [ustart, uend, vstart, vend]

	def setParam(self, rolling, pts, threshold, width, mass_start, mass_stop, saveRawPath, header):
		self.rolling = rolling
		self.pts = pts
		self.threshold = threshold
		self.width = width
		self.mass_start = mass_start
		self.mass_stop = mass_stop 
		self.saveRawPath = saveRawPath
		self.header = header

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







