import sys
import time
sys.path.append("../")
import logging
import numpy as np 
import py3lib.COMPort as usb
import py3lib.Camera2 as cam 
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
import thorlabs_apt as apt

STAGE_HOME_SPEED = 1
STAGE_SCAN_SPEED = 0.1

class stageAction(QObject):
	finishedConn = pyqtSignal(bool)
	finishedMove = pyqtSignal(float)
	def __init__(self, loggername, testmode, parent = None):	
		super(QObject, self).__init__(parent)
		self.loggername = loggername
		self.logger = logging.getLogger(loggername)
		self.testmode = testmode
		self.motor = None
		self.motorStatus = False
		self.goTo = 0
		self.speed = 0

	def connect(self):
		port = apt.list_available_devices()
		if self.testmode:
			time.sleep(1)
			self.motor = 1
			self.motorStatus = True
			self.finishedConn.emit(True)
		elif (len(port) > 0):
			stage_id = port[0][1]
			self.motor = apt.Motor(stage_id)
			# self.motor.move_home(True)
			self.motorStatus = True
			self.finishedConn.emit(True)
		else:
			self.motor = 0
			self.motorStatus = False
			self.finishedConn.emit(False)

	def homeAndGoto(self):
		# print(self.goTo)
		if self.testmode:
			time.sleep(1)
		elif (self.goTo > 0):
			self.motor.set_velocity_parameters(0, self.speed, self.speed)
			self.motor.move_to(self.goTo, True)
		else:
			self.motor.set_velocity_parameters(0, STAGE_HOME_SPEED, STAGE_HOME_SPEED) # use higher speed to return home
			self.motor.move_home(True)

		self.finishedMove.emit(self.goTo)


class qss012(QObject):
	# finishedConn = pyqtSignal(bool)
	# finishedMove = pyqtSignal(float)
	updateScan = pyqtSignal(float, object, int)
	finishedScan = pyqtSignal()
	def __init__(self, loggername, motor, motorTest, camTest, parent = None):
		super(QObject,self).__init__(parent)
		self.loggername = loggername
		self.logger = logging.getLogger(loggername)
		self.camera = cam.AndorEMCCD(loggername)
		self.camTest = camTest
		self.motorTest = motorTest
		self.motor = motor
		# self.motorStatus = False
		self.scanFrom = 0
		self.scanTo = 0
		self.delta = 0
		self.scanFlag = False
		self.average = 1

	def getCamImg(self):
		if not self.camTest:
			self.camera.startAcquisition()
			self.camera.getImgData()
		else: # only for test
			self.camera.img = np.random.rand(1024, 1024)*255
			self.camera.img = self.camera.img.astype(int)

	def stageScan(self):
		current = self.scanFrom
		while ( current < self.scanTo) and self.scanFlag:
			if self.motorTest:
				time.sleep(1)
			else:
				self.motor.set_velocity_parameters(0, STAGE_SCAN_SPEED, STAGE_SCAN_SPEED)
				self.motor.move_to(current, True)
			temp = np.zeros((1024, 1024))
			# print(self.average)
			for i in range(0, self.average):
				self.getCamImg()
				temp = temp + self.camera.img
			self.camera.img = temp/self.average 

			if not self.camTest:
				tcam = self.camera.getTemperature()
			else:
				tcam = 0
			self.updateScan.emit(current, self.camera.img, tcam)

			current = current + self.delta
			if (current > self.scanTo):
				current = self.scanTo
		# while end
		if self.motorTest:
			time.sleep(1)
		else:
			self.motor.set_velocity_parameters(0, STAGE_SCAN_SPEED, STAGE_SCAN_SPEED)
			self.motor.move_to(current, True)
		self.getCamImg()
		self.updateScan.emit(current, self.camera.img, 0)
		# action finish
		self.finishedScan.emit()    


if __name__ == '__main__':
	pass

