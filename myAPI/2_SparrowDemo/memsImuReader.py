import sys

sys.path.append("../")
from myLib.mySerial.Connector import Connector
from myLib.mySerial import getData
from myLib.crcCalculator import crcLib
import time
from threading import Thread
import common as cmn
import numpy as np

IMU_DATA_STRUCTURE = {
    "NANO33_W": (0, 0, 0),
    "NANO33_A": (0, 0, 0),
    "ADXL_A": (0, 0, 0)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
SENS_ADXL355_8G = 0.0000156
SENS_NANO33_GYRO_250 = 0.00875
SENS_NANO33_AXLM_4G = 0.000122
POS_NANO33_WX = 14 - 1
POS_ADXL355_AX = 5 - 1
POS_SPARROW = 26 - 1
POS_CRC = 26 - 1
print("__name__: ", __name__)
old = time.perf_counter_ns()

class memsImuReader(Thread):

    def __init__(self, portName: str = "COM5", baudRate: int = 230400):
        super(memsImuReader, self).__init__()
        self.__Connector = Connector(portName, baudRate)
        self.__isRun = True
        self.__isCali = False
        self.__callBack = None
        self.__crcFail = 0
        self.arrayNum = 20
        self.__old_imudata = {k: (-1,)*len(IMU_DATA_STRUCTURE.get(k)) for k in set(IMU_DATA_STRUCTURE)}
        self.__imuoffset = {k: np.zeros(len(IMU_DATA_STRUCTURE.get(k))) for k in set(IMU_DATA_STRUCTURE)}

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

    @property
    def isCali(self):
        return self.__isCali

    # End of memsImuReader::isCali(getter)

    @isCali.setter
    def isCali(self, isFlag):
        self.__isCali = isFlag

    # End of ImuReader::isCali(setter)

    def connectIMU(self):
        self.__Connector.connect()
        self.writeImuCmd(5, 1)

    # End of memsImuReader::connectIMU

    def disconnectIMU(self):
        self.writeImuCmd(5, 4)
        self.__Connector.disconnect()

    # End of memsImuReader::disconnectIMU

    def writeImuCmd(self, cmd, value):
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        self.__Connector.write(data)
        cmn.wait_ms(150)
    # End of memsImuReader::writeImuCmd

    def setCallback(self, callback):
        self.__callBack = callback
    # End of memsImuReader::setCallback

    def getImuData(self):
        buffer = self.__Connector.readInputBuffer()
        print("buf: ", buffer)
        head = getData.alignHeader_4B(self.__Connector, HEADER_KVH)
        dataPacket = getData.getdataPacket(self.__Connector, head, 25)
        NANO_W, NANO_A = cmn.readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX, sf_xlm=SENS_NANO33_AXLM_4G,
                                        sf_gyro=SENS_NANO33_GYRO_250)
        ADXL_A = cmn.readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX, sf=SENS_ADXL355_8G)
        imudata = {"NANO33_W": NANO_W, "NANO33_A": NANO_A, "ADXL_A": ADXL_A}
        return dataPacket, imudata

    def readInputBuffer(self):
        return self.__Connector.readInputBuffer()

    def do_cali(self, dictContainer, cali_times):
        if self.isCali:
            self.isCali = False
            temp = dictContainer
            print("---calibrating offset start-----")
            for i in range(cali_times):
                dataPacket, imudata = self.getImuData()
                temp = cmn.dictOperation(temp, imudata, "ADD")
            temp = {k: temp.get(k) / cali_times for k in set(self.__imuoffset)}
            print("---calibrating offset stop-----")
            return temp
        else:
            return dictContainer

    def run(self):
        while True:
            if not self.isRun:
                break
            # End of if-condition
            imudataArray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
                               for k in set(IMU_DATA_STRUCTURE)}
            for i in range(self.arrayNum):

                while self.__Connector.readInputBuffer()<self.arrayNum*10:
                    print(self.__Connector.readInputBuffer())
                    pass

                dataPacket,  imudata = self.getImuData()
                isCrcFail = crcLib.isCrc32Fail(dataPacket, len(dataPacket))

                # err correction
                if not isCrcFail:
                    self.__old_imudata = imudata
                else:
                    self.__crcFail += 1
                    print("crc fail occur: ", self.__crcFail)
                    imudata = self.__old_imudata
                # end of err correction

                cmn.dictOperation(imudataArray, imudata, "APPEND")
            # end of for loop
            # print(imudataArray)
            self.__imuoffset = self.do_cali(self.__imuoffset, 100)
            self.__callBack(imudataArray, self.__imuoffset)
    # End of memsImuReader::run


def myCallBack(imudata, imuoffset):
    global old
    new = time.perf_counter_ns()
    imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
    wx = imudata["NANO33_W"][0]
    wy = imudata["NANO33_W"][1]
    wz = imudata["NANO33_W"][2]
    ax = imudata["ADXL_A"][0]
    ay = imudata["ADXL_A"][1]
    az = imudata["ADXL_A"][2]
    # print(new)
    # print(old)
    # print(cnt)
    # print("%.1f  %.2f  %.2f  %.2f" % ( (new - old)*1e-3, wx, wy, wz))
    # print("%.5f  %.5f  %.5f  %.5f  %.5f  %.5f" % (wx, wy, wz, ax, ay, az))
    print(wx)
    print(wy)
    print(wz)
    print(ax)
    print(ay)
    print(az)
    old = new

if __name__ == "__main__":
    myImu = memsImuReader("COM6")
    myImu.setCallback(myCallBack)
    myImu.isCali = True
    myImu.connectIMU()
    myImu.start()
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.disconnectIMU()
        myImu.join()
        print('KeyboardInterrupt success')
