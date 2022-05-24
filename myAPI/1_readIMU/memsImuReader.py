import sys
import logging

sys.path.append("../")
from myLib.mySerial.Connector import Connector
from myLib.mySerial import getData
from myLib.crcCalculator import crcLib
import time
from PyQt5.QtCore import QThread, pyqtSignal
from myLib import common as cmn
import numpy as np

IMU_DATA_STRUCTURE = {
    "NANO33_W": (0, 0, 0),
    "NANO33_A": (0, 0, 0),
    "ADXL_A": (0, 0, 0),
    "TIME": (0,)
}
IMU_DATA_STRUCTURE_ARRAY = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE[k]))]
                            for k in set(IMU_DATA_STRUCTURE)}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_ADXL355_AX = 5 - 1
POS_NANO33_WX = 14 - 1
POS_CRC = 26 - 1
old = time.perf_counter_ns()


class memsImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object, object)
        imuThreadStop_qt = pyqtSignal()

    def __init__(self, portName: str = "COM6", baudRate: int = 230400, debug_en: bool = 0):
        super(memsImuReader, self).__init__()
        # self.__Connector = Connector(portName, baudRate)
        self.__portName = portName
        self.__baudRate = baudRate
        self.__isRun = True
        self.__isCali = False
        self.__callBack = None
        self.__crcFail = 0
        self.arrayNum = 10
        self.__debug = debug_en
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

    def connect(self, portName=None, baudRate=0):
        self.__Connector = Connector(self.__portName, self.__baudRate)
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
        # print(dataPacket + [255])
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
                input_buf = self.readInputBuffer()

                # while self.__Connector.readInputBuffer() < self.arrayNum * 10:
                while not self.__Connector.readInputBuffer():
                    # print(self.__Connector.readInputBuffer())
                    pass
                t1 = time.perf_counter()
                dataPacket, imudata = self.getImuData()
                t2 = time.perf_counter()
                isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                t3 = time.perf_counter()
                # err correction
                imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction
                t4 = time.perf_counter()
                imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND", IMU_DATA_STRUCTURE_ARRAY)
                t5 = time.perf_counter()

                debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                             + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                             + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)

            # end of for loop

            # print(imudataArray["TIME"][0]-10)
            imudataArray["TIME"] = imudataArray["TIME"] - t0
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
    imuoffset["TIME"] = [0]
    imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE_ARRAY)
    # print(imudata["NANO33_A"][2])
    wx = imudata["NANO33_W"][0]
    wy = imudata["NANO33_W"][1]
    wz = imudata["NANO33_W"][2]
    ax = imudata["ADXL_A"][0]
    ay = imudata["ADXL_A"][1]
    az = imudata["ADXL_A"][2]
    t = imudata["TIME"][0]
    # print("%.5f %.5f  %.5f  %.5f  %.5f  %.5f  %.5f" % (t, wx, wy, wz, ax, ay, az))
    # print(imudata["TIME"], imudata["NANO33_W"], imudata["ADXL_A"])
    old = new


if __name__ == "__main__":
    myImu = memsImuReader("COM5", debug_en=True)
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
