import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *
TITLE_TEXT = "COM_Read"

class mainWidget(QWidget):
    def __init__(self, parent=None):
        super(mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.usb = connectBlock("USB Connection")
        self.read_btn = Read_btn();
        self.stop_btn = Stop_btn();
        self.com_plot = outputPlot()
        # self.test = TestGroup()
        # self.adc = Signal_Read_Group()
        # self.adc_plot = outputPlot()
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        # mainLayout.addWidget(self.test, 0,0,1,1)
        mainLayout.addWidget(self.usb.layout1(), 0,0,1,1)
        mainLayout.addWidget(self.read_btn, 1,0,1,1)
        mainLayout.addWidget(self.stop_btn, 1,1,1,1)
        mainLayout.addWidget(self.com_plot, 2,0,3,3)
        # mainLayout.setRowStretch(0, 1)
        # mainLayout.setRowStretch(1, 1)
        # mainLayout.setColumnStretch(0, 1)
        # mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)
 
class Read_btn(QWidget):
    def __init__(self, parent=None):
        super(Read_btn, self).__init__(parent)
        self.read = QPushButton("read")

        self.Read_btn_UI()

    def Read_btn_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.read, 0,0,1,1)
        self.setLayout(layout)
        
class Stop_btn(QWidget):
    def __init__(self, parent=None):
        super(Stop_btn, self).__init__(parent)
        self.stop = QPushButton("stop")

        self.Stop_btn_UI()

    def Stop_btn_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.stop, 0,0,1,1)
        self.setLayout(layout)

 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())