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
    "TIME": (0,),
    "SPARROW": (0,)
}

IMU_DATA_STRUCTURE_ARRAY = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE[k]))]
                            for k in set(IMU_DATA_STRUCTURE)}

# print([(k, len(IMU_DATA_STRUCTURE[k])) for k in IMU_DATA_STRUCTURE])

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_ADXL355_AX = 5 - 1
POS_NANO33_WX = 14 - 1
POS_SPARROW = 26 - 1
POS_CRC = 32 - 1
old = time.perf_counter_ns()


class memsImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object, object)
        imuThreadStop_qt = pyqtSignal()

    def __init__(self, portName: str = "COM6", baudRate: int = 230400):
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
        # self.writeImuCmd(5, 1)
        self.__Connector.flushInputBuffer()
        self.writeImuCmd(6, 3)
        cmn.wait_ms(500)
        self.writeImuCmd(6, 1)

    def stopIMU(self):
        # self.writeImuCmd(5, 4)
        self.writeImuCmd(6, 4)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuData(self):
        head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
        dataPacket = getData.getdataPacket(self.__Connector, head, 31)
        NANO_W, NANO_A = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX, sf_xlm=SENS_NANO33_AXLM_4G,
                                        sf_gyro=SENS_NANO33_GYRO_250)
        ADXL_A = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX, sf=SENS_ADXL355_8G)
        SPARROW = cmn.readSparrow(dataPacket, EN=1, PRINT=0, POS_SPARROW=POS_SPARROW, sf_a=-0.0016939, sf_b=-0.0013805)
        t = time.perf_counter(),
        imudata = {"NANO33_W": NANO_W, "NANO33_A": NANO_A, "ADXL_A": ADXL_A, "TIME": t, "SPARROW": SPARROW}
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
                temp = cmn.dictOperation(temp, imudata, "ADD", IMU_DATA_STRUCTURE_ARRAY)
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
                print("ACT: ", end=", ")
                print(self.__Connector.readInputBuffer(), end=", ")
                t1 = time.perf_counter()
                # while self.__Connector.readInputBuffer() < self.arrayNum * 100:
                while not self.__Connector.readInputBuffer():
                    # print(self.__Connector.readInputBuffer())
                    pass

                dataPacket, imudata = self.getImuData()
                t2 = time.perf_counter()
                isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                t3 = time.perf_counter()
                # err correction
                imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction
                t4 = time.perf_counter()
                imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND", IMU_DATA_STRUCTURE_ARRAY)
                # imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
                # imudataArray["SPARROW"] = np.append(imudataArray["SPARROW"], imudata["SPARROW"])
                # imudataArray["NANO33_A"][0] = np.append(imudataArray["NANO33_A"][0], imudata["NANO33_A"][0])
                # imudataArray["NANO33_A"][1] = np.append(imudataArray["NANO33_A"][1], imudata["NANO33_A"][1])
                # imudataArray["NANO33_A"][2] = np.append(imudataArray["NANO33_A"][2], imudata["NANO33_A"][2])
                # imudataArray["NANO33_W"][0] = np.append(imudataArray["NANO33_W"][0], imudata["NANO33_W"][0])
                # imudataArray["NANO33_W"][1] = np.append(imudataArray["NANO33_W"][1], imudata["NANO33_W"][1])
                # imudataArray["NANO33_W"][2] = np.append(imudataArray["NANO33_W"][2], imudata["NANO33_W"][2])
                t5 = time.perf_counter()
                # print((t5 - t1) * 1000, end=", ")
                # print((t2 - t1) * 1000, end=", ")
                # print((t3 - t2) * 1000, end=", ")
                # print((t4 - t3) * 1000, end=", ")
                # print((t5 - t4) * 1000)

                t1 = t5
            # end of for loop

            imudataArray["TIME"] = imudataArray["TIME"] - t0  # do not remove this bracket
            # imudataArray["SPARROW"] = [imudataArray["SPARROW"]]

            if self.__callBack is not None:
                self.__callBack(imudataArray, self.__imuoffset)

            if not __name__ == "__main__":
                self.imudata_qt.emit(imudataArray, self.__imuoffset)

        # end of while loop
    # End of memsImuReader::run


def myCallBack(imudata, imuoffset):
    global old
    new = time.perf_counter_ns()
    imuoffset["TIME"] = [0]
    imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE_ARRAY)
    # print(imudata["NANO33_A"][2])
    wx = imudata["NANO33_W"][0]
    wy = imudata["NANO33_W"][1]
    wz = imudata["NANO33_W"][2]
    ax = imudata["ADXL_A"][0]
    ay = imudata["ADXL_A"][1]
    az = imudata["ADXL_A"][2]
    fog = imudata["SPARROW"]
    t = imudata["TIME"]
    # print("%.5f %.5f  %.5f  %.5f  %.5f  %.5f  %.5f" % (t, wx, wy, wz, ax, ay, az))
    print(t, fog)
    old = new


if __name__ == "__main__":
    myImu = memsImuReader("COM6")
    myImu.arrayNum = 5
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
