import sys
# from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

sys.path.append("../")
from myLib.mySerial.Connector import Connector
from myLib.mySerial import getData
from myLib.crcCalculator import crcLib
import time
import common as cmn
import numpy as np

IMU_DATA_STRUCTURE = {
    "NANO33_W": (0, 0, 0),
    "NANO33_A": (0, 0, 0),
    "ADXL_A": (0, 0, 0),
    "SPARROW": (0,)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00763
SENS_NANO33_AXLM_4G = 0.000122
POS_NANO33_WX = 14 - 1
POS_ADXL355_AX = 5 - 1
POS_SPARROW = 26 - 1
POS_CRC = 26 - 1
print("__name__: ", __name__)


class memsImuReader(QThread):
    imudata_qt = pyqtSignal(object, object, object)

    def __init__(self, portName: str = "COM6", baudRate: int = 230400):
        super(memsImuReader, self).__init__()
        self.Connector = Connector(portName, baudRate)
        self.__isRun = True
        self.__isCali = False
        self.__callBack = None
        self.arrayNum = 10
        self.__crcFail = 0
        self.__old_imudata = {k: (-1,) * len(IMU_DATA_STRUCTURE.get(k)) for k in set(IMU_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(len(IMU_DATA_STRUCTURE.get(k))) for k in set(IMU_DATA_STRUCTURE)}
        # self.imudata_qt.connect(self.getPyqtsignal)
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
        print("setter ", isFlag)
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

    def connectIMU(self):
        self.Connector.connect()
        # self.writeImuCmd(5, 1)

    # End of memsImuReader::connectIMU

    def disconnectIMU(self):
        self.writeImuCmd(5, 4)
        self.Connector.disconnect()

    # End of memsImuReader::disconnectIMU

    def startIMU(self):
        self.writeImuCmd(6, 3)
        cmn.wait_ms(100)
        self.writeImuCmd(6, 1)

    def stopIMU(self):
        self.writeImuCmd(6, 4)

    def writeImuCmd(self, cmd, value):
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        self.Connector.write(data)
        cmn.wait_ms(150)

    # End of memsImuReader::writeImuCmd

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuData(self):
        head = getData.alignHeader_4B(self.Connector, HEADER_KVH)
        dataPacket = getData.getdataPacket(self.Connector, head, 31)
        NANO_W, NANO_A = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX, sf_xlm=SENS_NANO33_AXLM_4G,
                                        sf_gyro=SENS_NANO33_GYRO_250)
        ADXL_A = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX, sf=SENS_ADXL355_8G)
        SPARROW = cmn.readSparrow(dataPacket, EN=1, PRINT=0, POS_SPARROW=POS_SPARROW, sf_a=-0.0016939, sf_b=-0.0013805)
        imudata = {"NANO33_W": NANO_W, "NANO33_A": NANO_A, "ADXL_A": ADXL_A, "SPARROW": SPARROW}
        return dataPacket, imudata

    def readInputBuffer(self):
        return self.Connector.readInputBuffer()

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
        while True:
            if not self.isRun:
                break
            # End of if-condition
            imudataArray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
                            for k in set(IMU_DATA_STRUCTURE)}
            self.__imuoffset = self.do_cali(self.__imuoffset, 100)

            t = np.empty(0)
            for i in range(self.arrayNum):
                while self.Connector.readInputBuffer()<self.arrayNum*10:
                    # print(self.Connector.readInputBuffer())
                    pass

                dataPacket, imudata = self.getImuData()
                isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                t = np.append(t, time.perf_counter())
                # err correction
                if not isCrcFail:
                    self.__old_imudata = imudata
                else:
                    self.__crcFail += 1
                    print("crc fail occur: ", self.__crcFail)
                    imudata = self.__old_imudata
                # end of err correction
                cmn.dictOperation(imudataArray, imudata, "APPEND")
            # end of for loop
            # print(imudataArray)

            # self.__callBack(imudataArray, self.__imuoffset)
            self.imudata_qt.emit(imudataArray, self.__imuoffset, t)
    # End of memsImuReader::run



def getPyqtsignal(imudata, imuoffset):
    print("getPyqtsignal: ", imudata)
    print("getPyqtsignal: ", imuoffset)


def myCallBack(imudata, imuoffset):
    # print("\nimudata: ", imudata)
    # print("imuoffset: ", imuoffset)
    # print("callback")
    imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
    print(imudata)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myImu = memsImuReader("COM6")
    myImu.imudata_qt.connect(getPyqtsignal)
    # myImu.setCallback(myCallBack)
    myImu.isCali = True
    myImu.connectIMU()
    # myImu.imudata_qt.connect(getPyqtsignal)
    myImu.start()

    try:
        app.exec_()
        # while True:
        #     time.sleep(.1)
    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.disconnectIMU()
        myImu.wait()

        print('KeyboardInterrupt success')

