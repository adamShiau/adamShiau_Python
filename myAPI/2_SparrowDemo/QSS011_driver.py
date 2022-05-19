import time
import numpy as np 
# import scipy as sp
# from scipy import signal
import serial
import serial.tools.list_ports
# import logging
# import datetime
import struct
import platform

setSPI_cmd = "setSPI "
OUTPUT_ADD = "90 "	
OPEN_MODE = "0"
CLOSE_MODE = "1"

GAIN1PWR_ADD = "8A " 
GAIN2PWR_ADD = "8B " 

MOD_HIGH_ADD = "81 " 
MOD_LOW_ADD = "82 "
MOD_FREQ_ADD = "80 " 
MOD_PiVth_ADD = "8E " 
Polarity_ADD = "87 " 

IGNOR_ADD = "85 " 
OFFSET_ADD = "84 " 
StepVth_ADD = "83 " 
AVG_ADD = "86 " 
INTER_LIMIT_ADD = "89 "
RESET_LADDER = "88 "


readSPI_cmd = "readSPI "
readTemp_cmd = "readTemp "
ANGULAR_V = "17 "
OPEN_V = "12 "

Read_cmd = "1"
Stop_cmd = "0"

UPPER_BAND_ADD = "8C "
LOWER_BAND_ADD = "8D " 

MOD_OFF_CMD = "8F 0"

PARA_MODHIGH_INDEX = 0
PARA_MODLOW_INDEX = 1
PARA_MODFREQ_INDEX = 2
PARA_PIVTH_INDEX = 3
PARA_POLARITY_INDEX = 4

PARA_IGNOR_INDEX = 5
PARA_OFFSET_INDEX = 6
PARA_STEPVTH_INDEX = 7
PARA_INPUTAVG_INDEX = 8
PARA_MODEOPEN_INDEX = 9
PARA_INTER_LIMIT = 10

PARA_HOST_INDEX = 11
PARA_MODE_INDEX = 12
PARA_GAIN1_INDEX = 13
PARA_GAIN1PWR_INDEX = 14
PARA_GAIN2PWR_INDEX = 15

PARA_COEFF_INDEX = 16

PARA_MODQ_INDEX = 17
PARA_MODR_INDEX = 18
PARA_MODQ2_INDEX = 19
PARA_MODR2_INDEX = 20
PARA_UPPER_BAND_INDEX = 21
PARA_LOWER_BAND_INDEX = 22
PARA_TEMP_CH = 23

Max_Para_Index = 24
SAMPLEING_RATE = 100

#The folling define should be input from GUI
LOW_PASS_FILTER_FCUT = 1 # min 0.01 max 50 default = 1
FILTER_LEVEL = 5 # min = 1 max = 10 default = 5

WRITE_SLEEP_TIME = 0.01
READ_DATA_NUM = 400
# READ_DATA_LEN = 4
READ_DATA_LEN = 6
READ_DATA_TIME = 0.01
READ_SLEEP_TIME = 0.5

TEST_MODE = False
# ARDUINO_TESTMODE = False

DAC_RATIO = 4000.0/32767.0 # 0.2442 = 2000.0 / 8192
FREQ_RATIO = 62500.0

class checkCom:
	def __init__(self):
		pass
	
	def listAllCom(self):
		portlist = serial.tools.list_ports.comports()
		os = platform.system()
		multiCom = []
		error_code = 0
		for a in portlist:
			multiCom.append(a[0])
		if (len(multiCom) == 0):
			error_code = NO_COMPORT
			
		return multiCom, error_code

class FT232:
	def __init__(self):
		self.cp = 0
		self.port = serial.Serial()
	#use
	def comPortConnect(self, portName, baudrate = 115200, timeout =1):
		try:
			self.port = serial.Serial(portName)
		except:
			return False
		self.port.baudrate = baudrate
		self.port.timeout = timeout
		return True
		


	def reset_InputBuffer(self):
		self.port.reset_input_buffer()

	def getInWaitingLength(self):
		try:
			temp = self.port.inWaiting()
		except:
			return -1
		else:
			return temp
	def readBytes(self, number):
		try:
			temp = self.port.read(number)
		except:
			return "ERROR"
		else:
			return temp
	def writeLine(self, data):
		data_list = data + '\n'
		try:
			self.port.write(data_list.encode('utf-8'))
		except:
			status = False
		else:
			status = True
		return status

