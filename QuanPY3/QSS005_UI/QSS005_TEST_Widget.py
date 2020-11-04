import os
import sys
sys.path.append("../")
from py3lib.QuGUIclass import *

# SETTING_FILEPATH = "set"
# SETTING_FILENAME = "set/setting.txt"

# Preparation setting constant
WFO_FREQUENCY_MIN = 1    #kHz
WFO_FREQUENCY_MAX = 1500 #kHz
WFO_AMP_MIN = 0     #mV
WFO_AMP_MAX = 1000  #mV
DC_AMP_MIN = 0      #mV
DC_AMP_MAX = 10000  #mV

TITLE_TEXT = "QIT TEST"

class housingKeeping(QWidget):
    def __init__(self, parent=None):
        super(housingKeeping, self).__init__(parent)
        self.net1 = IPconnectBlock("Major Connection")

        self.HK_UI()

    def HK_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.net1.layout1(),0,0,2,1)
        self.setLayout(layout)


class Waveform_Output(QWidget):
    def __init__(self, parent=None):
        super(Waveform_Output, self).__init__(parent)
        self.freq = spinBlock("Frequency (kHz)", WFO_FREQUENCY_MIN, WFO_FREQUENCY_MAX)
        self.rfamp = spinBlock("RF Amp (mV)", WFO_AMP_MIN, WFO_AMP_MAX, True, 0.1, 1)
        self.dcamp = spinBlock("DC Amp (mV)", DC_AMP_MIN, DC_AMP_MAX, True, 0.01, 2)

        self.run1_btn = QPushButton("Set")
        self.run1_btn.setEnabled(False)

        self.wfo_UI()

    def wfo_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.freq,0,0,1,1)
        layout.addWidget(self.rfamp,0,1,1,1)
        layout.addWidget(self.dcamp,1,0,1,1)
        layout.addWidget(self.run1_btn,1,1,1,1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)

        self.setLayout(layout)


class msTabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(msTabSetting, self).__init__(parent)
        self.tab1 = QWidget()

        self.addTab(self.tab1,"TEST")
        self.wf_out = Waveform_Output()
        self.Tab1_UI()

    def Tab1_UI(self):
        tab1_layout = QHBoxLayout()
        tab1_layout.addWidget(self.wf_out)
        self.tab1.setLayout(tab1_layout)


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        # self.resize(1024,768)
        # self.move(50,50)
        self.ms = msTabSetting()
        self.hk = housingKeeping()

        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.ms,0,0,1,1)
        mainLayout.addWidget(self.hk,0,1,1,1)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 7)
        mainLayout.setColumnStretch(0, 5)
        mainLayout.setColumnStretch(1, 1)
        #self.setCentralWidget(QWidget(self))
        #self.centralWidget().setLayout(mainLayout)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
