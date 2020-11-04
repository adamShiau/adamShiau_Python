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

LIB_PATH ='LD_LIBRARY_PATH=/opt/redpitaya/lib '
MONITOR_PATH ='/opt/redpitaya/bin/monitor '

INT_HOLD_ADD = '0x4020004C '
INT_REST_ADD = '0x40200048 '
INT_INT_ADD  = '0x40200050 '
# remove request by adam 2019.11.7
# SCAN_REG_ADD = '0x40200044 '
# REG_EOI_CMD  = '0x40200054'

CYCLE_CONST = 125000 #Integrator time ratio 
DAC_Constant_S5 = 6.0/5000.0

#ADC_READ ='./ADC_MV '
ADC_READ ='./ADC_MV_2 '
ADC_GAIN ='1 '
DAC_SCAN ='./DAC 1 '
DAC_FIXED ='./DAC 2 '

INCREASE_STEP = 100
SLOWINCREASE_TIME = 0.01 #change to 0.01 in formal version

class qss004Action(QObject):
	update_text = pyqtSignal(float, float)
	update_array = pyqtSignal(object, object, object)
	update_index = pyqtSignal(int, object)
	finished = pyqtSignal()

	def __init__(self, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.Qss004header = ""
		self.ssh = net.NetSSH(loggername)
		self.logger = logging.getLogger(loggername)
		self.data = np.zeros(0)
		self.Alldata = np.zeros(0)
		self.Alldata2 = np.zeros(0)
		self.dv = np.zeros(0)
		self.run_index = 0
		self.run_flag = False
		self.Vdcout = 0
		self.Vscanout = 0

	# start the function define for all QSS004
	def sshConnect(self, ip, port, usr, psswd):
		sshresult = self.ssh.connectSSH(ip, port, usr, psswd)
		ftpresult = self.ssh.connectFTP()
		return (sshresult and ftpresult)

	def SlowIncrease(self, vout, vdc):
		# print("SlowIncrease")
		# print(vout)
		# print(vdc)
		while (abs(vout - self.Vscanout) > INCREASE_STEP):
			if ( (vout - self.Vscanout) > 0):
				self.Vscanout = self.Vscanout + INCREASE_STEP
			else:
				self.Vscanout = self.Vscanout - INCREASE_STEP

			if ( (vdc - self.Vdcout) > INCREASE_STEP):
				self.Vdcout = self.Vdcout + INCREASE_STEP
			elif ( (self.Vdcout - vdc) > INCREASE_STEP):
				self.Vdcout = self.Vdcout - INCREASE_STEP
			else:
				self.Vdcout = vdc

			# print("--------")
			# print(self.Vscanout)
			# print(self.Vdcout)

			vout_str = str(self.Vscanout * DAC_Constant_S5)
			cmd = LIB_PATH + DAC_SCAN + vout_str
			self.ssh.sendCmd(cmd) # Set DAC 1 vaulue

			vdc_str = str(self.Vdcout * DAC_Constant_S5)
			cmd = LIB_PATH + DAC_FIXED + vdc_str
			self.ssh.sendCmd(cmd) # Set DAC 2 vaulue

			time.sleep(SLOWINCREASE_TIME)

		self.Vscanout = vout
		vout_str = str(self.Vscanout * DAC_Constant_S5)
		cmd = LIB_PATH + DAC_SCAN + vout_str
		self.ssh.sendCmd(cmd) # Set DAC 1 vaulue

	def VoltageOut(self, scanFlag, scanParam):
		self.OutputInit(scanParam)
		vthstatus = 0
		while (self.run_index < scanParam.max_run_loops) and (self.run_flag):
			status = 0
			self.data = np.zeros(0)
			#self.Alldata = np.zeros(0)
			#self.Alldata2 = np.zeros(0)
			i = scanParam.scanBkWd * (-1)
			vdc = float(scanParam.dc_fixed)
			vout = float(scanParam.start) 
			# self.SlowIncrease(vout, vdc)
			while (i < scanParam.loops) and (self.run_flag):	
				vout = float(scanParam.start) + scanParam.step * float(i) / 1000.0
				dv = vout - vdc
				# status = self.checkIntVth(vout, status, scanParam)
				vout_str = str(vout * DAC_Constant_S5)
				cmd = LIB_PATH + DAC_SCAN + vout_str
				self.ssh.sendCmd(cmd) # Set DAC 1 vaulue
				# remove request by adam 2019.11.7
				# cmd = MONITOR_PATH + SCAN_REG_ADD + '1'
				# self.ssh.sendCmd(cmd) # Reset Reg to wait
				# self.waitRegReady()

				# remove request by adam 2019.11.7
				#adcValue = self.readADC(scanParam.avg_time, scanParam.adc_pority)
				stdout = self.ssh.sendQuerry(self.adc_cmd, False, 0)
				temp = stdout.readline()
				# print(temp)
				adcValue = float(temp) * scanParam.adc_pority * 1000.0 + scanParam.offset
				self.update_text.emit(vout, adcValue)

				if (i >= 0):
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
					self.update_array.emit(self.data, self.Alldata2, self.dv)
				i += 1
			self.update_index.emit(self.run_index+1, self.data)
			self.run_index += 1
		self.finished.emit()

	# def checkIntVth(self, vout, status, scanParam):
	# 	if ((status == 0) and (vout >= scanParam.integrator_th1)):
	# 		self.setIntgrator(scanParam.integrator_time2)
	# 		return status+1
	# 	if ((status == 1) and (vout >= scanParam.integrator_th2)):
	# 		self.setIntgrator(scanParam.integrator_time3)
	# 		return status+1
	# 	if ((status == 2) and (vout >= scanParam.integrator_th3)):
	# 		self.setIntgrator(scanParam.integrator_time4)
	# 		return status+1
	# 	return status

	# remove request by adam 2019.11.7
	# def readADC(self, avg_times, pority):
	# 	subtotal = 0
	# 	for i in range(0, avg_times):
	# 		stdout = self.ssh.sendQuerry(self.adc_cmd, False, 0)
	# 		result = float(stdout.readline()) * pority
	# 		subtotal = subtotal + result
	# 	return subtotal/float(avg_times) 

	# remove request by adam 2019.11.7
	# def waitRegReady(self):
	# 	reg_EOI = 0
	# 	while (reg_EOI == 0):
	# 		cmd = MONITOR_PATH + REG_EOI_CMD
	# 		stdout = self.ssh.sendQuerry(cmd, False, 0.1) # Send REG Querry
	# 		result = stdout.readline()
	# 		reg_EOI = int(result[9])

	def OutputInit(self, scanParam):
		# int_time = scanParam.integrator_time1
		int_time = scanParam.int_time
		mv_avg_str = str(scanParam.mv_avg_num) + " "
		avg_time_str = str(scanParam.avg_time)
		self.runFlag = True
		self.adc_cmd = LIB_PATH + ADC_READ + scanParam.channel_str + mv_avg_str + ADC_GAIN + avg_time_str
		#print(self.adc_cmd)
		self.initIntgrator(int_time)

	def initIntgrator(self, int_time):
		cmd = MONITOR_PATH + INT_REST_ADD + "125000"
		self.ssh.sendCmd(cmd, False, 0)

		cmd = MONITOR_PATH + INT_HOLD_ADD + "125000"
		self.ssh.sendCmd(cmd, False, 0)
		
		self.setIntgrator(int_time)
		self.ssh.sendCmd(cmd, False, 0)
	
	def setIntgrator(self,int_time):
		cmd = MONITOR_PATH+INT_INT_ADD+str(int(int_time*CYCLE_CONST))
		self.ssh.sendCmd(cmd, False, 0)
	
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

	#def getRawFilePath(self):
	#	raw_path = QFileDialog.getExistingDirectory(self,"Save Raw Data", "./")
	#	if raw_path !="":
	#		return raw_path




