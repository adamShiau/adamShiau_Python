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


SETTING_FILEPATH = "set"
PRSETFILE = "set/setting.txt"
TIME_PRESET_FILE_NAME = "set/time_setting.txt"

INDEX_freq = 0
INDEX_phase = 1
Max_Para_Index = 2

TEST_MODE = False


class qss014Action(QObject):
    update_text = pyqtSignal(float)
    update_adcArray = pyqtSignal(object)
    
    adc_array = np.zeros(0)

    def __init__(self, loggername):	
        super().__init__()
        self.loggername = loggername
        self.COM = usb.FT232(loggername)
        self.logger = logging.getLogger(loggername)
        self.paramInit()
        # self.loadPreset()
        # self.status = True

    def usbConnect(self):
        if (TEST_MODE):
            status = True
        else:
            status = self.COM.connect(baudrate = 9600, timeout = 1)
            print(status)
        return status

    def paramInit(self):
        self.freq = 1000
        self.phase = 0
        self.paralist = ["" for i in range(0, Max_Para_Index)]

    def loadPreset(self):
        if not os.path.isdir(SETTING_FILEPATH):
            os.mkdir(SETTING_FILEPATH)
            self.writePreset()
            self.logger.warning("preseet file dir not exist")

        if os.path.exists(PRSETFILE):
            paralist = fil2a.TexTFileto1DList(PRSETFILE, self.loggername)
            if (len(paralist) != Max_Para_Index):
                self.writePreset()
                self.logger.warning("preseet file formate error")
            else:
                self.paralist = paralist
                self.freq = int(self.paralist[INDEX_freq])
                self.phase = int(self.paralist[INDEX_phase])
        else:
            self.writePreset()
            self.logger.warning("preseet file load failed")

        if os.path.exists(TIME_PRESET_FILE_NAME):
            self.timePreset = fil2a.TexTFileto1DList(TIME_PRESET_FILE_NAME, self.loggername)
        else:
            self.logger.warning("time preset file load failed")
            self.timePreset = [1, 1, 1, 1]
            self.writePreset(1)


    def writePreset(self, type):
        if (type == 1):
            paralist = self.timePreset
            filename = TIME_PRESET_FILE_NAME
        else:
            self.paralist[INDEX_freq] = self.freq
            self.paralist[INDEX_phase] = self.phase
            paralist = self.preset
            filename = PRESET_FILE_NAME

        fil2a.array1DtoTextFile(filename, paralist, self.loggername)

    def sendComCmd(self):
        cmd_freq = "MOD_FREQ " + str(self.freq)
        cmd_phase = "MOD_PHASE " + str(self.phase)
        print (cmd_freq)
        print (cmd_phase)
        self.COM.writeLine(cmd_freq)
        self.COM.writeLine(cmd_phase)
            
    def sendRdAdcCmd(self, stop_flag):
        cmd = "READ_ADC"
        self.COM.writeLine(cmd)
        print(cmd)
        temp = self.COM.readLineF()
        print(temp)       
        self.adc_array = np.append(self.adc_array, float(temp))
        
        if(stop_flag):
            self.adc_array = np.zeros(0)
        # print(stop_flag)
        # print(self.adc_array)
        self.update_text.emit(float(temp))
        self.update_adcArray.emit(self.adc_array)

