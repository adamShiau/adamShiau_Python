import sys
import logging

sys.path.append("../")
from imuLib.Connector import Connector
from imuLib import getData
from imuLib import crcLib
import time
from PyQt5.QtCore import QThread, pyqtSignal
from imuLib import common as cmn
import numpy as np
import logging

# from pig_parameters import *

IMU_DATA_STRUCTURE = {
    "NANO33_WX": np.zeros(1),
    "NANO33_WY": np.zeros(1),
    "NANO33_WZ": np.zeros(1),
    "ADXL_AX": np.zeros(1),
    "ADXL_AY": np.zeros(1),
    "ADXL_AZ": np.zeros(1),
    "PIG_ERR": np.zeros(1),
    "PIG_WZ": np.zeros(1),
    "PD_TEMP": np.zeros(1),
    "TIME": np.zeros(1)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_ADXL355_AX = 4
POS_NANO33_WX = 13
POS_PIG = 25
POS_CRC = 35
old = time.perf_counter_ns()


class pigImuReader(QThread):
    # if not __name__ == "__main__":
    # imudata_qt = pyqtSignal(object, object)
    # imuThreadStop_qt = pyqtSignal()
    # buffer_qt = pyqtSignal(int)

    def __init__(self, portName: str = "None", boolCaliw=0, boolCalia=0, baudRate: int = 230400, debug_en: bool = 0):
        super(pigImuReader, self).__init__()
        self.__isCali_w = boolCaliw
        self.__isCali_a = boolCalia
        self.__Connector = None
        self.__portName = portName
        self.__baudRate = baudRate
        self.__isRun = True
        self.__isCali = (self.isCali_w or self.isCali_a)
        # print(self.isCali_w)
        # print(self.isCali_a)
        # print(self.__isCali)
        self.__callBack = None
        self.__crcFail = 0
        self.arrayNum = 10
        self.__debug = debug_en
        self.__old_imudata = {k: (-1,) * len(IMU_DATA_STRUCTURE.get(k)) for k in set(IMU_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(1) for k in set(IMU_DATA_STRUCTURE)}
        # print(not __name__ == "__main__")

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

    @property
    def isCali_w(self):
        return self.__isCali_w

    # End of memsImuReader::isCali_w(getter)

    @isCali_w.setter
    def isCali_w(self, isFlag):
        self.__isCali_w = isFlag

    # End of ImuReader::isCali_w(setter)

    @property
    def isCali_a(self):
        return self.__isCali_a

    # End of memsImuReader::isCali_a(getter)

    @isCali_a.setter
    def isCali_a(self, isFlag):
        self.__isCali_a = isFlag

    # End of ImuReader::isCali_a(setter)

    def writeImuCmd(self, cmd, value):
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        self.__Connector.write(data)
        cmn.wait_ms(150)

    # End of memsImuReader::writeImuCmd

    def connect(self, port, portName, baudRate):
        self.__Connector = port
        port.portName = portName
        port.baudRate = baudRate
        is_open = self.__Connector.connect()
        return is_open

    # End of memsImuReader::connectIMU

    def disconnect(self):
        is_open = self.__Connector.disconnect()
        return is_open

    # End of memsImuReader::disconnectIMU

    def readIMU(self):
        self.writeImuCmd(2, 1)

    def stopIMU(self):
        self.writeImuCmd(2, 4)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuData(self):
        head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
        dataPacket = getData.getdataPacket(self.__Connector, head, 35)
        NANO_WX, NANO_WY, NANO_WZ, \
        NANO_AX, NANO_AY, NANO_AZ = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX,
                                                   sf_xlm=SENS_NANO33_AXLM_4G,
                                                   sf_gyro=SENS_NANO33_GYRO_250)
        ADXL_AX, ADXL_AY, ADXL_AZ = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX,
                                                    sf=SENS_ADXL355_8G)
        ERR, STEP, PD_TEMP = cmn.readPIG(dataPacket, EN=1, PRINT=0, sf_a=1, sf_b=0, POS_ERR=POS_PIG)
        t = time.perf_counter()
        imudata = {"NANO33_WX": NANO_WX, "NANO33_WY": NANO_WY, "NANO33_WZ": NANO_WZ,
                   "ADXL_AX": NANO_AX, "ADXL_AY": ADXL_AY, "ADXL_AZ": ADXL_AZ, "TIME": t,
                   "PIG_ERR": ERR, "PIG_WZ": STEP, "PD_TEMP": PD_TEMP
                   }
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
                temp = cmn.dictOperation(temp, imudata, "ADD", IMU_DATA_STRUCTURE)
            temp = {k: temp.get(k) / cali_times for k in set(self.__imuoffset)}
            print("---calibrating offset stop-----")
            return temp
        else:
            return dictContainer

    def run(self):
        logging.basicConfig(level=100)
        t0 = time.perf_counter()
        while True:
            if not self.isRun:
                self.stopIMU()
                # self.imuThreadStop_qt.emit()
                break
            # End of if-condition

            self.__imuoffset = self.do_cali(self.__imuoffset, 100)

            # imudataArray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
            #                 for k in set(IMU_DATA_STRUCTURE)}

            imudataArray = {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

            for i in range(self.arrayNum):
                input_buf = self.readInputBuffer()
                # self.buffer_qt.emit(input_buf)
                # while self.__Connector.readInputBuffer() < self.arrayNum * 10:
                while not self.__Connector.readInputBuffer():
                    # print(self.__Connector.readInputBuffer())
                    # print("No input data!")
                    # cmn.wait_ms(500)
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
                # imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND", IMU_DATA_STRUCTURE)
                imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
                imudataArray["ADXL_AX"] = np.append(imudataArray["ADXL_AX"], imudata["ADXL_AX"])
                imudataArray["ADXL_AY"] = np.append(imudataArray["ADXL_AY"], imudata["ADXL_AY"])
                imudataArray["ADXL_AZ"] = np.append(imudataArray["ADXL_AZ"], imudata["ADXL_AZ"])
                imudataArray["NANO33_WX"] = np.append(imudataArray["NANO33_WX"], imudata["NANO33_WX"])
                imudataArray["NANO33_WY"] = np.append(imudataArray["NANO33_WY"], imudata["NANO33_WY"])
                imudataArray["NANO33_WZ"] = np.append(imudataArray["NANO33_WZ"], imudata["NANO33_WZ"])
                imudataArray["PIG_ERR"] = np.append(imudataArray["PIG_ERR"], imudata["PIG_ERR"])
                imudataArray["PIG_WZ"] = np.append(imudataArray["PIG_WZ"], imudata["PIG_WZ"])
                imudataArray["PD_TEMP"] = np.append(imudataArray["PD_TEMP"], imudata["PD_TEMP"])
                t5 = time.perf_counter()

                debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                             + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                             + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)

            # end of for loop
            imudataArray["TIME"] = imudataArray["TIME"] - t0
            if self.__callBack is not None:
                self.__callBack(imudataArray, self.__imuoffset)

            # if not __name__ == "__main__":
            #     self.imudata_qt.emit(imudataArray, self.__imuoffset)
            # print(imudataArray)

        # end of while loop
    # End of memsImuReader::run


