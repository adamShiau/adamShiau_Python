import os
import sys
sys.path.append("../")
import time
import datetime
import logging
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.NetSSH as net 
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# start the function define for all QSS005
class qss005Action():
	def __init__(self, loggername, paraent = None):	
		self.loggername = loggername
		self.ssh1 = net.NetSSH(loggername)

	def sshConnect(self, ch, ip, port, usr, psswd):
		sshresult = self.ssh1.connectSSH(ip, port, usr, psswd)
		ftpresult = self.ssh1.connectFTP()
		return (sshresult and ftpresult)

