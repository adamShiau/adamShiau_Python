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
# global variable defined for error correction
err_correction_data = 0
crcFailCnt = 0

err_correction_data_vbox = 0
crcFailCnt_vbox = 0

import numpy as np


def crc_8(message, nBytes):
    """
    Description
    -----------
    Calculate 8-bit CRC of input message.
    ref: https://barrgroup.com/embedded-systems/how-to/crc-calculation-c-code
    Parameters
    ----------
    message: byte list, to be used to calculate the CRC.
    nBytes: int, total bytes number of input message.
    Returns
    -------
    remainder: One byte CRC value.
    """
    WIDTH = 8
    TOPBIT = (1 << (WIDTH - 1))
    POLYNOMIAL = 0x07
    remainder = 0
    for byte in range(0, nBytes):
        remainder = remainder ^ (message[byte] << (WIDTH - 8))

        for bit in range(8, 0, -1):
            if remainder & TOPBIT:
                remainder = ((remainder << 1) & 0xFF) ^ POLYNOMIAL
            else:
                remainder = (remainder << 1)
    return remainder


def crc_16_vbox(message, nBytes):
    # print(len(message))
    WIDTH = 16
    TOPBIT = (1 << (WIDTH - 1))
    POLYNOMIAL = 4129
    remainder = 0
    # print("crc_32:", message)
    for byte in range(0, nBytes):
        remainder = remainder ^ (message[byte] << (WIDTH - 8))
        for bit in range(8, 0, -1):
            if remainder & TOPBIT:
                remainder = ((remainder << 1) & 0xFFFF) ^ POLYNOMIAL
            else:
                remainder = (remainder << 1)

    return [remainder >> 8 & 0xFF, remainder & 0xFF]


def crc_32(message, nBytes):
    # print(len(message))
    WIDTH = 32
    TOPBIT = (1 << (WIDTH - 1))
    POLYNOMIAL = 0x04C11DB7
    remainder = 0xFFFFFFFF
    # print("crc_32:", message)
    for byte in range(0, nBytes):
        remainder = remainder ^ (message[byte] << (WIDTH - 8))
        for bit in range(8, 0, -1):
            # print(bit)
            if remainder & TOPBIT:
                remainder = ((remainder << 1) & 0xFFFFFFFF) ^ POLYNOMIAL
            else:
                remainder = (remainder << 1)

    return [remainder >> 24 & 0xFF, remainder >> 16 & 0xFF, remainder >> 8 & 0xFF, remainder & 0xFF]


def isCrc8Fail(message, nBytes):
    return crc_8(message, nBytes) != 0


def isCrc16_vbox_Fail(message, nBytes):
    return crc_16_vbox(message, nBytes) != [0, 0]


def isCrc32Fail(message, nBytes):
    return crc_32(message, nBytes) != [0, 0, 0, 0]


def errCorrection(isCrcFail, imudata):
    global err_correction_data, crcFailCnt

    if not isCrcFail:
        err_correction_data = imudata
    else:
        imudata = err_correction_data
        crcFailCnt += 1
        logger.warning("crc fail: ", crcFailCnt)
    return imudata


def errCorrection_vbox(isCrcFail, vbox_data):
    global err_correction_data_vbox, crcFailCnt_vbox

    if not isCrcFail:
        err_correction_data_vbox = vbox_data
    else:
        vbox_data = err_correction_data_vbox
        crcFailCnt_vbox += 1
        logger.warning("vbox crc fail: ", crcFailCnt_vbox)
    return vbox_data


if __name__ == "__main__":
    # ''' KVH CRC test
    data1 = [0xFE, 0x81, 0xFF, 0x55]
    data2 = [0x49, 0x00, 0xAE, 0xFF, 0xD7, 0xFF, 0x48, 0x00, 0x4B, 0xFF, 0x3F, 0x20]
    data3 = [0x00, 0x04, 0xD4, 0x06, 0XFF, 0xFF, 0xFF, 0xF5, 0x00, 0x00, 0x00, 0x05, 0x1D, 0x00]
    data4 = [0x00, 0x04, 0xD3, 0xDC, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0X00, 0x03, 0x1C, 0x80]
    data5 = [0x00, 0x04, 0xD6, 0x3B, 0xFF, 0xFF, 0XFF, 0xFD, 0x00, 0x00, 0x00, 0x01, 0x1D, 0x00]
    # data1 = [0xFE, 0x81, 0xFF, 0x55, 0x37, 0xA9, 0x6A, 0x6E, 0x38, 0x58, 0x6C, 0x1F, 0xB7, 0x5B, 0xF8, 0x62, 0xBF, 0x80,
    #          0x3E, 0x78, 0xBB, 0x65, 0x0D, 0x28, 0x3B, 0x0A, 0x37, 0xAC, 0x77, 0x3D, 0x00, 0x28]
    crc = [0X2B, 0xCD, 0xF1, 0xB3]
    data = np.array(data1 + data2 + data3 + data4 + data5)
    # data = np.array(data1 + data2 + data3 + data4 + data5 + crc)
    # data = data1
    print(len(data))
    print([hex(x) for x in data])
    # print("%x" % crc_8(data, len(data)))
    # print("isCrc8Fail: ", isCrc8Fail(data, len(data)))
    print([hex(x) for x in crc_32(data, len(data))])
    # print("%x" % crc_32(data, len(data)))
    print("isCrc32Fail: ", isCrc32Fail(data, len(data)))
    # '''
    # data1 = [36, 86, 66, 51, 105, 115, 36, 0, 0, 0, 29, 4, 131, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 255, 253, 0, 13, 255, 243, 255, 247, 0, 9, 3, 202, 84, 214, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #          0, 0, 0, 0, 0, 0, 0, 0, 0]
    # crc = [94, 200]
    # data = data1 + crc
    # print(crc_16_vbox(data, len(data)))
    # print("isCrc16_vbox_Fail: ", isCrc16_vbox_Fail(data, len(data)))
