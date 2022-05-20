from PyQt5.QtWidgets import *
import sys
sys.path.append("../")
from myLib.myGui.graph import *
from myLib.myGui.serial import *
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class memsImuWidget(QMainWindow):

    def __init__(self):
        super(memsImuWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.connect_bt = QPushButton("connect")
        self.start_bt = QPushButton("read")
        self.stop_bt = QPushButton("stop")
        # self.plot1 = mplGraph_1()
        # self.plot2 = mplGraph_2()
        self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG VS MEMS [DPS]")
        self.plot2 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [g]")
        self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [g]")
        self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_WX [DPS]")
        self.plot6 = pgGraph_1(color=(255, 0, 0), title="MEMS_WY [DPS]")


        layout = QGridLayout()
        layout.addWidget(self.connect_bt, 0, 0, 1, 1)
        layout.addWidget(self.start_bt, 0, 5, 1, 1)
        layout.addWidget(self.stop_bt, 0, 7, 1, 1)
        layout.addWidget(self.plot1, 1, 0, 5, 5)
        layout.addWidget(self.plot2, 1, 5, 1, 5)
        layout.addWidget(self.plot3, 2, 5, 1, 5)
        layout.addWidget(self.plot4, 3, 5, 1, 5)
        layout.addWidget(self.plot5, 4, 5, 1, 5)
        layout.addWidget(self.plot6, 5, 5, 1, 5)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = memsImuWidget()
    w.show()
    app.exec_()

