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
        self.__ser.timeout = 25
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

    def _find_sync_fa(self, timeout_s: float) -> None:
        """Consume bytes until 0xFA is found (sync)."""
        end = time.time() + timeout_s
        while time.time() < end:
            b = self.__ser.read(1)
            if not b:
                continue
            if b[0] == 0xFA:
                return
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

        return {
            "type": ftype, "cmd": cmd, "status": status,
            "len": length, "payload": payload
        }

    # ---------- updated dump ----------

    def dump_fog_parameters(self, ch=3):
        # 送命令維持你目前的格式：AB BA ... 55 56
        self.__ser.write(bytearray([0xAB, 0xBA]))
        self.__ser.write([0x66, 0, 0, 0, 0x02, ch])
        self.__ser.write(bytearray([0x55, 0x56]))

        try:
            # 1) ACK
            ack = self._read_frame(timeout_s=1.0)
            if ack["type"] != 0xA1 or ack["cmd"] != 0x66:
                raise ValueError(f"unexpected ACK frame: {ack}")
            if ack["len"] != 0:
                # 依你規格 ACK 應該是 len=0
                raise ValueError(f"ACK len should be 0, got {ack['len']}")

            # ACK 的 status 代表「已受理」；若你 MCU 規劃 ACK 可能回錯誤碼，這裡可先擋
            # if ack["status"] != 0: ...

            # 2) RESULT
            res = self._read_frame(timeout_s=2.0)  # dump 可能比 ACK 慢
            if res["type"] != 0xA2 or res["cmd"] != 0x66:
                raise ValueError(f"unexpected RESULT frame: {res}")

            # status handling
            if res["len"] == 0:
                # timeout / failure：照你結論 timeout 會 len=0
                return "無法取得值"

            # payload: JSON bytes
            payload_bytes = res["payload"]
            try:
                payload_str = payload_bytes.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                # 如果 MCU 送的是 ASCII/UTF-8 混雜，寬鬆一點也行
                payload_str = payload_bytes.decode("utf-8", errors="replace")

            return json.loads(payload_str)

        except TimeoutError:
            logger.error("dump_fog_parameters timeout while waiting ACK/RESULT")
            return "無法取得值"
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"dump_fog_parameters parse error: {e}")
            return "無法取得值"

    def dump_cali_parameters(self, ch=2):
        # CMD_DUMP_MIS = 0x81
        self.__ser.write(bytearray([0xAB, 0xBA]))
        self.__ser.write([0x81, 0, 0, 0, 0, ch])
        self.__ser.write(bytearray([0x55, 0x56]))

        try:
            # 1) ACK (A1)
            ack = self._read_frame(timeout_s=1.0)
            if ack["type"] != 0xA1 or ack["cmd"] != 0x81:
                raise ValueError(f"unexpected ACK frame: {ack}")
            if ack["len"] != 0:
                raise ValueError(f"ACK len should be 0, got {ack['len']}")

            # 2) RESULT (A2)
            res = self._read_frame(timeout_s=2.0)
            if res["type"] != 0xA2 or res["cmd"] != 0x81:
                raise ValueError(f"unexpected RESULT frame: {res}")

            if res["len"] == 0:
                # timeout / failure：依你 MCU 規格 len=0
                return "無法取得值"

            payload_bytes = res["payload"]
            try:
                payload_str = payload_bytes.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                payload_str = payload_bytes.decode("utf-8", errors="replace")

            return json.loads(payload_str)

        except TimeoutError:
            logger.error("dump_cali_parameters timeout while waiting ACK/RESULT")
            return "無法取得值"
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"dump_cali_parameters parse error: {e}")
            return "無法取得值"

    # def dump_cali_parameters(self, ch=2):
    #     self.__ser.write(bytearray([0xAB, 0xBA]))
    #     self.__ser.write([0x81, 0, 0, 0, 0, ch])
    #     self.__ser.write(bytearray([0x55, 0x56]))
    #     caliVal = self.__ser.read_until(b'\n')
    #     try:
    #         return json.loads(caliVal)
    #     except json.JSONDecodeError:
    #         logger.error("執行撈取misalignment參數出現錯誤。")
    #         return False


    def getVersion(self, ch=2):
        self.__ser.write(bytearray([0xAB, 0xBA]))
        self.__ser.write([0x83, 0, 0, 0, 0, ch])
        self.__ser.write(bytearray([0x55, 0x56]))
        try:
            # 1) ACK (A1): FA A1 83 status lenL lenH checksum16
            ack = self._read_frame(timeout_s=1.0)
            if ack["type"] != 0xA1 or ack["cmd"] != 0x83:
                raise ValueError(f"unexpected ACK frame: {ack}")
            if ack["len"] != 0:
                raise ValueError(f"ACK len should be 0, got {ack['len']}")

            # 2) RESULT (A2): FA A2 83 status lenL lenH payload[len] checksum16
            res = self._read_frame(timeout_s=2.0)
            if res["type"] != 0xA2 or res["cmd"] != 0x83:
                raise ValueError(f"unexpected RESULT frame: {res}")

            if res["len"] == 0:
                # timeout / failure
                return "Error"

            ver = res["payload"].decode("ascii", errors="replace")
            ver = ver.rstrip("\x00").rstrip("\r").rstrip("\n").strip()
            return ver

        except TimeoutError:
            logger.error("getVersion timeout while waiting ACK/RESULT")
            return "Error"
        except ValueError as e:
            logger.error(f"getVersion parse error: {e}")
            return "Error"

    def dump_SN_parameters(self, ch=2):
        # CMD_DUMP_SN = 0x82
        self.__ser.write(bytearray([0xAB, 0xBA]))
        self.__ser.write([0x82, 0, 0, 0, 0, ch])
        self.__ser.write(bytearray([0x55, 0x56]))

        try:
            # 1) ACK (A1): FA A1 82 status lenL lenH checksum16
            ack = self._read_frame(timeout_s=1.0)
            if ack["type"] != 0xA1 or ack["cmd"] != 0x82:
                raise ValueError(f"unexpected ACK frame: {ack}")
            if ack["len"] != 0:
                # 依你的規格 ACK 應該 len=0
                raise ValueError(f"ACK len should be 0, got {ack['len']}")

            # 2) RESULT (A2): FA A2 82 status lenL lenH payload[len] checksum16
            res = self._read_frame(timeout_s=2.0)
            if res["type"] != 0xA2 or res["cmd"] != 0x82:
                raise ValueError(f"unexpected RESULT frame: {res}")

            if res["len"] == 0:
                # MCU timeout / SN 未設定 / 其他 failure（你目前 GUI 用這個訊息判斷）
                return "發生參數值為空的狀況"

            payload = res["payload"]

            # 你的 SN payload 固定 12 bytes ASCII（可含空白/0x00 padding）
            # 先 decode，再把尾端 padding 去掉，讓 GUI 顯示更乾淨
            sn = payload.decode("ascii", errors="replace")
            sn = sn.rstrip("\x00").rstrip(" ")

            # 若全部被 strip 乾淨變空字串，仍回報為空
            if sn == "":
                return "發生參數值為空的狀況"

            return sn

        except TimeoutError:
            logger.error("dump_SN_parameters timeout while waiting ACK/RESULT")
            return "發生參數值為空的狀況"
        except ValueError as e:
            logger.error(f"dump_SN_parameters parse error: {e}")
            return "發生參數值為空的狀況"


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

