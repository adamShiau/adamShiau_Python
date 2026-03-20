# -*- coding:UTF-8 -*-
import logging
import struct
import time
import datetime
import math
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
CMD_CFG_LPF_FOG = 0x57

DR_TABLE = [10, 50, 100, 200, 400]  # 對應 dr_idx 0~4
ALPHA_F_TABLE = [1.000, 0.611, 0.386, 0.239, 0.136, 0.030]  # 定義在 MCU 的 alpha 係數
LPF_G_TABLE = ["133 Hz", "128 Hz", "112 Hz", "134 Hz", "86 Hz", "48 Hz", "24.6 Hz", "12.6 Hz"]
LPF_A_TABLE = ["104 Hz", "41.6 Hz", "20.8 Hz", "9.24 Hz", "4.2 Hz", "2.1 Hz", "1 Hz", "0.5 Hz"]


class pig_configuration_widget(QWidget):
    rcs_updated_qt = Signal(list)

    def __init__(self, act=None, parent=None):
        super().__init__(parent)
        self.__act = act
        self._updating_ui = False

        self.setWindowTitle("Configuration")
        self.resize(450, 850)

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
            "15": {"type": "int", "widget": self.lpf_f_idx.spin, "comment": "FOG LPF Index"},
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
        self.br_idx = spinBlock(title="Baud rate Index", minValue=0, maxValue=4, double=False, step=1)
        self.dr_idx = spinBlock(title="Data rate Index", minValue=0, maxValue=4, double=False, step=1)
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
        self.lpf_group = QGroupBox("IMU LPF Setting")
        lpf_layout = QGridLayout()
        self.lpf_g_idx = spinBlock(title="Gyro LPF1 Index", minValue=0, maxValue=7, double=False, step=1)
        self.lpf_a_idx = spinBlock(title="Accl LPF2 Index", minValue=0, maxValue=7, double=False, step=1)
        self.lpf_f_idx = spinBlock(title="FOG LPF Index", minValue=0, maxValue=5, double=False, step=1)
        self.lpf_g_val_label = QLabel(f"BW: {LPF_G_TABLE[0]}")
        self.lpf_a_val_label = QLabel(f"BW: {LPF_A_TABLE[0]}")
        self.lpf_f_val_label = QLabel("BW: Bypass") # 初始值

        lpf_layout.addWidget(self.lpf_g_idx, 0, 0);
        lpf_layout.addWidget(self.lpf_g_val_label, 0, 1)
        lpf_layout.addWidget(self.lpf_a_idx, 1, 0);
        lpf_layout.addWidget(self.lpf_a_val_label, 1, 1)
        lpf_layout.addWidget(self.lpf_f_idx, 2, 0)
        lpf_layout.addWidget(self.lpf_f_val_label, 2, 1)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        lpf_layout.addWidget(line, 3, 0, 1, 2)

        # 精簡顯示最終頻寬的標籤
        self.final_bw_label = QLabel("Final BW >> G: -- | A: -- | F: --")
        self.final_bw_label.setStyleSheet("color: #0055ff; font-weight: bold;")  # 使用藍色加粗區別
        lpf_layout.addWidget(self.final_bw_label, 4, 0, 1, 2)

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
        self.dr_idx.spin.valueChanged.connect(self._update_fog_lpf_label)
        self.br_idx.spin.valueChanged.connect(self._on_br_changed)
        self.set_rcs_btn.clicked.connect(self.set_rcs_matrix)
        self.dump_btn.clicked.connect(self.dump_configuration)
        self.lf_btn_group.idClicked.connect(self._on_lf_changed)
        self.lpf_g_idx.spin.valueChanged.connect(self._on_lpf_g_changed)
        self.lpf_a_idx.spin.valueChanged.connect(self._on_lpf_a_changed)
        self.lpf_f_idx.spin.valueChanged.connect(self._on_lpf_f_changed)
        self.gz_btn_group.idClicked.connect(self._on_gz_changed)
        self.export_btn.clicked.connect(self.export_to_txt)
        self.import_btn.clicked.connect(self.import_from_txt)
        self.dr_idx.spin.valueChanged.connect(self._update_all_bw_display)
        self.lpf_g_idx.spin.valueChanged.connect(self._update_all_bw_display)
        self.lpf_a_idx.spin.valueChanged.connect(self._update_all_bw_display)
        self.lpf_f_idx.spin.valueChanged.connect(self._update_all_bw_display)


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
                self._update_fog_lpf_label() # 更新 FOG LPF Label
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

    def _on_lpf_f_changed(self, val):
        self._update_fog_lpf_label()  # 調用動態計算
        if not self._updating_ui and self._ensure_act():
            self.__act.writeImuCmd(CMD_CFG_LPF_FOG, val, 6)

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

    def _update_fog_lpf_label(self):
        """根據公式計算並更新 FOG LPF 的頻寬顯示"""
        try:
            fs = DR_TABLE[self.dr_idx.spin.value()]
            alpha = ALPHA_F_TABLE[self.lpf_f_idx.spin.value()]

            if alpha >= 1.0:
                # 計算 Sinc 濾波的 3dB 頻寬
                f_cf = 0.443 * fs
                bw_text = f"{f_cf:.2f} Hz (bypass)"
            else:
                # 公式: f_cf = (alpha * fs) / (2 * pi * (1 - alpha))
                f_cf = (alpha * fs) / (2 * math.pi * (1 - alpha))
                bw_text = f"{f_cf:.2f} Hz"

            self.lpf_f_val_label.setText(f"BW: {bw_text}")
        except Exception as e:
            logging.error(f"Calculate FOG BW error: {e}")

    def _update_all_bw_display(self):
        """計算並更新最下方的精簡頻寬資訊"""
        try:
            # 1. 取得 Data Rate
            fs = DR_TABLE[self.dr_idx.spin.value()]

            # 2. 取得 MEMS 數值 (直接從 Table 拿字串並去掉 " Hz")
            bw_g = LPF_G_TABLE[self.lpf_g_idx.spin.value()].replace(" Hz", "")
            bw_a = LPF_A_TABLE[self.lpf_a_idx.spin.value()].replace(" Hz", "")

            # 3. 計算 FOG 合成頻寬
            f1 = 0.443 * fs  # Stage 1: FPGA Mean (Sinc)
            alpha = ALPHA_F_TABLE[self.lpf_f_idx.spin.value()]

            if alpha >= 1.0:
                f_fog_final = f1
            else:
                f2 = (alpha * fs) / (2 * math.pi * (1 - alpha))  # Stage 2: IIR
                # 級聯頻寬公式: 1 / sqrt( (1/f1)^2 + (1/f2)^2 )
                f_fog_final = 1 / math.sqrt((1 / f1 ** 2) + (1 / f2 ** 2))

            # 4. 更新 UI 顯示 (精簡格式)
            info = f"Final BW >> G: {bw_g}Hz | A: {bw_a}Hz | F: {f_fog_final:.1f}Hz"
            self.final_bw_label.setText(info)

            # 同步更新原本的 FOG Label (如果你還留著的話)
            self._update_fog_lpf_label()

        except Exception as e:
            print(f"Update BW Error: {e}")

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
