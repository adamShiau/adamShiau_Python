import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *
TITLE_TEXT = "GRC ElectroChemical Analysis"

StartV_MIN = -300
StartV_MAX = 3000

DV_MIN = 10
DV_MAX = 1000

EndV_MIN = -300
EndV_MAX = 3000

DT_MIN = 10
DT_MAX = 300000

RATE_MIN = 10
RATE_MAX = 100

Q_TIME_MIN = 0
Q_TIME_MAX = 10


class CVMethod(QWidget):
    def __init__(self, parent=None):
        super(CVMethod, self).__init__(parent)
        self.startV = spinBlock("Start Potential (mV)", StartV_MIN, StartV_MAX)
        self.dv = spinBlock("Delta Potential (mV)", DV_MIN, DV_MAX)
        self.endV = spinBlock("End Potential (mV)", EndV_MIN, EndV_MAX)
        self.dt = spinBlock("Amp. gain (us)", DT_MIN, DT_MAX)
        self.rate = spinBlock("Sampling Rate (Hz)", RATE_MIN, RATE_MAX)
        self.quiet = spinBlock("Quiet Time (s)", Q_TIME_MIN, Q_TIME_MAX)
        self.quiet_left = QLabel("Quiet Time Left : 0")
        self.start = QPushButton("Start")
        self.stop = QPushButton("Stop")
        self.save = QPushButton("Save")
        self.start.setEnabled(False)
        self.stop.setEnabled(False)
        self.save.setEnabled(False)
        self.CV_UI()
        self.startV.spin.valueChanged.connect(lambda:self.update_endV())
        self.endV.spin.valueChanged.connect(lambda:self.update_startV())

    def CV_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.startV, 0,0,1,1)
        layout.addWidget(self.dv, 0,1,1,1)
        layout.addWidget(self.endV, 0,2,1,1)
        layout.addWidget(self.dt, 0,3,1,1)
        layout.addWidget(self.rate, 0,4,1,1)
        layout.addWidget(self.quiet, 1,0,1,1)
        layout.addWidget(self.quiet_left, 1,1,1,1)
        layout.addWidget(self.start, 1,2,1,1)
        layout.addWidget(self.stop, 1,3,1,1)
        layout.addWidget(self.save, 1,4,1,1)
        self.setLayout(layout)

    def update_endV(self):
        startV = self.startV.spin.value()
        #print startV
        self.endV.spin.setRange(startV, EndV_MAX)

    def update_startV(self):
        endV = self.endV.spin.value()
        #print endV
        self.startV.spin.setRange(StartV_MIN, endV)

class ITMethod(QWidget):
    def __init__(self, parent=None):
        super(ITMethod, self).__init__(parent)
        self.setV = spinBlock("Fixed Potential (mV)", StartV_MIN, StartV_MAX)
        self.dt = spinBlock("Amp. gain (us)", DT_MIN, DT_MAX)
        self.rate = spinBlock("Sampling Rate (Hz)", RATE_MIN, RATE_MAX)
        self.quiet = spinBlock("Quiet Time (s)", Q_TIME_MIN, Q_TIME_MAX)
        self.quiet_left = QLabel("Quiet Time Left : 0")
        self.start = QPushButton("Start")
        self.stop = QPushButton("Stop")
        self.save = QPushButton("Save")
        self.start.setEnabled(False)
        self.stop.setEnabled(False)
        self.save.setEnabled(False)
        self.IT_UI()

    def IT_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.setV, 0,0,1,1)
        layout.addWidget(self.dt, 0,1,1,1)
        layout.addWidget(self.rate, 0,2,1,1)
        layout.addWidget(self.quiet, 0,3,1,1)
        layout.addWidget(self.quiet_left, 1,0,1,1)
        layout.addWidget(self.start, 1,1,1,1)
        layout.addWidget(self.stop, 1,2,1,1)
        layout.addWidget(self.save, 1,3,1,1)
        self.setLayout(layout)


class TabAll(QTabWidget):
    def __init__(self, parent=None):
        super(TabAll, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.CV = CVMethod()
        self.IT = ITMethod()
        self.addTab(self.tab1,"Cyclic Voltammetry")
        self.addTab(self.tab2,"Amerometry")
        self.Tab1_UI()
        self.Tab2_UI()

    def Tab1_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.CV)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.IT)
        self.tab2.setLayout(layout)


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.usb = connectBlock("USB Connection")
        self.header = editBlock("File Header")
        self.plot = output3Plot()
        self.taball = TabAll()
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.taball, 0,0,2,1)
        mainLayout.addWidget(self.usb.layout1(), 0,1,1,1)
        mainLayout.addWidget(self.header, 1,1,1,1)
        mainLayout.addWidget(self.plot, 2,0,1,2)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 10)
        mainLayout.setColumnStretch(0, 5)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
