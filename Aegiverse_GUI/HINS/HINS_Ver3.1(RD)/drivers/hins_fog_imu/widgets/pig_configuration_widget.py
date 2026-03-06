# -*- coding:UTF-8 -*-
import logging
import struct
import time
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox
from myLib.myGui.mygui_serial import *
from myLib.myGui.myLabel import *  # 定義指令常數

CMD_CFG_DR = 0x48
CMD_CFG_BR = 0x49
CMD_CFG_RSC_MAP = [
    [0x4A, 0x4B, 0x4C],
    [0x4D, 0x4E, 0x4F],
    [0x50, 0x51, 0x52]
]
CMD_CFG_LF = 0x53
CMD_CFG_LPF_G = 0x54  # Gyro LPF
CMD_CFG_LPF_A = 0x55  # Accl LPF
CMD_CFG_WZ_SRC = 0x56  # Accl LPF

# LPF 頻寬對應表
LPF_G_TABLE = ["133 Hz", "128 Hz", "112 Hz", "134 Hz", "86 Hz", "48 Hz", "24.6 Hz", "12.6 Hz"]
LPF_A_TABLE = ["104 Hz", "41.6 Hz", "20.8 Hz", "9.24 Hz", "4.2 Hz", "2.1 Hz", "1 Hz", "0.5 Hz"]


