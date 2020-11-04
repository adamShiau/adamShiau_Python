from os import environ
from pyftdi.ftdi import Ftdi
from pyftdi.gpio import GpioAsyncController
from ctypes import *

dll = cdll.LoadLibrary("ftd2xx.dll")
FT_OPEN_BY_SERIAL_NUMBER =1
PVOID = c_void_p
#FT_HANDLE = c_void_p
#FT_STATUS = c_ulong
openFlag=c_ulong(FT_OPEN_BY_SERIAL_NUMBER)
handle = c_void_p()
handle2 = c_void_p()
Rxbytes = c_ulong()
TxBytes = c_ulong()
bitmode = c_ubyte()
bitmask = c_ubyte(0xFF)
asyncfifomode = c_ubyte(0x01)
mpssemode = c_ubyte(0x02)

listDeviceFlag = c_ulong()
ftdevice = c_ulong()

eventDwords = c_ulong()
number_of_device = c_ulong()


class device_list(Structure):
	_fields_ =[
		('Flags', c_ulong),
		('Type', c_ulong),
		('ID', c_ulong),
		('LocId', c_ulong),
		('SerialNumber', c_char*16),
		('Description', c_char*64),
		('ftHandle', c_ulong)
	]
#dev_no1 = c_ulong(1)
devlist = device_list()
status = dll.FT_CreateDeviceInfoList(byref(number_of_device))
print(str(number_of_device.value)+" FTDI connected.")
status = dll.FT_GetDeviceInfoList(byref(devlist), byref(number_of_device))
print ("device type="+str(devlist.Type))
if devlist.Type == 8:
	status = dll.FT_Open(0,byref(handle))
	
	status = dll.FT_GetBitMode(handle, byref(bitmode))
	print(bitmode.value)
	status = dll.FT_SetBitMode(handle, bitmask, asyncfifomode) # set to  async fifo mode
	status = dll.FT_GetBitMode(handle, byref(bitmode))
	print(bitmode.value)
	status = dll.FT_SetTimeouts(handle, 500, 500)
	status = dll.FT_ResetDevice(handle)
	input("Send some data to fifo when ready press any key to continue")
	status = dll.FT_GetStatus(handle, byref(Rxbytes), byref(TxBytes), byref(eventDwords))
	print("recieve bytes:"+str(Rxbytes))

	dataarray= c_char*65536
	data = dataarray()
	readed = c_ulong()
	written = c_ulong()
	if Rxbytes.value !=0 :
		status = dll.FT_Read(handle, pointer(data), Rxbytes.value, byref(readed))
		print(str(readed.value)+" bytes readed.")
		for i in range(0, readed.value):
			#data[i] = data[i]+3
			print(data[i])
	for i in range(0, 12):
		data[i] = i*2+1

	status = dll.FT_Write(handle, byref(data), 12, byref(written))
	print(str(written.value)+" bytes has been send")
else:
	input("FT232H not founed, press any key to quit")









# print(status)



#dev =ftdi.get_device(url)
#print(dev)