class Gyro():
	def __init__(self):	
		self.multiCom = checkCom()
		self.usb = FT232()
		self.paramInit() # set the default value of all parameters

	def checkUsbCom(self):
		comPortList = self.multiCom.listAllCom()
		return comPortList

	# For example: Gryo.usbConnect("COM10") 
	def usbConnect(self, portName):
		status = self.usb.comPortConnect(portName, timeout = 1)
		#print("is open")
		# print(self.usb.port.is_open)
		return status

	def sendComCmd(self, cmd):
		try:
			status = self.usb.writeLine(cmd)
			print(cmd)
		except:
			status = False
		else:
			status = True
			time.sleep(WRITE_SLEEP_TIME)
	
		return status

	def paramInit(self):
		# parameter Init user can set Default setting here
		self.modHigh = 4096 # modulation high voltage dac code
		self.modLow = 0 # modulation low voltage dac code
		self.modFreq = 125 # modulation freq period in 8ns scale
		self.piVth = 8191 # voltage threshold for Pi phase shift
		self.polarity = 1 # signal polarity
		
		self.ignor = 32 # ignor 
		self.offset = 0 # input offset voltage ADC level
		self.stepVth = 0 # the threshould value for step 
		self.inavg = 4 # moving average level in power of 2
		self.mode_open = 6 # open mode moveing average level  in power of 2
		self.fstIntegratorLimit = 0x7FFFFF # first integrator Limit, It is recommand don't change the value
		self.upperBand = 1
		self.lowerBand = -1
		
		self.mode = "close" # mode selection. user can set open mode or close mode here
		# gain setting 
		# gain1 is the gain for lst integration. gain1 = gain1 / 2**gain1pwr
		# gain2 is the gain for 2nd integration. gain2 = 1/2**gain2pwr
		self.gain1 = 1 # 
		self.gain1pwr = 6
		self.gain2pwr = 6


		

	def getTemp(self, ch): # get the target the temperature of target channel
		cmd = readTemp_cmd + str(ch)
		self.sendComCmd(cmd)
		out = self.usb.readBytes(2)

		if (out == b'') or (out == "ERROR"):
			return -1
		else:
			out2 = out[0]<<8 | out[1]
			return out2

	def transTemp(self, temp): # transfer the binary code to temperature in Celsius
		mV = float(temp)*1500.0/1023.0 # real PCB
		Temperature = -7.857923e-6*mV*mV-1.777501e-1*mV+204.6938
		return Temperature

	def setModOff(self): # disable the modulation 
		cmd = setSPI_cmd + MOD_OFF_CMD
		self.sendComCmd(cmd)

	def setOutputMode(self): #set the output mode
		if (self.mode == "close"):
			mode_cmd = CLOSE_MODE
		else:
			mode_cmd = OPEN_MODE
		cmd = setSPI_cmd + OUTPUT_ADD + mode_cmd

		self.sendComCmd(cmd)

	def setModHigh(self): 
		cmd = setSPI_cmd + MOD_HIGH_ADD + str(self.modHigh)
		self.sendComCmd(cmd)
		return self.modHigh*DAC_RATIO

	def setModLow(self):
		cmd = setSPI_cmd + MOD_LOW_ADD + str(self.modLow)
		self.sendComCmd(cmd)
		return self.modLow*DAC_RATIO

	def setModFreq(self):
		cmd = setSPI_cmd + MOD_FREQ_ADD + str(self.modFreq)
		self.sendComCmd(cmd)
		return FREQ_RATIO/float(self.modFreq)

	def setPiVth(self):
		cmd = setSPI_cmd + MOD_PiVth_ADD + str(self.piVth)
		self.sendComCmd(cmd)
		return DAC_RATIO*float(self.piVth)

	def setPolarity(self):
		cmd = setSPI_cmd + Polarity_ADD + str(self.polarity)
		self.sendComCmd(cmd)

	def setIgnor(self):
		cmd = setSPI_cmd + IGNOR_ADD + str(self.ignor)
		self.sendComCmd(cmd)
		return self.ignor

	def setOffset(self):
		cmd = setSPI_cmd + OFFSET_ADD + str(self.offset)
		self.sendComCmd(cmd)
		return float(self.offset)*0.2442

	def setStepVth(self):
		cmd = setSPI_cmd + StepVth_ADD + str(self.stepVth)
		self.sendComCmd(cmd)
		return float(self.stepVth) * 0.2442

	def setAVG(self):
		cmd = setSPI_cmd + AVG_ADD + str(self.inavg)
		self.sendComCmd(cmd)

	def setFstIntegratorLimit(self):
		cmd = setSPI_cmd + INTER_LIMIT_ADD + str(self.fstIntegratorLimit)
		self.sendComCmd(cmd)

	def setResetLadder(self):
		cmd = setSPI_cmd + RESET_LADDER + "1"
		self.sendComCmd(cmd)
		cmd = setSPI_cmd + RESET_LADDER + "0"
		self.sendComCmd(cmd)

	def setGain1(self):
		cmd = setSPI_cmd + GAIN1PWR_ADD + str(self.gain1pwr)
		self.sendComCmd(cmd)
		Gain1 = float(self.gain1)/float(2**self.gain1pwr)
		return Gain1

	def setGain2(self):
		cmd = setSPI_cmd + GAIN2PWR_ADD + str(self.gain2pwr)
		self.sendComCmd(cmd)
		Gain2 = 1/float(2**self.gain2pwr)
		return Gain2

	def setStop(self):
		cmd_close = readSPI_cmd + ANGULAR_V + Stop_cmd
		cmd_open = readSPI_cmd + OPEN_V + Stop_cmd
		if self.mode == "open":
			self.sendComCmd(cmd_open)
		else:
			self.sendComCmd(cmd_close)
	
		self.usb.port.flushInput()
	
	def setUpperBand(self):
		cmd = setSPI_cmd + UPPER_BAND_ADD + str(self.upperBand)
		self.sendComCmd(cmd)

	def setLowerBand(self):
		cmd = setSPI_cmd + LOWER_BAND_ADD + str(self.lowerBand)
		self.sendComCmd(cmd)

	def getVersion(self):
		self.sendComCmd("getVersion")
		version = self.usb.readLine()
		return version

	def startRead(self, ch):
		if self.mode =="open":
			start_cmd = cmd_open = readSPI_cmd + OPEN_V + str(ch)
		else:
			start_cmd = cmd_close = readSPI_cmd + ANGULAR_V + str(ch)
		self.usb.port.flushInput()
		# print(type(start_cmd))
		# print(start_cmd)
		self.sendComCmd(start_cmd)

	def readData(self, time_to_write):
		total_read = self.usb.getInWaitingLength()
		count = 0
		data = np.empty(0, dtype=np.int32)
		tempature = np.empty(0, dtype=np.int32)
		dt = np.empty(0)
		while(total_read ==0 and count <=100):
			time.sleep(0.05)
			count = count+1
			total_read = self.usb.getInWaitingLength()
		if (total_read==0 and count >= 100):
			print("No Data Input")
			return
		else:
			total_read = int(total_read / READ_DATA_LEN)
			usbdata = self.usb.readBytes(total_read * READ_DATA_LEN)
			print(len(usbdata), end=", ")
			print([hex(i) for i in usbdata])
			
			if (usbdata == b'') or (usbdata == "ERROR"):
				print("USB readBytes error")
				return
			else:
				datain = struct.iter_unpack('>lH', usbdata)
				i = 0
				for sub_data in datain:
					data = np.append(data,sub_data[0])
					temp = self.transTemp(sub_data[1])
					tempature = np.append(tempature, temp)
					time_to_write = time_to_write + READ_DATA_TIME
					dt = np.append(dt, time_to_write)
					i = i + 1

			return dt, data, tempature, time_to_write

