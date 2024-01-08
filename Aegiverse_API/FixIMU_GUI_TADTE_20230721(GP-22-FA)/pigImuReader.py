""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
from datetime import datetime

from PyQt5.QtWidgets import QApplication

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
from myLib.myGui.pig_parameters_widget import CMD_FOG_TIMER_RST
import time
from PyQt5.QtCore import QThread, pyqtSignal
from myLib import common as cmn
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
    "TIME": np.zeros(1),
    "YEAR": np.zeros(1),
    "MON": np.zeros(1),
    "DAY": np.zeros(1),
    "HOUR": np.zeros(1),
    "MIN": np.zeros(1),
    "SEC": np.zeros(1),
    "mSEC": np.zeros(1)
}

Posture_DATA_STRUCTURE = {
    "xMEMS": np.zeros(1),
    "yMEMS": np.zeros(1),
    "xFOG": np.zeros(1),
    "yFOG": np.zeros(1),
    "xTrue": np.zeros(1),
    "yTrue": np.zeros(1)
}

ChangeVersion_DATA_STRUCTURE = {
    "TIME": np.zeros(1),
    "WX": np.zeros(1),
    "WY": np.zeros(1),
    "WZ": np.zeros(1),
    "AX": np.zeros(1),
    "AY": np.zeros(1),
    "AZ": np.zeros(1),
    "PD_TEMP_X": np.zeros(1),
    "PD_TEMP_Y": np.zeros(1),
    "PD_TEMP_Z": np.zeros(1)
}

VBOX_DATA_STRUCTURE_MAIN = {
    "GPS": np.zeros(1),
    "GLONASS": np.zeros(1),
    "BeiDou": np.zeros(1),
    "VBOXTime": np.zeros(1),
    "Latitude": np.zeros(1),
    "Longitude": np.zeros(1),
    "Velocity": np.zeros(1),
    'Heading': np.zeros(1),
    'Altitude': np.zeros(1),
    'Vertical_Vel': np.zeros(1),
    "Pitch_KF": np.zeros(1),
    "Roll_KF": np.zeros(1),
    "Heading_KF": np.zeros(1),
    "Pitch_rate": np.zeros(1),
    "Roll_rate": np.zeros(1),
    "Yaw_rate": np.zeros(1),
    "Acc_X": np.zeros(1),
    "Acc_Y": np.zeros(1),
    "Acc_Z": np.zeros(1),
    "Date": np.zeros(1),
    "KF_Status": np.zeros(1),
    "Pos_Quality": np.zeros(1),
    'Vel_Quality': np.zeros(1),
    "Heading2_KF": np.zeros(1)
}

VBOX_Time_DATA_STRUCTURE_MAIN = {
    "Velocity": np.zeros(1),
    'Vertical_Vel': np.zeros(1),
    "Latitude": np.zeros(1),
    "Longitude": np.zeros(1)
}

KVH_DATA_STRUCTURE_MANI = {
    "kvh_wx": np.zeros(1),
    "kvh_wy": np.zeros(1),
    "kvh_wz": np.zeros(1),
    "kvh_ax": np.zeros(1),
    "kvh_ay": np.zeros(1),
    "kvh_az": np.zeros(1),
    "kvh_status": np.zeros(1),
    'kvh_seq_num': np.zeros(1),
    'kvh_Temperature': np.zeros(1)
}

