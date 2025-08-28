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

ExternalName_log = __name__
if os.getenv('verNum') == str(True) :
    ExternalName_log = "getDt_logger"

logProcess.fileStartedInfo(logger_name, ExternalName_log)
# logger = logging.getLogger(logger_name + '.' + ExternalName_log)
# logger.info(__name__ + ' logger start')
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
            except IndexError as e:  # ValueError的錯誤，在list中不會出現此錯誤，除非有使用到轉換類型或運算，才有可能因資料類型不同發生ValueError。
                # tb = e.__traceback__  # 錯誤軌跡資訊
                # # 錯誤內容：請確認陣列的索引數量是符合設定撈取的數量。alignHeader_4B Error
                # logProcess.centrailzedError(num="", fileName=ExternalName_log, content='Please make sure the number of indices matches the expected dimensions for retrieval.', line=tb.tb_lineno)
                logProcess.receive(logName=logger_name, num="1600001", fileName=ExternalName_log, error=e)
                # sys.exit()
                # break
                return False

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
                print("IndexError: alignHeader_7B")
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
