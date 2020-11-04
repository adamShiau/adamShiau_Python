import serial
import serial.tools.list_ports
import time

FuncQuerryReg = [0x03]
FuncSingleReg = [0x06]
FuncMultiReg = [0x10]
AbsPostionReg =[0xDE]
FixPositionReg = [0x18, 0x02]
FixPositionCount = [0x00, 0x04]
FixPositionByte =[0x08]
TrigReg=[0x00, 0x7D]
TrigStart =[0x00, 0x08]
TrigStop = [0x00, 0x00]
HomeStart =[0x00, 0x10]
QurPosReg = [0x00, 0xCC]
QurPosCount = [0x00, 0x02]


def auotConnect(baud, timeout):
	portlist = serial.tools.list_ports.comports()
	for a in portlist:
		if "067B:2303" in a[2]:
			portname = a[0]
			port = serial.Serial(portname)
			port.baudrate = baud
			port.timeout = timeout
			port.parity = "E"
			return port
	if portname == "":
		return 0

def CRC_16(data, divider):
	reg = 0xFFFF
	length = len(data)
	for i in range(0, length):
		reg = reg ^ data[i]
		for j in range(0, 8):
			if reg & 0x01 ==1:
				reg = (reg >>1) ^ divider
			else:
				reg = reg >> 1

	reg_H = reg >> 8
	reg_L = reg & 0x00FF
	data.append(reg_L)
	data.append(reg_H)
	return data

def writeCmd(port, cmd):
	dataout = CRC_16(cmd, 0xA001)
	
	byte =port.write(dataout)

	#port.flush()

def int32toList(int32):
	if int32 >0: 
		outlist = [int32 >> 24]
	else:
		a = int32 >> 24
		outlist = [a + 256]

	outlist.append((int32 >> 16) & 0xFF)
	outlist.append((int32>>8) & 0xFF)
	outlist.append(int32&0xFF)

	return outlist

def fixPostionRun(port, address):
	cmd = [address]
	cmd.extend(FuncSingleReg)
	cmd.extend(TrigReg)
	cmd.extend(TrigStart)
	writeCmd(port, cmd)
	#datain = port.read(8)
	datain = readBinary(port, 8)

	if datain[1] == FuncSingleReg[0]:
		return 1
	else:
		return 0

def setPosSpeed(port, address, position, speed, uplimit, lowlimit):
	curpos= querryPos(port,1)
	print("curpos="+str(curpos))
	temp = curpos+position
	print (temp)
	if temp > uplimit or temp < lowlimit:
		return -1
	cmd = [address]
	cmd.extend(FuncMultiReg)
	cmd.extend(FixPositionReg)
	cmd.extend(FixPositionCount)
	cmd.extend(FixPositionByte)
	cmd.extend(int32toList(position))
	cmd.extend(int32toList(speed))
	print(cmd)
	writeCmd(port, cmd)

	datain = readBinary(port, 8)
	if datain[1]==FuncMultiReg[0]:
		return 1
	else:
		return 0

def setHome(port, address):
	cmd =[address]
	cmd.extend(FuncSingleReg)
	cmd.extend(TrigReg)
	cmd.extend(HomeStart)
	writeCmd(port,cmd)
	datain = readBinary(port,8)
	if datain[1] == FuncSingleReg[0]:
		return 1
	else:
		return 0

def allStop(port, address):
	cmd = [address]
	cmd.extend(FuncSingleReg)
	cmd.extend(TrigReg)
	cmd.extend(TrigStop)
	writeCmd(port, cmd)

	datain = readBinary(port,8)
	if datain[1]== FuncSingleReg[0]:
		return 1
	else:
		return 0

def querryPos(port, address):
	cmd = [address]
	cmd.extend(FuncQuerryReg)
	cmd.extend(QurPosReg)
	cmd.extend(QurPosCount)
	writeCmd(port, cmd)
	datain = readBinary(port,9)

	if datain[1] == FuncQuerryReg[0]:
		

		if datain[3]>127:
			temp =int(datain[3]-256)
			pos = (temp <<24) + (datain[4] <<16) + (datain[5]<< 8) + datain[6]
			
		else:
			pos = (datain[3]<<24) + (datain[4]<<16) + (datain[5]<< 8) + datain[6]
			
			
		return pos
	else:
		return -1

def readBinary(port, count):
	datain =[]
	for i in range (0, count):
		temp = ord(port.read())
		datain.append(temp)

	return datain

def ListToInt32(inputlist):
	if inputlist[0] > 127:
		temp = int(inputlist[0]-256)
	else:
		temp = inputlist[0]
	number = (temp << 24) + inputlist[1]


if __name__ == '__main__':

	
	port =auotConnect(115200, 0.2)
	address =1
	setpos = 500
	######## Let Moter back to Home position #############
	input("press anykey to start Home postion")
	result = setHome(port, address)
	if result == 1:
		input("Motor is moving home, press anykey when it finished")
	else:
		return 0
		#### after setHome must run allStop##########
	result = allStop(port, address)
	if result == 1:
		print("Home setting finished")
	else:
		print("Home setting failed")
		return 0
	##########Set postion and Speed ##################
	print("set postion and speed")
	result =setPosSpeed(port, address, setpos,1000, 8000, 0)
	print ("move "+str(setpos)+"steps")
	if result == 1:
		print (" set sucess!")
		######### after fixPostionRun Motor will start moving#########
		result2=fixPostionRun(port,address)
		if result2 == 1:
			print (" Run sucess!")
		else:
			print (" Run Failed")
		######## Must use allStop Command even the motor is stopped #####
		result3 =allStop(port,address)
		if result3 == 1:
			print (" stop sucess!")
		else:
			print (" stop Failed")
		time.sleep(5)
		######### Querry the postion if you want ############
		pos= querryPos(port,1)
		if pos == -1:
			print("querry Failed")
		else:
			print("postion = "+str(pos)+"steps")
	
	##### If the postion is out of range set setPosSpeed will return -1
	##### If motor response is not correct, setPosSpeed will return 0
	elif result ==-1:
		print("range error")
	else:
		print (" set Failed")
	
	
	
	
	
	
	#fixPostionRun(port, 1, 2000,1000)
	

		


