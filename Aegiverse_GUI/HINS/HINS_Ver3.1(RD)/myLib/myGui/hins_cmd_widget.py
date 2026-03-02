# -*- coding:UTF-8 -*-
import sys
import os
import logging
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QGridLayout, QApplication)

# 處理 Logger
import builtins

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)


class hins_cmd_widget(QWidget):
    def __init__(self, act=None, parent=None):
        super().__init__(parent)
        self.__act = act
        self.setWindowTitle("HINS Command Control & Monitor")
        self.resize(650, 450)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # --- GPIO 控制區 ---
        gp_group = QGroupBox("HINS GPIO Setting")
        gp_lay = QGridLayout()

        self.btn_set_gp1 = QPushButton("Set GP1 (UART2 Tx)")
        self.btn_read_gp1 = QPushButton("Read GP1")
        self.btn_set_gp2 = QPushButton("Set GP2 (UART2 Rx)")
        self.btn_read_gp2 = QPushButton("Read GP2")

        gp_lay.addWidget(self.btn_set_gp1, 0, 0)
        gp_lay.addWidget(self.btn_read_gp1, 0, 1)
        gp_lay.addWidget(self.btn_set_gp2, 1, 0)
        gp_lay.addWidget(self.btn_read_gp2, 1, 1)
        gp_group.setLayout(gp_lay)
        main_layout.addWidget(gp_group)

        # --- 指令監控區 ---
        monitor_group = QGroupBox("Command Monitor")
        mon_lay = QGridLayout()

        mon_lay.addWidget(QLabel("Last Sent (TX):"), 0, 0)
        self.le_sent = QLineEdit()
        self.le_sent.setReadOnly(True)
        self.le_sent.setStyleSheet("color: blue; font-weight: bold; font-family: Consolas;")
        mon_lay.addWidget(self.le_sent, 0, 1)

        mon_lay.addWidget(QLabel("Last Received (RX):"), 1, 0)
        self.le_recv = QLineEdit()
        self.le_recv.setReadOnly(True)
        self.le_recv.setStyleSheet("color: darkgreen; font-weight: bold; font-family: Consolas;")
        mon_lay.addWidget(self.le_recv, 1, 1)

        monitor_group.setLayout(mon_lay)
        main_layout.addWidget(monitor_group)
        main_layout.addStretch()

        # 連接按鈕
        self.btn_set_gp1.clicked.connect(lambda: self.send_hins_cmd("SET_GP1"))
        self.btn_set_gp2.clicked.connect(lambda: self.send_hins_cmd("SET_GP2"))
        self.btn_read_gp1.clicked.connect(lambda: self.send_hins_cmd("READ_GP1"))
        self.btn_read_gp2.clicked.connect(lambda: self.send_hins_cmd("READ_GP2"))

    @QtCore.Slot(list)
    def update_rx_display(self, data):
        """ 更新接收顯示欄位 """
        hex_str = " ".join(["%02X" % b for b in data])
        self.le_recv.setText(hex_str)

    def send_hins_cmd(self, action):
        if not self.__act: return

        mip_map = {
            "SET_GP1": [0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x01, 0x05, 0x21, 0x00, 0x5D, 0xAE],
            "SET_GP2": [0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x02, 0x05, 0x22, 0x02, 0x61, 0xB6],
            "READ_GP1": [0x75, 0x65, 0x0C, 0x04, 0x04, 0x41, 0x02, 0x01, 0x32, 0x9F],
            "READ_GP2": [0x75, 0x65, 0x0C, 0x04, 0x04, 0x41, 0x02, 0x02, 0x33, 0xA0]
        }

        mip_payload = mip_map.get(action)
        # 格式：BC CB + 97 + Len + MIP + 51 52
        full_pkt = [0xBC, 0xCB, 0x97, len(mip_payload)] + mip_payload + [0x51, 0x52]

        # 更新顯示
        self.le_sent.setText(" ".join(["%02X" % b for b in full_pkt]))

        # 送出
        try:
            self.__act.writeRawCmd(full_pkt)
        except Exception as e:
            self.le_sent.setText(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = hins_cmd_widget()
    window.show()
    sys.exit(app.exec())