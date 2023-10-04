""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys
import logging

sys.path.append("../")
from myLib.mySerial.Connector import Connector
from myLib.mySerial import getData
from myLib.crcCalculator import crcLib
from myLib.myFilter import filter
import time
from PyQt5.QtCore import QThread, pyqtSignal
from myLib import common as cmn
import numpy as np
import logging

# from pig_parameters import *

IMU_DATA_STRUCTURE = {
    "PIG_ERR": np.zeros(1),
    "PIG_WZ": np.zeros(1),
    "PD_TEMP": np.zeros(1),
    "TIME": np.zeros(1),
    "HEADING": np.zeros(1)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_ADXL355_AX = None
POS_NANO33_WX = None
POS_PIG = 4
POS_TIME = 18
old = time.perf_counter_ns()


class pigImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object)
        imuThreadStop_qt = pyqtSignal()
        buffer_qt = pyqtSignal(int)

    def __init__(self, portName: str = "None", boolCaliw=False, boolCalia=False, baudRate: int = 230400,
                 debug_en: bool = 0):
        super(pigImuReader, self).__init__()
        self.pig_err_kal = filter.kalman_1D()
        self.pig_wz_kal = filter.kalman_1D()
        self.__isCali_a = boolCalia
        self.__isCali_w = boolCaliw
        self.sf_a = 1
        self.sf_b = 0
        self.isKal = False
        self.kal_Q = 1
        self.kal_R = 1
        self.isCali = (self.isCali_w or self.isCali_a)
        self.__Connector = None
        self.__portName = portName
        self.__baudRate = baudRate
        self.__isRun = True
        # self.__isCali = False
        self.__callBack = None
        self.__crcFail = 0
        self.arrayNum = 10
        self.__debug = debug_en
        self.__old_imudata = {k: (-1,) * len(IMU_DATA_STRUCTURE.get(k)) for k in set(IMU_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(1) for k in set(IMU_DATA_STRUCTURE)}
        # print(not __name__ == "__main__")

    # class constructor

    def __del__(self):
        logger.info("class memsImuReader's destructor called!")

    # End of destructor

    @property
    def sf_a(self):
        return self.__sf_a

    @sf_a.setter
    def sf_a(self, value):
        self.__sf_a = value
        print("act.sf_a: ", self.sf_a)

    @property
    def sf_b(self):
        return self.__sf_b

    @sf_b.setter
    def sf_b(self, value):
        self.__sf_b = value
        # print("act.sf_b: ", self.__sf_b)

    @property
    def isKal(self):
        return self.__isKal

    @isKal.setter
    def isKal(self, en):
        self.__isKal = en
        # logger.info("act.isKal: ", self.isKal)

    @property
    def kal_Q(self):
        return self.__kal_Q

    @kal_Q.setter
    def kal_Q(self, Q):
        self.__kal_Q = Q
        self.pig_err_kal.kal_Q = self.kal_Q
        self.pig_wz_kal.kal_Q = self.kal_Q

    @property
    def kal_R(self):
        return self.__kal_R

    @kal_R.setter
    def kal_R(self, R):
        self.__kal_R = R
        self.pig_err_kal.kal_R = self.kal_R
        self.pig_wz_kal.kal_R = self.kal_R

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
        # print("self.__isCali: ", self.__isCali)

    # End of ImuReader::isCali(setter)

    @property
    def isCali_w(self):
        return self.__isCali_w

    # End of memsImuReader::isCali_w(getter)

    @isCali_w.setter
    def isCali_w(self, isFlag):
        self.__isCali_w = bool(int(isFlag))
        self.isCali = (self.isCali_w or self.isCali_a)

    # End of ImuReader::isCali_w(setter)

    @property
    def isCali_a(self):
        return self.__isCali_a

    # End of memsImuReader::isCali_a(getter)

    @isCali_a.setter
    def isCali_a(self, isFlag):
        self.__isCali_a = bool(int(isFlag))
        self.isCali = (self.isCali_w or self.isCali_a)

    # End of ImuReader::isCali_a(setter)

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

    def writeImuCmd(self, cmd, value, fog_ch=2): #GP1Z use 2, SP use 3
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF), fog_ch])
        # print(cmd, end=', ')
        # print([i for i in data])
        self.__Connector.write(bytearray([0xAB, 0xBA]))
        self.__Connector.write(data)
        self.__Connector.write(bytearray([0x55, 0x56]))
        cmn.wait_ms(150)

    # End of memsImuReader::writeImuCmd

    def readIMU(self):
        print('read')
        self.writeImuCmd(1, 2, 2)

    def stopIMU(self):
        self.writeImuCmd(1, 4, 2)

    def dump_fog_parameters(self, ch):
        # self.writeImuCmd(0x66, 2)
        return self.__Connector.dump_fog_parameters(ch)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuData(self):
        dataPacket = getData.getNMEAdataPacket(self.__Connector)
        dataPacket, heading, checkSum = cmn.readNMEA(dataPacket, EN=1, PRINT=0)

        # if not self.isCali:
        #     if self.isKal:
        #         ERR = self.pig_err_kal.update(ERR)
        #         STEP = self.pig_wz_kal.update(STEP)

        # t = time.perf_counter()
        # t = FPGA_TIME
        imudata = {"HEADING": heading}
        return dataPacket, imudata, checkSum

    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def do_cali(self, dictContainer, cali_times):
        if self.isCali:
            temp = {k: np.zeros(1) for k in set(IMU_DATA_STRUCTURE)}
            print("---calibrating offset start-----")
            for i in range(cali_times):
                dataPacket, imudata = self.getImuData()
                temp = cmn.dictOperation(temp, imudata, "ADD", IMU_DATA_STRUCTURE)
            temp = {k: temp.get(k) / cali_times for k in set(self.__imuoffset)}
            print("---calibrating offset stop-----")
            self.isCali = False
            return temp
        else:
            return dictContainer

    def run(self):
        logging.basicConfig(level=100)
        t0 = time.perf_counter()
        while True:
            if not self.isRun:
                print('run flag is false')
                self.stopIMU()
                self.imuThreadStop_qt.emit()
                break
            # End of if-condition

            # self.__imuoffset = self.do_cali(self.__imuoffset, 100)

            imudataArray = {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

            for i in range(self.arrayNum):
                input_buf = self.readInputBuffer()
                self.buffer_qt.emit(input_buf)
                # while self.__Connector.readInputBuffer() < self.arrayNum * 10:
                while not self.__Connector.readInputBuffer():
                    # print(self.__Connector.readInputBuffer())
                    # print("No input data!")
                    # cmn.wait_ms(500)
                    pass
                t1 = time.perf_counter()

                dataPacket, imudata, checkSum = self.getImuData()

                t2 = time.perf_counter()
                # isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                isCrcFail = crcLib.isNmeaCheckSumFail(dataPacket, checkSum)
                t3 = time.perf_counter()
                # err correction
                imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction
                t4 = time.perf_counter()
                # print(imudata)
                # imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
                # imudataArray["PIG_ERR"] = np.append(imudataArray["PIG_ERR"], imudata["PIG_ERR"])
                # imudataArray["PIG_WZ"] = np.append(imudataArray["PIG_WZ"], imudata["PIG_WZ"])
                # imudataArray["PD_TEMP"] = np.append(imudataArray["PD_TEMP"], imudata["PD_TEMP"])
                imudataArray["HEADING"] = np.append(imudataArray["HEADING"], imudata["HEADING"])
                t5 = time.perf_counter()

                debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                             + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                             + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)

            # end of for loop

            # imudataArray["TIME"] = imudataArray["TIME"] - t0

            # self.offset_setting(self.__imuoffset)
            # imudataArray = cmn.dictOperation(imudataArray, self.__imuoffset, "SUB", IMU_DATA_STRUCTURE)
            if self.__callBack is not None:
                self.__callBack(imudataArray)

            if not __name__ == "__main__":
                self.imudata_qt.emit(imudataArray)
            # print(imudataArray)

        # end of while loop

    # End of memsImuReader::run

    def offset_setting(self, imuoffset):
        imuoffset["TIME"] = [0]
        imuoffset["PD_TEMP"] = [0]
        imuoffset["PIG_ERR"] = [0]
        imuoffset["PIG_WZ"] = [0]
        if not self.isCali_w:
            imuoffset["PIG_ERR"] = [0]
            imuoffset["PIG_WZ"] = [0]
        if not self.isCali_a:
            pass




def myCallBack(imudata):
    global old
    new = time.perf_counter_ns()
    old = new


if __name__ == "__main__":
    ser = Connector()
    myImu = pigImuReader(debug_en=False)
    myImu.arrayNum = 2
    myImu.setCallback(myCallBack)
    myImu.isCali = False
    myImu.connect(ser, "COM8", 115200)
    para = myImu.dump_fog_parameters(1)
    print(para)
    print(para["FREQ"])
    print(para["SF0"])
    # myImu.readIMU()
    # myImu.isRun = True
    # myImu.start()
    # try:
    #     while True:
    #         time.sleep(.1)
    # except KeyboardInterrupt:
    #     myImu.isRun = False
    #     myImu.stopIMU()
    #     myImu.disconnect()
    #     myImu.wait()
    #     print('KeyboardInterrupt success')
