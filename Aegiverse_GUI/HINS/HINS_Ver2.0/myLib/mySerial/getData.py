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
import myLib.common as cmn
import sys

PRINT_DEBUG = 0


def alignHeader_4B(comportObj, header):
    datain = comportObj.readBinaryList(4)
    while 1:
        if datain == header:
            return datain
        else:
            try:
                datain[0] = datain[1]
                datain[1] = datain[2]
                datain[2] = datain[3]
                datain[3] = comportObj.readBinaryList(1)[0]
            # except IndexError:
            #     logger.error('IndexError: alignHeader_4B')
            #     sys.exit()
            #     break
            except:
                logger.error('alignHeader_4B Error')
                return False
                # sys.exit()
                # break

            # print(datain)


# End of alignHeader_4B

def alignHeader_7B(comportObj, header):
    datain = comportObj.readBinaryList(7)
    while 1:
        if datain == header:
            return datain
        else:
            try:
                datain[0] = datain[1]
                datain[1] = datain[2]
                datain[2] = datain[3]
                datain[3] = datain[4]
                datain[4] = datain[5]
                datain[5] = datain[6]
                datain[6] = comportObj.readBinaryList(1)[0]
                # print(datain, header, datain==header)
            except IndexError:
                logger.error('IndexError: alignHeader_7B')
                sys.exit()
                break


def getdataPacket(comportObj, head, rbytes=25):
    rdata = comportObj.readBinaryList(rbytes)
    imuPacket = head + rdata
    if rdata == False:
        return False
    return imuPacket


# End of getdataPacket

# --- getData.py 01-18-2026 ---

class ImuParser:
    def __init__(self, header, pkt_len):
        self.header = list(header)
        self.pkt_len = pkt_len
        self.buffer = []

    def push_byte(self, byte):
        self.buffer.append(byte)
        h_len = len(self.header)
        # 狀態機階段 1: 標頭對齊 (對應 alignHeader 邏輯)
        if len(self.buffer) <= h_len:
            if self.buffer != self.header[:len(self.buffer)]:
                self.buffer.pop(0) # 標頭不符，滑動 1 Byte
            return None
        # 狀態機階段 2: 收集數據 (對應 getdataPacket 邏輯)
        if len(self.buffer) == self.pkt_len:
            packet = list(self.buffer)
            self.buffer = [] # 清空緩衝區，準備下一包
            return packet
        return None

class HinsParser:
    def __init__(self):
        self.buffer = []

    def push_byte(self, byte):
        if not self.buffer and byte != 0xFA:
            return None
        self.buffer.append(byte)
        if len(self.buffer) < 6: return None
        # V1 協議：SOF(0), TYPE(1), CMD(2), STATUS(3), LenL(4), LenH(5)
        payload_len = self.buffer[4] | (self.buffer[5] << 8)
        total_len = 6 + payload_len + 2 # Header(6) + Payload + Checksum(2)
        if len(self.buffer) == total_len:
            packet = list(self.buffer)
            self.buffer = []
            return packet
        return None

class ProtocolDispatcher:
    def __init__(self):
        self.parsers = []
    def add_parser(self, parser, callback):
        self.parsers.append({'p': parser, 'c': callback})
    def feed_data(self, raw_bytes):
        """ 接收來自 Connector.readBinaryList 的原始列表數據 """
        for byte in raw_bytes:
            for item in self.parsers:
                packet = item['p'].push_byte(byte)
                if packet:
                    item['c'](packet)
                    break # 封包已被領走，不交給其他解析器


if __name__ == "__main__":
    from Connector import Connector
    import time

    HEADER_KVH = [0xFE, 0x81, 0xFF, 0x55]
    ser = Connector("COM5")
    old_time = time.perf_counter()
    ser.connect()
    ser.write([5, 0, 0, 0, 1])
    try:
        while 1:
            ser.readInputBuffer()
            head = alignHeader_4B(ser, HEADER_KVH)
            dataPacket = getdataPacket(ser, head, 25)
            print(dataPacket)
            print("%f\n" % ((time.perf_counter() - old_time) * 1e6))
            old_time = time.perf_counter()

    except KeyboardInterrupt:
        ser.write([5, 0, 0, 0, 4])
        ser.disconnect()
    pass
