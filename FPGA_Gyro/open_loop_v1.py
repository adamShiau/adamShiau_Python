import os 
import sys 
sys.path.append("../") 
import py3lib.COMPort as usb
import time

COM = usb.FT232('test')
COM.selectCom()
if(COM.portNum > 0):
	for i in range(COM.portNum):
		print(COM.comPort[i][0])
cp = 'COM4'
status = COM.connect_comboBox(baudrate = 115200, timeout = 1, port_name=cp)
print("status:" + str(status))
# COM.port.flushInput()
COM.writeLine('0 300')
time.sleep(0.1)
COM.writeLine('3 14680')
time.sleep(0.1)
COM.writeLine('12 1')
time.sleep(0.1)
cnt = 0
flag = 1
while(flag):
	while(not (COM.port.inWaiting()>0)) : 
		pass
	print(COM.port.inWaiting(), end=', ')
	datain = COM.read4Binary()
	shift_data = (datain[0]<<24|datain[1]<<16|datain[2]<<8|datain[3])
	if((datain[0]>>7) == 1):
		shift_data = (shift_data - (1<<32))
	print(shift_data)
	cnt = cnt + 1
	if cnt == 100 :
		flag = 0
