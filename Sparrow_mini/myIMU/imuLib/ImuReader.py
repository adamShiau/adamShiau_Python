#!/usr/bin/env python
# -*- coding:UTF-8 -*-
from threading import Thread
import time
import sys

sys.path.append("../")
from imuLib.ImuConnector import ImuConnector


class ImuReader(Thread):
    """
    Description:
    =============================================

    ---------------------------------------------
    Author:    Adam Shiau
    Date:      04/18/2022
    """

    def __init__(self, strPortName="COM15", iBaudRate=230400, fTimeOut=2):
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
        super().__init__()
        self.__oImuConnector = ImuConnector(strPortName, iBaudRate, fTimeOut)
        self.__isRun = True
        self.__oCallBacker = None

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
        self.__oImuConnector.closeFOG()

    def disconnectUSB(self):
        self.__oImuConnector.close()

    def run(self):
        startTime = time.perf_counter()
        while True:
            if not self.isRun:
                break
            # End of if-condition
            err, fog_wz, PD_temperature, ax, ay, az, wx, wy, mems_wz = self.__oImuConnector.getImuData()
            currentTime = time.perf_counter() - startTime
            imuData = {"TIME": currentTime, "FOG_W": fog_wz, "MEMS_W": (wx, wy), "MEMS_A": (ax, ay, az)}
            if not (self.__oCallBacker is None):
                self.__oCallBacker(imuData)
            # End of if-condition
        # End of while loop


def getImuData(imudata: dict):
    t = imudata["TIME"]
    fog_wz = imudata["FOG_W"]
    wx, wy = imudata["MEMS_W"]
    ax, ay, az = imudata["MEMS_A"]
    print("%.5f, %d, %.5f, %.5f, %.5f, %.5f, %.5f" % (t, fog_wz, wx, wy, ax, ay, az))


if __name__ == "__main__":
    print("running ImuReader.py")
    old_time = time.perf_counter()
    myImu = ImuReader()
    myImu.connectIMU()
    myImu.setCallback(getImuData)
    myImu.start()

    try:
        while True:
            time.sleep(.1)
            pass
    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.disconnectIMU()
        myImu.join()
        myImu.disconnectUSB()
        print('KeyboardInterrupt success')
