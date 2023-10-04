""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
from datetime import datetime
from threading import Timer

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
    # "NANO33_WX": np.zeros(1),
    # "NANO33_WY": np.zeros(1),
    # "NANO33_WZ": np.zeros(1),
    # "ADXL_AX": np.zeros(1),
    # "ADXL_AY": np.zeros(1),
    # "ADXL_AZ": np.zeros(1),
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
    "mSEC": np.zeros(1),
    "time_accumulate": np.zeros(1)
}

IMU_Angle_STRUCTURE = {
    "AngleZ": np.zeros(1),
    "TXTVal": np.chararray(1, itemsize=100),
    #"HexVal": np.chararray(1, itemsize=60),
    "YEAR": np.zeros(1),
    "MON": np.zeros(1),
    "DAY": np.zeros(1),
    "HOUR": np.zeros(1),
    "MIN": np.zeros(1),
    "SEC": np.zeros(1),
    "mSEC": np.zeros(1),
    "time_accumulate": np.zeros(1)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
HEADER_NMEA = [36, 89, 65, 87]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_GYRO_500 = 0.01750
SENS_NANO33_AXLM_4G = 0.000122
POS_ADXL355_AX = 4
POS_NANO33_WX = 13
POS_PIG = 4
POS_CRC = 35
old = time.perf_counter_ns()


class pigImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object)
        imuThreadStop_qt = pyqtSignal()
        buffer_qt = pyqtSignal(int)
        Portstatus_qt = pyqtSignal(bool)
        deviceReset_qt = pyqtSignal(bool)
        oneHundred_data_qt = pyqtSignal(object)
        hourChange_qt = pyqtSignal(bool)

    def __init__(self, portName: str = "None", boolCaliw=False, boolCalia=False, baudRate: int = 230400,
                 debug_en: bool = 0):
        super(pigImuReader, self).__init__()
        # self.__first_run_flag = False
        self.time_pass_flag = False
        self.__isExtMode = False
        self.time_pass_cnt = 5
        self.first_run_flag = True
        self.pass_flag = False
        self.nano33_wz_kal = filter.kalman_1D()
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
        self.start_read = 0
        self.__dataRate = 1  # 1秒會傳輸的資料筆數
        self.first_sec = 0  # 20230607 添加
        self.record_sec = 0  # 記錄秒
        self.record_hh = 0  # 紀錄小時
        self.first_sec_has_passed = 0  # 20230712 判斷開始的第一秒是否已經過了
        self.current_time = 0
        self.__current_sec = 0
        self.__InTheMoment_GUI_status = "STOP"
        self.__Stop_NotTimeout = False  # 判斷在timeout時間裡是否有點擊stop或是disconnect
        self.__time_accumulate = 1
        self.__reset_isTrue = False

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
        self.nano33_wz_kal.kal_Q = self.kal_Q
        self.pig_wz_kal.kal_Q = self.kal_Q

    @property
    def kal_R(self):
        return self.__kal_R

    @kal_R.setter
    def kal_R(self, R):
        self.__kal_R = R
        self.nano33_wz_kal.kal_R = self.kal_R
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
        else:
            self.writeImuCmd(101, 0)
            self.writeImuCmd(1, 5)
        return is_open

    # End of memsImuReader::connectIMU

    def disconnect(self):
        is_open = self.__Connector.disconnect()
        return is_open

    # End of memsImuReader::disconnectIMU

    def readIMU(self):
        # print(self.isExtMode + ' MODE')
        if self.isExtMode == 'ON':  # 玉豐的狀態都為ON
            self.writeImuCmd(1, 2)  # External Mode
        elif self.isExtMode == 'OFF':
            self.writeImuCmd(1, 1)  # Internal Mode
        else:
            self.writeImuCmd(1, 1)  # Internal Mode
        # self.first_run_flag = True
        self.time_pass_cnt = 5
        self.time_pass_flag = False
        self.writeImuCmd(CMD_FOG_TIMER_RST, 1) # reset FPGA time
        print('reset FPGA time')

    def stopIMU(self):
        self.writeImuCmd(1, 4)

    def getVersion(self):
        versionText = self.__Connector.readVersion()
        return versionText

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    # 判斷在timeout之前按下stop Or disconnect
    @property
    def Stop_NotTimeout(self):
        return self.__Stop_NotTimeout

    @Stop_NotTimeout.setter
    def Stop_NotTimeout(self, status):
        self.__Stop_NotTimeout = status

    def calculateDataTime(self):
        currentDataAndTime = datetime.now()
        year = currentDataAndTime.year
        mon = currentDataAndTime.month
        day = currentDataAndTime.day
        hour = currentDataAndTime.hour
        min = currentDataAndTime.minute
        sec = currentDataAndTime.second
        mSce = currentDataAndTime.microsecond
        # self.dataRate += 1
        if (self.start_read == 0):
            '''PC Time'''
            msec = int(currentDataAndTime.microsecond * 1e-3)
            '''end of PC time'''
            self.start_read = 1
            self.first_sec = sec
            self.record_sec = sec
        else:
            if sec != self.record_sec:
                self.__dataRate = 1
                self.current_time = 0
                self.record_sec = sec

        if self.current_time >= 1000:
            self.current_time = self.current_time - 1000
        # print("sec:" + str(sec))
        # print("read get data:" + str(self.current_time))
        return year, mon, day, hour, min, sec, mSce

    def getImuData(self):
        head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
        if head == 1:  # 當head撈取不到時，會執行此功能，代表COM Port可能被拔掉了
            if self.__Stop_NotTimeout:  # timeout時，點擊stop或是disconnect
                self.__Connector.portDoNotConnectStatus = False
                return head, {}
            self.__Connector.portDoNotConnectStatus = True
            self.get_Port_connect_status()
            return head, {}
        else:
            dataPacket = getData.getdataPacket(self.__Connector, head, 18)
            if dataPacket == head:  # 當dataPacket撈取不到時，就會執行此功能，代表COM Port可能被拔掉了(撈取不到值)
                if self.__Stop_NotTimeout:  # timeout時，點擊stop或是disconnect
                    self.__Connector.portDoNotConnectStatus = False
                    return head, {}
                self.get_Port_connect_status()
                self.__Connector.portDoNotConnectStatus = True
                return head, {}

        # print([hex(x) for x in dataPacket])

        # ADXL_AX, ADXL_AY, ADXL_AZ = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX,
        #                                             sf=SENS_ADXL355_8G)
        # if ADXL_AX == 10000 and ADXL_AY == 10000 and ADXL_AZ == 10000:
        #     self.__Connector.portDoNotConnectStatus = True
        #     self.get_Port_connect_status()
        #
        # NANO_WX, NANO_WY, NANO_WZ, \
        # NANO_AX, NANO_AY, NANO_AZ = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX,
        #                                            sf_xlm=SENS_NANO33_AXLM_4G,
        #                                            sf_gyro=SENS_NANO33_GYRO_500)
        # if NANO_WX == 10000 and NANO_WY == 10000 and NANO_WZ == 10000 and NANO_AX == 10000 and NANO_AY == 10000 and NANO_AZ == 10000:
        #     self.__Connector.portDoNotConnectStatus = True
        #     self.get_Port_connect_status()

        FPGA_TIME, ERR, STEP, PD_TEMP = cmn.readPIG(dataPacket, EN=1, PRINT=0, sf_a=self.sf_a, sf_b=self.sf_b,
                                                    POS_TIME=POS_PIG)
        if FPGA_TIME == 10000 and ERR == 10000 and STEP == 10000 and PD_TEMP == 10000:
            self.__Connector.portDoNotConnectStatus = True
            self.get_Port_connect_status()

        if not self.isCali:
            if self.isKal:
                #NANO_WZ = self.nano33_wz_kal.update(NANO_WZ)
                STEP = self.pig_wz_kal.update(STEP)
        #
        # # t = time.perf_counter()
        t = FPGA_TIME
        imudata = {#"NANO33_WX": NANO_WX, "NANO33_WY": NANO_WY, "NANO33_WZ": NANO_WZ,
                   #"ADXL_AX": ADXL_AX, "ADXL_AY": ADXL_AY, "ADXL_AZ": ADXL_AZ,
                   # "ADXL_AX": NANO_AX, "ADXL_AY": NANO_AY, "ADXL_AZ": NANO_AZ,
                   "PIG_ERR": ERR, "PIG_WZ": STEP, "PD_TEMP": PD_TEMP, "TIME": t,
                   'YEAR': 0, 'MON': 0, 'DAY': 0, 'HOUR': 0,
                   'MIN': 0, 'SEC': 0, 'mSEC': 0, "time_accumulate": 0,
                   }
        if self.__Stop_NotTimeout:
            self.__Connector.portDoNotConnectStatus = False
        return dataPacket, imudata

    def getImuData_NMEA(self):
        dataPacket = getData.OneRowData(self.__Connector, HEADER_NMEA)
        print(dataPacket)
        if dataPacket == 1:  # 當head撈取不到時，會執行此功能，代表COM Port可能被拔掉了
            if self.__Stop_NotTimeout:  # timeout時，點擊stop或是disconnect
                self.__Connector.portDoNotConnectStatus = False
                return dataPacket, {}
            self.__Connector.portDoNotConnectStatus = True
            self.get_Port_connect_status()
            return dataPacket, {}

        # print([hex(x) for x in dataPacket])

        # ADXL_AX, ADXL_AY, ADXL_AZ = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX,
        #                                             sf=SENS_ADXL355_8G)
        # if ADXL_AX == 10000 and ADXL_AY == 10000 and ADXL_AZ == 10000:
        #     self.__Connector.portDoNotConnectStatus = True
        #     self.get_Port_connect_status()
        #
        # NANO_WX, NANO_WY, NANO_WZ, \
        # NANO_AX, NANO_AY, NANO_AZ = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX,
        #                                            sf_xlm=SENS_NANO33_AXLM_4G,
        #                                            sf_gyro=SENS_NANO33_GYRO_500)
        # if NANO_WX == 10000 and NANO_WY == 10000 and NANO_WZ == 10000 and NANO_AX == 10000 and NANO_AY == 10000 and NANO_AZ == 10000:
        #     self.__Connector.portDoNotConnectStatus = True
        #     self.get_Port_connect_status()

        Angle = cmn.readPIG_onlyAngle(dataPacket, EN=1, PRINT=0, POS_TIME=5)
        if Angle == 10000:
            self.__Connector.portDoNotConnectStatus = True
            self.get_Port_connect_status()

        # if not self.isCali:
        #     if self.isKal:
        #         #NANO_WZ = self.nano33_wz_kal.update(NANO_WZ)
        #         STEP = self.pig_wz_kal.update(STEP)
        #
        # # t = time.perf_counter()

        imudata = {"AngleZ": Angle,'YEAR': 0, 'MON': 0, 'DAY': 0, 'HOUR': 0,
                   'MIN': 0, 'SEC': 0, 'mSEC': 0, "time_accumulate": 0}
        if self.__Stop_NotTimeout:
            self.__Connector.portDoNotConnectStatus = False
        return dataPacket, imudata

    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def do_cali(self, dictContainer, cali_times):
        try:
            if self.isCali:
                print('do_cali')
                temp = {k: np.zeros(1) for k in set(IMU_DATA_STRUCTURE)}
                print("---calibrating offset start-----")
                for i in range(cali_times):
                    dataPacket, imudata = self.getImuData()
                    temp = cmn.dictOperation(temp, imudata, "ADD", IMU_DATA_STRUCTURE)
                temp = {k: temp.get(k) / cali_times for k in set(self.__imuoffset)}
                print("---calibrating offset stop-----")
                self.isCali = False
                return temp
        except Exception as e:
            logger.error("錯誤原因: %s" % e)
            return None
        else:
            return dictContainer

    def time_pass_check(self, isPass, time_in):
        if not isPass:
            if time_in < 0.8:
                self.time_pass_flag = True

    @property
    def InTheMoment_GUI_status(self):
        return self.__InTheMoment_GUI_status

    @InTheMoment_GUI_status.setter
    def InTheMoment_GUI_status(self, status):
        self.__InTheMoment_GUI_status = status

    def get_Port_connect_status(self):  # 判斷USB線被拔除或是沒有電的狀況下
        self.__PortStatus = self.__Connector.portDoNotConnectStatus
        if self.__PortStatus == 1:
            self.isRun = False
            self.Portstatus_qt.emit(False)

    def judgment_Reset(self):
        if self.__recording_device_reset_time == 0:
            self.__recording_device_reset_time = time.perf_counter()
        else:
            now_time = time.perf_counter()
            if (now_time - self.__recording_device_reset_time) > 3:
                self.__recording_device_reset_time = time.perf_counter()
                self.__reset_isTrue = True
                self.deviceReset_qt.emit(True)
                #print("reset次數")
            else:
                self.__recording_device_reset_time = time.perf_counter()

    @property
    def recording_device_reset_time(self):
        return self.__recording_device_reset_time

    @recording_device_reset_time.setter
    def recording_device_reset_time(self, Time):
        self.__recording_device_reset_time = Time

    def reset_data_set_val(self):  # 當儀器停止傳輸時(手動與自動斷線)
        self.start_read = 0
        self.record_sec = 0
        self.first_sec_has_passed = 0
        self.__time_accumulate = 1

    def sysReset_data(self):
        self.__time_accumulate = 1
        self.__dataRate = 1

