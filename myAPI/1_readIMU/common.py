import time
import numpy as np


def readPIG(dataPacket, dataLen=4, POS_TIME=4, sf_a=1, sf_b=0, EN=True, PRINT=False):
    if EN:
        temp_time = dataPacket[POS_TIME:POS_TIME + dataLen]
        temp_err = dataPacket[POS_TIME + 4:POS_TIME + dataLen]
        temp_fog = dataPacket[POS_TIME + 8:POS_TIME + dataLen]
        temp_PD_temperature = dataPacket[POS_TIME + 12:POS_TIME + dataLen]
        fpga_time = convert2Unsign_4B(temp_time) * 1e-4
        err_mv = convert2Sign_4B(temp_err) * (4000 / 8192)
        step_dps = convert2Sign_4B(temp_fog) * sf_a + sf_b
        PD_temperature = convert2Unsign_4B(temp_PD_temperature) / 2.0
    else:
        fpga_time = 0
        err_mv = 0
        step_dps = 0
        PD_temperature = 0
    # End of if-condition

    if PRINT:
        print(round(fpga_time, 4), end='\t\t')
        print(round(err_mv, 3), end='\t\t')
        print(round(step_dps * 3600, 3), end='\t\t')
        print(round(PD_temperature, 1))
    # End of if-condition

    return fpga_time, err_mv, step_dps, PD_temperature
# End of ImuConnector::readPIG


def readNANO33(dataPacket, EN, dataLen=2, POS_WX=13, sf_xlm=1.0, sf_gyro=1.0, PRINT=0):
    if EN:
        temp_nano33_wx = dataPacket[POS_WX:POS_WX + dataLen]
        temp_nano33_wy = dataPacket[POS_WX + 2:POS_WX + 2 + dataLen]
        temp_nano33_wz = dataPacket[POS_WX + 4:POS_WX + 4 + dataLen]
        temp_nano33_ax = dataPacket[POS_WX + 6:POS_WX + 6 + dataLen]
        temp_nano33_ay = dataPacket[POS_WX + 8:POS_WX + 8 + dataLen]
        temp_nano33_az = dataPacket[POS_WX + 10:POS_WX + 10 + dataLen]
        nano33_wx = round(convert2Sign_nano33(temp_nano33_wx) * sf_gyro, 5)
        nano33_wy = round(convert2Sign_nano33(temp_nano33_wy) * sf_gyro, 5)
        nano33_wz = round(convert2Sign_nano33(temp_nano33_wz) * sf_gyro, 5)
        nano33_ax = round(convert2Sign_nano33(temp_nano33_ax) * sf_xlm, 5)
        nano33_ay = round(convert2Sign_nano33(temp_nano33_ay) * sf_xlm, 5)
        nano33_az = round(convert2Sign_nano33(temp_nano33_az) * sf_xlm, 5)
    else:
        nano33_wx = 0.2
        nano33_wy = 0.2
        nano33_wz = 0.2
        nano33_ax = 10
        nano33_ay = 10
        nano33_az = 10

    if PRINT:
        print(nano33_wx, end='\t\t')
        print(nano33_wy, end='\t\t')
        print(nano33_wz, end='\t\t')
        print(nano33_ax, end='\t\t')
        print(nano33_ay, end='\t\t')
        print(nano33_az)

    return (nano33_wx, nano33_wy, nano33_wz), (nano33_ax, nano33_ay, nano33_az)
# End of readNANO33


def readADXL355(dataPacket, dataLen=3, POS_AX=4, EN=1, sf=1.0, PRINT=0):
    if EN:
        temp_adxl355_x = dataPacket[POS_AX:POS_AX + dataLen]
        temp_adxl355_y = dataPacket[POS_AX + 3:POS_AX + 3 + dataLen]
        temp_adxl355_z = dataPacket[POS_AX + 6:POS_AX + 6 + dataLen]
        # adxl355_x = round(convert2Sign_adxl355(temp_adxl355_x) * sf, 5)
        adxl355_x = temp_adxl355_x[0]<<24 | temp_adxl355_x[1]<<16 | temp_adxl355_x[2]<<8 | temp_adxl355_y[0]
        adxl355_y = round(convert2Sign_adxl355(temp_adxl355_y) * sf, 5)
        adxl355_z = round(convert2Sign_adxl355(temp_adxl355_z) * sf, 5)
    else:
        adxl355_x = 9.8
        adxl355_y = 9.8
        adxl355_z = 9.8
    # End of if-condition

    if PRINT:
        print(adxl355_x, end='\t\t')
        print(adxl355_y, end='\t\t')
        print(adxl355_z)
    # End of if-condition

    return adxl355_x, adxl355_y, adxl355_z
