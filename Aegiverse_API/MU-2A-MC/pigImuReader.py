""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

import serial
from serial import PortNotOpenError

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
    "TIME": np.zeros(1),
    "WX": np.zeros(1),
    "WY": np.zeros(1),
    "WZ": np.zeros(1),
    "AX": np.zeros(1),
    "AY": np.zeros(1),
    "AZ": np.zeros(1),
    "PD_TEMP_X": np.zeros(1),
    "PD_TEMP_Y": np.zeros(1),
    "PD_TEMP_Z": np.zeros(1),
    "PITCH": np.zeros(1),
    "ROLL": np.zeros(1),
    "YAW": np.zeros(1)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_ADXL355_AX = None
POS_NANO33_WX = None
SIZE_4 = 4
SIZE_12 = 12
SIZE_HEADER = 4
SIZE_NANO33 = 12
SIZE_FOG = 14
SIZE_MCUTIME = 4
POS_NANO33 = SIZE_HEADER
POS_WX = SIZE_HEADER
POS_WY = POS_WX + SIZE_4
POS_WZ = POS_WY + SIZE_4
# POS_A = POS_WZ + SIZE_12
POS_AX = POS_WZ + SIZE_4
POS_AY = POS_AX + SIZE_4
POS_AZ = POS_AY + SIZE_4
POS_TX = POS_AZ + SIZE_4
POS_TY = POS_TX + SIZE_4
POS_TZ = POS_TY + SIZE_4
POS_MCUTIME = POS_TZ + SIZE_4
POS_PITCH = POS_MCUTIME + SIZE_4
POS_ROLL = POS_PITCH + SIZE_4
POS_YAW = POS_ROLL + SIZE_4

POS_PIG = POS_NANO33 + SIZE_NANO33
old = time.perf_counter_ns()


class pigImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object)
        imuThreadStop_qt = pyqtSignal()
        buffer_qt = pyqtSignal(int)
        occur_err_qt = pyqtSignal(str)
        deviceReset_qt = pyqtSignal(bool)

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
        self.recording_device_reset_time = 0 # 紀錄是否重啟的狀況


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

    def writeImuCmd(self, cmd, value, fog_ch=2):  # GP1Z use 2, SP use 3
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
        self.flushInputBuffer()
        self.writeImuCmd(7, 2, 2)

    def stopIMU(self):
        self.writeImuCmd(7, 4, 2)
        cmn.wait_ms(100)
        # self.writeImuCmd(5, 4, 2)
        # cmn.wait_ms(100)
        # self.writeImuCmd(5, 4, 2)
        # cmn.wait_ms(100)
        # self.writeImuCmd(5, 4, 2)
        # cmn.wait_ms(100)
        # self.writeImuCmd(5, 4, 2)
        # cmn.wait_ms(100)
        # self.writeImuCmd(5, 4, 2)
        self.flushInputBuffer()

    def dump_fog_parameters(self, ch):
        # self.writeImuCmd(0x66, 2)
        return self.__Connector.dump_fog_parameters(ch)

    def getVersion(self, ch):
        # self.writeImuCmd(0x66, 2)
        return self.__Connector.getVersion(ch)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuData(self):
        try:
            head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
            dataPacket = getData.getdataPacket(self.__Connector, head, 56)
            if dataPacket == False:
                return False, False
            # print([hex(i) for i in dataPacket])
            TIME, WX, WY, WZ, AX, AY, AZ, TX, TY, TZ, PITCH, ROLL, YAW = cmn.readAFI_ATT_PDf(dataPacket, POS_WX, POS_WY,
                                                                                             POS_WZ, POS_AX, POS_AY,
                                                                                             POS_AZ, POS_MCUTIME,
                                                                                             POS_TX, POS_TY, POS_TZ,
                                                                                             POS_PITCH, POS_ROLL,
                                                                                             POS_YAW, SIZE_4, PRINT=1)

            if self.isKal:
                # WX = self.pig_wz_kal.update(WX)
                # WY = self.pig_wz_kal.update(WY)
                WZ = self.pig_wz_kal.update(WZ)
                # AX = self.pig_wz_kal.update(AX)
                # AY = self.pig_wz_kal.update(AY)
                # AZ = self.pig_wz_kal.update(AZ)

            imudata = {"TIME": TIME,
                       "WX": WX, "WY": WY, "WZ": WZ,
                       "AX": AX, "AY": AY, "AZ": AZ,
                       "PD_TEMP_X": TX, "PD_TEMP_Y": TY, "PD_TEMP_Z": TZ,
                       "PITCH": PITCH, "ROLL": ROLL, "YAW": YAW
                       }
            return dataPacket, imudata
        except IndexError as IdxErr:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'IndexError — The index position has exceeded the range of the list.(An error occurred during the data retrieval process, line {__lineNum}.)')
            errStr = "An error occurred during the data retrieval process, IndexError.\n Please check the issue where the error occurred, thank you.\n" \
                     "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
            self.isRun = False
            self.occur_err_qt.emit(errStr)
            return False, False
        except TypeError as typeErr:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'TypeError — {typeErr}.(An error occurred during the data retrieval process, line {__lineNum}.)')
            errStr = "An error occurred during the data retrieval process, TypeError.\n Please check the issue where the error occurred, thank you.\n" \
                     "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
            self.isRun = False
            self.occur_err_qt.emit(errStr)
            return False, False
        except ValueError as ValErr:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'ValueError — {ValErr}.(An error occurred during the data retrieval process, line {__lineNum}.)')
            errStr = "An error occurred during the data retrieval process, ValueError.\n Please check the issue where the error occurred, thank you.\n" \
                     "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
            self.isRun = False
            self.occur_err_qt.emit(errStr)
            return False, False
        except Exception as e:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'Exception — {e}.(An error occurred during the data retrieval process, line {__lineNum}.)')
            ExceptionType = type(e)
            errStr = f"An error occurred during the data retrieval process, {ExceptionType}.\n Please check the issue where the error occurred, thank you.\n" \
                     "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
            self.isRun = False
            self.occur_err_qt.emit(errStr)
            return False, False


    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def flushInputBuffer(self):
        try:
            print('buf before:', self.readInputBuffer())
            self.__Connector.flushInputBuffer()
            print('buf after:', self.readInputBuffer())
        except serial.serialutil.SerialException as err:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'SerialException — {err}.(The error occurred while clearing buffer, line {__lineNum}.)')
            errStr = "An error occurred during reset Buffer.\n Please check the issue where the error occurred, thank you.\n" \
                     "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
            self.occur_err_qt.emit(errStr)

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

    def judgment_Reset(self):
        if self.recording_device_reset_time == 0:
            self.recording_device_reset_time = time.perf_counter()
        else:
            now_time = time.perf_counter()
            if (now_time - self.recording_device_reset_time) > 15:
                self.recording_device_reset_time = time.perf_counter()
                self.deviceReset_qt.emit(True)
                print("自動重啟")
            else:
                self.recording_device_reset_time = time.perf_counter()


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
                self.judgment_Reset()
                try:
                    input_buf = self.readInputBuffer()
                    self.buffer_qt.emit(input_buf)
                    # while self.__Connector.readInputBuffer() < self.arrayNum * 10:
                    while not self.__Connector.readInputBuffer():
                        # print(self.__Connector.readInputBuffer())
                        # print("No input data!")
                        # cmn.wait_ms(500)
                        pass
                except PortNotOpenError as e:
                    __excType, __excObj, __excTb = sys.exc_info()
                    __lineNum = __excTb.tb_lineno
                    logger.error(
                        f'PortNotOpenError — {e}.(An error occurred during the data retrieval process, line {__lineNum}.)')
                    errStr = f"An error occurred during the data retrieval process.\n Please check the issue where the error occurred, thank you.\n" \
                             "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
                    self.isRun = False
                    # self.stopIMU()
                    # self.imuThreadStop_qt.emit()
                    self.occur_err_qt.emit(errStr)
                    break
                except serial.serialutil.SerialException as e:  # 沒開電狀況下會出錯
                    __excType, __excObj, __excTb = sys.exc_info()
                    __lineNum = __excTb.tb_lineno
                    logger.error(f'SerialException — {e}.(An error occurred during the data retrieval process, line {__lineNum}.)')
                    errStr = "An error occurred during the data retrieval process, SerialException.\n Please check the issue where the error occurred, thank you.\n" \
                             "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
                    self.isRun = False
                    # self.stopIMU()
                    # self.imuThreadStop_qt.emit()
                    self.occur_err_qt.emit(errStr)
                    break
                t1 = time.perf_counter()

                dataPacket, imudata = self.getImuData()
                if dataPacket == False and imudata == False:
                    self.isRun = False
                    __errStr = "An error occurred during the data retrieval process.\n Please check the issue where the error occurred, thank you.\n" \
                               "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
                    self.occur_err_qt.emit(__errStr)
                    break
                # print(len(dataPacket))
                t2 = time.perf_counter()

                try:
                    isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                    t3 = time.perf_counter()
                    # err correction
                    imudata = crcLib.errCorrection(isCrcFail, imudata)
                    # end of err correction
                    t4 = time.perf_counter()
                    # print('isCrcFail: ', isCrcFail)
                    if isCrcFail is False:
                        imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
                        imudataArray["WX"] = np.append(imudataArray["WX"], imudata["WX"])
                        imudataArray["WY"] = np.append(imudataArray["WY"], imudata["WY"])
                        imudataArray["WZ"] = np.append(imudataArray["WZ"], imudata["WZ"])
                        imudataArray["AX"] = np.append(imudataArray["AX"], imudata["AX"])
                        imudataArray["AY"] = np.append(imudataArray["AY"], imudata["AY"])
                        imudataArray["AZ"] = np.append(imudataArray["AZ"], imudata["AZ"])
                        imudataArray["PD_TEMP_X"] = np.append(imudataArray["PD_TEMP_X"], imudata["PD_TEMP_X"])
                        imudataArray["PD_TEMP_Y"] = np.append(imudataArray["PD_TEMP_Y"], imudata["PD_TEMP_Y"])
                        imudataArray["PD_TEMP_Z"] = np.append(imudataArray["PD_TEMP_Z"], imudata["PD_TEMP_Z"])
                    t5 = time.perf_counter()

                    debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                                 + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                                 + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                    cmn.print_debug(debug_info, self.__debug)
                except TypeError as TypeErr:
                    __excType, __excObj, __excTb = sys.exc_info()
                    __lineNum = __excTb.tb_lineno
                    logger.error(f'TypeError — {TypeErr}.(The main retrieval of the data  portion, line {__lineNum}.)')
                    errStr = "An error occurred during the data retrieval process, TypeError.\n Please check the issue where the error occurred, thank you.\n" \
                             "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
                    self.isRun = False
                    # self.stopIMU()
                    self.occur_err_qt.emit(errStr)
                    break
                except Exception as e:
                    logger.error(f'Exception — {e}.(The main retrieval of the data  portion, line {__lineNum}.)')
                    errStr = "An error occurred during the data retrieval process.\n Please check the issue where the error occurred, thank you.\n" \
                             "And please take a screenshot of the error message for further troubleshooting by the responsible party.\n Thank you for your cooperation."
                    self.isRun = False
                    # self.stopIMU()
                    self.occur_err_qt.emit(errStr)
            # end of for loop

            if not self.isRun:
                print('run flag is false')
                self.stopIMU()
                self.imuThreadStop_qt.emit()
                break
            # imudataArray["TIME"] = imudataArray["TIME"] - t0

            self.offset_setting(self.__imuoffset)
            # imudataArray = cmn.dictOperation(imudataArray, self.__imuoffset, "SUB", IMU_DATA_STRUCTURE)
            if self.__callBack is not None:
                self.__callBack(imudataArray)

            if not __name__ == "__main__":
                if len(imudataArray["PD_TEMP_Z"]) != 0:
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
    myImu.connect(ser, "COM27", 230400)
    # para = myImu.dump_fog_parameters(1)
    # print(para)
    # print(para["FREQ"])
    # print(para["SF0"])
    myImu.readIMU()
    myImu.isRun = True
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
