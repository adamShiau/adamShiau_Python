import os
import sys
sys.path.append("../")
from py3lib.QuGUIclass import *


# Preparation setting constant
class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.datacount = spinBlock("Total Data Number", 1024, 16384)
        self.deltaT = spinBlock("Time interval (us)",1, 100000)
        self.net = connectBlock("SSH Connection")
        self.run = QPushButton("Run")
        self.plot = output4Plot()
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.datacount.spinBlockWidget(),0,0,1,1)
        mainLayout.addWidget(self.deltaT.spinBlockWidget(),0,1,1,1)
        mainLayout.addWidget(self.run, 0,2,1,1)
        mainLayout.addWidget(self.net.connectBlockWidget(),0,3,1,1)
        mainLayout.addWidget(self.plot, 1,0,1,4)
        mainLayout.setColumnStretch(0,2)
        mainLayout.setColumnStretch(1,2)
        mainLayout.setColumnStretch(2,1)
        mainLayout.setColumnStretch(3,2)
        mainLayout.setRowStretch(0,1)
        mainLayout.setRowStretch(1,5)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
