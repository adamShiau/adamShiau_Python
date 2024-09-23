# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
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
import struct

PRINT_DEBUG = 0


def readPIG(dataPacket, EN=1, POS_TIME=25, sf_a=1, sf_b=0, PRINT=0):
    if EN:
        temp_time = dataPacket[POS_TIME:POS_TIME + 4]
        temp_err = dataPacket[POS_TIME + 4:POS_TIME + 8]
        temp_fog = dataPacket[POS_TIME + 8:POS_TIME + 12]
        temp_PD_temperature = dataPacket[POS_TIME + 12:POS_TIME + 14]
        fpga_time = IEEE_754_INT2F(temp_time)
        err_mv = convert2Sign_4B(temp_err)
        step_dps = IEEE_754_INT2F(temp_fog)
        PD_temperature = convert2Temperature(temp_PD_temperature)
    else:
        fpga_time = 0
        err_mv = 0
        step_dps = 0
        PD_temperature = 0
    # End of if-condition

    if PRINT:
        # print()
        print('\nPIG: ', end='\t')
        # print(sf_a, sf_b)
        print('%f, ' % fpga_time, end=', ')
        print('%d, ' % err_mv, end=', ')
        print('%f, ' % step_dps, end=', ')
        print(round(PD_temperature, 1))
        # print(round(err_mv, 3), end='\t\t')
        # print(round(step_dps, 3), end='\t\t')
        # print(round(PD_temperature, 1))
    # End of if-condition

    return fpga_time, err_mv, step_dps, PD_temperature


def readTime(dataPacket, EN=1, POS_TIME=18, PRINT=0):
    if EN:
        temp_time = dataPacket[POS_TIME:POS_TIME + 4]
        mcu_time = convert2Unsign_4B_R(temp_time) / 1000.0
        # mcu_time = temp_time / 1000.0

    else:
        temp_time = 0
    # End of if-condition

    if PRINT:
        # print()
        print('\nTIME: ', end='\t')
        # print(sf_a, sf_b)
        print('%f, ' % mcu_time)
    # End of if-condition

    return mcu_time,


# End of ImuConnector::readPIG

def readADXL357(dataPacket, dataLen=4, POS_AX=4, EN=1, PRINT=0):
    if EN:
        temp_adxl357_x = dataPacket[POS_AX:POS_AX + dataLen]
        temp_adxl357_y = dataPacket[POS_AX + 4:POS_AX + 4 + dataLen]
        temp_adxl357_z = dataPacket[POS_AX + 8:POS_AX + 8 + dataLen]
        # xlm_temp = dataPacket[POS_AX + 12:POS_AX + 13]
        adxl357_x = IEEE_754_INT2F_R(temp_adxl357_x)
        adxl357_y = IEEE_754_INT2F_R(temp_adxl357_y)
        adxl357_z = IEEE_754_INT2F_R(temp_adxl357_z)
    else:
        adxl357_x = 9.8
        adxl357_y = 9.8
        adxl357_z = 9.8
    # End of if-condition

    if PRINT:
        print('\nADXL357: ', end=', ')
        print(adxl357_x, end='\t\t')
        print(adxl357_y, end='\t\t')
        print(adxl357_z)
        # print(xlm_temp)
    # End of if-condition

    return adxl357_x, adxl357_y, adxl357_z

