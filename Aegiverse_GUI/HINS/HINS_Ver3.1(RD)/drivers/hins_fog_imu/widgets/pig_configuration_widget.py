# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import logging
import struct
import time
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout, QGroupBox
from myLib.myGui.mygui_serial import *
from myLib.myGui.myLabel import *  # spinBlock

# import sys
# sys.path.append("../../")
# print(__name__)
# print(sys.path)

# 定義指令常數
CMD_CFG_DR = 0x48
CMD_CFG_BR = 0x49
CMD_CFG_RSC_MAP = [
    [0x4A, 0x4B, 0x4C], # Row 1: 11, 12, 13
    [0x4D, 0x4E, 0x4F], # Row 2: 21, 22, 23
    [0x50, 0x51, 0x52]  # Row 3: 31, 32, 33
]
CMD_CFG_LF = 0x53

# BR_TABLE = [9600, 115200, 230400, 460800, 921600]
# DR_TABLE = [10, 50, 100, 200, 400]


class pig_configuration_widget(QWidget):
    rcs_updated_qt = Signal(list)

    def __init__(self, act=None, parent=None):
        super().__init__(parent)
        self.__act = act
        self._updating_ui = False  # 防止 dump 回填時又觸發 valueChanged

        self.setWindowTitle("Configuration")
        self.resize(450, 500)

        # --- UI ---
        # --- DR/BR ---
        self.br_idx = spinBlock(title="Baudrate Index", minValue=0, maxValue=4, double=False, step=1)
        self.dr_idx = spinBlock(title="Datarate Index", minValue=0, maxValue=4, double=False, step=1)
        self.br_hint = QLabel("Index->BR: 0=9600, 1=115200, 2=230400, 3=460800, 4=921600")
        self.dr_hint = QLabel("Index->DR: 0=10, 1=50, 2=100, 3=200, 4=400 Hz")

        # --- RCS 3x3 矩陣  ---
        # self.rcs_group = QtWidgets.QGroupBox("Sensor to Case (RCS) Matrix")
        self.rcs_group = QGroupBox("Sensor to Case (RCS) Matrix")
        rcs_layout = QGridLayout()
        self.rcs_elements = []  # 儲存 spinBlock 實例以供後續存取

        for r in range(3):
            row_elements = []
            for c in range(3):
                # 建立浮點數輸入框，範圍通常是 -1.0 到 1.0 或更大
                sb = spinBlock(title=f"R{r + 1}{c + 1}", minValue=-10, maxValue=10, double=True, step=0.01)
                rcs_layout.addWidget(sb, r, c)
                row_elements.append(sb)
            self.rcs_elements.append(row_elements)
        self.rcs_group.setLayout(rcs_layout)

        self.set_rcs_btn = QPushButton("Set RCS Matrix")

        # --- dump 按鈕  ---
        self.dump_btn = QPushButton("Dump Configuration")

        # --- 新增 UI: Local Frame 區塊 ---
        self.lf_group = QGroupBox("Local Frame Setting")
        lf_layout = QHBoxLayout()  # 使用水平佈局
        self.cb_enu = QtWidgets.QCheckBox("ENU (0)")
        self.cb_ned = QtWidgets.QCheckBox("NED (1)")

        # 使用 ButtonGroup 確保互斥 (二選一)
        self.lf_btn_group = QtWidgets.QButtonGroup(self)
        self.lf_btn_group.addButton(self.cb_enu, 0)  # ID 為 0
        self.lf_btn_group.addButton(self.cb_ned, 1)  # ID 為 1
        self.lf_btn_group.setExclusive(True)  # 開啟互斥

        lf_layout.addWidget(self.cb_enu)
        lf_layout.addWidget(self.cb_ned)
        self.lf_group.setLayout(lf_layout)

        # --- Layout 配置 ---
        layout = QVBoxLayout()  # 使用垂直佈局包裝
        layout.addWidget(self.dr_idx)
        layout.addWidget(self.dr_hint)
        layout.addWidget(self.br_idx)
        layout.addWidget(self.br_hint)
        layout.addWidget(self.rcs_group)
        layout.addWidget(self.set_rcs_btn)
        layout.addWidget(self.lf_group)
        layout.addWidget(self.dump_btn)
        self.setLayout(layout)

        # --- Signal ---
        self.dr_idx.spin.valueChanged.connect(self._on_dr_changed)
        self.br_idx.spin.valueChanged.connect(self._on_br_changed)
        self.set_rcs_btn.clicked.connect(self.set_rcs_matrix)
        self.dump_btn.clicked.connect(self.dump_configuration)
        self.lf_btn_group.idClicked.connect(self._on_lf_changed)

    # --- 內部工具函數  ---
    def _float_to_int_bits(self, val: float) -> int:
        """將 float 轉為 IEEE 754 uint32 整數"""
        return struct.unpack('<I', struct.pack('<f', float(val)))[0]

    def _int_bits_to_float(self, val_int: int) -> float:
        """將從 MCU dump 回來的整數（包含負數形式）轉回 float"""
        try:
            # 修改點：使用 'i' (小寫) 來處理帶符號整數 (signed int)
            # 這樣就能正確處理如 -1082130432 這樣的負值輸入
            return struct.unpack('<f', struct.pack('<i', int(val_int)))[0]
        except Exception as e:
            # 增加 logging 方便追蹤錯誤
            # logger.error(f"Conversion error with value {val_int}: {e}")
            return 0.0

    def _ensure_act(self) -> bool:
        """檢查 act 是否存在"""
        if self.__act is None:
            QtWidgets.QMessageBox.information(self, "Info", "act 尚未設定")
            return False
        return True

    def set_rcs_matrix(self):
        """按下 Set 按鈕後送出 9 個元素的指令"""
        if not self._ensure_act():
            return

        for r in range(3):
            for c in range(3):
                val_float = self.rcs_elements[r][c].spin.value()
                val_int = self._float_to_int_bits(val_float)
                cmd = CMD_CFG_RSC_MAP[r][c]

                # 印出調試資訊：cmd 轉為 HEX (例如 0x4A)，val_float 顯示原始數值
                print(
                    f"Sending RCS Matrix: CMD={hex(cmd).upper()}, Val(float)={val_float:.4f}, Val(int_bits)={val_int}")

                # 調用 act 的 writeImuCmd
                # 這裡 val_int 是經過 IEEE 754 轉換後的 32-bit 整數
                self.__act.writeImuCmd(cmd, val_int, 6)

                time.sleep(0.05)  # 短暫延遲確保發送穩定

        QtWidgets.QMessageBox.information(self, "Success", "RCS Matrix sent to device.")

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
        """從設備讀取配置並回填 UI"""
        if not self._ensure_act():
            return

        self.__act.flushInputBuffer("None")  #
        cfg = self.__act.dump_configuration()  #
        print(cfg)

        if isinstance(cfg, dict):
            self._updating_ui = True # 開啟旗標避免回填時觸發 _on_lf_changed
            try:
                # 1. 回填 DR/BR
                self.dr_idx.spin.setValue(int(cfg.get("0", 0)))
                self.br_idx.spin.setValue(int(cfg.get("1", 0)))

                # 2. 回填 RCS 矩陣 (Key 2 ~ 10)
                key_idx = 2
                rcs_values = []
                for r in range(3):
                    for c in range(3):
                        val_int = cfg.get(str(key_idx))
                        if val_int is not None:
                            # 轉換回浮點數後填入 UI
                            f_val = self._int_bits_to_float(int(val_int))
                            rcs_values.append(f_val)
                            self.rcs_elements[r][c].spin.setValue(f_val)
                        key_idx += 1
                self.rcs_updated_qt.emit(rcs_values)

                # 3. 回填 Local Frame (Key: 11)
                lf_val = cfg.get("11")
                if lf_val is not None:
                    lf_val = int(lf_val)
                    if lf_val == 0:
                        self.cb_enu.setChecked(True)
                    elif lf_val == 1:
                        self.cb_ned.setChecked(True)
                    else:
                        # 若數值非 0 或 1，取消所有勾選
                        self.lf_btn_group.setExclusive(False)
                        self.cb_enu.setChecked(False)
                        self.cb_ned.setChecked(False)
                        self.lf_btn_group.setExclusive(True)

            except Exception as e:
                logger.error(f"UI Update Error: {e}")
            finally:
                self._updating_ui = False
        elif cfg == "無法取得值":  #
            QtWidgets.QMessageBox.warning(self, "Dump Error", "無法取得設定值")

    def _on_lf_changed(self, val: int):
        """當 CheckBox 被勾選時，立即送出指令"""
        if self._updating_ui:
            return

        if self._ensure_act():
            print(f"Sending Local Frame CMD: {hex(CMD_CFG_LF).upper()}, Val={val}")
            self.__act.writeImuCmd(CMD_CFG_LF, val, 6)

    # 覆寫 show()，看排版（也會把視窗帶到最上層）
    def show(self):
        super().show()
        self.raise_()
        self.activateWindow()


# ==========================================
#   UI 預覽測試區塊 (Layout Preview Only)
# ==========================================
if __name__ == "__main__":
    import sys
    import os
    from PySide6.QtWidgets import QApplication

    # 1. 修正路徑：將專案根目錄加入 path，以便能 import myLib
    # 目前位置：drivers/hins_fog_imu/widgets/ (向上 4 層即為根目錄)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))
    sys.path.append(root_dir)


    # 2. 定義一個「啞巴」Reader (Dummy Reader)
    # 它的目的只是為了讓 Widget 初始化不報錯，不需要任何功能
    class DummyReader:
        def __getattr__(self, name):
            # 無論 UI 呼叫什麼方法 (writeImuCmd, flushInputBuffer...)
            # 都回傳一個「什麼都不做的函式」，並回傳空值
            def method(*args, **kwargs):
                print(f"[UI Preview] Method called: {name}")
                return 0  # 避免某些計算需要數值

            return method


    app = QApplication(sys.argv)

    # 3. 啟動視窗 (請依據檔案名稱修改對應的 Class)
    # ------------------------------------------------

    # 如果是 pig_configuration_widget.py:
    window = pig_configuration_widget(DummyReader())
    # ------------------------------------------------

    window.show()
    sys.exit(app.exec())
