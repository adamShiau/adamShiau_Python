# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import os
from myLib.logProcess import logProcess

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

import time
import logging
from collections import deque

logger = logging.getLogger(__name__)

def alignHeader_4B(comportObj, header, *, timeout_s=2.0, max_scan_bytes=100000):
    """
    在串流中對齊 4-byte header。
    - comportObj.readBinaryList(n) 預期回傳 list[int] 或 tuple[int]，若回傳 False/None/空，將略過並重試（直到逾時/達到上限）。
    - header 預期為長度 4 的可迭代（list/tuple/bytes），元素 0~255。
    回傳：list[4]（找到 header）或 None（逾時/失敗）
    """
    # 標準化 header
    hdr = list(header)
    if len(hdr) != 4:
        logger.error("alignHeader_4B: header length != 4, got %r", header)
        return None

    win = deque(maxlen=4)
    start = time.monotonic()
    scanned = 0

    # 先嘗試讀滿 4 bytes
    first = comportObj.readBinaryList(4)
    if not (isinstance(first, (list, tuple)) and len(first) == 4):
        logger.error("alignHeader_4B: initial readBinaryList(4) failed, got %r", first)
        return None
    win.extend(int(x) & 0xFF for x in first)
    scanned += 4

    # 主循環
    while True:
        if list(win) == hdr:
            return list(win)

        # 逾時/掃描上限保護
        if (time.monotonic() - start) > timeout_s or scanned >= max_scan_bytes:
            logger.warning("alignHeader_4B: timeout/max_scan reached (scanned=%d)", scanned)
            return None

        nxt = comportObj.readBinaryList(1)
        # 串口暫時沒有資料或異常：短暫 sleep 後重試，而不是崩潰
        if not (isinstance(nxt, (list, tuple)) and len(nxt) == 1):
            time.sleep(0.001)
            continue

        win.append(int(nxt[0]) & 0xFF)
        scanned += 1


''' 
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
            except IndexError as e:  # ValueError的錯誤，在list中不會出現此錯誤，除非有使用到轉換類型或運算，才有可能因資料類型不同發生ValueError。
                logger.error('1600001, Please make sure the number of indices matches the expected dimensions for retrieval.')
                # sys.exit()
                # break
                return False

            # print(datain)
# End of alignHeader_4B
'''

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
                print("1600002, IndexError: alignHeader_7B")
                # logger.error('IndexError: alignHeader_7B')
                sys.exit()
                break

def getdataPacket(comportObj, head, rbytes=25):
    rdata = comportObj.readBinaryList(rbytes)
    if head == False or rdata == False:
        return False
    imuPacket = head + rdata
    return imuPacket
    # if head == False:
    #     rdata = comportObj.readBinaryList(rbytes)
    #     imuPacket = head + rdata
    #     return imuPacket
    # else:
    #     imuPacket= head
    #     return imuPacket
# End of getdataPacket


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
