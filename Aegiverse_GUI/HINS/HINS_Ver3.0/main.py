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
from myLib import common as cmn

# 引用 menu Widget
from drivers.hins_fog_imu.widgets.pig_parameters_widget import pig_parameters_widget
from drivers.hins_fog_imu.widgets.pig_W_A_calibration_parameter_widget import pig_calibration_widget
from drivers.hins_fog_imu.widgets.pig_version_widget import VersionTable
from drivers.hins_fog_imu.widgets.pig_configuration_widget import pig_configuration_widget
from drivers.hins_gnss_ins.widgets.hins_config_widget import HinsConfigWidget

# 引用 monitor Widget
from drivers.hins_heading_monitor.widgets.monitor_graph_widget import MonitorGraphWidget

# 引用新架構 Drivers
from drivers.hins_hybrid_reader import HinsHybridReader
from drivers.hins_fog_imu.hins_fog_imu_reader import HinsFogImuReader
from drivers.hins_gnss_ins.hins_gnss_ins_reader import HinsGnssInsReader
from drivers.hins_heading_monitor.hins_monitor_reader import HinsMonitorReader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.GUI_VERSION = "HINS_Ver2.0"
        self.setWindowTitle("Aegiverse HINS GUI")
        self.resize(1450, 800)

        # 1. 核心物件初始化
        self.connector = Connector()
        # (A) 建立總機 (Active Thread)
        self.hybrid_reader = HinsHybridReader()  # 使用單一混合 Reader
        # (B) 建立分機 (Passive Processors)
        self.fog_reader = HinsFogImuReader()
        self.gnss_reader = HinsGnssInsReader()
        self.monitor_reader = HinsMonitorReader()
        # (C) 掛載：把分機交給總機管理
        # 這一步會自動註冊 Decoder 到 Dispatcher
        self.hybrid_reader.add_device(self.fog_reader)
        self.hybrid_reader.add_device(self.gnss_reader)
        self.hybrid_reader.add_device(self.monitor_reader)

        # 資料存檔管理員 (參考 common.py)
        self.imudata_file = cmn.data_manager(fnum=0)

        # 2. 建立繪圖資料緩衝區
        self.plot_buffer_size = 1000
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
        self.monitor_win = MonitorGraphWidget()

        # 4. 初始化功能子視窗
        # 注意：使用 fog_reader 傳入，因為它才有 dump_fog_parameters 等特定指令
        self.pig_parameter_widget = pig_parameters_widget(self.fog_reader, "parameters_config")
        self.cali_parameter_menu = pig_calibration_widget(self.fog_reader, None, "cali_config")
        self.pig_configuration_menu = pig_configuration_widget(self.fog_reader)
        # 版本讀取統一走 hybrid 或 fog 都可以，因為底層都是 call connector
        self.pig_version_menu = VersionTable()
        # GNSS 設定視窗使用 gnss_reader
        self.hins_config_widget = HinsConfigWidget(self.gnss_reader)

        # 5. GUI Timer
        ''' 5.1. 建立一個計時器物件 '''
        self.gui_timer = QTimer()
        ''' 5.2. 設定鬧鐘響的時候要執行哪個函式 '''
        self.gui_timer.timeout.connect(self.update_gui_periodic)
        ''' 5.3. 啟動計時器，設定間隔為 100 毫秒 (ms)
        1000ms = 1秒，所以 100ms = 每秒執行 10 次 (10 FPS) '''
        self.gui_timer.start(100)

        # 6. 訊號連接
        self.connect_signals()

    def connect_signals(self):
        # USB 連線相關
        self.central_widget.usb.bt_update.clicked.connect(self.update_com_ports)
        self.central_widget.usb.cb.currentIndexChanged.connect(self.on_port_selected)
        self.central_widget.usb.bt_connect.clicked.connect(self.connect_serial)
        self.central_widget.usb.bt_disconnect.clicked.connect(self.disconnect_serial)

        # 點擊 Monitor 按鈕顯示監控視窗
        self.central_widget.monitor_bt.clicked.connect(self.show_monitor_window)

        # 讀取控制
        self.central_widget.read_bt.clicked.connect(self.start_reading)
        self.central_widget.stop_bt.clicked.connect(self.stop_reading)

        # 綁定 Save RadioButton 點擊事件 -> 觸發開檔/關檔
        self.central_widget.save_block.rb.clicked.connect(self.toggle_save_data)

        # --- Menu Action 連接 ---
        # 根據 pig_menu_manager.py 的 action_trigger_connect 順序:
        # fn[0]: Parameters
        # fn[1]: Calibration
        # fn[2]: Version
        # fn[3]: Configuration
        # fn[4]: HINS Config
        self.pig_menu.action_trigger_connect([
            self.show_parameters,
            self.show_W_A_cali_parameter_menu,
            self.show_version_menu,
            self.show_configuration_menu,
            self.show_hins_cmd_menu
        ])
        # -----------------------------

        # 數據流 (只進 Buffer)，數據流從 FogReader 發出的
        self.fog_reader.data_ready_qt.connect(self.collect_fog_data)

        # [新增] 數據流連接：當 Monitor 數據解析完成時，更新圖表視窗
        self.monitor_reader.data_ready_qt.connect(self.monitor_win.update_data)

        # RCS Checkbox 直接控制 FogReader 的模式
        self.central_widget.save_block.rcs_cb.clicked.connect(self.on_rcs_changed)

        # 連接圖表 Checkbox
        self.central_widget.plot1_lineName.cb1.clicked.connect(self.central_widget.plot1LineNameOneVisible)
        self.central_widget.plot1_lineName.cb2.clicked.connect(self.central_widget.plot1LineNameTwoVisible)
        self.central_widget.plot1_lineName.cb3.clicked.connect(self.central_widget.plot1LineNameThreeVisible)
        self.central_widget.plot2_lineName.cb1.clicked.connect(self.central_widget.plot2LineNameOneVisible)
        self.central_widget.plot2_lineName.cb2.clicked.connect(self.central_widget.plot2LineNameTwoVisible)
        self.central_widget.plot2_lineName.cb3.clicked.connect(self.central_widget.plot2LineNameThreeVisible)

        # 單位切換
        self.central_widget.plot1_unit_rb.rb1.clicked.connect(self.plotTitleChanged)
        self.central_widget.plot1_unit_rb.rb2.clicked.connect(self.plotTitleChanged)

    def on_rcs_changed(self):
        is_checked = self.central_widget.save_block.rcs_cb.isChecked()
        # 直接告訴 FogReader 切換模式，Main 不需要知道矩陣運算
        self.fog_reader.set_rcs_mode(is_checked)

    def show_monitor_window(self):
        if self.monitor_win:
            self.monitor_win.show()
            self.monitor_win.raise_()  # 確保視窗跳到最前面
            self.monitor_win.activateWindow()

    def collect_fog_data(self, new_data_dict):
        """ 極速收集數據 (無阻塞) """
        try:
            # --- 存檔 (Save) ---
            # 檢查 Save RadioButton 是否勾選 且 檔案已開啟
            if self.central_widget.save_block.rb.isChecked() and self.imudata_file.isOpenFile():
                # 準備要寫入的數據列表 (順序需對應 header)
                save_list = [
                    new_data_dict["TIME"],
                    new_data_dict["WX"], new_data_dict["WY"], new_data_dict["WZ"],
                    new_data_dict["AX"], new_data_dict["AY"], new_data_dict["AZ"],
                    new_data_dict["PD_TEMP_X"], new_data_dict["PD_TEMP_Y"], new_data_dict["PD_TEMP_Z"],
                    new_data_dict["ACC_TEMP"],
                    new_data_dict["PITCH"], new_data_dict["ROLL"], new_data_dict["YAW"]
                ]
                # 格式化字串 (參考舊代碼)
                fmt = "%.3f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.3f,%.3f,%.3f,%.3f,%.5f,%.5f,%.5f"
                self.imudata_file.saveData(save_list, fmt)

            # 存入繪圖 Buffer
            for key in self.data_buffer.keys():
                if key in new_data_dict:
                    val = new_data_dict[key][0]
                    self.data_buffer[key].append(val)

            if len(self.data_buffer["TIME"]) > self.plot_buffer_size:
                trim = len(self.data_buffer["TIME"]) - self.plot_buffer_size
                for key in self.data_buffer.keys():
                    del self.data_buffer[key][:trim]
        except:
            pass

    def toggle_save_data(self):
        """ 當 Save RadioButton 被點擊時觸發 """
        is_checked = self.central_widget.save_block.rb.isChecked()

        if is_checked:
            # 1. 取得檔名與副檔名
            base_name = self.central_widget.save_block.le_filename.text()
            ext = self.central_widget.save_block.le_ext.text()

            # 2. 處理檔名後綴 (如果有勾選 RCS，檔名加 _Rcs)
            if self.central_widget.save_block.rcs_cb.isChecked():
                full_name = f"{base_name}_Rcs{ext}"
            else:
                full_name = f"{base_name}{ext}"

            # 3. 開啟檔案
            self.imudata_file.name = full_name
            self.imudata_file.open(True)

            # 4. 寫入檔頭 (Header)
            if self.central_widget.save_block.rcs_cb.isChecked():
                self.imudata_file.write_line("# data rotate to sensor frame")
            self.imudata_file.write_line('time,wx,wy,wz,ax,ay,az,Tx,Ty,Tz,Tacc,pitch,roll,yaw')

            logger.info(f"Start recording to {full_name}")
        else:
            # 停止存檔 -> 關閉檔案
            self.imudata_file.close()
            logger.info("Stop recording.")

    def update_gui_periodic(self):
        """ 定時更新畫面總機 (包含圖表、Labels、姿態儀) """
        # 1. 永遠更新 Buffer Size (即使沒在讀數據，也會顯示 0 或殘留值)
        self.update_buffer_label()

        # 如果沒有數據，就不更新圖表和數值
        if not self.data_buffer["TIME"]:
            self.central_widget.data_rate_lb.lb.setText("0.0")
            return

        # 準備時間軸數據 (共用)
        t_array = np.array(self.data_buffer["TIME"])

        # 2. 更新圖表
        self.update_plots(t_array)

        # 3. 更新 Data Rate
        self.calculate_update_rate(t_array)

        # 4. 更新溫度 Label
        self.update_temp_labels()

        # 5. 更新姿態 Label 與儀表板
        self.update_att_labels()

    # --- [重構需求] 獨立的 Label 更新函式 ---

    def update_buffer_label(self):
        if self.connector:
            try:
                # 這裡使用 Connector.py 中的 readInputBuffer
                buf_size = self.connector.readInputBuffer()
                self.central_widget.buffer_lb.lb.setText(str(buf_size))
            except:
                self.central_widget.buffer_lb.lb.setText("Err")

    def calculate_update_rate(self, t_array):
        """ 計算 Data Rate (移植自 pigImu_Main.py) """
        try:
            if len(t_array) < 2: return

            # 取最近 100 點來算平均，避免計算量過大
            window = 100
            subset = t_array[-window:]
            if len(subset) < 2: return

            # 計算相鄰差
            deltas = subset[1:] - subset[:-1]
            # 過濾掉異常值 (<=0)
            deltas = deltas[deltas > 0]

            if len(deltas) > 0:
                avg_dt = np.mean(deltas)
                if avg_dt > 0:
                    rate = 1.0 / avg_dt
                    self.central_widget.data_rate_lb.lb.setText(f"{rate:.1f}")
        except:
            pass

    def update_temp_labels(self):
        """ 更新 PD Temp 和 Acc Temp """
        try:
            # 取最後一筆
            last_idx = -1
            px = self.data_buffer['PD_TEMP_X'][last_idx]
            py = self.data_buffer['PD_TEMP_Y'][last_idx]
            pz = self.data_buffer['PD_TEMP_Z'][last_idx]

            self.central_widget.pdX_temp_lb.lb.setText(f"{px:.1f}")
            self.central_widget.pdY_temp_lb.lb.setText(f"{py:.1f}")
            self.central_widget.pdZ_temp_lb.lb.setText(f"{pz:.1f}")
        except IndexError:
            pass

    def update_att_labels(self):
        """ 更新姿態角數值與動畫 """
        try:
            last_idx = -1
            pitch = self.data_buffer['PITCH'][last_idx]
            roll = self.data_buffer['ROLL'][last_idx]
            yaw = self.data_buffer['YAW'][last_idx]

            # 更新文字
            self.central_widget.pitch_lb.lb.setText(f"{pitch:.2f}")
            self.central_widget.row_lb.lb.setText(f"{roll:.2f}")
            self.central_widget.yaw_lb.lb.setText(f"{yaw:.2f}")

            # 更新動畫 (Attitude Indicator)
            self.central_widget.Att_indicator.pitch_flight_update_translate(pitch)
            self.central_widget.Att_indicator.roll_flight_axis_update_rotation(roll)
            self.central_widget.Att_indicator.yaw_flight_update_move(yaw)
            self.central_widget.Att_indicator.updateView()
        except IndexError:
            pass

    def update_plots(self, t):
        """ 更新折線圖 """
        try:
            factor = 3600.0 if getattr(self.central_widget, 'plot1_unit_rb', None) and \
                               self.central_widget.plot1_unit_rb.btn_status == "dph" else 1.0

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
            logger.error(f"Plot Error: {e}")

    def plotTitleChanged(self):
        if self.central_widget.plot1_unit_rb.btn_status == "dph":
            self.central_widget.plot1.p.setTitle('FOG　　  [unit: dph]')
        elif self.central_widget.plot1_unit_rb.btn_status == "dps":
            self.central_widget.plot1.p.setTitle('FOG　　  [unit: dps]')

    # --- 連線與控制邏輯 (修正 Start/Stop Bug) ---

    def on_port_selected(self):
        selected_port = self.central_widget.usb.selectPort()
        self.connector.portName = selected_port
        logger.info(f"Port Selected: {selected_port}")

    def update_com_ports(self):
        num, ports = self.connector.portList()
        self.central_widget.usb.addPortItems(num, ports)
        if num > 0: self.on_port_selected()

        # main.py

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

            # --- [關鍵修正開始] ---
            # 1. 設定 connector 給 hybrid (總機)
            self.hybrid_reader.set_connector(self.connector)

            # 2. [新增] 明確設定 connector 給分機 (GNSS Reader)
            # 這會觸發 HinsGnssInsReader 內的 flushInputBuffer，清除殘留垃圾
            self.gnss_reader.set_connector(self.connector)

            # 3. [建議] 雖然 fog_reader 沒用到，但也同步更新比較保險
            self.fog_reader.set_connector(self.connector)
            # --- [關鍵修正結束] ---

            self.hybrid_reader.start()  # 啟動執行緒
        else:
            QMessageBox.critical(self, "Connection Error", "無法連接 Serial Port")

    def disconnect_serial(self):
        self.stop_reading()

        # --- 若正在存檔，強制關閉 ---
        if self.central_widget.save_block.rb.isChecked():
            self.central_widget.save_block.rb.setChecked(False)  # 取消 UI 勾選
            self.toggle_save_data()  # 觸發關檔邏輯

        self.hybrid_reader.stop()  # 這裡會把 is_run 設為 False
        self.hybrid_reader.wait()  # 等待執行緒完全結束

        self.connector.disconnectConn()
        self.central_widget.usb.updateStatusLabel(False)
        self.central_widget.setBtnEnable(False)
        self.pig_menu.setEnable(False)

    def start_reading(self):
        # 1. 清空 UI 繪圖 Buffer (清除舊圖)
        for key in self.data_buffer:
            self.data_buffer[key] = []

        # 2. 啟動總機 Thread
        self.hybrid_reader.is_run = True
        if not self.hybrid_reader.isRunning():
            logger.info("Restarting Hybrid Reader Thread...")
            self.hybrid_reader.start()

        # 3. 清空緩衝 (總機會幫大家清空 decoder)
        self.hybrid_reader.flush_buffers()

        # 4. 發送讀取指令 (透過 FogReader 封裝好的方法)
        self.fog_reader.read_imu()

    def stop_reading(self):
        # 透過 FogReader 發送停止
        self.fog_reader.stop_imu()
        self.hybrid_reader.stop()
        self.hybrid_reader.wait()

    # --- Menu Actions ---
    def show_parameters(self):
        self.pig_parameter_widget.show()

    def show_W_A_cali_parameter_menu(self):
        self.cali_parameter_menu.show()

    def show_version_menu(self):
        ver_str = self.fog_reader.getVersion(2)
        self.pig_version_menu.ViewVersion(ver_str, self.GUI_VERSION)
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