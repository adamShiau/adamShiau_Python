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
from myLib.myNavigation import planar_Navigation
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
    "TIME": np.zeros(1)
}

VBOX_DATA_STRUCTURE = {
    "GPS_sats": np.zeros(1),
    "Heading": np.zeros(1),
    "Heading_from_KF": np.zeros(1),
    "Altitude": np.zeros(1),
    "Latitude": np.zeros(1),
    "Longitude": np.zeros(1),
    "Velocity": np.zeros(1),
    "Vertical_velocity": np.zeros(1),
    "Accz": np.zeros(1)
}

INS_DATA_STRUCTURE = {
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
    'SPEED': np.zeros(1)
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
    if not __name__ == "__main__":
        imudata_qt = pyqtSignal(object, object)
        imuThreadStop_qt = pyqtSignal()
        buffer_qt = pyqtSignal(int)
        nav_qt = pyqtSignal(float, float)

    def __init__(self, portName: str = "None", boolCaliw=False, boolCalia=False, baudRate: int = 230400,
                 debug_en: bool = 0):
        super(pigImuReader, self).__init__()
        self.navi = planar_Navigation.planarNav()
        self.vboxdata = None
        self.Vertical_velocity = 0
        self.Velocity = 0
        self.Longitude = 0
        self.Latitude = 0
        self.Altitude = 0
        self.Heading_from_KF = 0
        self.Heading = 0
        self.GPS_sats = 0
        self.accz = 0
        self.encoder_speed = 0
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
        print('isCali setter: ', self.isCali)
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
        print('isCali_w setter: ', self.isCali_w)

    # End of ImuReader::isCali_w(setter)

    @property
    def isCali_a(self):
        return self.__isCali_a

    # End of memsImuReader::isCali_a(getter)

    @isCali_a.setter
    def isCali_a(self, isFlag):
        self.__isCali_a = bool(int(isFlag))
        self.isCali = (self.isCali_w or self.isCali_a)
        print('isCali_a setter: ', self.isCali_a)

    # End of ImuReader::isCali_a(setter)

    @property
    def encoder_speed(self):
        return self.__encoder_speed

    @encoder_speed.setter
    def encoder_speed(self, speed):
        self.__encoder_speed = speed

    @property
    def Heading(self):
        return self.__Heading

    @Heading.setter
    def Heading(self, val):
        self.__Heading = val
        self.navi.head0 = self.Heading
        print('heading setter: ', self.Heading)

    @property
    def Altitude(self):
        return self.__Altitude

    @Altitude.setter
    def Altitude(self, val):
        self.__Altitude = val
        print('Altitude setter: ', self.Altitude)

    @property
    def Latitude(self):
        return self.__Latitude

    @Latitude.setter
    def Latitude(self, val):
        self.__Latitude = val
        print('Latitude setter: ', self.Latitude)

    @property
    def Longitude(self):
        return self.__Longitude

    @Longitude.setter
    def Longitude(self, val):
        self.__Longitude = val
        print('Longitude setter: ', self.Longitude)

    @property
    def vboxdata(self):
        return self.__vboxdata

    @vboxdata.setter
    def vboxdata(self, val):
        self.__vboxdata = val

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
        self.navi.set_init(lat0=self.Latitude, lon0=self.Longitude, head0=self.Heading, hei0=self.Altitude)
        # self.navi.set_init(lat0=24.898628, lon0=121.156344, head0=self.Heading, hei0=self.Altitude)

    def stopIMU(self):
        self.writeImuCmd(2, 4)

    def setCallback(self, callback):
        self.__callBack = callback

    # End of memsImuReader::setCallback

    def getImuData(self):
        head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
        dataPacket = getData.getdataPacket(self.__Connector, head, 39)

        ADXL_AX, ADXL_AY, ADXL_AZ = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX,
                                                    sf=SENS_ADXL355_8G)
        NANO_WX, NANO_WY, NANO_WZ, \
        NANO_AX, NANO_AY, NANO_AZ = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX,
                                                   sf_xlm=SENS_NANO33_AXLM_4G,
                                                   sf_gyro=SENS_NANO33_GYRO_250)

        FPGA_TIME, ERR, STEP, PD_TEMP = cmn.readPIG(dataPacket, EN=1, PRINT=0, sf_a=self.sf_a, sf_b=self.sf_b,
                                                    POS_TIME=POS_PIG)
        if not self.isCali:
            if self.isKal:
                NANO_WZ = self.nano33_wz_kal.update(NANO_WZ)
                STEP = self.pig_wz_kal.update(STEP)
        # t = time.perf_counter()
        t = FPGA_TIME
        imudata = {"NANO33_WX": NANO_WX, "NANO33_WY": NANO_WY, "NANO33_WZ": NANO_WZ,
                   "ADXL_AX": NANO_AX, "ADXL_AY": ADXL_AY, "ADXL_AZ": ADXL_AZ, "TIME": t,
                   "PIG_ERR": ERR, "PIG_WZ": STEP, "PD_TEMP": PD_TEMP
                   }
        return dataPacket, imudata

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
                self.stopIMU()
                self.imuThreadStop_qt.emit()
                break
            # End of if-condition

            self.__imuoffset = self.do_cali(self.__imuoffset, 100)

            imudataArray = {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}
            vboxArray = {k: np.empty(0) for k in set(VBOX_DATA_STRUCTURE)}
            speedArray = np.empty(0)

            acczArray = np.empty(0)
            # print(imudataArray)

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
                t2 = time.perf_counter()
                isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))
                t3 = time.perf_counter()
                # err correction
                imudata = crcLib.errCorrection(isCrcFail, imudata)
                # end of err correction
                t4 = time.perf_counter()
                # imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND", IMU_DATA_STRUCTURE)
                # print('act.loop: ', imudataArray["TIME"], imudata["TIME"])
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

                vboxArray['GPS_sats'] = np.append(vboxArray['GPS_sats'], self.vboxdata['GPS_sats'])
                vboxArray['Heading'] = np.append(vboxArray['Heading'], self.vboxdata['Heading'])
                vboxArray['Heading_from_KF'] = np.append(vboxArray['Heading_from_KF'], self.vboxdata['Heading_from_KF'])
                vboxArray['Altitude'] = np.append(vboxArray['Altitude'], self.vboxdata['Altitude'])
                vboxArray['Latitude'] = np.append(vboxArray['Latitude'], self.vboxdata['Latitude'])
                vboxArray['Longitude'] = np.append(vboxArray['Longitude'], self.vboxdata['Longitude'])
                vboxArray['Velocity'] = np.append(vboxArray['Velocity'], self.vboxdata['Velocity'])
                vboxArray['Accz'] = np.append(vboxArray['Accz'], self.vboxdata['Accz'])
                vboxArray['Vertical_velocity'] = np.append(vboxArray['Vertical_velocity'],
                                                           self.vboxdata['Vertical_velocity'])
                speedArray = np.append(speedArray, self.encoder_speed)
                lon, lat = self.navi.track(t=imudata["TIME"], wz=imudata['PIG_WZ'], speed=self.encoder_speed/3.6,
                                hei=self.vboxdata['Altitude'])
                # lon, lat = self.navi.track(t=imudata["TIME"], wz=imudata['PIG_WZ'], speed=30, hei=self.vboxdata['Altitude'])

                self.nav_qt.emit(lon, lat)

                t5 = time.perf_counter()

                debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                             + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                             + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)

            # end of for loop

            # imudataArray["TIME"] = imudataArray["TIME"] - t0

            self.offset_setting(self.__imuoffset)
            imudataArray = cmn.dictOperation(imudataArray, self.__imuoffset, "SUB", IMU_DATA_STRUCTURE)
            imudataArray['SPEED'] = speedArray
            # imudataArray['Accz'] = acczArray
            if self.__callBack is not None:
                self.__callBack(imudataArray)
            # print('act', imudataArray)
            if not __name__ == "__main__":
                self.imudata_qt.emit(imudataArray, vboxArray)
            # print(imudataArray)

        # end of while loop

    # End of memsImuReader::run

    def offset_setting(self, imuoffset):
        imuoffset["TIME"] = [0]
        imuoffset["PD_TEMP"] = [0]
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