class pig_configuration_widget(QWidget):
    rcs_updated_qt = Signal(list)

    def __init__(self, act=None, parent=None):
        super().__init__(parent)
        self.__act = act
        self._updating_ui = False

        self.setWindowTitle("Configuration")
        self.resize(450, 750)  # 稍微調高視窗高度

        # --- UI ---
        # --- DR/BR ---
        self.br_idx = spinBlock(title="Baudrate Index", minValue=0, maxValue=4, double=False, step=1)
        self.dr_idx = spinBlock(title="Datarate Index", minValue=0, maxValue=4, double=False, step=1)
        self.br_hint = QLabel("Index->BR: 0=9600, 1=115200, 2=230400, 3=460800, 4=921600")
        self.dr_hint = QLabel("Index->DR: 0=10, 1=50, 2=100, 3=200, 4=400 Hz")

        # --- RCS 3x3 矩陣 ---
        self.rcs_group = QGroupBox("Sensor to Case (RCS) Matrix")
        rcs_layout = QGridLayout()
        self.rcs_elements = []

        for r in range(3):
            row_elements = []
            for c in range(3):
                sb = spinBlock(title=f"R{r + 1}{c + 1}", minValue=-10, maxValue=10, double=True, step=0.01)
                rcs_layout.addWidget(sb, r, c)
                row_elements.append(sb)
            self.rcs_elements.append(row_elements)
        self.rcs_group.setLayout(rcs_layout)
        self.set_rcs_btn = QPushButton("Set RCS Matrix")

        # --- Local Frame ---
        self.lf_group = QGroupBox("Local Frame Setting")
        lf_layout = QHBoxLayout()
        self.cb_enu = QtWidgets.QCheckBox("ENU")
        self.cb_ned = QtWidgets.QCheckBox("NED")
        self.lf_btn_group = QtWidgets.QButtonGroup(self)
        self.lf_btn_group.addButton(self.cb_enu, 0)
        self.lf_btn_group.addButton(self.cb_ned, 1)
        self.lf_btn_group.setExclusive(True)
        lf_layout.addWidget(self.cb_enu)
        lf_layout.addWidget(self.cb_ned)
        self.lf_group.setLayout(lf_layout)

        # --- Gyro Z Source Setting ---
        self.gz_group = QGroupBox("Gyro Z Source Setting")
        gz_layout = QHBoxLayout()
        self.cb_gz_mems = QtWidgets.QCheckBox("MEMS")
        self.cb_gz_fog = QtWidgets.QCheckBox("FOG")
        self.gz_btn_group = QtWidgets.QButtonGroup(self)
        self.gz_btn_group.addButton(self.cb_gz_mems, 0)
        self.gz_btn_group.addButton(self.cb_gz_fog, 1)
        self.gz_btn_group.setExclusive(True)
        gz_layout.addWidget(self.cb_gz_mems)
        gz_layout.addWidget(self.cb_gz_fog)
        self.gz_group.setLayout(gz_layout)

        # --- MEMS IMU LPF ---
        self.lpf_group = QGroupBox("MEMS IMU LPF Setting")
        lpf_layout = QGridLayout()
        self.lpf_g_idx = spinBlock(title="Gyro LPF Index", minValue=0, maxValue=7, double=False, step=1)
        self.lpf_a_idx = spinBlock(title="Accl LPF2 Index", minValue=0, maxValue=7, double=False, step=1)
        self.lpf_g_val_label = QLabel(f"BW: {LPF_G_TABLE[0]}")
        self.lpf_a_val_label = QLabel(f"BW: {LPF_A_TABLE[0]}")

        lpf_layout.addWidget(self.lpf_g_idx, 0, 0)
        lpf_layout.addWidget(self.lpf_g_val_label, 0, 1)
        lpf_layout.addWidget(self.lpf_a_idx, 1, 0)
        lpf_layout.addWidget(self.lpf_a_val_label, 1, 1)
        self.lpf_group.setLayout(lpf_layout)

        # --- dump 按鈕 ---
        self.dump_btn = QPushButton("Dump Configuration")

        # --- Layout 配置 ---
        layout = QVBoxLayout()
        layout.addWidget(self.dr_idx)
        layout.addWidget(self.dr_hint)
        layout.addWidget(self.br_idx)
        layout.addWidget(self.br_hint)
        layout.addWidget(self.gz_group)
        layout.addWidget(self.lpf_group)
        layout.addWidget(self.lf_group)
        layout.addWidget(self.rcs_group)
        layout.addWidget(self.set_rcs_btn)
        layout.addWidget(self.dump_btn)
        self.setLayout(layout)

        # --- Signal ---
        self.dr_idx.spin.valueChanged.connect(self._on_dr_changed)
        self.br_idx.spin.valueChanged.connect(self._on_br_changed)
        self.set_rcs_btn.clicked.connect(self.set_rcs_matrix)
        self.dump_btn.clicked.connect(self.dump_configuration)
        self.lf_btn_group.idClicked.connect(self._on_lf_changed)
        self.lpf_g_idx.spin.valueChanged.connect(self._on_lpf_g_changed)
        self.lpf_a_idx.spin.valueChanged.connect(self._on_lpf_a_changed)
        self.gz_btn_group.idClicked.connect(self._on_gz_changed)

    # --- 內部工具函數 ---
    def _float_to_int_bits(self, val: float) -> int:
        return struct.unpack('<I', struct.pack('<f', float(val)))[0]

    def _int_bits_to_float(self, val_int: int) -> float:
        try:
            return struct.unpack('<f', struct.pack('<i', int(val_int)))[0]
        except Exception:
            return 0.0

    def _ensure_act(self) -> bool:
        if self.__act is None:
            QtWidgets.QMessageBox.information(self, "Info", "act 尚未設定")
            return False
        return True

    # --- Event Handlers ---
    def _on_gz_changed(self, val: int):
        if getattr(self, '_updating_ui', False):
            return
        if not self._ensure_act():
            return
        print(f"Sending Gyro Z Source CMD: {hex(CMD_CFG_WZ_SRC).upper()}, Val={val}")
        self.__act.writeImuCmd(CMD_CFG_WZ_SRC, val, 6)

    def _on_lpf_g_changed(self, val: int):
        if 0 <= val < len(LPF_G_TABLE):
            self.lpf_g_val_label.setText(f"BW: {LPF_G_TABLE[val]}")

        if getattr(self, '_updating_ui', False):
            return
        if not self._ensure_act():
            return
        print(f"Sending Gyro LPF CMD: {hex(CMD_CFG_LPF_G).upper()}, Val={val}")
        self.__act.writeImuCmd(CMD_CFG_LPF_G, val, 6)

    def _on_lpf_a_changed(self, val: int):
        if 0 <= val < len(LPF_A_TABLE):
            self.lpf_a_val_label.setText(f"BW: {LPF_A_TABLE[val]}")

        if getattr(self, '_updating_ui', False):
            return
        if not self._ensure_act():
            return
        print(f"Sending Accl LPF CMD: {hex(CMD_CFG_LPF_A).upper()}, Val={val}")
        self.__act.writeImuCmd(CMD_CFG_LPF_A, val, 6)

    def set_rcs_matrix(self):
        if getattr(self, '_updating_ui', False):
            return
        if not self._ensure_act():
            return
        for r in range(3):
            for c in range(3):
                val_float = self.rcs_elements[r][c].spin.value()
                val_int = self._float_to_int_bits(val_float)
                cmd = CMD_CFG_RSC_MAP[r][c]
                self.__act.writeImuCmd(cmd, val_int, 6)
                time.sleep(0.05)
        QtWidgets.QMessageBox.information(self, "Success", "RCS Matrix sent.")

    def _on_dr_changed(self, idx: int):
        if getattr(self, '_updating_ui', False):
            return
        if not self._ensure_act():
            return
        print(f"Sending data rate: {hex(CMD_CFG_DR).upper()}, Val={idx}")
        self.__act.writeImuCmd(CMD_CFG_DR, int(idx), 6)

    def _on_br_changed(self, idx: int):
        if getattr(self, '_updating_ui', False):
            return
        if not self._ensure_act():
            return
        print(f"Sending baud rate: {hex(CMD_CFG_BR).upper()}, Val={idx}")
        self.__act.writeImuCmd(CMD_CFG_BR, int(idx), 6)

    def _on_lf_changed(self, val: int):
        if getattr(self, '_updating_ui', False):
            return
        if not self._ensure_act():
            return
        self.__act.writeImuCmd(CMD_CFG_LF, val, 6)

    # 修改 dump_configuration 函式後半段
    def dump_configuration(self):
        if not self._ensure_act():
            return
        self.__act.flushInputBuffer("None")
        cfg = self.__act.dump_configuration()

        print(f"DEBUG - Raw cfg from act: {cfg} (Type: {type(cfg)})")

        # --- 關鍵修改：只有當 cfg 是字典時才執行解析 ---
        if isinstance(cfg, dict):
            self._updating_ui = True
            try:
                # 建議使用 get 的安全寫法，避免 Key 不存在時出錯
                def get_int(k, default=0):
                    v = cfg.get(str(k))
                    return int(v) if v is not None else default

                # 1. DR/BR
                self.dr_idx.spin.setValue(get_int(0))
                self.br_idx.spin.setValue(get_int(1))

                # 2. RCS Matrix (2~10)
                rcs_values = []
                for i in range(2, 11):
                    val_int = cfg.get(str(i))
                    if val_int is not None:
                        f_val = self._int_bits_to_float(int(val_int))
                        rcs_values.append(f_val)
                        r, c = (i - 2) // 3, (i - 2) % 3
                        self.rcs_elements[r][c].spin.setValue(f_val)
                self.rcs_updated_qt.emit(rcs_values)

                # 3. Local Frame (11)
                lf_val = cfg.get("11")
                if lf_val is not None:
                    if int(lf_val) == 0:
                        self.cb_enu.setChecked(True)
                    elif int(lf_val) == 1:
                        self.cb_ned.setChecked(True)

                # 4. LPF (12, 13)
                self.lpf_g_idx.spin.setValue(get_int(12))
                self.lpf_a_idx.spin.setValue(get_int(13))

                # 5. Gyro Z Source (14)
                gz_val = cfg.get("14")
                if gz_val is not None:
                    print(f"DEBUG - Setting Gyro Z Source to: {gz_val}")
                    if int(gz_val) == 0:
                        self.cb_gz_mems.setChecked(True)
                    elif int(gz_val) == 1:
                        self.cb_gz_fog.setChecked(True)

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"UI Update Error: {e}")
            finally:
                self._updating_ui = False
        else:
            # 如果是 "無法取得值"，只印出 log 或警告，不執行更新 UI 邏輯
            logger.error("Configuration dump failed: Hardware did not respond.")

    # def dump_configuration(self):
    #     if not self._ensure_act(): return
    #     self.__act.flushInputBuffer("None")
    #     cfg = self.__act.dump_configuration()
    #     # Debug 1: 印出原始回傳資料
    #     print(f"DEBUG - Raw cfg from act: {cfg} (Type: {type(cfg)})")
    #
    #     if isinstance(cfg, dict):
    #         self._updating_ui = True
    #         try:
    #             # Debug 2: 檢查特定的 Key 是否存在
    #             for key in ["0", "1", "11", "12", "13", "14"]:
    #                 print(f"DEBUG - Key {key} value: {cfg.get(key)}")
    #
    #             # 1. DR/BR
    #             self.dr_idx.spin.setValue(int(cfg.get("0", 0)))
    #             self.br_idx.spin.setValue(int(cfg.get("1", 0)))
    #
    #             # 2. RCS Matrix (Key 2 ~ 10)
    #             rcs_values = []
    #             for i in range(2, 11):
    #                 val_int = cfg.get(str(i))
    #                 if val_int is not None:
    #                     f_val = self._int_bits_to_float(int(val_int))
    #                     rcs_values.append(f_val)
    #                     r, c = (i - 2) // 3, (i - 2) % 3
    #                     self.rcs_elements[r][c].spin.setValue(f_val)
    #             self.rcs_updated_qt.emit(rcs_values)
    #
    #             # 3. Local Frame (Key 11)
    #             lf_val = cfg.get("11")
    #             if lf_val is not None:
    #                 lf_val = int(lf_val)
    #                 if lf_val == 0:
    #                     self.cb_enu.setChecked(True)
    #                 elif lf_val == 1:
    #                     self.cb_ned.setChecked(True)
    #
    #             # 4. LPF Gyro (Key 12) & Accl (Key 13)
    #             lpf_g_val = cfg.get("12")
    #             if lpf_g_val is not None:
    #                 self.lpf_g_idx.spin.setValue(int(lpf_g_val))
    #
    #             lpf_a_val = cfg.get("13")
    #             if lpf_a_val is not None:
    #                 self.lpf_a_idx.spin.setValue(int(lpf_a_val))
    #
    #             # 5. Gyro Z Source (Key 14)
    #             gz_val = cfg.get("14")
    #             if gz_val is not None:
    #                 gz_val = int(gz_val)
    #                 if gz_val == 0:
    #                     self.cb_gz_mems.setChecked(True)
    #                 elif gz_val == 1:
    #                     self.cb_gz_fog.setChecked(True)
    #
    #             # Debug 3: 檢查 Gyro Z Source (Key 14)
    #             gz_val = cfg.get("14")
    #             if gz_val is not None:
    #                 print(f"DEBUG - Setting Gyro Z Source to: {gz_val}")
    #                 if int(gz_val) == 0:
    #                     self.cb_gz_mems.setChecked(True)
    #                 elif int(gz_val) == 1:
    #                     self.cb_gz_fog.setChecked(True)
    #
    #         except Exception as e:
    #             # Debug 4: 捕捉報錯行數與原因
    #             import traceback
    #             print("--- UI Update Error Traceback ---")
    #             traceback.print_exc()
    #             print(f"Error detail: {e}")
    #         finally:
    #             self._updating_ui = False
    #     elif cfg == "無法取得值":
    #         QtWidgets.QMessageBox.warning(self, "Dump Error", "無法取得設定值")

    def show(self):
        super().show()
        self.raise_()
        self.activateWindow()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication


    class DummyReader:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"[Preview] {name} called with {args}")
                return {"0": 0, "1": 1, "12": 3, "13": 5}  # 模擬一些回傳值

            return method


    app = QApplication(sys.argv)
    window = pig_configuration_widget(DummyReader())
    window.show()
    sys.exit(app.exec())
