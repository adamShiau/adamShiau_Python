# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import json
import logging

from serial.serialutil import SerialException

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import serial
import serial.tools.list_ports
import time
import sys
sys.path.append('../../')
import numpy as np
import myLib.common as cmn

PRINT_DEBUG = 0

class Connector:
    def __init__(self, portName: str = "COM11", baudRate: int = 115200) -> None:
        # self.portlist = None
        self.__portName = portName
        self.__baudRate = baudRate
        self.__is_open = False
        self.__ser = serial.Serial()

    # End of constructor

    def __del__(self):
        # self.disconnect()
        logger.info("class connector's destructor called!")

    # End of destructor

    @property
    def portName(self):
        return self.__portName

    @portName.setter
    def portName(self, name):
        self.__portName = name

    @property
    def baudRate(self):
        return self.__baudRate

    @baudRate.setter
    def baudRate(self, br):
        self.__baudRate = br

    def portList(self):
        portlist = np.empty(0)
        portlistInfo = serial.tools.list_ports.comports()
        portNum = len(portlistInfo)

        for i in range(portNum):
            portlist = np.append(portlist, portlistInfo[i])
            # print(portlistInfo[i].device)

        return portNum, portlist

    def connectConn(self):
        self.__ser.baudrate = self.__baudRate
        self.__ser.port = self.__portName
        self.__ser.timeout = 1
        # self.__ser.writeTimeout = 5
        self.__ser.parity = serial.PARITY_NONE
        self.__ser.stopbits = serial.STOPBITS_ONE
        self.__ser.bytesize = serial.EIGHTBITS

        try:
            self.__ser.open()
        except IOError:
            logger.error("IOError, the device: " + self.__ser.port + " can not be found or can not be configured!")
            #sys.exit(0)
            self.__is_open = False
            return self.__is_open
        except Exception as e:
            logger.error(f"Other exceptional events occurred. The error is '{e}'")
            self.__is_open = False
            return self.__is_open
        # End of try-catch
        logger.info(self.__ser.port + " is connected")
        self.__is_open = self.__ser.is_open
        return self.__is_open

    # End of Connector::connect

    def disconnectConn(self):
        self.__ser.close()
        self.__is_open = self.__ser.is_open
        logger.info(self.__ser.port + " is disconnected")
        return self.__is_open

    # End of Connector::close

    def write(self, data_w):
        try:
            data_w = bytearray(data_w)
            self.__ser.write(data_w)
        except serial.SerialTimeoutException:
            logger.error("write timeOut")
        except serial.PortNotOpenError:
            logger.error("Port not open, please check!")
        except SerialException:
            logger.error("The device can not be found or can not be configured.")
        except Exception as e:
            logger.error(f"Other exceptional events occurred. The error is '{e}'")
        # End of try-catch

    # End of Connector::write

    def readinto(self, array):
        byte = self.__ser.readinto(array)
        return byte

    # End of Connector::readinto

    def readBinaryList(self, mum):
        try:
            data_r = self.__ser.read(mum)
            data_r = [i for i in data_r]
        except serial.SerialException:
            logger.error("ERROR")
            return False
        except Exception as e:
            logger.error(f"Other exceptional events occurred. The error is '{e}'")
            return False
        # data = [hex(i) for i in data]
        else:
            if not data_r:
                cmn.print_debug('empty list', PRINT_DEBUG)
                logger.error('serial read timeout: check if the input power is ON, close the GUI and re-excute.')
                return False
                #sys.exit()
            return data_r

    # End of Connector::readBinaryList

    def read(self):
        return self.__ser.read()

    def readInputBuffer(self):
        #print("input buffer: %d" % self.__ser.in_waiting)
        return self.__ser.in_waiting

    # End of Connector::readInputBuffer

    def flushInputBuffer(self):
        if self.__ser.is_open:
            self.__ser.reset_input_buffer()
        # print("flushInputBuffer")
        pass

    # End of Connector::flushInputBuffer

    def flushOutputBuffer(self):
        self.__ser.reset_output_buffer()

    # End of Connector::flushOutputBuffer

    def selectCom(self):
        self.comPort = np.empty(0)
        portlist = serial.tools.list_ports.comports()
        self.portNum = len(portlist)

        for i in range(self.portNum):
            self.comPort = np.append(self.comPort, portlist[i])

        # ---------- checksum: fletcher16 ----------
    @staticmethod
    def _fletcher16(data: bytes) -> int:
        # Fletcher-16, mod 255
        sum1 = 0
        sum2 = 0
        for b in data:
            sum1 = (sum1 + b) % 255
            sum2 = (sum2 + sum1) % 255
        # 常見組法：sum2為高位、sum1為低位
        return (sum2 << 8) | sum1

    def _read_exact(self, n: int, timeout_s: float) -> bytes:
        """Read exactly n bytes or raise TimeoutError."""
        end = time.time() + timeout_s
        buf = bytearray()
        while len(buf) < n and time.time() < end:
            chunk = self.__ser.read(n - len(buf))
            if chunk:
                buf += chunk
            else:
                # read() timeout會回 b''，小睡一下避免 busy loop
                time.sleep(0.001)
        if len(buf) != n:
            raise TimeoutError(f"serial timeout: want {n} bytes, got {len(buf)} bytes")
        return bytes(buf)

    # Connector.py

    def _find_sync_fa(self, timeout_s: float) -> None:
        """Consume bytes until 0xFA is found (sync)."""
        end = time.time() + timeout_s
        discarded_count = 0
        while time.time() < end:
            b = self.__ser.read(1)
            if not b:
                continue
            if b[0] == 0xFA:
                if discarded_count > 0:
                    # 若丟棄過多位元組，代表數據流中有干擾或是讀取不同步
                    logger.warning(f"DIAGNOSIS: Found 0xFA after discarding {discarded_count} bytes")
                return
            discarded_count += 1

        # 若超時沒找到 0xFA，列印目前 Buffer 狀態
        logger.error(f"DIAGNOSIS: [TIMEOUT] Cannot find 0xFA. Buffer size: {self.readInputBuffer()}")
        raise TimeoutError("serial timeout: cannot find 0xFA sync")

    def _read_frame(self, timeout_s: float = 1.0) -> dict:
        """
        Read one MCU frame:
          ACK : FA A1 cmd status lenL lenH cksumL cksumH
          RES : FA A2 cmd status lenL lenH payload[len] cksumL cksumH
        checksum coverage: from type(A1/A2) to payload end => 5 + len bytes
        """
        self._find_sync_fa(timeout_s)

        # type/cmd/status/lenL/lenH
        hdr = self._read_exact(5, timeout_s)
        ftype, cmd, status, lenL, lenH = hdr
        logger.debug(f"DIAGNOSIS: [HEADER] type={hex(ftype)}, cmd={hex(cmd)}, len={(lenH << 8) | lenL}")

        length = (lenH << 8) | lenL

        payload = b""
        if length > 0:
            payload = self._read_exact(length, timeout_s)

        cksum_bytes = self._read_exact(2, timeout_s)
        recv_ck_le = cksum_bytes[0] | (cksum_bytes[1] << 8)

        # compute
        cover = bytes([ftype, cmd, status, lenL, lenH]) + payload
        # print('cover: ', cover);
        calc_ck = self._fletcher16(cover)

        # 有些實作會用 big-endian 放 checksum；這裡容錯一下
        if recv_ck_le != calc_ck:
            recv_ck_be = (cksum_bytes[0] << 8) | cksum_bytes[1]
            if recv_ck_be != calc_ck:
                raise ValueError(
                    f"checksum mismatch: calc=0x{calc_ck:04X}, recv(le)=0x{recv_ck_le:04X}, recv(be)=0x{recv_ck_be:04X}"
                )
            logger.error(f"DIAGNOSIS: [CHECKSUM ERROR] Cmd: {hex(cmd)}, Calc: {hex(calc_ck)}, Recv: {hex(recv_ck_le)}")

        return {
            "type": ftype, "cmd": cmd, "status": status,
            "len": length, "payload": payload
        }

    # ---------- updated dump ----------

    def _execute_dump_sequence(self, cmd_bytes, expected_cmd, ch=None, timeout_res=2.0):
        """
        通用重試邏輯封裝：發送指令 -> 等待 ACK -> 等待 RESULT
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 1. 前置清空
                self.flushInputBuffer()

                # 2. 發送指令 (格式: AB BA [Payload] 55 56)
                self.__ser.write(bytearray([0xAB, 0xBA]))
                self.__ser.write(cmd_bytes)
                self.__ser.write(bytearray([0x55, 0x56]))

                # 3. 等待 ACK (A1)
                ack = self._read_frame(timeout_s=0.5)
                if ack["type"] != 0xA1 or ack["cmd"] != expected_cmd:
                    raise ValueError(f"Unexpected ACK: {ack['type']}")

                # 4. 等待 RESULT (A2)
                res = self._read_frame(timeout_s=timeout_res)
                if res["type"] != 0xA2 or res["cmd"] != expected_cmd:
                    raise ValueError(f"Unexpected RESULT: {res['type']}")

                return res  # 成功則回傳整個 frame

            except (TimeoutError, ValueError) as e:
                logger.warning(f"CMD {hex(expected_cmd)} Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.1)  # 短暫休息後重試
                    continue
                else:
                    raise e  # 三次都失敗才拋出異常

    def dump_fog_parameters(self, ch=3):
        try:
            res = self._execute_dump_sequence([0x66, 0, 0, 0, 0x02, ch], 0x66)
            if res["len"] == 0: return "無法取得值"
            return json.loads(res["payload"].decode("utf-8", errors="replace"))
        except Exception:
            return "無法取得值"

    def dump_cali_parameters(self, ch=2):
        try:
            res = self._execute_dump_sequence([0x81, 0, 0, 0, 0, ch], 0x81)
            if res["len"] == 0: return "無法取得值"
            return json.loads(res["payload"].decode("utf-8", errors="replace"))
        except Exception:
            return "無法取得值"

    def dump_configuration(self):
        try:
            res = self._execute_dump_sequence([0x84, 0, 0, 0, 0, 0], 0x84)
            if res["len"] == 0: return "無法取得值"
            return json.loads(res["payload"].decode("utf-8", errors="replace"))
        except Exception:
            return "無法取得值"

    def dump_SN_parameters(self, ch=2):
        try:
            res = self._execute_dump_sequence([0x82, 0, 0, 0, 0, ch], 0x82)
            if res["len"] == 0: return "發生參數值為空的狀況"
            sn = res["payload"].decode("ascii", errors="replace").rstrip("\x00").strip()
            return sn if sn else "發生參數值為空的狀況"
        except Exception:
            return "發生參數值為空的狀況"

    def getVersion(self, ch=2):
        try:
            res = self._execute_dump_sequence([0x83, 0, 0, 0, 0, ch], 0x83)
            if res["len"] == 0: return "Unknown"
            return res["payload"].decode("ascii", errors="replace").strip()
        except Exception:
            return "Unknown"

    def readLine(self):
        return self.__ser.readline()

    # def dumpFogParameter(self):
    #     self.writeImuCmd(66, 5)
    #     s = self.__Connector.readline()
    #     print(s)


if __name__ == "__main__":
    print("running Connector.py")
    old_time = time.perf_counter_ns()
    ser = Connector("COM17", 115200)
    ser.connect()
    ser.flushInputBuffer()
    ser.write(bytearray([0xAB, 0xBA]))
    ser.write([0x01, 0, 0, 0, 0x02, 0x02])
    ser.write(bytearray([0x55, 0x56]))
    para = ser.readLine().decode('utf-8')
    start_index = para.find("$")
    end_index = para.find("*")
    para2 = para[start_index+1:end_index]
    checkSum = para[-4:-2]
    heading = float(para2[4:10])
    print(para)
    print(heading)
    print(checkSum)

    # print(start_index)
    # print(end_index)

    checksum_cal = 0
    # [checksum = checksum ^ ord(i) for i in para2]
    for i in para2:
        checksum_cal = checksum_cal ^ ord(i)
    # a=str(hex(checksum))[-2:]
    # print('hihi')
    # print(a)
    print(checksum_cal)
    print((checkSum))
    # print(int(a) == int(checkSum))
    print()
    # para = ser.dump_fog_parameters()
    # print(para)
    # print(para["FREQ"])
    # print(para["SF0"])

    # print(line.decode('utf-8'))
    # for i in range(200):
    #     data = ser.read()
    #     print(data.decode('utf-8'), end='')
    '''for sparrow test
    ser.write([6, 0, 0, 0, 3])
    time.sleep(1)
    ser.write([6, 0, 0, 0, 1])
    '''

    # old_time = 0
    # try:
    #     while True:
    #         if ser.readInputBuffer() > 22:
    #             print("buf: ", ser.readInputBuffer())
    #             new = time.perf_counter_ns()
    #             print(ser.readBinaryList(22))
    #             print("%.1f\n" % ((new - old_time) * 1e-3))
    #             old_time = new
    #             cmn.wait_ms(4)
    #
    # except KeyboardInterrupt:
    #     ser.write(bytearray([0xAB, 0xBA]))
    #     ser.write([1, 0, 0, 0, 4, 2])
    #     ser.write(bytearray([0x55, 0x56]))
    #     # ser.write([6, 0, 0, 0, 4])
    #     ser.disconnect()
    # pass

