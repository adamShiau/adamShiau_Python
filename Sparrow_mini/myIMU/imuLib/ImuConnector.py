#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import serial
import time
import numpy as np
import sys

sys.path.append("../")
import imuLib.fogParameters as fog

SENS_GYRO_250 = 0.00875
SENS_AXLM_4G = 0.000122
SENS_ADXL355_8G = 0.0000156
HEADER_PIG = np.array([0xFE, 0x81, 0xFF, 0x55])
WIDTH = 8
TOPBIT = (1 << (WIDTH - 1))
POLYNOMIAL = 0x07


def wait_ms(ms):
    t_old = time.perf_counter_ns()
    while (time.perf_counter_ns() - t_old) < ms * 1e6:
        pass


class ImuConnector:
    """
    Description:
    =============================================

    ---------------------------------------------
    Author:    Adam Shiau
    Date:      04/18/2022
    """

    def __init__(self, strPortName="COM15", iBaudRate=230400, fTimeOut=0) -> None:
        """
        Description:
        =============================================
        Initialize the object of this class.

        Args
        =============================================
        strPortName:    type: str, the serial port name
        iBaudRate:      type: int, the baud rate of serial port
        fTimeOut:       type: float, set a read timeout value.

        """
        self.__strPortName = strPortName
        self.__iBaudRate = iBaudRate
        self.__fTimeOut = fTimeOut
        self.__is_open = False
        self.__ser = serial.Serial()
        self.__old_time = 0
        self.__old_err = 0
        self.__old_step = 0
        self.__old_PD_temp = 0
        self.__crc_fail_cnt = 0
        self.__fake_time = 0
        self.__crcFail = 0

    # End of constructor

    def connect(self):
        """
        Description:
        =============================================
        Open serial port to connect.

        Args
        =============================================
        None

        Exceptions:
        =============================================
        IOError:  In case the device can not be found or can not be configured.

        """

        self.__ser.baudrate = self.__iBaudRate
        self.__ser.port = self.__strPortName
        self.__ser.timeout = None
        self.__ser.writeTimeout = self.__fTimeOut
        self.__ser.parity = serial.PARITY_NONE
        self.__ser.stopbits = serial.STOPBITS_ONE
        self.__ser.bytesize = serial.EIGHTBITS

        try:
            self.__ser.open()
        except IOError:
            print("IOError, the device can not be found or can not be configured!")
            sys.exit(0)
        # End of try-catch

        print(self.__ser.name + " is connected")
        self.__is_open = self.__ser.is_open

    # End of ImuConnector::connect

    def close(self):
        """
        Description:
        =============================================
        Close port immediately.

        Args
        =============================================
        None
        """
        self.__ser.close()
        self.__is_open = self.__ser.is_open
        print(self.__ser.name + " is disconnected")

    # End of ImuConnector::close

    def write(self, data):
        """
        Description:
        =============================================
        Write the bytes data to the port.

        Args
        =============================================
        data:    type: int, binary data to write out

        Exceptions:
        =============================================
        timeout: In case a write timeout is configured for the port and the time is exceeded.
        """
        try:
            data = [data]
            print(self.__ser.write(data))
        except serial.SerialTimeoutException:
            print("write timeOut")
        # End of try-catch

    # End of ImuConnector::write

    def writeFogCmd(self, cmd, value):
        if value < 0:
            value = (1 << 32) + value
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        self.__ser.write(data)
        wait_ms(150)

    # End of ImuConnector::writeFogCmd

    def updateFogParameters(self):
        if self.__is_open:
            self.__ser.reset_input_buffer()
            self.__ser.reset_output_buffer()
            self.writeFogCmd(fog.CMD_FOG_MOD_FREQ, fog.FREQ_INIT)
            self.writeFogCmd(fog.CMD_FOG_MOD_AMP_H, fog.MOD_H_INIT)
            self.writeFogCmd(fog.CMD_FOG_MOD_AMP_L, fog.MOD_L_INIT)
            self.writeFogCmd(fog.CMD_FOG_ERR_OFFSET, fog.ERR_OFFSET_INIT)
            self.writeFogCmd(fog.CMD_FOG_POLARITY, fog.POLARITY_INIT)
            self.writeFogCmd(fog.CMD_FOG_WAIT_CNT, fog.WAIT_CNT_INIT)
            self.writeFogCmd(fog.CMD_FOG_ERR_TH, fog.ERR_TH_INIT)
            self.writeFogCmd(fog.CMD_FOG_ERR_AVG, fog.ERR_AVG_INIT)
            self.writeFogCmd(fog.CMD_FOG_GAIN1, fog.GAIN1_SEL_INIT)
            self.writeFogCmd(fog.CMD_FOG_GAIN2, fog.GAIN2_SEL_INIT)
            self.writeFogCmd(fog.CMD_FOG_DAC_GAIN, fog.DAC_GAIN_INIT)
            self.writeFogCmd(fog.CMD_FOG_FB_ON, fog.FB_ON_INIT)
            self.writeFogCmd(fog.CMD_FOG_CONST_STEP, fog.CONST_STEP_INIT)
            self.writeFogCmd(fog.CMD_FOG_INT_DELAY, fog.DATA_RATE_INIT)
            self.writeFogCmd(fog.CMD_FOG_TIMER_RST, 1)
            self.writeFogCmd(fog.MODE_IMU, fog.INT_SYNC)

    # End of ImuConnector::updateFogParameters

    def getImuData(self):
        [temp_time,
         temp_err,
         temp_step,
         temp_PD_temperature] = self.readPIG(EN=1, PRINT=0)

        [temp_adxl355_x,
         temp_adxl355_y,
         temp_adxl355_z] = self.readADXL355(EN=1, SF=SENS_ADXL355_8G
                                            , PRINT=0)
        [temp_nano33_wx,
         temp_nano33_wy,
         temp_nano33_wz,
         temp_nano33_ax,
         temp_nano33_ay,
         temp_nano33_az] = self.readNANO33(EN=1, SF_XLM=SENS_AXLM_4G
                                           , SF_GYRO=SENS_GYRO_250
                                           , PRINT=0)

        temp_step_dph = (temp_step * fog.SF_A_INIT + fog.SF_B_INIT) * 3600

        return (temp_err, temp_step_dph, temp_PD_temperature, temp_adxl355_x, temp_adxl355_y, temp_adxl355_z,
                temp_nano33_wx, temp_nano33_wy, temp_nano33_wz)

    def checkHeader_4B(self, HEADER):
        headerArr = bytearray(self.__ser.read(4))
        hold = 1
        while hold:
            if ((headerArr[0] == HEADER[0]) and
                    (headerArr[1] == HEADER[1]) and
                    (headerArr[2] == HEADER[2]) and
                    (headerArr[3] == HEADER[3])
            ):
                hold = 0
                return headerArr
            else:
                headerArr[0] = headerArr[1]
                headerArr[1] = headerArr[2]
                headerArr[2] = headerArr[3]
                headerArr[3] = self.__ser.read(1)[0]

    def crcSlow(self, message, nBytes):
        remainder = 0
        byte = 0
        bit = 8
        for byte in range(0, nBytes):
            remainder = remainder ^ (message[byte] << (WIDTH - 8))

            for bit in range(8, 0, -1):
                if remainder & TOPBIT:
                    remainder = ((remainder << 1) & 0xFF) ^ POLYNOMIAL
                else:
                    remainder = (remainder << 1)
        return remainder

    def readPIG(self, EN=1, PRINT=0):
        if EN:
            temp_header = self.checkHeader_4B(HEADER_PIG)
            temp_time = bytearray(self.__ser.read(4))
            temp_err = bytearray(self.__ser.read(4))
            temp_step = bytearray(self.__ser.read(4))
            temp_PD_temperature = bytearray(self.__ser.read(4))
            temp_crc = self.__ser.read(1)
            msg = temp_header + temp_time + temp_err + temp_step + temp_PD_temperature
            crc = self.crcSlow(msg, 20)

            if temp_crc[0] == crc:
                temp_time = self.convert2Unsign_4B(temp_time)
                temp_err = self.convert2Sign_4B(temp_err)
                temp_step = self.convert2Sign_4B(temp_step)
                temp_PD_temperature = self.convert2Unsign_4B(temp_PD_temperature) / 2
                self.__old_time = temp_time
                self.__old_err = temp_err
                self.__old_step = temp_step
                self.__old_PD_temp = temp_PD_temperature
                self.__crcFail = 0
            else:
                self.__crc_fail_cnt = self.__crc_fail_cnt + 1
                self.__crcFail = 1
                print('crc fail : ', self.__crc_fail_cnt)
                temp_time = self.__old_time + 0.005
                temp_err = self.__old_err
                temp_step = self.__old_step
                temp_PD_temperature = self.__old_PD_temp

        else:
            temp_time = self.__fake_time
            temp_err = 0
            temp_step = 0
            temp_PD_temperature = 0
            temp_crc = 0
            self.__fake_time = self.__fake_time + 100
            time.sleep(0.1)

        if PRINT:
            print(round(temp_time, 3), end='\t\t')
            print(round(temp_err, 3), end='\t\t')
            print(round(temp_step, 3), end='\t\t')
            print(round(temp_PD_temperature, 3), end='\t\t')
            print(temp_crc[0], end='\t\t')
            print(self.__crc_fail_cnt)

        return temp_time, temp_err, temp_step, temp_PD_temperature

    def readADXL355(self, EN, SF, PRINT=0):
        if EN:
            temp_adxl355_x = self.__ser.read(3)
            temp_adxl355_y = self.__ser.read(3)
            temp_adxl355_z = self.__ser.read(3)
            temp_adxl355_x = self.convert2Sign_adxl355(temp_adxl355_x) * SF
            temp_adxl355_y = self.convert2Sign_adxl355(temp_adxl355_y) * SF
            temp_adxl355_z = self.convert2Sign_adxl355(temp_adxl355_z) * SF
        else:
            temp_adxl355_x = 9.8
            temp_adxl355_y = 9.8
            temp_adxl355_z = 9.8

        if PRINT:
            print(round(temp_adxl355_x, 4), end='\t\t')
            print(round(temp_adxl355_y, 4), end='\t\t')
            print(round(temp_adxl355_z, 4))

        return temp_adxl355_x, temp_adxl355_y, temp_adxl355_z

    def readNANO33(self, EN, SF_XLM, SF_GYRO, PRINT=0):
        if EN:
            temp_nano33_wx = self.__ser.read(2)
            temp_nano33_wy = self.__ser.read(2)
            temp_nano33_wz = self.__ser.read(2)
            temp_nano33_ax = self.__ser.read(2)
            temp_nano33_ay = self.__ser.read(2)
            temp_nano33_az = self.__ser.read(2)
            temp_nano33_wx = self.convert2Sign_nano33(temp_nano33_wx) * SF_GYRO
            temp_nano33_wy = self.convert2Sign_nano33(temp_nano33_wy) * SF_GYRO
            temp_nano33_wz = self.convert2Sign_nano33(temp_nano33_wz) * SF_GYRO
            temp_nano33_ax = self.convert2Sign_nano33(temp_nano33_ax) * SF_XLM
            temp_nano33_ay = self.convert2Sign_nano33(temp_nano33_ay) * SF_XLM
            temp_nano33_az = self.convert2Sign_nano33(temp_nano33_az) * SF_XLM
        else:
            temp_nano33_wx = 0.2
            temp_nano33_wy = 0.2
            temp_nano33_wz = 0.2
            temp_nano33_ax = 10
            temp_nano33_ay = 10
            temp_nano33_az = 10

        if PRINT:
            print(round(temp_nano33_ax, 4), end='\t\t')
            print(round(temp_nano33_ay, 4), end='\t\t')
            print(round(temp_nano33_az, 4), end='\t\t')
            print(round(temp_nano33_wx, 4), end='\t\t')
            print(round(temp_nano33_wy, 4), end='\t\t')
            print(round(temp_nano33_wz, 4))

        return (temp_nano33_wx, temp_nano33_wy, temp_nano33_wz,
                temp_nano33_ax, temp_nano33_ay, temp_nano33_az)

    def convert2Unsign_4B(self, datain):
        shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
        return shift_data

    def convert2Sign_4B(self, datain):
        shift_data = (datain[0] << 24 | datain[1] << 16 | datain[2] << 8 | datain[3])
        if (datain[0] >> 7) == 1:
            return shift_data - (1 << 32)
        else:
            return shift_data

    def convert2Sign_adxl355(self, datain):
        shift_data = (datain[0] << 12 | datain[1] << 4 | datain[2] >> 4)
        if (datain[0] >> 7) == 1:
            return shift_data - (1 << 20)
        else:
            return shift_data

    def convert2Sign_nano33(self, datain):
        shift_data = (datain[1] << 8 | datain[0])
        if (datain[1] >> 7) == 1:
            return shift_data - (1 << 16)
        else:
            return shift_data

    def readInputBuffer(self):
        print(self.__ser.in_waiting)

    def closeFOG(self):
        self.writeFogCmd(fog.MODE_IMU, fog.STOP_SYNC)


if __name__ == "__main__":
    print("running ImuConnector.py")
    old_time = time.perf_counter()
    oImuConnector = ImuConnector("COM15")
    oImuConnector.connect()
    oImuConnector.updateFogParameters()
    while (time.perf_counter() - old_time) < 5:
        oImuConnector.getImuData()
    oImuConnector.closeFOG()
    oImuConnector.close()
