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
        self.resize(750, 800)
        self.setup_ui()

        # 連接 Reader 的解析訊號 (接收 Dict 用於填寫欄位)
        self.reader.data_ready_qt.connect(self.on_mip_data_received)
        # 連接 Reader 的原始訊號 (接收原始列表用於 Raw Monitor 顏色解析)
        self.reader.raw_ack_qt.connect(self.on_raw_data_received)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # --- GPIO 控制區 ---
        gpio_group = QGroupBox("GPIO Configuration (0x0C, 0x41)")
        gpio_layout = QGridLayout()
        gpio_layout.setColumnStretch(0, 1)
        gpio_layout.setColumnStretch(1, 1)

        # 第一排：Read 按鈕
        self.btn_read_gpio1 = QPushButton("Read GPIO 1")
        self.btn_read_gpio1.clicked.connect(lambda: self.send_cmd("READ_GP1"))
        self.btn_read_gpio2 = QPushButton("Read GPIO 2")
        self.btn_read_gpio2.clicked.connect(lambda: self.send_cmd("READ_GP2"))

        # 第二排：Set 按鈕
        self.btn_set_gpio1 = QPushButton("Set GPIO 1 (UART2 Tx)")
        self.btn_set_gpio1.clicked.connect(lambda: self.send_cmd("SET_GP1_UART_TX"))
        self.btn_set_gpio2 = QPushButton("Set GPIO 2 (UART2 Rx)")
        self.btn_set_gpio2.clicked.connect(lambda: self.send_cmd("SET_GP2_UART_RX"))

        # 放置按鈕
        gpio_layout.addWidget(self.btn_read_gpio1, 0, 0)
        gpio_layout.addWidget(self.btn_read_gpio2, 0, 1)
        gpio_layout.addWidget(self.btn_set_gpio1, 1, 0)
        gpio_layout.addWidget(self.btn_set_gpio2, 1, 1)

        # 放置顯示欄位 (從第 2 列開始)
        self.le_pin_id = QLineEdit();
        self.le_pin_id.setReadOnly(True)
        self.le_feature = QLineEdit();
        self.le_feature.setReadOnly(True)
        self.le_behavior = QLineEdit();
        self.le_behavior.setReadOnly(True)
        self.le_pin_mode = QLineEdit();
        self.le_pin_mode.setReadOnly(True)

        gpio_layout.addWidget(QLabel("Pin ID:"), 2, 0)
        gpio_layout.addWidget(self.le_pin_id, 2, 1)
        gpio_layout.addWidget(QLabel("Feature:"), 3, 0)
        gpio_layout.addWidget(self.le_feature, 3, 1)
        gpio_layout.addWidget(QLabel("Behavior:"), 4, 0)
        gpio_layout.addWidget(self.le_behavior, 4, 1)
        gpio_layout.addWidget(QLabel("Pin Mode:"), 5, 0)
        gpio_layout.addWidget(self.le_pin_mode, 5, 1)

        gpio_group.setLayout(gpio_layout)
        layout.addWidget(gpio_group)

        # --- UART2 Baud Rate 控制區 (0x01, 0x09) ---
        uart_group = QGroupBox("UART2 Configuration (0x01, 0x09)")
        uart_layout = QGridLayout()
        uart_layout.setColumnStretch(0, 1)  # 左欄權重
        uart_layout.setColumnStretch(1, 1)  # 右欄權重

        self.btn_read_uart2_br = QPushButton("Read UART2 BR")
        self.btn_set_br_230400 = QPushButton("Set UART2 BR=230400")
        self.btn_set_br_115200 = QPushButton("Set UART2 BR=115200")
        self.le_baud_rate = QLineEdit();
        self.le_baud_rate.setReadOnly(True)

        self.btn_read_uart2_br.clicked.connect(lambda: self.send_cmd("READ_UART2_BR"))
        self.btn_set_br_230400.clicked.connect(lambda: self.send_cmd("SET_UART2_BR_230400"))
        self.btn_set_br_115200.clicked.connect(lambda: self.send_cmd("SET_UART2_BR_115200"))

        # 佈局：Read 在上，兩個 Set 在下並排
        uart_layout.addWidget(self.btn_read_uart2_br, 0, 0)
        uart_layout.addWidget(QLabel("Current Baud:"), 0, 1, Qt.AlignRight)
        uart_layout.addWidget(self.le_baud_rate, 0, 2)  # 佔據第三列
        uart_layout.addWidget(self.btn_set_br_230400, 1, 0)
        uart_layout.addWidget(self.btn_set_br_115200, 1, 1)

        uart_group.setLayout(uart_layout)
        layout.addWidget(uart_group)
        # --- UART2 Baud Rate 控制區 控制區結束 ---

        # --- Interface Control 控制區 (0x7F, 0x02) ---
        if_group = QGroupBox("Interface Control (0x7F, 0x02)")
        if_layout = QGridLayout()
        if_layout.setColumnStretch(0, 1)
        if_layout.setColumnStretch(1, 1)

        # 1. 先實例化按鈕
        self.btn_read_if = QPushButton("Read UART2 Interface")
        self.btn_set_if_mip = QPushButton("Set UART2 MIP")

        # 2. 連接訊號 (確保只連線這一次)
        self.btn_read_if.clicked.connect(lambda: self.send_cmd("READ_IF_UART2"))
        self.btn_set_if_mip.clicked.connect(lambda: self.send_cmd("SET_UART2_MIP"))

        self.le_port = QLineEdit();
        self.le_port.setReadOnly(True)
        self.le_in_proto = QLineEdit();
        self.le_in_proto.setReadOnly(True)
        self.le_out_proto = QLineEdit();
        self.le_out_proto.setReadOnly(True)

        # 3. 佈局放置
        if_layout.addWidget(self.btn_read_if, 0, 0)
        if_layout.addWidget(self.btn_set_if_mip, 0, 1)

        if_layout.addWidget(QLabel("Port:"), 1, 0)
        if_layout.addWidget(self.le_port, 1, 1)
        if_layout.addWidget(QLabel("Protocols Incoming:"), 2, 0)
        if_layout.addWidget(self.le_in_proto, 2, 1)
        if_layout.addWidget(QLabel("Protocols Outgoing:"), 3, 0)
        if_layout.addWidget(self.le_out_proto, 3, 1)

        if_group.setLayout(if_layout)
        layout.addWidget(if_group)
        # --- Interface Control 控制區 (0x7F, 0x02) 結束---

        # --- 2. 系統回應區 (修正：恢復原本的 Command 顯示器) ---
        status_group = QGroupBox("System Status (ACK/NACK)")
        status_layout = QFormLayout()
        self.le_last_cmd = QLineEdit();
        self.le_last_cmd.setReadOnly(True)
        self.le_ack_status = QLineEdit();
        self.le_ack_status.setReadOnly(True)
        status_layout.addRow("Last Command:", self.le_last_cmd)
        status_layout.addRow("ACK Status:", self.le_ack_status)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # --- 3. 原始數據監控 (Raw Monitor) ---
        raw_group = QGroupBox("Raw Monitor")
        raw_layout = QVBoxLayout()
        tool_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear Console")
        self.btn_clear.setFixedWidth(100)
        self.btn_clear.clicked.connect(self.clear_console)
        tool_layout.addStretch();
        tool_layout.addWidget(self.btn_clear)

        self.console_te = QTextEdit();
        self.console_te.setReadOnly(True)
        self.console_te.setStyleSheet(
            "background-color: #1E1E1E; color: #D4D4D4; font-family: Consolas; font-size: 10pt;")
        raw_layout.addLayout(tool_layout);
        raw_layout.addWidget(self.console_te)
        raw_group.setLayout(raw_layout)
        layout.addWidget(raw_group)

    def clear_console(self):
        self.console_te.clear()

    def append_console(self, text, color="#FFFFFF"):
        html = f'<span style="color:{color};">{text}</span>'
        self.console_te.append(html)
        sb = self.console_te.verticalScrollBar()
        sb.setValue(sb.maximum())

    def send_cmd(self, cmd_name):
        """ 發送指令：清空緩衝 -> 發送 -> 同步讀取解析 """
        cmd_map = {
            "READ_GP1": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x0C, 0x04, 0x04, 0x41, 0x02, 0x01, 0x32, 0x9F, 0x51,
                         0x52],
            "READ_GP2": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x0C, 0x04, 0x04, 0x41, 0x02, 0x02, 0x33, 0xA0, 0x51,
                         0x52],
            "SET_GP1_UART_TX": [0xBC, 0xCB, 0x97, 0x0D, 0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x01, 0x05, 0x21,
                                0x00, 0x5D, 0xAE, 0x51, 0x52],
            "SET_GP2_UART_RX": [0xBC, 0xCB, 0x97, 0x0D, 0x75, 0x65, 0x0C, 0x07, 0x07, 0x41, 0x01, 0x02, 0x05, 0x22,
                                0x02, 0x61, 0xB6, 0x51, 0x52],
            "READ_UART2_BR": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x01, 0x04, 0x04, 0x09, 0x02, 0x12, 0x00, 0xC6, 0x51,
                              0x52],
            "SET_UART2_BR_230400": [0xBC, 0xCB, 0x97, 0x0E, 0x75, 0x65, 0x01, 0x08, 0x08, 0x09, 0x01, 0x12, 0x00, 0x03,
                                    0x84, 0x00, 0x8E, 0x15, 0x51, 0x52],
            "SET_UART2_BR_115200": [0xBC, 0xCB, 0x97, 0x0E, 0x75, 0x65, 0x01, 0x08, 0x08, 0x09, 0x01, 0x12, 0x00, 0x01,
                                    0xC2, 0x00, 0xCA, 0x8B, 0x51, 0x52],
            "READ_IF_UART2": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x7F, 0x04, 0x04, 0x02, 0x02, 0x12, 0x77, 0xA5, 0x51,
                              0x52],
            "SET_UART2_MIP": [0xBC, 0xCB, 0x97, 0x12, 0x75, 0x65, 0x7F, 0x0C, 0x0C, 0x02, 0x01, 0x12, 0x00, 0x00,
                                 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x88, 0x21, 0x51, 0x52]
        }

        if cmd_name in cmd_map:
            cmd_bytes = cmd_map[cmd_name]
            conn = getattr(self.reader, '_connector', None)

            if conn:
                pre_n = conn.readInputBuffer()
                if pre_n > 0: conn.readBinaryList(pre_n)

                hex_str = " ".join([f"{b:02X}" for b in cmd_bytes])
                self.append_console(
                    f"[{QDateTime.currentDateTime().toString('HH:mm:ss.zzz')}] TX [{cmd_name}]: {hex_str}", "#569CD6")
                self.reader.write_raw(cmd_bytes)
                self.le_ack_status.setText("Sending...")
                self.le_last_cmd.setText(cmd_name)

                time.sleep(0.2)
                post_n = conn.readInputBuffer()
                if post_n > 0:
                    raw_data = conn.readBinaryList(post_n)
                    self.on_raw_data_received(raw_data)
                    # 關鍵：將數據餵給 Reader 解析引擎，ACK 才會變 OK
                    self.reader.handle_packet(raw_data)

    @Slot(list)
    def on_raw_data_received(self, packet: list):
        """ 解析接收數據並上色顯示 (支援粘包處理) """
        if not packet: return
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")

        # 顯示完整原始流 (灰色)
        full_hex = " ".join([f"{b:02X}" for b in packet])
        self.append_console(f"[{timestamp}] RX [RAW]: {full_hex}", "#D4D4D4")

        # 封包拆解迴圈
        idx = 0
        while idx < len(packet):
            if packet[idx] == 0xFA:  # 找到標頭
                if idx + 6 > len(packet): break
                payload_len = packet[idx + 4] | (packet[idx + 5] << 8)
                v1_type = packet[idx + 1]
                total_len = 6 + payload_len + 2

                if idx + total_len > len(packet): break
                sub_pkt = packet[idx: idx + total_len]
                sub_hex = " ".join([f"{b:02X}" for b in sub_pkt])

                if v1_type == 0xA1:  # ACK
                    self.append_console(f"RX [ACK] : {sub_hex}", "#6A9955")
                elif v1_type == 0xA2:  # RESULT
                    self.append_console(f"RX [RESULT] : {sub_hex}", "#808080")
                    # 進一步解析 MIP Payload
                    if payload_len >= 2:
                        mip_data = sub_pkt[6: 6 + payload_len]
                        if mip_data[0] == 0x75 and mip_data[1] == 0x65:
                            mip_hex = " ".join([f"{b:02X}" for b in mip_data])
                            self.append_console(f"MIP Response: {mip_hex}", "#C586C0")
                idx += total_len
            else:
                idx += 1

    @Slot(dict)
    def on_mip_data_received(self, parsed_data):
        """ 更新 UI 顯示欄位 """
        desc_set = parsed_data.get("desc_set")
        fields = parsed_data.get("fields", [])

        for field in fields:
            f_type = field.get("type")
            if desc_set == '0xc' and f_type == 'GPIO_CONF':
                print('field:', field)
                print(f"DEBUG: Processing field type: {field.get('type')}")  # 加入這行檢查
                self.le_pin_id.setText(str(field.get('pin_id')))
                self.le_feature.setText(field.get('feature'))
                self.le_behavior.setText(field.get('behavior'))
                self.le_pin_mode.setText(str(field.get('pin_mode')))
            # --- 處理 UART 波特率回傳 (0x01, 0x09) ---
            elif desc_set == '0x1' and f_type == 'BAUD_RATE':
                self.le_baud_rate.setText(str(field.get('baud_rate')))
            # 處理 Interface Control (0x7F)
            elif desc_set == '0x7f' and f_type == 'INTERFACE_CTRL':
                self.le_port.setText(field.get('port'))
                self.le_in_proto.setText(field.get('incoming'))
                self.le_out_proto.setText(field.get('outgoing'))
            elif f_type == "ACK":
                err_code = field.get('error_code')
                if err_code == 0:
                    self.le_ack_status.setStyleSheet("color: green; font-weight: bold;")
                    self.le_ack_status.setText("OK")
                else:
                    self.le_ack_status.setStyleSheet("color: red; font-weight: bold;")
                    self.le_ack_status.setText(f"Error {err_code}")


# ==========================================
#   UI 預覽測試區塊 (Layout Preview Only)
# ==========================================
if __name__ == "__main__":
    import sys
    import os
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QObject, Signal

    # 1. 修正路徑：向上 4 層即為根目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))
    sys.path.append(root_dir)

    # 2. 定義一個「啞巴」Reader (Dummy Reader)
    # 繼承 QObject 才能定義 Signal
    class DummyReader(QObject):
        data_ready_qt = Signal(dict)
        raw_ack_qt = Signal(list)

        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"[UI Preview] Method called: {name}")
                return 0
            return method

    app = QApplication(sys.argv)

    # 3. 啟動視窗
    # 傳入 DummyReader()，它現在具備 connect 屬性了
    window = HinsConfigWidget(DummyReader())

    window.show()
    sys.exit(app.exec())