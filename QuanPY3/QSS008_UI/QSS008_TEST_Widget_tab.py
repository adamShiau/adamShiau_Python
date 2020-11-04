import os
import sys
sys.path.append("../")
from py3lib.QuGUIclass import *

class picTabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(picTabSetting, self).__init__(parent)
        self.picTab1 = QWidget()
        self.picTab2 = QWidget()
        self.picTab3 = QWidget()
        self.picTab4 = QWidget()
        self.addTab(self.picTab1,"ERROR")
        self.addTab(self.picTab2,"1st INT")
        self.addTab(self.picTab3,"1st INT_Div")
        self.addTab(self.picTab4,"2nd INT_Div")
        self.plot = outputPlot()
        self.plot2 = outputPlot()
        self.plot3 = outputPlot()
        self.plot4 = outputPlot()
        self.picTab1UI()
        self.picTab2UI()
        self.picTab3UI()
        self.picTab4UI()

    def picTab1UI(self):
        piclayout = QVBoxLayout()
        piclayout.addWidget(self.plot)
        self.picTab1.setLayout(piclayout)

    def picTab2UI(self):
        piclayout = QVBoxLayout()
        piclayout.addWidget(self.plot2)
        self.picTab2.setLayout(piclayout)

    def picTab3UI(self):
        piclayout = QVBoxLayout()
        piclayout.addWidget(self.plot3)
        self.picTab3.setLayout(piclayout)

    def picTab4UI(self):
        piclayout = QVBoxLayout()
        piclayout.addWidget(self.plot4)
        self.picTab4.setLayout(piclayout)


# Preparation setting constant
class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.datacount = spinBlock("Total Data Number", 1024, 16384)
        self.deltaT = spinBlock("Time interval (us)",1, 100000)
        self.net = connectBlock("SSH Connection")
        self.run = QPushButton("Run")
        #self.plot = output2HPlot()
        self.pic = picTabSetting()
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.datacount.spinBlockWidget(),0,0,1,1)
        mainLayout.addWidget(self.deltaT.spinBlockWidget(),0,1,1,1)
        mainLayout.addWidget(self.run, 0,2,1,1)
        mainLayout.addWidget(self.net.connectBlockWidget(),0,3,1,1)
        #mainLayout.addWidget(self.plot, 1,0,1,4)
        mainLayout.addWidget(self.pic, 1,0,1,4)
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
