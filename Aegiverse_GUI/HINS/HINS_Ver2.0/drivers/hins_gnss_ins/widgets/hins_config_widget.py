# drivers/hins_gnss_ins/widgets/hins_config_widget.py
# -*- coding:UTF-8 -*-
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGroupBox,
                               QGridLayout, QLabel, QLineEdit, QFormLayout, QTextEdit, QHBoxLayout)
from PySide6.QtCore import Slot, Qt, QDateTime


class HinsConfigWidget(QWidget):
    def __init__(self, reader):
        super().__init__()
        self.reader = reader
        self.setWindowTitle("HINS GNSS/INS Configuration")
        self.resize(750, 650)  # 視窗加大一點
        self.setup_ui()

        # 連接 Reader 的解析訊號 (接收 Dict)
        self.reader.data_ready_qt.connect(self.on_mip_data_received)
        # 連接 Reader 的原始訊號 (接收 Hex，用於 Debug 欄位)
        self.reader.raw_ack_qt.connect(self.on_raw_data_received)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # --- 1. GPIO 控制區 ---
        gpio_group = QGroupBox("GPIO Configuration (0x0C, 0x41)")
        gpio_layout = QGridLayout()

        self.btn_read_gpio1 = QPushButton("Read GPIO 1")
        self.btn_read_gpio1.clicked.connect(lambda: self.send_cmd("READ_GP1"))

        # 顯示解析結果的欄位
        self.le_pin_id = QLineEdit();
        self.le_pin_id.setReadOnly(True)
        self.le_feature = QLineEdit();
        self.le_feature.setReadOnly(True)
        self.le_behavior = QLineEdit();
        self.le_behavior.setReadOnly(True)
        self.le_state = QLineEdit();
        self.le_state.setReadOnly(True)

        # 排版
        gpio_layout.addWidget(self.btn_read_gpio1, 0, 0, 1, 2)
        gpio_layout.addWidget(QLabel("Pin ID:"), 1, 0);
        gpio_layout.addWidget(self.le_pin_id, 1, 1)
        gpio_layout.addWidget(QLabel("Feature:"), 2, 0);
        gpio_layout.addWidget(self.le_feature, 2, 1)
        gpio_layout.addWidget(QLabel("Behavior:"), 3, 0);
        gpio_layout.addWidget(self.le_behavior, 3, 1)
        gpio_layout.addWidget(QLabel("Pin Mode:"), 4, 0);
        gpio_layout.addWidget(self.le_state, 4, 1)

        gpio_group.setLayout(gpio_layout)
        layout.addWidget(gpio_group)

        # --- 2. 系統回應區 ---
        status_group = QGroupBox("System Status (ACK/NACK)")
        status_layout = QFormLayout()
        self.le_last_cmd = QLineEdit()
        self.le_ack_status = QLineEdit()
        status_layout.addRow("Last Command:", self.le_last_cmd)
        status_layout.addRow("ACK Status:", self.le_ack_status)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # --- 3. 原始數據監控 (升級版) ---
        raw_group = QGroupBox("Raw Monitor")
        raw_layout = QVBoxLayout()

        # [新增] 工具列 layout (放置 Clear 按鈕)
        tool_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear Console")
        self.btn_clear.setFixedWidth(100)
        self.btn_clear.clicked.connect(self.clear_console)  # 連接清除功能

        tool_layout.addStretch()  # 彈簧，把按鈕推到右邊
        tool_layout.addWidget(self.btn_clear)

        # [升級] 使用 QTextEdit 取代 QLineEdit
        self.console_te = QTextEdit()
        self.console_te.setReadOnly(True)
        self.console_te.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E; 
                color: #D4D4D4; 
                font-family: Consolas, Monospace; 
                font-size: 10pt;
            }
        """)

        raw_layout.addLayout(tool_layout)  # 加入工具列
        raw_layout.addWidget(self.console_te)
        raw_group.setLayout(raw_layout)
        layout.addWidget(raw_group)

    # --- 輔助函式 ---
    def clear_console(self):
        """ 清除 Console 畫面 """
        self.console_te.clear()

    def append_console(self, text, color="#FFFFFF"):
        """ 將帶顏色的文字加入 Console """
        html = f'<span style="color:{color};">{text}</span>'
        self.console_te.append(html)
        # 自動捲動到底部
        sb = self.console_te.verticalScrollBar()
        sb.setValue(sb.maximum())

    def send_cmd(self, cmd_name):
        """ 發送指令並顯示 TX Log """
        cmd_map = {
            "READ_GP1": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x0C, 0x04, 0x04, 0x41, 0x02, 0x01, 0x32, 0x9F, 0x51, 0x52]
        }

        if cmd_name in cmd_map:
            cmd_bytes = cmd_map[cmd_name]

            # 1. 顯示 TX Log (藍色)
            hex_str = " ".join([f"{b:02X}" for b in cmd_bytes])
            timestamp = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
            self.append_console(f"[{timestamp}] TX [{cmd_name}]: {hex_str}", color="#569CD6")

            # 2. 發送
            self.reader.write_raw(cmd_bytes)

            # 3. 更新狀態
            self.le_ack_status.setText("Sending...")
            self.le_last_cmd.setText(cmd_name)

    @Slot(list)
    def on_raw_data_received(self, packet: list):
        """
        接收原始數據並拆解顯示 (支援黏包處理)
        """
        if not packet: return

        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")

        # 1. 顯示完整 RAW Data (灰色)
        full_hex = " ".join([f"{b:02X}" for b in packet])
        self.append_console(f"[{timestamp}] RX [RAW]: {full_hex}", color="#D4D4D4")

        # 2. 迴圈解析：在 packet 中尋找 V1 封包 (FA 開頭)
        idx = 0
        while idx < len(packet):
            # 檢查是否為 FA Header
            if packet[idx] == 0xFA:
                if idx + 6 > len(packet): break

                # 依據 ack_codec_v1.cpp: Len 在 Index 4, 5 (Little Endian)
                payload_len = packet[idx + 4] | (packet[idx + 5] << 8)
                v1_type = packet[idx + 1]

                # 計算該封包總長
                total_len = 6 + payload_len + 2

                # 確保封包完整
                if idx + total_len > len(packet): break

                # 取出當前這個子封包
                sub_pkt = packet[idx: idx + total_len]
                sub_hex = " ".join([f"{b:02X}" for b in sub_pkt])

                # --- A. 顯示 ACK (綠色) ---
                if v1_type == 0xA1:
                    self.append_console(f"RX [ACK] : {sub_hex}", color="#6A9955")

                # --- B. 顯示 RESULT (灰色) ---
                elif v1_type == 0xA2:
                    self.append_console(f"RX [RESULT] : {sub_hex}", color="#808080")

                    # 檢查內部是否有 MIP Payload (從 index 6 開始)
                    if payload_len >= 2:
                        mip_data = sub_pkt[6: 6 + payload_len]
                        if len(mip_data) >= 2 and mip_data[0] == 0x75 and mip_data[1] == 0x65:
                            mip_hex = " ".join([f"{b:02X}" for b in mip_data])
                            # 顯示 MIP Response (紫色)
                            self.append_console(f"MIP Response: {mip_hex}", color="#C586C0")

                # 移動索引到下一個封包
                idx += total_len

            else:
                # 如果不是 FA 開頭，就往下一個 byte 找 (容錯)
                idx += 1

    @Slot(dict)
    def on_mip_data_received(self, parsed_data):
        desc_set = parsed_data.get("desc_set")
        fields = parsed_data.get("fields", [])

        for field in fields:
            # 使用 type 判斷比較安全
            f_type = field.get("type")

            # Case 1: GPIO Config
            if desc_set == '0xc' and f_type == 'GPIO_CONF':
                self.le_pin_id.setText(str(field.get('pin_id')))
                self.le_feature.setText(field.get('feature'))
                self.le_behavior.setText(field.get('behavior'))
                self.le_state.setText(str(field.get('pin_mode')))  # 改名為 pin_mode

            # Case 2: ACK (更新 UI 狀態文字)
            elif f_type == "ACK":
                cmd_echo = field.get('cmd_echo')
                err_code = field.get('error_code')
                if err_code == 0:
                    self.le_ack_status.setStyleSheet("color: green; font-weight: bold;")
                    self.le_ack_status.setText(f"OK (Cmd {cmd_echo})")
                else:
                    self.le_ack_status.setStyleSheet("color: red; font-weight: bold;")
                    self.le_ack_status.setText(f"Error {err_code} (Cmd {cmd_echo})")