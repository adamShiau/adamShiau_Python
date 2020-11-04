import os
from ctypes import *

filepath = os.path.dirname(os.path.abspath(__file__))
dllname = "ftd2xx64.dll"

dll = cdll.LoadLibrary(os.path.join(filepath, dllname))

print(os.path.join(filepath, dllname))


class device_list(Structure):
	_fields_ =[
		('Flags', c_ulong),
		('Type', c_ulong),
		('ID', c_ulong),
		('LocId', c_ulong),
		('SerialNumber', c_char*16),
		('Description', c_char*64),
		('ftHandle', c_void_p)
	]

'''
define global variable
'''
number_of_device = c_ulong()
devlist = device_list()
handle = c_void_p()
FT_OK = 0




status = dll.FT_CreateDeviceInfoList(byref(number_of_device))
print("connected dev # : " , number_of_device.value)
if (status != FT_OK):
    print("FT_CreateDeviceInfoList fail")
    
status = dll.FT_GetDeviceInfoList(byref(devlist), byref(number_of_device))
print(devlist.Flags)
print(devlist.Type)
print(devlist.LocId)
print(devlist.Description)

# status = dll.FT_OpenEx( 20 , 4, byref(handle))
status = dll.FT_OpenEx( b'FT232H' , 2, byref(handle)) #FT_OPEN_BY_DESCRIPTION