# 20230825註解
    # def run(self):
    #     self.__Connector.portDoNotConnectStatus = False
    #     logging.basicConfig(level=100)
    #     t0 = time.perf_counter()
    #     self.record_hh = datetime.now().hour
    #     self.time_less_than_one = None  # 讓畫面不要在reset過後，再次撈資料時，造成畫面很亂的問題
    #     #self.overOneHundred_and_secChange = None
    #     while True:
    #         self.FirstSec_Flag = False  # 當進入的第一秒資料不要使用
    #         #self.timeIsChange_Flag = False  # 當迴圈break的時候使用
    #         self.__reset_isTrue = False  # 判斷reset
    #         if not self.isRun:
    #             self.stopIMU()
    #             self.reset_data_set_val()
    #             self.imuThreadStop_qt.emit()
    #             # self.first_run_flag = True
    #             break
    #         # End of if-condition
    #
    #         self.__imuoffset = self.do_cali(self.__imuoffset, 100)
    #         if self.__imuoffset == None:  # 當calibration開啟之後，需要做此判斷
    #             self.__Connector.portDoNotConnectStatus = False
    #             self.get_Port_connect_status()
    #
    #         oneHundred_imudata = {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}
    #         year, mon, day, hour, min, sec, mSec = self.calculateDataTime()
    #
    #         hour_ = datetime.now().hour
    #         if hour_ != self.record_hh:
    #             self.record_hh = hour_
    #             # self.hourChange_qt.emit(True)
    #             self.__time_accumulate = 1
    #         for i in range(self.arrayNum):
    #             self.__timeDelay = False
    #             self.get_Port_connect_status()
    #             if not self.isRun:
    #                 self.stopIMU()
    #                 self.reset_data_set_val()
    #                 self.imuThreadStop_qt.emit()
    #                 # self.first_run_flag = True
    #                 break
    #
    #             imudataArray = {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}
    #
    #             sec_judgment_1 = datetime.now().second
    #             if self.first_sec_has_passed == 0:
    #                 if sec_judgment_1 != self.first_sec:  # 當第一秒已經換到下一秒時，需要做的處理
    #                     self.FirstSec_Flag = True
    #                     self.first_sec_has_passed = 1
    #                     self.sysReset_data()
    #                     #print("第一秒改變了~~")
    #                     break
    #                 dataPacket, imudata = self.getImuData()
    #                 continue
    #             for k in range(self.arrayNum):
    #                 if self.__dataRate >= 101:
    #                     sec_judgment = datetime.now().second
    #                     if sec_judgment == self.record_sec:
    #                         self.FirstSec_Flag = True
    #                         #print("第101筆資料")
    #
    #                     if sec_judgment != self.record_sec:
    #                         self.FirstSec_Flag = True
    #                         self.overOneHundred_and_secChange = True
    #                         self.__dataRate = 1
    #                         #print("超過100筆的畫畫")
    #                         break
    #
    #                 self.__dataRate += 1
    #                 # 顯示read buffer size的部分
    #                 # input_buf = self.readInputBuffer()
    #                 # self.buffer_qt.emit(input_buf)
    #                 # while self.__Connector.readInputBuffer() < self.arrayNum * 10:
    #                 # while not self.__Connector.readInputBuffer():
    #                 #     # print(self.__Connector.readInputBuffer())
    #                 #     # print("No input data!")
    #                 #     # cmn.wait_ms(500)
    #                 #     pass
    #                 t1 = time.perf_counter()
    #
    #                 dataPacket, imudata = self.getImuData()
    #                 self.judgment_Reset()  # 判斷reset的功能
    #                 if self.__reset_isTrue:
    #                     break
    #                 if not self.isRun:
    #                     self.stopIMU()
    #                     self.reset_data_set_val()
    #                     self.imuThreadStop_qt.emit()
    #                     # self.first_run_flag = True
    #                     break
    #                 # 當點擊STOP之後，再read的buffer會有舊資料，需要將舊資料排除不呈現於介面中
    #                 # 所做的判斷部分
    #                 # if self.__InTheMoment_GUI_status == "STOP":
    #                 #     if imudata["TIME"] > 1:
    #                 #         self.time_less_than_one = False
    #                 #         continue
    #                 #     elif imudata["TIME"] < 1:
    #                 #         self.time_less_than_one = True
    #                 #         break
    #                 # if self.first_run_flag and (imudata['TIME'] > 2):
    #                 #     print('\n in act: first_run_flag is ', self.first_run_flag)
    #                 # print('imudata[TIME]: ', round(imudata['TIME'], 5), end=', ')
    #                 # print('self.time_pass_cnt: ', self.time_pass_cnt, end='\n\n')
    #                 # print('reset timer!\n')
    #                 # self.time_pass_cnt = 5
    #                 # self.first_run_flag = False
    #                 # self.writeImuCmd(CMD_FOG_TIMER_RST, 1)
    #                 # else:
    #                 #     self.first_run_flag = False
    #                 # print('\n in act: first_run_flag is ', self.first_run_flag)
    #                 # print('imudata[TIME]: ', imudata['TIME'])
    #                 # print('pass\n')
    #
    #                 # self.first_run_flag = False
    #                 t2 = time.perf_counter()
    #                 #isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
    #                 isChecksumFail = crcLib.isChecksumFail()
    #                 t3 = time.perf_counter()
    #                 # err correction
    #                 #imudata = crcLib.errCorrection(isCrcFail, imudata)
    #                 imudata = crcLib.errCorrection(isChecksumFail, imudata)
    #                 # end of err correction
    #                 t4 = time.perf_counter()
    #                 # imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND", IMU_DATA_STRUCTURE)
    #                 # print('act.loop: ', imudataArray["TIME"], imudata["TIME"])
    #                 # print('\n self.time_pass_cnt: ', self.time_pass_cnt)
    #
    #                 self.time_pass_check(self.time_pass_flag, imudata["TIME"])
    #
    #                 # if self.time_pass_flag:
    #                 imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
    #                 # imudataArray["ADXL_AX"] = np.append(imudataArray["ADXL_AX"], imudata["ADXL_AX"])
    #                 # imudataArray["ADXL_AY"] = np.append(imudataArray["ADXL_AY"], imudata["ADXL_AY"])
    #                 # imudataArray["ADXL_AZ"] = np.append(imudataArray["ADXL_AZ"], imudata["ADXL_AZ"])
    #                 # imudataArray["NANO33_WX"] = np.append(imudataArray["NANO33_WX"], imudata["NANO33_WX"])
    #                 # imudataArray["NANO33_WY"] = np.append(imudataArray["NANO33_WY"], imudata["NANO33_WY"])
    #                 # imudataArray["NANO33_WZ"] = np.append(imudataArray["NANO33_WZ"], imudata["NANO33_WZ"])
    #                 imudataArray["PIG_ERR"] = np.append(imudataArray["PIG_ERR"], imudata["PIG_ERR"])
    #                 imudataArray["PIG_WZ"] = np.append(imudataArray["PIG_WZ"], imudata["PIG_WZ"])
    #                 imudataArray["PD_TEMP"] = np.append(imudataArray["PD_TEMP"], imudata["PD_TEMP"])
    #                 imudataArray["YEAR"] = np.append(imudataArray["YEAR"], year)
    #                 imudataArray["MON"] = np.append(imudataArray["MON"], mon)
    #                 imudataArray["DAY"] = np.append(imudataArray["DAY"], day)
    #                 imudataArray["HOUR"] = np.append(imudataArray["HOUR"], hour)
    #                 imudataArray["MIN"] = np.append(imudataArray["MIN"], min)
    #                 imudataArray["SEC"] = np.append(imudataArray["SEC"], sec)
    #                 imudataArray["mSEC"] = np.append(imudataArray["mSEC"], self.current_time)
    #                 imudataArray["time_accumulate"] = np.append(imudataArray["time_accumulate"], self.__time_accumulate)
    #                 # print('imudata[TIME]: ', round(imudata['TIME'], 5), end=', ')
    #                 # print('self.time_pass_flag: ', self.time_pass_flag, end='\n\n')
    #
    #                 # if self.time_pass_cnt == 0:
    #                 #     imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
    #                 #     imudataArray["ADXL_AX"] = np.append(imudataArray["ADXL_AX"], imudata["ADXL_AX"])
    #                 #     imudataArray["ADXL_AY"] = np.append(imudataArray["ADXL_AY"], imudata["ADXL_AY"])
    #                 #     imudataArray["ADXL_AZ"] = np.append(imudataArray["ADXL_AZ"], imudata["ADXL_AZ"])
    #                 #     imudataArray["NANO33_WX"] = np.append(imudataArray["NANO33_WX"], imudata["NANO33_WX"])
    #                 #     imudataArray["NANO33_WY"] = np.append(imudataArray["NANO33_WY"], imudata["NANO33_WY"])
    #                 #     imudataArray["NANO33_WZ"] = np.append(imudataArray["NANO33_WZ"], imudata["NANO33_WZ"])
    #                 #     imudataArray["PIG_ERR"] = np.append(imudataArray["PIG_ERR"], imudata["PIG_ERR"])
    #                 #     imudataArray["PIG_WZ"] = np.append(imudataArray["PIG_WZ"], imudata["PIG_WZ"])
    #                 #     imudataArray["PD_TEMP"] = np.append(imudataArray["PD_TEMP"], imudata["PD_TEMP"])
    #                 # if not (self.time_pass_cnt == 0):
    #                 #     self.time_pass_cnt = self.time_pass_cnt - 1
    #
    #                 t5 = time.perf_counter()
    #
    #                 # debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
    #                 #              + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
    #                 #              + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
    #                 debug_info = "ACT: ," + str(round((t5 - t1) * 1000, 5)) + ", " \
    #                              + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
    #                              + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
    #
    #                 cmn.print_debug(debug_info, self.__debug)
    #                 # print('ACT imudataArray["TIME"]: ', imudataArray["TIME"], end='\n\n')
    #                 if not self.FirstSec_Flag:
    #                     self.__time_accumulate += 1
    #                     self.current_time += 10
    #
    #             if not self.isRun:
    #                 self.stopIMU()
    #                 self.reset_data_set_val()
    #                 self.imuThreadStop_qt.emit()
    #                 # self.first_run_flag = True
    #                 break
    #         # end of for loop
    #
    #             if self.FirstSec_Flag and self.overOneHundred_and_secChange:
    #                 break
    #         # imudataArray["TIME"] = imudataArray["TIME"] - t0
    #             self.offset_setting(self.__imuoffset)
    #             imudataArray = cmn.dictOperation(imudataArray, self.__imuoffset, "SUB", IMU_DATA_STRUCTURE)
    #             if self.__callBack is not None:
    #                 self.__callBack(imudataArray)
    #
    #             if not __name__ == "__main__":
    #                 # if self.__InTheMoment_GUI_status == "START":
    #                 if len(imudataArray["TIME"]) != 0:
    #                     self.imudata_qt.emit(imudataArray)
    #             # if self.timeIsChange_Flag == True:  # 只卡第一秒
    #             #     self.timeIsChange_Flag = False
    #             #     self.hourChange_qt.emit(True)
    #             #     continue
    #
    #             # if self.time_less_than_one == True and self.__InTheMoment_GUI_status == "STOP":
    #             #     self.__InTheMoment_GUI_status = "START"
    #             #     self.time_less_than_one = False
    #             #     continue
    #
    #             if self.FirstSec_Flag == False:
    #                 # 儲存100筆資料
    #                 oneHundred_imudata["TIME"] = np.append(oneHundred_imudata["TIME"], imudataArray["TIME"])
    #                 # imudataArray["ADXL_AX"] = np.append(imudataArray["ADXL_AX"], imudata["ADXL_AX"])
    #                 # imudataArray["ADXL_AY"] = np.append(imudataArray["ADXL_AY"], imudata["ADXL_AY"])
    #                 # imudataArray["ADXL_AZ"] = np.append(imudataArray["ADXL_AZ"], imudata["ADXL_AZ"])
    #                 # imudataArray["NANO33_WX"] = np.append(imudataArray["NANO33_WX"], imudata["NANO33_WX"])
    #                 # imudataArray["NANO33_WY"] = np.append(imudataArray["NANO33_WY"], imudata["NANO33_WY"])
    #                 # imudataArray["NANO33_WZ"] = np.append(imudataArray["NANO33_WZ"], imudata["NANO33_WZ"])
    #                 oneHundred_imudata["PIG_ERR"] = np.append(oneHundred_imudata["PIG_ERR"], imudataArray["PIG_ERR"])
    #                 oneHundred_imudata["PIG_WZ"] = np.append(oneHundred_imudata["PIG_WZ"], imudataArray["PIG_WZ"])
    #                 oneHundred_imudata["PD_TEMP"] = np.append(oneHundred_imudata["PD_TEMP"], imudataArray["PD_TEMP"])
    #                 oneHundred_imudata["YEAR"] = np.append(oneHundred_imudata["YEAR"], imudataArray["YEAR"])
    #                 oneHundred_imudata["MON"] = np.append(oneHundred_imudata["MON"], imudataArray["MON"])
    #                 oneHundred_imudata["DAY"] = np.append(oneHundred_imudata["DAY"], imudataArray["DAY"])
    #                 oneHundred_imudata["HOUR"] = np.append(oneHundred_imudata["HOUR"], imudataArray["HOUR"])
    #                 oneHundred_imudata["MIN"] = np.append(oneHundred_imudata["MIN"], imudataArray["MIN"])
    #                 oneHundred_imudata["SEC"] = np.append(oneHundred_imudata["SEC"], imudataArray["SEC"])
    #                 oneHundred_imudata["mSEC"] = np.append(oneHundred_imudata["mSEC"], imudataArray["mSEC"])
    #                 oneHundred_imudata["time_accumulate"] = np.append(oneHundred_imudata["time_accumulate"], imudataArray["time_accumulate"])
    #
    #                 if not __name__ == "__main__":
    #                     if len(oneHundred_imudata["TIME"]) == 100 and self.FirstSec_Flag == False:
    #                         self.oneHundred_data_qt.emit(oneHundred_imudata)
    #
    #             # print(imudataArray["PIG_WZ"])
    #
    #             # if self.first_run_flag or (imudata['TIME'] > 2):
    #             #         print('in act reset timer!')
    #             #         self.writeImuCmd(CMD_FOG_TIMER_RST, 1)
    #             # else:
    #             #     print('in act pass!')
    #             #     self.imudata_qt.emit(imudataArray)
    #             # elif (not self.first_run_flag) or (not (imudata['TIME'] > 2)):
    #             #     self.imudata_qt.emit(imudataArray)
    #         if self.__reset_isTrue:
    #             self.__reset_isTrue = False
    #             self.first_sec_has_passed = 0
    #             continue
    #         if self.FirstSec_Flag == True:  # 只卡第一秒
    #             self.FirstSec_Flag = False
    #             self.overOneHundred_and_secChange = None
    #             continue
    #         # print(imudataArray)
    #
    #     # end of while loop
    #
    # # End of memsImuReader::run

    def run(self):
        self.__Connector.portDoNotConnectStatus = False
        logging.basicConfig(level=100)
        t0 = time.perf_counter()
        self.record_hh = datetime.now().hour
        self.time_less_than_one = None  # 讓畫面不要在reset過後，再次撈資料時，造成畫面很亂的問題
        #self.overOneHundred_and_secChange = None
        while True:
            self.FirstSec_Flag = False  # 當進入的第一秒資料不要使用
            #self.timeIsChange_Flag = False  # 當迴圈break的時候使用
            self.overOneHundred_and_secChange = False
            self.__reset_isTrue = False  # 判斷reset
            if not self.isRun:
                self.stopIMU()
                self.reset_data_set_val()
                self.imuThreadStop_qt.emit()
                # self.first_run_flag = True
                break
            # End of if-condition

            #self.__imuoffset = self.do_cali(self.__imuoffset, 100)
            # if self.__imuoffset == None:  # 當calibration開啟之後，需要做此判斷
            #     self.__Connector.portDoNotConnectStatus = False
            #     self.get_Port_connect_status()

            oneHundred_imudata = {k: np.empty(0) for k in set(IMU_Angle_STRUCTURE)}
            year, mon, day, hour, min, sec, mSec = self.calculateDataTime()

            hour_ = datetime.now().hour
            if hour_ != self.record_hh:
                self.record_hh = hour_
                # self.hourChange_qt.emit(True)
                self.__time_accumulate = 1
            for i in range(self.arrayNum):
                self.__timeDelay = False
                self.get_Port_connect_status()
                if not self.isRun:
                    self.stopIMU()
                    self.reset_data_set_val()
                    self.imuThreadStop_qt.emit()
                    # self.first_run_flag = True
                    break

                imudataArray = {k: np.empty(0) for k in set(IMU_Angle_STRUCTURE)}

                sec_judgment_1 = datetime.now().second
                if self.first_sec_has_passed == 0:
                    if sec_judgment_1 != self.first_sec:  # 當第一秒已經換到下一秒時，需要做的處理
                        self.FirstSec_Flag = True
                        self.first_sec_has_passed = 1
                        self.sysReset_data()
                        #print("第一秒改變了~~")
                        break
                    dataPacket, imudata = self.getImuData_NMEA()
                    continue
                for k in range(self.arrayNum):
                    if self.__dataRate >= 101:
                        sec_judgment = datetime.now().second
                        if sec_judgment == self.record_sec:
                            self.FirstSec_Flag = True
                            #print("第101筆資料")

                        if sec_judgment != self.record_sec:
                            self.FirstSec_Flag = True
                            self.overOneHundred_and_secChange = True
                            self.__dataRate = 1
                            #print("超過100筆的畫畫")
                            break

                    self.__dataRate += 1

                    t1 = time.perf_counter()

                    dataPacket, imudata = self.getImuData_NMEA()
                    ASCIIStr = cmn.changeToASCII(dataPacket)
                    HexStr = cmn.changToHex(dataPacket)
                    TXTStr = ASCIIStr + "; " + HexStr
                    self.judgment_Reset()  # 判斷reset的功能
                    if self.__reset_isTrue:
                        break
                    if not self.isRun:
                        self.stopIMU()
                        self.reset_data_set_val()
                        self.imuThreadStop_qt.emit()
                        # self.first_run_flag = True
                        break

                    t2 = time.perf_counter()
                    #isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                    corret_str = chr(dataPacket[12])
                    corret_str2 = chr(dataPacket[13])
                    correct = corret_str+corret_str2
                    isChecksumFail = crcLib.isChecksumFail(dataPacket[1:11], correct)
                    t3 = time.perf_counter()
                    # err correction
                    #imudata = crcLib.errCorrection(isCrcFail, imudata)
                    imudata = crcLib.errCorrection(isChecksumFail, imudata)
                    # if isChecksumFail and self.__time_accumulate == 1:
                    #     imudata["AngleZ"] = 0.0
                    # end of err correction
                    t4 = time.perf_counter()
                    # imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND", IMU_DATA_STRUCTURE)
                    # print('act.loop: ', imudataArray["TIME"], imudata["TIME"])
                    # print('\n self.time_pass_cnt: ', self.time_pass_cnt)

                    # if self.time_pass_flag:
                    imudataArray["AngleZ"] = np.append(imudataArray["AngleZ"], imudata["AngleZ"])
                    imudataArray["TXTVal"] = np.append(imudataArray["TXTVal"], TXTStr)
                    imudataArray["YEAR"] = np.append(imudataArray["YEAR"], year)
                    imudataArray["MON"] = np.append(imudataArray["MON"], mon)
                    imudataArray["DAY"] = np.append(imudataArray["DAY"], day)
                    imudataArray["HOUR"] = np.append(imudataArray["HOUR"], hour)
                    imudataArray["MIN"] = np.append(imudataArray["MIN"], min)
                    imudataArray["SEC"] = np.append(imudataArray["SEC"], sec)
                    imudataArray["mSEC"] = np.append(imudataArray["mSEC"], self.current_time)
                    imudataArray["time_accumulate"] = np.append(imudataArray["time_accumulate"], self.__time_accumulate)
                    t5 = time.perf_counter()

                    # debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                    #              + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                    #              + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                    debug_info = "ACT: ," + str(round((t5 - t1) * 1000, 5)) + ", " \
                                 + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                                 + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))

                    cmn.print_debug(debug_info, self.__debug)
                    # print('ACT imudataArray["TIME"]: ', imudataArray["TIME"], end='\n\n')
                    if not self.FirstSec_Flag:
                        self.__time_accumulate += 1
                        self.current_time += 10

                    #print(imudata["AngleZ"])

                if not self.isRun:
                    self.stopIMU()
                    self.reset_data_set_val()
                    self.imuThreadStop_qt.emit()
                    # self.first_run_flag = True
                    break
            # end of for loop

                # if self.__reset_isTrue:
                #     break
                # if self.overOneHundred_and_secChange:
                #     break
            # # imudataArray["TIME"] = imudataArray["TIME"] - t0
            #     self.offset_setting(self.__imuoffset)
            #     imudataArray = cmn.dictOperation(imudataArray, self.__imuoffset, "SUB", IMU_DATA_STRUCTURE)
            #     if self.__callBack is not None:
            #         self.__callBack(imudataArray)

                if not __name__ == "__main__":
                    # if self.__InTheMoment_GUI_status == "START":
                    if len(imudataArray["AngleZ"]) != 0:
                        self.imudata_qt.emit(imudataArray)
                        #print(imudataArray)
                # if self.timeIsChange_Flag == True:  # 只卡第一秒
                #     self.timeIsChange_Flag = False
                #     self.hourChange_qt.emit(True)
                #     continue

                # if self.time_less_than_one == True and self.__InTheMoment_GUI_status == "STOP":
                #     self.__InTheMoment_GUI_status = "START"
                #     self.time_less_than_one = False
                #     continue

                if self.FirstSec_Flag == False:
                    # 儲存100筆資料
                    oneHundred_imudata["AngleZ"] = np.append(oneHundred_imudata["AngleZ"], imudataArray["AngleZ"])
                    oneHundred_imudata["TXTVal"] = np.append(oneHundred_imudata["TXTVal"], imudataArray["TXTVal"])
                    oneHundred_imudata["YEAR"] = np.append(oneHundred_imudata["YEAR"], imudataArray["YEAR"])
                    oneHundred_imudata["MON"] = np.append(oneHundred_imudata["MON"], imudataArray["MON"])
                    oneHundred_imudata["DAY"] = np.append(oneHundred_imudata["DAY"], imudataArray["DAY"])
                    oneHundred_imudata["HOUR"] = np.append(oneHundred_imudata["HOUR"], imudataArray["HOUR"])
                    oneHundred_imudata["MIN"] = np.append(oneHundred_imudata["MIN"], imudataArray["MIN"])
                    oneHundred_imudata["SEC"] = np.append(oneHundred_imudata["SEC"], imudataArray["SEC"])
                    oneHundred_imudata["mSEC"] = np.append(oneHundred_imudata["mSEC"], imudataArray["mSEC"])
                    oneHundred_imudata["time_accumulate"] = np.append(oneHundred_imudata["time_accumulate"], imudataArray["time_accumulate"])

                    if not __name__ == "__main__":
                        if len(oneHundred_imudata["AngleZ"]) == 100 and self.FirstSec_Flag == False:
                            self.oneHundred_data_qt.emit(oneHundred_imudata)

                # print(imudataArray["PIG_WZ"])

                # if self.first_run_flag or (imudata['TIME'] > 2):
                #         print('in act reset timer!')
                #         self.writeImuCmd(CMD_FOG_TIMER_RST, 1)
                # else:
                #     print('in act pass!')
                #     self.imudata_qt.emit(imudataArray)
                # elif (not self.first_run_flag) or (not (imudata['TIME'] > 2)):
                #     self.imudata_qt.emit(imudataArray)
            if self.__reset_isTrue:
                self.__reset_isTrue = False
                self.first_sec_has_passed = 0
                continue
            if self.FirstSec_Flag == True:  # 只卡第一秒
                self.FirstSec_Flag = False
                self.overOneHundred_and_secChange = False
                continue
            # print(imudataArray)

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
        imuoffset["time_accumulate"] = [0]
        if not self.isCali_w:
            # imuoffset["NANO33_WX"] = [0]
            # imuoffset["NANO33_WY"] = [0]
            # imuoffset["NANO33_WZ"] = [0]
            imuoffset["PIG_ERR"] = [0]
            imuoffset["PIG_WZ"] = [0]
        # if not self.isCali_a:
        #     imuoffset["ADXL_AX"] = [0]
        #     imuoffset["ADXL_AY"] = [0]
        #     imuoffset["ADXL_AZ"] = [0]

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
