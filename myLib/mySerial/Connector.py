# -*- coding:UTF-8 -*-

import serial
import time
import sys


class Connector:
    def __init__(self, portName: str = "COM15", baudRate: int = 230400) -> None:
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
        self.__ser.timeout = 1
        self.__ser.writeTimeout = 1
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
        data_r = self.__ser.read(mum)
        data_r = [i for i in data_r]
        # data = [hex(i) for i in data]
        return data_r

    # End of Connector::readBinaryList

    def readInputBuffer(self):
        print("input buffer: %d" % self.__ser.in_waiting)

    # End of Connector::readInputBuffer

    def flushInputBuffer(self):
        self.__ser.reset_input_buffer()

    # End of Connector::flushInputBuffer

    def flushOutputBuffer(self):
        self.__ser.reset_output_buffer()

    # End of Connector::flushOutputBuffer


if __name__ == "__main__":
    print("running Connector.py")
    old_time = time.perf_counter()
    ser = Connector("COM5")
    ser.connect()
    ser.write([5, 0, 0, 0, 1])
    try:
        while 1:
            ser.readInputBuffer()
            print(ser.readBinaryList(29))
            print("%f\n" % ((time.perf_counter() - old_time) * 1e6))
            old_time = time.perf_counter()

    except KeyboardInterrupt:
        ser.write([5, 0, 0, 0, 4])
        ser.disconnect()
