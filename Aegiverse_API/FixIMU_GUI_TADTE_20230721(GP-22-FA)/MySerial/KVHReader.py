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


KVH_DATA_STRUCTURE = {
    "kvh_wx": np.zeros(1),
    "kvh_wy": np.zeros(1),
    "kvh_wz": np.zeros(1),
    "kvh_ax": np.zeros(1),
    "kvh_ay": np.zeros(1),
    "kvh_az": np.zeros(1),
    "kvh_status": np.zeros(1),
    "kvh_seq_num": np.zeros(1),
    "kvh_Temperature": np.zeros(1)
}

class KVHReader(Connector):
    def __init__(self, portName: str = "None", baudRate: int = 115200, debug_en: bool = 0):
        super().__init__()
        if portName != "None":
            self.portName = portName
            self.baudRate = baudRate
        self.__debug = debug_en
        self.__my_CRC = MyCRC()

        self.__HEADER = [0xFE, 0x81, 0xFF, 0x55]

        self.__DATA_BYTES_LEN_LIST = [4, 4, 4, 4, 4, 4, 1, 1, 2]
        self.__HEADER_DATA_LIST = ['kvh_wx', 'kvh_wy', 'kvh_wz', 'kvh_ax', 'kvh_ay', 'kvh_az', 'kvh_status',
                                   'kvh_seq_num', 'kvh_Temperature']
        self.__DATA_SIGN_LIST = [0, 0, 0, 0, 0, 0, 1, 1, 1]
        self.__SCALE = [1 for _ in range(9)]
        self.__data_type = ['float', 'float', 'float', 'float', 'float', 'float', 'int', 'int', 'int']

    def getByteMessage(self):
        datapackage = self.getdataPacket(self.__HEADER, sum(self.__DATA_BYTES_LEN_LIST))
        if datapackage:
            return datapackage
        else:
            logger.error("getByteMessage Error: No datapackage")

    def ByteMessageParsing(self, message):
        my_data = {}
        bytes_parsed = 0
        first_byte = ["MSB" for _ in range(len(self.__HEADER_DATA_LIST))]
        message_no_header = message[len(self.__HEADER):]
        try:
            for name, length, sign, type_first, scale, data_type in zip(self.__HEADER_DATA_LIST,
                                                                        self.__DATA_BYTES_LEN_LIST,
                                                                        self.__DATA_SIGN_LIST, first_byte, self.__SCALE,
                                                                        self.__data_type):
                data_hex = message_no_header[bytes_parsed:bytes_parsed + length]
                if data_type == "int":
                    my_data[name] = convert2Int(data_hex, length, sign, type_first) * scale
                elif data_type == "float":
                    my_data[name] = convert2Float(data_hex, length, type_first) * scale
                if not isinstance(my_data[name], int):
                    my_data[name] = round(my_data[name], 2)
                bytes_parsed += length

            # isCrcFail = self.__my_CRC.isCRCPass(message)
            # my_data = self.__my_CRC.errCorrection(isCrcFail, my_data)
            return my_data
        except Exception as e:
            logger.error(f"MessageParsing Error: {e}")


class KVHReaderQthread(QThread):
    KVHdata_qt = pyqtSignal(object)
    ThreadStop_qt = pyqtSignal()
    buffer_qt = pyqtSignal(int)

    def __init__(self, sensor: Connector, debug_en: bool = 0):
        super(KVHReaderQthread, self).__init__()
        self.__sensor = sensor
        self.isRun = False
        self.__debug_en = debug_en

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
        return {k: np.empty(0) for k in set(KVH_DATA_STRUCTURE)}

    def run(self):
        logging.basicConfig(level=100)
        kvh_list = ['kvh_wx', 'kvh_wy', 'kvh_wz', 'kvh_ax', 'kvh_ay', 'kvh_az', 'kvh_status',
         'kvh_seq_num', "kvh_Temperature"]
        while True:
            KVHData = self.resetStruck()
            if not self.isRun:
                self.ThreadStop_qt.emit()
                break
            # End of if-condition

            for i in range(10):
                dataPacket = self.__sensor.getByteMessage()
                if not self.isRun:
                    self.ThreadStop_qt.emit()
                    break
                KVH_data = self.__sensor.ByteMessageParsing(dataPacket)

                # print(KVH_data[kvh_list[8]])
                KVHData[kvh_list[0]] = np.append(KVHData[kvh_list[0]], KVH_data[kvh_list[0]])
                KVHData[kvh_list[1]] = np.append(KVHData[kvh_list[1]], KVH_data[kvh_list[1]])
                KVHData[kvh_list[2]] = np.append(KVHData[kvh_list[2]], KVH_data[kvh_list[2]])
                KVHData[kvh_list[3]] = np.append(KVHData[kvh_list[3]], KVH_data[kvh_list[3]])
                KVHData[kvh_list[4]] = np.append(KVHData[kvh_list[4]], KVH_data[kvh_list[4]])
                KVHData[kvh_list[5]] = np.append(KVHData[kvh_list[5]], KVH_data[kvh_list[5]])
                KVHData[kvh_list[6]] = np.append(KVHData[kvh_list[6]], KVH_data[kvh_list[6]])
                KVHData[kvh_list[7]] = np.append(KVHData[kvh_list[7]], KVH_data[kvh_list[7]])
                KVHData[kvh_list[8]] = np.append(KVHData[kvh_list[8]], KVH_data[kvh_list[8]])

                # print(KVH_data)
            #
            self.KVHdata_qt.emit(KVHData)

    # end of while loop
    # End of run

    def connectSerial(self):
        self.__sensor.connectSerial()

    def disconnectSerial(self):
        self.__sensor.disconnectSerial()


if __name__ == "__main__":
    received_data = []
    p1750 = KVHReader("COM16", baudRate=115200, debug_en=True)
    KVH_myImu = KVHReaderQthread(p1750, debug_en=True)
    # myImu.data_qt.connect(lambda mydata: received_data.append(mydata))

    KVH_myImu.connectSerial()
    KVH_myImu.isRun = True
    start_time = time.time()
    KVH_myImu.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        KVH_myImu.isRun = False
        KVH_myImu.disconnectSerial()
        KVH_myImu.wait()
        print('KeyboardInterrupt success')
