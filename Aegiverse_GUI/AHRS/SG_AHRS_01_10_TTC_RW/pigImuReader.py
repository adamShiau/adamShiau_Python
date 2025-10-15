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
    "YAW": np.zeros(1)
}


HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
HEADER_VN300 = [0xFA, 0x05, 0x29, 0x01, 0x10, 0x00]
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

POS_PIG = POS_NANO33 + SIZE_NANO33
old = time.perf_counter_ns()


class pigImuReader(QThread):
    if not __name__ == "__main__":
        imudata_qt = Signal(object)
        imuThreadStop_qt = Signal()
        buffer_qt = Signal(int)
        AutoCompAvg_qt = Signal(object)


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

    def readVN300(self):
        self.flushInputBuffer()
        self.__Connector.send_vnwr_command("$VNSIH,0.0*48")  # reset yaw to zero
        time.sleep(0.1)
        self.__Connector.send_vnwr_command("$VNWRG,75,1,04,05,0129,0010*63")

    def stopVN300(self):
        self.__Connector.send_vnwr_command("$VNWRG,75,0,0,0*XX") # stop output
        time.sleep(0.1)
        self.__Connector.send_vnwr_command("$VNRST*4D")  # reset time


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

    def getImuData(self):
        try:
            # 嘗試對齊 Header
            head = getData.alignHeader_6B(self.__Connector, HEADER_VN300)
            if head is None:
                return None, None  # 安全跳過
            # print("Header (HEX):", " ".join(f"{b:02X}" for b in head))

            # 取得資料包
            dataPacket = getData.getdataPacket(self.__Connector, head, 50)
            if dataPacket is None:
                return None, None
            # print("dataPacket (HEX):", " ".join(f"{b:02X}" for b in dataPacket))

            # 解碼資料
            TIME, WX, WY, WZ, AX, AY, AZ, PD_TEMP, PITCH, ROLL, YAW = cmn.readVN_300(
                dataPacket, HEADER_BYTE=6, PRINT=0)

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
                "PITCH": PITCH, "ROLL": ROLL, "YAW": YAW
            }
            return dataPacket, imudata

        except Exception as e:
            logger.error(f"getImuData exception: {e}")
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

                t1 = time.perf_counter()

                dataPacket, imudata = self.getImuData()
                # 取數據發生錯誤，所以將'判斷是否可以停止執行GUI的變數'設定為False，進行停止作業
                if dataPacket == False and imudata == False:
                    print('dataPacket: run flag is false\n')
                    self.isRun = False
                    self.occurredErr()

                if not self.isRun:
                    print('run flag is false\n')
                    #self.stopIMU()
                    self.imuThreadStop_qt.emit()
                    return

                t2 = time.perf_counter()
                # isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                t3 = time.perf_counter()
                # err correction
                # imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction
                t4 = time.perf_counter()
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
    # 建立 serial 連線
    ser = Connector("COM17", 115200)
    myImu = pigImuReader(debug_en=False)
    myImu.setCallback(myCallBack)

    # 連線
    if not myImu.connectRead(ser, "COM17", 115200):
        print("Serial connect failed.")
        sys.exit(1)

    print("[1] 發送 VN300 啟動指令")
    myImu.readVN300()  # 發送 $VNRST 與 $VNWRG 設定輸出模式
    time.sleep(0.1)

    print("[2] 開始使用 getImuData() 連續撈取 (Ctrl+C 結束)...\n")

    try:
        while True:
            dataPacket, imudata = myImu.getImuData()
            # if dataPacket is not None and imudata is not None:
            #     # 這裡不印資料，由 cmn.readVN_300() 自行印出
            #     pass
            # else:
            #     print("等待資料中...")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n停止讀取。")

    myImu.stopVN300()
    myImu.disconnectRead()
    print("測試結束。")

    # try:
    #     while True:
    #         available = myImu.readInputBuffer()
    #         if available > 0:
    #             data = ser.readBinaryList(available)
    #             if data:
    #                 print("Received (HEX):", " ".join(f"{b:02X}" for b in data))
    #         time.sleep(0.05)
    # except KeyboardInterrupt:
    #     print("\n停止讀取。")
    #
    # myImu.stopVN300()
    # myImu.disconnectRead()
    # print("測試結束。")


