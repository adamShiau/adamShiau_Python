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
import datetime

V_START_CMD = "initial Voatage(V): "
V_STEP_CMD = "scan step(V): "
PTS_CMD = "scan points: "
DT_CMD = "integrate time(us): "
DATA_RATE_CMD = "update rate(Hz): "

PRSETFILE = "set/setting.txt"
SETTING_FILEPATH = "set"

CV_START_V_INDEX = 0
CV_DV_INDEX = 1
CV_END_V_INDEX = 2
CV_DT_INDEX = 3
CV_RATE_INDEX = 4
CV_QUIET_INDEX = 5

IT_VSET_INDEX = 6
IT_DT_INDEX = 7
IT_RATE_INDEX = 8
IT_QUIET_INDEX = 9

HEADER_INDEX = 10
Max_Para_Index = 11


class qss010Action():
	def __init__(self, loggername):	
		self.loggername = loggername
		self.COM = usb.FT232(loggername)
		self.logger = logging.getLogger(loggername)
		self.paramInit()
		self.loadPreset()

	def usbConnect(self):
		status = self.COM.connect(baudrate = 115200, timeout = 1)
		return status

	def paramInit(self):
		self.startV = 0
		self.dv = 10
		self.endV = 3000
		self.CVdt = 10
		self.CVrate = 10
		self.CVquiet = 0

		self.Vset = 2000
		self.ITdt = 10
		self.ITrate = 10
		self.ITquiet = 0

		self.header = ""
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

				self.startV = int(self.paralist[CV_START_V_INDEX])
				self.dv = int(self.paralist[CV_DV_INDEX])
				self.endV = int(self.paralist[CV_END_V_INDEX])
				self.CVdt = int(self.paralist[CV_DT_INDEX])
				self.CVrate = int(self.paralist[CV_RATE_INDEX])
				self.CVquiet = int(self.paralist[CV_QUIET_INDEX])

				self.Vset = int(self.paralist[IT_VSET_INDEX])
				self.ITdt = int(self.paralist[IT_DT_INDEX])
				self.ITrate = int(self.paralist[IT_RATE_INDEX])
				self.ITquiet = int(self.paralist[IT_QUIET_INDEX])

				self.header = self.paralist[HEADER_INDEX]

	def writePreset(self):
		self.paralist[CV_START_V_INDEX] = self.startV
		self.paralist[CV_DV_INDEX] = self.dv
		self.paralist[CV_END_V_INDEX] = self.endV
		self.paralist[CV_DT_INDEX] = self.CVdt
		self.paralist[CV_RATE_INDEX] = self.CVrate
		self.paralist[CV_QUIET_INDEX] = self.CVquiet

		self.paralist[IT_VSET_INDEX] = self.Vset
		self.paralist[IT_DT_INDEX] = self.ITdt
		self.paralist[IT_RATE_INDEX] = self.ITrate
		self.paralist[IT_QUIET_INDEX] = self.ITquiet

		self.paralist[HEADER_INDEX] = self.header
		fil2a.array1DtoTextFile(PRSETFILE, self.paralist, self.loggername)


