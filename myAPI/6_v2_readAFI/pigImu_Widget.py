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
        self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_SP8_GP")
        # self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_G03")
        self.buffer_lb = displayOneBlock('Buffer Size')
        self.pd_temp_lb = displayOneBlock('PD Temp.')
        self.xlm_temp_lb = displayOneBlock('ADXL357 Temp.')
        self.data_rate_lb = displayOneBlock('Data Rate')
        self.logo_lb = logo('./aegiverse_logo_bk.jpg')
        self.kal_filter_rb = QRadioButton('Kalman Filter')
        self.plot1_showWz_cb = checkBoxBlock_2('Wz', 'pig', 'mems')
        # self.plot1_showWz_cb.setEnabled(False)
        self.plot1_unit_rb = radioButtonBlock_2('Unit', 'dph', 'dps')
        # self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG")
        self.plot1 = pgGraph_1(color="w", title="FOG1")
        self.plot2 = pgGraph_1(color="w", title="FOG2")
        self.plot6 = pgGraph_1(color="w", title="FOG3")
        self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [g]")
        self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [g]")
        # self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_WX [DPS]")
        # self.plot6 = pgGraph_1(color=(255, 0, 0), title="MEMS_WY [DPS]")

        layout = QGridLayout()
        layout.addWidget(self.usb.layout(), 0, 0, 1, 4)
        layout.addWidget(self.read_bt, 0, 5, 1, 1)
        layout.addWidget(self.stop_bt, 0, 6, 1, 1)
        layout.addWidget(self.save_block, 0, 10, 1, 3)
        # layout.addWidget(self.para_block, 1, 10, 1, 3)
        layout.addWidget(self.xlm_temp_lb, 1, 10, 1, 1)
        layout.addWidget(self.buffer_lb, 1, 4, 1, 1)
        layout.addWidget(self.pd_temp_lb, 1, 5, 1, 1)
        layout.addWidget(self.data_rate_lb, 1, 6, 1, 1)
        layout.addWidget(self.logo_lb, 0, 13, 2, 7)
        layout.addWidget(self.kal_filter_rb, 0, 4, 1, 1)
        layout.addWidget(self.plot1, 2, 0, 4, 10)
        layout.addWidget(self.plot1_showWz_cb, 1, 2, 1, 2)
        layout.addWidget(self.plot1_unit_rb, 1, 0, 1, 2)
        layout.addWidget(self.plot2, 6, 0, 4, 10)
        layout.addWidget(self.plot6, 10, 0, 4, 10)
        layout.addWidget(self.plot3, 2, 10, 4, 10)
        layout.addWidget(self.plot4, 6, 10, 4, 10)
        layout.addWidget(self.plot5, 10, 10, 4, 10)
        # layout.addWidget(self.plot6, 10, 10, 2, 10)

        self.setLayout(layout)

    def setBtnEnable(self, en):
        self.read_bt.setEnabled(en)
        self.stop_bt.setEnabled(en)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pigImuWidget()

    w.show()
    app.exec_()