def readADS122C04(dataPacket, dataLen=4, POS_AX=4, EN=1, PRINT=0):
    if EN:
        temp_adxl357_x = dataPacket[POS_AX:POS_AX + dataLen]
        temp_adxl357_y = dataPacket[POS_AX + 4:POS_AX + 4 + dataLen]
        temp_adxl357_z = dataPacket[POS_AX + 8:POS_AX + 8 + dataLen]
        adxl357_x = convert2Sign_4B_R(temp_adxl357_x)
        adxl357_y = convert2Sign_4B_R(temp_adxl357_y)
        adxl357_z = convert2Sign_4B_R(temp_adxl357_z)
        # adxl357_z = adxl357_z*2.048/2**23
    else:
        adxl357_x = 9.8
        adxl357_y = 9.8
        adxl357_z = 9.8
    # End of if-condition

    if PRINT:
        print('\nADXL357: ', end=', ')
        print(adxl357_x, end='\t\t')
        print(adxl357_y, end='\t\t')
        print(adxl357_z)
        # print(xlm_temp)
    # End of if-condition

    return adxl357_x, adxl357_y, adxl357_z


def readAFI(dataPacket, POS_WX, POS_WY, POS_WZ, POS_A, POS_TIME, POS_TEMPX, POS_TEMPY, POS_TEMPZ,
            dataLen, PRINT=0):
    temp_wx = dataPacket[POS_WX:POS_WX + dataLen]
    temp_wy = dataPacket[POS_WY:POS_WY + dataLen]
    temp_wz = dataPacket[POS_WZ:POS_WZ + dataLen]
    temp_Tx = dataPacket[POS_TEMPX:POS_TEMPX + dataLen]
    temp_Ty = dataPacket[POS_TEMPY:POS_TEMPY + dataLen]
    temp_Tz = dataPacket[POS_TEMPZ:POS_TEMPZ + dataLen]
    temp_time = dataPacket[POS_TIME:POS_TIME + dataLen]

    wx = IEEE_754_INT2F(temp_wx)
    wy = IEEE_754_INT2F(temp_wy)
    wz = IEEE_754_INT2F(temp_wz)
    ax, ay, az = readADXL357(dataPacket, 4, POS_A, 1, PRINT)
    Tx = IEEE_754_INT2F_R(temp_Tx)
    Ty = IEEE_754_INT2F_R(temp_Ty)
    Tz = IEEE_754_INT2F_R(temp_Tz)
    mcu_time = convert2Unsign_4B_R(temp_time) / 1000.0
    if PRINT:
        print('\n%f, ' % mcu_time, end=', ')
        print('%f, ' % wx, end=', ')
        print('%f, ' % wy, end=', ')
        print('%f, ' % wz, end=', ')
        print('%f, ' % ax, end=', ')
        print('%f, ' % ay, end=', ')
        print('%f, ' % az, end=', ')
        print('%f, ' % Tx, end=', ')
        print('%f, ' % Ty, end=', ')
        print('%f, ' % Tz)

    return mcu_time, wx, wy, wz, ax, ay, az, Tx, Ty, Tz

def readAFI_PDf(dataPacket, POS_WX, POS_WY, POS_WZ, POS_A, POS_TIME, POS_TEMPX, POS_TEMPY, POS_TEMPZ,
            dataLen, PRINT=0):
    temp_wx = dataPacket[POS_WX:POS_WX + dataLen]
    temp_wy = dataPacket[POS_WY:POS_WY + dataLen]
    temp_wz = dataPacket[POS_WZ:POS_WZ + dataLen]
    temp_Tx = dataPacket[POS_TEMPX:POS_TEMPX + dataLen]
    temp_Ty = dataPacket[POS_TEMPY:POS_TEMPY + dataLen]
    temp_Tz = dataPacket[POS_TEMPZ:POS_TEMPZ + dataLen]
    temp_time = dataPacket[POS_TIME:POS_TIME + dataLen]

    wx = IEEE_754_INT2F(temp_wx)
    wy = IEEE_754_INT2F(temp_wy)
    wz = IEEE_754_INT2F(temp_wz)
    ax, ay, az = readADS122C04(dataPacket, 4, POS_A, 1, PRINT=0)

    Tx = IEEE_754_INT2F(temp_Tx)
    Ty = IEEE_754_INT2F(temp_Ty)
    Tz = IEEE_754_INT2F(temp_Tz)
    mcu_time = convert2Unsign_4B_R(temp_time) / 1000.0
    if PRINT:
        print('\n%f, ' % mcu_time, end=', ')
        print('%f, ' % wx, end=', ')
        print('%f, ' % wy, end=', ')
        print('%f, ' % wz, end=', ')
        print('%f, ' % ax, end=', ')
        print('%f, ' % ay, end=', ')
        print('%f, ' % az, end=', ')
        print('%f, ' % Tx, end=', ')
        print('%f, ' % Ty, end=', ')
        print('%f, ' % Tz)

    return mcu_time, wx, wy, wz, ax, ay, az, Tx, Ty, Tz


