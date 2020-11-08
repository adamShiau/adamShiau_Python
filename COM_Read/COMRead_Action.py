import os
import sys
sys.path.append("../")
import time
import numpy as np 
import scipy as sp
from scipy import signal
import py3lib.COMPort as usb
import py3lib.FileToArray as fil2a
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import logging

TEST_MODE = False

class COMRead_Action(QObject):
    # update_data = pyqtSignal(float)
    update_COMArray = pyqtSignal(object)
    com_array = np.zeros(0)
    def __init__(self, loggername):	
        super().__init__()
        # self.loggername = loggername
        self.COM = usb.FT232(loggername)
        self.logger = logging.getLogger(loggername)
        # self.paramInit()
        # self.loadPreset()
        # self.status = True

    def usbConnect(self):
        if (TEST_MODE):
            status = True
        else:
            status = self.COM.connect(baudrate = 115200, timeout = 1)
            print(status)
        return status
    
    def readAscii(self, stop_flag):
        temp = self.COM.readLineF()
        print(temp)
        self.com_array = np.append(self.com_array, float(temp))
        self.update_COMArray.emit(self.com_array)
        if(stop_flag):
            self.com_array = np.zeros(0)
        