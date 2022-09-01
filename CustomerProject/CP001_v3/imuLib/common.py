""" ####### log stuff creation, always on the top ########  """
#!/usr/bin/env python
# -*- coding:UTF-8 -*-
from __future__ import print_function
import __builtin__
import logging

if hasattr(__builtin__, 'LOGGER_NAME'):
    logger_name = __builtin__.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import time
import numpy as np
from datetime import datetime
import logging
import json


# logging.basicConfig(level=100)

def readPIG(dataPacket, EN=1, POS_TIME=25, sf_a=1, sf_b=0, PRINT=0):
    if EN:
        temp_time = dataPacket[POS_TIME:POS_TIME + 4]
        temp_err = dataPacket[POS_TIME+ 4 :POS_TIME + 8]
        temp_fog = dataPacket[POS_TIME + 8:POS_TIME + 12]
        temp_PD_temperature = dataPacket[POS_TIME + 12:POS_TIME + 14]
        fpga_time = convert2Unsign_4B(temp_time) * 1e-4
        err_mv = convert2Sign_4B(temp_err) * (4000 / 8192)
        step_dps = convert2Sign_4B(temp_fog) * sf_a + sf_b
        PD_temperature = convert2Temperature(temp_PD_temperature)
    else:
        fpga_time = 0
        err_mv = 0
        step_dps = 0
        PD_temperature = 0
    # End of if-condition

    if PRINT:
        print()
        print(sf_a, sf_b)
        print(round(fpga_time, 4), end='\t\t')
        print(round(err_mv, 3), end='\t\t')
        print(round(step_dps, 3), end='\t\t')
        print(round(PD_temperature, 1))
    # End of if-condition

    return fpga_time, err_mv, step_dps, PD_temperature

def readPIG_old(dataPacket, EN=1, POS_ERR=25, sf_a=1, sf_b=0, PRINT=0):
    if EN:
        temp_err = dataPacket[POS_ERR:POS_ERR + 4]
        temp_fog = dataPacket[POS_ERR + 4:POS_ERR + 4 + 4]
        temp_PD_temperature = dataPacket[POS_ERR + 8:POS_ERR + 8 + 2]
        err_mv = convert2Sign_4B(temp_err) * (4000 / 8192)
        step_dps = convert2Sign_4B(temp_fog) * sf_a + sf_b
        PD_temperature = convert2Temperature(temp_PD_temperature)
    else:
        err_mv = 0
        step_dps = 0
        PD_temperature = 0
    # End of if-condition

    if PRINT:
        print()
        print(dataPacket)
        print(temp_err)
        print(temp_fog)
        print(temp_PD_temperature)
        print(round(err_mv, 3), end='\t\t')
        print(round(step_dps, 3), end='\t\t')
        print(round(PD_temperature, 1))
    # End of if-condition

    return err_mv, step_dps, PD_temperature


# End of ImuConnector::readPIG

# def readPIG(dataPacket, dataLen=4, POS_TIME=4, sf_a=1, sf_b=0, EN=True, PRINT=False):
#     if EN:
#         temp_time = dataPacket[POS_TIME:POS_TIME + dataLen]
#         temp_err = dataPacket[POS_TIME + 4:POS_TIME + dataLen]
#         temp_fog = dataPacket[POS_TIME + 8:POS_TIME + dataLen]
#         temp_PD_temperature = dataPacket[POS_TIME + 12:POS_TIME + dataLen]
#         fpga_time = convert2Unsign_4B(temp_time) * 1e-4
#         err_mv = convert2Sign_4B(temp_err) * (4000 / 8192)
#         step_dps = convert2Sign_4B(temp_fog) * sf_a + sf_b
#         PD_temperature = convert2Unsign_4B(temp_PD_temperature) / 2.0
#     else:
#         fpga_time = 0
#         err_mv = 0
#         step_dps = 0
#         PD_temperature = 0
#     # End of if-condition
#
#     if PRINT:
#         print(round(fpga_time, 4), end='\t\t')
#         print(round(err_mv, 3), end='\t\t')
#         print(round(step_dps * 3600, 3), end='\t\t')
#         print(round(PD_temperature, 1))
#     # End of if-condition
#
#     return fpga_time, err_mv, step_dps, PD_temperature


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

    return nano33_wx, nano33_wy, nano33_wz, nano33_ax, nano33_ay, nano33_az


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


# file controller global variable definition
fd = [None, None]


# End of file controller global variable definition

def file_manager(isopen=False, name="notitle", mode="w", fnum=0):
    global fd
    if isopen:
        try:
            fd[fnum] = open(name, mode)
            # print("file " + name + " is open")

        except:
            logger.info("file " + name + " does not exist, auto create new!")
            fd[fnum] = open(name, "w")

        return True, fd[fnum]

    else:
        try:
            fd[fnum].close()
            # print("file " + name + " is close")
        except NameError:
            logger.info("NameError")
            pass
        except AttributeError:
            logger.info("AttributeError: the file attempt to close does not exist !")
            pass
        return False, fd[fnum]


# End of file_controller

