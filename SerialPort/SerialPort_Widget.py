import os
import sys
# import logging
sys.path.append("../")
from lib.GUIclass import *
TITLE_TEXT = "test"


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super(mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.usb = connectBlock("connect start")
        # self.test = TestGroup()
        # self.adc = Signal_Read_Group()
        self.adc_plot = outputPlot()
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        # mainLayout.addWidget(self.test, 0,0,0,2)
        mainLayout.addWidget(self.usb.layout1(), 0,0)
        # mainLayout.addWidget(self.adc, 0,1,1,1)
        mainLayout.addWidget(self.adc_plot, 1,0)
        # mainLayout.setRowStretch(0, 1)
        # mainLayout.setRowStretch(1, 1)
        # mainLayout.setColumnStretch(0, 1)
        # mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())