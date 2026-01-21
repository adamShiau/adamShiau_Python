# drivers/hins_gnss_ins/hins_config_widget.py
# -*- coding:UTF-8 -*-
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGroupBox,
                               QGridLayout, QLabel, QLineEdit, QFormLayout)
from PySide6.QtCore import Slot, Qt


class HinsConfigWidget(QWidget):
    def __init__(self, reader):
        super().__init__()
        self.reader = reader
        self.setWindowTitle("HINS GNSS/INS Configuration")
        self.resize(600, 500)
        self.setup_ui()

        # 連接 Reader 的解析訊號 (接收 Dict)
        self.reader.data_ready_qt.connect(self.on_mip_data_received)
        # 連接 Reader 的原始訊號 (接收 Hex，用於 Debug 欄位)
        self.reader.raw_ack_qt.connect(self.on_raw_data_received)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # --- 1. GPIO 控制區 ---
        gpio_group = QGroupBox("GPIO 1 Configuration (0x0C, 0x41)")
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
        gpio_layout.addWidget(QLabel("Pin ID:"), 1, 0)
        gpio_layout.addWidget(self.le_pin_id, 1, 1)
        gpio_layout.addWidget(QLabel("Feature:"), 2, 0)
        gpio_layout.addWidget(self.le_feature, 2, 1)
        gpio_layout.addWidget(QLabel("Behavior:"), 3, 0)
        gpio_layout.addWidget(self.le_behavior, 3, 1)
        gpio_layout.addWidget(QLabel("Pin State:"), 4, 0)
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

        # --- 3. 原始數據監控 ---
        raw_group = QGroupBox("Raw Monitor")
        raw_layout = QVBoxLayout()
        self.le_raw_hex = QLineEdit()
        self.le_raw_hex.setPlaceholderText("Waiting for RX...")
        raw_layout.addWidget(self.le_raw_hex)
        raw_group.setLayout(raw_layout)
        layout.addWidget(raw_group)

    def send_cmd(self, cmd_name):
        """ 發送封裝好的 V1 + MIP 指令 """
        cmd_map = {
            # V1 Header(BC CB 97 Len) + MIP(75 65 0C 04 04 41 02 01 32 9F) + V1 Tail(51 52)
            "READ_GP1": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x0C, 0x04, 0x04, 0x41, 0x02, 0x01, 0x32, 0x9F, 0x51, 0x52]
        }

        if cmd_name in cmd_map:
            self.reader.write_raw(cmd_map[cmd_name])
            self.le_ack_status.setText("Sending...")
            self.le_last_cmd.setText(cmd_name)

    @Slot(list)
    def on_raw_data_received(self, raw_bytes):
        """ 顯示原始 Hex """
        self.le_raw_hex.setText(" ".join([f"{b:02X}" for b in raw_bytes]))

    @Slot(dict)
    def on_mip_data_received(self, parsed_data):
        """ 核心：根據 Parser 的結果更新 UI """
        desc_set = parsed_data.get("desc_set")
        fields = parsed_data.get("fields", [])

        for field in fields:
            descriptor = field.get("descriptor")

            # --- Case 1: GPIO Config Response (0x0C, 0xC1) ---
            if desc_set == '0xc' and descriptor == '0xc1':
                # 直接讀取 Parser 翻譯好的字串！
                self.le_pin_id.setText(str(field.get('pin_id')))
                self.le_feature.setText(field.get('feature'))  # e.g., "UART"
                self.le_behavior.setText(field.get('behavior'))  # e.g., "UART2_TX"
                self.le_state.setText(str(field.get('pin_state')))

            # --- Case 2: ACK/NACK (0xF1) ---
            elif field.get("type") == "ACK":
                cmd_echo = field.get('cmd_echo')
                status = field.get('status')
                err_code = field.get('error_code')

                if err_code == 0:
                    self.le_ack_status.setStyleSheet("color: green; font-weight: bold;")
                    self.le_ack_status.setText(f"OK (Cmd {cmd_echo})")
                else:
                    self.le_ack_status.setStyleSheet("color: red; font-weight: bold;")
                    self.le_ack_status.setText(f"Error {err_code} (Cmd {cmd_echo})")