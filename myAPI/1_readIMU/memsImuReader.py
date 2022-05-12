import sys

sys.path.append("../")
from myLib.mySerial.Connector import Connector
from myLib.mySerial import getData
import time
from threading import Thread
import common as cmn


class memsImuReader(Thread):

    def __init__(self, portName: str = "COM5", baudRate: int = 230400):
        super(memsImuReader, self).__init__()
        self.__Connector = Connector(portName, baudRate)
        self.__isRun = True
        self.__oCallBacker = None
        self.__crcFail = 0
    # class constructor

    def __del__(self):
        print("class memsImuReader's destructor called!")
    # End of destructor

    @property
    def isRun(self):
        return self.__isRun
    # End of memsImuReader::isRun(getter)

    @isRun.setter
    def isRun(self, isFlag):
        self.__isRun = isFlag
    # End of ImuReader::isRun(setter)

    def connectIMU(self):
        self.__Connector.connect()
        self.writeImuCmd(5, 1)

    def disconnectIMU(self):
        self.writeImuCmd(5, 4)
        self.__Connector.disconnect()

    def writeImuCmd(self, cmd, value):
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        self.__Connector.write(data)
        cmn.wait_ms(150)
    # End of memsImuReader::writeImuCmd


if __name__ == "__main__":
    myImu = memsImuReader("COM6")
    myImu.connectIMU()
    cmn.wait_ms(1000)
    myImu.disconnectIMU()