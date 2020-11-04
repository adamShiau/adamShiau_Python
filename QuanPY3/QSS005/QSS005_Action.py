import time
import sys
import scipy as sp
import numpy as np 
from scipy import signal
sys.path.append("../")
import py3lib.NetSSH as net 
import py3lib.FileToArray as fil2a
from PyQt4.QtCore import *
from PyQt4.QtGui import *

ms1param_start =0
ms1param_end =10
calibparam_start =11
calibparam_end = 12
PRESET_FILE_NAME="../set/setting.txt"
FAKE_DATA ="data.txt"
INIT_DATACOUNT = 10000


class qss005Action(QObject):
	update_array = pyqtSignal(object)
	update_tot_array = pyqtSignal(object)
	finished = pyqtSignal()
	def __init__(self,loggername):	
		self.loggername = loggername
		self.Qss005header =""
		self.ssh = net.NetSSH(loggername)
		self.ms1init()
		self.calibra_init()
		self.loadPreset()

			
# start the function define for all QSS005
	
	def setQss005header (self, header):
		elf.Qss005header = header

	def resetIndex(self):
		self.rawfileindex =0
		self.ms1totData = np.zeros(INIT_DATACOUNT)
		self.ms1datalen =INIT_DATACOUNT;

	def sshConnect(self, ip, port, usr, psswd):
		sshresult =self.ssh.connectSSH(ip,port,usr,psswd)
		ftpresult =self.ssh.connectFTP()
		setbitstream ="ls -al"
		self.ssh.sendCmd("setbitstram", timedelay=0.5)
		return (sshresult and ftpresult)

	def loadPreset(self):
		paralist =fil2a.TexTFileto1DList(PRESET_FILE_NAME, self.loggername)
		self.ms1Preset = paralist[ms1param_start:ms1param_end]
		self.calibPreset = paralist[calibparam_start:calibparam_end]
		self.xplotdata = [ self.calibPreset[0]*i +self.calibPreset[1] for i in range(0, INIT_DATACOUNT)] # Set x value for calibration data

	def savePreset(self):
		paralist=self.ms1Preset
		paralist.append(self.calibPreset)
		fil2a.array1DtoTextFile(PRESET_FILE_NAME, paralist, self.loggername)



# start the function define for Prepare

	def p0init(self):
		self.p0data = [0,0,0]
	def p0run(self):
		setadc="ls -al"
		ssh.sendCmd(setadc)

# start the function define for MS1
	def ms1init(self):
		self.ms1runFlag = False
		self.ms1saveRaw = False
		self.ms1saveRawPath ="./ms1rawdata/"
		self.rawfileindex =0
		self.ms1totData = np.zeros(INIT_DATACOUNT)
		self.ms1datalen =INIT_DATACOUNT;
		self.ms1noisefilter = False
		self.ms1filterLevel =5
		self.singledata =np.empty(0)
		self.ms1Preset =[]

	def setms1RawPath(self, path):
		self.ms1saveRawPath =path


	def ms1setNoise(enable, level):
		self.ms1noisefilter = enable
		self.ms1filterLevel = level
	
	def ms1fakeData(self):
		self.singledata=fil2a.TexTFileto1DList(FAKE_DATA, self.loggername)

	def ms1single(self, single=True):
		setadc="ls -al"
		readadc="ls -al"
		ssh.sendCmd(setadc)
		stdout =ssh.sendQuerry(radadc, getpty=True)
		filelists =["filename1", "filename2"]
		ssh.getFtpFiles(filelists)
		self.singledata =fil2a.BinFiletoArray("filename1",4,'f', self.loggername)
		if self.ms1noisefilter:
			self.singledata = sp.signal.medfilt(self.singledata, self.ms1filterLevel*2+1)
		self.update_array.emit(self.singledata)
		if single:
			self.finished.emit()

	def ms1multiRun(self):
		while self.ms1runFlag:
			outdata =self.ms1single(single=False)
			self.ms1datalen = min(len(outdata), self.ms1datalen)
			self.ms1totData =self.ms1totData[0:self.ms1datalen]
			self.ms1totData += outdata
			if self.ms1saveRaw:
				fname =self.ms1saveRawPath+str(self.rawfileindex)+".txt"
				fil2a.array1DtoTextFile(fname,outdata, header =self.Qss005header)
			self.rawfileindex +=1
			totdataout = self.ms1totData/self.rawfileindex
			self.update_tot_array.emit(totdataout)
		self.finished.emit()

	# start the function define for calibration
	def calibra_init(self):
		self.calibPreset=[1,0]
		self.xplotdata =np.zeros(INIT_DATACOUNT)


	def calibra_findPeak(self, minHeight, minWidth):
		if self.rawfileindex==0:
			anadata = self.singledata
		else:
			anadata = self.ms1totData/self.rawfileindex

		peaks, _= sp.signal.find_peaks(anadata, minHeight, minWidth)
		return peaks

	def calibra_curveFit(self, index, calbratedata) :
		self.calibPreset =  np.polyfit(index, calbratedata,1)
		return calibPreset

	def calibra_UpdateMass(self):
		self.xplotdata = [ self.calibPreset[0]*i +self.calibPreset[1] for i in range(0, INIT_DATACOUNT)] 











		












