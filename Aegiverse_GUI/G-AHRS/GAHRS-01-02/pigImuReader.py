""" ####### log stuff creation, always on the top ########  """
import builtins
import inspect
import logging
import os
import traceback

from PySide6.QtWidgets import QApplication

from myLib.logProcess import logProcess
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
from PySide6.QtCore import QThread, Signal
from myLib import common as cmn, logProcess
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
    "PD_TEMP": np.zeros(1),
    "PITCH": np.zeros(1),
    "ROLL": np.zeros(1),
    "YAW": np.zeros(1),
    "GPS_STATUS_CODE": np.zeros(1, dtype=np.uint8),
    "GPS_STATUS_NAME": np.array([''], dtype='U20')
}


HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
HEADER_GPS = [0xFE, 0x82, 0xFF, 0x55]  # GPS 位置封包標頭

# GPS 數據結構
GPS_DATA_STRUCTURE = {
    "LATITUDE": np.zeros(1),     # 緯度 (double)
    "LONGITUDE": np.zeros(1),    # 經度 (double)
    "ALTITUDE": np.zeros(1),     # 海拔 (float)
    "TIMESTAMP": np.zeros(1),    # 時間戳 (float)
    "UTC_HOUR": np.zeros(1, dtype=np.uint8),      # UTC 時
    "UTC_MINUTE": np.zeros(1, dtype=np.uint8),    # UTC 分
    "UTC_SECOND": np.zeros(1, dtype=np.uint8),    # UTC 秒
    "UTC_MILLISECOND": np.zeros(1, dtype=np.uint16),  # UTC 毫秒
    "UTC_DAY": np.zeros(1, dtype=np.uint8),       # UTC 日
    "UTC_MONTH": np.zeros(1, dtype=np.uint8),     # UTC 月
    "UTC_YEAR": np.zeros(1, dtype=np.uint16),     # UTC 年
    "MCU_TIME": np.zeros(1),     # MCU 時間
    "GPS_STATUS_CODE": np.zeros(1, dtype=np.uint8),  # GPS 狀態
    "GPS_STATUS_NAME": np.array([''], dtype='U20')
}

# GPS 狀態碼定義
GPS_STATUS_CODES = {
    0x00: "DATA_ALL_VALID",     # 位置和航向都有效
    0x01: "DATA_POS_ONLY",      # 僅位置有效，航向無效
    0x02: "DATA_NO_FIX",        # 無定位信號
    0x03: "DATA_UNSTABLE",      # 數據不穩定/驗證失敗
    0xFF: "DATA_INVALID"        # 數據無效
}

def get_gps_status_name(status_code):
    """取得 GPS 狀態碼對應的名稱"""
    return GPS_STATUS_CODES.get(status_code, f"UNKNOWN_STATUS_{status_code:02X}")
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_ADXL355_AX = None
POS_NANO33_WX = None
SIZE_4 = 4
SIZE_HEADER = 4
SIZE_NANO33 = 12
SIZE_FOG = 14
SIZE_MCUTIME = 4
POS_NANO33 = SIZE_HEADER
POS_WX = SIZE_HEADER
POS_WY = POS_WX + SIZE_4
POS_WZ = POS_WY + SIZE_4
POS_AX = POS_WZ + SIZE_4
POS_AY = POS_AX + SIZE_4
POS_AZ = POS_AY + SIZE_4
POS_PD_TEMP = POS_AZ + SIZE_4
POS_MCUTIME = POS_PD_TEMP + SIZE_4
POS_PITCH = POS_MCUTIME + SIZE_4
POS_ROLL = POS_PITCH + SIZE_4
POS_YAW = POS_ROLL + SIZE_4
POS_GPS_STATUS = POS_YAW + SIZE_4  # GPS 狀態碼位置 (1 byte)，在 YAW 後面
SIZE_GPS_STATUS = 1

POS_PIG = POS_NANO33 + SIZE_NANO33
old = time.perf_counter_ns()


class pigImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = Signal(object)
        imuThreadStop_qt = Signal()
        buffer_qt = Signal(int)
        AutoCompAvg_qt = Signal(object)
        gps_data_qt = Signal(dict)  # GPS數據信號


    def __init__(self, portName: str = "None", boolCaliw=False, boolCalia=False, baudRate: int = 230400,
                 debug_en: bool = 0):
        super(pigImuReader, self).__init__()
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
        self.__debug = debug_en
        # 計算補償的動作 20250807
        self.__isRunAutoComp = None
        self.__old_imudata = {k: (-1,) * len(IMU_DATA_STRUCTURE.get(k)) for k in set(IMU_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(1) for k in set(IMU_DATA_STRUCTURE)}
        # print(not __name__ == "__main__")

        # 20241211 用於選擇指令的內容
        self.__startCmd = [2, 2, 2]
        self.__stopCmd = [2, 4, 2]
        # 發生錯誤要顯示因錯誤所以停止並出現訊息視窗
        self.__isOccurrErr = False

        # 2025/09/11 新增，for R_CS 姿態旋轉使用
        # R_CS 和 MCU 端一致（row-major）
        self.__use_rcs = False
        self.__R_CS = None # 3x3 row-major, len=9（與MCU相同的 Rcs）

        # GPS 頻率測量變數
        self.__gps_last_time = None
        self.__gps_count = 0
        self.__gps_time_start = None
        self.__gps_intervals = []

    # class constructor

    def __del__(self):
        logger.info("class memsImuReader's destructor called!")

    # End of destructor

    # use_rcs property
    @property
    def use_rcs(self) -> bool:
        return self.__use_rcs

    @use_rcs.setter
    def use_rcs(self, enabled: bool):
        self.__use_rcs = bool(enabled)
        print("act.use_rcs:", self.__use_rcs)
        # traceback.print_stack(limit=3)  # 顯示呼叫堆疊（只印 3 層，方便追）

    # R_CS property
    @property
    def R_CS(self):
        return self.__R_CS

    @R_CS.setter
    def R_CS(self, value):
        if value is None:
            self.__R_CS = None
            print("act.R_CS cleared")
            return
        if hasattr(value, "__len__") and len(value) == 9:
            self.__R_CS = list(value)
            print("act.R_CS updated:", self.__R_CS)
        else:
            raise ValueError("R_CS must be length-9 row-major 3x3 matrix")

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
        self.pig_ax_kal.kal_Q = self.kal_Q
        self.pig_ay_kal.kal_Q = self.kal_Q
        self.pig_az_kal.kal_Q = self.kal_Q

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
        self.pig_ax_kal.kal_R = self.kal_R
        self.pig_ay_kal.kal_R = self.kal_R
        self.pig_az_kal.kal_R = self.kal_R

    @property
    def isRun(self):
        return self.__isRun

    # End of memsImuReader::isRun(getter)

    @isRun.setter
    def isRun(self, isFlag):
        self.__isRun = isFlag

    # End of ImuReader::isRun(setter)

    @property
    def isRunAutoComp(self):
        return self.__isRunAutoComp

    @isRunAutoComp.setter
    def isRunAutoComp(self, isFlag):
        self.__isRunAutoComp = isFlag

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

    def connectRead(self, port, portName, baudRate):
        self.__Connector = port
        port.portName = portName
        port.baudRate = baudRate
        is_open = self.__Connector.connectConn()
        return is_open

    # End of memsImuReader::connectIMU

    def disconnectRead(self):
        is_open = self.__Connector.disconnectConn()
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
        self.writeImuCmd(self.__startCmd[0], self.__startCmd[1], self.__startCmd[2])

    def stopIMU(self):
        self.writeImuCmd(self.__stopCmd[0], self.__stopCmd[1], self.__stopCmd[2])

    # 使用此設定reader層或是再底層發生錯誤
    def occurredErr(self):
        self.__isOccurrErr = True

    @property
    def isOccurrErr(self):
        return self.__isOccurrErr

    @isOccurrErr.setter
    def isOccurrErr(self, boolVal):
        self.__isOccurrErr = boolVal

    def selectCMD(self, type, cmd):
        Str_split = cmd.split(", ")

        if type == "start":
            self.__startCmd = [int(Str_split[0]), int(Str_split[1]), int(Str_split[2])]


    def dump_fog_parameters(self, ch):
        # self.writeImuCmd(0x66, 2)
        print('DUMP here')
        return self.__Connector.dump_fog_parameters(ch)

    def dump_cali_parameters(self, ch):
        return self.__Connector.dump_cali_parameters(ch)

    def getVersion(self, ch):
        # self.writeImuCmd(0x66, 2)
        return self.__Connector.getVersion(ch)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuDataWithHeader(self, header_bytes):
        """處理已讀取header的IMU數據"""
        try:
            # 直接讀取payload，不需要對齊header
            payload_data = self.__Connector.readBinaryList(36 + 12 + 1)  # 49 bytes payload
            if len(payload_data) < 49:
                return None, None

            # 組合完整的dataPacket (header + payload)
            dataPacket = list(header_bytes) + list(payload_data)

            # 解碼資料
            TIME, WX, WY, WZ, AX, AY, AZ, PD_TEMP, PITCH, ROLL, YAW = cmn.readAHRS_Rotate(
                dataPacket,
                POS_WX, POS_WY, POS_WZ, POS_AX, POS_AY, POS_AZ,
                POS_MCUTIME, POS_PD_TEMP, POS_PITCH, POS_ROLL, POS_YAW, 4, PRINT=0,
                use_rcs=self.use_rcs, R_CS=self.R_CS
            )

            # 提取 GPS 狀態碼
            gps_status_code = int(dataPacket[POS_GPS_STATUS]) if len(dataPacket) > POS_GPS_STATUS else 0xFF
            gps_status_name = get_gps_status_name(gps_status_code)

            # Kalman 濾波處理
            if self.isKal:
                WX = self.pig_wx_kal.update(WX)
                WY = self.pig_wy_kal.update(WY)
                WZ = self.pig_wz_kal.update(WZ)
                AX = self.pig_ax_kal.update(AX)
                AY = self.pig_ay_kal.update(AY)
                AZ = self.pig_az_kal.update(AZ)

            # 打包結果
            imudata = {
                "TIME": TIME,
                "WX": WX, "WY": WY, "WZ": WZ,
                "AX": AX, "AY": AY, "AZ": AZ,
                "PD_TEMP": PD_TEMP,
                "PITCH": PITCH, "ROLL": ROLL, "YAW": YAW,
                "GPS_STATUS_CODE": gps_status_code,
                "GPS_STATUS_NAME": gps_status_name
            }
            return dataPacket, imudata

        except Exception as e:
            logger.error(f"getImuDataWithHeader exception: {e}")
            return None, None

    def getGpsDataWithHeader(self, header_bytes):
        """處理已讀取header的GPS數據"""
        try:
            # 直接讀取GPS payload
            payload_data = self.__Connector.readBinaryList(53 - 4)  # 49 bytes payload
            if len(payload_data) < 49:
                return None, None

            # 組合完整的dataPacket (header + payload)
            dataPacket = bytes(header_bytes) + bytes(payload_data)

            # 按照MCU sendGpsPacketKVH的方式解析
            import struct

            # 位置資料
            latitude_bytes = bytes(dataPacket[4:12])
            latitude = struct.unpack('d', latitude_bytes)[0]

            longitude_bytes = bytes(dataPacket[12:20])
            longitude = struct.unpack('d', longitude_bytes)[0]

            altitude_bytes = bytes(dataPacket[20:24])
            altitude = struct.unpack('f', altitude_bytes)[0]

            timestamp_bytes = bytes(dataPacket[24:28])
            timestamp = struct.unpack('f', timestamp_bytes)[0]

            # UTC 時間
            utc_hour = dataPacket[28]
            utc_minute = dataPacket[29]
            utc_second = dataPacket[30]
            utc_millisecond = dataPacket[31] | (dataPacket[32] << 8)
            utc_day = dataPacket[33]
            utc_month = dataPacket[34]
            utc_year = dataPacket[35] | (dataPacket[36] << 8)

            # MCU 時間
            mcu_time_bytes = bytes(dataPacket[41:45])
            mcu_time_raw = struct.unpack('I', mcu_time_bytes)[0]
            mcu_time = mcu_time_raw / 1000.0

            # GPS 狀態
            gps_status_code = dataPacket[45]
            gps_status_name = get_gps_status_name(gps_status_code)

            # GPS頻率計算
            current_time = time.perf_counter()
            if self.__gps_last_time is not None:
                interval = current_time - self.__gps_last_time
                self.__gps_intervals.append(interval)
                if len(self.__gps_intervals) > 20:
                    self.__gps_intervals.pop(0)

            self.__gps_last_time = current_time
            self.__gps_count += 1

            if self.__gps_time_start is None:
                self.__gps_time_start = current_time

            # 計算頻率（確保 avg_freq 總是有值）
            if len(self.__gps_intervals) > 0:
                avg_interval = sum(self.__gps_intervals) / len(self.__gps_intervals)
                avg_freq = 1.0 / avg_interval if avg_interval > 0 else 0
            else:
                avg_freq = 0  # 初始化時設為 0

            # GPS資料顯示 (包含必要信息)
            print(f"GPS #{self.__gps_count}: {latitude:.6f},{longitude:.6f},{altitude:.1f}m")
            print(f"  UTC: {utc_year:04d}/{utc_month:02d}/{utc_day:02d} {utc_hour:02d}:{utc_minute:02d}:{utc_second:02d}.{utc_millisecond:03d}")
            print(f"  MCU: {mcu_time:.3f}s | 頻率: {avg_freq:.1f}Hz | Status: {gps_status_name}")

            # 打包GPS結果
            gpsdata = {
                "LATITUDE": latitude,
                "LONGITUDE": longitude,
                "ALTITUDE": altitude,
                "TIMESTAMP": timestamp,
                "UTC_HOUR": utc_hour,
                "UTC_MINUTE": utc_minute,
                "UTC_SECOND": utc_second,
                "UTC_MILLISECOND": utc_millisecond,
                "UTC_DAY": utc_day,
                "UTC_MONTH": utc_month,
                "UTC_YEAR": utc_year,
                "MCU_TIME": mcu_time,
                "GPS_STATUS_CODE": gps_status_code,
                "GPS_STATUS_NAME": gps_status_name
            }

            return dataPacket, gpsdata

        except Exception as e:
            logger.error(f"getGpsDataWithHeader exception: {e}")
            return None, None

    def getImuData(self):
        try:
            # 嘗試對齊 Header
            head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
            if head is None:
                return None, None  # 安全跳過

            # 更新讀取方式，包含新增的 GPS 狀態碼 (49 bytes = 48 + 1)
            dataPacket = getData.getdataPacket(self.__Connector, head, 36 + 12 + 1)
            if dataPacket is None or dataPacket is False:
                return None, None

            # 檢查 dataPacket 類型，避免 'bool' object is not subscriptable 錯誤
            if not isinstance(dataPacket, (list, bytes, bytearray)):
                return None, None

            # 解碼資料
            TIME, WX, WY, WZ, AX, AY, AZ, PD_TEMP, PITCH, ROLL, YAW = cmn.readAHRS_Rotate(
                dataPacket,
                POS_WX, POS_WY, POS_WZ, POS_AX, POS_AY, POS_AZ,
                POS_MCUTIME, POS_PD_TEMP, POS_PITCH, POS_ROLL, POS_YAW, 4, PRINT=0,
                use_rcs=self.use_rcs, R_CS=self.R_CS
            )

            # 提取 GPS 狀態碼 (1 byte, 位於 YAW 後面)
            gps_status_code = int(dataPacket[POS_GPS_STATUS]) if len(dataPacket) > POS_GPS_STATUS else 0xFF
            gps_status_name = get_gps_status_name(gps_status_code)


            # Kalman 濾波處理（如果開啟）
            if self.isKal:
                WX = self.pig_wx_kal.update(WX)
                WY = self.pig_wy_kal.update(WY)
                WZ = self.pig_wz_kal.update(WZ)
                AX = self.pig_ax_kal.update(AX)
                AY = self.pig_ay_kal.update(AY)
                AZ = self.pig_az_kal.update(AZ)

            # 打包結果
            imudata = {
                "TIME": TIME,
                "WX": WX, "WY": WY, "WZ": WZ,
                "AX": AX, "AY": AY, "AZ": AZ,
                "PD_TEMP": PD_TEMP,
                "PITCH": PITCH, "ROLL": ROLL, "YAW": YAW,
                "GPS_STATUS_CODE": gps_status_code,
                "GPS_STATUS_NAME": gps_status_name
            }
            return dataPacket, imudata

        except Exception as e:
            logger.error(f"getImuData exception: {e}")
            return None, None

    def getGpsData(self):
        try:
            # 嘗試對齊 GPS Header
            head = getData.alignHeader_4B(self.__Connector, HEADER_GPS)
            if head is None:
                return None, None  # 安全跳過

            # GPS 封包固定 53 bytes (4 header + 49 payload)
            dataPacket = getData.getdataPacket(self.__Connector, head, 53 - 4)  # 49 bytes payload
            if dataPacket is None or dataPacket is False:
                return None, None

            # 轉換 list 為 bytes (如果需要)
            if isinstance(dataPacket, list):
                dataPacket = bytes(dataPacket)

            # 檢查長度
            if len(dataPacket) < 49:
                print(f"GPS packet too short: {len(dataPacket)} bytes")
                return None, None

            # 直接按照 MCU-MARS sendGpsPacketKVH 的包裝方式反向解析
            import struct

            # MCU 包裝: memcpy(gps_packet + offset, union.b, size)
            # GAHRS 解析: 直接從 dataPacket[offset-4] 提取 (因為去除了 4-byte header)

            # ⚠️ CRITICAL: dataPacket 包含完整封包 (含 header)
            # MCU: gps_packet[4-11] = lat_union.b → dataPacket[4:12]
            latitude_bytes = bytes(dataPacket[4:12])
            latitude = struct.unpack('d', latitude_bytes)[0]

            # MCU: gps_packet[12-19] = lon_union.b → dataPacket[12:20]
            longitude_bytes = bytes(dataPacket[12:20])
            longitude = struct.unpack('d', longitude_bytes)[0]

            # MCU: gps_packet[20-23] = alt_union.b → dataPacket[20:24]
            altitude_bytes = bytes(dataPacket[20:24])
            altitude = struct.unpack('f', altitude_bytes)[0]

            # MCU: gps_packet[24-27] = time_union.b → dataPacket[24:28]
            timestamp_bytes = bytes(dataPacket[24:28])
            timestamp = struct.unpack('f', timestamp_bytes)[0]

            # UTC 時間: MCU gps_packet[28-36] → dataPacket[28:37]
            utc_hour = dataPacket[28]        # gps_packet[28]
            utc_minute = dataPacket[29]      # gps_packet[29]
            utc_second = dataPacket[30]      # gps_packet[30]

            # 毫秒: MCU little-endian
            utc_millisecond = dataPacket[31] | (dataPacket[32] << 8)

            utc_day = dataPacket[33]         # gps_packet[33]
            utc_month = dataPacket[34]       # gps_packet[34]

            # 年份: MCU little-endian
            utc_year = dataPacket[35] | (dataPacket[36] << 8)

            # MCU 時間: MCU gps_packet[41-44] → dataPacket[41:45]
            mcu_time_bytes = bytes(dataPacket[41:45])
            mcu_time_raw = struct.unpack('I', mcu_time_bytes)[0]
            mcu_time = mcu_time_raw / 1000.0

            # GPS 狀態: MCU gps_packet[45] → dataPacket[45]
            gps_status_code = dataPacket[45]
            gps_status_name = get_gps_status_name(gps_status_code)

            # 計算 GPS 頻率
            current_time = time.perf_counter()
            if self.__gps_last_time is not None:
                interval = current_time - self.__gps_last_time
                self.__gps_intervals.append(interval)
                # 保持最近20筆記錄來計算平均頻率
                if len(self.__gps_intervals) > 20:
                    self.__gps_intervals.pop(0)

            self.__gps_last_time = current_time
            self.__gps_count += 1

            if self.__gps_time_start is None:
                self.__gps_time_start = current_time

            # 計算即時頻率和平均頻率（確保變數總是有值）
            if len(self.__gps_intervals) > 0:
                instant_freq = 1.0 / self.__gps_intervals[-1] if self.__gps_intervals[-1] > 0 else 0
                avg_interval = sum(self.__gps_intervals) / len(self.__gps_intervals)
                avg_freq = 1.0 / avg_interval if avg_interval > 0 else 0
            else:
                instant_freq = 0
                avg_freq = 0

            # GPS資料完整顯示
            print(f"🛰️ GPS #{self.__gps_count} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📍 Position: Lat={latitude:.6f}° Lon={longitude:.6f}° Alt={altitude:.2f}m")
            print(f"⏰ UTC Time: {utc_year:04d}/{utc_month:02d}/{utc_day:02d} {utc_hour:02d}:{utc_minute:02d}:{utc_second:02d}.{utc_millisecond:03d}")
            print(f"🕒 MCU Time: {mcu_time:.3f}s | Timestamp: {timestamp:.2f}")
            print(f"📊 Status: {gps_status_name} (0x{gps_status_code:02X}) | 頻率: {avg_freq:.1f}Hz")

            # 打包 GPS 結果
            gpsdata = {
                "LATITUDE": latitude,
                "LONGITUDE": longitude,
                "ALTITUDE": altitude,
                "TIMESTAMP": timestamp,
                "UTC_HOUR": utc_hour,
                "UTC_MINUTE": utc_minute,
                "UTC_SECOND": utc_second,
                "UTC_MILLISECOND": utc_millisecond,
                "UTC_DAY": utc_day,
                "UTC_MONTH": utc_month,
                "UTC_YEAR": utc_year,
                "MCU_TIME": mcu_time,
                "GPS_STATUS_CODE": gps_status_code,
                "GPS_STATUS_NAME": gps_status_name
            }


            return dataPacket, gpsdata

        except Exception as e:
            logger.error(f"getGpsData exception: {e}")
            return None, None

    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def flushInputBuffer(self):
        print('buf before:', self.readInputBuffer())
        self.__Connector.flushInputBuffer()
        print('buf after:', self.readInputBuffer())

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

    def AutoCompAvg(self, imudata, count):
        # 計算總數
        dt_count = count
        # WX_total = 0
        # WY_total = 0
        # AX_total = 0
        # AY_total = 0
        # for i in range(dt_count):
        #     WX_total += imudata["WX"][i]
        #     WY_total += imudata["WY"][i]
        #     AX_total += imudata["AX"][i]
        #     AY_total += imudata["AY"][i]

        # 計算平均值
        WX_avg = imudata["WX"] / dt_count
        WY_avg = imudata["WY"] / dt_count
        AX_avg = imudata["AX"] / dt_count
        AY_avg = imudata["AY"] / dt_count

        avg = np.array([WX_avg, WY_avg, AX_avg, AY_avg])
        return avg

    def runAutoComp(self, s):
        logging.basicConfig(level=100)
        ms = int(s) * 1000
        t_old = time.perf_counter()
        imudataArray = {"WX":0, "WY":0, "AX":0, "AY":0}
        count_dt = 0
        while (time.perf_counter() - t_old) * 1000 < ms:
            input_buf = self.readInputBuffer()
            # 避免出現錯誤
            if not isinstance(input_buf, int):
                input_buf = -1  # 設定為-1，較好判斷這一塊發生錯誤
            self.buffer_qt.emit(input_buf)

            dataPacket, imudata = self.getImuData()
            # 取數據發生錯誤，所以將'判斷是否可以停止執行GUI的變數'設定為False，進行停止作業
            if dataPacket == False and imudata == False:
                self.occurredErr()
                break

            t2 = time.perf_counter()
            isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
            t3 = time.perf_counter()
            # err correction
            imudata = crcLib.errCorrection(isCrcFail, imudata)
            # end of err correction
            t4 = time.perf_counter()
            # print(imudata)
            QApplication.processEvents()
            try:
                imudataArray["WX"] = imudataArray["WX"] + imudata["WX"]
                imudataArray["WY"] = imudataArray["WY"] + imudata["WY"]
                imudataArray["AX"] = imudataArray["AX"] + imudata["AX"]
                imudataArray["AY"] = imudataArray["AY"] + imudata["AY"]
            except KeyError as Err:
                logger.debug(f'在執行自動補償功能撈取數據的部分，發生KeyErreor的錯誤。')
                self.occurredErr()
            except TypeError as e:
                __excType, __excObj, __excTb = sys.exc_info()
                __lineNum = __excTb.tb_lineno
                logger.error(f'1100003, Please check if there is an error in the data type being saved, line {__lineNum}.')
                self.occurredErr()
            finally:
                if self.__isOccurrErr:
                    break

            t5 = time.perf_counter()
            count_dt += 1
            print("當下撈取筆數:")
            print(str(count_dt))
            QApplication.processEvents()

        avg = self.AutoCompAvg(imudataArray, count_dt)
        self.AutoCompAvg_qt.emit(avg)
            # end of for loop

    def run(self):  # 1100003
        logging.basicConfig(level=100)
        t0 = time.perf_counter()
        while True:
            if not self.isRun:
                print('run flag is false\n')
                #self.stopIMU()
                self.imuThreadStop_qt.emit()
                break
            # End of if-condition

            # self.__imuoffset = self.do_cali(self.__imuoffset, 100)

            imudataArray = {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

            for i in range(self.arrayNum):
                input_buf = self.readInputBuffer()
                # 避免出現錯誤
                if not isinstance(input_buf, int):
                    input_buf = -1  # 設定為-1，較好判斷這一塊發生錯誤
                self.buffer_qt.emit(input_buf)

                # while self.__Connector.readInputBuffer() < self.arrayNum * 10:
                # while not self.__Connector.readInputBuffer():
                #     # print(self.__Connector.readInputBuffer())
                #     # print("No input data!")
                #     # cmn.wait_ms(500)
                #     pass
                t1 = time.perf_counter()

                # 🚀 統一封包檢測機制 - 一開始就分辨封包類型
                try:
                    # 先讀取4字節header
                    header_bytes = self.__Connector.readBinaryList(4)
                    if len(header_bytes) < 4:
                        continue

                    # 檢查header格式
                    if header_bytes[0] != 0xFE or header_bytes[2] != 0xFF or header_bytes[3] != 0x55:
                        continue

                    # 根據第2個字節分辨封包類型
                    if header_bytes[1] == 0x81:
                        # IMU封包處理
                        dataPacket, imudata = self.getImuDataWithHeader(header_bytes)
                        if dataPacket is not None and imudata is not None:
                            pass  # 繼續下面的IMU處理
                        else:
                            continue

                    elif header_bytes[1] == 0x82:
                        # GPS封包處理
                        gps_dataPacket, gpsdata = self.getGpsDataWithHeader(header_bytes)
                        if gps_dataPacket is not None and gpsdata is not None:
                            # GPS數據CRC驗證
                            isCrcFail_gps = crcLib.isCrc32Fail(gps_dataPacket, len(gps_dataPacket))
                            if not isCrcFail_gps:
                                self.gps_data_qt.emit(gpsdata)
                        continue  # GPS處理完畢，跳到下一個循環

                    else:
                        continue

                except Exception as e:
                    continue

                t2 = time.perf_counter()
                isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                t3 = time.perf_counter()
                # err correction
                corrected_imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction
                t4 = time.perf_counter()

                # 檢查 corrected_imudata 是否有效
                if corrected_imudata is False or corrected_imudata is None or not isinstance(corrected_imudata, dict):
                    # logger.warning("CRC error or invalid imudata received, skipping...")
                    continue

                imudata = corrected_imudata
                # print(imudata)
                try:
                    imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
                    imudataArray["WX"] = np.append(imudataArray["WX"], imudata["WX"])
                    imudataArray["WY"] = np.append(imudataArray["WY"], imudata["WY"])
                    imudataArray["WZ"] = np.append(imudataArray["WZ"], imudata["WZ"])
                    imudataArray["AX"] = np.append(imudataArray["AX"], imudata["AX"])
                    imudataArray["AY"] = np.append(imudataArray["AY"], imudata["AY"])
                    imudataArray["AZ"] = np.append(imudataArray["AZ"], imudata["AZ"])
                    imudataArray["PD_TEMP"] = np.append(imudataArray["PD_TEMP"], imudata["PD_TEMP"])
                    imudataArray["PITCH"] = np.append(imudataArray["PITCH"], imudata["PITCH"])
                    imudataArray["ROLL"] = np.append(imudataArray["ROLL"], imudata["ROLL"])
                    imudataArray["YAW"] = np.append(imudataArray["YAW"], imudata["YAW"])
                    imudataArray["GPS_STATUS_CODE"] = np.append(imudataArray["GPS_STATUS_CODE"], imudata["GPS_STATUS_CODE"])
                    imudataArray["GPS_STATUS_NAME"] = np.append(imudataArray["GPS_STATUS_NAME"], imudata["GPS_STATUS_NAME"])
                except KeyError as Err:
                    logger.debug(f'1200003, Key value error. Please verify the error caused by the key value.')
                    self.occurredErr()
                except TypeError as e:
                    __excType, __excObj, __excTb = sys.exc_info()
                    __lineNum = __excTb.tb_lineno
                    logger.error(f'1200003, TypeError — {e}.(Please check if there is an error in the data type being saved, line {__lineNum}.)')
                    self.occurredErr()
                finally:
                    if self.__isOccurrErr:
                        self.isRun = False

                t5 = time.perf_counter()

                debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                             + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                             + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)
            # end of for loop

            # imudataArray["TIME"] = imudataArray["TIME"] - t0

            self.offset_setting(self.__imuoffset)
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
        imuoffset["GPS_STATUS_CODE"] = [0]
        imuoffset["GPS_STATUS_NAME"] = ['']
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
