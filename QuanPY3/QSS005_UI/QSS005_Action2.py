import os
import sys
sys.path.append("../")
import time
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.NetSSH as net 
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging
import datetime
import py3lib.fakeData as fakeData

SETTING_FILEPATH = "set"
SCAN_PRESET_FILE_NAME = "set/scan_setting.txt"
SYS_PRESET_FILE_NAME = "set/sys_setting.txt"
CAL_PRESET_FILE_NAME = "set/cal_setting.txt"
HK_PRESET_FILE_NAME = "set/hk_setting.txt"
ENG_SETTING_FILE = "set/eng_Setting.txt"

ROW_FILEPATH = "./ms1rawdata/"

MS1_FILE = "MS1.txt"
FAKE_DATA = "data.txt"
INIT_DATACOUNT = 10000

UART_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./UART "

ADC_DATA_FILE = "adc_data.bin"
ISO_OUT_FILE = "chirp_out.bin"
MSMS_OUT_FILE = "msms_out.bin"
ADC_CMD = "/opt/redpitaya/bin/monitor 0x40200058"
ADC_TIMEOUT = 1000
DELTAT = 0.00024 #ms = 8*30 = 240 ns
CHIRP_DATA_COUNT = 32768
FREQ_SPACE = 125

ISO_ERROR_MSG1 = "The mass should be between "
ISO_ERROR_MSG2 = "\nPlease modify ISO Mass"

TEST_MODE = False

