import sys
import logging
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QGridLayout, QLineEdit, QPushButton,
                               QCheckBox, QApplication, QSpinBox)
from PySide6.QtCore import Qt, Slot

# 初始化 Logger
logger = logging.getLogger("drivers.HinsMonitor.Widget")


class MonitorGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HINS Heading Monitor - Rolling Window View")
        self.resize(1150, 850)

        # --- 數據映射定義 ---
        self.FIX_NAMES = {0: "FIX NONE", 1: "FIX DA FLOAT", 2: "FIX DA FIXED"}
        self.STATE_NAMES = {1: "Initialization", 2: "Vertical Gyro", 3: "AHRS", 4: "Full Navigation"}
        self.COND_NAMES = {1: "Stable", 2: "Converging"}

        # --- 數據緩衝區 (用於滾動繪圖) ---
        self.max_pts = 100
        self.buf_da = np.zeros(self.max_pts)
        self.buf_imu = np.zeros(self.max_pts)
        self.buf_off = np.zeros(self.max_pts)

        self.setup_ui()
        self.update_buffer_size()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        status_group = QGroupBox("MCU Monitor Status")
        grid = QGridLayout()
        grid.setSpacing(10)

        self.le_widgets = {}
        fields = [
            ("DA Fix Type:", "fix_type"), ("DA Valid Flag:", "valid"),
            ("GPS TOW (s):", "tow"), ("Dynamic Mode:", "dyn"),
            ("Filter State:", "state"), ("Filter Condition:", "cond"),
            ("Warning/Error:", "warn")
        ]

        for i, (label, key) in enumerate(fields):
            row, col = i // 4, (i % 4) * 2
            grid.addWidget(QLabel(f"<b>{label}</b>"), row, col)
            le = QLineEdit("-")
            le.setReadOnly(True)
            le.setAlignment(Qt.AlignCenter)
            le.setStyleSheet("background-color: #F8F9FA; color: #333; border: 1px solid #DDD;")
            self.le_widgets[key] = le
            if i == 6:
                grid.addWidget(le, row, col + 1, 1, 3)
            else:
                grid.addWidget(le, row, col + 1)

        status_group.setLayout(grid)
        main_layout.addWidget(status_group)

        # 控制列
        ctrl_layout = QHBoxLayout()
        self.cb_da = QCheckBox("Heading DA (Cyan)");
        self.cb_da.setChecked(True)
        self.cb_imu = QCheckBox("IMU Heading (Yellow)");
        self.cb_imu.setChecked(True)
        self.cb_off = QCheckBox("G-Heading Offset (Magenta)");
        self.cb_off.setChecked(True)

        # 連結 Checkbox 的隱藏/顯示功能
        self.cb_da.toggled.connect(lambda v: self.cur_da.setVisible(v))
        self.cb_imu.toggled.connect(lambda v: self.cur_imu.setVisible(v))
        self.cb_off.toggled.connect(lambda v: self.cur_off.setVisible(v))

        ctrl_layout.addWidget(self.cb_da);
        ctrl_layout.addWidget(self.cb_imu);
        ctrl_layout.addWidget(self.cb_off)
        ctrl_layout.addStretch()

        ctrl_layout.addWidget(QLabel("<b>Plot Points:</b>"))
        self.sb_points = QSpinBox()
        self.sb_points.setRange(10, 5000);
        self.sb_points.setValue(100);
        self.sb_points.setFixedWidth(80)
        self.sb_points.valueChanged.connect(self.update_buffer_size)
        ctrl_layout.addWidget(self.sb_points)
        main_layout.addLayout(ctrl_layout)

        # 圖表區
        self.pw = pg.PlotWidget(title="Heading Data Rolling Monitor")
        self.pw.setBackground('#000000')
        self.pw.addLegend(offset=(30, 30), brush=(40, 40, 40, 200), labelTextColor='#FFFFFF')
        self.cur_da = self.pw.plot(pen=pg.mkPen('#00FFFF', width=2), name="Heading DA")
        self.cur_imu = self.pw.plot(pen=pg.mkPen('#FFFF00', width=2), name="IMU Heading")
        self.cur_off = self.pw.plot(pen=pg.mkPen('#FF00FF', width=2), name="G-Heading Offset")
        main_layout.addWidget(self.pw)

    def update_buffer_size(self):
        self.max_pts = self.sb_points.value()
        self.buf_da = np.zeros(self.max_pts)
        self.buf_imu = np.zeros(self.max_pts)
        self.buf_off = np.zeros(self.max_pts)

    @Slot(dict)
    def update_data(self, data):
        """ 修正：這就是 main.py 找不到的方法 """
        try:
            # 1. 更新文字顯示
            fix = data.get("fix_type", 0)
            self.le_widgets["fix_type"].setText(f"{fix} ({self.FIX_NAMES.get(fix, 'UNK')})")
            self.le_widgets["tow"].setText(f"{data.get('gps_tow', 0.0):.3f}")
            self.le_widgets["dyn"].setText(str(data.get("dynamic_mode", 0)))

            state = data.get("filter_state", 0)
            self.le_widgets["state"].setText(f"{state} ({self.STATE_NAMES.get(state, 'UNK')})")

            s82 = data.get("status_82", 0)
            cond = s82 & 0x03
            self.le_widgets["cond"].setText(f"{cond} ({self.COND_NAMES.get(cond, 'UNK')})")

            # 2. 修正：DA Valid Flag 解析
            valid = data.get("valid_flag_da", 0)
            v_list = []
            if valid & (1 << 0): v_list.append("RCV1")
            if valid & (1 << 1): v_list.append("RCV2")
            if valid & (1 << 2): v_list.append("ANT_OFF")
            self.le_widgets["valid"].setText(f"{hex(valid)} ({'/'.join(v_list) if v_list else 'INV'})")

            # 3. 修正：Warning/Error 解析
            w_list = []
            if s82 & (1 << 2): w_list.append("Roll/Pitch")
            if s82 & (1 << 3): w_list.append("Heading")
            if s82 & (1 << 4): w_list.append("Position")
            if s82 & (1 << 5): w_list.append("Velocity")
            if s82 & (1 << 10): w_list.append("NoTimeSync")
            self.le_widgets["warn"].setText(", ".join(w_list) if w_list else "Stable")

            # 4. 更新繪圖數據 (Rad to Deg)
            h_da = np.degrees(data.get("heading_da", 0.0))
            h_imu = np.degrees(data.get("imu_heading", 0.0))
            h_off = np.degrees(data.get("offset", 0.0))

            self.buf_da[:-1] = self.buf_da[1:];
            self.buf_da[-1] = h_da
            self.buf_imu[:-1] = self.buf_imu[1:];
            self.buf_imu[-1] = h_imu
            self.buf_off[:-1] = self.buf_off[1:];
            self.buf_off[-1] = h_off

            self.cur_da.setData(self.buf_da)
            self.cur_imu.setData(self.buf_imu)
            self.cur_off.setData(self.buf_off)
        except Exception as e:
            logger.error(f"UI Update Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MonitorGraphWidget()
    window.show()
    sys.exit(app.exec())