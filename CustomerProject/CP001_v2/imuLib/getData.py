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

def alignHeader_4B(comportObj, header):
    datain = comportObj.readBinaryList(4)
    while 1:
        if datain == header:
            return datain
        else:
            datain[0] = datain[1]
            datain[1] = datain[2]
            datain[2] = datain[3]
            datain[3] = comportObj.readBinaryList(1)[0]
            # print(datain)
# End of alignHeader_4B


def getdataPacket(comportObj, head, rbytes=25):
    rdata = comportObj.readBinaryList(rbytes)
    imuPacket = head + rdata
    return imuPacket
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
