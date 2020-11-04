from os import environ
from pyftdi.ftdi import Ftdi
from pyftdi.gpio import GpioAsyncController
from ctypes import *

dll = cdll.LoadLibrary("ftd2xx.dll")
number_of_device = c_ulong()
handle = c_void_p()
bitmode = c_ubyte()
bitmask = c_ubyte(0xFF)
asyncfifomode = c_ubyte(0x01)
Rxbytes = c_ulong()
TxBytes = c_ulong()
eventDwords = c_ulong()

class device_list(Structure):
	_fields_ = [
		('Flags', c_ulong),
		('Type', c_ulong),
		('ID', c_ulong),
		('LocId', c_ulong),
		('SerialNumber', c_char*16),
		('Description', c_char*64),
		('ftHandle', c_ulong)
	]

FT232H_TYPE = 8
READ_TIMEOUT = 500
WRITE_TIMEOUT = 500

class FT232H:
	def __init__(self, loggername):
		self.handle = 0
		self.find_com = False
		self.logger = logging.getLogger(loggername)
	
	def connect(self):
		devlist = device_list()
		status = dll.FT_CreateDeviceInfoList(byref(number_of_device))
		print(str(number_of_device.value) + " FTDI connected.")
		status = dll.FT_GetDeviceInfoList(byref(devlist), byref(number_of_device))
		print ("device type=" + str(devlist.Type))

		if (devlist.Type == FT232H_TYPE):
			status = dll.FT_Open(0,byref(handle))
			self.handle = handle
			self.find_com = True
			status = dll.FT_GetBitMode(handle, byref(bitmode))
			print(bitmode.value)
			status = dll.FT_SetBitMode(handle, bitmask, asyncfifomode) # set to  async fifo mode
			status = dll.FT_GetBitMode(handle, byref(bitmode))
			print(bitmode.value)
			status = dll.FT_SetTimeouts(handle, READ_TIMEOUT, WRITE_TIMEOUT)
			status = dll.FT_ResetDevice(handle)
		else:
			self.find_com = False
			self.handle = 0
			self.logger.error("Can't Find the FT232H Port in Connect")

		return self.find_com

	def read(self, num):
		data = c_char * num
		readed = c_ulong()
		if (self.find_com == True):
			status = dll.FT_GetStatus(handle, byref(Rxbytes), byref(TxBytes), byref(eventDwords))
			if (Rxbytes.value != 0):
				status = dll.FT_Read(self.handle, pointer(data), Rxbytes.value, byref(readed))
			else:
				status = False
				readed = ''
		else:
			status = False
			readed = ''
			self.logger.error("Can't Find the FT232H Port in Read")

		return status, readed

	def write(self, data):
		written = c_ulong()
		if (self.find_com == True):
			status = dll.FT_Write(handle, byref(data), len(data), byref(written))
		else:
			status = False
			self.logger.error("Can't Find the FT232H Port in Read")

		return status

