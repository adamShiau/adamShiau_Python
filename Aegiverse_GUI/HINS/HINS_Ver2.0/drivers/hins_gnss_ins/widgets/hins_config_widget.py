# drivers/hins_gnss_ins/widgets/hins_config_widget.py
# -*- coding:UTF-8 -*-
import sys
import time
import struct
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGroupBox, QApplication,
                               QGridLayout, QLabel, QLineEdit, QFormLayout, QTextEdit,
                               QHBoxLayout, QScrollArea) # 確保這裡有 QScrollArea
from PySide6.QtCore import Slot, Qt, QDateTime


class HinsConfigWidget(QWidget):
    def __init__(self, reader):
        super().__init__()
        self.reader = reader
        self.setWindowTitle("HINS GNSS/INS Configuration")
        self.resize(1200, 1000)
        self.setup_ui()

        # 連接 Reader 的解析訊號 (接收 Dict 用於填寫欄位)
        self.reader.data_ready_qt.connect(self.on_mip_data_received)
        # 連接 Reader 的原始訊號 (接收原始列表用於 Raw Monitor 顏色解析)
        self.reader.raw_ack_qt.connect(self.on_raw_data_received)

    def setup_ui(self):
        # 主佈局改為橫向排列 (左邊設定，右邊 Console)
        main_h_layout = QHBoxLayout(self)

        # --- 左側：參數設定捲動區 (防止內容過長擋住螢幕) ---
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        # 1. GPIO 控制區 (維持原排版)
        gpio_group = QGroupBox("GPIO Configuration (0x0C, 0x41)")
        gpio_layout = QGridLayout()
        self.btn_read_gpio1 = QPushButton("Read GPIO 1")
        self.btn_read_gpio1.clicked.connect(lambda: self.send_cmd("READ_GP1"))
        self.btn_read_gpio2 = QPushButton("Read GPIO 2")
        self.btn_read_gpio2.clicked.connect(lambda: self.send_cmd("READ_GP2"))
        self.btn_set_gpio1 = QPushButton("Set GPIO 1 (UART2 Tx)")
        self.btn_set_gpio1.clicked.connect(lambda: self.send_cmd("SET_GP1_UART_TX"))
        self.btn_set_gpio2 = QPushButton("Set GPIO 2 (UART2 Rx)")
        self.btn_set_gpio2.clicked.connect(lambda: self.send_cmd("SET_GP2_UART_RX"))

        gpio_layout.addWidget(self.btn_read_gpio1, 0, 0)
        gpio_layout.addWidget(self.btn_read_gpio2, 0, 1)
        gpio_layout.addWidget(self.btn_set_gpio1, 1, 0)
        gpio_layout.addWidget(self.btn_set_gpio2, 1, 1)

        self.le_pin_id = QLineEdit();
        self.le_pin_id.setReadOnly(True)
        self.le_feature = QLineEdit();
        self.le_feature.setReadOnly(True)
        self.le_behavior = QLineEdit();
        self.le_behavior.setReadOnly(True)
        self.le_pin_mode = QLineEdit();
        self.le_pin_mode.setReadOnly(True)
        gpio_layout.addWidget(QLabel("Pin ID:"), 2, 0);
        gpio_layout.addWidget(self.le_pin_id, 2, 1)
        gpio_layout.addWidget(QLabel("Feature:"), 3, 0);
        gpio_layout.addWidget(self.le_feature, 3, 1)
        gpio_layout.addWidget(QLabel("Behavior:"), 4, 0);
        gpio_layout.addWidget(self.le_behavior, 4, 1)
        gpio_layout.addWidget(QLabel("Pin Mode:"), 5, 0);
        gpio_layout.addWidget(self.le_pin_mode, 5, 1)
        gpio_group.setLayout(gpio_layout)
        left_layout.addWidget(gpio_group)

        # 2. Data Stream Control (收緊排版)
        stream_group = QGroupBox("Data Stream Control (0x0C, 0x0F/0x11)")
        stream_grid = QGridLayout()
        self.btn_set_data = QPushButton("Set Data")
        self.btn_stream_on = QPushButton("Stream ON");
        self.btn_stream_on.setStyleSheet("background-color: #1E4620; color: white;")
        self.btn_stream_off = QPushButton("Stream OFF");
        self.btn_stream_off.setStyleSheet("background-color: #5F2120; color: white;")
        self.btn_set_data.clicked.connect(lambda: self.send_cmd("SET_DATA"))
        self.btn_stream_on.clicked.connect(lambda: self.send_cmd("STREAM_ON"))
        self.btn_stream_off.clicked.connect(lambda: self.send_cmd("STREAM_OFF"))
        # 限制按鈕寬度
        for btn in [self.btn_set_data, self.btn_stream_on, self.btn_stream_off]: btn.setMaximumWidth(120)
        stream_grid.addWidget(self.btn_set_data, 0, 0)
        stream_grid.addWidget(self.btn_stream_on, 0, 1)
        stream_grid.addWidget(self.btn_stream_off, 0, 2)
        stream_group.setLayout(stream_grid)
        left_layout.addWidget(stream_group)

        # 3. UART2 Configuration (已移除 115200)
        uart_group = QGroupBox("UART2 Configuration (0x01, 0x09)")
        uart_layout = QGridLayout()
        self.btn_read_uart2_br = QPushButton("Read UART2 BR")
        self.btn_set_br_230400 = QPushButton("Set UART2 BR=230400")
        self.le_baud_rate = QLineEdit();
        self.le_baud_rate.setReadOnly(True)
        self.btn_read_uart2_br.clicked.connect(lambda: self.send_cmd("READ_UART2_BR"))
        self.btn_set_br_230400.clicked.connect(lambda: self.send_cmd("SET_UART2_BR_230400"))
        uart_layout.addWidget(self.btn_read_uart2_br, 0, 0)
        uart_layout.addWidget(QLabel("Current Baud:"), 0, 1, Qt.AlignRight)
        uart_layout.addWidget(self.le_baud_rate, 0, 2)
        uart_layout.addWidget(self.btn_set_br_230400, 1, 0)
        uart_group.setLayout(uart_layout)
        left_layout.addWidget(uart_group)

        # 4. Interface Control (補回顯示欄位)
        if_group = QGroupBox("Interface Control (0x7F, 0x02)")
        if_layout = QGridLayout()
        self.btn_read_if = QPushButton("Read UART2 Interface")
        self.btn_set_if_mip = QPushButton("Set UART2 MIP")
        self.btn_read_if.clicked.connect(lambda: self.send_cmd("READ_IF_UART2"))
        self.btn_set_if_mip.clicked.connect(lambda: self.send_cmd("SET_UART2_MIP"))
        self.le_port = QLineEdit();
        self.le_port.setReadOnly(True)
        self.le_in_proto = QLineEdit();
        self.le_in_proto.setReadOnly(True)
        self.le_out_proto = QLineEdit();
        self.le_out_proto.setReadOnly(True)
        if_layout.addWidget(self.btn_read_if, 0, 0);
        if_layout.addWidget(self.btn_set_if_mip, 0, 1)
        if_layout.addWidget(QLabel("Port:"), 1, 0);
        if_layout.addWidget(self.le_port, 1, 1)
        if_layout.addWidget(QLabel("Incoming Proto:"), 2, 0);
        if_layout.addWidget(self.le_in_proto, 2, 1)
        if_layout.addWidget(QLabel("Outgoing Proto:"), 3, 0);
        if_layout.addWidget(self.le_out_proto, 3, 1)
        if_group.setLayout(if_layout)
        left_layout.addWidget(if_group)

        # 5. DCM Transformation (0x33)
        dcm_group = QGroupBox("Sensor-to-Vehicle DCM (0x33)")
        dcm_layout = QVBoxLayout()
        dcm_btn_layout = QHBoxLayout()
        self.btn_read_dcm = QPushButton("Read DCM");
        self.btn_set_dcm = QPushButton("Set DCM")
        self.btn_set_dcm.setStyleSheet("background-color: #2D5A27; color: white;")
        dcm_btn_layout.addWidget(self.btn_read_dcm);
        dcm_btn_layout.addWidget(self.btn_set_dcm)
        self.btn_read_dcm.clicked.connect(lambda: self.send_cmd("READ_DCM"))
        self.btn_set_dcm.clicked.connect(self.send_set_dcm_payload)
        self.matrix_grid = QGridLayout();
        self.matrix_cells = []
        for r in range(3):
            row_cells = []
            for c in range(3):
                le = QLineEdit("0.0");
                le.setFixedWidth(75);
                le.setAlignment(Qt.AlignCenter)
                self.matrix_grid.addWidget(le, r, c);
                row_cells.append(le)
            self.matrix_cells.append(row_cells)
        dcm_layout.addLayout(dcm_btn_layout);
        dcm_layout.addLayout(self.matrix_grid)
        dcm_group.setLayout(dcm_layout)
        left_layout.addWidget(dcm_group)

        # 6. System Commands & Status
        sys_group = QGroupBox("System Control")
        sys_v_layout = QVBoxLayout()
        sys_h_layout = QHBoxLayout()
        self.btn_idle = QPushButton("IDLE");
        self.btn_resume = QPushButton("RESUME");
        self.btn_save = QPushButton("SAVE")
        self.btn_save.setStyleSheet("background-color: #2D5A27; color: white; font-weight: bold;")
        self.btn_idle.clicked.connect(lambda: self.send_cmd("SET_TO_IDLE"))
        self.btn_resume.clicked.connect(lambda: self.send_cmd("RESUME"))
        self.btn_save.clicked.connect(lambda: self.send_cmd("SAVE_SETTINGS"))
        sys_h_layout.addWidget(self.btn_idle);
        sys_h_layout.addWidget(self.btn_resume);
        sys_h_layout.addWidget(self.btn_save)
        sys_v_layout.addLayout(sys_h_layout)

        status_form = QFormLayout()
        self.le_last_cmd = QLineEdit();
        self.le_last_cmd.setReadOnly(True)
        self.le_ack_status = QLineEdit();
        self.le_ack_status.setReadOnly(True)
        status_form.addRow("Last CMD:", self.le_last_cmd);
        status_form.addRow("ACK Status:", self.le_ack_status)
        sys_v_layout.addLayout(status_form)
        sys_group.setLayout(sys_v_layout);
        left_layout.addWidget(sys_group)
        # --- 新增天線區塊：GNSS Multi-Antenna Offset (0x0D, 0x54) ---
        ant_group = QGroupBox("GNSS Multi-Antenna Offset (0x0D, 0x54) [Unit: m]")
        ant_v_layout = QVBoxLayout()
        self.ant_inputs = {}

        for ant_id in [1, 2]:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)
            row_layout.addWidget(QLabel(f"Ant {ant_id}:"))

            axes_controls = []
            for axis in ['X', 'Y', 'Z']:
                # 軸標籤：設定固定寬度並靠右，確保緊貼輸入框
                lbl = QLabel(f"{axis}:")
                lbl.setFixedWidth(15)
                lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                le = QLineEdit("0.000")
                le.setFixedWidth(60)
                le.setAlignment(Qt.AlignCenter)

                row_layout.addWidget(lbl)
                row_layout.addWidget(le)

                # 在 Z 軸輸入框後方多加一點間隔，避免連到後面的按鈕
                if axis != 'Z':
                    row_layout.addSpacing(10)

                axes_controls.append(le)

            self.ant_inputs[ant_id] = axes_controls

            btn_read = QPushButton(f"Read Ant {ant_id}")
            btn_set = QPushButton(f"Set Ant {ant_id}")
            btn_set.setStyleSheet("background-color: #2D5A27; color: white;")

            # 連結新增的方法
            btn_read.clicked.connect(lambda _, aid=ant_id: self.send_cmd(f"READ_ANT{aid}"))
            btn_set.clicked.connect(lambda _, aid=ant_id: self.send_set_antenna_offset(aid))

            row_layout.addWidget(btn_read)
            row_layout.addWidget(btn_set)
            ant_v_layout.addLayout(row_layout)

        ant_group.setLayout(ant_v_layout)
        left_layout.addWidget(ant_group)

        left_scroll.setWidget(left_container)
        main_h_layout.addWidget(left_scroll, 45)  # 左側權重 45%

        # --- 右側：Raw Monitor ---
        raw_group = QGroupBox("Raw Monitor")
        raw_v_layout = QVBoxLayout()
        self.console_te = QTextEdit();
        self.console_te.setReadOnly(True)
        self.console_te.setStyleSheet(
            "background-color: #1E1E1E; color: #D4D4D4; font-family: Consolas; font-size: 10pt;")
        self.btn_clear = QPushButton("Clear Console");
        self.btn_clear.clicked.connect(self.clear_console)
        raw_v_layout.addWidget(self.console_te);
        raw_v_layout.addWidget(self.btn_clear)
        raw_group.setLayout(raw_v_layout)
        main_h_layout.addWidget(raw_group, 55)  # 右側權重 55%

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
                                 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x88, 0x21, 0x51, 0x52],
            "SET_TO_IDLE": [0xBC, 0xCB, 0x97, 0x08, 0x75, 0x65, 0x01, 0x02, 0x02, 0x02, 0xE1, 0xC7, 0x51, 0x52],
            "RESUME": [0xBC, 0xCB, 0x97, 0x08, 0x75, 0x65, 0x01, 0x02, 0x02, 0x06, 0xE5, 0xCB, 0x51, 0x52],
            "SAVE_SETTINGS": [0xBC, 0xCB, 0x97, 0x09, 0x75, 0x65, 0x0C, 0x03, 0x03, 0x30, 0x03, 0x1F, 0x45, 0x51, 0x52],
            "SET_DATA": [0xBC, 0xCB, 0x97, 0x11, 0x75, 0x65, 0x0C, 0x0B, 0x0B, 0x0F, 0x01, 0x82, 0x02, 0xD3, 0x00, 0x64,
                         0x49, 0x00, 0x64, 0x74, 0x78, 0x51, 0x52],
            "STREAM_ON": [0xBC, 0xCB, 0x97, 0x0B, 0x75, 0x65, 0x0C, 0x05, 0x05, 0x11, 0x01, 0x82, 0x01, 0x85, 0x1C,
                          0x51, 0x52],
            "STREAM_OFF": [0xBC, 0xCB, 0x97, 0x0B, 0x75, 0x65, 0x0C, 0x05, 0x05, 0x11, 0x01, 0x82, 0x00, 0x84, 0x1B,
                           0x51, 0x52],
            "READ_DCM": [0xBC, 0xCB, 0x97, 0x09, 0x75, 0x65, 0x0C, 0x03, 0x03, 0x33, 0x02, 0x21, 0x4A, 0x51, 0x52],
            "READ_ANT1": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x0D, 0x04, 0x04, 0x54, 0x02, 0x01, 0x46, 0xDE, 0x51,
                          0x52],
            "READ_ANT2": [0xBC, 0xCB, 0x97, 0x0A, 0x75, 0x65, 0x0D, 0x04, 0x04, 0x54, 0x02, 0x02, 0x47, 0xDF, 0x51,
                          0x52],
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

                QApplication.processEvents()

                wait_time = 3.0 if cmd_name == "SAVE_SETTINGS" else 0.2
                time.sleep(wait_time)
                post_n = conn.readInputBuffer()
                if post_n > 0:
                    raw_data = conn.readBinaryList(post_n)
                    # self.on_raw_data_received(raw_data)
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
            # --- 新增註解：將 ACK 判斷獨立出來，確保 Read DCM (0x33) 的 ACK 也能觸發 ---
            if f_type == "ACK":
                err_code = field.get('error_code')
                self.le_ack_status.setText("OK" if err_code == 0 else f"Error {err_code}")
                self.le_ack_status.setStyleSheet(f"color: {'green' if err_code == 0 else 'red'}; font-weight: bold;")
                continue

            if desc_set == '0xc' and f_type == 'GPIO_CONF':
                print('field:', field)
                print(f"DEBUG: Processing field type: {field.get('type')}")  # 加入這行檢查
                self.le_pin_id.setText(str(field.get('pin_id')))
                self.le_feature.setText(field.get('feature'))
                self.le_behavior.setText(field.get('behavior'))
                self.le_pin_mode.setText(str(field.get('pin_mode')))
            # --- 新增註解：處理 DCM 回傳數據顯示 ---
            elif desc_set == '0xc' and f_type == 'SENS_VEH_DCM':
                m = field.get('matrix', [])
                for r in range(3):
                    for c in range(3):
                        self.matrix_cells[r][c].setText(f"{m[r][c]:.4f}")
            # --- 處理 UART 波特率回傳 (0x01, 0x09) ---
            elif desc_set == '0x1' and f_type == 'BAUD_RATE':
                self.le_baud_rate.setText(str(field.get('baud_rate')))
            # 處理 Interface Control (0x7F)
            elif desc_set == '0x7f' and f_type == 'INTERFACE_CTRL':
                self.le_port.setText(field.get('port'))
                self.le_in_proto.setText(field.get('incoming'))
                self.le_out_proto.setText(field.get('outgoing'))
            elif desc_set == '0xc' and f_type == 'STREAM_CTRL':
                status = "ON" if field.get('enabled') else "OFF"
                self.le_ack_status.setText(f"Stream {field.get('desc_set')}: {status}")
            elif desc_set == '0xc' and f_type == 'MSG_FORMAT':
                self.le_ack_status.setText(f"Format Set: {field.get('desc_set')}")
            # --- 新增：處理天線 Offset 回讀顯示 (0x0D, 0xD4) ---
            elif desc_set == '0xd' and f_type == 'ANTENNA_OFFSET':
                ant_id = field.get('receiver_id')
                offsets = field.get('offset', [])
                if ant_id in self.ant_inputs and len(offsets) == 3:
                    for i in range(3):
                        self.ant_inputs[ant_id][i].setText(f"{offsets[i]:.3f}")


    def calculate_checksum(self, data):
        """ MIP Fletcher Checksum (16-bit)  """
        ck1 = 0
        ck2 = 0
        for b in data:
            ck1 = (ck1 + b) & 0xFF
            ck2 = (ck2 + ck1) & 0xFF
        return [ck1, ck2]


    def send_set_dcm_payload(self):
        """ 動態產生 DCM 寫入封包 """
        try:
            m = [float(cell.text()) for row in self.matrix_cells for cell in row]

            # --- 原始封包組裝邏輯 ---
            header = [0x75, 0x65, 0x0C, 0x27, 0x27, 0x33, 0x01]
            payload = list(struct.pack('>9f', *m))
            full_no_ck = header + payload

            # --- 修正：呼叫類別內的 Checksum 函式 ---
            ck = self.calculate_checksum(full_no_ck)
            sync = [0xBC, 0xCB, 0x97, 0x2D]
            final = sync + full_no_ck + ck + [0x51, 0x52]

            # --- 發送數據 ---
            self.reader.write_raw(final)
            self.le_last_cmd.setText("SET_DCM")
            self.le_ack_status.setText("Sending...")

            QApplication.processEvents()

            # --- 原始 Log 顯示與同步解析邏輯 ---
            hex_str = " ".join([f"{b:02X}" for b in final])
            self.append_console(
                f"[{QDateTime.currentDateTime().toString('HH:mm:ss.zzz')}] TX [SET_DCM]: {hex_str}", "#569CD6")

            time.sleep(0.2)
            conn = getattr(self.reader, '_connector', None)
            if conn:
                n = conn.readInputBuffer()
                if n > 0:
                    self.reader.handle_packet(conn.readBinaryList(n))

        except ValueError:
            self.append_console("Error: Invalid Matrix input", "red")

    def send_set_antenna_offset(self, ant_id):
        """ 動態產生 Vector3f 寫入封包 (修正長度計算問題) """
        try:
            # 1. 取得 UI 數值
            vals = [float(le.text()) for le in self.ant_inputs[ant_id]]

            # 2. 組裝 MIP 部分 (完全對應您的真實指令格式)
            # 75 65 0D (Header) + 10 (Payload Len) + 10 (Field Len) + 54 (Desc) + 01 (Func) + ID
            mip_header = [0x75, 0x65, 0x0D, 0x10, 0x10, 0x54, 0x01, ant_id]
            payload = list(struct.pack('>3f', *vals))
            full_no_ck = mip_header + payload

            # 3. 計算 Fletcher Checksum
            ck = self.calculate_checksum(full_no_ck)

            # 4. 關鍵修正：動態計算 Sync Header 的長度欄位
            # 這會自動根據資料量算出 22 (0x16)
            total_payload_len = len(full_no_ck) + len(ck)

            sync = [0xBC, 0xCB, 0x97, total_payload_len]
            final = sync + full_no_ck + ck + [0x51, 0x52]

            # 5. 更新 UI 與發送
            self.le_last_cmd.setText(f"SET_ANT_{ant_id}")
            self.le_ack_status.setText("Sending...")
            QApplication.processEvents()

            self.reader.write_raw(final)
            hex_str = " ".join([f"{b:02X}" for b in final])
            self.append_console(
                f"[{QDateTime.currentDateTime().toString('HH:mm:ss.zzz')}] TX [SET_ANT_{ant_id}]: {hex_str}", "#569CD6")

            # 6. 同步讀取解析
            time.sleep(0.2)
            conn = getattr(self.reader, '_connector', None)
            if conn:
                n = conn.readInputBuffer()
                if n > 0:
                    self.reader.handle_packet(conn.readBinaryList(n))
        except ValueError:
            self.append_console("Error: Invalid Antenna Offset input", "red")

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