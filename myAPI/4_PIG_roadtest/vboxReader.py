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
import time
from PyQt5.QtCore import QThread, pyqtSignal
from myLib import common as cmn
import numpy as np
import logging

# from pig_parameters import *

VBOX_DATA_STRUCTURE = {
    "GPS_sats": np.zeros(1),
    "Heading": np.zeros(1),
    "Heading_from_KF": np.zeros(1),
    "Altitude": np.zeros(1),
    "Latitude": np.zeros(1),
    "Longitude": np.zeros(1),
    "Velocity": np.zeros(1),
    "Vertical_velocity": np.zeros(1)
}

HEADER_VBOX_TEXT = ['$', 'V', 'B', '3', 'i', 's', '$']
HEADER_VBOX = [ord(i) for i in HEADER_VBOX_TEXT]

POS_GPS_SATS = 7
POS_GLONASS_SATS = 8
POS_BeiDou_SATS = 9
POS_Time = 10
POS_Latitude = 13
POS_Longitude = 17
POS_Velocity = 21
POS_Heading = 24
POS_Altitude = 26
POS_Vertical_velocity = 29
POS_Pitch_angle = 33
POS_Roll_angle = 35
POS_Heading_from_KF = 37
POS_Pitch_rate = 39
POS_Roll_rate = 41
POS_Yaw_rate = 43
POS_X_accel = 45
POS_Y_accel = 47
POS_Z_accel = 49
POS_Data = 51
POS_Kalman_Filter_Status = 56

old = time.perf_counter_ns()


class vboxReader(QThread):
    if not __name__ == "__main__":
        vboxdata_qt = pyqtSignal(object)
        vboxThreadStop_qt = pyqtSignal()
        vbox_buffer_qt = pyqtSignal(int)

    def __init__(self, portName: str = "None", boolCaliw=False, boolCalia=False, baudRate: int = 115200,
                 debug_en: bool = 0):
        super(vboxReader, self).__init__()
        self.__Connector = None
        self.__portName = portName
        self.__baudRate = baudRate
        self.__isRun = True
        self.__crcFail = 0
        self.arrayNum = 10
        self.__debug = debug_en
        self.__old_imudata = {k: (-1,) * len(VBOX_DATA_STRUCTURE.get(k)) for k in set(VBOX_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(1) for k in set(VBOX_DATA_STRUCTURE)}
        # print(not __name__ == "__main__")

    # class constructor

    def __del__(self):
        logger.info("class memsImuReader's destructor called!")

    # End of destructor

    @property
    def isRun(self):
        return self.__isRun

    # End of memsImuReader::isRun(getter)

    @isRun.setter
    def isRun(self, isFlag):
        self.__isRun = isFlag

    # End of ImuReader::isRun(setter)

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
        # self.writeImuCmd(2, 1)
        pass

    def stopIMU(self):
        # self.writeImuCmd(2, 4)
        pass


    # End of memsImuReader::setCallback

    def getVboxData(self):
        head = getData.alignHeader_7B(self.__Connector, HEADER_VBOX)
        dataPacket = getData.getdataPacket(self.__Connector, head, 66)
        # print('dataPacket: ', dataPacket)
        # print('\nbuf: ', self.readInputBuffer())

        GPS_sats, Heading, Heading_from_KF, Altitude, \
        Latitude, Longitude, Velocity, \
        Vertical_velocity, accz = cmn.readVBOX(dataPacket, POS_GPS_SATS, POS_Z_accel, POS_Time, POS_Heading,
                                         POS_Heading_from_KF, POS_Altitude, POS_Latitude, POS_Longitude, POS_Velocity,
                                         POS_Vertical_velocity, EN=1, PRINT=0)
        vboxdata = {"GPS_sats": GPS_sats, "Heading": Heading, "Heading_from_KF": Heading_from_KF,
                    "Altitude": Altitude, "Latitude": Latitude, "Longitude": Longitude, "Velocity": Velocity,
                    "Vertical_velocity": Vertical_velocity, "accz": accz
                    }
        return dataPacket, vboxdata

    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def run(self):
        logging.basicConfig(level=100)
        t0 = time.perf_counter()
        while True:
            if not self.isRun:
                self.stopIMU()
                self.vboxThreadStop_qt.emit()
                break
            # End of if-condition

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

                dataPacket, vboxdata = self.getVboxData()
                t2 = time.perf_counter()
                isCrcFail = crcLib.isCrc16_vbox_Fail(dataPacket, len(dataPacket))
                t3 = time.perf_counter()
                # err correction
                vboxdata = crcLib.errCorrection_vbox(isCrcFail, vboxdata)
                # end of err correction
                t4 = time.perf_counter()
                # print(vboxdata)
                # imudataArray = cmn.dictOperation(imudataArray, imudata, "APPEND", IMU_DATA_STRUCTURE)
                # imudataArray["TIME"] = np.append(imudataArray["TIME"], imudata["TIME"])
                # imudataArray["ADXL_AX"] = np.append(imudataArray["ADXL_AX"], imudata["ADXL_AX"])
                # imudataArray["ADXL_AY"] = np.append(imudataArray["ADXL_AY"], imudata["ADXL_AY"])
                # imudataArray["ADXL_AZ"] = np.append(imudataArray["ADXL_AZ"], imudata["ADXL_AZ"])
                # imudataArray["NANO33_WX"] = np.append(imudataArray["NANO33_WX"], imudata["NANO33_WX"])
                # imudataArray["NANO33_WY"] = np.append(imudataArray["NANO33_WY"], imudata["NANO33_WY"])
                # imudataArray["NANO33_WZ"] = np.append(imudataArray["NANO33_WZ"], imudata["NANO33_WZ"])
                # imudataArray["PIG_ERR"] = np.append(imudataArray["PIG_ERR"], imudata["PIG_ERR"])
                # imudataArray["PIG_WZ"] = np.append(imudataArray["PIG_WZ"], imudata["PIG_WZ"])
                # imudataArray["PD_TEMP"] = np.append(imudataArray["PD_TEMP"], imudata["PD_TEMP"])
                t5 = time.perf_counter()

                debug_info = "ACT: ," + str(input_buf) + ", " + str(round((t5 - t1) * 1000, 5)) + ", " \
                             + str(round((t2 - t1) * 1000, 5)) + ", " + str(round((t3 - t2) * 1000, 5)) + ", " \
                             + str(round((t4 - t3) * 1000, 5)) + ", " + str(round((t5 - t4) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)

            # end of for loop

            # imudataArray["TIME"] = imudataArray["TIME"] - t0

            # if self.__callBack is not None:
            #     self.__callBack(imudataArray)
            #
            if not __name__ == "__main__":
                self.vboxdata_qt.emit(vboxdata)
            # print(vboxdata)

        # end of while loop

    # End of memsImuReader::run


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
    myImu = vboxReader(debug_en=False)
    myImu.arrayNum = 1
    myImu.setCallback(myCallBack)
    myImu.connect(ser, "COM11", baudRate=115200)
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
