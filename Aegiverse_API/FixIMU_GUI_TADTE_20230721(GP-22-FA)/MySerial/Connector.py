# -*- coding:UTF-8 -*-
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

import serial
import serial.tools.list_ports
import sys

sys.path.append('../../')
import numpy as np


class Connector:
    def __init__(self, portName: str = "COM11", baudRate: int = 115200) -> None:
        self.__portName = portName
        self.__baudRate = baudRate
        self.__is_open = False
        self.__ser = serial.Serial()

    # End of constructor

    def __del__(self):
        # self.disconnect()
        logger.info("class connector's destructor called!")

    # End of destructor

    @property
    def portName(self):
        return self.__portName

    @portName.setter
    def portName(self, name):
        self.__portName = name

    @property
    def baudRate(self):
        return self.__baudRate

    @baudRate.setter
    def baudRate(self, br):
        self.__baudRate = br

    @staticmethod
    def portList():
        portlist = np.empty(0)
        portlistInfo = serial.tools.list_ports.comports()
        portNum = len(portlistInfo)

        for i in range(portNum):
            portlist = np.append(portlist, portlistInfo[i])
            # print(portlistInfo[i].device)

        return portNum, portlist

    def connectSerial(self, port=None, baudRate=None):
        if port and baudRate:
            self.__ser.baudrate = baudRate
            self.__ser.port = port
        else:
            self.__ser.baudrate = self.__baudRate
            self.__ser.port = self.__portName
        self.__ser.timeout = 10
        self.__ser.parity = serial.PARITY_NONE
        self.__ser.stopbits = serial.STOPBITS_ONE
        self.__ser.bytesize = serial.EIGHTBITS

        try:
            self.__ser.open()
            logger.info(self.__ser.port + " is connected")
            self.__is_open = self.__ser.is_open
            return True
        except IOError:
            logger.error("IOError, the device: " + self.__ser.port + " can not be found or can not be configured!")

    # End of Connector::connect

    def disconnectSerial(self):
        try:
            self.__ser.close()
            self.__is_open = self.__ser.is_open
            logger.info(self.__ser.port + " is disconnected")
            return True
        except IOError:
            logger.info("disconnect failed")

    # End of Connector::close

    def write(self, data_w):
        try:
            data_w = bytearray(data_w)
            self.__ser.write(data_w)
            return True
        except serial.SerialTimeoutException:
            logger.error("write timeOut")
        except serial.PortNotOpenError:
            logger.error("Port not open, please check!")

    def readinto(self, array):
        try:
            byte = self.__ser.readinto(array)
            return byte
        except Exception as e:
            logger.error(f"Readinto Failed : {e}")

    def readBinaryList(self, mum):
        try:
            data_r = self.__ser.read(mum)
            data_r = [i for i in data_r]
            return data_r
        except Exception as e:
            logger.error(f"ReadBinaryList Error : {e}")


    def alignHeader(self, header):
        if header is None:
            return True

        len_header = len(header)
        data_in = self.readBinaryList(len_header)
        count = 0
        if data_in:
            while 1 and count < 1000:
                if data_in == header:
                    return True
                else:
                    try:
                        data_in[:-1] = data_in[1:len_header]
                        data_in[-1] = self.readBinaryList(1)[0]
                        count += 1
                    except Exception as e:
                        logger.error(f'alignHeader Error : {e}')
                        break
            logger.error("Align Header Timeout")

    def getdataPacket(self, header, rbytes=25):
        if self.alignHeader(header):
            rdata = self.readBinaryList(rbytes)
            if rdata and header:
                return header + rdata
            return rdata

    def read(self):
        try:
            return self.__ser.read()
        except Exception as e:
            logger.error(f'Read Error: {e}')

    def readInputBuffer(self):
        try:
            return self.__ser.in_waiting
        except Exception as e:
            logger.error(f'readInputBuffer Error: {e}')

    def flushInputBuffer(self):
        try:
            self.__ser.reset_input_buffer()
            return True
        except Exception as e:
            logger.error(f'flushInputBuffer Error: {e}')

    def flushOutputBuffer(self):
        try:
            self.__ser.reset_output_buffer()
            return True
        except Exception as e:
            logger.error(f'flushOutputBuffer Error: {e}')

    def getByteMessage(self):
        pass

    def ByteMessageParsing(self, message):
        pass

    # def selectCom(self):
    #     self.comPort = np.empty(0)
    #     portlist = serial.tools.list_ports.comports()
    #     self.portNum = len(portlist)
    #     for i in range(self.portNum):
    #         self.comPort = np.append(self.comPort, portlist[i])


if __name__ == "__main__":
    print("running Connector.py")
    HEADER_VBOX_TEXT = ['$', 'V', 'B', '3', 'i', 's', '$']
    HEADER_VBOX_TEXT = [ord(i) for i in HEADER_VBOX_TEXT]
    DATA_LENGTH = 66

    ser = Connector("COM18", 115200)
    ser.connectSerial()
    ser.flushInputBuffer()
    # ser.write([5, 0, 0, 0, 1])
    '''for sparrow test
    ser.write([6, 0, 0, 0, 3])
    time.sleep(1)
    ser.write([6, 0, 0, 0, 1])
    '''

    old_time = 0
    try:
        while True:
            print(ser.getdataPacket(None, DATA_LENGTH))

    except KeyboardInterrupt:
        ser.write([5, 0, 0, 0, 4])
        # ser.write([6, 0, 0, 0, 4])
        ser.disconnectSerial()
    pass
