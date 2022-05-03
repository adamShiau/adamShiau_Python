#!/usr/bin/env python
# -*- coding:UTF-8 -*-
from __future__ import print_function
import serial
import time
import numpy as np
import sys
import traceback

sys.path.append("../")
import imuLib.fogParameters as fog



WIDTH = 8
TOPBIT = (1 << (WIDTH - 1))
POLYNOMIAL = 0x07
""" imu data packet data position"""
POS_TIME_START = 4
POS_TIME_END = POS_TIME_START + 4
POS_ERR_START = 8
POS_ERR_END = POS_ERR_START + 4
POS_FOG_START = 12
POS_FOG_END = POS_FOG_START + 4
POS_TEMPERATURE_START = 16
POS_TEMPERATURE_END = POS_TEMPERATURE_START + 4
POS_CRC = 20
POS_ADXL355_AX_START = 21
POS_ADXL355_AX_END = POS_ADXL355_AX_START + 3
POS_ADXL355_AY_START = 24
POS_ADXL355_AY_END = POS_ADXL355_AY_START + 3
POS_ADXL355_AZ_START = 27
POS_ADXL355_AZ_END = POS_ADXL355_AZ_START + 3
POS_NANO33_WX_START = 30
POS_NANO33_WX_END = POS_NANO33_WX_START + 2
POS_NANO33_WY_START = 32
POS_NANO33_WY_END = POS_NANO33_WY_START + 2
POS_NANO33_WZ_START = 34
POS_NANO33_WZ_END = POS_NANO33_WZ_START + 2
POS_NANO33_AX_START = 36
POS_NANO33_AX_END = POS_NANO33_AX_START + 2
POS_NANO33_AY_START = 38
POS_NANO33_AY_END = POS_NANO33_AY_START + 2
POS_NANO33_AZ_START = 40
POS_NANO33_AZ_END = POS_NANO33_AZ_START + 2
""" end of imu data packet data position"""

def wait_ms(ms):
    t_old = time.clock()
    while (time.clock() - t_old) * 1000 < ms:
        pass


