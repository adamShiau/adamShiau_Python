# main.py
import sys
import os
import logging
import logging.handlers
from datetime import datetime
import numpy as np  # 用於處理繪圖數據

# --- 1. 系統 Log 設定 (最優先執行) ---
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

# --- Imports ---
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Slot

# 引用您的 UI 元件
from pigImu_Widget import pigImuWidget
from myLib.myGui.pig_menu_manager import pig_menu_manager
from myLib.mySerial.Connector import Connector

# 引用新架構 Drivers
from drivers.hins_gnss_ins.hins_gnss_ins_reader import HinsGnssInsReader
from drivers.hins_fog_imu.hins_fog_imu_reader import HinsFogImuReader


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aegiverse HINS GUI (New Arch)")
        self.resize(1450, 800)

        # 1. 核心物件初始化
        self.connector = Connector()
        self.fog_reader = HinsFogImuReader()
        self.gnss_reader = HinsGnssInsReader()

        # 2. 建立繪圖資料緩衝區 (因為 Reader 現在是單點發送，我們需要在 UI 層累積)
        self.plot_buffer_size = 3000  # 保留最近 3000 點
        self.data_buffer = {
            "TIME": [], "WX": [], "WY": [], "WZ": [],
            "AX": [], "AY": [], "AZ": [], "ACC_TEMP": []
        }

        # 3. UI 初始化 (使用舊有的 Widget)
        self.central_widget = pigImuWidget()
        self.setCentralWidget(self.central_widget)

        # 4. 初始化 Menu (傳入 self 作為 obj)
        self.pig_menu = pig_menu_manager(self.menuBar(), self)

        # 5. 訊號連接 (整合新舊世界)
        self.connect_signals()

    def connect_signals(self):
        # USB 連線相關
        self.central_widget.usb.bt_update.clicked.connect(self.update_com_ports)
        self.central_widget.usb.bt_connect.clicked.connect(self.connect_serial)
        self.central_widget.usb.bt_disconnect.clicked.connect(self.disconnect_serial)

        # 讀取控制
        self.central_widget.read_bt.clicked.connect(self.start_reading)
        self.central_widget.stop_bt.clicked.connect(self.stop_reading)

        # --- [修正點] 將 Reader 數據導向 Main 的處理函式 ---
        self.fog_reader.data_ready_qt.connect(self.process_fog_data)

        # 顯示原始 Hex (選配，用於除錯)
        # self.fog_reader.raw_ack_qt.connect(self.debug_raw_data)

    def process_fog_data(self, new_data_dict):
        """
        核心繪圖邏輯：
        1. 接收單點數據
        2. 存入 Buffer
        3. 更新 Widget 的圖表
        """
        try:
            # 1. 將新數據 append 到緩衝區
            # new_data_dict 裡的 value 是 np.array([v])，我們取 [0]
            for key in self.data_buffer.keys():
                if key in new_data_dict:
                    val = new_data_dict[key][0]
                    self.data_buffer[key].append(val)

            # 2. 控制 Buffer 大小 (FIFO)
            if len(self.data_buffer["TIME"]) > self.plot_buffer_size:
                for key in self.data_buffer.keys():
                    self.data_buffer[key].pop(0)

            # 3. 準備繪圖數據 (轉為 list 或 numpy array)
            # 這裡必須檢查 Widget 上是否有選擇 dph 或 dps 單位
            factor = 1.0
            if hasattr(self.central_widget, 'plot1_unit_rb'):
                if self.central_widget.plot1_unit_rb.btn_status == "dph":
                    factor = 3600.0  # dps -> dph

            t = self.data_buffer["TIME"]

            # 更新 Plot 1 (Gyro)
            self.central_widget.plot1.ax1.setData(t, np.array(self.data_buffer["WX"]) * factor)
            self.central_widget.plot1.ax2.setData(t, np.array(self.data_buffer["WY"]) * factor)
            self.central_widget.plot1.ax3.setData(t, np.array(self.data_buffer["WZ"]) * factor)

            # 更新 Plot 2 (Accel & Temp)
            self.central_widget.plot2.ax1.setData(t, self.data_buffer["AX"])
            self.central_widget.plot2.ax2.setData(t, self.data_buffer["AY"])
            self.central_widget.plot2.ax3.setData(t, self.data_buffer["AZ"])
            self.central_widget.plot2.ax4.setData(t, self.data_buffer["ACC_TEMP"])

        except Exception as e:
            logger.error(f"Plotting Error: {e}")

    def update_com_ports(self):
        num, ports = self.connector.portList()
        self.central_widget.usb.addPortItems(num, ports)

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

            self.fog_reader.set_connector(self.connector)
            self.fog_reader.start()
        else:
            QMessageBox.critical(self, "Connection Error", "無法連接 Serial Port")

    def disconnect_serial(self):
        self.stop_reading()
        self.fog_reader.stop()
        self.fog_reader.wait()

        self.connector.disconnectConn()
        self.central_widget.usb.updateStatusLabel(False)
        self.central_widget.setBtnEnable(False)
        self.pig_menu.setEnable(False)

    def start_reading(self):
        # 清空舊圖表
        for key in self.data_buffer:
            self.data_buffer[key] = []

        self.fog_reader.read_imu()
        self.fog_reader.is_run = True

    def stop_reading(self):
        self.fog_reader.stop_imu()

    def debug_raw_data(self, data):
        # 除錯用：印出 Hex
        print("RAW:", " ".join([f"{b:02X}" for b in data]))

    # --- Menu Actions Stub (對應 pig_menu_manager) ---
    def show_parameters(self):
        print("Show Parameters (TODO)")

    def show_W_A_cali_parameter_menu(self):
        print("Show Calibration (TODO)")

    def show_version_menu(self):
        print("Show Version (TODO)")

    def show_configuration_menu(self):
        print("Show Configuration (TODO)")

    def show_hins_cmd_menu(self):
        print("Show HINS Config (TODO)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())