def readMP_1Z(dataPacket, POS_WX, POS_WY, POS_WZ, POS_AX, POS_AY, POS_AZ, POS_TIME, POS_PDTEMP, dataLen, PRINT=0):
    temp_wx = dataPacket[POS_WX:POS_WX + dataLen]
    temp_wy = dataPacket[POS_WY:POS_WY + dataLen]
    temp_wz = dataPacket[POS_WZ:POS_WZ + dataLen]
    temp_ax = dataPacket[POS_AX:POS_AX + dataLen]
    temp_ay = dataPacket[POS_AY:POS_AY + dataLen]
    temp_az = dataPacket[POS_AZ:POS_AZ + dataLen]
    temp_pdtemp = dataPacket[POS_PDTEMP:POS_PDTEMP + dataLen]
    temp_time = dataPacket[POS_TIME:POS_TIME + dataLen]

    wx = IEEE_754_INT2F_R(temp_wx)
    wy = IEEE_754_INT2F_R(temp_wy)
    wz = IEEE_754_INT2F(temp_wz)
    ax = IEEE_754_INT2F_R(temp_ax)
    ay = IEEE_754_INT2F_R(temp_ay)
    az = IEEE_754_INT2F_R(temp_az)
    pd_temp = IEEE_754_INT2F_R(temp_pdtemp)
    mcu_time = convert2Unsign_4B_R(temp_time) / 1000.0
    if PRINT:
        print('\n%f, ' % mcu_time, end=', ')
        print('%f, ' % wx, end=', ')
        print('%f, ' % wy, end=', ')
        print('%f, ' % wz, end=', ')
        print('%f, ' % ax, end=', ')
        print('%f, ' % ay, end=', ')
        print('%f, ' % az, end=', ')
        print('%f, ' % pd_temp)

    return mcu_time, wx, wy, wz, ax, ay, az, pd_temp


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
        print('\nNANO: ', end=', ')
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
        print('\nADXL355: ', end=', ')
        print(adxl355_x, end='\t\t')
        print(adxl355_y, end='\t\t')
        print(adxl355_z)
    # End of if-condition

    return adxl355_x, adxl355_y, adxl355_z


# End of ImuConnector::readADXL355

def readGPS(dataPacket, POS_data, EN=1, PRINT=0):
    if EN:
        temp_date = dataPacket[POS_data:POS_data + 4]
        temp_time = dataPacket[POS_data + 4:POS_data + 8]
        valid = bool(dataPacket[POS_data + 8])
        gps_data = convert2Unsign_4B(temp_date)
        gps_time = convert2Unsign_4B(temp_time)
        # if valid:
        #     print(time.perf_counter())
        #     print(gps_data, gps_time)

    else:
        gps_data = 10722
        gps_time = 8292000
        valid = 0
    # End of if-condition

    if PRINT:
        if valid:
            print(gps_data, end='\t\t')
            print(gps_time, end='\t\t')
            print(time.perf_counter())
            # print(valid)
    # End of if-condition

    return gps_data, gps_time, valid


# def convert2GpsData(data):


