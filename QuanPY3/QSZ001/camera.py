import os
import logging 
import PySpin
#import numpy as np 
#import cv2



class FLIRcamera():
	def __init__(self, loggername):
		self.connect_status = False
		self.logger = logging.getLogger(loggername)

	def camInit(self):
		self.system = PySpin.System.GetInstance()
		camlist = self.system.GetCameras()
		num =camlist.GetSize()
		if num != 1:
			camlist.Clear()
			self.system.ReleaseInstance()
			self.logger.error("Camera Connect number "+str(num))
			self.connect_status = False
			return 0
		self.cam = camlist[0]
		self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
		try:
			self.cam.Init()
			self.nodemap = self.cam.GetNodeMap()
			self.connect_status = True
		except PySpin.SpinnakerException as ex:
			self.logger.error("Init Error at Init %s" %ex)
		return 1

	def setExplosure(self, expTime):
		if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
			self.logger("Can't access explosure time setting")
			return False

		self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

		if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
			self.logger("Can't access explosure time setting")
			return False

		time_to_set = min(self.cam.ExposureTime.GetMax(), expTime)
		try:
			self.cam.ExposureTime.SetValue(time_to_set)
			return True

		except PySpin.SpinnakerException as ex:
			self.logger.error(" ExposureTime set error %s" %ex)

	def setExplosureAuto(self):
		if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
			self.logger("Can't access explosure time setting")
			return False
		self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
		return True

	def setGain(self, gain):
		if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
			self.logger("Can't access Gain setting")
			return False
		
		self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)

		if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
			self.logger("Can't access Gain  setting")
			return False
		gain_to_set = min(self.cam.Gain.GetMax(), gain)
		print(self.cam.Gain.GetMax())
		try:
			self.cam.Gain.SetValue(gain)
			return True

		except PySpin.SpinnakerException as ex:
			self.logger.error(" Gain set error %s" %ex)

	def setGainAuto(self):

		if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
			self.logger("Can't access Gain setting")
			return False	
		self.cam.GainAuto.SetValue(PySpin.GainAuto_Continuous)
		return True
	
	def startAcquire(self):
		if self.cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
			self.logger("can't set acquisition mode")
			return False
		self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
		self.cam.BeginAcquisition()

	def getImage(self, transpose=False):
		img =self.cam.GetNextImage()
		imgout = img.GetNDArray()
		if transpose:
			imgout = imgout.transpose()
		#img2 = np.array(imgout)
		img.Release()
		return imgout

if __name__ == '__main__':
	myCam = FLIRcamera("test")
	myCam.camInit()
	result =myCam.setExplosureAuto()
	#result = myCam.setExplosure(1000)
	result = myCam.setGainAuto()
	myCam.startAcquire()	
	img = myCam.getImage()
	print(img.shape)
	#pg.image(img)
	#cv2.namedWindow('My Image', cv2.WINDOW_NORMAL)
	#cv2.imshow('My Image',img)
	#cv2.waitKey(0)

	#print(result)


