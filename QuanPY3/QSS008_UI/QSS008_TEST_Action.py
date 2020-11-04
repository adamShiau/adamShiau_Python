import time
import sys
import numpy as np 
sys.path.append("../")
import py3lib.NetSSH as net 
import py3lib.FileToArray as fil2a
from PyQt5.QtCore import *
#from PyQt5.QtGui import *

ms1param_start =0
ms1param_end =10
calibparam_start =11
calibparam_end = 12
PRESET_FILE_NAME="../set/setting.txt"
FAKE_DATA ="data.txt"
INIT_DATACOUNT = 10000


class qss008Action(QObject):
	update_array = pyqtSignal(object)
	update_tot_array = pyqtSignal(object)
	finished = pyqtSignal()
	def __init__(self,loggername):	
		self.loggername = loggername
		self.ssh = net.NetSSH(loggername)
			
# start the function define for all QSS005
	def sshCnt(self, ip, port, usr, psswd):
		sshresult =self.ssh.connectSSH(ip,port,usr,psswd)
		ftpresult =self.ssh.connectFTP()
		return (sshresult and ftpresult)

	def sendSSHCmd(self,cmd, getpty = False, timedelay = 0):	#use
		result = self.ssh.sendCmd(cmd, getpty = getpty, timedelay = timedelay)
		return result







		












