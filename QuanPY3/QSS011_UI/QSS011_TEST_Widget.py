import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *
import pyqtgraph as pg
TITLE_TEXT = "QSS011_TEST"

freq_MIN = 10
freq_MAX = 1000

phase_MIN = 0
phase_MAX = 180


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super(mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.usb = connectBlock("USB Connection")
        self.getadc = QPushButton("GetADC")
        self.plot = pg.PlotWidget()
        self.main_UI()

    def main_UI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.usb.layout2())
        mainLayout.addWidget(self.getadc)
        mainLayout.addWidget(self.plot)
        #mainLayout.setRowStretch(0, 1)
        #mainLayout.setRowStretch(1, 1)
        #mainLayout.setColumnStretch(0, 1)
        #mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())