Integration_DATA_STRUCTURE = {
    "TIME": np.zeros(1),
    "WX": np.zeros(1),
    "WY": np.zeros(1),
    "WZ": np.zeros(1),
    "AX": np.zeros(1),
    "AY": np.zeros(1),
    "AZ": np.zeros(1),
    "PD_TEMP": np.zeros(1),
    "GPS": np.zeros(1),
    "GLONASS": np.zeros(1),
    "BeiDou": np.zeros(1),
    "Time": np.zeros(1),
    "Latitude": np.zeros(1),
    "Longitude": np.zeros(1),
    "Velocity": np.zeros(1),
    'Heading': np.zeros(1),
    'Altitude': np.zeros(1),
    'Vertical_Vel': np.zeros(1),
    "Pitch_KF": np.zeros(1),
    "Roll_KF": np.zeros(1),
    "Heading_KF": np.zeros(1),
    "Pitch_rate": np.zeros(1),
    "Roll_rate": np.zeros(1),
    "Yaw_rate": np.zeros(1),
    "Acc_X": np.zeros(1),
    "Acc_Y": np.zeros(1),
    "Acc_Z": np.zeros(1),
    "Date": np.zeros(1),
    "KF_Status": np.zeros(1),
    "Pos_Quality": np.zeros(1),
    'Vel_Quality': np.zeros(1),
    "Heading2_KF": np.zeros(1)
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
POS_A = POS_WZ + SIZE_4
POS_TX = POS_A + SIZE_12
POS_TY = POS_TX + SIZE_4
POS_TZ = POS_TY + SIZE_4
POS_MCUTIME = POS_TZ + SIZE_4

POS_PIG = POS_NANO33 + SIZE_NANO33
old = time.perf_counter_ns()


class pigImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object)
        imuThreadStop_qt = pyqtSignal()
        buffer_qt = pyqtSignal(int)
        Portstatus_qt = pyqtSignal(bool)
        deviceReset_qt = pyqtSignal(bool)
        imuPosture_qt = pyqtSignal(object)
        # # 即時軌跡
        # realTImePointqt_signal = pyqtSignal(object, object)


    def __init__(self, portName: str = "None", boolCaliw=False, boolCalia=False, baudRate: int = 230400,
                 debug_en: bool = 0):
        super(pigImuReader, self).__init__()
        # self.__first_run_flag = False
        self.time_pass_flag = False
        self.__isExtMode = False
        self.time_pass_cnt = 5
        self.first_run_flag = True
        self.pass_flag = False
        self.pig_err_kal = filter.kalman_1D()
        self.pig_wz_kal = filter.kalman_1D()
        self.pig_wx_kal = filter.kalman_1D()
        self.pig_wy_kal = filter.kalman_1D()
        self.pig_az_kal = filter.kalman_1D()
        self.pig_ax_kal = filter.kalman_1D()
        self.pig_ay_kal = filter.kalman_1D()
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
        self.start_read = 0
        self.__dataRate = 1  # 1秒會傳輸的資料筆數
        self.first_sec = 0  # 20230607 添加
        self.record_sec = 0  # 記錄秒
        self.record_hh = 0  # 紀錄小時
        self.first_sec_has_passed = 0  # 20230712 判斷開始的第一秒是否已經過了
        self.current_time = 0
        self.__current_sec = 0
        self.__debug = debug_en
        self.__old_imudata = {k: (-1,) * len(ChangeVersion_DATA_STRUCTURE.get(k)) for k in set(ChangeVersion_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(1) for k in set(ChangeVersion_DATA_STRUCTURE)}
        # print(not __name__ == "__main__")
        self.__recording_device_reset_time = 0
        self.__time_accumulate = 0
        self.TabNum = 0



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
        self.pig_wx_kal.kal_Q = self.kal_Q
        self.pig_wy_kal.kal_Q = self.kal_Q
        self.pig_az_kal.kal_Q = self.kal_Q
        self.pig_ax_kal.kal_Q = self.kal_Q
        self.pig_ay_kal.kal_Q = self.kal_Q

    @property
    def kal_R(self):
        return self.__kal_R

    @kal_R.setter
    def kal_R(self, R):
        self.__kal_R = R
        self.pig_err_kal.kal_R = self.kal_R
        self.pig_wz_kal.kal_R = self.kal_R
        self.pig_wx_kal.kal_R = self.kal_R
        self.pig_wy_kal.kal_R = self.kal_R
        self.pig_az_kal.kal_R = self.kal_R
        self.pig_ax_kal.kal_R = self.kal_R
        self.pig_ay_kal.kal_R = self.kal_R

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

    @property
    def isExtMode(self):
        return self.__isExtMode

    # End of memsImuReader::isCali_a(getter)

    @isExtMode.setter
    def isExtMode(self, setValue):
        self.__isExtMode = setValue

    # End of ImuReader::isCali_a(setter)

    @property
    def first_run_flag(self):
        return self.__first_run_flag

    @first_run_flag.setter
    def first_run_flag(self, flag):
        self.__first_run_flag = flag

    @property
    def time_pass_flag(self):
        return self.__time_pass_flag

    @time_pass_flag.setter
    def time_pass_flag(self, flag):
        self.__time_pass_flag = flag

    @property
    def time_pass_cnt(self):
        return self.__time_pass_cnt

    @time_pass_cnt.setter
    def time_pass_cnt(self, cnt):
        self.__time_pass_cnt = cnt

    @property
    def time_accumulate(self):
        return self.__time_accumulate

    @time_accumulate.setter
    def time_accumulate(self, val):
        self.__time_accumulate = val

    def writeImuCmd(self, cmd, value, fog_ch=2):
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

    def connect(self, port, portName, baudRate):
        self.__Connector = port
        port.portName = portName
        port.baudRate = baudRate
        is_open = self.__Connector.connect()
        if is_open == False:
            self.get_Port_connect_status()
        return is_open

    # End of memsImuReader::connectIMU

    def disconnect(self):
        is_open = self.__Connector.disconnect()
        return is_open

    # End of memsImuReader::disconnectIMU

    def readIMU(self):
        self.flushInputBuffer()
        self.writeImuCmd(5, 2, 2)
        # self.flushInputBuffer()
        # self.writeImuCmd(2, 2, 2)

    def stopIMU(self):
        self.writeImuCmd(5, 4, 2)
        cmn.wait_ms(100)
        self.writeImuCmd(5, 4, 2)
        cmn.wait_ms(100)
        self.writeImuCmd(5, 4, 2)
        cmn.wait_ms(100)
        self.writeImuCmd(5, 4, 2)
        cmn.wait_ms(100)
        self.writeImuCmd(5, 4, 2)
        cmn.wait_ms(100)
        self.writeImuCmd(5, 4, 2)
        self.flushInputBuffer()
        # self.writeImuCmd(2, 4, 2)

    def dump_fog_parameters(self, ch):
        # self.writeImuCmd(0x66, 2)
        return self.__Connector.dump_fog_parameters(ch)

    def dump_cali_parameters(self, ch):
        return self.__Connector.dump_cali_parameters(ch)

    def getVersion(self, ch):
        # self.writeImuCmd(0x66, 2)
        return self.__Connector.getVersion(ch)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def calculateDataTime(self):
        currentDataAndTime = datetime.now()
        year = currentDataAndTime.year
        mon = currentDataAndTime.month
        day = currentDataAndTime.day
        hour = currentDataAndTime.hour
        min = currentDataAndTime.minute
        sec = currentDataAndTime.second

        if (self.start_read == 0):
            '''PC Time'''
            msec = int(currentDataAndTime.microsecond * 1e-3)
            '''end of PC time'''
            self.current_time = msec
            self.start_read = 1
            # self.__datacnt = msec/10
            self.first_sec = sec
            self.data_num = ((1000 - msec) * 1e-3) * 101  # (剩下秒數 大約會傳輸筆數)
            self.first_msec = msec
        else:
            self.current_time = self.current_time + (
                        (1000 - self.first_msec) / self.data_num)  # 用剩下秒數除以大約有幾筆資料，換算每一筆的間隔時間
            if sec != self.first_sec:
                self.current_time = self.current_time % 10
                # self.first_sec_change = True
                self.first_sec = sec

        if self.current_time >= 1000:
            self.current_time = self.current_time - 1000
        # print("sec:" + str(sec))
        # print("read get data:" + str(self.current_time))
        return year, mon, day, hour, min, sec

    def getImuData(self):
        try:
            head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
            if head == 1:  # 當head撈取不到時，會執行此功能，代表COM Port可能被拔掉了
                self.__Connector.portDoNotConnectStatus = True
                self.get_Port_connect_status()
                return head, {}
            else:
                dataPacket = getData.getdataPacket(self.__Connector, head, 44)
                if dataPacket == head:  # 當dataPacket撈取不到時，就會執行此功能，代表COM Port可能被拔掉了(撈取不到值)
                    self.get_Port_connect_status()

            # print([hex(x) for x in dataPacket])
            TIME, WX, WY, WZ, AX, AY, AZ, TX, TY, TZ = cmn.readAFI(dataPacket, POS_WX, POS_WY, POS_WZ, POS_A,
                                                                   POS_MCUTIME,
                                                                   POS_TX, POS_TY, POS_TZ, SIZE_4, PRINT=0)

            if self.isKal:
                WX = self.pig_wx_kal.update(WX)
                WY = self.pig_wy_kal.update(WY)
                WZ = self.pig_wz_kal.update(WZ)
                AX = self.pig_ax_kal.update(AX)
                AY = self.pig_ay_kal.update(AY)
                AZ = self.pig_az_kal.update(AZ)

            # t = time.perf_counter()
            imudata = {"TIME": TIME,
                       "WX": WX, "WY": WY, "WZ": WZ,
                       "AX": AX, "AY": AY, "AZ": AZ,
                       "PD_TEMP_X": TX, "PD_TEMP_Y": TY, "PD_TEMP_Z": TZ}
            return dataPacket, imudata
        except Exception as e:
            print(e)

    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def flushInputBuffer(self):
        print('buf before:', self.readInputBuffer())
        self.__Connector.flushInputBuffer()
        print('buf after:', self.readInputBuffer())

    def do_cali(self, dictContainer, cali_times):
        try:
            if self.isCali:
                print('do_cali')
                temp = {k: np.zeros(1) for k in set(ChangeVersion_DATA_STRUCTURE)}
                print("---calibrating offset start-----")
                for i in range(cali_times):
                    dataPacket, imudata = self.getImuData()
                    temp = cmn.dictOperation(temp, imudata, "ADD", ChangeVersion_DATA_STRUCTURE)
                temp = {k: temp.get(k) / cali_times for k in set(self.__imuoffset)}
                print("---calibrating offset stop-----")
                self.isCali = False
                return temp
        except Exception as e:
            logger.error("錯誤的原因: %s" % e)
            return None
        else:
            return dictContainer

    def time_pass_check(self, isPass, time_in):
        if not isPass:
            if time_in < 0.8:
                self.time_pass_flag = True

    def get_Port_connect_status(self):  # 判斷USB線被拔除或是沒有電的狀況下
        self.__PortStatus = self.__Connector.portDoNotConnectStatus
        if self.__PortStatus == 1:
            self.isRun = False
            self.Portstatus_qt.emit(False)

    def judgment_Reset(self, t):
        if self.__recording_device_reset_time == 0:
            self.__recording_device_reset_time = time.perf_counter()
        else:
            now_time = time.perf_counter()
            if (now_time - self.__recording_device_reset_time) > 3:
                self.__recording_device_reset_time = time.perf_counter()
                timeList = self.SecConvertToHourMinute(t)
                self.deviceReset_qt.emit(timeList)
            else:
                self.__recording_device_reset_time = time.perf_counter()

    def SecConvertToHourMinute(self, t):
        Sec = 0
        Min = 0
        Hour = 0
        Min_quotient, Sec = divmod(t , 60)
        if Min_quotient != 0:
            Hour, Min = divmod(Min_quotient, 60)

        TimeList = [Sec, Min, Hour]
        return  TimeList

    @property
    def recording_device_reset_time(self):
        return self.__recording_device_reset_time

    @recording_device_reset_time.setter
    def recording_device_reset_time(self, T):
        self.__recording_device_reset_time = T


    def run(self):
        if self.TabNum == 0:
            currentDataSec = 0
            try:
                self.__Connector.portDoNotConnectStatus = False
                logging.basicConfig(level=100)
                t0 = time.perf_counter()
                while True:
                    # 判斷儀器是否自己重新reset
                    self.judgment_Reset(currentDataSec)
                    if not self.isRun:
                        self.stopIMU()
                        self.imuThreadStop_qt.emit()
                        # self.first_run_flag = True
                        break
                    # End of if-condition

                    # self.__imuoffset = self.do_cali(self.__imuoffset, 100)
                    # if self.__imuoffset == None:
                    #     self.__Connector.portDoNotConnectStatus = True
                    #     self.get_Port_connect_status()

                    imudataArray = {k: np.empty(0) for k in set(ChangeVersion_DATA_STRUCTURE)}

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

                        dataPacket, imudata = self.getImuData()
                        if not self.isRun:
                            self.stopIMU()
                            self.imuThreadStop_qt.emit()
                            # self.first_run_flag = True
                            break

                        if i == 0:
                            currentDataSec = int(imudata["TIME"])
                        t2 = time.perf_counter()
                        isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                        t3 = time.perf_counter()
                        # err correction
                        imudata = crcLib.errCorrection(isCrcFail, imudata)
                        # end of err correction
                        t4 = time.perf_counter()
                        # print(imudata)
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

                    # end of for loop

                    # imudataArray["TIME"] = imudataArray["TIME"] - t0

                    # self.offset_setting(self.__imuoffset)
                    # imudataArray = cmn.dictOperation(imudataArray, self.__imuoffset, "SUB", IMU_DATA_STRUCTURE)
                    if self.__callBack is not None:
                        self.__callBack(imudataArray)

                    if not __name__ == "__main__":
                        if np.any(imudataArray["TIME"]):
                            #print(imudataArray)
                            self.imudata_qt.emit(imudataArray)
            except Exception as e:
                print(e)
                    # print(imudataArray["PIG_WZ"])

                    # if self.first_run_flag or (imudata['TIME'] > 2):
                    #         print('in act reset timer!')
                    #         self.writeImuCmd(CMD_FOG_TIMER_RST, 1)
                    # else:
                    #     print('in act pass!')
                    #     self.imudata_qt.emit(imudataArray)
                    # elif (not self.first_run_flag) or (not (imudata['TIME'] > 2)):
                    #     self.imudata_qt.emit(imudataArray)

                # print(imudataArray)

            # end of while loop

        # End of memsImuReader::run
        else:
            self.postureStart()

    def postureStart(self):
        self.__Connector.portDoNotConnectStatus = False
        logging.basicConfig(level=100)
        t0 = time.perf_counter()
        while True:
            # 判斷儀器是否自己重新reset
            self.judgment_Reset()
            if not self.isRun:
                self.stopIMU()
                self.imuThreadStop_qt.emit()
                # self.first_run_flag = True
                print("Stop")
                break
            # End of if-condition

            self.__imuoffset = self.do_cali(self.__imuoffset, 100)
            if self.__imuoffset == None:  # 當calibration開啟之後，需要做此判斷
                self.__Connector.portDoNotConnectStatus = True
                self.get_Port_connect_status()

            postureDataArray = {k: np.empty(0) for k in set(ChangeVersion_DATA_STRUCTURE)}

            self.get_Port_connect_status()
            t1 = time.perf_counter()

            dataPacket, imudata = self.getImuData()
            if not self.isRun:
                self.stopIMU()
                self.imuThreadStop_qt.emit()
                    # self.first_run_flag = True
                print("Stop")
                break
            t2 = time.perf_counter()
            isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
            t3 = time.perf_counter()
                # err correction
            imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction
            t4 = time.perf_counter()
            postureDataArray["TIME"] = np.append(postureDataArray["TIME"], imudata["TIME"])
            postureDataArray["AX"] = np.append(postureDataArray["AX"], imudata["AX"])
            postureDataArray["AY"] = np.append(postureDataArray["AY"], imudata["AY"])
            postureDataArray["AZ"] = np.append(postureDataArray["AZ"], imudata["AZ"])
            postureDataArray["WX"] = np.append(postureDataArray["WX"], imudata["WX"])
            postureDataArray["WY"] = np.append(postureDataArray["WY"], imudata["WY"])
            postureDataArray["WZ"] = np.append(postureDataArray["WZ"], imudata["WZ"])
            postureDataArray["PD_TEMP"] = np.append(postureDataArray["PD_TEMP"], imudata["PD_TEMP"])

            t5 = time.perf_counter()

            if not self.isRun:
                self.stopIMU()
                self.imuThreadStop_qt.emit()
                # self.first_run_flag = True
                print("Stop")
                break
                
            self.offset_setting(self.__imuoffset)
            postureDataArray = cmn.dictOperation(postureDataArray, self.__imuoffset, "SUB", ChangeVersion_DATA_STRUCTURE)
            if self.__callBack is not None:
                self.__callBack(postureDataArray)

            if not __name__ == "__main__":
                self.imuPosture_qt.emit(postureDataArray)
        # end of while loop

    # End of memsImuReader::run


    def offset_setting(self, imuoffset):
        imuoffset["TIME"] = [0]
        imuoffset["PD_TEMP"] = [0]
        imuoffset["YEAR"] = [0]
        imuoffset["MON"] = [0]
        imuoffset["DAY"] = [0]
        imuoffset["HOUR"] = [0]
        imuoffset["MIN"] = [0]
        imuoffset["SEC"] = [0]
        imuoffset["mSEC"] = [0]
        if not self.isCali_w:
            imuoffset["NANO33_WX"] = [0]
            imuoffset["NANO33_WY"] = [0]
            imuoffset["NANO33_WZ"] = [0]
            imuoffset["PIG_ERR"] = [0]
            imuoffset["PIG_WZ"] = [0]
        if not self.isCali_a:
            imuoffset["ADXL_AX"] = [0]
            imuoffset["ADXL_AY"] = [0]
            imuoffset["ADXL_AZ"] = [0]


# class Processing_data(QThread):
#     def __init__(self):
#
#         imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
#         imudataArray["ADXL_AX"] = np.append(imudataArray["ADXL_AX"], imudata["ADXL_AX"])
#         imudataArray["ADXL_AY"] = np.append(imudataArray["ADXL_AY"], imudata["ADXL_AY"])
#         imudataArray["ADXL_AZ"] = np.append(imudataArray["ADXL_AZ"], imudata["ADXL_AZ"])
#         imudataArray["NANO33_WX"] = np.append(imudataArray["NANO33_WX"], imudata["NANO33_WX"])
#         imudataArray["NANO33_WY"] = np.append(imudataArray["NANO33_WY"], imudata["NANO33_WY"])
#         imudataArray["NANO33_WZ"] = np.append(imudataArray["NANO33_WZ"], imudata["NANO33_WZ"])
#         imudataArray["PIG_ERR"] = np.append(imudataArray["PIG_ERR"], imudata["PIG_ERR"])
#         imudataArray["PIG_WZ"] = np.append(imudataArray["PIG_WZ"], imudata["PIG_WZ"])
#         imudataArray["PD_TEMP"] = np.append(imudataArray["PD_TEMP"], imudata["PD_TEMP"])
#
#         imudataArray["YEAR"] = np.append(imudataArray["YEAR"], imudata["YEAR"])
#         imudataArray["MON"] = np.append(imudataArray["MON"], imudata["MON"])
#         imudataArray["DAY"] = np.append(imudataArray["DAY"], imudata["DAY"])
#         imudataArray["HOUR"] = np.append(imudataArray["HOUR"], imudata["HOUR"])
#         imudataArray["MIN"] = np.append(imudataArray["MIN"], imudata["MIN"])
#         imudataArray["SEC"] = np.append(imudataArray["SEC"], imudata["SEC"])
#         imudataArray["mSEC"] = np.append(imudataArray["mSEC"], imudata["mSEC"])
#         imudataArray["time_accumulate"] = np.append(imudataArray["time_accumulate"], self.__time_accumulate)

def myCallBack(imudata):
    global old
    new = time.perf_counter_ns()
    # print(imudata)
    # wx = imudata["NANO33_W"][0]
    # wy = imudata["NANO33_W"][1]
    # wz = imudata["NANO33_W"][2]
    # ax = imudata["ADXL_A"][0]
    # ay = imudata["ADXL_A"][1]
    # az = imudata["ADXL_A"][2]
    # t = imudata["TIME"][0]
    # print("%.5f %.5f  %.5f  %.5f  %.5f  %.5f  %.5f" % (t, wx, wy, wz, ax, ay, az))
    # print(imudata["TIME"], imudata["NANO33_W"], imudata["ADXL_A"])
    old = new


if __name__ == "__main__":
    ser = Connector()
    myImu = pigImuReader(debug_en=False)
    myImu.arrayNum = 2
    myImu.setCallback(myCallBack)
    myImu.isCali = True
    myImu.connect(ser, "COM6", 230400)
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
