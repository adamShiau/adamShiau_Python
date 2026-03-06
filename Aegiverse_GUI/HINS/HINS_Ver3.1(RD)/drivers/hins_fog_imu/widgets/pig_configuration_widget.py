# -*- coding:UTF-8 -*-
import logging
import struct
import time
import datetime
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QFileDialog, QMessageBox)
from myLib.myGui.mygui_serial import *
from myLib.myGui.myLabel import *

# 指令常數定義
CMD_CFG_DR = 0x48
CMD_CFG_BR = 0x49
CMD_CFG_RSC_MAP = [
    [0x4A, 0x4B, 0x4C],
    [0x4D, 0x4E, 0x4F],
    [0x50, 0x51, 0x52]
]
CMD_CFG_LF = 0x53
CMD_CFG_LPF_G = 0x54
CMD_CFG_LPF_A = 0x55
CMD_CFG_WZ_SRC = 0x56

LPF_G_TABLE = ["133 Hz", "128 Hz", "112 Hz", "134 Hz", "86 Hz", "48 Hz", "24.6 Hz", "12.6 Hz"]
LPF_A_TABLE = ["104 Hz", "41.6 Hz", "20.8 Hz", "9.24 Hz", "4.2 Hz", "2.1 Hz", "1 Hz", "0.5 Hz"]


