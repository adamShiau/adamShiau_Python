# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import json
import logging

from serial.serialutil import SerialException

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import serial
import serial.tools.list_ports
import time
import sys
sys.path.append('../../')
import numpy as np
import myLib.common as cmn

PRINT_DEBUG = 0

class Connector:
    def __init__(self, portName: str = "COM11", baudRate: int = 115200) -> None:
        # self.portlist = None
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

    def portList(self):
        portlist = np.empty(0)
        portlistInfo = serial.tools.list_ports.comports()
        portNum = len(portlistInfo)

        for i in range(portNum):
            portlist = np.append(portlist, portlistInfo[i])
            # print(portlistInfo[i].device)

        return portNum, portlist

    def connectConn(self):
        self.__ser.baudrate = self.__baudRate
        self.__ser.port = self.__portName
        self.__ser.timeout = 25
        # self.__ser.writeTimeout = 5
        self.__ser.parity = serial.PARITY_NONE
        self.__ser.stopbits = serial.STOPBITS_ONE
        self.__ser.bytesize = serial.EIGHTBITS

        try:
            self.__ser.open()
        except IOError:
            logger.error("IOError, the device: " + self.__ser.port + " can not be found or can not be configured!")
            #sys.exit(0)
            self.__is_open = False
            return self.__is_open
        except Exception as e:
            logger.error(f"Other exceptional events occurred. The error is '{e}'")
            self.__is_open = False
            return self.__is_open
        # End of try-catch
        logger.info(self.__ser.port + " is connected")
        self.__is_open = self.__ser.is_open
        return self.__is_open

    # End of Connector::connect

    def disconnectConn(self):
        self.__ser.close()
        self.__is_open = self.__ser.is_open
        logger.info(self.__ser.port + " is disconnected")
        return self.__is_open

    # End of Connector::close

    def write(self, data_w):
        try:
            data_w = bytearray(data_w)
            self.__ser.write(data_w)
        except serial.SerialTimeoutException:
            logger.error("write timeOut")
        except serial.PortNotOpenError:
            logger.error("Port not open, please check!")
        except SerialException:
            logger.error("The device can not be found or can not be configured.")
        except Exception as e:
            logger.error(f"Other exceptional events occurred. The error is '{e}'")
        # End of try-catch

    # End of Connector::write

    def readinto(self, array):
        byte = self.__ser.readinto(array)
        return byte

    # End of Connector::readinto

    def readBinaryList(self, mum):
        try:
            data_r = self.__ser.read(mum)
            data_r = [i for i in data_r]
        except serial.SerialException:
            logger.error("ERROR")
            return False
        except Exception as e:
            logger.error(f"Other exceptional events occurred. The error is '{e}'")
            return False
        # data = [hex(i) for i in data]
        else:
            if not data_r:
                cmn.print_debug('empty list', PRINT_DEBUG)
                logger.error('serial read timeout: check if the input power is ON, close the GUI and re-excute.')
                return False
                #sys.exit()
            return data_r

    # End of Connector::readBinaryList

    def read(self):
        return self.__ser.read()

    def readInputBuffer(self):
        #print("input buffer: %d" % self.__ser.in_waiting)
        return self.__ser.in_waiting

    # End of Connector::readInputBuffer

    def flushInputBuffer(self):
        if self.__ser.is_open:
            self.__ser.reset_input_buffer()
        # print("flushInputBuffer")
        pass

    # End of Connector::flushInputBuffer

    def flushOutputBuffer(self):
        self.__ser.reset_output_buffer()

    # End of Connector::flushOutputBuffer

    def selectCom(self):
        self.comPort = np.empty(0)
        portlist = serial.tools.list_ports.comports()
        self.portNum = len(portlist)

        for i in range(self.portNum):
            self.comPort = np.append(self.comPort, portlist[i])

    def dump_fog_parameters(self, ch=3):
        self.__ser.write(bytearray([0xAB, 0xBA]))
        self.__ser.write([0x66, 0, 0, 0, 0x05, ch])
        self.__ser.write(bytearray([0x55, 0x56]))
        # self.__ser.write(bytearray([0x55, 0x56]))
        A = self.__ser.readline()
        #print(A)
        try:
            parafeedback = json.loads(A)
            return parafeedback
        except json.JSONDecodeError:
            logger.error("執行參數撈取出現錯誤。")
            return "無法取得值"

    def dump_cali_parameters(self, ch=2):
        self.__ser.write(bytearray([0xAB, 0xBA]))
        self.__ser.write([0x81, 0, 0, 0, 0, ch])
        self.__ser.write(bytearray([0x55, 0x56]))
        caliVal = self.__ser.read_until(b'\n')
        try:
            return json.loads(caliVal)
        except json.JSONDecodeError:
            logger.error("執行撈取misalignment參數出現錯誤。")
            return False


    def getVersion(self, ch=2):
        self.__ser.write(bytearray([0xAB, 0xBA]))
        self.__ser.write([0x65, 0, 0, 0, 0x05, ch])
        self.__ser.write(bytearray([0x55, 0x56]))
        # self.__ser.write(bytearray([0x55, 0x56]))
        try:
            return self.__ser.readline().decode('utf-8')
        except Exception as e:
            logger.error("執行撈取設備版號出現錯誤。")
            return "Error"

    def dump_SN_parameters(self, ch=2):
        self.__ser.write(bytearray([0xAB, 0xBA]))
        self.__ser.write([0x82, 0, 0, 0, 0, ch])
        self.__ser.write(bytearray([0x55, 0x56]))
        # 透過修改撈取的方式，如果暫存區有12字節就撈取，避免受timeout的影響
        SNAscii = self.__ser.read(12)
        # # 將ASCII轉換為文字
        # # 當接收的資料格式為"72 101 108 108 111 32 87 111 114 108 100 33"
        # # 字串形式的ASCII碼，可以使用下方的轉換方式
        # SNAscii_split = SNAscii
        if SNAscii != b'':
        #     if isinstance(SNAscii, str):
        #         SNAscii_split = map(int, SNAscii.split())
        #     # 如果撈取的資料格式為[72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 33]
        #     # 可以指使用下列的程式碼做轉換
        #     SNStr = ''.join(map(chr, SNAscii_split))
        #     return SNStr
            return SNAscii.decode('ascii')
        elif SNAscii == b'':
            return "發生參數值為空的狀況"


    def readLine(self):
        return self.__ser.readline()

    # def dumpFogParameter(self):
    #     self.writeImuCmd(66, 5)
    #     s = self.__Connector.readline()
    #     print(s)


