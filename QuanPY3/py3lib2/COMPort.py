import serial
import serial.tools.list_ports
import platform
import logging
import py3lib.QuLogger
import numpy as np

ft232_name_in = "0403:6001"
arduino_name_in = "2341:0043"
#ft232_name_in_mac = "0403:6001"
#ft232_name_in_win = "VID_0403+PID_6001"
#ft232_name_in_win = "USB VID:PID=2341:0043"	#Arduino Uno
manual_comport = 'COM5'

class UART:
	def __init__(self, loggername=' '):
		self.cp = 0
		self.port = serial.Serial()
		self.find_com = False
		self.logger = logging.getLogger(loggername)
		#self.port = self.comDetect()
		#if (self.find_com == True):
		#	self.port.flush()
	
	def connect(self, baudrate = 115200, timeout = 1):
		self.baudrate = baudrate
		self.timeout = timeout
		self.find_com = self.checkCom() #決定cp (com port)
		self.port = self.comDetect()
		if (self.find_com == True):
			self.port.flush()

		return self.find_com
		
	def connect_comboBox(self, baudrate = 115200, timeout = 1, port_name = ''):
		self.baudrate = baudrate
		self.timeout = timeout
		# self.find_com = self.checkCom() #決定cp (com port)
		print('comboBox cp=', port_name)
		self.cp = port_name
		self.find_com = True
		# print('find_com: ', self.find_com)
		self.port = self.comDetect()
		# self.port.flush()
		
		return 1
		
	def comDetect(self):
		# print('enter1')
		ser = serial.Serial()
		# print('find_com: ', self.find_com)
		if (self.find_com == True):
			print('self.cp: ', self.cp)
			ser = serial.Serial(self.cp)
			print('port: ', ser.port)
			ser.baudrate = self.baudrate
			ser.timeout = self.timeout
			

		return ser

	def portConnect(self, portid, baudrate = 115200, timeout = 1):
		self.baudrate = baudrate;
		self.timeout = timeout
		self.find_com = self.checkPortCom(portid)
		self.port = self.comDetect()
		if (self.find_com == True):
			self.port.flush()

		return self.find_com

	def checkPortCom(self, portid):
		find_com = False
		portlist = serial.tools.list_ports.comports()
		os = platform.system()
		for a in portlist:
			if portid in a[2]:
				self.cp = a[0]

		if self.cp != 0:
			find_com = True
		else:
			self.logger.error("Can't Find the COM Port")

		return find_com

	def selectCom(self):
		self.comPort = np.empty(0)
		portlist = serial.tools.list_ports.comports()
		self.portNum = len(portlist)
		
		for i in range(self.portNum):
			self.comPort = np.append(self.comPort, portlist[i])

	def checkCom(self):
		find_com = False
		portlist = serial.tools.list_ports.comports()
		# os = platform.system()
		# print(os)
		for a in portlist:
			if ft232_name_in in a[2] or arduino_name_in in a[2]:
				self.cp = a[0]
		print( "cp = " + str(self.cp) )
		
		if self.cp != 0:
			find_com = True
		else:
			self.logger.error("Can't Find the COM Port")

		return find_com


	def writeBinary(self, data):
		#print("in")
		data_list = list([data])
		#data_list.append('\n')
		self.port.write(data_list)
		self.logger.debug("write hex data="+str(data_list))

	def writeList(self, datalist):
		self.port.write(datalist) 

	def readBinary(self):
		try:
			temp = self.port.read()
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			if len(temp) > 0:
				data = ord(temp)
				self.logger.debug("read hex data="+str(data))
			else:
				data = temp

			self.logger.debug("read hex data failed")
			return data
			
	def read1Binary(self):
		try:
			data = self.port.read(1)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data
			
	def read4Binary(self):
		try:
			data = self.port.read(4)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data
	def read5Binary(self):
		try:
			data = self.port.read(5)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data
			
	def read3Binary(self):
		try:
			data = self.port.read(3)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data
			
	def read2Binary(self):
		try:
			data = self.port.read(2)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data

	def readBinaryMust(self, timeoutloop = 10):
		run = True
		loop = 1
		while(run):
			try:
				temp = self.port.read()
			except:
				self.logger.error("readBinaryMust failed")
				return "ERROR"
			else:
				if len(temp) > 0:
					data = ord(temp)
					self.logger.debug("read hex data =" +str(data))
					run = False
					return data
				loop = loop+1
				if (loop == timeoutloop):
					run = False
					self.logger.debug("read data timeout in readBinaryMust")

	def writeLine(self, data, addR = False):
		#print("in")
		if (addR == True):
			data_list = data + '\r\n'
		else:
			data_list = data + '\n'
		#print(data_list)
		try:
			
			self.port.write(data_list.encode())
		except:
			self.logger.error("writeLine failed")

	def readLine(self):
		#print("out")
		try:
			data = self.port.readline().decode()
		except:
			self.logger.error("readLine failed")
			return "ERROR"
		else:
			#print(data)
			return data
			
	def readLineF(self):
		self.port.flushInput()
		try:
			data = self.port.readline().decode()
		except:
			self.logger.error("readLine failed")
			return "ERROR"
		else:
			return data

