import os
import logging 
import PySpin
import numpy as np 
import cv2
from ctypes import *
import matplotlib.pyplot as plt 
import time

ANDOR_NOERROR = 20002

# reference: https://github.com/hamidohadi/pyandor/blob/master/Camera/andor.py
class AndorEMCCD():
	def __init__(self, loggername):
		self.logger = logging.getLogger(loggername)
	
	def camInit(self):
		try:
			self.dll = cdll.LoadLibrary("C:/Program Files/Andor SDK/atmcd64d.dll")
		except:
			self.logger.error("Load dll failed")
			return -3
		cpath = c_char()
		error= self.dll.Initialize(byref(cpath))
		if error != ANDOR_NOERROR:
			self.logger.error("Init Failed")
			return -2
		width = c_int()
		height = c_int()
		self.dll.GetDetector(byref(width), byref(height))
		self.img_width = width.value
		self.img_height = height.value
		return 1

	def errorCheck(self,error, massage):
		if error != ANDOR_NOERROR:
			self.logger.error(massage)
			return -1
		return 1

	def setReadMode(self, mode):
		#0: Full vertical binnin
		#1: multi track
		#2: random track
		#3: single track
		#4: image
		error = self.dll.SetReadMode(mode)
		self.ReadMode = mode
		return self.errorCheck(error,"set read mode error")

	def setAcquistionMode(self, mode):
	#1: Single scan
	#3: Kinetic scan
		error = self.dll.SetAcquisitionMode(mode)
		self.acquisitionMode = mode
		return self.errorCheck(error, "set Acq error")
	
	def setImage(self,hbin, vbin, hstart, hend, vstart, vend):
		self.hbin = hbin
		self.vbin = vbin
		self.hstart = hstart
		self.hend = hend
		self.vstart = vstart
		self.vend = vend
		error = self.dll.SetImage(hbin,vbin,hstart,hend,vstart,vend)
		return self.errorCheck(error,"setImage error")

	def setShutter(self,typ,mode,closingtime,openingtime):
		#type 0: TTL low to open to shutter 1: TTL high to open the shutter
		#mode 0: auto 1: permant open 2: permant close
		error = self.dll.SetShutter(typ,mode,closingtime,openingtime)
		return self.errorCheck(error,"setShutter error")

	def getNumberPreAmpGains(self):
		noGains = c_int()
		error = self.dll.GetNumberPreAmpGains(byref(noGains))
		self.noGains = noGains.value
		return self.errorCheck(erro, "get Gain number error")

	def getPreAmpGains(self):
		self.preAmpGain=[]
		gain = c_float()
		for i in range(0, self.noGains):
			self.dll.GetPreAmpGain(i,byref(gain))
			self.preAmpGain.append(gain.value)

	def setPreAmpGain(self, index):
		error = self.dll.SetPreAmpGain(index)
		return self.errorCheck(error, "set preAmpGain error")

	def getEMGainRange(self):
		low = c_int()
		high = c_int()
		error = self.dll.GetEMGainRange(byref(low), byref(high))
		self.gain_low = low.value
		self.gain_high = high.value
		return errorCheck(error, "get EMgainRagne Error")

	def setEMGainMode(self,mode):
		# 0 : DAC in range 0-255 (default)
		# 1 : DAC in range 0-4095
		# 2 : Linear Mode
		# 3 : Real EM gain
		error = self.dll.SetEMGainMode (mode)
		return self.errorCheck(error, "setEMGainMode error")

	def setEMCCDGain(self, gain):
		error = self.dll.SetEMCCDGain(gain)
		return self.errorCheck(error, "SetEMCCDGain error")

	def setCoolerMode(self, mode):
		# 1: Temperature controlled
		# 0: Ambient temperature
		error = self.dll.SetCoolerMode(mode)
		return self.errorCheck(error, "set cooler mode error")

	def setTemperature(self,temperature):
		error = self.dll.SetTemperature(temperature)
		self.tset = temperature
		return self.errorCheck(error, " set Temperature error")
	
	def CoolerOn(self):
		error = self.dll.CoolerON()
		self.cooler = 1
		return self.errorCheck(error, " set Cooler ON error")

	def CoolerOff(self):
		error = self.dll.CoolerOFF()
		self.cooler = 0
		return self.errorCheck(error, " set Cooler OFF error")

	def getTemperature(self):
		temperature = c_int()
		error = self.dll.GetTemperature(byref(temperature))
		return temperature.value

	def shutDown(self):
		self.CoolerOff()
		t =self.getTemperature()
		while t < -20:
			time.sleep(0.5)
			t = self.getTemperature()
		error =self.dll.ShutDown()
		
	
	def setTriggerMode(self, mode):
		# 0: internal
		# 1: External
		# 10:Software Trigger
		error = self.dll.SetTriggerMode(mode)
		return self.errorCheck(error, "set Trigger mode error")
	
	def setExplosureTime(self, time):
		error = self.dll.SetExposureTime(c_float(time))
		self.exptime = time
		return self.errorCheck(error, "set Exp Time error")
	
	def startAcquisition(self):
		error = self.dll.StartAcquisition()
		self.dll.WaitForAcquisition()
		return self.errorCheck(error, "set Acquistion error")

	def getImgData(self):
		hpixel = int(self.img_width/self.hbin)
		vpixel = int(self.img_width/self.vbin)
		self.img = np.zeros([hpixel, vpixel])
		if self.ReadMode == 4 and self.acquisitionMode==1:
			dim = hpixel*vpixel
		else:
			self.logger.error("acq and read mode check error")
		cimgArray = c_int*dim
		cimage = cimgArray()
		error = self.dll.GetAcquiredData(pointer(cimage), dim)

		for i in range(len(cimage)):
			(hindex, vindex) = divmod(i, self.img_width)
			self.img[hindex][vindex] = cimage[i]

		#self.img2 = np.array(self.img)
		#self.img2.reshape(self.img_width, self.img_height)
		return self.errorCheck(error, "read image error")


if __name__ == '__main__':
	myCam = AndorEMCCD("test")
	print(myCam.camInit())
	print(myCam.setReadMode(4))
	print(myCam.setAcquistionMode(1))
	print(myCam.setTriggerMode(0))
	print(myCam.setExplosureTime(0.1))
	print(myCam.setShutter(1,1,0,0))
	myCam.setTemperature(-60)
	time.sleep(1)
	t =myCam.getTemperature()
	print("temp="+str(t))
	print(myCam.setImage(1,1,1,myCam.img_width,1,myCam.img_height))
	print("width")
	print(myCam.img_width)
	print("height")
	print(myCam.img_height)
	print(myCam.startAcquisition())
	print(myCam.getImgData())
	#print(myCam.img)
	plt.imshow(myCam.img)
	plt.show()
	print(myCam.startAcquisition())
	print(myCam.getImgData())
	#print(myCam.img)
	plt.imshow(myCam.img)
	plt.show()
	myCam.shutDown()
	print("shutDown Done")
	#myCam = FLIRcamera("test")
	#myCam.camInit()
	#result =myCam.setExplosureAuto()
	#result = myCam.setExplosure(1000)
	#result = myCam.setGainAuto()
	#myCam.startAcquire()	
	#img = myCam.getImage()
	#pg.image(img)
	#cv2.namedWindow('My Image', cv2.WINDOW_NORMAL)
	#cv2.imshow('My Image',img)
	#cv2.waitKey(0)

	#print(result)



