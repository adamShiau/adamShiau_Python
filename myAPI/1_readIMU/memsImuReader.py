import sys

sys.path.append("../")
from myLib.mySerial.Connector import Connector
from myLib.mySerial import getData
from myLib.crcCalculator import crcLib
import time
from PyQt5.QtCore import QThread, pyqtSignal
from threading import Thread
from myLib import common as cmn
import numpy as np

IMU_DATA_STRUCTURE = {
    "NANO33_W": (0, 0, 0),
    "NANO33_A": (0, 0, 0),
    "ADXL_A": (0, 0, 0),
    "TIME": (0,)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_NANO33_WX = 14 - 1
POS_ADXL355_AX = 5 - 1
POS_CRC = 26 - 1
old = time.perf_counter_ns()


class memsImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object, object)
        imuThreadStop_qt = pyqtSignal()

    def __init__(self, portName: str = "COM5", baudRate: int = 230400):
        super(memsImuReader, self).__init__()
        self.__Connector = Connector(portName, baudRate)
        self.__isRun = True
        self.__isCali = False
        self.__callBack = None
        self.__crcFail = 0
        self.arrayNum = 10
        self.__old_imudata = {k: (-1,) * len(IMU_DATA_STRUCTURE.get(k)) for k in set(IMU_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(len(IMU_DATA_STRUCTURE.get(k))) for k in set(IMU_DATA_STRUCTURE)}
        print(not __name__ == "__main__")

    # class constructor

    def __del__(self):
        print("class memsImuReader's destructor called!")

    # End of destructor

    @property
    def isRun(self):
        return self.__isRun

    # End of memsImuReader::isRun(getter)

    @isRun.setter
    def isRun(self, isFlag):
        self.__isRun = isFlag

    # End of ImuReader::isRun(setter)

    @property
    def isCali(self):
        return self.__isCali

    # End of memsImuReader::isCali(getter)

    @isCali.setter
    def isCali(self, isFlag):
        self.__isCali = isFlag

    # End of ImuReader::isCali(setter)

    def writeImuCmd(self, cmd, value):
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        self.__Connector.write(data)
        cmn.wait_ms(150)

    # End of memsImuReader::writeImuCmd

    def connect(self):
        self.__Connector.connect()

    # End of memsImuReader::connectIMU

    def disconnect(self):
        self.__Connector.disconnect()

    # End of memsImuReader::disconnectIMU

    def readIMU(self):
        self.writeImuCmd(5, 1)

    def stopIMU(self):
        self.writeImuCmd(5, 4)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuData(self):
        head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
        dataPacket = getData.getdataPacket(self.__Connector, head, 25)
        NANO_W, NANO_A = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX, sf_xlm=SENS_NANO33_AXLM_4G,
                                        sf_gyro=SENS_NANO33_GYRO_250)
        ADXL_A = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX, sf=SENS_ADXL355_8G)
        t = time.perf_counter(),
        imudata = {"NANO33_W": NANO_W, "NANO33_A": NANO_A, "ADXL_A": ADXL_A, "TIME": t}
        # print(imudata)
        return dataPacket, imudata

    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def do_cali(self, dictContainer, cali_times):
        if self.isCali:
            self.isCali = False
            temp = dictContainer
            print("---calibrating offset start-----")
            for i in range(cali_times):
                dataPacket, imudata = self.getImuData()
                temp = cmn.dictOperation(temp, imudata, "ADD")
            temp = {k: temp.get(k) / cali_times for k in set(self.__imuoffset)}
            print("---calibrating offset stop-----")
            return temp
        else:
            return dictContainer

    def run(self):
        t0 = time.perf_counter()
        while True:
            if not self.isRun:
                self.stopIMU()
                self.imuThreadStop_qt.emit()
                break
            # End of if-condition

            self.__imuoffset = self.do_cali(self.__imuoffset, 100)

            imudataArray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
                            for k in set(IMU_DATA_STRUCTURE)}
            for i in range(self.arrayNum):
                while self.__Connector.readInputBuffer() < self.arrayNum * 10:
                    # print(self.__Connector.readInputBuffer())
                    pass

                dataPacket, imudata = self.getImuData()
                isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))

                # err correction
                # if not isCrcFail:
                #     self.__old_imudata = imudata
                # else:
                #     self.__crcFail += 1
                #     print("crc fail occur: ", self.__crcFail)
                #     imudata = self.__old_imudata
                imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction

                imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND")
            # end of for loop

            # print(imudataArray["TIME"][0]-10)
            imudataArray["TIME"] = [imudataArray["TIME"] - t0]  # do not remove this bracket
            # print("reader: ", end=", ")
            # print(imudataArray["TIME"])
            if self.__callBack is not None:
                self.__callBack(imudataArray, self.__imuoffset)

            if not __name__ == "__main__":
                self.imudata_qt.emit(imudataArray, self.__imuoffset)
            # print(imudataArray)

        # end of while loop
    # End of memsImuReader::run


def myCallBack(imudata, imuoffset):
    global old
    new = time.perf_counter_ns()
    # print(imudata)
    # print(imuoffset)
    # print()
    # print(imudata["NANO33_A"][2])
    # print(imuoffset["NANO33_A"][2])
    # print(imudata["NANO33_A"][2]-imuoffset["NANO33_A"][2])
    # imuoffset["TIME"] = [0]
    imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
    # print(imudata["NANO33_A"][2])
    wx = imudata["NANO33_W"][0]
    wy = imudata["NANO33_W"][1]
    wz = imudata["NANO33_W"][2]
    ax = imudata["ADXL_A"][0]
    ay = imudata["ADXL_A"][1]
    az = imudata["ADXL_A"][2]
    t = imudata["TIME"][0]
    print("%.5f %.5f  %.5f  %.5f  %.5f  %.5f  %.5f" % (t, wx, wy, wz, ax, ay, az))
    # print(imuoffset["TIME"], imuoffset["NANO33_W"], imuoffset["ADXL_A"])
    old = new


if __name__ == "__main__":
    myImu = memsImuReader("COM5")
    myImu.arrayNum = 1
    myImu.setCallback(myCallBack)
    myImu.isCali = True
    myImu.connect()
    myImu.readIMU()
    myImu.start()
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.stopIMU()
        myImu.disconnect()
        myImu.wait()
        print('KeyboardInterrupt success')
