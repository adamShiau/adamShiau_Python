import ftd2xx as ft
import logging 

class FT232H():
	def __init__(self, loggername):
		self.logger = logging.getLogger(loggername)
		self.device = None

	def connect(self):
		devNumber = ft.createDeviceInfoList()
		self.logger.info(str(devNumber)+"devices connected")
		if devNumber == 0:
			status = 1
		else:
			status = 2
			for i in range(0, devNumber):
				d = ft.getDeviceInfoDetail(i)
				if d['description'] == b'FT232H':
					status = 0
					self.device = ft.openEx(b'FT232H', 2)
			return status

	def writeList(self, datalist):
		for i in range(len(datalist)):
			data = datalist[i]
			if data == 0:
				data = 256
			self.device.write(chr(data))

	def Flush(self):
		self.device.purge()
	
	def ReadBuffer(self):
		size = self.device.getQueueStatus()
		val = self.device.read(size)
		return size, val


if __name__ == '__main__':
	import matplotlib.pyplot as plt 
	import time
	usb = FT232H("test")
	print("connect status =" +str(usb.connect()))
	cmd1 = [53, 0, 0, 0, 0]
	cmd2 = [54, 0, 0, 0, 0]
	cmd3 = [55, 0, 0, 0, 0]
	cmd4 = [56, 0, 0, 0, 0]
	cmdReadA0 = [48, 0, 0, 0, 0]
	cmdStopA0 = [49, 0, 0, 0, 0]
	
	usb.writeList(cmd1)
	print("stage1:")
	time.sleep(1)
	
	usb.writeList(cmd2)
	print("stage2:")
	time.sleep(1)
	
	usb.writeList(cmd3)
	print("stage3:")
	time.sleep(1)
	
	usb.writeList(cmd4)
	print("stage4:")
	time.sleep(1)
	
	data = []
	totalsize =[]
	usb.Flush()
	usb.writeList(cmdReadA0)
	print("stageRead:")
	for j in range(0, 10):
		time.sleep(0.1)
		size, val = usb.ReadBuffer()
		totalsize.append(size)
		data.extend(val)
	usb.writeList(cmdStopA0)
	print(totalsize)
	realdata =[]
	for i in range (0, len(data),2):
		realdata.append((data[i]*256 + data[i+1])*5/65535)

	plt.plot(realdata)
	plt.show()

