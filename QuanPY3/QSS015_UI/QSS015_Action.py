import os
import sys
sys.path.append("../")
import time
import numpy as np 
import scipy as sp 
from scipy import signal
import py3lib.COMPort as usb 
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging

DAC_Constant_S5 = 6.0/2000.0
DAC_ratio = 65535.0 / 10.0
Fan_DAC_ratio = 65535.0 / 5.0
DAC_Constant_ESI = 6.0 / 5000.0

ADC_ratio = 65535.0 / 20.0
ADC_offset = 10.0

INCREASE_STEP = 100
SLOWINCREASE_TIME = 0.01 #change to 0.01 in formal version

DC_CHANNEL = 1
SCAN_CHANNEL = 2
ESI_CHANNEL = 3
FAN_CHANNEL = 4

TEST_MODE = False

class QSS015ction(QObject):
	update_text = pyqtSignal(float, float)
	# update_array = pyqtSignal(object, object, object)
	update_array_filter = pyqtSignal(object, object, object, bool, object)
	update_index = pyqtSignal(int, object)
	update_xic = pyqtSignal(object, object, object)
	finished = pyqtSignal()

	def __init__(self, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.Qss015header = ""
		self.COM = usb.FT232(loggername)
		self.logger = logging.getLogger(loggername)
		self.data = np.zeros(0)
		self.Alldata = np.zeros(0)
		self.Alldata2 = np.zeros(0)
		self.xicData = np.zeros(0)
		self.ticData = np.zeros(0)
		self.dv = np.zeros(0)
		self.run_index = 0
		self.Vdcout = 0
		self.Vscanout = 0

	# start the function define for all QSS015
	def usbConnect(self):
		if (TEST_MODE):
			status = True
		else:
			status = self.COM.connect(timeout = 0.5)
		return status

	def sendComCmd(self, cmd):
		# print (cmd)
		self.COM.writeLine(cmd)

	def setVoltage(self, ch, value):
		if (ch == ESI_CHANNEL):
			vout = int(value*DAC_Constant_ESI*DAC_ratio)
		elif (ch == FAN_CHANNEL):
			vout = int(value*Fan_DAC_ratio)
		else:
			vout = int(value*DAC_Constant_S5*DAC_ratio)
		
		cmd = "SetVoltage "+str(ch)+" "+str(vout)
		# print(cmd)
		self.sendComCmd(cmd)

	def readVoltage(self, mv):
		cmd = "ReadVoltage "+str(mv)
		# print(cmd)
		self.sendComCmd(cmd)

	def setIntTime(self, value):
		cmd = "SetIntTime "+str(value)
		# print(cmd)
		self.sendComCmd(cmd)

	def SlowIncrease(self, vout, vdc):
		# print("SlowIncrease vout = " + str(vout))
		# print("SlowIncrease vdc = " + str(vdc))
		while ( (vout != self.Vscanout)
			or (vdc != self.Vdcout) ):

			if (vout != self.Vscanout):
				if ( (vout - self.Vscanout) >= INCREASE_STEP):
					self.Vscanout = float(self.Vscanout + INCREASE_STEP)
				elif ( (self.Vscanout - vout) >= INCREASE_STEP):
					self.Vscanout = float(self.Vscanout - INCREASE_STEP)
				else:
					self.Vscanout = vout
				if (TEST_MODE):
					print("SlowIncrease self.Vscanout = " + str(self.Vscanout))

			if (vdc != self.Vdcout):
				if ( (vdc - self.Vdcout) >= INCREASE_STEP):
					self.Vdcout = float(self.Vdcout + INCREASE_STEP)
				elif ( (self.Vdcout - vdc) >= INCREASE_STEP):
					self.Vdcout = float(self.Vdcout - INCREASE_STEP)
				else:
					self.Vdcout = vdc
				if (TEST_MODE):
					print("SlowIncrease self.Vdcout = " + str(self.Vdcout))

			self.setVoltage(SCAN_CHANNEL, self.Vscanout)
			self.setVoltage(DC_CHANNEL, self.Vdcout)
			time.sleep(SLOWINCREASE_TIME)
			# print("--------")

	def VoltageOut(self, scanFlag, scanParam):
		fs = 1000.0/float(scanParam.delay)
		critalF = 2*scanParam.cutFreq / fs
		# add set integral time
		self.setIntTime(scanParam.delay*1000)

		b, a = sp.signal.butter(5, critalF, 'low', analog = False)
		xic_t = np.empty(0)
		t0 = time.time()

		while (self.run_index < scanParam.max_run_loops) and (self.run_flag):
			status = 0
			self.data = np.zeros(0)

			#self.Alldata = np.zeros(0)
			#self.Alldata2 = np.zeros(0)
			i = scanParam.scanBkWd * (-1)
			vdc = float(scanParam.dc_fixed)
			vout = float(scanParam.start) 
			self.SlowIncrease(vout, vdc)
			while (i < scanParam.loops) and (self.run_flag):	
				vout = float(scanParam.start) + scanParam.step * float(i) / 1000.0
				dv = vout - vdc
				self.Vscanout = vout
				self.setVoltage(SCAN_CHANNEL, self.Vscanout)
				if (TEST_MODE):
					print("VoltageOut self.Vscanout = " + str(self.Vscanout))
				time.sleep(scanParam.delay/1000.0)
				self.readVoltage(scanParam.mv_avg_num)
				adcValue = 0
				# print("read adc")
				if (TEST_MODE):
					temp = np.random.rand()*65535
				else:
					temp = self.COM.readLine()
				if (temp != '') or (temp != "ERROR"):
					# print("temp = " + str(temp))
					adcValue = (int(temp)/ADC_ratio-ADC_offset)*scanParam.adc_pority*1000 + scanParam.offset
					# print("adcValue = " + str(adcValue))
					# print("----------")
					self.update_text.emit(vout, adcValue)
				if (i >= 0):
					#print (i)
					self.data = np.append(self.data, adcValue)
					if (scanFlag and (self.run_index == 0)):
						self.dv = np.append(self.dv, dv)
					elif not scanFlag:
						self.dv = np.append(self.dv,i)
					if (self.run_index == 0):
						self.Alldata = np.append(self.Alldata, adcValue)
						self.Alldata2 = np.append(self.Alldata2, adcValue)
					else:
						self.Alldata[i] = self.Alldata[i] + adcValue						
						self.Alldata2[i] =  self.Alldata[i] / float(self.run_index + 1)
					if scanParam.filter:
						filteredData = sp.signal.lfilter(b, a, self.data)
						self.update_array_filter.emit(self.data, self.Alldata2, self.dv, True, filteredData)
					else:
						# self.update_array.emit(self.data, self.Alldata2, self.dv)
						self.update_array_filter.emit(self.data, self.Alldata2, self.dv, False, None)
				i += 1
			t = time.time() - t0
			xic_t = np.append(xic_t, t)
			self.update_index.emit(self.run_index+1, self.data)
			if scanParam.xicMode:
				self.ticFunction(scanParam)
				self.update_xic.emit(xic_t, self.ticData, self.xicData)
			self.run_index += 1
		self.finished.emit()

	def ticFunction(self, scanParam):
		anaresult =self.findPeak(self.dv, self.data, scanParam.ana_height, scanParam.ana_width)
		peaknum = len(anaresult)
		Massmin = scanParam.xic_center - scanParam.xic_delta
		Massmax = scanParam.xic_center + scanParam.xic_delta
		ticValue = 0
		xicValue = 0
		if peaknum > 0:
			for i in range(0, peaknum):
				ticValue = ticValue + anaresult[i][1]
				if (Massmin < anaresult[i][1]) and (anaresult[i][1] < Massmax):
					xicValue = xicValue + anaresult[i][1]
			self.ticData = np.append(self.ticData, ticValue)
			self.xicData = np.append(self.xicData, xicValue)
		else:
			self.ticData = np.append(self.ticData, 0)
			self.xicData = np.append(self.xicData, 0)
			self.logger.warning("No Peak was found during xic process")

	def findPeak(self, ana_x, ana_y, threshold, inputwidth):
		peaks, _= sp.signal.find_peaks(ana_y, height= threshold, width = inputwidth)
		fwhm = sp.signal.peak_widths(ana_y, peaks, rel_height = 0.5)
		analist = []
		i = 0
		for index in peaks:
			xvalue = ana_x[index]
			yvalue = ana_y[index]
			width = fwhm[0][i]
			analist.append([xvalue, yvalue, width])
		i = i+1 
		return analist

	def resetAlldata(self):
		self.data = np.zeros(0)
		self.Alldata = np.zeros(0)
		self.Alldata2 = np.zeros(0)
		self.dv = np.zeros(0)
		self.run_index = 0
		self.ticData = np.zeros(0)
		self.xicData = np.zeros(0)




class QSS015ction2(QObject):
	update_fan = pyqtSignal(int)
	finished = pyqtSignal()
	def __init__(self, port, loggername, paraent = None):
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.COM = port
		self.fanFlag = False

	def fanQuerry(self):
		while self.fanFlag:
			# print("ReadCounter")
			self.COM.writeLine("ReadCounter")
			# print("read fan")
			freq = int(self.COM.readLine())
			#freq = np.random.rand()*3000
			self.update_fan.emit(freq)
			time.sleep(1)

		self.finished.emit()
