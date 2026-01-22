# drivers/hins_gnss_ins/widgets/hins_config_widget.py
# -*- coding:UTF-8 -*-
import sys
import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGroupBox, QApplication,
                               QGridLayout, QLabel, QLineEdit, QFormLayout, QTextEdit, QHBoxLayout)
from PySide6.QtCore import Slot, Qt, QDateTime


class HinsConfigWidget(QWidget):
    def __init__(self, reader):
        super().__init__()
        self.reader = reader
        self.setWindowTitle("HINS GNSS/INS Configuration")
        self.resize(750, 650)
        self.setup_ui()

        # 連接 Reader 的解析訊號
        if self.reader:
            self.reader.data_ready_qt.connect(self.on_mip_data_received)
            self.reader.raw_ack_qt.connect(self.on_raw_data_received)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # --- 1. GPIO 控制區 ---
        gpio_group = QGroupBox("GPIO Configuration (0x0C, 0x41)")
        gpio_layout = QGridLayout()

        self.btn_read_gpio1 = QPushButton("Read GPIO 1")
        self.btn_read_gpio1.clicked.connect(lambda: self.send_cmd("READ_GP1"))

        self.le_pin_id = QLineEdit();
        self.le_pin_id.setReadOnly(True)
        self.le_feature = QLineEdit();
        self.le_feature.setReadOnly(True)
        self.le_behavior = QLineEdit();
        self.le_behavior.setReadOnly(True)
        self.le_state = QLineEdit();
        self.le_state.setReadOnly(True)

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

        # --- 3. 原始數據監控 ---
        raw_group = QGroupBox("Raw Monitor")
        raw_layout = QVBoxLayout()

        tool_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear Console")
        self.btn_clear.setFixedWidth(100)
        self.btn_clear.clicked.connect(self.clear_console)
        tool_layout.addStretch()
        tool_layout.addWidget(self.btn_clear)

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

        raw_layout.addLayout(tool_layout)
        raw_layout.addWidget(self.console_te)
        raw_group.setLayout(raw_layout)
        layout.addWidget(raw_group)

    def clear_console(self):
        self.console_te.clear()

    def append_console(self, text, color="#FFFFFF"):
        html = f'<span style="color:{color};">{text}</span>'
        self.console_te.append(html)

    def send_cmd(self, cmd_name):
        """ 發送指令：先清空 Buffer，再發送，最後讀取 """
        cmd_map = {
            "READ_GP1": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x0C, 0x04, 0x04, 0x41, 0x02, 0x01, 0x32, 0x9F, 0x51, 0x52]
        }
        if cmd_name in cmd_map:
            cmd_bytes = cmd_map[cmd_name]

            conn = getattr(self.reader, '_connector', None)
            if conn:
                # --- [Step 1] 發送前徹底清空 Buffer (Flush) ---
                pre_n = conn.readInputBuffer()
                if pre_n > 0:
                    # 把舊的垃圾讀出來但不處理，直接丟掉
                    conn.readBinaryList(pre_n)
                    print(f"[DEBUG] 發送前已清空殘留數據: {pre_n} bytes")

                # --- [Step 2] 發送指令 ---
                self.reader.write_raw(cmd_bytes)

                # --- [Step 3] 等待並讀取最新回應 ---
                time.sleep(0.2)  # 給硬體反應時間

                n = conn.readInputBuffer()
                print(f"\n[DEBUG] 按下按鈕後讀取 Buffer Size: {n}")
                if n > 0:
                    raw = conn.readBinaryList(n)
                    print(f"[DEBUG] 收到數據: {' '.join([f'{b:02X}' for b in raw])}")
                    # 更新 UI 顯示
                    self.on_raw_data_received(raw)
                else:
                    print("[DEBUG] 警告：沒有收到回傳數據")

    @Slot(list)
    def on_raw_data_received(self, packet: list):
        if not packet: return
        self.append_console(f"RX: {' '.join([f'{b:02X}' for b in packet])}", "#D4D4D4")

    @Slot(dict)
    def on_mip_data_received(self, parsed_data):
        # 這裡處理 UI 欄位更新...
        pass


# --- 讓檔案可以單獨執行預覽 ---
if __name__ == "__main__":
    from PySide6.QtCore import QObject, Signal


    # Mock Reader 模擬物件，避免單獨執行時報錯
    class MockReader(QObject):
        data_ready_qt = Signal(dict)
        raw_ack_qt = Signal(list)

        def write_raw(self, data): print(f"Mock TX: {data}")


    app = QApplication(sys.argv)
    mock = MockReader()
    window = HinsConfigWidget(mock)
    window.show()
    sys.exit(app.exec())