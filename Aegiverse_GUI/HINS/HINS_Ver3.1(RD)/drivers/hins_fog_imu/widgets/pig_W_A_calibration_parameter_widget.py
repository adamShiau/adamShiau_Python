# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import ast
import builtins
import datetime
import logging
import struct
import time
import pandas

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (QGroupBox, QStackedWidget, QGridLayout, QVBoxLayout, QWidget,
                               QPushButton, QSpacerItem, QSizePolicy, QHBoxLayout,
                               QFileDialog, QMessageBox, QFrame)

from myLib.myGui.mygui_serial import editBlock
from myLib import common as cmn

# 指令 ID 與 參數 Key 的對照表 (對應你原始定義的 CMD_Gyro_... 等)
CMD_MAP = {
    "0": 48, "1": 49, "2": 50,  # Accel Bias: AX, AY, AZ
    "3": 51, "4": 52, "5": 53,  # Accel R: A11, A12, A13
    "6": 54, "7": 55, "8": 56,  # Accel R: A21, A22, A23
    "9": 57, "10": 58, "11": 59,  # Accel R: A31, A32, A33
    "12": 60, "13": 61, "14": 62,  # Gyro Bias: GX, GY, GZ
    "15": 63, "16": 64, "17": 65,  # Gyro R: G11, G12, G13
    "18": 66, "19": 67, "20": 68,  # Gyro R: G21, G22, G23
    "21": 69, "22": 70, "23": 71  # Gyro R: G31, G32, G33
}

INIT_PARAMETERS = {
    "0": 0, "1": 0, "2": 0, "3": 9.8, "4": 0, "5": 0, "6": 0, "7": 9.8, "8": 0, "9": 0, "10": 0,
    "11": 9.8, "12": 0, "13": 0, "14": 0, "15": 1, "16": 0, "17": 0, "18": 0, "19": 1, "20": 0, "21": 0,
    "22": 0, "23": 1
}


