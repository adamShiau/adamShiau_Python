# -*- coding:UTF-8 -*-

import serial
import serial.tools.list_ports
import time
import sys
import numpy as np


class Connector:
    def __init__(self, portName: str = "COM5", baudRate: int = 230400) -> None:
        self.__portName = portName
        self.__baudRate = baudRate
        self.__is_open = False
        self.__ser = serial.Serial()

    # End of constructor

    def __del__(self):
        # self.disconnect()
        print("class connector's destructor called!")

    # End of destructor

    def connect(self):
        self.__ser.baudrate = self.__baudRate
        self.__ser.port = self.__portName
        # self.__ser.timeout = 1
        # self.__ser.writeTimeout = 1
        self.__ser.parity = serial.PARITY_NONE
        self.__ser.stopbits = serial.STOPBITS_ONE
        self.__ser.bytesize = serial.EIGHTBITS

        try:
            self.__ser.open()
        except IOError:
            print("IOError, the device: " + self.__ser.port + " can not be found or can not be configured!")
            sys.exit(0)
        # End of try-catch
        print(self.__ser.name + " is connected")
        self.__is_open = self.__ser.is_open

    # End of Connector::connect

    def disconnect(self):
        self.__ser.close()
        self.__is_open = self.__ser.is_open
        print(self.__ser.name + " is disconnected")

    # End of Connector::close

    def write(self, data_w):
        try:
            data_w = bytearray(data_w)
            print(self.__ser.write(data_w))
        except serial.SerialTimeoutException:
            print("write timeOut")
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
        except:
            print("ERROR")
        # data = [hex(i) for i in data]
        else:
            return data_r

    # End of Connector::readBinaryList

    def readInputBuffer(self):
        # print("input buffer: %d" % self.__ser.in_waiting)
        return self.__ser.in_waiting

    # End of Connector::readInputBuffer

    def flushInputBuffer(self):
        self.__ser.reset_input_buffer()

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


if __name__ == "__main__":
    print("running Connector.py")
    old_time = time.perf_counter_ns()
    ser = Connector("COM6")
    ser.connect()
    ser.flushInputBuffer()
    ser.write([5, 0, 0, 0, 1])
    try:
        while 1:
            # if ser.readInputBuffer() > 0:
            new = time.perf_counter_ns()
            print("buf: ", ser.readInputBuffer())
            print(ser.readBinaryList(29))
            print("%.1f\n" % ((new - old_time) * 1e-3))
            old_time = new
            time.sleep(1e-6)

    except KeyboardInterrupt:
        ser.write([5, 0, 0, 0, 4])
        ser.disconnect()
    pass