def readVBOX(dataPacket, POS_GPS_SATS, POS_GLONASS_SATS, POS_BeiDou_SATS, POS_Z_accel, POS_Time, POS_Heading,
             POS_Heading_from_KF,
             POS_Altitude, POS_Latitude, POS_Longitude, POS_Velocity, POS_Vertical_velocity, EN=1, PRINT=0):
    if EN:
        GPS_sats = dataPacket[POS_GPS_SATS]
        GPS_sats_glo = dataPacket[POS_GLONASS_SATS]
        GPS_sats_bei = dataPacket[POS_BeiDou_SATS]
        temp_Z_accel = dataPacket[POS_Z_accel:POS_Z_accel + 2]
        temp_Time = dataPacket[POS_Time:POS_Time + 3]
        temp_Heading = dataPacket[POS_Heading:POS_Heading + 2]
        temp_Heading_from_KF = dataPacket[POS_Heading_from_KF:POS_Heading_from_KF + 2]
        temp_Altitude = dataPacket[POS_Altitude:POS_Altitude + 3]
        temp_Latitude = dataPacket[POS_Latitude:POS_Latitude + 4]
        temp_Longtitude = dataPacket[POS_Longitude:POS_Longitude + 4]
        temp_Velocity = dataPacket[POS_Velocity:POS_Velocity + 3]
        temp_Vertical_velocity = dataPacket[POS_Vertical_velocity:POS_Vertical_velocity + 3]

        Z_accel = round(convert2Sign_2B(temp_Z_accel) * 0.01, 2)
        Time = convert2Unsign_3B(temp_Time)
        Heading = round(convert2Sign_2B(temp_Heading) * 0.01, 2)
        Heading_from_KF = round(convert2Sign_2B(temp_Heading_from_KF) * 0.01, 2)
        Altitude = round(convert2Sign_3B(temp_Altitude) * 0.01, 2)
        Latitude = round(convert2Sign_4B(temp_Latitude) * 0.0000001, 7)
        Longitude = round(convert2Sign_4B(temp_Longtitude) * 0.0000001, 7)
        Velocity = round(convert2Unsign_3B(temp_Velocity) * 0.001, 3)
        Vertical_velocity = round(convert2Sign_3B(temp_Vertical_velocity) * 0.001, 3)

    else:
        logger.info('readVBOX EN = 0')
    # End of if-condition

    if PRINT:
        print('GPS_sats: ', GPS_sats)
        print('GPS_sats_glo: ', GPS_sats_glo)
        print('GPS_sats_bei: ', GPS_sats_bei)
        print('Time: ', Time)
        print('Z_accel: ', Z_accel)
        print('Heading: ', Heading)
        print('Heading_from_KF: ', Heading_from_KF)
        print('Altitude: ', Altitude)
        print('Latitude: ', Latitude)
        print('Longitude: ', Longitude)
        print('Velocity: ', Velocity)
        print('Vertical_velocity: ', Vertical_velocity)
    # End of if-condition

    return (GPS_sats, GPS_sats_glo, GPS_sats_bei, Heading, Heading_from_KF, Altitude, Latitude, Longitude, Velocity, \
            Vertical_velocity, Z_accel)


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
fd = [None, None, None]


# End of file controller global variable definition

def file_manager(isopen=False, name="notitle", mode="w", fnum=0):
    global fd
    if isopen:
        try:
            fd[fnum] = open(name, mode, encoding='utf-8')
            # print("file " + name + " is open")

        except FileNotFoundError:
            print("file_manager: file " + name + " does not exist, auto create new!")
            fd[fnum] = open(name, "w", encoding='utf-8')

        return True, fd[fnum]

    else:
        try:
            fd[fnum].close()
            # print("file " + name + " is close")
        except NameError:
            # print("file_manager: NameError")
            logger.error("NameError")
            pass
        except AttributeError:
            # print("file_manager: AttributeError")
            logger.info('AttributeError: the file attempt to close does not exist!')
            # logger.error("file_manager: AttributeError")
            # logger.exception("file_manager: AttributeError")
            pass
        return False, fd[fnum]


