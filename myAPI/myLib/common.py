# -*- coding:UTF-8 -*-
import time
import numpy as np
import logging


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
        adxl355_x = round(convert2Sign_adxl355(temp_adxl355_x) * sf, 5)
        # adxl355_x = temp_adxl355_x[0]<<24 | temp_adxl355_x[1]<<16 | temp_adxl355_x[2]<<8 | temp_adxl355_y[0]
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

def readSparrow(dataPacket, POS_SPARROW=25, EN=1, sf_a=1.0, sf_b=0.0, PRINT=0):
    if EN:
        sparrow_wz = dataPacket[POS_SPARROW:POS_SPARROW + 4]
        temperature = dataPacket[POS_SPARROW + 4:POS_SPARROW + 4 + 2]
        sparrow_wz = round(convert2Sign_4B(sparrow_wz) * sf_a + sf_b, 5)
    else:
        sparrow_wz = 0
    # End of if-condition

    if PRINT:
        print(sparrow_wz)
    # End of if-condition

    return sparrow_wz,


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


def dictOperation(dictA: dict, dictB: dict, mode: str):
    # rt = dictA
    A = {k: np.array(dictA[k]) for k in dictA}
    B = {k: np.array(dictB[k]) for k in dictB}

    # print("A: ", A)
    # print("B: ", B)

    # if mode == "ADD":
    #     # rt = {k: np.array(dictA.get(k)) for k in set(dictA)}
    #     # rt = dictA
    #     for k in set(dictB):
    #         for j in range(len(dictB.get(k))):
    #             rt.get(k)[j] = dictA.get(k)[j] + dictB.get(k)[j]
    #     return rt

    if mode == "ADD":
        rt = A
        logging.debug("")
        logging.debug("MODE = " + str(mode))
        logging.debug("dictA= " + str(dictA))
        logging.debug("dictB= " + str(dictB))
        logging.debug("rt= " + str(rt))
        logging.debug("")
        for k in set(B):
            logging.debug("k= " + str(k) + "   len(dictB[k])= " + str(len(B[k])))
            var_size = len(B[k])
            if var_size == 1:
                logging.debug("dictA[k]= " + str(A[k]))
                logging.debug("dictB[k]= " + str(B[k]))
                rt[k] = A[k] + B[k]
                logging.debug("rt[k]= " + str(rt[k]) + "\n")
            else:
                for j in range(len(B.get(k))):
                    logging.debug("j= " + str(j))
                    logging.debug("dictA[k][j]= " + str(A.get(k)[j]))
                    logging.debug("dictB[k][j]= " + str(B.get(k)[j]))
                    rt.get(k)[j] = A.get(k)[j] + B.get(k)[j]
                    logging.debug("rt[k][j]= " + str(rt.get(k)[j]) + "\n")
        return rt

    elif mode == "SUB":
        rt = A
        rt = {k: [np.empty(0) for i in range(len(B[k]))] for k in dictA}
        logging.debug("")
        logging.debug("MODE = " + str(mode))
        logging.debug("dictA= " + str(dictA))
        logging.debug("dictB= " + str(dictB))
        logging.debug("rt= " + str(rt))
        logging.debug("")
        for k in set(B):
            logging.debug("k= " + str(k) + "   len(dictB[k])= " + str(len(B[k])))
            var_size = len(B[k])
            if var_size == 1:
                logging.debug("dictA[k]= " + str(A[k]))
                logging.debug("dictB[k]= " + str(B[k]))
                rt[k] = A[k] - B[k]
                logging.debug("rt[k]= " + str(rt[k]) + "\n")
            else:
                for j in range(len(B.get(k))):
                    logging.debug("j= " + str(j))
                    logging.debug("dictA[k][j]= " + str(A.get(k)[j]))
                    logging.debug("dictB[k][j]= " + str(B.get(k)[j]))
                    rt.get(k)[j] = A.get(k)[j] - B.get(k)[j]
                    logging.debug("rt[k][j]= " + str(rt.get(k)[j]) + "\n")
        return rt

    elif mode == "APPEND":
        rt = {k: [np.empty(0) for i in range(len(B[k]))] for k in dictA}
        logging.debug("")
        logging.debug("MODE = " + str(mode))
        logging.debug("dictA= " + str(dictA))
        logging.debug("dictB= " + str(dictB))
        logging.debug("rt= " + str(rt))
        logging.debug("")
        for k in set(B):
            logging.debug("k= " + str(k) + "   len(dictB[k])= " + str(len(B[k])))
            var_size = len(B[k])
            if var_size == 1:
                logging.debug("dictA[k]= " + str(A[k]))
                logging.debug("dictB[k]= " + str(B[k]))
                rt[k] = np.append(A[k], B[k])
                logging.debug("rt[k]= " + str(rt[k]) + "\n")
            else:
                for j in range(len(B.get(k))):
                    logging.debug("j= " + str(j))
                    logging.debug("dictA[k][j]= " + str(A[k][j]))
                    logging.debug("dictB[k][j]= " + str(B[k][j]))
                    rt[k][j] = np.append(A[k][j], B[k][j])
                    logging.debug("rt[k][j]= " + str(rt[k][j]) + "\n")
        return rt

    # elif mode == "APPEND":
    #     # rt = dictA
    #     # print("rt:", rt)
    #     for k in set(dictB):
    #         # print("mode=", mode, end=", ")
    #         # print("k=", k, end=", ")
    #         # print("len(dictB.get(k))=", len(dictB.get(k)), end=", ")
    #         # print("dictA[k]=", dictA[k], end=", ")
    #         # print("dictB[k]=", dictB[k])
    #         var_size = len(dictB[k])
    #         if var_size == 1:
    #             # print("dictA[k]=", dictA.get(k), end=", ")
    #             # print("dictB[k]=", dictB.get(k), end=", ")
    #             rt[k] = np.append(dictA[k], dictB[k])
    #             # print(rt.get(k))
    #         else:
    #             for j in range(len(dictB[k])):
    #                 # print("j=", j)
    #                 # print("dictA[k][j]=", dictA.get(k)[j], end=", ")
    #                 # print("dictB[k][j]=", dictB.get(k)[j], end=", ")
    #                 rt[k][j] = np.append(dictA[k][j], dictB[k][j])
    #                 # print(rt[k][j])
    #                 # print()
    #     return rt

    else:
        print(mode + " method doesn't exist!")
        pass


