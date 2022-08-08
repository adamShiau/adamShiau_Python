import serial
import time
from threading import Thread
import numpy as np

# global variable defined for error correction
err_correction_data = 0
crcFailCnt = 0

IMU_DATA_STRUCTURE = {
    "PIG_WZ": np.zeros(1),
    "PD_TEMP": np.zeros(1)
}

HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
POS_PIG = 4


def convert2Sign_4B(datain):
    shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
    if (datain[0] >> 7) == 1:
        return shift_data - (1 << 32)
    else:
        return shift_data


def convert2Temperature(datain):
    temp = datain[0] + (datain[1] >> 7) * 0.5
    return temp


def readPIG(dataPacket, EN=1, POS_TIME=25, sf_a=1.0, sf_b=0, PRINT=0):
    if EN:
        temp_fog = dataPacket[POS_TIME + 8:POS_TIME + 12]
        temp_PD_temperature = dataPacket[POS_TIME + 12:POS_TIME + 14]
        step_dps = convert2Sign_4B(temp_fog) * sf_a + sf_b
        PD_temperature = convert2Temperature(temp_PD_temperature)
    else:
        step_dps = 0
        PD_temperature = 0
    # End of if-condition

    if PRINT:
        print(round(step_dps, 3), end='\t\t')
        print(round(step_dps * 3600, 3), end='\t\t')
        print(round(PD_temperature, 1))
    # End of if-condition

    return step_dps, PD_temperature


def alignHeader_4B(comportObj, header):
    data = comportObj.read(4)
    datain = [i for i in data]
    while 1:
        if datain == header:
            return datain
        else:
            try:
                datain[0] = datain[1]
                datain[1] = datain[2]
                datain[2] = datain[3]
                datain[3] = comportObj.readB(1)[0]
            except IndexError:
                break


def crc_32(message, nBytes):
    WIDTH = 32
    TOPBIT = (1 << (WIDTH - 1))
    POLYNOMIAL = 0x04C11DB7
    remainder = 0xFFFFFFFF
    for byte in range(0, nBytes):
        remainder = remainder ^ (message[byte] << (WIDTH - 8))
        for bit in range(8, 0, -1):
            if remainder & TOPBIT:
                remainder = ((remainder << 1) & 0xFFFFFFFF) ^ POLYNOMIAL
            else:
                remainder = (remainder << 1)

    return [remainder >> 24 & 0xFF, remainder >> 16 & 0xFF, remainder >> 8 & 0xFF, remainder & 0xFF]


def isCrc32Fail(message, nBytes):
    return crc_32(message, nBytes) != [0, 0, 0, 0]


def errCorrection(isCrcFail, imudata):
    global err_correction_data, crcFailCnt

    if not isCrcFail:
        err_correction_data = imudata
    else:
        imudata = err_correction_data
        crcFailCnt += 1
    return imudata


class pigImuReader(Thread):
    def __init__(self, portName: str = "None", baudRate: int = 230400):
        super(pigImuReader, self).__init__()
        self.sf_a = 1
        self.sf_b = 0
        self.__Connector = None
        self.__isRun = True
        self.__callBack = None
        self.__crcFail = 0
        self.arrayNum = 10

    def __del__(self):
        print("class memsImuReader's destructor called!")

    @property
    def sf_a(self):
        return self.__sf_a

    @sf_a.setter
    def sf_a(self, value):
        self.__sf_a = value

    @property
    def sf_b(self):
        return self.__sf_b

    @sf_b.setter
    def sf_b(self, value):
        self.__sf_b = value

    @property
    def isRun(self):
        return self.__isRun

    @isRun.setter
    def isRun(self, isFlag):
        self.__isRun = isFlag

    def writeImuCmd(self, cmd, value):
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        print(cmd, end=', ')
        print([i for i in data])
        self.__Connector.write(data)
        time.sleep(0.15)

    def connect(self, port, portName, baudRate):
        self.__Connector = port
        self.__Connector.baudrate = baudRate
        self.__Connector.port = portName
        self.__Connector.open()
        is_open = self.__Connector.is_open
        return is_open

    def disconnect(self):
        self.__Connector.close()
        is_open = self.__Connector.is_open
        return is_open

    def readIMU(self):
        self.writeImuCmd(1, 1)

    def stopIMU(self):
        self.writeImuCmd(1, 4)

    def setCallback(self, callback):
        self.__callBack = callback

    def getImuData(self):
        head = alignHeader_4B(self.__Connector, HEADER_KVH)
        rdata = self.__Connector.read(18)
        dataPacket = head + [i for i in rdata]
        STEP, PD_TEMP = readPIG(dataPacket, EN=1, PRINT=0, sf_a=0.00151990104803339, sf_b=0,
                                POS_TIME=POS_PIG)
        # t = FPGA_TIME
        imudata = {"PIG_WZ": STEP, "PD_TEMP": PD_TEMP}
        return dataPacket, imudata

    def readInputBuffer(self):
        return self.__Connector.in_waiting

    def run(self):
        while True:
            if not self.isRun:
                self.stopIMU()
                break
            # End of if-condition

            imudataArray = {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

            for i in range(self.arrayNum):
                while not self.readInputBuffer():
                    pass

                dataPacket, imudata = self.getImuData()
                isCrcFail = isCrc32Fail(dataPacket, len(dataPacket))
                imudata = errCorrection(isCrcFail, imudata)
                imudataArray["PIG_WZ"] = np.append(imudataArray["PIG_WZ"], imudata["PIG_WZ"])
                imudataArray["PD_TEMP"] = np.append(imudataArray["PD_TEMP"], imudata["PD_TEMP"])
            # end of for loop
            if self.__callBack is not None:
                self.__callBack(imudataArray)
        # end of while loop

    # End of memsImuReader::run

    def send_init_value(self):
        self.writeImuCmd(8, 135)  # freq
        self.writeImuCmd(13, 65)  # wait cnt
        self.writeImuCmd(15, 6)  # avg
        self.writeImuCmd(9, 6850)  # mod_H
        self.writeImuCmd(10, -6850)  # mod_L
        self.writeImuCmd(14, 0)  # err_th
        self.writeImuCmd(11, 0)  # err_offset
        self.writeImuCmd(12, 1)  # pol
        self.writeImuCmd(20, 0)  # cons_step
        self.writeImuCmd(17, 6)  # g1
        self.writeImuCmd(18, 5)  # g2
        self.writeImuCmd(19, 1)  # fb_on
        self.writeImuCmd(23, 20)  # dac_g
        self.writeImuCmd(24, 2177)  # data rate


def myCallBack(imudata):
    print('%3.1f' % imudata['PD_TEMP'], end=', ')
    print('%f\n' % imudata['PIG_WZ'])
    pass


if __name__ == "__main__":
    ser = serial.Serial()
    myImu = pigImuReader()
    myImu.setCallback(myCallBack)
    myImu.arrayNum = 1
    myImu.connect(ser, "COM20", 230400)
    myImu.send_init_value()
    myImu.readIMU()
    myImu.isRun = True
    myImu.start()
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.stopIMU()
        myImu.disconnect()
        myImu.join()
        print('KeyboardInterrupt success')
