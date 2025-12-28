# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import ast
import builtins
import datetime
import decimal
import logging
import math
import re
import time

import numpy as np
import pandas as pd
from PySide6 import QtWidgets, QtCore

from myLib.myGui.myComboBox import comboGroup_1
if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys
import struct

sys.path.append("../../")
print(__name__)
print(sys.path)
from myLib.myGui.mygui_serial import *
from myLib import common as cmn
from myLib.myGui.myLabel import *


from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel
from PySide6.QtCore import Qt

from myLib.myGui.myLabel import *  # spinBlock

CMD_CFG_DR = 0x48
CMD_CFG_BR = 0x49

BR_TABLE = [9600, 115200, 230400, 460800, 921600]
DR_TABLE = [10, 50, 100, 200, 400]


class pig_configuration_widget(QWidget):
    def __init__(self, act=None, parent=None):
        super().__init__(parent)
        self.__act = act
        self._updating_ui = False  # 防止 dump 回填時又觸發 valueChanged

        self.setWindowTitle("Configuration")
        self.resize(420, 220)

        # --- UI ---
        self.br_idx = spinBlock(title="Baudrate Index", minValue=0, maxValue=4, double=False, step=1)
        self.dr_idx = spinBlock(title="Datarate Index", minValue=0, maxValue=4, double=False, step=1)

        self.br_hint = QLabel("Index->BR: 0=9600,1=115200,2=230400,3=460800,4=921600")
        self.dr_hint = QLabel("Index->DR: 0=10,1=50,2=100,3=200,4=400 Hz")

        self.dump_btn = QPushButton("Dump Configuration")

        layout = QGridLayout()
        layout.addWidget(self.dr_idx,   0, 0, 1, 2)
        layout.addWidget(self.dr_hint,  1, 0, 1, 2)
        layout.addWidget(self.br_idx,   2, 0, 1, 2)
        layout.addWidget(self.br_hint,  3, 0, 1, 2)
        layout.addWidget(self.dump_btn, 4, 0, 1, 2)
        self.setLayout(layout)

        # --- signal ---
        self.dr_idx.spin.valueChanged.connect(self._on_dr_changed)
        self.br_idx.spin.valueChanged.connect(self._on_br_changed)
        self.dump_btn.clicked.connect(self.dump_configuration)

    # ✅ 新增：覆寫 show()，方便你先看排版（也會把視窗帶到最上層）
    def show(self):
        super().show()
        self.raise_()
        self.activateWindow()

    def _ensure_act(self) -> bool:
        """act 尚未接上時，先提示並阻止送命令/讀取。"""
        if self.__act is None:
            QtWidgets.QMessageBox.information(
                self, "Info",
                "act 尚未設定，目前僅供檢視版面。\n\n"
                "請在 connectMain() 後用 pig_configuration_widget(self.act) 建立。"
            )
            return False
        return True

    def _on_dr_changed(self, idx: int):
        if self._updating_ui:
            return
        if not self._ensure_act():
            return

        idx = int(idx)
        if 0 <= idx <= 4:
            self.__act.writeImuCmd(CMD_CFG_DR, idx, 6)  # ch 固定 6

    def _on_br_changed(self, idx: int):
        if self._updating_ui:
            return
        if not self._ensure_act():
            return

        idx = int(idx)
        if 0 <= idx <= 4:
            self.__act.writeImuCmd(CMD_CFG_BR, idx, 6)  # ch 固定 6

    def dump_configuration(self):
        if not self._ensure_act():
            return

        self.__act.flushInputBuffer("None")
        cfg = self.__act.dump_configuration()

        if isinstance(cfg, dict):
            dr = int(cfg.get("0", 0))  # "0" -> datarate idx
            br = int(cfg.get("1", 0))  # "1" -> baudrate idx

            self._updating_ui = True
            try:
                self.dr_idx.spin.setValue(max(0, min(4, dr)))
                self.br_idx.spin.setValue(max(0, min(4, br)))
            finally:
                self._updating_ui = False

        elif cfg == "無法取得值":
            QtWidgets.QMessageBox.warning(
                self, "Dump Error",
                "Error occurred while dumping configuration.\nPlease check if the device has power."
            )

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # act 先給 None，只看版面
    w = pig_configuration_widget(act=None)
    w.show()

    sys.exit(app.exec())
