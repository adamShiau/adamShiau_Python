#!/usr/bin/env python
# -*- coding:UTF-8 -*-
from __future__ import print_function
from threading import Thread
import time
import sys

sys.path.append("../")
from imuLib.ImuConnector import ImuConnector
import imuLib.fogParameters as fog


class ImuReader(Thread):
    """
    Description:
    =============================================

    ---------------------------------------------
    Author:    Adam Shiau
    Date:      04/18/2022
    """

    def __init__(self, strPortName="COM15", boolCaliw=0, boolCalia=0, iBaudRate=230400, fTimeOut=2):
        """
        Description:
        =============================================
        Initialize the object of this class.

        Args
        =============================================
        strPortName:    type: str, the serial port name
        iBaudRate:      type: int, the baud rate of serial port
        fTimeOut:       type: float, set a read timeout value.
        """
        super(ImuReader, self).__init__()
        self.__oImuConnector = ImuConnector(strPortName, iBaudRate, fTimeOut)
        self.__isRun = True
        self.__oCallBacker = None
        self.__crcFail = 0
        self.__old_pig = tuple([0] * 4)
        self.__old_nano33 = tuple([0] * 6)
        self.__old_adxl355 = tuple([0] * 3)
        self.__cali_iteration = 0
        self.__cali_offset = {"FOG_OS": .0, "MEMS_W_OS": [.0, .0, .0], "MEMS_A_OS": [.0, .0, .0]}
        self.__cali_accumulator = {"FOG": .0, "MEMS_W": [.0, .0, .0], "MEMS_A": [.0, .0, .0]}
        if boolCaliw:
            self.__cali_gyro = True
        else:
            self.__cali_gyro = False

        if boolCalia:
            self.__cali_xlm = True
        else:
            self.__cali_xlm = False


    # End of constructor

    @property
    def isRun(self):
        """
        Description:
        =====================================================
        This flag can control this class to run or not.
        """
        return self.__isRun

    # End of ImuReader::isRun(getter)

    @isRun.setter
    def isRun(self, isFlag):
        self.__isRun = isFlag

    # End of ImuReader::isRun(setter)

    @property
    def cali_gyro(self):
        return self.__cali_gyro

    @cali_gyro.setter
    def cali_gyro(self, cali_gflag):
        self.__cali_gyro = cali_gflag

    @property
    def cali_xlm(self):
        return self.__cali_xlm

    @cali_xlm.setter
    def cali_xlm(self, cali_xflag):
        self.__cali_xlm = cali_xflag

    def setCallback(self, callback):
        """
        Description:
        ======================================================
        Set the callback fucntion.

        Args:
        ======================================================
        - callback: ptype: fuction, this argument is a callback fucntion

        Returns:
        ======================================================
        - rtype: void

        """
        self.__oCallBacker = callback

    def connectIMU(self):
        self.__oImuConnector.connect()
        self.__oImuConnector.updateFogParameters()

    def disconnectIMU(self):
        self.__oImuConnector.stopFOG()
        self.__oImuConnector.close()

    def disconnectUSB(self):
        self.__oImuConnector.close()

    def getImuData(self):
        imuPacket, isCRCfail = self.__oImuConnector.readImuPacket(fog.HEADER_PIG, 38)
        pig = self.__oImuConnector.readPIG(imuPacket, EN=True, PRINT=False, sf_a=fog.SF_A_INIT, sf_b=fog.SF_B_INIT)
        adxl355 = self.__oImuConnector.readADXL355(imuPacket, EN=True, PRINT=False, sf=fog.SENS_ADXL355_8G)
        nano33 = self.__oImuConnector.readNANO33(imuPacket, EN=True, PRINT=False, sf_xlm=fog.SENS_NANO33_AXLM_4G,
                                                 sf_gyro=fog.SENS_NANO33_GYRO_250)
        return pig, adxl355, nano33, isCRCfail

    def do_cali(self, imuData):
        print("---calibrating offset-----")
        if self.__cali_iteration < 100:
            self.__cali_accumulator["FOG"] += imuData["FOG_W"]
            for i in range(3):
                self.__cali_accumulator["MEMS_W"][i] += imuData["MEMS_W"][i]
                self.__cali_accumulator["MEMS_A"][i] += imuData["MEMS_A"][i]
            self.__cali_iteration += 1
        else:
            if self.cali_gyro:
                self.__cali_offset["FOG_OS"] = self.__cali_accumulator["FOG"] / self.__cali_iteration
                for i in range(3):
                    self.__cali_offset["MEMS_W_OS"][i] = self.__cali_accumulator["MEMS_W"][i] / self.__cali_iteration
            if self.cali_xlm:
                for i in range(3):
                    self.__cali_offset["MEMS_A_OS"][i] = self.__cali_accumulator["MEMS_A"][i] / self.__cali_iteration
            self.__cali_gyro = False
            self.__cali_xlm = False

    def run(self):
        while True:
            if not self.isRun:
                break
            # End of if-condition
            pig, adxl355, nano33, isCRCfail = self.getImuData()
            if isCRCfail:
                pig = self.__old_pig
                adxl355 = self.__old_adxl355
                nano33 = self.__old_nano33
                self.__crcFail += 1
                print("crc fail: ", self.__crcFail)
            currentTime = pig[0]
            fog_wz = pig[2]
            wx = nano33[1]
            wy = -nano33[0]
            wz = nano33[2]
            ax = adxl355[0]
            ay = adxl355[1]
            az = adxl355[2]
            self.__old_pig = pig
            self.__old_adxl355 = adxl355
            self.__old_nano33 = nano33
            imuData = {"TIME": currentTime, "FOG_W": fog_wz, "MEMS_W": (wx, wy, wz), "MEMS_A": (ax, ay, az)}
            if self.__cali_gyro or self.__cali_xlm:
                self.do_cali(imuData)
            if (not (self.__oCallBacker is None)) and (not self.__cali_gyro) and (not self.__cali_xlm):
                self.__oCallBacker(imuData, self.__cali_offset)
            # End of if-condition
        # End of while loop


def myCallBack(imudata, offset):
    t = imudata["TIME"]
    fog_wz = imudata["FOG_W"] - offset["FOG_OS"]
    wx, wy, wz = [imudata["MEMS_W"][i] - offset["MEMS_W_OS"][i] for i in range(3)]
    ax, ay, az = [imudata["MEMS_A"][i] - offset["MEMS_A_OS"][i] for i in range(3)]
    print("%.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f" % (t, wx, wy, fog_wz, ax, ay, az))


if __name__ == "__main__":
    print("running ImuReader.py")
    myImu = ImuReader("/dev/ttyACM1")
    myImu.cali_gyro = True
    myImu.cali_xlm = True
    myImu.connectIMU()
    myImu.setCallback(myCallBack)
    myImu.start()

    try:
        while True:
            time.sleep(.1)
            pass
    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.disconnectIMU()
        myImu.join()
        print('KeyboardInterrupt success')