# End of file_controller

def saveData2File(isopen: bool = False, data: list = None, fmt: str = " ", file: object = None):
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
        print("in open:", self.__fd)
        if self.__isopen:
            date_now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            self.__fd.writelines('#' + date_now + '\n')

    def close(self):
        if self.__isopen:
            date_now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            self.__fd.writelines('#' + date_now + '\n')
            # print('close !!')
        self.__isopen, fd = file_manager(name=self.__name__, isopen=False, mode="w", fnum=self.__fnum__)

    def write_line(self, comment):
        if self.__isopen:
            self.__fd.writelines(comment + '\n')

    def saveData(self, datalist, fmt):
        saveData2File(isopen=self.__isopen, data=datalist, fmt=fmt, file=self.__fd)
        # print("in saveData:", self.__isopen)


class parameters_manager:
    def __init__(self, name, parameter_init, fnum=1):
        self.__par = parameter_init
        self.__name = name
        self.__fnum = fnum

    def check_file_exist(self) -> dict:
        isopen, fd = file_manager(isopen=True, name=self.__name, mode="r", fnum=self.__fnum)

        if isopen:
            # parameter file doesn't exist， create new with write mode and dump initial parameters into the file.
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

class data_hub_manager:
    def __init__(self):
        self.df_data = None
        self.key = None

    def connect_combobox(self, obj):
        self.key = obj.currentText()
        print('connect_combobox:', self.key)

    def store_df_data(self, df_data):
        self.df_data = df_data
        # print('data_hub_manager.store_df_data: ', self.df_data)

    def switch_df_data(self):
        # print('data_hub_manager.switch_df_data: ', self.key)
        return self.df_data[self.key]

    def manual_access_data(self, key):
        return self.df_data[key]

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, val):
        self.__key = val
        print_debug('data_hub_manager.key= %s' % self.key, PRINT_DEBUG)


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


def convert2Unsign_2B(datain):
    shift_data = (datain[0] << 8 | datain[1])
    return shift_data


def convert2Sign_2B(datain):
    shift_data = (datain[0] << 8 | datain[1])
    if (datain[0] >> 7) == 1:
        return shift_data - (1 << 16)
    else:
        return shift_data


def convert2Unsign_3B(datain):
    shift_data = (datain[0] << 16 | datain[1] << 8 | datain[2])
    return shift_data


def convert2Sign_3B(datain):
    shift_data = (datain[0] << 16 | datain[1] << 8 | datain[2])
    if (datain[0] >> 7) == 1:
        return shift_data - (1 << 24)
    else:
        return shift_data


def convert2Unsign_4B(datain):
    shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
    return shift_data


def convert2Unsign_4B_R(datain):
    shift_data = (datain[3] << 24 | datain[2] << 16 | datain[1] << 8 | datain[0])
    return shift_data


def IEEE_754_INT2F(datain):
    if len(datain) == 4:
        shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
        # shift_data = (datain[3] << 24 | datain[2] << 16 | datain[1] << 8 | datain[0])
        f = struct.unpack('<f', struct.pack('<I', shift_data))
        # print('%.3f' % f[0])
        return f[0]
    else:
        return -1


def IEEE_754_INT2F_R(datain):
    if len(datain) == 4:
        # shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
        shift_data = (datain[3] << 24 | datain[2] << 16 | datain[1] << 8 | datain[0])
        f = struct.unpack('<f', struct.pack('<I', shift_data))
        # print('%.3f' % f[0])
        return f[0]
    else:
        return -1


def convert2Sign_4B(datain):
    if len(datain) == 4:
        shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
        if (datain[0] >> 7) == 1:
            return shift_data - (1 << 32)
        else:
            return shift_data
    else:
        return -1

