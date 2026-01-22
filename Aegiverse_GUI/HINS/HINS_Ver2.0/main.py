# main.py
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
# from drivers.hins_gnss_ins.hins_gnss_ins_reader import HinsGnssInsReader
# from drivers.hins_fog_imu.hins_fog_imu_reader import HinsFogImuReader
from drivers.hins_hybrid_reader import HinsHybridReader
from drivers.hins_gnss_ins.hins_config_widget import HinsConfigWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aegiverse HINS GUI (Final Stable)")
        self.resize(1450, 800)

        # 1. 核心物件初始化
        self.connector = Connector()
        self.hybrid_reader = HinsHybridReader()
        # [修改] 讓所有功能都依賴這個 Reader
        # 因為它同時擁有 write_fog_cmd (給 FOG 用) 和 write_raw (給 GNSS 用)
        self.fog_reader = self.hybrid_reader
        self.gnss_reader = self.hybrid_reader

        # self.fog_reader = HinsFogImuReader()
        # self.gnss_reader = HinsGnssInsReader()

        # 2. 建立繪圖資料緩衝區
        self.plot_buffer_size = 3000
        self.data_buffer = {
            "TIME": [], "WX": [], "WY": [], "WZ": [],
            "AX": [], "AY": [], "AZ": [], "ACC_TEMP": []
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
        # 5.1. 建立一個計時器物件
        self.plot_timer = QTimer()
        # 5.2. 設定鬧鐘響的時候要執行哪個函式
        # 這裡綁定的是 self.update_plots (負責畫圖的函式)
        self.plot_timer.timeout.connect(self.update_plots)
        # 5.3. 啟動計時器，設定間隔為 100 毫秒 (ms)
        # 1000ms = 1秒，所以 100ms = 每秒執行 10 次 (10 FPS)
        self.plot_timer.start(100)

        # 6. 訊號連接
        self.connect_signals()

    def connect_signals(self):
        self.central_widget.usb.bt_update.clicked.connect(self.update_com_ports)
        # [修復] 下拉選單選擇事件
        self.central_widget.usb.cb.currentIndexChanged.connect(self.on_port_selected)

        self.central_widget.usb.bt_connect.clicked.connect(self.connect_serial)
        self.central_widget.usb.bt_disconnect.clicked.connect(self.disconnect_serial)
        self.central_widget.read_bt.clicked.connect(self.start_reading)
        self.central_widget.stop_bt.clicked.connect(self.stop_reading)

        # 數據只進 Buffer，不直接畫圖
        self.fog_reader.data_ready_qt.connect(self.collect_fog_data)

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
        """ 定時更新畫面 (保護 UI 執行緒) """
        try:
            if not self.data_buffer["TIME"]: return

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

        except Exception as e:
            logger.error(f"Plotting Error: {e}")

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
            # self.fog_reader.set_connector(self.connector)
            # self.gnss_reader.set_connector(self.connector)

            # 同時啟動兩個 Reader (但在 Step 1 已移除 print，所以不會卡)
            # self.fog_reader.start()
            # self.gnss_reader.start()
        else:
            QMessageBox.critical(self, "Connection Error", "無法連接 Serial Port")

    def disconnect_serial(self):
        self.stop_reading()
        self.hybrid_reader.stop()
        self.hybrid_reader.wait()
        # self.fog_reader.stop()
        # self.gnss_reader.stop()
        # self.fog_reader.wait()
        # self.gnss_reader.wait()

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