class CVaction(QObject):
	update_CV = pyqtSignal(object, object, object)
	stop_CV = pyqtSignal(bool)
	finished = pyqtSignal()
	def __init__(self, port, paralist, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.COM = port
		self.paralist = paralist
		self.CVrun = False

	# def setParam(self, startV, dv, endV, dt, rate):
	# 	self.startV = startV/1000
	# 	self.dv = dv/1000
	# 	self.endV = endV/1000
	# 	self.dt = dt
	# 	self.rate = rate
	# 	self.pts = int((endV - startV) / dv)

	def setParam(self):
		startV = self.paralist[CV_START_V_INDEX]
		self.startV = float((startV+2000)/1000)
		dv = self.paralist[CV_DV_INDEX]
		self.dv = float(dv/1000)
		endV = self.paralist[CV_END_V_INDEX]
		self.endV = float((endV+2000)/1000)
		self.dt = self.paralist[CV_DT_INDEX]
		self.rate = self.paralist[CV_RATE_INDEX]
		self.pts = int((endV - startV) / dv)

	def CV_send_usb_cmd(self, cmd):
		# print(cmd)
		self.COM.writeLine(cmd)
		temp = self.COM.readLine()
		# print(temp)
		if (temp == "ERROR"):
			send_cmd_flag = False
			self.stop_CV.emit(False)
			self.finished.emit()
		else:
			send_cmd_flag = True
		return send_cmd_flag

	def CV_send_all_cmd(self):
		self.COM.port.flush()
		self.COM.port.flushInput()
		send_cmd_flag = False

		while (send_cmd_flag != True):
			# cmd = V_START_CMD + str(self.startV)
			send_cmd_flag = self.CV_send_usb_cmd(str(self.startV))
			if (send_cmd_flag == False):
				break
			# cmd = V_STEP_CMD + str(self.dv)
			send_cmd_flag = self.CV_send_usb_cmd(str(self.dv))
			if (send_cmd_flag == False):
				break
			# cmd = PTS_CMD + str(self.pts)
			send_cmd_flag = self.CV_send_usb_cmd(str(self.pts))
			if (send_cmd_flag == False):
				break
			# cmd = DT_CMD + str(self.dt)
			send_cmd_flag = self.CV_send_usb_cmd(str(self.dt))
			if (send_cmd_flag == False):
				break
			# cmd = DATA_RATE_CMD + str(self.rate)
			send_cmd_flag = self.CV_send_usb_cmd(str(self.rate))
			if (send_cmd_flag == False):
				break

	def CVstart(self):
		self.CV_send_all_cmd()
		#2020-03-17 , update Vout
		Vout = self.startV - self.dv
		Vout_flag = 1
		Vout_loop = 0
		# print(self.startV, self.dv, self.endV, self.pts)

		pts_ploop = int(0.5 * self.rate)
		# print("pts_ploop = " + str(pts_ploop))
		diff_time = 1/float(self.rate)
		# print("diff_time = " + str(diff_time))
		# print("CV--------")
		curr_time = 0

		while (self.CVrun):
			time_data = np.empty(0)
			Vout_data = np.empty(0)
			Iout_data = np.empty(0)
			temp = np.empty(4)
			for i in range(0, pts_ploop):
				# line = self.COM.readLine()
				# if (line == ""):
				# 	print("readline is empty")
				# else:
				# 	temp = line.split(',')
				# 	Vout = int(temp[0])
				# 	Iout = int(temp[1])
				if (self.CVrun):
					for i in range(0, 4):
						if (curr_time == 0) and (i == 0):
							temp[i] = int(self.COM.readBinaryMust())
						else:							
							temp[i] = int(self.COM.readBinary())

					#2020-03-17 , update Vout
					#Vout = (temp[0] * 256 + temp[1])*5/65535
					Vout = Vout + self.dv * Vout_flag
					Vout_loop = Vout_loop + 1
					if (Vout_loop > self.pts):
						# print("=====")
						Vout_flag = -1 * Vout_flag
						Vout_loop = 1
					# print(Vout)
					Vout_data = np.append(Vout_data, Vout)

					Iout = temp[2] * 256 + temp[3]
					# print(Iout)
					Iout_data = np.append(Iout_data, Iout)

					curr_time = curr_time + diff_time
					time_data = np.append(time_data, curr_time)
			self.update_CV.emit(time_data, Vout_data, Iout_data)
		self.finished.emit()
		self.COM.port.flush()
		self.COM.port.flushInput()


class ITaction(QObject):
	update_IT = pyqtSignal(object, object)
	stop_IT = pyqtSignal(bool)
	finished = pyqtSignal()
	def __init__(self, port, paralist, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.COM = port
		self.paralist = paralist
		self.ITrun = False

	# def setParam(self, Vset, dt, rate):
	# 	self.Vset = Vset
	# 	self.dt = dt
	# 	self.rate = rate

	def setParam(self):
		self.startV = (self.paralist[IT_VSET_INDEX]+2000)/1000
		self.dv = 0
		self.pts = 100
		self.dt = self.paralist[IT_DT_INDEX]
		self.rate = self.paralist[IT_RATE_INDEX]

	def IT_send_usb_cmd(self, cmd):
		# print(cmd)
		self.COM.writeLine(cmd)
		temp = self.COM.readLine()
		# print(temp)
		if (temp == "ERROR"):
			send_cmd_flag = False
			self.stop_IT.emit(False)
			self.finished.emit()
		else:
			send_cmd_flag = True
		return send_cmd_flag

	def IT_send_all_cmd(self):
		self.COM.port.flush()
		self.COM.port.flushInput()
		send_cmd_flag = False

		while (send_cmd_flag != True):
			# cmd = V_START_CMD + str(self.startV)
			send_cmd_flag = self.IT_send_usb_cmd(str(self.startV))
			if (send_cmd_flag == False):
				break
			# cmd = V_STEP_CMD + str(self.dv)
			send_cmd_flag = self.IT_send_usb_cmd(str(self.dv))
			if (send_cmd_flag == False):
				break
			# cmd = PTS_CMD + str(self.pts)
			send_cmd_flag = self.IT_send_usb_cmd(str(self.pts))
			if (send_cmd_flag == False):
				break
			# cmd = DT_CMD + str(self.dt)
			send_cmd_flag = self.IT_send_usb_cmd(str(self.dt))
			if (send_cmd_flag == False):
				break
			# cmd = DATA_RATE_CMD + str(self.rate)
			send_cmd_flag = self.IT_send_usb_cmd(str(self.rate))
			if (send_cmd_flag == False):
				break

	def ITstart(self):
		self.IT_send_all_cmd()
		pts_ploop = int(0.5 * self.rate)
		# print("pts_ploop = " + str(pts_ploop))
		diff_time = 1/float(self.rate)
		# print("diff_time = " + str(diff_time))
		# print("IT--------")
		curr_time = 0

		while (self.ITrun):
			time_data = np.empty(0)
			# Vout_data = np.empty(0)
			Iout_data = np.empty(0)
			temp = np.empty(4)
			for i in range(0, pts_ploop):
				if (self.ITrun):
					for i in range(0, 4):
						if (curr_time == 0) and (i == 0):
							temp[i] = int(self.COM.readBinaryMust())
						else:							
							temp[i] = int(self.COM.readBinary())

					# Vout = temp[0] * 256 + temp[1]
					# print(Vout)
					# Vout_data = np.append(Vout_data, Vout)

					Iout = temp[2] * 256 + temp[3]
					# print(Iout)
					Iout_data = np.append(Iout_data, Iout)

					curr_time = curr_time + diff_time
					time_data = np.append(time_data, curr_time)
			self.update_IT.emit(time_data, Iout_data)
		self.finished.emit()
		self.COM.port.flush()
		self.COM.port.flushInput()