def convert2Sign_4B_R(datain):
    if len(datain) == 4:
        shift_data = (datain[3] << 24 | datain[2] << 16 | datain[1] << 8 | datain[0])
        if (datain[3] >> 7) == 1:
            return shift_data - (1 << 32)
        else:
            return shift_data
    else:
        return -1


# End of convert2Sign_4B


def wait_ms(ms):
    t_old = time.perf_counter()
    while (time.perf_counter() - t_old) * 1000 < ms:
        pass


# End of wait_ms

def print_debug(s, en=0):
    if en:
        print(s)


def dictOperation(dictA: dict, dictB: dict, mode: str, dictStruct: dict):
    # rt = dictStruct
    rt = {k: [j for j in dictStruct[k]] for k in dictStruct}
    # print("rt: ", rt)

    if mode == "ADD":
        print_debug("", PRINT_DEBUG)
        print_debug("MODE = " + mode, PRINT_DEBUG)
        print_debug("dictA= " + str(dictA), PRINT_DEBUG)
        print_debug("dictB= " + str(dictB), PRINT_DEBUG)
        print_debug("rt= " + str(rt), PRINT_DEBUG)
        print_debug("", PRINT_DEBUG)
        for k in dictStruct:
            print_debug("k= " + str(k), PRINT_DEBUG)
            print_debug("dictA[k]= " + str(dictA[k]), PRINT_DEBUG)
            print_debug("dictB[k]= " + str(dictB[k]), PRINT_DEBUG)
            rt[k] = np.array(dictA[k] + dictB[k])
            print_debug("rt[k]= " + str(rt[k]) + "\n", PRINT_DEBUG)

        # end of for-loop of k
        return rt

    if mode == "SUB":
        print_debug("", PRINT_DEBUG)
        print_debug("MODE = " + mode, PRINT_DEBUG)
        print_debug("dictA= " + str(dictA), PRINT_DEBUG)
        print_debug("dictB= " + str(dictB), PRINT_DEBUG)
        print_debug("rt= " + str(rt), PRINT_DEBUG)
        print_debug("", PRINT_DEBUG)
        for k in dictStruct:
            print_debug("k= " + str(k), PRINT_DEBUG)
            print_debug("dictA[k]= " + str(dictA[k]), PRINT_DEBUG)
            print_debug("dictB[k]= " + str(dictB[k]), PRINT_DEBUG)
            rt[k] = np.array(dictA[k] - dictB[k])
            print_debug("rt[k]= " + str(rt[k]) + "\n", PRINT_DEBUG)
        # end of for-loop of k
        return rt

    elif mode == "APPEND":
        # rt = {k: [np.empty(0) for i in range(len(dictStruct[k]))] for k in dictStruct}
        print_debug("", PRINT_DEBUG)
        print_debug("MODE = " + mode, PRINT_DEBUG)
        print_debug("dictStruct= " + str(dictStruct), PRINT_DEBUG)
        print_debug("dictA= " + str(dictA), PRINT_DEBUG)
        print_debug("dictB= " + str(dictB), PRINT_DEBUG)
        print_debug("rt= " + str(rt), PRINT_DEBUG)
        print_debug("", PRINT_DEBUG)
        for k in dictStruct:
            print_debug("k= " + str(k), PRINT_DEBUG)
            print_debug("dictA[k]= " + str(dictA[k]), PRINT_DEBUG)
            print_debug("dictB[k]= " + str(dictB[k]), PRINT_DEBUG)
            rt[k] = np.append(dictA[k], dictB[k])
            print_debug("rt[k]= " + str(rt[k]) + "\n", PRINT_DEBUG)

        # end of for-loop of k
        return rt

    else:
        print(mode + " method doesn't exist!")
        pass


# End of dicOperation


if __name__ == "__main__":
    # import sys
    #
    # sys.path.append("../")
    # import time
    # import numpy as np
    import struct

    f_ = struct.unpack('<f', struct.pack('<I', 0xc2f6e979))
    print('%.3f' % f_[0])