# code exmpale for this driver
if __name__ == '__main__':
	gyro = Gyro()
	comportlist = gyro.checkUsbCom()
	print(comportlist)
	status = gyro.usbConnect('COM13')
	# wait sometime until the connection is build. if in the GUI, it may not necessary
	time.sleep(2)
	# setting the parameters from GUI.
	# if user didn't set below commands, the driver will set the parameters by default value in paramInit()
	# gyro.mode = "open"
	# gyro.modHigh = 4096
	# gyro.modeLow = 0
	# gyro.modFreq = 125
	# gyro.piVth = 8191
	# gyro.polarity = 1
	# gyro.ignor = 32
	# gyro.offset = 0
	# gyro.inavg = 4
	# gyro.mode_open = 6
	# gyro.gain1 =1
	# gyro.gain1pwr = 6
	# gyro.gain2pwr = 6

	gyro.setOutputMode() #90 1
	gyro.setModOff()	#8F 0
	gyro.setGain1()	#8A 6
	gyro.setGain2() #8B 6
	gyro.setModHigh() #81 4096
	gyro.setModLow() #82 0
	gyro.setModFreq() #80 125
	gyro.setPiVth() #81 8191
	gyro.setPolarity() #87 1
	gyro.setIgnor() #85 32
	gyro.setOffset() #84 0
	gyro.setStepVth() #83 0
	gyro.setAVG() #86 4
	gyro.setFstIntegratorLimit() #89 8388607
	gyro.setUpperBand() #8c 1
	gyro.setLowerBand() #8d -1
	
	# before start reset the ladder first 
	# gyro.setStop()
	gyro.setResetLadder()	
	
	measureTime = 0
	time_to_write = 0
	time_start= time.time()
	
	gyro.startRead(1) # read ch1 temperature
	while (measureTime < 100): # Measure the data for 100s and print it
		time.sleep(0.2)
		dt, data, tempature, time_to_write = gyro.readData(time_to_write)
		# for i in range(len(dt)):
		# 	print("%4.2f, %d, %3.2f" % (dt[i],data[i], tempature[i]))
		# 	pass
		measureTime = time.time() - time_start
	gyro.setStop()





	


	