class pig_configuration_widget(QWidget):
    rcs_updated_qt = Signal(list)

    def __init__(self, act=None, parent=None):
        super().__init__(parent)
        self.__act = act
        self._updating_ui = False

        self.setWindowTitle("Configuration")
        self.resize(450, 800)

        # --- UI 初始化 ---
        self._init_ui()

        # --- 核心：配置管理表 (Table-Driven Design) ---
        # 建立一個統一的對照表，未來增加參數只需改這裡
        self.config_table = {
            "0": {"type": "int", "widget": self.dr_idx.spin, "comment": "Data Rate Index"},
            "1": {"type": "int", "widget": self.br_idx.spin, "comment": "Baud Rate Index"},
            "11": {"type": "enum", "widget": self.lf_btn_group, "comment": "Local Frame (0:ENU, 1:NED)"},
            "12": {"type": "int", "widget": self.lpf_g_idx.spin, "comment": "Gyro LPF Index"},
            "13": {"type": "int", "widget": self.lpf_a_idx.spin, "comment": "Accl LPF Index"},
            "14": {"type": "enum", "widget": self.gz_btn_group, "comment": "Gyro Z Source (0:MEMS, 1:FOG)"},
        }
        # 動態加入 RCS Matrix (ID 2~10) 到 Table
        for i in range(2, 11):
            r, c = (i - 2) // 3, (i - 2) % 3
            self.config_table[str(i)] = {
                "type": "float",
                "widget": self.rcs_elements[r][c].spin,
                "comment": f"RCS Matrix R{r + 1}{c + 1}"
            }

        # --- Signal 連線 ---
        self._connect_signals()

    def _init_ui(self):
        """初始化所有 UI 組件"""
        self.br_idx = spinBlock(title="Baudrate Index", minValue=0, maxValue=4, double=False, step=1)
        self.dr_idx = spinBlock(title="Datarate Index", minValue=0, maxValue=4, double=False, step=1)
        self.br_hint = QLabel("Index->BR: 0=9600, 1=115200, 2=230400, 3=460800, 4=921600")
        self.dr_hint = QLabel("Index->DR: 0=10, 1=50, 2=100, 3=200, 4=400 Hz")

        # RCS Matrix
        self.rcs_group = QGroupBox("Sensor to Case (RCS) Matrix")
        rcs_layout = QGridLayout()
        self.rcs_elements = []
        for r in range(3):
            row = []
            for c in range(3):
                sb = spinBlock(title=f"R{r + 1}{c + 1}", minValue=-10, maxValue=10, double=True, step=0.01)
                rcs_layout.addWidget(sb, r, c)
                row.append(sb)
            self.rcs_elements.append(row)
        self.rcs_group.setLayout(rcs_layout)
        self.set_rcs_btn = QPushButton("Set RCS Matrix")

        # Local Frame
        self.lf_group = QGroupBox("Local Frame Setting")
        lf_layout = QHBoxLayout()
        self.cb_enu, self.cb_ned = QtWidgets.QCheckBox("ENU"), QtWidgets.QCheckBox("NED")
        self.lf_btn_group = QtWidgets.QButtonGroup(self)
        self.lf_btn_group.addButton(self.cb_enu, 0)
        self.lf_btn_group.addButton(self.cb_ned, 1)
        lf_layout.addWidget(self.cb_enu);
        lf_layout.addWidget(self.cb_ned)
        self.lf_group.setLayout(lf_layout)

        # Gyro Z Source
        self.gz_group = QGroupBox("Gyro Z Source Setting")
        gz_layout = QHBoxLayout()
        self.cb_gz_mems, self.cb_gz_fog = QtWidgets.QCheckBox("MEMS"), QtWidgets.QCheckBox("FOG")
        self.gz_btn_group = QtWidgets.QButtonGroup(self)
        self.gz_btn_group.addButton(self.cb_gz_mems, 0)
        self.gz_btn_group.addButton(self.cb_gz_fog, 1)
        gz_layout.addWidget(self.cb_gz_mems);
        gz_layout.addWidget(self.cb_gz_fog)
        self.gz_group.setLayout(gz_layout)

        # LPF
        self.lpf_group = QGroupBox("MEMS IMU LPF Setting")
        lpf_layout = QGridLayout()
        self.lpf_g_idx = spinBlock(title="Gyro LPF Index", minValue=0, maxValue=7, double=False, step=1)
        self.lpf_a_idx = spinBlock(title="Accl LPF2 Index", minValue=0, maxValue=7, double=False, step=1)
        self.lpf_g_val_label = QLabel(f"BW: {LPF_G_TABLE[0]}")
        self.lpf_a_val_label = QLabel(f"BW: {LPF_A_TABLE[0]}")
        lpf_layout.addWidget(self.lpf_g_idx, 0, 0);
        lpf_layout.addWidget(self.lpf_g_val_label, 0, 1)
        lpf_layout.addWidget(self.lpf_a_idx, 1, 0);
        lpf_layout.addWidget(self.lpf_a_val_label, 1, 1)
        self.lpf_group.setLayout(lpf_layout)

        # File I/O
        self.file_group = QGroupBox("Configuration File Management")
        file_layout = QHBoxLayout()
        self.export_btn, self.import_btn = QPushButton("Export (.txt)"), QPushButton("Import (.txt)")
        file_layout.addWidget(self.export_btn);
        file_layout.addWidget(self.import_btn)
        self.file_group.setLayout(file_layout)

        self.dump_btn = QPushButton("Dump Configuration")

        # Main Layout
        layout = QVBoxLayout()
        for w in [self.dr_idx, self.dr_hint, self.br_idx, self.br_hint, self.gz_group,
                  self.lpf_group, self.lf_group, self.rcs_group, self.set_rcs_btn,
                  self.dump_btn, self.file_group]:
            layout.addWidget(w)
        self.setLayout(layout)

    def _connect_signals(self):
        self.dr_idx.spin.valueChanged.connect(self._on_dr_changed)
        self.br_idx.spin.valueChanged.connect(self._on_br_changed)
        self.set_rcs_btn.clicked.connect(self.set_rcs_matrix)
        self.dump_btn.clicked.connect(self.dump_configuration)
        self.lf_btn_group.idClicked.connect(self._on_lf_changed)
        self.lpf_g_idx.spin.valueChanged.connect(self._on_lpf_g_changed)
        self.lpf_a_idx.spin.valueChanged.connect(self._on_lpf_a_changed)
        self.gz_btn_group.idClicked.connect(self._on_gz_changed)
        self.export_btn.clicked.connect(self.export_to_txt)
        self.import_btn.clicked.connect(self.import_from_txt)

    # --- 工具函數 ---
    def _float_to_int_bits(self, val: float) -> int:
        return struct.unpack('<I', struct.pack('<f', float(val)))[0]

    def _int_bits_to_float(self, val_int: int) -> float:
        try:
            # 關鍵修正：加上 & 0xFFFFFFFF 確保負數 bit 能正確解析為 float
            return struct.unpack('<f', struct.pack('<I', int(val_int) & 0xFFFFFFFF))[0]
        except Exception:
            return 0.0

    def _ensure_act(self) -> bool:
        if self.__act is None:
            QMessageBox.information(self, "Info", "act 尚未設定")
            return False
        return True

    # --- 核心邏輯 (Table-Driven) ---
    def dump_configuration(self):
        if not self._ensure_act(): return
        self.__act.flushInputBuffer("None")
        cfg = self.__act.dump_configuration()

        if isinstance(cfg, dict):
            self._updating_ui = True
            try:
                for cid, info in self.config_table.items():
                    raw_val = cfg.get(cid)
                    if raw_val is None: continue

                    # 根據 Table 定義進行型別轉換
                    val = self._int_bits_to_float(raw_val) if info["type"] == "float" else int(raw_val)

                    # 更新 UI
                    widget = info["widget"]
                    if isinstance(widget, QtWidgets.QAbstractSpinBox):
                        widget.setValue(val)
                    elif isinstance(widget, QtWidgets.QButtonGroup):
                        btn = widget.button(val)
                        if btn: btn.setChecked(True)

                # 更新 LPF 標籤與發送信號
                self.lpf_g_val_label.setText(f"BW: {LPF_G_TABLE[self.lpf_g_idx.spin.value()]}")
                self.lpf_a_val_label.setText(f"BW: {LPF_A_TABLE[self.lpf_a_idx.spin.value()]}")
                rcs_vals = [self._int_bits_to_float(cfg.get(str(i), 0)) for i in range(2, 11)]
                self.rcs_updated_qt.emit(rcs_vals)

            finally:
                self._updating_ui = False
        else:
            logging.error("Configuration dump failed.")

    def export_to_txt(self):
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path, _ = QFileDialog.getSaveFileName(self, "Export Config", f"{now}_config.txt", "Text Files (*.txt)")
        if not path: return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# PIG Configuration Export - {now}\n\n")
                # 依 ID 排序輸出
                for cid in sorted(self.config_table.keys(), key=int):
                    info = self.config_table[cid]
                    widget = info["widget"]
                    val = widget.value() if isinstance(widget, QtWidgets.QAbstractSpinBox) else widget.checkedId()
                    f.write(f"{cid}={val:<12} # {info['comment']}\n")
            QMessageBox.information(self, "Success", "Export completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def import_from_txt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Config", "", "Text Files (*.txt)")
        if not path: return

        try:
            file_data = {}
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    clean = line.split('#')[0].strip()
                    if "=" in clean:
                        k, v = clean.split('=')
                        file_data[k.strip()] = v.strip()

            self._updating_ui = False  # 確保執行 setValue 會觸發發送指令
            for cid, info in self.config_table.items():
                if cid not in file_data: continue

                val = float(file_data[cid]) if info["type"] == "float" else int(file_data[cid])
                widget = info["widget"]

                if isinstance(widget, QtWidgets.QAbstractSpinBox):
                    widget.setValue(val)
                elif isinstance(widget, QtWidgets.QButtonGroup):
                    btn = widget.button(int(val))
                    if btn: btn.click()  # click() 會觸發 idClicked 並發送指令

            # RCS Matrix 通常分多次傳送，詢問是否同步
            if QMessageBox.question(self, "Sync", "Import UI done. Send RCS Matrix to hardware?") == QMessageBox.Yes:
                self.set_rcs_matrix()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import failed: {e}")

    # --- 原有發送指令 Handler ---
    def _on_gz_changed(self, val):
        if not self._updating_ui and self._ensure_act():
            self.__act.writeImuCmd(CMD_CFG_WZ_SRC, val, 6)

    def _on_lpf_g_changed(self, val):
        self.lpf_g_val_label.setText(f"BW: {LPF_G_TABLE[val]}")
        if not self._updating_ui and self._ensure_act():
            self.__act.writeImuCmd(CMD_CFG_LPF_G, val, 6)

    def _on_lpf_a_changed(self, val):
        self.lpf_a_val_label.setText(f"BW: {LPF_A_TABLE[val]}")
        if not self._updating_ui and self._ensure_act():
            self.__act.writeImuCmd(CMD_CFG_LPF_A, val, 6)

    def set_rcs_matrix(self):
        if not self._ensure_act(): return
        for r in range(3):
            for c in range(3):
                val_int = self._float_to_int_bits(self.rcs_elements[r][c].spin.value())
                self.__act.writeImuCmd(CMD_CFG_RSC_MAP[r][c], val_int, 6)
                time.sleep(0.05)
        QMessageBox.information(self, "Success", "RCS Matrix sent.")

    def _on_dr_changed(self, idx):
        if not self._updating_ui and self._ensure_act():
            self.__act.writeImuCmd(CMD_CFG_DR, int(idx), 6)

    def _on_br_changed(self, idx):
        if not self._updating_ui and self._ensure_act():
            self.__act.writeImuCmd(CMD_CFG_BR, int(idx), 6)

    def _on_lf_changed(self, val):
        if not self._updating_ui and self._ensure_act():
            self.__act.writeImuCmd(CMD_CFG_LF, val, 6)

    def show(self):
        super().show()
        self.raise_();
        self.activateWindow()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication


    class Dummy:
        def dump_configuration(self): return {"3": -1082130432}  # 測試 -1.0

        def flushInputBuffer(self, x): pass

        def writeImuCmd(self, *args): print(f"CMD: {args}")


    app = QApplication(sys.argv)
    window = pig_configuration_widget(Dummy())
    window.show()
    sys.exit(app.exec())