def saveData2File(isopen=False, data=None, fmt=" ", file=None):
    if isopen:
        data = np.vstack(data).T
        np.savetxt(file, data, fmt=fmt)


# End of saveData2File

class data_manager:
    def __init__(self, name="untitled.txt", fnum=0):
        self.__fd = None
        self.__isopen = False
        self.__name__ = name
        self.__fnum__ = fnum

    @property
    def name(self):
        return self.__name__

    @name.setter
    def name(self, name):
        self.__name__ = name

    def open(self, status):
        self.__isopen, self.__fd = file_manager(name=self.__name__, isopen=status, mode="w", fnum=self.__fnum__)
        # print("in open:", self.__fd)
        if self.__isopen:
            date_now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            self.__fd.writelines('#' + date_now + '\n')

    def close(self):
        if self.__isopen:
            date_now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            self.__fd.writelines('#' + date_now + '\n')
        self.__isopen, fd = file_manager(name=self.__name__, isopen=False, mode="w", fnum=self.__fnum__)

    def saveData(self, datalist, fmt):
        saveData2File(isopen=self.__isopen, data=datalist, fmt=fmt, file=self.__fd)
        # print("in saveData:", self.__isopen)


class parameters_manager:
    def __init__(self, name, parameter_init, fnum=1):
        self.__par = parameter_init
        self.__name = name
        self.__fnum = fnum

    def check_file_exist(self):
        isopen, fd = file_manager(isopen=True, name=self.__name, mode="r", fnum=self.__fnum)

        if isopen:
            # parameter file does not exist, create new with write mode and dump initial parameters into the file.
            if fd.mode == "w":
                self.__dump_init_parameters(fd, self.__par)

            # parameter file exists, close the file.
            elif fd.mode == "r":
                self.__par = json.load(fd)
                # print(self.__par)
                file_manager(isopen=False, name=self.__name, fnum=self.__fnum)

        return self.__par

    def __dump_init_parameters(self, fd, data):
        json.dump(data, fd)
        file_manager(isopen=False, name=self.__name, fnum=self.__fnum)

    def update_parameters(self, key, value):
        isopen, fd = file_manager(isopen=True, name=self.__name, fnum=self.__fnum)
        self.__par[key] = value
        json.dump(self.__par, fd)
        file_manager(isopen=False, name=self.__name, fnum=self.__fnum)


# End of parameters_manager


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


def convert2Temperature(datain):
    temp = datain[0] + (datain[1] >> 7) * 0.5
    return temp


# End of convert2Unsign_4B

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
    t_old = time.clock()
    while (time.clock() - t_old) * 1000 < ms:
        pass


# End of wait_ms

def print_debug(s, en=0):
    if en:
        print(s)


def dictOperation(dictA, dictB, mode, dictStruct):
    # rt = dictStruct
    rt = {k: [j for j in dictStruct[k]] for k in dictStruct}
    # print("rt: ", rt)

    if mode == "ADD":
        logging.debug("")
        logging.debug("MODE = " + str(mode))
        logging.debug("dictA= " + str(dictA))
        logging.debug("dictB= " + str(dictB))
        logging.debug("rt= " + str(rt))
        logging.debug("")
        for k in dictStruct:
            logging.debug("k= " + str(k))
            logging.debug("dictA[k]= " + str(dictA[k]))
            logging.debug("dictB[k]= " + str(dictB[k]))
            rt[k] = np.array(dictA[k] + dictB[k])
            logging.debug("rt[k]= " + str(rt[k]) + "\n")
        # end of for-loop of k
        return rt

    if mode == "SUB":
        logging.debug("")
        logging.debug("MODE = " + str(mode))
        logging.debug("dictA= " + str(dictA))
        logging.debug("dictB= " + str(dictB))
        logging.debug("rt= " + str(rt))
        logging.debug("")
        for k in dictStruct:
            logging.debug("k= " + str(k))
            logging.debug("dictA[k]= " + str(dictA[k]))
            logging.debug("dictB[k]= " + str(dictB[k]))
            rt[k] = np.array(dictA[k] - dictB[k])
            logging.debug("rt[k]= " + str(rt[k]) + "\n")
        # end of for-loop of k
        return rt

    elif mode == "APPEND":
        # rt = {k: [np.empty(0) for i in range(len(dictStruct[k]))] for k in dictStruct}
        logging.debug("")
        logging.debug("MODE = " + str(mode))
        logging.debug("dictStruct= " + str(dictStruct))
        logging.debug("dictA= " + str(dictA))
        logging.debug("dictB= " + str(dictB))
        logging.debug("rt= " + str(rt))
        logging.debug("")
        for k in dictStruct:
            logging.debug("k= " + str(k))
            logging.debug("dictA[k]= " + str(dictA[k]))
            logging.debug("dictB[k]= " + str(dictB[k]))
            rt[k] = np.append(dictA[k], dictB[k])
            logging.debug("rt[k]= " + str(rt[k]) + "\n")

        # end of for-loop of k
        return rt

    else:
        print(mode + " method doesn't exist!")
        pass


# End of dicOperation