# End of ImuConnector::readADXL355


def readCRC(dataPacket, dataLen=4, POS_CRC=25, EN=1, PRINT=0):
    if EN:
        crc = dataPacket[POS_CRC:POS_CRC + dataLen]
    else:
        crc = [i for i in range(dataLen)]
    # End of if-condition

    if PRINT:
        print(crc)
    # End of if-condition

    return crc
# End of ImuConnector::readADXL355


def convert2Sign_nano33(datain):
    shift_data = (datain[1] << 8 | datain[0])
    if (datain[1] >> 7) == 1:
        return shift_data - (1 << 16)
    else:
        return shift_data
# End of convert2Sign_nano33


def convert2Sign_adxl355(datain):
    shift_data = (datain[0] << 12 | datain[1] << 4 | datain[2] >> 4)
    if (datain[0] >> 7) == 1:
        return shift_data - (1 << 20)
    else:
        return shift_data
# End of convert2Sign_adxl355


def convert2Unsign_4B(datain):
    shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
    return shift_data
# End of convert2Unsign_4B


def convert2Sign_4B(datain):
    shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
    if (datain[0] >> 7) == 1:
        return shift_data - (1 << 32)
    else:
        return shift_data
# End of convert2Sign_4B


def wait_ms(ms):
    t_old = time.perf_counter()
    while (time.perf_counter() - t_old) * 1000 < ms:
        pass
# End of wait_ms


def dictOperation(dictA, dictB, mode):
    rt = {k: np.array(dictA.get(k)) for k in set(dictA)}
    if mode == "ADD":
        for k in set(dictA):
            for j in range(len(dictA.get(k))):
                rt.get(k)[j] = dictA.get(k)[j] + dictB.get(k)[j]

    elif mode == "SUB":
        for k in set(dictA):
            for j in range(len(dictA.get(k))):
                rt.get(k)[j] = dictA.get(k)[j] - dictB.get(k)[j]

    else:
        print(mode + " method doesn't exist!")
        pass
    return rt
# End of dicOperation


if __name__ == "__main__":
    import sys
    sys.path.append("../")
    from myLib.mySerial.Connector import Connector
    from myLib.mySerial import getData
    import time
    import numpy as np

    A = {"A11": [1, 2, 3], "B22": [2, 4, 6, 8]}
    B = {"A11": [4, 5, 6], "B22": [100, 102, 103, 104]}
    C = dictOperation(A, B, "ADD")
    print(C)

    # SENS_ADXL355_8G = 0.0000156
    # SENS_NANO33_GYRO_250 = 0.00875
    # SENS_NANO33_AXLM_4G = 0.000122
    # POS_NANO33_WX = 14 - 1
    # POS_ADXL355_AX = 5 - 1
    # POS_CRC = 26 - 1
    #
    # HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
    # ser = Connector("COM5")
    # old_time = time.perf_counter()
    # ser.connect()
    # ser.write([5, 0, 0, 0, 1])
    # try:
    #     while 1:
    #         head = getData.alignHeader_4B(ser, HEADER_KVH)
    #         dataPacket = getData.getdataPacket(ser, head, 25)
    #         print(dataPacket)
    #         readNANO33(dataPacket, EN=1, PRINT=0, POS_WX=POS_NANO33_WX, sf_xlm=SENS_NANO33_AXLM_4G,
    #                    sf_gyro=SENS_NANO33_GYRO_250)
    #         readADXL355(dataPacket, EN=1, PRINT=0, POS_AX=POS_ADXL355_AX, sf=SENS_ADXL355_8G)
    #         readCRC(dataPacket, EN=1, dataLen=4, PRINT=1, POS_CRC=POS_CRC)
    #         # print("%f\n" % ((time.perf_counter() - old_time) * 1e6))
    #         old_time = time.perf_counter()
    #
    # except KeyboardInterrupt:
    #     ser.write([5, 0, 0, 0, 4])
    #     ser.disconnect()
    # pass
