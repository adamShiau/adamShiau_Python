import sys
import logging
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QGridLayout, QLineEdit, QPushButton,
                               QCheckBox, QApplication, QSpinBox, QFrame)
from PySide6.QtCore import Qt, Slot

# [完整保留] 您原始檔案的 Logging 設定
logger = logging.getLogger("drivers.HinsMonitor.Widget")


class MonitorGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HINS Heading Monitor")
        self.resize(1150, 850)

        # --- 1. 數據映射定義 ---
        self.FIX_NAMES = {0: "FIX NONE", 1: "FIX DA FLOAT", 2: "FIX DA FIXED"}
        self.STATE_NAMES = {1: "Initialization", 2: "Vertical Gyro", 3: "AHRS", 4: "Full Navigation"}
        self.COND_NAMES = {1: "Stable", 2: "Converging"}

        # --- 2. 數據緩衝區初始化 ---
        self.max_pts = 100
        self.buf_da = np.zeros(self.max_pts)
        self.buf_imu = np.zeros(self.max_pts)
        self.buf_off = np.zeros(self.max_pts)

        self.setup_ui()

        # [完整保留] 確保初始緩衝區與 SpinBox 同步
        self.update_buffer_size()

    def create_formal_label(self, title, color):
        """ 建立模仿主介面風格的正式數值組件 """
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        frame.setStyleSheet("border: 1px solid #AAA; border-radius: 4px; background: #F0F0F0;")
        frame.setFixedWidth(140)

        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(5, 2, 5, 2)
        v_layout.setSpacing(0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 9pt; color: #333; border: none; background: transparent;")
        title_lbl.setAlignment(Qt.AlignCenter)

        value_lbl = QLabel("-0.00")
        value_lbl.setStyleSheet(
            f"font-size: 14pt; font-weight: bold; color: {color}; border: none; background: transparent;")
        value_lbl.setAlignment(Qt.AlignCenter)

        unit_lbl = QLabel("deg")
        unit_lbl.setStyleSheet("font-size: 8pt; color: #666; border: none; background: transparent;")
        unit_lbl.setAlignment(Qt.AlignRight)

        v_layout.addWidget(title_lbl)
        v_layout.addWidget(value_lbl)
        v_layout.addWidget(unit_lbl)

        return frame, value_lbl

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # --- 1. MCU 狀態數據看板 ---
        status_group = QGroupBox("MCU Monitor Status")
        grid = QGridLayout()
        grid.setSpacing(10)

        self.le_widgets = {}
        fields = [
            ("DA Fix Type:", "fix_type"), ("DA Valid Flag:", "valid"),
            ("GPS TOW (s):", "tow"), ("Dynamic Mode:", "dyn"),
            ("Filter State:", "state"), ("Filter Condition:", "cond"),
            ("Case Flag:", "case"), ("Warning/Error:", "warn")
        ]

        for i, (label, key) in enumerate(fields):
            row, col = i // 4, (i % 4) * 2
            grid.addWidget(QLabel(f"<b>{label}</b>"), row, col)
            le = QLineEdit("-")
            le.setReadOnly(True)
            le.setAlignment(Qt.AlignCenter)
            le.setStyleSheet("background-color: #FDFDFD; color: #333; border: 1px solid #CCC;")
            self.le_widgets[key] = le
            if key == "warn":
                grid.addWidget(le, row, col + 1, 1, 3)
            else:
                grid.addWidget(le, row, col + 1)

        status_group.setLayout(grid)
        main_layout.addWidget(status_group)

        # --- 2. 圖表控制列 ---
        ctrl_layout = QHBoxLayout()

        self.cb_da = QCheckBox("Heading DA");
        self.cb_da.setChecked(True)
        self.cb_imu = QCheckBox("IMU Heading");
        self.cb_imu.setChecked(True)
        self.cb_off = QCheckBox("G-Heading Offset");
        self.cb_off.setChecked(True)

        ctrl_layout.addWidget(self.cb_da)
        ctrl_layout.addWidget(self.cb_imu)
        ctrl_layout.addWidget(self.cb_off)

        ctrl_layout.addStretch(1)

        self.frame_da, self.lbl_val_da = self.create_formal_label("DA Heading", "#008080")
        self.frame_imu, self.lbl_val_imu = self.create_formal_label("IMU Heading", "#8B4513")
        self.frame_off, self.lbl_val_off = self.create_formal_label("G-Offset", "#800080")

        ctrl_layout.addWidget(self.frame_da)
        ctrl_layout.addSpacing(40)
        ctrl_layout.addWidget(self.frame_imu)
        ctrl_layout.addSpacing(40)
        ctrl_layout.addWidget(self.frame_off)

        ctrl_layout.addStretch(1)

        ctrl_layout.addWidget(QLabel("<b>Plot Points:</b>"))
        self.sb_points = QSpinBox()
        self.sb_points.setRange(10, 5000);
        self.sb_points.setValue(100);
        self.sb_points.setFixedWidth(80)
        self.sb_points.valueChanged.connect(self.update_buffer_size)
        ctrl_layout.addWidget(self.sb_points)

        main_layout.addLayout(ctrl_layout)

        # --- 3. 圖表區 ---
        self.pw = pg.PlotWidget(title="Heading Data Rolling Monitor")
        self.pw.setBackground('#000000')
        self.pw.addLegend(offset=(30, 30), brush=(40, 40, 40, 200), labelTextColor='#FFFFFF')
        self.cur_da = self.pw.plot(pen=pg.mkPen('#00FFFF', width=2), name="Heading DA")
        self.cur_imu = self.pw.plot(pen=pg.mkPen('#FFFF00', width=2), name="IMU Heading")
        self.cur_off = self.pw.plot(pen=pg.mkPen('#FF00FF', width=2), name="G-Heading Offset")

        self.cb_da.toggled.connect(lambda v: self.cur_da.setVisible(v))
        self.cb_imu.toggled.connect(lambda v: self.cur_imu.setVisible(v))
        self.cb_off.toggled.connect(lambda v: self.cur_off.setVisible(v))

        main_layout.addWidget(self.pw)

    def update_buffer_size(self):
        self.max_pts = self.sb_points.value()
        self.buf_da = np.zeros(self.max_pts);
        self.buf_imu = np.zeros(self.max_pts);
        self.buf_off = np.zeros(self.max_pts)

    @Slot(dict)
    def update_data(self, data):
        try:
            # 1. 狀態與名稱更新
            valid = data.get("valid_flag_da", 0)
            v_names = []
            if valid & (1 << 0): v_names.append("RCV1")
            if valid & (1 << 1): v_names.append("RCV2")
            if valid & (1 << 2): v_names.append("ANT_OFF")
            self.le_widgets["valid"].setText(f"{hex(valid)} ({'/'.join(v_names) if v_names else 'INV'})")

            s82 = data.get("status_82", 0)
            w_names = []
            if s82 & (1 << 2): w_names.append("Roll/Pitch")
            if s82 & (1 << 3): w_names.append("Heading")
            if s82 & (1 << 4): w_names.append("Position")
            if s82 & (1 << 5): w_names.append("Velocity")
            if s82 & (1 << 10): w_names.append("NoTimeSync")

            # [修正] 當沒有警告位元(Bit 2-15)被觸發時，顯示 "no warning/err"
            warn_suffix = ", ".join(w_names) if w_names else "no warning/err"
            self.le_widgets["warn"].setText(f"{hex(s82)} ({warn_suffix})")

            # [修正] Case Flag 背景顏色調整
            c_flag = data.get("case_flag", 0)
            c_name = "GNSS mode" if c_flag == 1 else "Inertial mode" if c_flag == 2 else "Unknown"
            self.le_widgets["case"].setText(f"{c_flag} ({c_name})")

            # 當 case flag 為 2 時，背景顯示為淡藍色
            if c_flag == 2:
                self.le_widgets["case"].setStyleSheet("background-color: #E0F7FA; color: #333; border: 1px solid #CCC;")
            else:
                self.le_widgets["case"].setStyleSheet("background-color: #FDFDFD; color: #333; border: 1px solid #CCC;")

            # 其他數值更新
            self.le_widgets["tow"].setText(f"{data.get('gps_tow', 0.0):.3f}")
            self.le_widgets["dyn"].setText(str(data.get("dynamic_mode", 0)))
            st = data.get("filter_state", 0);
            self.le_widgets["state"].setText(f"{st} ({self.STATE_NAMES.get(st, 'UNK')})")
            ft = data.get("fix_type", 0);
            self.le_widgets["fix_type"].setText(f"{ft} ({self.FIX_NAMES.get(ft, 'UNK')})")
            cond = s82 & 0x03;
            self.le_widgets["cond"].setText(f"{cond} ({self.COND_NAMES.get(cond, 'UNK')})")

            # 2. 正式數值更新
            h_da = np.degrees(data.get("heading_da", 0.0))
            h_imu = np.degrees(data.get("imu_heading", 0.0))
            h_off = np.degrees(data.get("offset", 0.0))
            self.lbl_val_da.setText(f"{h_da:.2f}");
            self.lbl_val_imu.setText(f"{h_imu:.2f}");
            self.lbl_val_off.setText(f"{h_off:.2f}")

            # 3. 滾動繪圖
            self.buf_da[:-1] = self.buf_da[1:];
            self.buf_da[-1] = h_da
            self.buf_imu[:-1] = self.buf_imu[1:];
            self.buf_imu[-1] = h_imu
            self.buf_off[:-1] = self.buf_off[1:];
            self.buf_off[-1] = h_off
            self.cur_da.setData(self.buf_da);
            self.cur_imu.setData(self.buf_imu);
            self.cur_off.setData(self.buf_off)

        except Exception as e:
            logger.error(f"UI Update Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MonitorGraphWidget()
    window.show()
    sys.exit(app.exec())