from PyQt5.QtWidgets import *
import sys
sys.path.append("../")
from myLib.myGui.graph import *
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
        self.plot1 = pgGraph_1()
        self.plot2 = pgGraph_2()

        layout = QGridLayout()
        layout.addWidget(self.connect_bt, 0, 0, 1, 1)
        layout.addWidget(self.start_bt, 1, 0, 1, 1)
        layout.addWidget(self.stop_bt, 1, 1, 1, 1)
        layout.addWidget(self.plot1, 2, 0, 3, 3)
        layout.addWidget(self.plot2, 2, 3, 3, 3)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = memsImuWidget()
    w.show()
    app.exec_()

