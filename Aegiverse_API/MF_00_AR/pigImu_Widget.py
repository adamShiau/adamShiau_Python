""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

from PyQt5.QtWidgets import *
import sys
from myLib.myGui.graph import *
from myLib.myGui.mygui_serial import *
from myLib.myGui.myLabel import *
from myLib.myGui.myLineEdit import *
from myLib.myGui.myCheckBox import *
from myLib.myGui.myRadioButton import *
from myLib.myGui.myComboBox import *
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


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
        self.save_block.rb.setEnabled(False)
        self.save_block.le_filename.setEnabled(False)
        self.save_block.le_ext.setEnabled(False)
        self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_SP8_GP")
        self.para_block.setEnabled(False)
        # self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_G03")
        self.buffer_lb = displayOneBlock('Buffer Size')
        self.pd_temp_lb = displayOneBlock('PD Temp Z-Axis.')
        self.pdX_temp_lb = displayOneBlock('PD Temp X-Axis.')
        self.pdY_temp_lb = displayOneBlock('PD Temp Y-Axis.')
        self.data_rate_lb = displayOneBlock('Data Rate')
        self.logo_lb = logo('./aegiverse_logo_bk.jpg')
        self.kal_filter_rb = QRadioButton('Kalman Filter')
        # self.kal_filter_rb.setChecked(True)
        self.plot1_showWz_cb = checkBoxBlock_2('Wz', 'pig', 'mems')
        self.plot1_showWz_cb.setEnabled(False)
        self.plot1_unit_rb = radioButtonBlock_2('Unit', 'dph', 'dps')

        # title="FOG_WX：White，FOG_WZ：Red，FOG_WY：Blue　　  [unit: DPH]"
        self.plot1 = pgGraph_1_3(color1="w", color2="r", color3="y",linename1="WX", linename2="WY", linename3="WZ", title="FOG　　  [unit: dph]")
        # self.plot2 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        # self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [g]")
        # self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [g]")
        # self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_WX [DPS]")
        # self.plot6 = pgGraph_1(color=(255, 0, 0), title="MEMS_WY [DPS]")
        # title="MEMS_AX：White，MEMS_AY：Red，MEMS_AZ：Blue      [unit: g]"
        self.plot7 = pgGraph_1_3(color1="w", color2="r", color3="y", linename1="AX", linename2="AY", linename3="AZ", title="XML      [unit: m/s²]")
        self.plot1_lineName = checkBoxBlock_3("FOG Line Chart", "WX (White)", "WY (Red)", "WZ (Yellow)")
        self.plot7_lineName = checkBoxBlock_3("XML Line Chart", "AX (White)", "AY (Red)", "AZ (Yellow)")
        self.saveDumpCb = selectSaveCheckBox()
        self.saveDumpCb.DumpCb_Z.setEnabled(False)
        self.saveDumpCb.DumpCb_X.setEnabled(False)
        self.saveDumpCb.DumpCb_Y.setEnabled(False)

        self.pitch_lb = displayOneBlock("Pitch")
        self.row_lb = displayOneBlock("Row                                ")
        self.yaw_lb = displayOneBlock("Yaw                                ")


        layout = QGridLayout()
        layout.addWidget(self.usb.layout(), 0, 0, 1, 4)
        layout.addWidget(self.read_bt, 0, 5, 1, 1)
        layout.addWidget(self.stop_bt, 0, 6, 1, 1)
        layout.addWidget(self.saveDumpCb, 0, 7, 1, 1)
        layout.addWidget(self.save_block, 0, 8, 2, 4)
        #layout.addWidget(self.para_block, 1, 10, 1, 3)
        # layout.addWidget(self.buffer_lb, 1, 4, 1, 1)
        # layout.addWidget(self.pd_temp_lb, 1, 5, 1, 1)
        # layout.addWidget(self.data_rate_lb, 1, 6, 1, 2)
        layout.addWidget(self.buffer_lb, 1, 4, 1, 2)
        layout.addWidget(self.pd_temp_lb, 2, 0, 1, 2)
        layout.addWidget(self.data_rate_lb, 1, 6, 1, 2)
        layout.addWidget(self.logo_lb, 0, 13, 3, 7)
        layout.addWidget(self.kal_filter_rb, 0, 4, 1, 1)
        layout.addWidget(self.plot1, 3, 1, 5, 19)
        layout.addWidget(self.plot1_showWz_cb, 1, 2, 1, 2)
        layout.addWidget(self.plot1_unit_rb, 1, 0, 1, 2)
        # layout.addWidget(self.plot2, 2, 10, 3, 10)
        # layout.addWidget(self.plot3, 5, 10, 3, 10)
        # layout.addWidget(self.plot4, 8, 10, 3, 10)
        layout.addWidget(self.plot7, 8, 1, 5, 19)
        #layout.addWidget(self.plot5, 8, 10, 2, 10)
        #layout.addWidget(self.plot6, 10, 10, 2, 10)
        layout.addWidget(self.plot1_lineName, 3, 0, 5, 1)
        layout.addWidget(self.plot7_lineName, 8, 0, 5, 1)
        layout.addWidget(self.pdX_temp_lb, 2, 2, 1, 2)
        layout.addWidget(self.pdY_temp_lb, 2, 4, 1, 2)
        layout.addWidget(self.pitch_lb, 2, 6, 1, 2)
        layout.addWidget(self.row_lb, 2, 8, 1, 2)
        layout.addWidget(self.yaw_lb, 2, 10, 1, 2)

        self.setLayout(layout)

    def setBtnEnable(self, en):
        self.read_bt.setEnabled(en)
        self.stop_bt.setEnabled(en)
        self.save_block.rb.setEnabled(en)
        self.save_block.le_filename.setEnabled(en)
        # 控制AFI的下dump(save)
        self.saveDumpCb.DumpCb_Z.setEnabled(en)
        self.saveDumpCb.DumpCb_X.setEnabled(en)
        self.saveDumpCb.DumpCb_Y.setEnabled(en)

    def plot1LineNameOneVisible(self):
        if self.plot1_lineName.cb1.isChecked():
            self.plot1.ax1.setVisible(True)
        elif self.plot1_lineName.cb1.isChecked() == False:
            self.plot1.ax1.setVisible(False)

    def plot1LineNameTwoVisible(self):
        if self.plot1_lineName.cb2.isChecked():
            self.plot1.ax2.setVisible(True)
        elif self.plot1_lineName.cb2.isChecked() == False:
            self.plot1.ax2.setVisible(False)

    def plot1LineNameThreeVisible(self):
        if self.plot1_lineName.cb3.isChecked():
            self.plot1.ax3.setVisible(True)
        elif self.plot1_lineName.cb3.isChecked() == False:
            self.plot1.ax3.setVisible(False)

    def plot7LineNameOneVisible(self):
        if self.plot7_lineName.cb1.isChecked():
            self.plot7.ax1.setVisible(True)
        elif self.plot7_lineName.cb1.isChecked() == False:
            self.plot7.ax1.setVisible(False)

    def plot7LineNameTwoVisible(self):
        if self.plot7_lineName.cb2.isChecked():
            self.plot7.ax2.setVisible(True)
        elif self.plot7_lineName.cb2.isChecked() == False:
            self.plot7.ax2.setVisible(False)

    def plot7LineNameThreeVisible(self):
        if self.plot7_lineName.cb3.isChecked():
            self.plot7.ax3.setVisible(True)
        elif self.plot7_lineName.cb3.isChecked() == False:
            self.plot7.ax3.setVisible(False)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pigImuWidget()

    w.show()
    app.exec_()
