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

sys.path.append("../")
from MySerial.Connector import Connector
import time
from PyQt5.QtCore import QThread, pyqtSignal
from MySerial.MessageReader import *
import logging


VBOX_DATA_STRUCTURE = {
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


class VBOXReader(Connector):
    def __init__(self, portName: str = "None", baudRate: int = 115200, debug_en: bool = 0):
        super().__init__()
        if portName != "None":
            self.portName = portName
            self.baudRate = baudRate
        self.__debug = debug_en
        self.__my_CRC = MyCRC()

        self.__HEADER_VBOX_TEXT = ['$', 'V', 'B', '3', 'i', 's', '$']
        self.__HEADER_VBOX = [ord(i) for i in self.__HEADER_VBOX_TEXT]
        self.__DATA_BYTES_LEN_LIST = [1, 1, 1, 3, 4, 4, 3, 2, 3, 3, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 1, 2, 2, 3,
                                      3, 2, 2]
        self.__HEADER_DATA_LIST = ["GPS", "GLONASS", "BeiDou", "Time", "Latitude", "Longitude", "Velocity",
                                   'Heading', 'Altitude', 'Vertical_Vel', 'Solution_type', "Pitch_KF", "Roll_KF",
                                   "Heading_KF", "Pitch_rate", "Roll_rate", "Yaw_rate", "Acc_X", "Acc_Y", "Acc_Z",
                                   "Date", "Trigger_time", "KF_Status", "Pos_Quality", 'Vel_Quality',
                                   'T1', "Wheel_vel1", "Wheel_vel2", "Heading2_KF", "Checksum"]
        self.__DATA_SIGN_LIST = [1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
                                 1]
        self.__SCALE = [1, 1, 1, 0.01, 0.0000001, 0.0000001, 0.000277778, 0.01, 0.01, 0.001, 1, 0.01, 0.01, 0.01, 0.01,
                        0.01, 0.01, 0.01, 0.01, 0.01, 1, 0.000001, 1, 1, 0.001, 0.0000001, 0.001, 0.001, 0.01, 1]

    def getByteMessage(self):
        datapackage = self.getdataPacket(self.__HEADER_VBOX, sum(self.__DATA_BYTES_LEN_LIST))
        if datapackage:
            return datapackage
        else:
            logger.error("getByteMessage Error: No datapackage")

    def ByteMessageParsing(self, message):
        my_data = {}
        bytes_parsed = 0
        first_byte = ["MSB" for _ in range(len(self.__HEADER_DATA_LIST))]
        message_no_header = message[7:]
        try:
            for name, length, sign, type_first, scale in zip(self.__HEADER_DATA_LIST, self.__DATA_BYTES_LEN_LIST,
                                                             self.__DATA_SIGN_LIST, first_byte, self.__SCALE):
                data_hex = message_no_header[bytes_parsed:bytes_parsed + length]
                my_data[name] = convert2Int(data_hex, length, sign, type_first) * scale
                # if not isinstance(my_data[name], int):
                #     my_data[name] = round(my_data[name], 2)
                bytes_parsed += length

            isCrcFail = self.__my_CRC.isCRCPass(message)
            my_data = self.__my_CRC.errCorrection(isCrcFail, my_data)
            return my_data
        except Exception as e:
            logger.error(f"MessageParsing Error: {e}")


class ReaderQthread(QThread):
    data_qt = pyqtSignal(object)
    ThreadStop_qt = pyqtSignal()
    buffer_qt = pyqtSignal(int)

    def __init__(self, sensor: Connector, debug_en: bool = 0):
        super(ReaderQthread, self).__init__()
        self.__sensor = sensor
        self.isRun = False
        self.__debug_en = debug_en
        self.arrayNum = 10

    # class constructor

    def __del__(self):
        logger.info("class destructor called!")

    # End of destructor

    @property
    def isRun(self):
        return self.__isRun

    # End of isRun(getter)

    @isRun.setter
    def isRun(self, isFlag):
        self.__isRun = isFlag

    # End of isRun(setter)

    def resetStruck(self):
        return {k: np.empty(0) for k in set(VBOX_DATA_STRUCTURE)}

    def run(self):
        logging.basicConfig(level=100)
        while True:
            try:
                VBOXData = self.resetStruck()
                #print(self.isRun)
                if not self.isRun:
                    #self.ThreadStop_qt.emit()
                    print("break for迴圈")
                    break
                # End of if-condition
                dataPacket = self.__sensor.getByteMessage()
                if not self.isRun:
                    #self.ThreadStop_qt.emit()
                    print("break for迴圈2")
                    break
                vbox_data = self.__sensor.ByteMessageParsing(dataPacket)

                VBOXData["GPS"] = np.append(VBOXData["GPS"], vbox_data["GPS"])
                VBOXData["GLONASS"] = np.append(VBOXData["GLONASS"], vbox_data["GLONASS"])
                VBOXData["BeiDou"] = np.append(VBOXData["BeiDou"], vbox_data["BeiDou"])
                VBOXData["VBOXTime"] = np.append(VBOXData["VBOXTime"], vbox_data["Time"])
                VBOXData["Latitude"] = np.append(VBOXData["Latitude"], vbox_data["Latitude"])
                VBOXData["Longitude"] = np.append(VBOXData["Longitude"], vbox_data["Longitude"])
                VBOXData["Velocity"] = np.append(VBOXData["Velocity"], vbox_data["Velocity"])
                VBOXData["Heading"] = np.append(VBOXData["Heading"], vbox_data["Heading"])
                VBOXData["Altitude"] = np.append(VBOXData["Altitude"], vbox_data["Altitude"])
                VBOXData["Vertical_Vel"] = np.append(VBOXData["Vertical_Vel"], vbox_data["Vertical_Vel"])
                VBOXData["Pitch_KF"] = np.append(VBOXData["Pitch_KF"], vbox_data["Pitch_KF"])
                VBOXData["Roll_KF"] = np.append(VBOXData["Roll_KF"], vbox_data["Roll_KF"])
                VBOXData["Heading_KF"] = np.append(VBOXData["Heading_KF"], vbox_data["Heading_KF"])
                VBOXData["Pitch_rate"] = np.append(VBOXData["Pitch_rate"], vbox_data["Pitch_rate"])
                VBOXData["Roll_rate"] = np.append(VBOXData["Roll_rate"], vbox_data["Roll_rate"])
                VBOXData["Yaw_rate"] = np.append(VBOXData["Yaw_rate"], vbox_data["Yaw_rate"])
                VBOXData["Acc_X"] = np.append(VBOXData["Acc_X"], vbox_data["Acc_X"])
                VBOXData["Acc_Y"] = np.append(VBOXData["Acc_Y"], vbox_data["Acc_Y"])
                VBOXData["Acc_Z"] = np.append(VBOXData["Acc_Z"], vbox_data["Acc_Z"])
                VBOXData["Date"] = np.append(VBOXData["Date"], vbox_data["Date"])
                VBOXData["KF_Status"] = np.append(VBOXData["KF_Status"], vbox_data["KF_Status"])
                VBOXData["Pos_Quality"] = np.append(VBOXData["Pos_Quality"], vbox_data["Pos_Quality"])
                VBOXData["Vel_Quality"] = np.append(VBOXData["Vel_Quality"], vbox_data["Vel_Quality"])
                VBOXData["Heading2_KF"] = np.append(VBOXData["Heading2_KF"], vbox_data["Heading2_KF"])

                # print(VBOXData)

                    #print(vbox_data)

                if not __name__ == "__main__":
                    self.data_qt.emit(VBOXData)
            except:
                break
    # end of while loop
    # End of run

    def connectSerial(self):
        self.__sensor.connectSerial()

    def disconnectSerial(self):
        self.__sensor.disconnectSerial()


if __name__ == "__main__":
    received_data = []
    vbox = VBOXReader("COM6", baudRate=115200,debug_en=False)
    myImu = ReaderQthread(vbox, debug_en=False)
    # myImu.data_qt.connect(lambda mydata: received_data.append(mydata))

    myImu.connectSerial()
    myImu.isRun = True
    start_time = time.time()
    myImu.start()
    try:
        while True:
            # time.sleep(.1)
            pass
    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.disconnectSerial()
        myImu.wait()
        print('KeyboardInterrupt success')
