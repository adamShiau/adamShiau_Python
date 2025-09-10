""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import os



if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__

ExternalName_log = __name__
if os.getenv('verNum') == str(True) :
    ExternalName_log = "interface_logger"

logger = logging.getLogger(logger_name + '.' + ExternalName_log)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """


from myLib.myGui.graph import *
from myLib.myGui.mygui_serial import *
from myLib.myGui.myLabel import *
from myLib.myGui.myLineEdit import dataSaveBlock, lineEditBlock
from myLib.myGui.myCheckBox import checkBoxBlock_2, checkBoxBlock_3
from myLib.myGui.myRadioButton import radioButtonBlock_2
from myLib.myGui.AttitudeIndicator import AttitudeIndicator_view_processing


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
        self.save_block = dataSaveBlock("save data")
        self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_SP8_GP")
        self.para_block.setEnabled(False)
        # self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_G03")
        self.buffer_lb = displayOneBlock('Buffer Size')
        self.pd_temp_lb = displayOneBlock('PD Temp.')
        self.data_rate_lb = displayOneBlock('Data Rate')
        self.pitch_lb = displayOneBlock('Pitch')
        self.row_lb = displayOneBlock('Roll')
        self.yaw_lb = displayOneBlock('Yaw')

        # self.logo_lb = logo('./aegiverse_logo_bk_fix1.jpg')
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
        layout.addWidget(self.save_block, 0, 8, 1, 10)
        # layout.addWidget(self.para_block, 1, 10, 1, 3)
        layout.addWidget(self.buffer_lb, 1, 2, 1, 1)
        layout.addWidget(self.pd_temp_lb, 1, 3, 1, 1)
        layout.addWidget(self.data_rate_lb, 1, 4, 1, 1)
        # layout.addWidget(self.logo_lb, 0, 17, 2, 5)

        layout.addWidget(self.pitch_lb, 1, 5, 1, 1)
        layout.addWidget(self.row_lb, 1, 6, 1, 1)
        layout.addWidget(self.yaw_lb, 1, 7, 1, 1)

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
