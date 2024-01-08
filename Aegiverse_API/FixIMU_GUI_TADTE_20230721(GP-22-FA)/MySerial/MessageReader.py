# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

import numpy as np

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """


def convert2Int(data_in, num_bytes, unsigned=True, first='MSB'):
    if num_bytes < 1 or num_bytes > 4:
        logger.error('Number of bytes must be between 1 and 4 inclusive.')
    try:
        shift_data = 0
        if first == 'MSB':
            for i in range(num_bytes):
                shift_data |= (data_in[i] << (8 * (num_bytes - 1 - i)))
    
            if not unsigned and (data_in[0] >> 7) == 1:
                return shift_data - (1 << 8 * num_bytes)
            else:
                return shift_data
    
        elif first == 'LSB':
            for i in range(num_bytes):
                shift_data |= (data_in[num_bytes - 1 - i] << (8 * (num_bytes - 1 - i)))
    
            if not unsigned and (data_in[-1] >> 7) == 1:
                return shift_data - (1 << 8 * num_bytes)
            else:
                return shift_data
    
        else:
            logger.error('first must be "MSB" or "LSB"')
    except Exception as e:
        logger.error(f'convert2Int Error: {e}')


import struct


def convert2Float(data_in, num_bytes, first='MSB'):
    if num_bytes < 1 or num_bytes > 4:
        logger.error('Number of bytes must be between 1 and 4 inclusive.')
    try:
        if first == 'MSB':
            hex_string = ''.join([format(byte, '02x') for byte in data_in])
        elif first == 'LSB':
            hex_string = ''.join([format(byte, '02x') for byte in reversed(data_in)])
        else:
            logger.error('first must be "MSB" or "LSB"')

        float_value = struct.unpack('>f', bytes.fromhex(hex_string))[0]
        return float_value

    except Exception as e:
        logger.error(f'convert2Float Error: {e}')


class MyCRC:
    def __init__(self, WIDTH=16, POLYNOMIAL=4129, initial_remainder=0):
        self.__WIDTH = WIDTH
        self.__POLYNOMIAL = POLYNOMIAL
        self.__REMAINDER = initial_remainder
        self.__crcFailCnt = 0
        self.__err_correction_data = 0

    def calCRC(self, message: list):
        """
        Description
        -----------
        Calculate 8-bit CRC of input message.
        ref: https://barrgroup.com/embedded-systems/how-to/crc-calculation-c-code
        Parameters
        ----------
        message: byte list, to be used to calculate the CRC.
        nBytes: int, total bytes number of input message.
        WIDTH: int, bit width of the CRC.
        POLYNOMIAL: int, CRC polynomial.
        initial_remainder: int, initial value of the remainder.
        Returns
        -------
        remainder: One byte CRC value.
        """
        try:
            nBytes = len(message)
            TOPBIT = (1 << (self.__WIDTH - 1))
            mask = (1 << self.__WIDTH) - 1
            remainder = self.__REMAINDER
            for byte in range(0, nBytes):
                remainder = remainder ^ (message[byte] << (self.__WIDTH - 8))
    
                for bit in range(8, 0, -1):
                    if remainder & TOPBIT:
                        remainder = ((remainder << 1) & mask) ^ self.__POLYNOMIAL
                    else:
                        remainder = (remainder << 1)
    
            num_crc_bytes = (self.__WIDTH + 7) // 8
            crc_bytes = [(remainder >> (8 * (num_crc_bytes - 1 - i))) & 0xFF for i in range(num_crc_bytes)]

            return crc_bytes
        
        except Exception as e:
            logger.error(f"CRC calculation Error: {e}")

    def isCRCPass(self, message: list):
        num_crc_bytes = (self.__WIDTH + 7) // 8
        itm = [0 for _ in range(num_crc_bytes)]
        return self.calCRC(message) == itm

    def errCorrection(self, isCrcPass, my_data):
        if isCrcPass:
            self.__err_correction_data = my_data
        else:
            my_data = self.__err_correction_data
            self.__crcFailCnt += 1
            logger.warning("vbox crc fail: ", self.__crcFailCnt)
        return my_data


def MessageParsing(message, header, data_length, data_sign, first_byte=None, scale_list=None):
    my_data = {}
    bytes_parsed = 0
    if first_byte is None:
        first_byte = ["MSB" for _ in range(len(header))]
    if scale_list is None:
        scale_list = np.ones(len(header))
    try:
        for name, length, sign, type_first, scale in zip(header, data_length, data_sign, first_byte, scale_list):
            data_hex = message[bytes_parsed:bytes_parsed + length]
            my_data[name] = convert2Int(data_hex, length, sign, type_first) * scale
            bytes_parsed += length
        return my_data
    except Exception as e:
        logger.error(f"MessageParsing Error: {e}")


if __name__ == "__main__":
    print(" ''' KVH CRC test")
    data = [0xFE, 0x81, 0xFF, 0x55, 0x37, 0xA9, 0x6A, 0x6E, 0x38, 0x58, 0x6C, 0x1F, 0xB7, 0x5B, 0xF8, 0x62, 0xBF, 0x80,
            0x3E, 0x78, 0xBB, 0x65, 0x0D, 0x28, 0x3B, 0x0A, 0x37, 0xAC, 0x77, 0x3D, 0x00, 0x28]
    crc = [0X4B, 0xFA, 0x34, 0xD8]
    my_crc = MyCRC(32, 0x04C11DB7, 0xFFFFFFFF)
    print([hex(x) for x in data])
    print([hex(x) for x in my_crc.calCRC(data)])
    print("isCrcPASS: ", my_crc.isCRCPass(data + crc))

    print(" ''' VBOX CRC test")
    data_bytes_list = [1, 1, 1, 3, 4, 4, 3, 2, 3, 3, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 1, 2, 2, 3, 3, 2, 2]
    header_list = ["GPS", "GLONASS", "BeiDou", "Time", "Latitude", "Longitude", "Velocity", 'Heading',
                   'Altitude', 'Vertical_Vel', 'Solution_type', "Pitch_KF", "Roll_KF",
                   "Heading_KF", "Pitch", "Roll", "Yaw", "Acc_X", "Acc_Y", "Acc_Z", "Date", "Trigger_time", "KF_Status",
                   "Pos_Quality", 'Vel_Quality', 'T1', "Wheel_vel1", "Wheel_vel2", "Heading2_KF", "Checksum"]
    sign_list = [1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1]
    print(f"sum={np.cumsum(data_bytes_list)}")
    data2 = [36, 86, 66, 51, 105, 115, 36, 0, 0, 0, 3, 29, 118, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 16, 255, 225, 255, 247, 0, 9, 3, 212, 64, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 204, 164]
    print(len(data2))
    my_crc = MyCRC(16, 4129, 0)
    print([hex(x) for x in data2])
    print([hex(x) for x in my_crc.calCRC(data2[:-2])])
    print("isCrcPASS: ", my_crc.isCRCPass(data2))
    parsed_data = MessageParsing(data2[7:], header_list, data_bytes_list, sign_list)
    print(parsed_data)
