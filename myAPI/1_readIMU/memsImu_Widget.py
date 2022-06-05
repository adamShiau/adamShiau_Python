from PyQt5.QtWidgets import *
import sys
from myLib.myGui.graph import *
from myLib.myGui.mygui_serial import *
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class memsImuWidget(QMainWindow):

    def __init__(self):
        super(memsImuWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.usb = usbConnect()
        self.start_bt = QPushButton("read")
        self.stop_bt = QPushButton("stop")
        self.save_block = dataSaveBlock("save data")
        self.buffer_lb = displayOneBlock('Buffer size')
        self.data_rate_lb = displayOneBlock('data rate')
        self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG VS MEMS [DPS]")
        self.plot2 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [g]")
        self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [g]")
        self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_WX [DPS]")
        self.plot6 = pgGraph_1(color=(255, 0, 0), title="MEMS_WY [DPS]")
        # self.pig_parameter_bt = QPushButton("parameter")
        # self.pig_parameter_bt.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.usb.layout(), 0, 0, 2, 4)
        # layout.addWidget(self.pig_parameter_bt, 0, 4, 1, 1)
        layout.addWidget(self.start_bt, 0, 5, 1, 1)
        layout.addWidget(self.stop_bt, 0, 6, 1, 1)
        layout.addWidget(self.save_block, 0, 7, 2, 3)
        layout.addWidget(self.buffer_lb, 1, 4, 1, 1)
        layout.addWidget(self.data_rate_lb, 1, 5, 1, 1)
        layout.addWidget(self.plot1, 2, 0, 5, 5)
        layout.addWidget(self.plot2, 2, 5, 1, 5)
        layout.addWidget(self.plot3, 3, 5, 1, 5)
        layout.addWidget(self.plot4, 4, 5, 1, 5)
        layout.addWidget(self.plot5, 5, 5, 1, 5)
        layout.addWidget(self.plot6, 6, 5, 1, 5)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setLayout(layout)


# class pigParameters(QGroupBox):
#     def __init__(self, parent=None):
#         super(pigParameters, self).__init__(parent)
#         self.setTitle("parameters")
#         self.wait_cnt = spinBlock(title='Wait cnt', minValue=0, maxValue=100, double=False, step=1)
#         self.avg = spinBlock(title='avg', minValue=0, maxValue=6, double=False, step=1)
#         self.err_offset = spinBlock(title='Err offset', minValue=-10000, maxValue=10000, double=False, step=1)
#         self.polarity = spinBlock(title='polarity', minValue=0, maxValue=1, double=False, step=1)
#         self.mod_H = spinBlock(title='MOD_H', minValue=-32768, maxValue=32767, double=False, step=100)
#         self.mod_L = spinBlock(title='MOD_L', minValue=-32768, maxValue=0, double=False, step=100)
#         self.gain1 = spinBlock(title='GAIN1', minValue=0, maxValue=14, double=False, step=1)
#         self.gain2 = spinBlock(title='GAIN2', minValue=0, maxValue=14, double=False, step=1)
#         self.const_step = spinBlock(title='const_step', minValue=-32768, maxValue=32767, double=False, step=1)
#         self.dac_gain = spinBlock(title='DAC_GAIN', minValue=0, maxValue=1023, double=False, step=10)
#         self.fb_on = spinBlock(title='mode(0:OPEN)', minValue=0, maxValue=2, double=False, step=1)
#         self.err_th = spinBlock(title='ERR_TH', minValue=0, maxValue=16384, double=False, step=1)
#         self.freq = spinBlockOneLabel(title='frequency', minValue=10, maxValue=1500, double=False, step=1)
#         self.SW_Q = spinBlock(title='SW_Q', minValue=1, maxValue=100000, double=False, step=1)
#         self.SW_R = spinBlock(title='SW_R', minValue=0, maxValue=100000, double=False, step=1)
#         self.HD_Q = spinBlock(title='FPGA_Q', minValue=1, maxValue=100000, double=False, step=1)
#         self.HD_R = spinBlock(title='FPGA_R', minValue=0, maxValue=100000, double=False, step=1)
#
#         mainLayout = QGridLayout()
#         mainLayout.addWidget(self.wait_cnt, 1, 10, 1, 2)
#         mainLayout.addWidget(self.avg, 1, 12, 1, 2)
#         mainLayout.addWidget(self.mod_H, 2, 10, 1, 2)
#         mainLayout.addWidget(self.mod_L, 2, 12, 1, 2)
#         mainLayout.addWidget(self.err_offset, 3, 10, 1, 2)
#         mainLayout.addWidget(self.polarity, 3, 12, 1, 2)
#         mainLayout.addWidget(self.gain1, 4, 10, 1, 2)
#         mainLayout.addWidget(self.const_step, 5, 12, 1, 2)
#         mainLayout.addWidget(self.dac_gain, 5, 10, 1, 2)
#         mainLayout.addWidget(self.gain2, 4, 12, 1, 2)
#         mainLayout.addWidget(self.fb_on, 6, 12, 1, 2)
#         mainLayout.addWidget(self.err_th, 6, 10, 1, 2)
#         mainLayout.addWidget(self.freq, 7, 10, 1, 4)
#
#         mainLayout.addWidget(self.HD_Q, 8, 10, 1, 2)
#         mainLayout.addWidget(self.HD_R, 8, 12, 1, 2)
#         mainLayout.addWidget(self.SW_Q, 9, 10, 1, 2)
#         mainLayout.addWidget(self.SW_R, 9, 12, 1, 2)
#         self.setLayout(mainLayout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = memsImuWidget()

    w.show()
    app.exec_()