if __name__ == "__main__":
    print("running Connector.py")
    old_time = time.perf_counter_ns()
    ser = Connector("COM17", 115200)
    ser.connect()
    ser.flushInputBuffer()
    ser.write(bytearray([0xAB, 0xBA]))
    ser.write([0x01, 0, 0, 0, 0x02, 0x02])
    ser.write(bytearray([0x55, 0x56]))
    para = ser.readLine().decode('utf-8')
    start_index = para.find("$")
    end_index = para.find("*")
    para2 = para[start_index+1:end_index]
    checkSum = para[-4:-2]
    heading = float(para2[4:10])
    print(para)
    print(heading)
    print(checkSum)

    # print(start_index)
    # print(end_index)

    checksum_cal = 0
    # [checksum = checksum ^ ord(i) for i in para2]
    for i in para2:
        checksum_cal = checksum_cal ^ ord(i)
    # a=str(hex(checksum))[-2:]
    # print('hihi')
    # print(a)
    print(checksum_cal)
    print((checkSum))
    # print(int(a) == int(checkSum))
    print()
    # para = ser.dump_fog_parameters()
    # print(para)
    # print(para["FREQ"])
    # print(para["SF0"])

    # print(line.decode('utf-8'))
    # for i in range(200):
    #     data = ser.read()
    #     print(data.decode('utf-8'), end='')
    '''for sparrow test
    ser.write([6, 0, 0, 0, 3])
    time.sleep(1)
    ser.write([6, 0, 0, 0, 1])
    '''

    # old_time = 0
    # try:
    #     while True:
    #         if ser.readInputBuffer() > 22:
    #             print("buf: ", ser.readInputBuffer())
    #             new = time.perf_counter_ns()
    #             print(ser.readBinaryList(22))
    #             print("%.1f\n" % ((new - old_time) * 1e-3))
    #             old_time = new
    #             cmn.wait_ms(4)
    #
    # except KeyboardInterrupt:
    #     ser.write(bytearray([0xAB, 0xBA]))
    #     ser.write([1, 0, 0, 0, 4, 2])
    #     ser.write(bytearray([0x55, 0x56]))
    #     # ser.write([6, 0, 0, 0, 4])
    #     ser.disconnect()
    # pass

