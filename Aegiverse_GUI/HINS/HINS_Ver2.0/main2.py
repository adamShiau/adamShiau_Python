# main2.py
import sys
import os
import logging
import logging.handlers
from datetime import datetime
import numpy as np


# --- 1. 系統 Log 設定 ---
if not os.path.exists('./logs'):
    os.makedirs('./logs')

log_filename = f"./logs/system_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(log_filename, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Main")

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import QTimer

# 引用舊有 UI 元件
from pigImu_Widget import pigImuWidget
from myLib.myGui.pig_menu_manager import pig_menu_manager
from myLib.mySerial.Connector import Connector

# 引用舊有功能視窗
from myLib.myGui.pig_parameters_widget import pig_parameters_widget
from myLib.myGui.pig_W_A_calibration_parameter_widget import pig_calibration_widget
from myLib.myGui.pig_version_widget import VersionTable
from myLib.myGui.pig_configuration_widget import pig_configuration_widget

# 引用新架構 Drivers & Widgets
from drivers.hins_hybrid_reader import HinsHybridReader
from drivers.hins_gnss_ins.hins_config_widget import HinsConfigWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aegiverse HINS GUI (Final Stable)")
        self.resize(1450, 800)

        # 1. 核心物件初始化
        self.connector = Connector()
        self.hybrid_reader = HinsHybridReader() # 使用單一混合 Reader
        # 為了相容舊代碼邏輯，將 fog/gnss 指向同一個 reader
        self.fog_reader = self.hybrid_reader
        self.gnss_reader = self.hybrid_reader
        # self.fog_reader = HinsFogImuReader()
        # self.gnss_reader = HinsGnssInsReader()

        # 2. 建立繪圖資料緩衝區
        self.plot_buffer_size = 3000
        self.data_buffer = {
            "TIME": [], "WX": [], "WY": [], "WZ": [],
            "AX": [], "AY": [], "AZ": [], "ACC_TEMP": [],
            "PITCH": [], "ROLL": [], "YAW": [],
            "PD_TEMP_X": [], "PD_TEMP_Y": [], "PD_TEMP_Z": []
        }

        # 3. UI 初始化
        self.central_widget = pigImuWidget()
        self.setCentralWidget(self.central_widget)
        self.pig_menu = pig_menu_manager(self.menuBar(), self)

        # 4. 初始化功能子視窗
        self.pig_parameter_widget = pig_parameters_widget(self.fog_reader, "parameters_config")
        self.cali_parameter_menu = pig_calibration_widget(self.fog_reader, None, "cali_config")
        self.pig_configuration_menu = pig_configuration_widget(self.fog_reader)
        self.pig_version_menu = VersionTable()
        self.hins_config_widget = HinsConfigWidget(self.hybrid_reader)

        # 5. [安全機制] 繪圖 Timer (解決崩潰問題)
        ''' 5.1. 建立一個計時器物件 '''
        self.plot_timer = QTimer()
        ''' 5.2. 設定鬧鐘響的時候要執行哪個函式
        這裡綁定的是 self.update_plots (負責畫圖的函式) 
        '''
        self.plot_timer.timeout.connect(self.update_plots)
        ''' 5.3. 啟動計時器，設定間隔為 100 毫秒 (ms)
        1000ms = 1秒，所以 100ms = 每秒執行 10 次 (10 FPS) '''
        self.plot_timer.start(100)

        # 6. 訊號連接
        self.connect_signals()

    def connect_signals(self):
        # USB 連線相關
        self.central_widget.usb.bt_update.clicked.connect(self.update_com_ports)
        self.central_widget.usb.cb.currentIndexChanged.connect(self.on_port_selected)
        self.central_widget.usb.bt_connect.clicked.connect(self.connect_serial)
        self.central_widget.usb.bt_disconnect.clicked.connect(self.disconnect_serial)

        # 讀取控制
        self.central_widget.read_bt.clicked.connect(self.start_reading)
        self.central_widget.stop_bt.clicked.connect(self.stop_reading)

        # 數據只進 Buffer，不直接畫圖
        self.fog_reader.data_ready_qt.connect(self.collect_fog_data)

        # [新增 1] 連接圖表 Checkbox (FOG Line Chart)
        self.central_widget.plot1_lineName.cb1.clicked.connect(self.central_widget.plot1LineNameOneVisible)  # WX
        self.central_widget.plot1_lineName.cb2.clicked.connect(self.central_widget.plot1LineNameTwoVisible)  # WY
        self.central_widget.plot1_lineName.cb3.clicked.connect(self.central_widget.plot1LineNameThreeVisible)  # WZ

        # [新增 2] 連接圖表 Checkbox (XML Line Chart)
        self.central_widget.plot2_lineName.cb1.clicked.connect(self.central_widget.plot2LineNameOneVisible)  # AX
        self.central_widget.plot2_lineName.cb2.clicked.connect(self.central_widget.plot2LineNameTwoVisible)  # AY
        self.central_widget.plot2_lineName.cb3.clicked.connect(self.central_widget.plot2LineNameThreeVisible)  # AZ

        # [新增 3] 單位切換 (dph/dps) 更新標題
        self.central_widget.plot1_unit_rb.rb1.clicked.connect(self.plotTitleChanged)
        self.central_widget.plot1_unit_rb.rb2.clicked.connect(self.plotTitleChanged)

    def collect_fog_data(self, new_data_dict):
        """ 極速收集數據 (無阻塞) """
        try:
            for key in self.data_buffer.keys():
                if key in new_data_dict:
                    val = new_data_dict[key][0]
                    self.data_buffer[key].append(val)

            # 簡單的 Buffer 限制
            if len(self.data_buffer["TIME"]) > self.plot_buffer_size:
                trim = len(self.data_buffer["TIME"]) - self.plot_buffer_size
                for key in self.data_buffer.keys():
                    del self.data_buffer[key][:trim]
        except:
            pass

    def update_plots(self):
        """ 定時更新畫面 (包含圖表、Labels、姿態儀) """
        try:
            # 更新 Buffer Size Label (直接問 connector)
            if self.connector:
                buf_size = self.connector.readInputBuffer()
                self.central_widget.buffer_lb.lb.setText(str(buf_size))

            # 如果沒有數據，就不更新圖表和數值
            if not self.data_buffer["TIME"]:
                self.central_widget.data_rate_lb.lb.setText("0.0")
                return

            # ---  準備繪圖數據 ---
            factor = 3600.0 if getattr(self.central_widget, 'plot1_unit_rb', None) and \
                               self.central_widget.plot1_unit_rb.btn_status == "dph" else 1.0

            t = np.array(self.data_buffer["TIME"])
            # Gyro
            self.central_widget.plot1.ax1.setData(t, np.array(self.data_buffer["WX"]) * factor)
            self.central_widget.plot1.ax2.setData(t, np.array(self.data_buffer["WY"]) * factor)
            self.central_widget.plot1.ax3.setData(t, np.array(self.data_buffer["WZ"]) * factor)
            # Acc
            self.central_widget.plot2.ax1.setData(t, np.array(self.data_buffer["AX"]))
            self.central_widget.plot2.ax2.setData(t, np.array(self.data_buffer["AY"]))
            self.central_widget.plot2.ax3.setData(t, np.array(self.data_buffer["AZ"]))
            self.central_widget.plot2.ax4.setData(t, np.array(self.data_buffer["ACC_TEMP"]))

            # --- 計算並更新 Data Rate ---
            self.calculate_update_rate(t)

            # --- 更新數值 Label (取最後一筆) ---
            last_idx = -1
            self.central_widget.pdX_temp_lb.lb.setText(f"{self.data_buffer['PD_TEMP_X'][last_idx]:.1f}")
            self.central_widget.pdY_temp_lb.lb.setText(f"{self.data_buffer['PD_TEMP_Y'][last_idx]:.1f}")
            self.central_widget.pdZ_temp_lb.lb.setText(f"{self.data_buffer['PD_TEMP_Z'][last_idx]:.1f}")

            pitch = self.data_buffer['PITCH'][last_idx]
            roll = self.data_buffer['ROLL'][last_idx]
            yaw = self.data_buffer['YAW'][last_idx]

            self.central_widget.pitch_lb.lb.setText(f"{pitch:.2f}")
            self.central_widget.row_lb.lb.setText(f"{roll:.2f}")
            self.central_widget.yaw_lb.lb.setText(f"{yaw:.2f}")

            # --- 更新姿態儀 (Attitude Indicator) ---
            # 呼叫 pigImu_Widget 內嵌的 Att_indicator 方法
            self.central_widget.Att_indicator.pitch_flight_update_translate(pitch)
            self.central_widget.Att_indicator.roll_flight_axis_update_rotation(roll)
            self.central_widget.Att_indicator.yaw_flight_update_move(yaw)
            self.central_widget.Att_indicator.updateView()

        except Exception as e:
            # logger.error(f"Plotting Error: {e}")
            # 偶爾沒資料不需要一直噴錯，可以 pass 或印 debug
            pass

    def plotTitleChanged(self):
        """ 更新圖表標題 """
        if self.central_widget.plot1_unit_rb.btn_status == "dph":
            self.central_widget.plot1.p.setTitle('FOG　　  [unit: dph]')
        elif self.central_widget.plot1_unit_rb.btn_status == "dps":
            self.central_widget.plot1.p.setTitle('FOG　　  [unit: dps]')

    # --- 以下為標準連線邏輯  ---
    def on_port_selected(self):
        selected_port = self.central_widget.usb.selectPort()
        self.connector.portName = selected_port
        logger.info(f"Port Selected: {selected_port}")

    def update_com_ports(self):
        num, ports = self.connector.portList()
        self.central_widget.usb.addPortItems(num, ports)
        if num > 0: self.on_port_selected()

    def connect_serial(self):
        port = self.central_widget.usb.selectPort()
        baud = 230400
        logger.info(f"Connecting to {port} at {baud}...")
        if self.connector.portName != port:
            self.connector.portName = port
        self.connector.baudRate = baud

        if self.connector.connectConn():
            self.central_widget.usb.updateStatusLabel(True)
            self.central_widget.setBtnEnable(True)
            self.pig_menu.setEnable(True)

            # 設定 Connector
            self.hybrid_reader.set_connector(self.connector)
            self.hybrid_reader.start()
        else:
            QMessageBox.critical(self, "Connection Error", "無法連接 Serial Port")

    def disconnect_serial(self):
        self.stop_reading()
        self.hybrid_reader.stop()
        self.hybrid_reader.wait()

        self.connector.disconnectConn()
        self.central_widget.usb.updateStatusLabel(False)
        self.central_widget.setBtnEnable(False)
        self.pig_menu.setEnable(False)

    def start_reading(self):
        for key in self.data_buffer:
            self.data_buffer[key] = []
        self.fog_reader.read_imu()
        self.fog_reader.is_run = True

    def stop_reading(self):
        self.fog_reader.stop_imu()

    # --- Menu Actions ---
    def show_parameters(self):
        self.pig_parameter_widget.show()

    def show_W_A_cali_parameter_menu(self):
        self.cali_parameter_menu.show()

    def show_version_menu(self):
        ver_str = self.fog_reader.getVersion(2)
        self.pig_version_menu.ViewVersion(ver_str, "HINS-NEW-ARCH-01")
        self.pig_version_menu.show()

    def show_configuration_menu(self):
        self.pig_configuration_menu.show()

    def show_hins_cmd_menu(self):
        self.hins_config_widget.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())