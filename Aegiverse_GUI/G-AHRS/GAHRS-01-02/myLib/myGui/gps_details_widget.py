"""
GPS Details Window Widget
顯示詳細的GPS信息視窗
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QGridLayout, QDialog, QTextEdit)
from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtGui import QFont, QPalette

class GpsDetailsDialog(QDialog):
    """GPS詳細信息對話框"""

    def __init__(self, parent=None):
        super(GpsDetailsDialog, self).__init__(parent)
        self.initUI()

        # 設定視窗為非模式，可以同時操作主視窗
        self.setModal(False)

    def initUI(self):
        self.setWindowTitle("GPS Details")
        self.resize(500, 400)  # 設定初始大小但允許調整
        self.setMinimumSize(400, 350)  # 設定最小尺寸

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)  # 增加間距
        main_layout.setContentsMargins(15, 15, 15, 15)  # 增加邊距

        # ==========  位置信息群組 ==========
        position_group = QGroupBox("📍 Position")
        position_layout = QGridLayout()
        position_layout.setSpacing(8)

        # 緯度
        self.lat_label = QLabel("Latitude:")
        self.lat_value = QLabel("---.------°")
        self.lat_value.setMinimumWidth(320)
        self.lat_value.setMinimumHeight(40)  # 增加高度
        self.lat_value.setStyleSheet("background-color: #f8f9fa; padding: 8px; border: 1px solid #dee2e6; font-family: monospace; font-size: 12px;")

        # 經度
        self.lon_label = QLabel("Longitude:")
        self.lon_value = QLabel("---.------°")
        self.lon_value.setMinimumWidth(320)
        self.lon_value.setMinimumHeight(40)  # 增加高度
        self.lon_value.setStyleSheet("background-color: #f8f9fa; padding: 8px; border: 1px solid #dee2e6; font-family: monospace; font-size: 12px;")

        # 海拔
        self.alt_label = QLabel("Altitude:")
        self.alt_value = QLabel("---.- m")
        self.alt_value.setMinimumWidth(200)
        self.alt_value.setStyleSheet("background-color: #f8f9fa; padding: 6px; border: 1px solid #dee2e6; font-family: monospace;")

        position_layout.addWidget(self.lat_label, 0, 0)
        position_layout.addWidget(self.lat_value, 0, 1)
        position_layout.addWidget(self.lon_label, 1, 0)
        position_layout.addWidget(self.lon_value, 1, 1)
        position_layout.addWidget(self.alt_label, 2, 0)
        position_layout.addWidget(self.alt_value, 2, 1)

        position_group.setLayout(position_layout)

        # ==========  時間信息群組 ==========
        time_group = QGroupBox("⏰ Time")
        time_layout = QGridLayout()
        time_layout.setSpacing(8)

        # UTC時間
        self.utc_label = QLabel("UTC Time:")
        self.utc_value = QLabel("----/--/-- --:--:--.---")
        self.utc_value.setMinimumWidth(200)
        self.utc_value.setStyleSheet("background-color: #f8f9fa; padding: 6px; border: 1px solid #dee2e6; font-family: monospace;")

        # MCU時間
        self.mcu_label = QLabel("MCU Time:")
        self.mcu_value = QLabel("----.--- s")
        self.mcu_value.setMinimumWidth(200)
        self.mcu_value.setStyleSheet("background-color: #f8f9fa; padding: 6px; border: 1px solid #dee2e6; font-family: monospace;")

        time_layout.addWidget(self.utc_label, 0, 0)
        time_layout.addWidget(self.utc_value, 0, 1)
        time_layout.addWidget(self.mcu_label, 1, 0)
        time_layout.addWidget(self.mcu_value, 1, 1)

        time_group.setLayout(time_layout)

        # ==========  狀態信息群組 ==========
        status_group = QGroupBox("📶 Status")
        status_layout = QGridLayout()
        status_layout.setSpacing(8)

        # GPS狀態
        self.status_label = QLabel("GPS Status:")
        self.status_value = QLabel("DISCONNECTED")
        self.status_value.setMinimumWidth(100)
        self.status_value.setStyleSheet("background-color: gray; color: white; padding: 6px; border: 1px solid #ccc; font-weight: bold; text-align: center;")

        # 狀態碼
        self.code_label = QLabel("Code:")
        self.code_value = QLabel("0x--")
        self.code_value.setMinimumWidth(80)
        self.code_value.setStyleSheet("background-color: #f8f9fa; padding: 6px; border: 1px solid #dee2e6; font-family: monospace;")

        status_layout.addWidget(self.status_label, 0, 0)
        status_layout.addWidget(self.status_value, 0, 1)
        status_layout.addWidget(self.code_label, 0, 2)
        status_layout.addWidget(self.code_value, 0, 3)

        status_group.setLayout(status_layout)

        # 添加所有群組到主布局
        main_layout.addWidget(position_group)
        main_layout.addWidget(time_group)
        main_layout.addWidget(status_group)

        self.setLayout(main_layout)

        # 設定字體 - 稍微大一點
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

    def updateGpsData(self, gps_data):
        """更新GPS數據顯示"""
        try:
            # 更新位置信息
            if 'LATITUDE' in gps_data and 'LONGITUDE' in gps_data:
                lat_text = f"{gps_data['LATITUDE']:.6f}°"
                lon_text = f"{gps_data['LONGITUDE']:.6f}°"

                # 重新創建標籤內容，確保顯示
                self.lat_value.clear()
                self.lon_value.clear()

                # 暫時移除複雜樣式，使用簡單設置
                self.lat_value.setStyleSheet("background-color: white; color: black; padding: 5px; border: 1px solid gray;")
                self.lon_value.setStyleSheet("background-color: white; color: black; padding: 5px; border: 1px solid gray;")

                # 確保足夠的寬度
                self.lat_value.setMinimumWidth(320)
                self.lon_value.setMinimumWidth(320)

                # 設置文字
                self.lat_value.setText(lat_text)
                self.lon_value.setText(lon_text)

                # 強制刷新
                self.lat_value.update()
                self.lon_value.update()

            if 'ALTITUDE' in gps_data:
                self.alt_value.setText(f"{gps_data['ALTITUDE']:.2f} m")

            # 更新時間信息
            if all(key in gps_data for key in ['UTC_YEAR', 'UTC_MONTH', 'UTC_DAY',
                                              'UTC_HOUR', 'UTC_MINUTE', 'UTC_SECOND', 'UTC_MILLISECOND']):
                utc_str = f"{gps_data['UTC_YEAR']:04d}/{gps_data['UTC_MONTH']:02d}/{gps_data['UTC_DAY']:02d} " + \
                         f"{gps_data['UTC_HOUR']:02d}:{gps_data['UTC_MINUTE']:02d}:{gps_data['UTC_SECOND']:02d}.{gps_data['UTC_MILLISECOND']:03d}"
                self.utc_value.setText(utc_str)

            if 'MCU_TIME' in gps_data:
                if isinstance(gps_data['MCU_TIME'], (int, float)):
                    self.mcu_value.setText(f"{gps_data['MCU_TIME']:.3f} s")
                else:
                    self.mcu_value.setText(f"{gps_data['MCU_TIME']} s")

            # 更新狀態信息
            if 'GPS_STATUS_NAME' in gps_data and 'GPS_STATUS_CODE' in gps_data:
                status_name = gps_data['GPS_STATUS_NAME']
                status_code = gps_data['GPS_STATUS_CODE']

                self.status_value.setText(status_name)
                self.code_value.setText(f"0x{status_code:02X}")

                # 根據狀態設定顏色
                if status_code == 0x00:  # DATA_ALL_VALID
                    self.status_value.setStyleSheet("background-color: green; color: white; padding: 5px;")
                elif status_code == 0x01:  # DATA_POS_ONLY
                    self.status_value.setStyleSheet("background-color: yellow; color: black; padding: 5px;")
                elif status_code == 0x02:  # DATA_NO_FIX
                    self.status_value.setStyleSheet("background-color: blue; color: white; padding: 5px;")
                elif status_code == 0x03:  # DATA_UNSTABLE
                    self.status_value.setStyleSheet("background-color: red; color: white; padding: 5px;")
                else:  # DATA_INVALID
                    self.status_value.setStyleSheet("background-color: darkred; color: white; padding: 5px;")


        except Exception as e:
            print(f"GPS Display Update Error: {e}")

    def resetDisplay(self):
        """重置顯示內容"""
        self.lat_value.setText("---.------°")
        self.lon_value.setText("---.------°")
        self.alt_value.setText("---.- m")
        self.utc_value.setText("----/--/-- --:--:--.---")
        self.mcu_value.setText("----.--- s")
        self.status_value.setText("DISCONNECTED")
        self.status_value.setStyleSheet("background-color: gray; color: white; padding: 6px;")
        self.code_value.setText("0x--")