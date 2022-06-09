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
        self.plot1_cb = checkBoxBlock_2('Wz', 'pig', 'mems')
        self.plot1_rb = radioButtonBlock_2('unit', 'dph', 'dps')
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
        layout.addWidget(self.plot1_cb, 2, 4, 1, 1)
        layout.addWidget(self.plot1_rb, 2, 0, 1, 1)
        layout.addWidget(self.plot2, 2, 5, 1, 5)
        layout.addWidget(self.plot3, 3, 5, 1, 5)
        layout.addWidget(self.plot4, 4, 5, 1, 5)
        layout.addWidget(self.plot5, 5, 5, 1, 5)
        layout.addWidget(self.plot6, 6, 5, 1, 5)


        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = memsImuWidget()

    w.show()
    app.exec_()