# End of dicOperation


if __name__ == "__main__":
    import sys

    sys.path.append("../")
    from myLib.mySerial.Connector import Connector
    from myLib.mySerial import getData
    import time
    import numpy as np

    logging.basicConfig(level=100)

    # A = np.empty(0)
    # B = 2
    # print(A)
    # print(B)
    # C = np.append(A, B)
    # print(C)

    # imudata = {
    #     "NANO33_W": np.array((1., 2., 3.)),
    #     "NANO33_A": np.array((-1., -2., -3.)),
    #     "ADXL_A": np.array((4., 5., 6.)),
    #     "TIME": (1.5,)
    # }

    IMU_DATA_STRUCTURE = {
        "NANO33_W": (0, 0, 0),
        "NANO33_A": (0, 0, 0),
        "ADXL_A": (0, 0, 0),
        "TIME": (0,)
    }
    # rt = {k: [np.zeros(len(IMU_DATA_STRUCTURE[k])) ] for k in IMU_DATA_STRUCTURE}
    # print("rt: ", rt)
    # imudataArray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
    #                 for k in set(IMU_DATA_STRUCTURE)}
    # print("imudataArray: ", imudataArray)
    ''' TEST ADD '''
    '''
    # 測試累加功能
    imuoffset = {k: np.zeros(len(IMU_DATA_STRUCTURE[k])) for k in set(IMU_DATA_STRUCTURE)}
    print(imuoffset)
    data = {
        "NANO33_W": (1, 2, 3),
        "NANO33_A": (-1, -2, -3),
        "ADXL_A": (4, 5, 6),
        "TIME": (1.5,)
    }
    for i in range(10):
        imuoffset = dictOperation(imuoffset, data, "ADD")
    print(imuoffset)
    imuoffset = {k: imuoffset[k] / 10 for k in imuoffset}
    print(imuoffset)
    # end of 測試累加功能
    '''

    '''
    # 測試一起加上offset功能
    imudata = {
        "NANO33_W": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
        "NANO33_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
        "ADXL_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
        "TIME": (np.array([1.5, 1.6, 1.7]))
    }
    print(imudata)
    offset = {
        "NANO33_W": (1, 2, 3),
        "NANO33_A": (-1, -2, -3),
        "ADXL_A": (4, 5, 6),
        "TIME": (1.5,)
    }
    imudata_add_offset = dictOperation(imudata, offset, "ADD")
    print(imudata_add_offset)
    # end of 測試一起加上offset功能
    '''

    ''' TEST SUB '''
    '''
     # 測試一起扣掉offset功能
    imudata = {
        "NANO33_W": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
        "NANO33_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
        "ADXL_A": (np.array([1, 2, 3]), np.array([4, 5, 6]), np.array([7, 8, 9])),
        "TIME": (np.array([1.5, 1.6, 1.7]))
    }
    print(imudata)
    offset = {
        "NANO33_W": (1, 2, 3),
        "NANO33_A": (-1, -2, -3),
        "ADXL_A": (4, 5, 6),
        "TIME": (1.5,)
    }
    imudata_add_offset = dictOperation(imudata, offset, "SUB")
    print(imudata_add_offset)
    # end of 測試一起扣掉offset功能
    '''

    ''' TEST APPEND '''
    '''
      # 測試在memsImuReader裡對每個imudata append
    imudataArray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
                    for k in set(IMU_DATA_STRUCTURE)}
    imudata = {
        "NANO33_W": np.array((1., 2., 3.)),
        "NANO33_A": np.array((-1., -2., -3.)),
        "ADXL_A": np.array((4., 5., 6.)),
        "TIME": (1.5,)
    }
    print(imudataArray)
    for i in range(5):
        imudataArray = dictOperation(imudataArray, imudata, "APPEND")
    print(imudataArray)
    # end of 測試在memsImuReader裡對每個imudata append
    '''

    # 測試在main裡 對memsImuReader發送來的imudata append
    # '''
    data1 = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
                    for k in set(IMU_DATA_STRUCTURE)}
    data2 = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE))]
             for k in set(IMU_DATA_STRUCTURE)}
    imudata = {
        "NANO33_W": np.array((1., 2., 3.)),
        "NANO33_A": np.array((-1., -2., -3.)),
        "ADXL_A": np.array((4., 5., 6.)),
        "TIME": (1.5,)
    }

    for i in range(5):
        data1 = dictOperation(data1, imudata, "APPEND")

    print(data1)
    print(data2)
    data1["TIME"] = [data1["TIME"]]
    for i in range(3):
        data2 = dictOperation(data2, data1, "APPEND")
    print(data2)
    # '''
    # end of 測試在main裡 對memsImuReader發送來的imudata append