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
    fog_update = pyqtSignal(object,object)
    fog_finished = pyqtSignal()
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
            
    # def runFog(self):
            # if self.runFlag:
                    # dt_old = 0
                    # while self.runFlag:
                            # data = np.empty(0)
                            # dt = np.empty(0)
                            # for i in range(0,40): #更新40筆資料到data and dt array
                                    # temp = self.COM.readLine()
                                    # print('temp= ', temp)
                                    # if (temp != "") and (temp != "ERROR"):
                                            # temp = int(temp)
                                            # data = np.append(data, temp)
                                            # dt_new = dt_old + i*0.01
                                            # dt = np.append(dt, dt_new)
                            # self.fog_update.emit(data,dt)
                            # dt_old = dt_new + 0.01
                    # self.COM.port.flushInput()
                    # self.fog_finished.emit()
					
    def runFog(self):
        if self.runFlag:
            dt_old = 0
            data = np.empty(0)
            dt = np.empty(0)
            temp = 0
            while self.runFlag:
                data = np.empty(0)
                # dt = np.empty(0)
                while(not (self.COM.port.inWaiting()>64)) :
                    pass
                # temp = self.COM.read4Binary()
                # temp = temp[0]<<24|temp[1]<<16|temp[2]<<8|temp[3]
                # data = np.append(data, temp)
                # print(self.COM.port.inWaiting(), end=',')
                # print(temp)
                # dt_new = dt_old + 0.01
                # dt = np.append(dt, dt_new)
                                        
                    # if(self.COM.port.inWaiting() > 0):
                            # temp = self.COM.read4Binary()
                            # data = np.append(data, temp[0]<<24|temp[1]<<16|temp[2]<<8|temp[3])
                            # dt_new = dt_old + 0.01
                            # dt = np.append(dt, dt_new)
                                                        
                                                
                for i in range(0,5): #更新40筆資料到data and dt array
                    temp = self.COM.read4Binary()
                    temp = temp[0]<<24|temp[1]<<16|temp[2]<<8|temp[3]
                    data = np.append(data, temp)
                    dt_new = dt_old + i*0.01
                    dt = np.append(dt, dt_new)
						# print('temp= ', temp)
						# if (temp != "") and (temp != "ERROR"):
								# temp = int(temp)
								# data = np.append(data, temp)
								# dt_new = dt_old + i*0.01

                print(len(data), end=', ')
                print(len(dt), end=', ')
                print(self.COM.port.inWaiting())
                self.fog_update.emit(data,dt)
                # print(dt, end=', ')
                # print(data)
                dt_old = dt_new + 0.01
                data = np.empty(0)
                dt = np.empty(0)
                
                # self.COM.port.flushInput()
            self.fog_finished.emit()