class pig_calibration_widget(QGroupBox):
    def __init__(self, act, dataFile, dataFileName):
        super(pig_calibration_widget, self).__init__()
        self.setWindowTitle("IMU Misalignment Calibration")
        self.__act = act
        self.__file = dataFile
        self.filename = dataFileName
        self._updating_ui = False  # 防止回填時觸發指令發送
        self.dumpTrigerState = False

        self.intiUI()

        # --- 配置管理表 (Table-Driven) ---
        # 建立 Key 與 UI 元件的映射關係，方便自動化處理
        self.config_table = {
            "0": {"type": "float", "widget": self.Ax, "comment": "Accel Bias X"},
            "1": {"type": "float", "widget": self.Ay, "comment": "Accel Bias Y"},
            "2": {"type": "float", "widget": self.Az, "comment": "Accel Bias Z"},
            "3": {"type": "float", "widget": self.A1_1, "comment": "A11"},
            "4": {"type": "float", "widget": self.A1_2, "comment": "A12"},
            "5": {"type": "float", "widget": self.A1_3, "comment": "A13"},
            "6": {"type": "float", "widget": self.A2_1, "comment": "A21"},
            "7": {"type": "float", "widget": self.A2_2, "comment": "A22"},
            "8": {"type": "float", "widget": self.A2_3, "comment": "A23"},
            "9": {"type": "float", "widget": self.A3_1, "comment": "A31"},
            "10": {"type": "float", "widget": self.A3_2, "comment": "A32"},
            "11": {"type": "float", "widget": self.A3_3, "comment": "A33"},
            "12": {"type": "float", "widget": self.Wx, "comment": "Gyro Bias X"},
            "13": {"type": "float", "widget": self.Wy, "comment": "Gyro Bias Y"},
            "14": {"type": "float", "widget": self.Wz, "comment": "Gyro Bias Z"},
            "15": {"type": "float", "widget": self.W1_1, "comment": "G11"},
            "16": {"type": "float", "widget": self.W1_2, "comment": "G12"},
            "17": {"type": "float", "widget": self.W1_3, "comment": "G13"},
            "18": {"type": "float", "widget": self.W2_1, "comment": "G21"},
            "19": {"type": "float", "widget": self.W2_2, "comment": "G22"},
            "20": {"type": "float", "widget": self.W2_3, "comment": "G23"},
            "21": {"type": "float", "widget": self.W3_1, "comment": "G31"},
            "22": {"type": "float", "widget": self.W3_2, "comment": "G32"},
            "23": {"type": "float", "widget": self.W3_3, "comment": "G33"},
        }

        self.linkFunction()

    def intiUI(self):
        """ 初始化 UI 佈局 (維持原始結構) """
        All_Layout = QHBoxLayout()
        self.stackView_one = QStackedWidget()
        Angular_velocity_Layout = QVBoxLayout()
        acceleration_Layout = QVBoxLayout()
        OneWidget, TwoWidget = QWidget(), QWidget()

        # 第一頁: Gyro
        R_GroupBox = QGroupBox("Gyro R")
        R_layout = QGridLayout()
        self.W1_1, self.W1_2, self.W1_3 = editBlock("G11"), editBlock("G12"), editBlock("G13")
        self.W2_1, self.W2_2, self.W2_3 = editBlock("G21"), editBlock("G22"), editBlock("G23")
        self.W3_1, self.W3_2, self.W3_3 = editBlock("G31"), editBlock("G32"), editBlock("G33")
        for i, w in enumerate(
                [self.W1_1, self.W1_2, self.W1_3, self.W2_1, self.W2_2, self.W2_3, self.W3_1, self.W3_2, self.W3_3]):
            w.setFixedWidth(150)
            R_layout.addWidget(w, i // 3, (i % 3) * 2, 1, 2)
        R_GroupBox.setLayout(R_layout)

        b_GroupBox = QGroupBox("Gyro b")
        b_layout = QGridLayout()
        self.Wx, self.Wy, self.Wz = editBlock("Bias WX"), editBlock("Bias WY"), editBlock("Bias WZ")
        b_layout.addWidget(self.Wx, 0, 0, 1, 2);
        b_layout.addWidget(self.Wy, 0, 2, 1, 2);
        b_layout.addWidget(self.Wz, 0, 4, 1, 2)
        b_GroupBox.setLayout(b_layout)

        nextPage = QPushButton("next page -->")
        Angular_velocity_Layout.addWidget(R_GroupBox);
        Angular_velocity_Layout.addWidget(b_GroupBox)
        Angular_velocity_Layout.addWidget(nextPage, alignment=Qt.AlignRight)
        Angular_velocity_Layout.addStretch()
        OneWidget.setLayout(Angular_velocity_Layout)

        # 第二頁: Accelerometer
        acc_R_Group = QGroupBox("Accelerometer R")
        acc_R_layout = QGridLayout()
        self.A1_1, self.A1_2, self.A1_3 = editBlock("A11"), editBlock("A12"), editBlock("A13")
        self.A2_1, self.A2_2, self.A2_3 = editBlock("A21"), editBlock("A22"), editBlock("A23")
        self.A3_1, self.A3_2, self.A3_3 = editBlock("A31"), editBlock("A32"), editBlock("A33")
        for i, w in enumerate(
                [self.A1_1, self.A1_2, self.A1_3, self.A2_1, self.A2_2, self.A2_3, self.A3_1, self.A3_2, self.A3_3]):
            w.setFixedWidth(150)
            acc_R_layout.addWidget(w, i // 3, (i % 3) * 2, 1, 2)
        acc_R_Group.setLayout(acc_R_layout)

        acc_b_Group = QGroupBox("Accelerometer b")
        acc_b_layout = QGridLayout()
        self.Ax, self.Ay, self.Az = editBlock("AX"), editBlock("AY"), editBlock("AZ")
        acc_b_layout.addWidget(self.Ax, 0, 0, 1, 2);
        acc_b_layout.addWidget(self.Ay, 0, 2, 1, 2);
        acc_b_layout.addWidget(self.Az, 0, 4, 1, 2)
        acc_b_Group.setLayout(acc_b_layout)

        prevPage = QPushButton("<-- previous page")
        acceleration_Layout.addWidget(acc_R_Group);
        acceleration_Layout.addWidget(acc_b_Group)
        acceleration_Layout.addWidget(prevPage);
        acceleration_Layout.addStretch()
        TwoWidget.setLayout(acceleration_Layout)

        self.stackView_one.addWidget(OneWidget);
        self.stackView_one.addWidget(TwoWidget)
        nextPage.clicked.connect(lambda: self.stackView_one.setCurrentIndex(1))
        prevPage.clicked.connect(lambda: self.stackView_one.setCurrentIndex(0))

        # 控制按鈕區
        setting_frame = QFrame()
        setting_frame.setStyleSheet("background-color: rgba(0, 0, 0, 192); border-radius: 10px;")
        self.dump_Btn = QPushButton("Dump")
        self.init_para_btn = QPushButton("Init Para")
        self.loadMisalignmentFile_Gyro = QPushButton("Load Gyro File")
        self.loadMisalignmentFile_Acce = QPushButton("Load Acceleration File")
        self.export_Btn = QPushButton("Export")
        self.import_Btn = QPushButton("Import")

        btn_layout = QVBoxLayout()
        for btn in [self.dump_Btn, self.init_para_btn, self.loadMisalignmentFile_Gyro,
                    self.loadMisalignmentFile_Acce, self.export_Btn, self.import_Btn]:
            btn.setFixedHeight(30)
            self.setBtnStyle(btn)
            btn_layout.addWidget(btn)
        setting_frame.setLayout(btn_layout)

        All_Layout.addWidget(setting_frame, 1);
        All_Layout.addWidget(self.stackView_one, 3)
        self.setLayout(All_Layout)

    def linkFunction(self):
        """ 連接按鈕與數值變動信號 """
        self.dump_Btn.clicked.connect(self.dump_cali_parameter)
        self.init_para_btn.clicked.connect(self.init_para)
        self.export_Btn.clicked.connect(self.export_to_txt)
        self.import_Btn.clicked.connect(self.import_from_txt)
        self.loadMisalignmentFile_Gyro.clicked.connect(lambda: self.loadCSVandWriteMisalignment("G"))
        self.loadMisalignmentFile_Acce.clicked.connect(lambda: self.loadCSVandWriteMisalignment("A"))

        # 為所有輸入框綁定自動變色與發送指令功能
        for cid, info in self.config_table.items():
            info["widget"].le.textChanged.connect(lambda _, c=cid: self._on_value_changed(c))

    # --- 工具函數 ---
    def setBtnStyle(self, item):
        item.setStyleSheet("QPushButton { background-color: rgba(0, 0, 0, 32); color: white; border-radius: 10px; }"
                           "QPushButton::hover { background-color: white; color: black; }")

    def _float_to_int_bits(self, val_str: str) -> int:
        try:
            return struct.unpack('<I', struct.pack('<f', float(val_str)))[0]
        except:
            return 0

    def _int_bits_to_float_str(self, val_int: int) -> str:
        try:
            f_val = struct.unpack('<f', struct.pack('<I', int(val_int) & 0xFFFFFFFF))[0]
            return f"{f_val:.10f}".rstrip('0').rstrip('.')
        except:
            return "0"

    # --- 核心邏輯 (重寫部分) ---

    def dump_cali_parameter(self):
        """ 從硬體讀取並根據 type 進行轉換回填 """
        if not self.__act: return
        self.__act.flushInputBuffer("None")
        cfg = self.__act.dump_cali_parameters(2)

        if isinstance(cfg, dict):
            self._updating_ui = True
            try:
                for cid, info in self.config_table.items():
                    raw_val = cfg.get(cid)
                    if raw_val is None: continue

                    # 根據 Table 中的 type 決定轉換方式
                    if info["type"] == "float":
                        val_str = self._int_bits_to_float_str(raw_val)
                    else:
                        val_str = str(int(raw_val))

                    info["widget"].le.setText(val_str)
                    info["widget"].le.setStyleSheet('background-color: white')
                self.dumpTrigerState = True
                QMessageBox.information(self, "Success", "Cali parameters dumped.")
            finally:
                self._updating_ui = False

    def export_to_txt(self):
        """ 修正檔名格式：日期 + _cali.txt """
        if not self.dumpTrigerState:
            QMessageBox.warning(self, "Warning", "Please Dump first.")
            return

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # 修改 1: 檔名改為 日期 + _cali.txt
        default_name = f"{now}_cali.txt"

        path, _ = QFileDialog.getSaveFileName(self, "Export Calibration", default_name, "Text Files (*.txt)")
        if not path: return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# IMU Calibration Export - {now}\n\n")
                for cid in sorted(self.config_table.keys(), key=int):
                    info = self.config_table[cid]
                    val = info["widget"].le.text()
                    # 這裡輸出純文字數值與註解
                    f.write(f"{cid}={val:<15} # {info['comment']}\n")
            QMessageBox.information(self, "Success", "Calibration data exported.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def import_from_txt(self):
        """ 根據 type 進行讀取回填並觸發指令 """
        if not self.dumpTrigerState:
            QMessageBox.warning(self, "Warning", "Please Dump first.")
            return

        path, _ = QFileDialog.getOpenFileName(self, "Import Calibration", "", "Text Files (*.txt)")
        if not path: return

        try:
            cfg_data = {}
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    clean = line.split('#')[0].strip()
                    if "=" in clean:
                        k, v = clean.split('=')
                        cfg_data[k.strip()] = v.strip()

            self._updating_ui = False  # 確保 setText 會觸發 _on_value_changed
            for cid, info in self.config_table.items():
                if cid in cfg_data:
                    # 這裡直接填入字串，_on_value_changed 會負責處理轉碼發送
                    info["widget"].le.setText(cfg_data[cid])

            QMessageBox.information(self, "Success", "Import success and commands sent.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import failed: {e}")

    def _on_value_changed(self, cid):
        """ 統一發送指令，根據 type 處理編碼 """
        if getattr(self, '_updating_ui', False): return

        info = self.config_table[cid]
        val_str = info["widget"].le.text().strip()
        if not val_str: return

        info["widget"].le.setStyleSheet('background-color: yellow')

        cmd = CMD_MAP.get(cid)
        if cmd and self.__act:
            # 根據 type 決定發送前如何打包
            if info["type"] == "float":
                val_int = self._float_to_int_bits(val_str)
            else:
                val_int = int(float(val_str))  # 處理帶 .0 的整數情況

            self.__act.writeImuCmd(cmd, val_int, 4)
    def init_para(self):
        """ 初始化參數 (批次發送) """
        if QMessageBox.question(self, "Init", "Reset all parameters to default?") != QMessageBox.Yes: return

        self._updating_ui = False
        for cid, val in INIT_PARAMETERS.items():
            if cid in self.config_table:
                self.config_table[cid]["widget"].le.setText(str(val))
                time.sleep(0.02)  # 防止指令堆疊過快
        QMessageBox.information(self, "Done", "Parameters reset.")

    def loadCSVandWriteMisalignment(self, mode):
        """ 讀取校正報表 (維持原始 CSV 解析邏輯) """
        if not self.dumpTrigerState:
            QMessageBox.warning(self, "Warning", "Please Dump first.")
            return

        path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if path:
            data = cmn.loadCSVFile(path)
            self._updating_ui = False
            try:
                # 這裡對應你原始的 pandas iloc 讀取邏輯
                R = data.iloc[0:3, 2:5]  # 假設 R 矩陣位置
                bias = data.get("Bias", [0, 0, 0])

                if mode == "G":
                    targets = ["15", "16", "17", "18", "19", "20", "21", "22", "23"]  # Gyro R
                    for i, cid in enumerate(targets):
                        val = R.iloc[i // 3, i % 3]
                        self.config_table[cid]["widget"].le.setText(f"{val:.10f}".rstrip('0').rstrip('.'))
                else:
                    targets = ["3", "4", "5", "6", "7", "8", "9", "10", "11"]  # Accel R
                    for i, cid in enumerate(targets):
                        val = R.iloc[i // 3, i % 3]
                        self.config_table[cid]["widget"].le.setText(f"{val:.10f}".rstrip('0').rstrip('.'))
                    # Bias X, Y, Z
                    for i, cid in enumerate(["0", "1", "2"]):
                        self.config_table[cid]["widget"].le.setText(f"{bias[i]:.10f}".rstrip('0').rstrip('.'))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to parse CSV: {e}")


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication


    class Dummy:
        def dump_cali_parameters(self, t): return {"0": 0, "15": 1065353216}  # 1.0

        def writeImuCmd(self, *args): print(f"CMD Sent: {args}")

        def flushInputBuffer(self, x): pass


    app = QApplication(sys.argv)
    win = pig_calibration_widget(Dummy(), None, "test")
    win.show()
    sys.exit(app.exec())