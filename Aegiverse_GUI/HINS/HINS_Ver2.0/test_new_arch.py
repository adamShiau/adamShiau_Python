# test_new_arch.py (自動發送測試版)
import sys
import os
import time
from drivers.hins_gnss_ins.hins_gnss_ins_reader import HinsGnssInsReader
from myLib.mySerial.Connector import Connector
from PySide6.QtWidgets import QApplication # 必須導入


def ack_callback(data):
    # 當收到封包時印出
    hex_str = " ".join(["%02X" % b for b in data])
    print(f"\n[RX] 收到回傳: {hex_str}")


if __name__ == "__main__":
    # 1. 建立 QApplication，這會接管事件迴圈
    app = QApplication(sys.argv)

    ser = Connector(portName="COM8", baudRate=230400)
    if not ser.connectConn():
        print("無法連接 COM8")
        sys.exit()

    reader = HinsGnssInsReader()
    reader.set_connector(ser)

    # 這裡的連結是正確的
    reader.raw_ack_qt.connect(ack_callback)

    print("1. 啟動 Reader 執行緒...")
    reader.start()
    time.sleep(0.5)

    cmd_read_gp1 = [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x0C, 0x04, 0x04, 0x41, 0x02, 0x01, 0x32, 0x9F, 0x51, 0x52]
    print(f"2. 發送指令: {' '.join(['%02X' % b for b in cmd_read_gp1])}")
    reader.write_raw(cmd_read_gp1)

    print("3. 進入事件迴圈，等待回應...")

    # 2. 替代 while True，使用 app.exec()
    # 這會讓主執行緒開始處理所有進來的訊號
    sys.exit(app.exec())