class ImuConnector:
    """
    Description:
    =============================================

    ---------------------------------------------
    Author:    Adam Shiau
    Date:      04/18/2022
    """

    def __init__(self, strPortName="COM15", iBaudRate=230400, fTimeOut=0):
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
            print("IOError, the device: " + self.__ser.port + " can not be found or can not be configured!")
            sys.exit(0)
        # End of try-catch

        print(self.__ser.name + " is connected")
        self.__is_open = self.__ser.is_open
    # End of ImuConnector::connect

    def close(self):
        """
        Description
        -----------
        Close port immediately.

        """
        self.__ser.close()
        self.__is_open = self.__ser.is_open
        print(self.__ser.name + " is disconnected")
    # End of ImuConnector::close

    def write(self, data):
        """

        Description
        -----------
        Write the list byte data to the open port.

        Parameters
        ----------
        data: int list

        Exceptions
        ----------
        timeout: In case write timeout is configured for the port and the time is exceeded.

        """
        try:
            data = [data]
            print(self.__ser.write(data))
        except serial.SerialTimeoutException:
            print("write timeOut")
        # End of try-catch
    # End of ImuConnector::write

    def writeFogCmd(self, cmd, value):
        """

        Description
        -----------
        Set parameters to IMU. "cmd" is a unsigned byte value; "value" is a signed 32bit value.

        Parameters
        ----------
        cmd: byte
        value: int

        Returns
        -------

        """
        if value < 0:
            value = (1 << 32) + value
        # End of if-condition
        data = bytearray([cmd, (value >> 24 & 0xFF), (value >> 16 & 0xFF), (value >> 8 & 0xFF), (value & 0xFF)])
        self.__ser.write(data)
        wait_ms(150)
    # End of ImuConnector::writeFogCmd

    def updateFogParameters(self):
        """

        Description
        -----------
        After port is connected, update the working parameters to the FOG.

        """
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

    def checkHeader_4B(self, header):
        """

        Description
        -----------
        Check the imu data packet headers.

        Parameters
        ----------
        header: byte list

        Returns
        -------
        headerArr: byte list

        """
        headerArr = self.readBinaryList(4)
        while 1:
            if ((headerArr[0] == header[0]) and
                    (headerArr[1] == header[1]) and
                    (headerArr[2] == header[2]) and
                    (headerArr[3] == header[3])
            ):
                return headerArr
            else:
                headerArr[0] = headerArr[1]
                headerArr[1] = headerArr[2]
                headerArr[2] = headerArr[3]
                headerArr[3] = self.readBinaryList(1)[0]
    # End of ImuConnector::checkHeader_4B

    def crcSlow(self, message, nBytes):
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
    # End of ImuConnector::crcSlow

    def readImuPacket(self, head=fog.HEADER_PIG, rbytes=38):
        """

        Description
        -----------
        Read imu packet data and do crc.

        Parameters
        ----------
        head: byte list
        rbytes: Total imu data packet bytes excluded header bytes.

        Returns
        -------
        imuPacket: byte list, Full IMU data packet.
        is_crcFail: bool, "True" if the crc check if failed.

        """
        head = self.checkHeader_4B(head)
        rdata = self.readBinaryList(rbytes)
        imuPacket = head + rdata
        crc = imuPacket[POS_CRC]
        crc_cal = self.crcSlow(imuPacket, 20)
        is_crcFail = not (crc_cal == crc)
        return imuPacket, is_crcFail
    # End of ImuConnector::readImuPacket

    def readPIG(self, imuPacket, sf_a=1, sf_b=0, EN=True, PRINT=False):
        """

        Description
        -----------
        Extract the FOG data from input imu data packet, and convert to DPS unit by multiply the scale factor.
        Set EN to True to enable this function.
        Set PRINT to True to print the results on monitor.

        Parameters
        ----------
        imuPacket: byte list
        sf_a: float
        sf_b: float
        EN: bool
        PRINT: bool

        Returns
        -------
        fpga_time: float, resolution 0.1ms
        err_mv: float, fog open-loop signal
        step_dps: float, fog close-loop signal
        PD_temperature:, PD ambient temperature, resolution 0.5 degree C

        """
        if EN:
            temp_time = imuPacket[POS_TIME_START:POS_TIME_END]
            temp_err = imuPacket[POS_ERR_START:POS_ERR_END]
            temp_fog = imuPacket[POS_FOG_START:POS_FOG_END]
            temp_PD_temperature = imuPacket[POS_TEMPERATURE_START:POS_TEMPERATURE_END]
            fpga_time = self.convert2Unsign_4B(temp_time) * fog.TIME_COEFFI
            err_mv = self.convert2Sign_4B(temp_err) * fog.ADC_COEFFI
            step_dps = self.convert2Sign_4B(temp_fog)*sf_a + sf_b
            PD_temperature = self.convert2Unsign_4B(temp_PD_temperature) / 2.0
        else:
            fpga_time = self.__fake_time
            err_mv = 0
            step_dps = 0
            PD_temperature = 0
            self.__fake_time = self.__fake_time + 0.01
            time.sleep(0.01)
        # End of if-condition

        if PRINT:
            print(round(fpga_time, 4), end='\t\t')
            print(round(err_mv, 3), end='\t\t')
            print(round(step_dps*3600, 3), end='\t\t')
            print(round(PD_temperature, 1))
        # End of if-condition

        return fpga_time, err_mv, step_dps, PD_temperature
    # End of ImuConnector::readPIG

    def readADXL355(self, imuPacket, EN=1, sf=1.0, PRINT=0):
        """

        Description
        -----------
        Extract the ADXL355 accelerometer data from input imu data packet, and convert to g unit by multiply the scale factor.
        Set EN to True to enable this function.
        Set PRINT to True to print the results on monitor.

        Parameters
        ----------
        imuPacket: byte list
        EN: bool
        sf: float
        PRINT: bool

        Returns
        -------
        adxl355_x: float, x-axis acceleration
        adxl355_y: float, y-axis acceleration
        adxl355_z: float, z-axis acceleration

        """
        if EN:
            temp_adxl355_x = imuPacket[POS_ADXL355_AX_START:POS_ADXL355_AX_END]
            temp_adxl355_y = imuPacket[POS_ADXL355_AY_START:POS_ADXL355_AY_END]
            temp_adxl355_z = imuPacket[POS_ADXL355_AZ_START:POS_ADXL355_AZ_END]
            adxl355_x = self.convert2Sign_adxl355(temp_adxl355_x) * sf
            adxl355_y = self.convert2Sign_adxl355(temp_adxl355_y) * sf
            adxl355_z = self.convert2Sign_adxl355(temp_adxl355_z) * sf
        else:
            adxl355_x = 9.8
            adxl355_y = 9.8
            adxl355_z = 9.8
        # End of if-condition

        if PRINT:
            print(round(adxl355_x, 4), end='\t\t')
            print(round(adxl355_y, 4), end='\t\t')
            print(round(adxl355_z, 4))
        # End of if-condition

        return adxl355_x, adxl355_y, adxl355_z
    # End of ImuConnector::readADXL355

    def readNANO33(self, imuPacket, EN, sf_xlm=1.0, sf_gyro=1.0, PRINT=0):
        if EN:
            temp_nano33_wx = imuPacket[POS_NANO33_WX_START:POS_NANO33_WX_END]
            temp_nano33_wy = imuPacket[POS_NANO33_WY_START:POS_NANO33_WY_END]
            temp_nano33_wz = imuPacket[POS_NANO33_WZ_START:POS_NANO33_WZ_END]
            temp_nano33_ax = imuPacket[POS_NANO33_AX_START:POS_NANO33_AX_END]
            temp_nano33_ay = imuPacket[POS_NANO33_AY_START:POS_NANO33_AY_END]
            temp_nano33_az = imuPacket[POS_NANO33_AZ_START:POS_NANO33_AZ_END]
            nano33_wx = self.convert2Sign_nano33(temp_nano33_wx) * sf_gyro
            nano33_wy = self.convert2Sign_nano33(temp_nano33_wy) * sf_gyro
            nano33_wz = self.convert2Sign_nano33(temp_nano33_wz) * sf_gyro
            nano33_ax = self.convert2Sign_nano33(temp_nano33_ax) * sf_xlm
            nano33_ay = self.convert2Sign_nano33(temp_nano33_ay) * sf_xlm
            nano33_az = self.convert2Sign_nano33(temp_nano33_az) * sf_xlm
        else:
            nano33_wx = 0.2
            nano33_wy = 0.2
            nano33_wz = 0.2
            nano33_ax = 10
            nano33_ay = 10
            nano33_az = 10

        if PRINT:
            print(round(nano33_wx, 4), end='\t\t')
            print(round(nano33_wy, 4), end='\t\t')
            print(round(nano33_wz, 4), end='\t\t')
            print(round(nano33_ax, 4), end='\t\t')
            print(round(nano33_ay, 4), end='\t\t')
            print(round(nano33_az, 4))

        return (nano33_wx, nano33_wy, nano33_wz,
                nano33_ax, nano33_ay, nano33_az)

    def readBinaryList(self, mum):
        data = self.__ser.read(mum)
        data = [ord(i) for i in data]
        # data = [hex(ord(i)) for i in data]
        return data

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

    def stopFOG(self):
        self.writeFogCmd(fog.MODE_IMU, fog.STOP_SYNC)


if __name__ == "__main__":
    print("running ImuConnector.py")
    old_time = time.clock()
    oImuConnector = ImuConnector("/dev/ttyACM1")
    oImuConnector.connect()
    oImuConnector.updateFogParameters()
    try:
        while 1:
            # oImuConnector.readInputBuffer()
            imuPacket, isCRCfail = oImuConnector.readImuPacket(fog.HEADER_PIG, 38)
            oImuConnector.readPIG(imuPacket, EN=1, PRINT=1, sf_a=fog.SF_A_INIT, sf_b=fog.SF_B_INIT)
            oImuConnector.readADXL355(imuPacket, EN=1, PRINT=0, sf=fog.SENS_ADXL355_8G)
            oImuConnector.readNANO33(imuPacket, EN=1, PRINT=0, sf_xlm=fog.SENS_NANO33_AXLM_4G, sf_gyro=fog.SENS_NANO33_GYRO_250)

    except KeyboardInterrupt:
        # traceback.print_exc()
        oImuConnector.stopFOG()
        oImuConnector.close()
