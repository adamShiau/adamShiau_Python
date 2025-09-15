# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import json
import logging
import os
import traceback
from myLib.logProcess import logProcess

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

    def connectConn(self): # 1700001
        self.__ser.baudrate = self.__baudRate
        self.__ser.port = self.__portName
        self.__ser.timeout = 0.1
        # self.__ser.writeTimeout = 5
        self.__ser.parity = serial.PARITY_NONE
        self.__ser.stopbits = serial.STOPBITS_ONE
        self.__ser.bytesize = serial.EIGHTBITS

        try:
            self.__ser.open()
        except serial.SerialException as e:
            logger.error(f'1700001, The serial open operation failed while establishing the connection.')
            return False
        except IOError as e:
            logger.error("1700001, IOError, the device: " + self.__ser.port + " can not be found or can not be configured!")
            # sys.exit(0)
            return False
        # End of try-catch
        logger.info(self.__ser.port + " is connected")
        self.__is_open = self.__ser.is_open
        return self.__is_open

    # End of Connector::connect

    def disconnectConn(self):
        try:
            if self.__is_open:
                self.__ser.close()
            self.__is_open = self.__ser.is_open
            logger.info(self.__ser.port + " is disconnected")
        except serial.SerialException as serialErr:
            logger.error(f'1700006,{serialErr} - The serial close operation failed when disconnecting the connection.')
        return self.__is_open

    # End of Connector::close

    def write(self, data_w):  # 1700002
        try:
            data_w = bytearray(data_w)
            self.__ser.write(data_w)
        except serial.SerialTimeoutException as serErr:
            logger.error(f"1700002, {type(serErr).__name__} - write timeOut.")
        except serial.PortNotOpenError as serErr:
            logger.error(f"1700002, {type(serErr).__name__} - Port not open, please check!")
        except serial.SerialException as serErr:
            logger.error(f'1700002, {type(serErr).__name__} - The device can not be found or can not be configured.')
        except AttributeError as e:
            logger.error(f"1700002, The error is '{e}'")
        # except Exception as e:
        #     logProcess.centrailzedError(num="1700002", content=f"Other exceptional events occurred. The error is '{e}'", fileName=ExternalName_log)
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
        except serial.SerialTimeoutException as serialTimeout:
            logger.error("1700003, ERROR")
            return False
        # data = [hex(i) for i in data]
        except serial.serialutil.SerialException as serException:
            logger.error(f"1700003, Other exceptional events occurred. The error is '{serException}'")
            return False
        except AttributeError as attributeErr:
            logger.error(f'1700003, Please make sure the device is connected.')
            return False
        # except Exception as e:
        #     logProcess.centrailzedError(num="1700003", content=f"Other exceptional events occurred. The error is '{e}", fileName=ExternalName_log)
        #     return False
        else:
            if not data_r:
                cmn.print_debug('empty list', PRINT_DEBUG)
                # 此error為ValueError
                logger.error('1700003, serial read timeout: check if the input power is ON, close the GUI and re-execute.')
                return False
            return data_r

    # End of Connector::readBinaryList

    def read(self):
        return self.__ser.read()

    def readInputBuffer(self):
        # print("input buffer: %d" % self.__ser.in_waiting)
        try:
            return self.__ser.in_waiting
        except (serial.SerialException, ValueError, OSError) as e:
            logger.error(f"1700007, Errors encountered when the serial port is unavailable, disconnected, or already in use at runtime. The error is '{e}'")
            return 0

    # End of Connector::readInputBuffer

    def flushInputBuffer(self):
        try:
            self.__ser.reset_input_buffer()
            # print("flushInputBuffer")
        except serial.PortNotOpenError as notOpenErr:
            logger.error(f'1700008, PortNotOpenError, Failed to clear the serial port buffer — the port was not open.')
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

    def dump_fog_parameters(self, ch=2):
        try:
            self.__ser.write(bytearray([0xAB, 0xBA]))
            self.__ser.write([0x66, 0, 0, 0, 0x05, ch])
            time.sleep(0.5)
            self.__ser.write(bytearray([0x55, 0x56]))
            time.sleep(0.5)

            A = self.__ser.readline()
            print(A)

            # decode 成字串
            s = A.decode("utf-8").strip()

            # 把 NaN 換成 null (讓 JSON 合法)
            s = s.replace("nan", "null").replace("NaN", "null")

            parafeedback = json.loads(s)

            print(parafeedback)
            return parafeedback

        except serial.SerialException:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(
                f'Please verify that the serial port is properly connected and the device is powered, line {__lineNum}.')
            return False

        except json.JSONDecodeError:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(
                f'撈取數據並轉換為json格式的過程中，因數據格式無法轉換為json格式，所以出現json.decoder.JSONDecodeError, line {__lineNum}.')
            return False

    # def dump_fog_parameters(self, ch=2):
    #     try:
    #         self.__ser.write(bytearray([0xAB, 0xBA]))
    #         self.__ser.write([0x66, 0, 0, 0, 0x05, ch])
    #         time.sleep(0.5)
    #         self.__ser.write(bytearray([0x55, 0x56]))
    #         # self.__ser.write(bytearray([0x55, 0x56]))
    #         time.sleep(0.5)
    #         A = self.__ser.readline()
    #         print(A)
    #
    #         # decode 成字串
    #         s = A.decode("utf-8").strip()
    #
    #         # 允許 NaN 解析
    #         parafeedback = json.loads(s, strict=False)
    #
    #         print(parafeedback)
    #         return parafeedback
    #     except serial.SerialException as e:
    #         # tb = e.__traceback__  # 錯誤軌跡資訊
    #         # # 英文 -> Please verify that the serial port is properly connected and the device is powered.
    #         # logProcess.centrailzedError(num="", fileName=ExternalName_log, content="請確認序列埠是否已連接，且設備已經上電。", line=tb.tb_lineno)
    #         __excType, __excObj, __excTb = sys.exc_info()
    #         __lineNum = __excTb.tb_lineno
    #         logger.error(f'Please verify that the serial port is properly connected and the device is powered, line {__lineNum}.')
    #         return False
    #     except json.JSONDecodeError as jsonErr:
    #         # tb = jsonErr.__traceback__  # 錯誤軌跡資訊
    #         # logProcess.centrailzedError(num="", fileName=ExternalName_log, content="撈取數據並轉換為json格式的過程中，因數據格式無法轉換為json格式，所以出現json.decoder.JSONDecodeError。", line=tb.tb_lineno)
    #         __excType, __excObj, __excTb = sys.exc_info()
    #         __lineNum = __excTb.tb_lineno
    #         logger.error(f'撈取數據並轉換為json格式的過程中，因數據格式無法轉換為json格式，所以出現json.decoder.JSONDecodeError, line {__lineNum}.')
    #         return False

    def dump_cali_parameters(self, ch=2):
        try:
            self.__ser.write(bytearray([0xAB, 0xBA]))
            self.__ser.write([0x81, 0, 0, 0, 0, ch])
            time.sleep(1)
            self.__ser.write(bytearray([0x55, 0x56]))
            caliVal = self.__ser.readline()
            return json.loads(caliVal)
        except serial.SerialException as e:
            # tb = e.__traceback__  # 錯誤軌跡資訊
            # # 英文 -> Please verify that the serial port is properly connected and the device is powered.
            # logProcess.centrailzedError(num="", fileName=ExternalName_log, content="請確認序列埠是否已連接，且設備已經上電。", line=tb.tb_lineno)
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'Please verify that the serial port is properly connected and the device is powered, line {__lineNum}.')
            return False
        except json.JSONDecodeError as jsonErr:
            # tb = jsonErr.__traceback__  # 錯誤軌跡資訊
            # logProcess.centrailzedError(num="", fileName=ExternalName_log, content="撈取數據並轉換為json格式的過程中，因數據格式無法轉換為json格式，所以出現json.decoder.JSONDecodeError。", line=tb.tb_lineno)
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'撈取數據並轉換為json格式的過程中，因數據格式無法轉換為json格式，所以出現json.decoder.JSONDecodeError, line {__lineNum}.')
            return False

    def getVersion(self, ch=2):
        try:
            self.__ser.write(bytearray([0xAB, 0xBA]))
            self.__ser.write([0x65, 0, 0, 0, 0x05, ch])
            self.__ser.write(bytearray([0x55, 0x56]))
            # self.__ser.write(bytearray([0x55, 0x56]))
            VerVal = self.__ser.readline().decode('utf-8')
            return VerVal
        except serial.SerialException as e:
            # tb = e.__traceback__  # 錯誤軌跡資訊
            # # 英文 -> Please verify that the serial port is properly connected and the device is powered.
            # logProcess.centrailzedError(num="", fileName=ExternalName_log, content="請確認序列埠是否已連接，且設備已經上電。", line=tb.tb_lineno)
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'Please verify that the serial port is properly connected and the device is powered, line {__lineNum}.')
            return "Error"
        except (UnicodeDecodeError, AttributeError, TypeError) as e:
            # tb = e.__traceback__  # 錯誤軌跡資訊
            # logProcess.centrailzedError(num="", fileName=ExternalName_log, content="撈取數據並轉換為utf-8格式的過程中，出現轉換錯誤的狀況，請確認數據類型符合當下可以轉換的型態。", line=tb.tb_lineno)
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'撈取數據並轉換為utf-8格式的過程中，出現轉換錯誤的狀況，請確認數據類型符合當下可以轉換的型態, line {__lineNum}.')
            return "Error"

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