class FT232:
	def __init__(self, loggername):
		self.cp = 0
		self.port = serial.Serial()
		self.find_com = False
		self.logger = logging.getLogger(loggername)
		#self.port = self.comDetect()
		#if (self.find_com == True):
		#	self.port.flush()
	
	def connect(self, baudrate = 115200, timeout = 1):
		self.baudrate = baudrate
		self.timeout = timeout
		self.find_com = self.checkCom() #決定cp (com port)
		self.port = self.comDetect()
		if (self.find_com == True):
			self.port.flush()

		return self.find_com
		
	def connect_comboBox(self, baudrate = 115200, timeout = 1, port_name = ''):
		self.baudrate = baudrate
		self.timeout = timeout
		# self.find_com = self.checkCom() #決定cp (com port)
		print('comboBox cp=', port_name)
		self.cp = port_name
		self.find_com = True
		# print('find_com: ', self.find_com)
		self.port = self.comDetect()
		# self.port.flush()
		
		return 1
		
	def comDetect(self):
		# print('enter1')
		ser = serial.Serial()
		# print('find_com: ', self.find_com)
		if (self.find_com == True):
			print('self.cp: ', self.cp)
			ser = serial.Serial(self.cp)
			print('port: ', ser.port)
			ser.baudrate = self.baudrate
			ser.timeout = self.timeout
			

		return ser

	def portConnect(self, portid, baudrate = 115200, timeout = 1):
		self.baudrate = baudrate;
		self.timeout = timeout
		self.find_com = self.checkPortCom(portid)
		self.port = self.comDetect()
		if (self.find_com == True):
			self.port.flush()

		return self.find_com

	def checkPortCom(self, portid):
		find_com = False
		portlist = serial.tools.list_ports.comports()
		os = platform.system()
		for a in portlist:
			if portid in a[2]:
				self.cp = a[0]

		if self.cp != 0:
			find_com = True
		else:
			self.logger.error("Can't Find the COM Port")

		return find_com

	def selectCom(self):
		self.comPort = np.empty(0)
		portlist = serial.tools.list_ports.comports()
		self.portNum = len(portlist)
		
		for i in range(self.portNum):
			self.comPort = np.append(self.comPort, portlist[i])

	def checkCom(self):
		find_com = False
		portlist = serial.tools.list_ports.comports()
		# os = platform.system()
		# print(os)
		for a in portlist:
			if ft232_name_in in a[2] or arduino_name_in in a[2]:
				self.cp = a[0]
		print( "cp = " + str(self.cp) )
		
		if self.cp != 0:
			find_com = True
		else:
			self.logger.error("Can't Find the COM Port")

		return find_com


	def writeBinary(self, data):
		#print("in")
		data_list = list([data])
		#data_list.append('\n')
		self.port.write(data_list)
		self.logger.debug("write hex data="+str(data_list))

	def writeList(self, datalist):
		self.port.write(datalist) 

	def readBinary(self):
		try:
			temp = self.port.read()
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			if len(temp) > 0:
				data = ord(temp)
				self.logger.debug("read hex data="+str(data))
			else:
				data = temp

			self.logger.debug("read hex data failed")
			return data
			
	def read1Binary(self):
		try:
			data = self.port.read(1)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data
			
	def read4Binary(self):
		try:
			data = self.port.read(4)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data
			
	def read3Binary(self):
		try:
			data = self.port.read(3)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data
			
	def read2Binary(self):
		try:
			data = self.port.read(2)
		except:
			self.logger.error("readBinary failed")
			return "ERROR"
		else:
			return data

	def readBinaryMust(self, timeoutloop = 10):
		run = True
		loop = 1
		while(run):
			try:
				temp = self.port.read()
			except:
				self.logger.error("readBinaryMust failed")
				return "ERROR"
			else:
				if len(temp) > 0:
					data = ord(temp)
					self.logger.debug("read hex data =" +str(data))
					run = False
					return data
				loop = loop+1
				if (loop == timeoutloop):
					run = False
					self.logger.debug("read data timeout in readBinaryMust")

	def writeLine(self, data, addR = False):
		#print("in")
		if (addR == True):
			data_list = data + '\r\n'
		else:
			data_list = data + '\n'
		#print(data_list)
		try:
			
			self.port.write(data_list.encode())
		except:
			self.logger.error("writeLine failed")

	def readLine(self):
		#print("out")
		try:
			data = self.port.readline().decode()
		except:
			self.logger.error("readLine failed")
			return "ERROR"
		else:
			#print(data)
			return data
			
	def readLineF(self):
		self.port.flushInput()
		try:
			data = self.port.readline().decode()
		except:
			self.logger.error("readLine failed")
			return "ERROR"
		else:
			return data
	
