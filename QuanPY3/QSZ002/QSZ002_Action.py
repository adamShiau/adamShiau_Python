import sys
import time
import struct
import numpy as np
sys.path.append("../")
import logging
from array import *
from ctypes import *
import py3lib.COMPort as usb
from scipy.signal import freqs, medfilt
from PyQt5.QtCore import *
#OTO USB2.0 spectrameter's VID & PID
VID = 1592
PID = 2732
sys.path.append("../")
TESTPUMP = 0

class qsz002Spectrum(QObject):
    update = pyqtSignal(object,object, object, float)
    finished = pyqtSignal()
    def __init__(self, loggername, parent = None):
        super(QObject,self).__init__(parent)
        self.logger = logging.getLogger(loggername)  
        self.otodll =CDLL("UserApplication.dll")
        self.deviceHandle = c_int(0)
        self.frameSize = c_int(0)
        self.pump = usb.FT232("loggername")
        self.enablePump = False
        self.runFlag = False
        self.minWavelength = 300
        self.maxwavelength = 320
        self.intTime = 5000
        self.avgNumber = 1
        self.threshold = 10000
        self.filterLevel = 1
        self.filterOn = False
        #self.specOpen()
        #self.intTime =self.getIntTime()
    
    # def getDevNumber(self):
    #     number = c_int(0)
    #     print (number.value)
    #     self.otodll.UAI_SpectrometerGetDeviceAmount(0, byref(number), VID, PID)
    #     if number.value > 0:
    #         return True
    #     else:
    #         return False

    def specOpen(self):
        self.frameSizeRef = c_int(0)
        self.otodll.UAI_SpectrometerOpen(0, byref(self.deviceHandle), VID, PID)
        self.otodll.UAI_SpectromoduleGetFrameSize(self.deviceHandle, byref(self.frameSizeRef), VID, PID)
        self.frameSize = self.frameSizeRef.value

    def getIntTime(self):
        time = c_int(0)
        self.otodll.UAI_SpectrometerGetIntegrationTime(self.deviceHandle, byref(time))
        return time.value

    def setIntTime(self, time_us):
        self.otodll.UAI_SpectrometerSetIntegrationTime(self.deviceHandle, time_us)

    def getWavelength(self):
        wavelength=(c_float*self.frameSize)()
        self.wavelengthOut = np.empty(0)
        self.otodll.UAI_SpectrometerWavelengthAcquire(self.deviceHandle, wavelength)

        for i in range(0, self.frameSize):
            self.wavelengthOut = np.append(self.wavelengthOut, wavelength[i])
        print(self.wavelengthOut)
    def getSpectrum(self, time_us, avg):
        intensity = (c_float*self.frameSize)()
        self.intensityOut = np.empty(0)
        self.otodll.UAI_SpectrometerDataOneshot(self.deviceHandle,time_us, byref(intensity),avg)
        self.otodll.UAI_BackgroundRemove(self.deviceHandle, time_us, byref(intensity))
        self.otodll.UAI_LinearityCorrection(self.deviceHandle,self.frameSizeRef,byref(intensity))
        for i in range(0, self.frameSize):
            self.intensityOut = np.append(self.intensityOut, intensity[i])
        #print(self.intensityOut)

    def setFilter(self,level):
        self.filterOut =medfilt(self.intensityOut, level*2+1)

    def setTargetWavelength(self, minWavelength, maxwavelength):
        self.indexlist= np.where((self.wavelengthOut>minWavelength)&(self.wavelengthOut<maxwavelength))
       
        #print("length:"+str(len(indexlist[0]))+",first:"+str(indexlist[0][0])+",end"+str((indexlist[0][0]+len(indexlist[0]))))
        #print(self.wavelengthOut[indexlist[0][0]:indexlist[0][0]+len(indexlist[0])])
    def getTargetWavelenght(self, anaData):
        monitorOut = sum(anaData[self.indexlist[0][0]:self.indexlist[0][0]+len(self.indexlist[0])])
        return monitorOut

    def pumpOpen(self, portid):
        status =self.pump.newConnect(portid, baudrate = 115200, timeout = 1)
        return status

    def setPumpRate(self, rate):
        outstr = "irate "+str(rate)+" ml/min\r\n"
        self.pump.port.write(outstr.encode())

    def setPumpRun(self):
        outstr = "run\r\n"
        self.pump.port.write(outstr.encode())

    def setPumpStop(self):
        outstr ="stop\r\n"
        self.pump.port.write(outstr.encode())

    def devOpen(self, portid, rate):
        if TESTPUMP:
            status =self.pumpOpen(portid)
            self.setPumpRate(rate)
        else:
            status = 1
        
        self.specOpen()
        self.getWavelength()
        return status

    #def runSpectrum(self, minWave, maxWave, intTime, avgNumber, threshold, filterLevel, filterOn):
    def runSpectrum(self):
            index =0
            while (self.runFlag):
            
                self.getSpectrum(self.intTime, self.avgNumber)
                
                self.setTargetWavelength(self.minWave, self.maxWave)
                self.setFilter(self.filterLevel)
                if self.filterOn:  
                    output =self.getTargetWavelenght(self.filterOut)
                else:
                    output = self.getTargetWavelenght(self.intensityOut)

                if (self.enablePump):
                    if output > self.threshold:
                        self.setPumpRun()
                        print("pump on")
                        #self.logging.DEBUG("pump run: output="+str(output))
                    else:
                        print("pump off")
                        self.setPumpStop()

                if self.filterOn:
                    self.update.emit(self.wavelengthOut , self.intensityOut, self.filterOut, output)
                else:
                    self.update.emit(self.wavelengthOut, self.intensityOut, self.filterOut, output)
                index = index+1
                time.sleep(0.5)
            self.finished.emit()




if __name__ == '__main__':
    act = qsz002Spectrum("test")
    #act.setIntTime(1000)
    #act.getWavelength()
    #print(act.getIntTime())
    #act.getSpectrum(5000,20)
    #act.setFilter(1)
    #act.setTargetWavelength(300, 320)
    #data =act.getTargetWavelenght(act.filterOut)
    #print(data)
    #plt.plot(act.wavelengthOut, act.intensityOut)
    #plt.plot(act.wavelengthOut, act.filterOut)
    #plt.show()
    print(act.pumpOpen("1FE9:7101"))
    act.setPumpRate(0.003)
    act.setPumpRun()
    time.sleep(1)
    act.setPumpStop()


 
