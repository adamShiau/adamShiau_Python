""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import os
from myLib.logProcess import logProcess


if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """


from PySide6.QtWidgets import QWidget, QPushButton, QRadioButton, QGridLayout

from myLib.myGui.graph import *
from myLib.myGui.mygui_serial import *
from myLib.myGui.myLabel import *
from myLib.myGui.myLineEdit import dataSaveBlock_Rcs, lineEditBlock, btnLineEditBlock, compensateBlock
from myLib.myGui.myCheckBox import checkBoxBlock_2, checkBoxBlock_3
from myLib.myGui.myRadioButton import radioButtonBlock_2
from myLib.myGui.AttitudeIndicator import AttitudeIndicator_view_processing
from myLib.myGui.gps_details_widget import GpsDetailsDialog


class pigImuWidget(QWidget):

    def __init__(self):
        super(pigImuWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.usb = usbConnect()
        self.read_bt = QPushButton("read")
        self.read_bt.setEnabled(False)
        self.stop_bt = QPushButton("stop")
        self.stop_bt.setEnabled(False)
        self.save_block = dataSaveBlock_Rcs("save data")
        self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_SP8_GP")
        self.para_block.setEnabled(False)
        self.buffer_lb = displayOneBlock('Buffer Size')
        self.pd_temp_lb = displayOneBlock('PD Temp.')
        self.data_rate_lb = displayOneBlock('Data Rate')
        self.pitch_lb = displayOneBlock('Pitch')
        self.row_lb = displayOneBlock('Roll')
        self.yaw_lb = displayOneBlock('Yaw')
        self.gnss_status_lb = displayOneBlock('GNSS')
        # 設定 GNSS 初始狀態
        self.gnss_status_lb.lb.setText('INIT')
        self.gnss_status_lb.lb.setStyleSheet("background-color: gray; color: white;")

        # GPS Details 按鈕
        self.gps_details_bt = QPushButton("GPS Details")
        self.gps_details_bt.setEnabled(False)
        self.gps_details_bt.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        # GPS Details 視窗實例 (初始為 None)
        self.gps_details_window = None

        # 連接 GPS Details 按鈕點擊事件
        self.gps_details_bt.clicked.connect(self.openGpsDetailsWindow)

        self.compensate_block = compensateBlock("compensate", "Auto-comp.", "time(s)：")

        self.logo_lb = logo('./aegiverse_logo_bk_fix1.jpg')
        self.kal_filter_rb = QRadioButton('Kalman Filter')
        self.kal_filter_rb.setAutoExclusive(False)
        self.kal_filter_rb.setChecked(False)
        self.kal_filter_rb.setDisabled(True)
        self.plot1_showWz_cb = checkBoxBlock_2('Wz', 'pig', 'mems')
        self.plot1_showWz_cb.setEnabled(False)
        self.plot1_unit_rb = radioButtonBlock_2('Unit', 'dph', 'dps')
        # self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG [DPS]")
        # self.plot2 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [m/s²]")
        # self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [m/s²]")
        # self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [m/s²]")
        # self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_WX [DPS]")
        # self.plot6 = pgGraph_1(color=(255, 0, 0), title="MEMS_WY [DPS]")

        self.plot1_lineName = checkBoxBlock_3("GYRO", "X (White)", "Y (red)", "Z (Yellow)")
        self.plot2_lineName = checkBoxBlock_3("ACCL", "X (White)", "Y (red)", "Z (Yellow)")
        self.plot1 = pgGraph_1_3(color1="w", color2="r", color3="y", linename1="WX", linename2="WY", linename3="WZ", title="GYRO  [dph]")
        self.plot2 = pgGraph_1_3(color1="w", color2="r", color3="y", linename1="AX", linename2="AY", linename3="AZ", title="ACCL  [m/s²]")

        # 顯示姿態的介面
        self.Att_indicator = AttitudeIndicator_view_processing()

        layout = QGridLayout()
        layout.addWidget(self.usb.layout(), 0, 0, 1, 5)
        layout.addWidget(self.read_bt, 0, 6, 1, 1)
        layout.addWidget(self.stop_bt, 0, 7, 1, 1)
        layout.addWidget(self.save_block, 0, 8, 1, 7)
        # layout.addWidget(self.para_block, 1, 10, 1, 3)
        layout.addWidget(self.buffer_lb, 1, 2, 1, 1)
        layout.addWidget(self.pd_temp_lb, 1, 3, 1, 1)
        layout.addWidget(self.data_rate_lb, 1, 4, 1, 1)
        layout.addWidget(self.logo_lb, 0, 17, 2, 5)

        layout.addWidget(self.pitch_lb, 1, 5, 1, 1)
        layout.addWidget(self.row_lb, 1, 6, 1, 1)
        layout.addWidget(self.yaw_lb, 1, 7, 1, 1)
        layout.addWidget(self.gnss_status_lb, 1, 8, 1, 1)  # YAW 右邊
        layout.addWidget(self.gps_details_bt, 1, 9, 1, 1)  # GPS Details 按鈕移到第1行，GNSS狀態旁邊
        layout.addWidget(self.compensate_block, 1, 10, 1, 5)  # compensate_block 往右移一格

        layout.addWidget(self.kal_filter_rb, 0, 5, 1, 1)
        # layout.addWidget(self.plot1, 4, 0, 8, 10)
        # layout.addWidget(self.plot1_showWz_cb, 1, 2, 1, 2)
        layout.addWidget(self.plot1_unit_rb, 1, 0, 1, 2)
        # layout.addWidget(self.plot2, 2, 10, 2, 10)
        # layout.addWidget(self.plot3, 4, 10, 2, 10)
        # layout.addWidget(self.plot4, 6, 10, 2, 10)
        # layout.addWidget(self.plot5, 8, 10, 2, 10)
        # layout.addWidget(self.plot6, 10, 10, 2, 10)
        layout.addWidget(self.plot1_lineName, 2, 0, 5, 2)
        layout.addWidget(self.plot2_lineName, 7, 0, 5, 2)
        layout.addWidget(self.plot1, 2, 2, 5, 15)
        layout.addWidget(self.plot2, 7, 2, 5, 15)
        layout.addWidget(self.Att_indicator, 2, 17, 10, 5)

        self.setLayout(layout)

    def setBtnEnable(self, en):
        self.read_bt.setEnabled(en)
        self.stop_bt.setEnabled(en)
        self.kal_filter_rb.setDisabled(not en)
        self.compensate_block.bt.setEnabled(en)
        self.gps_details_bt.setEnabled(en)  # GPS Details 按鈕也跟隨連接狀態

    # 當執行自動補償的功能，就不能使用read與stop的功能按鈕
    def setRunAutoCompBtnEnable(self, en):
        self.read_bt.setEnabled(not en)
        self.stop_bt.setEnabled(not en)

    # 當執行read時，就不能執行自動補償功能
    def setAutoCompBtnEnable(self, en):
        self.compensate_block.bt.setEnabled(not en)

    def updateGnssStatus(self, status_code, status_name):
        """更新 GNSS 狀態顯示"""
        # 根據狀態碼設定顯示文字和顏色
        if status_code == 0x00:  # DATA_ALL_VALID
            display_text = "VALID"
            color = "background-color: green; color: white;"
        elif status_code == 0x01:  # DATA_POS_ONLY
            display_text = "POS"
            color = "background-color: yellow; color: black;"
        elif status_code == 0x02:  # DATA_NO_FIX
            display_text = "NO FIX"
            color = "background-color: blue; color: white;"
        elif status_code == 0x03:  # DATA_UNSTABLE
            display_text = "UNSTABLE"
            color = "background-color: red; color: white;"
        else:  # DATA_INVALID
            display_text = "INVALID"
            color = "background-color: darkred; color: white;"

        self.gnss_status_lb.lb.setText(display_text)
        self.gnss_status_lb.lb.setStyleSheet(color)

    def openGpsDetailsWindow(self):
        """開啟 GPS 詳細信息視窗"""
        try:
            if self.gps_details_window is None:
                # 創建新的GPS視窗
                self.gps_details_window = GpsDetailsDialog(self)

            # 顯示視窗 (非模式視窗，可以同時操作主視窗)
            self.gps_details_window.show()
            self.gps_details_window.raise_()  # 將視窗帶到前面
            self.gps_details_window.activateWindow()  # 激活視窗

        except Exception as e:
            print(f"Error opening GPS Details window: {e}")

    def updateGpsDetails(self, gps_data):
        """更新 GPS 詳細信息視窗的數據"""
        try:
            # 只有當GPS視窗開啟時才更新
            if self.gps_details_window is not None and self.gps_details_window.isVisible():
                self.gps_details_window.updateGpsData(gps_data)
        except Exception as e:
            print(f"Error updating GPS details: {e}")

    def closeGpsDetailsWindow(self):
        """關閉 GPS 詳細信息視窗"""
        try:
            if self.gps_details_window is not None:
                self.gps_details_window.close()
                self.gps_details_window = None
        except Exception as e:
            print(f"Error closing GPS details window: {e}")

    def plotLineWXVisible(self):
        if self.plot1_lineName.cb1.isChecked():
            self.plot1.ax1.setVisible(True)
        if self.plot1_lineName.cb1.isChecked() == False:
            self.plot1.ax1.setVisible(False)


    def plotLineWYVisible(self):
        if self.plot1_lineName.cb2.isChecked():
            self.plot1.ax2.setVisible(True)
        if self.plot1_lineName.cb2.isChecked() == False:
            self.plot1.ax2.setVisible(False)


    def plotLineWZVisible(self):
        if self.plot1_lineName.cb3.isChecked():
            self.plot1.ax3.setVisible(True)
        if self.plot1_lineName.cb3.isChecked() == False:
            self.plot1.ax3.setVisible(False)


    def plotLineAXVisible(self):
        if self.plot2_lineName.cb1.isChecked():
            self.plot2.ax1.setVisible(True)
        if self.plot2_lineName.cb1.isChecked() == False:
            self.plot2.ax1.setVisible(False)


    def plotLineAYVisible(self):
        if self.plot2_lineName.cb2.isChecked():
            self.plot2.ax2.setVisible(True)
        if self.plot2_lineName.cb2.isChecked() == False:
            self.plot2.ax2.setVisible(False)


    def plotLineAZVisible(self):
        if self.plot2_lineName.cb3.isChecked():
            self.plot2.ax3.setVisible(True)
        if self.plot2_lineName.cb3.isChecked() == False:
            self.plot2.ax3.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pigImuWidget()

    w.show()
    app.exec_()