def myCallBack(imudata, imuoffset):
    global old
    new = time.perf_counter_ns()
    imuoffset["TIME"] = [0]
    imuoffset["PD_TEMP"] = [0]
    if int(myImu.isCali_w) == 0:
        imuoffset["NANO33_WX"] = [0]
        imuoffset["NANO33_WY"] = [0]
        imuoffset["NANO33_WZ"] = [0]
        imuoffset["PIG_ERR"] = [0]
    if int(myImu.isCali_a) == 0:
        imuoffset["ADXL_AX"] = [0]
        imuoffset["ADXL_AY"] = [0]
        imuoffset["ADXL_AZ"] = [0]
    imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
    # print(imudata)
    # wx = imudata["NANO33_W"][0]
    # wy = imudata["NANO33_W"][1]
    # wz = imudata["NANO33_W"][2]
    # ax = imudata["ADXL_A"][0]
    # ay = imudata["ADXL_A"][1]
    # az = imudata["ADXL_A"][2]
    # t = imudata["TIME"][0]
    # print("%.5f %.5f  %.5f  %.5f  %.5f  %.5f  %.5f" % (t, wx, wy, wz, ax, ay, az))
    print(imudata["TIME"], imudata["PIG_WZ"], imudata["ADXL_AZ"], imudata["PD_TEMP"])
    old = new


if __name__ == "__main__":
    ser = Connector()
    myImu = pigImuReader(boolCalia=sys.argv[1], boolCaliw=sys.argv[2], debug_en=False)
    myImu.arrayNum = 2
    myImu.setCallback(myCallBack)
    print("isCali:", myImu.isCali)
    myImu.connect(ser, "COM6", 230400)
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