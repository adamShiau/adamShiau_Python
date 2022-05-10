import serial
import sys
import time


class mySerial:

    def __init__(self, strPortName="COM15", iBaudRate=115200, fTimeOut=0.00001):
        self.__strPortName = strPortName
        self.__iBaudRate = iBaudRate
        self.__fTimeOut = fTimeOut
        self.__is_open = False
        self.__ser = serial.Serial()
        self.__t_start = 0

    def connect(self):
        self.__ser.baudrate = self.__iBaudRate
        self.__ser.port = self.__strPortName
        # self.__ser.timeout = None
        # self.__ser.writeTimeout = self.__fTimeOut
        self.__ser.timeout = self.__fTimeOut
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

    # End of ImuConnector::connect

    def close(self):
        self.__ser.close()
        self.__is_open = self.__ser.is_open
        print(self.__ser.name + " is disconnected")
    # End of ImuConnector::close

    def readInputBuffer(self):
        print(self.__ser.in_waiting)

    def delay_ms(self, delay):
        while (time.perf_counter() - self.__t_start) < delay*1e-3:
            pass
        self.__t_start = time.perf_counter()

    def flush(self):
        self.__ser.reset_input_buffer()

    def readTimeOut(self):
        print(self.__ser.timeout)

    def readBinaryList(self, mum):
        data = self.__ser.read(mum)
        # print(type(data))
        # data = [ord(i) for i in data]
        data = [hex(i) for i in data]
        print(data)
        return data

if __name__ == "__main__":
    ser = mySerial("COM8")
    ser.connect()
    t_start = time.perf_counter()
    # while (time.perf_counter() - t_start) < 5:
    try:
        while 1:
            # ser.delay_ms(500)
            # ser.readInputBuffer()
            x=ser.readBinaryList(4)
            ser.readTimeOut()
    # ser.flush()

    except KeyboardInterrupt:
        ser.close()