class qss005Action(QObject):
	ms1_update_array = pyqtSignal(object)
	ms1_single_finished = pyqtSignal()

	ms1_update_total_array = pyqtSignal(object, object)
	ms1_finished = pyqtSignal()
	def __init__(self, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.Qss005header = ""
		self.ssh = net.NetSSH(loggername)
		self.logger = logging.getLogger(loggername)
		self.ms1init()
		self.calibra_init()
		self.loadPreset()
		self.updateCalMass()

# start the function define for all QSS005
	def sshConnect(self, ip, port, usr, psswd):
		sshresult = self.ssh.connectSSH(ip, port, usr, psswd)
		ftpresult = self.ssh.connectFTP()
		if TEST_MODE:
			return True
		else:
			return (sshresult and ftpresult)

	def loadPreset(self):
		if not os.path.isdir(SETTING_FILEPATH):
			os.mkdir(SETTING_FILEPATH)

		if os.path.exists(SCAN_PRESET_FILE_NAME):
			self.scanPreset = fil2a.TexTFileto1DList(SCAN_PRESET_FILE_NAME, self.loggername)
		else:
			self.logger.warning("scan file load failed")
			self.scanPreset = [100, 1, 0, 0, 0, 0, 1, 1, 10, 0.5, 100, 30, 50, 10, 10, 10]
			self.savePreset(1)

		if os.path.exists(SYS_PRESET_FILE_NAME):
			self.sysPreset = fil2a.TexTFileto1DList(SYS_PRESET_FILE_NAME, self.loggername)
		else:
			self.logger.warning("system file load failed")
			self.sysPreset = [1, 0.0, 1, 0, 0.1, 0, 0.1, 30, 0.67, 0.52]
			self.savePreset(2)

		if os.path.exists(CAL_PRESET_FILE_NAME):
			self.calibPreset = fil2a.TexTFileto1DList(CAL_PRESET_FILE_NAME, self.loggername)
		else:
			self.logger.warning("cal file load failed")
		
		if os.path.exists(HK_PRESET_FILE_NAME):
			self.hkPreset = fil2a.TexTFileto1DList(HK_PRESET_FILE_NAME, self.loggername)
		else:
			self.logger.warning("hk file load failed")

		if os.path.exists(ENG_SETTING_FILE):
			self.engSet = fil2a.TexTFileto1DList(ENG_SETTING_FILE, self.loggername)
		else:
			self.logger.warning("failed to laod eng setting file")

	def savePreset(self, type):
		if (type == 4):
			paralist = self.engSet
			filename = ENG_SETTING_FILE
		elif (type == 3):
			paralist = self.calibPreset
			filename = CAL_PRESET_FILE_NAME
		elif (type == 2):
			paralist = self.sysPreset
			filename = SYS_PRESET_FILE_NAME
		elif (type == 1):
			paralist = self.scanPreset
			filename = SCAN_PRESET_FILE_NAME
		else:	#elif (type == 0):
			paralist = self.hkPreset
			filename = HK_PRESET_FILE_NAME

		fil2a.array1DtoTextFile(filename, paralist, self.loggername)

	def setQss005header(self, header):
		self.Qss005header = header

# start the function define for MS1
	def ms1init(self):
		self.ms1singleRunFlag = False
		self.singleData = np.empty(0)
		self.cmd = ""
		self.cmd_delay_time = 0
		self.ms1noisefilter = False
		self.ms1filterLevel = 1
		self.ms1runFlag = False
		self.ms1TotalData = np.zeros(INIT_DATACOUNT)
		#self.ms1saveRaw = False
		self.ms1saveRawPath = ROW_FILEPATH
		self.rawfileindex = 0
		self.ms1datalen = INIT_DATACOUNT
		self.runLoop = 1
		self.polarity = 1
		self.pts = 0
		self.old_ch1_trapping_amp = 0
		self.old_ch2_freq_factor = 0
		self.old_ch2_final_freq = 0
		self.old_isoMassCenter = 0
		self.old_isoMassRange = 0
		self.old_iso_chirp_amp = 0
		self.old_msms_amp = 0
		self.ms1isChecked = False
		self.getFile_delay_time = 0

	def ms1_setCmdAndValue(self, cmd, cmd_delay_time, ms1isChecked, getFile_delay_time):
		self.cmd = cmd
		self.cmd_delay_time = cmd_delay_time
		self.ms1isChecked = ms1isChecked
		self.getFile_delay_time = getFile_delay_time

	def ms1_setNoiseAndLevel(self, enable, level):
		self.ms1noisefilter = enable
		self.ms1filterLevel = level

	def ms1_setRowAndPath(self, row_path = ""):
		#self.ms1saveRaw = save_row
		#if (self.ms1saveRaw):
			#if (row_path != ''):
		self.ms1saveRawPath = row_path

	def resetIndex(self):
		self.rawfileindex = 0
		self.ms1TotalData = np.zeros(INIT_DATACOUNT)
		self.ms1datalen = INIT_DATACOUNT

	# def ms1fakeData(self): # NOT use
	# 	self.singleData = fil2a.TexTFileto1DList(FAKE_DATA, self.loggername)

	def checkAndGetFile(self, filename, len):
		data = np.empty(0)
		ls_cmd = "ls " + filename
		TRIG_PASS_FLAG = False
		i = 0
		while (not TRIG_PASS_FLAG) and (i < ADC_TIMEOUT):
			stdout = self.ssh.sendQuerry(ls_cmd)
			output = stdout.readline()
			if output.find(filename, 0, len) == 0:
				TRIG_PASS_FLAG = True
			i = i + 1
			# print(i)
			if (i == 4):
				self.ssh.sendCmd(self.cmd)
				print("i = " + str(i))
				print("re-send cmd : " + self.cmd)
				i = 0
			else:
				# print("delay = " + str(self.getFile_delay_time) )
				time.sleep(self.getFile_delay_time)

		if not TRIG_PASS_FLAG:
			self.logger.error("ADC file time out")
		else:
			self.ssh.getFtpFile(filename)
		return TRIG_PASS_FLAG

	def setPolarity(self, polarity):
		if polarity:
			self.polarity = -1
		else:
			self.polarity = 1

	def ADCfiletoData(self):
		if (TEST_MODE):
			if (self.ms1isChecked):
				pass
			else:
				self.singleData = fil2a.BinFiletoArray(ISO_OUT_FILE, 4, 'f', self.loggername)*self.polarity
		else:
			self.singleData = fil2a.BinFiletoArray(ADC_DATA_FILE, 4, 'f', self.loggername)*self.polarity

		if len(self.singleData) > 0:
			# self.singleData = np.delete(self.singleData, 0)
			if (self.ms1noisefilter):
				self.singleData = sp.signal.medfilt(self.singleData, self.ms1filterLevel*2+1)
		else:
			self.logger.error("ADC File Empty")

	def sendSingleCmd(self):
		# rm ADC file
		rm_cmd = "rm " + ADC_DATA_FILE
		self.ssh.sendCmd(rm_cmd)
		adc_cmd = ADC_CMD + " 0"
		self.ssh.sendCmd(self.cmd)
		self.ssh.sendCmd(adc_cmd, getpty = True, timedelay = self.cmd_delay_time)

	def getData(self):
		if (TEST_MODE):
			if (0):
				self.ADCfiletoData()
			else:
				# print("action : " + str(self.pts))
				fakeD = fakeData.QSS005MSData(self.pts)
				define = fakeD.genRandDefine(5, 6)
				fakeD.genPeak(define, 4)
				fakeD.genNoise(1)
				self.singleData = fakeD.data*self.polarity
		else:
			self.checkAndGetFile(ADC_DATA_FILE, 13)
			self.ADCfiletoData()
		# rm ADC file
		rm_cmd = "rm " + ADC_DATA_FILE
		self.ssh.sendCmd(rm_cmd)

	def sendStartCmd(self):
		# write MS1.txt "0" to stop
		echo_cmd = "echo \"0\" > " + MS1_FILE
		# print(echo_cmd)
		self.ssh.sendCmd(echo_cmd)

	def sendStopCmd(self):
		# write MS1.txt "1" to stop
		echo_cmd = "echo \"1\" > " + MS1_FILE
		# print(echo_cmd)
		self.ssh.sendCmd(echo_cmd)

	def ms1single(self):
		time.sleep(0.1)
		# self.checkISOinit() # move to main : ms1BtnRun
		if self.ms1singleRunFlag:
			# self.sendStartCmd()
			self.sendStopCmd()
			self.sendSingleCmd()
			# t0 = time.time()
			# m0 = time.localtime(t0).tm_min
			# s0 = time.localtime(t0).tm_sec
			self.getData()
			# t1 = time.time()
			# m1 = time.localtime(t1).tm_min
			# s1 = time.localtime(t1).tm_sec
			# print("getData TIME = " + str(m1-m0) + ":" + str(s1-s0))
			self.ms1_update_array.emit(self.singleData)
		self.sendStopCmd()
		self.ms1_single_finished.emit()
		print("----------")

	def ms1multiRun(self):
		# self.checkISOinit() # move to main : ms1BtnRunAll
		self.sendStartCmd()
		self.sendSingleCmd()

		while (self.ms1runFlag and self.rawfileindex < self.runLoop):
			# t0 = time.time()
			# m0 = time.localtime(t0).tm_min
			# s0 = time.localtime(t0).tm_sec
			self.getData()
			# t1 = time.time()
			# m1 = time.localtime(t1).tm_min
			# s1 = time.localtime(t1).tm_sec
			# print("getData TIME = " + str(m1-m0) + ":" + str(s1-s0))
			newdatalen = len(self.singleData)
			if (newdatalen > 0):
				outdata = self.singleData
				self.ms1datalen = min(newdatalen, self.ms1datalen)	
				self.ms1TotalData = self.ms1TotalData[0:self.ms1datalen]
				outdata = outdata[0:self.ms1datalen]
				self.ms1TotalData += outdata
				if (self.ms1saveRawPath != ''):
					curr_time = datetime.datetime.now()
					fname = self.ms1saveRawPath +"/"+curr_time.strftime("%Y_%m_%d_%H_%M_%S")+"_"+str(self.rawfileindex)+".txt"	
					tempdata = np.array([self.xplotdata[0:self.ms1datalen], outdata], np.float64)
					tempdata = np.transpose(tempdata)
					header = self.Qss005header+"\n"+str(curr_time)+"\n"+"mass, signal"
					fil2a.list2DtoTextFile(fname, tempdata,",",self.loggername, header = header)
				self.rawfileindex += 1
				totalDataOut = self.ms1TotalData / self.rawfileindex
				self.ms1_update_total_array.emit(self.singleData, totalDataOut)
		# while end
		self.sendStopCmd()
		self.ms1_finished.emit()
		print("----------")

# start the function define for calibration
	def calibra_init(self):
		self.calibPreset = [1, 0]
		self.currData = np.zeros(INIT_DATACOUNT)
		self.xplotdata = np.zeros(INIT_DATACOUNT)

	def calibra_findPeak(self, minHeight, minWidth, calib):
		# print("threshold = " + str(minHeight))
		# print("noise_width = " + str(minWidth))
		if calib:
			self.peaks, _= sp.signal.find_peaks(self.currData, height = minHeight, width = minWidth)
		else:
			self.peaks, _= sp.signal.find_peaks(self.singleData, height = minHeight, width = minWidth)
		
		self.logger.debug("lens of peak" + str(self.peaks))
		self.logger.debug(str(self.peaks))
		return self.peaks

	def calibra_curveFit(self, calbratedata) :
		num = len(calbratedata)
		fitIndex = []
		calbIndex = []
		for i in range(0, num):
			fitIndex.append(self.peaks[calbratedata[i][0]])
			calbIndex.append(calbratedata[i][1])
		calibPreset = np.polyfit(fitIndex, calbIndex, 1)
		self.calibPreset[0] = "%2.4f"%calibPreset[0]
		self.calibPreset[1] = "%2.4f"%calibPreset[1]
		self.logger.debug(str(self.calibPreset))

	def updateCalMass(self):
		for i in range(0, INIT_DATACOUNT):
			self.xplotdata[i] = i*float(self.calibPreset[0]) + float(self.calibPreset[1])

	def checkParamChanged(self, ch2_freq_factor, ch2_final_freq, isoMassCenter, isoMassRange, \
		ch1_trapping_amp, rfVolGain, ch1_freq, r0, z0, iso_chirp_amp, msms_amp):
		if ( (self.old_ch1_trapping_amp == ch1_trapping_amp) 
		and (self.old_ch2_freq_factor == ch2_freq_factor)
		and (self.old_ch2_final_freq == ch2_final_freq)
		and (self.old_isoMassCenter == isoMassCenter)
		and (self.old_isoMassRange == isoMassRange)
		and (self.old_iso_chirp_amp == iso_chirp_amp)
		and (self.old_msms_amp == msms_amp) ):
			self.paramChanged = False
		else:
			self.paramChanged = True
		# print("paramChanged = " + str(self.paramChanged))

		self.ch1_trapping_amp = ch1_trapping_amp
		self.ch2_freq_factor = ch2_freq_factor
		self.ch2_final_freq = ch2_final_freq
		self.isoMassCenter = isoMassCenter
		self.isoMassRange = isoMassRange

		self.rfVolGain = rfVolGain
		self.ch1_freq = ch1_freq
		self.r0 = r0
		self.z0 = z0
		self.iso_chirp_amp = iso_chirp_amp
		self.msms_amp = msms_amp

	def checkISOinit(self):
		if (self.paramChanged == True):
			trapingV = self.ch1_trapping_amp * self.rfVolGain/1000
			#print("trapingVchekc:"+str(self.ch1))

			isoMassMin = self.isoMassCenter - self.isoMassRange
			isoMassMax = self.isoMassCenter + self.isoMassRange
			fmax = self.ch2_freq_factor * self.ch1_freq

			result, msg = self.isoInit(trapingV, self.ch1_freq, self.r0, self.z0, isoMassMin, isoMassMax, self.ch2_final_freq, fmax)
			return result, msg
		else:
			msg = "No Change"
			return True, msg


	def isoInit(self, trapingV, trapingF, r0, z0, isoMassMin, isoMassMax, fmin, fmax):
		self.freqlist = np.linspace(fmin, fmax, CHIRP_DATA_COUNT)
		self.tarray = np.linspace(0, DELTAT*(CHIRP_DATA_COUNT-1), CHIRP_DATA_COUNT)
		# print("trapingV: "+str(trapingV) )
		# print("trapingF: "+str(trapingF) )
		# print("r0: "+str(r0) )
		# print("z0:" +str(z0) )
		_, maxMass = self.massFreqTransfer(trapingV, trapingF, r0, z0, 0, fmin)
		_, minMass = self.massFreqTransfer(trapingV, trapingF, r0, z0, 0, fmax)
		# print("maxMass" + str(maxMass))
		# print("minMass" + str(minMass))
		if (isoMassMin < minMass) or (isoMassMax >  maxMass):
			maxMass_str = "%2.2f" % maxMass
			minMass_str = "%2.2f" % minMass
			msg = ISO_ERROR_MSG1 + minMass_str + " and " + maxMass_str + ISO_ERROR_MSG2
			# print(msg)
			msg = "Error!\n" + msg
			return False, msg
		else:
			self.calChirp(trapingV, trapingF, r0, z0, isoMassMin, isoMassMax)
			fil2a.ArraytoBinFile(ISO_OUT_FILE, self.isoChirpOut,'f')
			fil2a.ArraytoBinFile(MSMS_OUT_FILE, self.msmsOut,'f')
			rm_iso_cmd = "rm " + ISO_OUT_FILE
			rm_msms_cmd = "rm " + MSMS_OUT_FILE
			msg = "No Error"

			if TEST_MODE:
				pass
			else:
				self.ssh.sendCmd(rm_iso_cmd)
				self.ssh.sendCmd(rm_msms_cmd)
				self.ssh.putFtpFile(ISO_OUT_FILE)
				self.ssh.putFtpFile(MSMS_OUT_FILE)

			self.old_ch1_trapping_amp = self.ch1_trapping_amp
			self.old_ch2_freq_factor = self.ch2_freq_factor
			self.old_ch2_final_freq = self.ch2_final_freq
			self.old_isoMassCenter = self.isoMassCenter
			self.old_isoMassRange = self.isoMassRange
			self.old_iso_chirp_amp = self.iso_chirp_amp
			self.old_msms_amp = self.msms_amp

			return True, msg

	def massFreqTransfer(self, trapingV, trapingF, r0, z0, mass, freq):
		print("trapingV = " + str(trapingV))
		print("freq = " + str(freq))
		e = 1.602e-19 
		mol = 6.022e23
		pi = np.pi 
		trapingF = 1000*trapingF
		massout1 = 8*e*mol*trapingV*1000
		massout2 = (r0**2+2*z0**2)*1e-4*(2*pi*1050000)**2
		freq = freq*1000
		if (mass == 0):
			print("massFreqTransfer 1")
			a = 1.5*(35-np.sqrt((1225-70*(1-np.cos(2*pi*freq/trapingF)))))
			qz = (16/np.power(pi,3))*np.sqrt(a)	# Tina
			# qz = (4/np.power(pi,2))*np.sqrt(a)	# GRC
			massout = (massout1/massout2)/qz
			print("massout = " + str(massout))
			fout = freq 
		else:
			print("massFreqTransfer 2")
			qz = (massout1/massout2)/mass
			a = np.power(qz/(16/np.power(pi,3)),2)	# Tina
			# a = np.power(qz/(4/np.power(pi,2)),2)	# GRC
			fout = trapingF*np.arccos(1-((1225-np.power((a/1.5)-35,2))/70))/(2*pi)
			print("fout = " + str(fout))
			massout = mass	
		return fout, massout


	# def isoInit(self, trapingV, trapingF, r0, isoMassMin, isoMassMax, fmin, fmax):
	# 	print("fmin = "+str(fmin))
	# 	print("fmax = "+str(fmax))
	# 	self.freqlist = np.linspace(fmin, fmax, CHIRP_DATA_COUNT)
	# 	self.tarray = np.linspace(0, DELTAT*(CHIRP_DATA_COUNT-1), CHIRP_DATA_COUNT)
	# 	self.calChirp(trapingV, trapingF, r0, isoMassMin, isoMassMax)
	# 	fil2a.ArraytoBinFile(ISO_OUT_FILE, self.isoChirpOut,'f')
	# 	fil2a.ArraytoBinFile(MSMS_OUT_FILE, self.msmsOut,'f')
	# 	rm_iso_cmd = "rm " + ISO_OUT_FILE
	# 	rm_msms_cmd = "rm " + MSMS_OUT_FILE
	# 	self.ssh.sendCmd(rm_iso_cmd)
	# 	self.ssh.sendCmd(rm_msms_cmd)
	# 	self.ssh.putFtpFile(ISO_OUT_FILE)
	# 	self.ssh.putFtpFile(MSMS_OUT_FILE)

	# def massToFreq(self, trapingV, trapingF, r0, mass):
	# 	print("r0 = "+str(r0))
	# 	print("mass = "+str(mass))
	# 	e  = 1.6021766208e-19
	# 	mol = 6.022e23
	# 	# trapingV = trapingV/1000

	# 	qz1 = 8*e*mol*trapingV*1000
	# 	trapingF = trapingF*1000
	# 	qz2 = mass*r0*r0*np.power(2*np.pi*trapingF,2)
	# 	qz = qz1/qz2
	# 	print("trapingV = "+str(trapingV))
	# 	print("trapingF = "+str(trapingF))
	# 	# print("qz in new module="+ str(qz))

	# 	fout =np.arccos(1-(1225-np.power(35-np.power(qz*np.pi*np.pi/4,2)*2/3, 2))/70)*trapingF/2/np.pi
	# 	return fout 

	def calChirp(self, trapingV, trapingF, r0, z0, isoMassMin, isoMassMax):
		#isoFreq1 = self.massToFreq(trapingV, trapingF, r0, isoMassMin)
		isoFreq1, _=self.massFreqTransfer(trapingV, trapingF, r0, z0, isoMassMin, 0)
		isoFreq2, _=self.massFreqTransfer(trapingV, trapingF, r0, z0, isoMassMax, 0)
		print("isoFreq1="+str(isoFreq1))
		print("isoFreq2="+str(isoFreq2))
		self.isoChirpOut = np.zeros(len(self.freqlist))
		self.msmsOut = np.zeros(len(self.freqlist))
		fp1 = open("iso.txt","w")
		fp2 = open("msms.txt","w")

		for f in self.freqlist:
			if (isoFreq2/1000) < f < (isoFreq1/1000):
				self.msmsOut = self.msmsOut + np.sin(2*np.pi*f*self.tarray)
				fp1.write(str(f)+"\n")
			else:
				self.isoChirpOut = self.isoChirpOut + np.sin(2*np.pi*f*self.tarray)
				fp2.write(str(f)+"\n")
		fp1.close()
		fp2.close()
		ampmax_msms = max(self.msmsOut)
		ampmax_iso = max(self.isoChirpOut)
		msmsConst = self.msms_amp/ampmax_msms
		isoConst = self.iso_chirp_amp/ampmax_iso
		self.msmsOut = msmsConst*self.msmsOut
		self.isoChirpOut = isoConst*self.isoChirpOut
		self.setChrip = False

#gauge 
class qss005ActionHK(QObject):
	gauge_update_text = pyqtSignal(str)
	gauge_finished = pyqtSignal()

	def __init__(self, ssh, loggername, paraent = None):	
		super(QObject, self).__init__(paraent)
		self.loggername = loggername
		self.gauge_init()
		self.ssh = ssh

	def gauge_init(self):
		self.gauge_runFlag = False

	def gauge_readData(self):
		cmd = UART_CMD + "1 \"@254PR1?;FF\""
		print(cmd)
		#i = 0
		ErrStr = ""
		while (self.gauge_runFlag):
			stdout, stderr = self.ssh.sendQuerryWithError(cmd)
			ErrStr = stderr.readline()
			print("ErrStr="+ErrStr)
			if (ErrStr != ""):
				ErrStr = "ERROR"
				outlist = []
				self.gauge_update_text.emit(ErrStr)
				cmd = "ps aux | grep UART"
				stdout = self.ssh.sendQuerry(cmd)
				line = stdout.readline()
				#print(line)
				if (line != ""):
					subline = line.rstrip('\n')
					#print(subline)
					outlist.append(subline.split(' '))
					#print(outlist)
					cmd = "kill -9 " + outlist[0][6]
					#print(cmd)
					stdout = self.ssh.sendQuerry(cmd)
				self.gauge_runFlag = False
			else:
				output = stdout.readline()
				if (output != ""):
					output2 = output[7:-4]
					output = str(float(output2))
					self.gauge_update_text.emit(output)
				#print(i)
				#self.gauge_update_text.emit(str(i))
				#i = i + 1
				time.sleep(1)
		# while end
		self.gauge_finished.emit()

if __name__ == '__main__':

	aa = qss005Action("test")
	fout, massout = aa.massFreqTransfer(757, 800, 0.667, 0.522, 0, 10000)
	fout, massout = aa.massFreqTransfer(757, 800, 0.667, 0.522, massout, 0)


