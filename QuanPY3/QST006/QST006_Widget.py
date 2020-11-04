import os
import sys
sys.path.append("../")
from py3lib.QuGUIclass import *

# SETTING_FILEPATH = "set"
# SETTING_FILENAME = "set/setting.txt"
TITLE_TEXT = "Quantum Optics Experiment"

TIME_INTERVAL_MIN = 10 #us
TIME_INTERVAL_MAX = 40000 #us

Sampling_Time_Min = 10 #ms
Sampling_Time_Max = 100000 #ms


class TwoChRadioButton():
    def __init__(self):
        self.frame = QGroupBox("PD input channel")
        self.chBtn1 = QRadioButton("CH 0", self.frame)
        self.chBtn1.setChecked(True)  # select by default
        self.chBtn2 = QRadioButton("CH 1", self.frame)
    def RadioUI(self):
        frameLayout = QHBoxLayout()
        frameLayout.addWidget(self.chBtn1)
        frameLayout.addWidget(self.chBtn2)
        self.frame.setLayout(frameLayout)
        return self.frame

class TabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(TabSetting, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()  
        self.addTab(self.tab1,"APD optimization")
        self.addTab(self.tab2,"Photon Statics")
        self.Tab1_Init()
        self.Tab2_Init()
        
        self.Tab1_UI()
        self.Tab2_UI()

    def Tab1_Init(self):
        self.radio1 = TwoChRadioButton()
        self.Labelname = QLabel("Photon Count =")
        self.Labelname.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.countLabel = QLabel("0")
        pe = QPalette()
        pe.setColor(QPalette.WindowText,Qt.yellow)
        self.countLabel.setAutoFillBackground(True)
        pe.setColor(QPalette.Window,Qt.black)
        #pe.setColor(QPalette.Background,Qt.black)
        self.countLabel.setPalette(pe)
        self.countLabel.setAlignment(Qt.AlignCenter)
        self.countLabel.setFont(QFont("", 24, QFont.Bold))
        self.runPre = QPushButton("Run")
        self.stopPre = QPushButton("Stop")

        self.runPre.setEnabled(False)
        self.stopPre.setEnabled(False)

    def Tab1_UI(self):
        tab1_layout = QHBoxLayout()      
        tab1_layout.addWidget(self.radio1.RadioUI())
        tab1_layout.addWidget(self.Labelname)
        tab1_layout.addWidget(self.countLabel)
        tab1_layout.addWidget(self.runPre)
        tab1_layout.addWidget(self.stopPre)
        self.tab1.setLayout(tab1_layout)
    
    def Tab2_Init(self):
        self.radio2 = TwoChRadioButton()
        self.interval = spinBlock("Time Interval (us)", TIME_INTERVAL_MIN, TIME_INTERVAL_MAX)
        self.totalTime = spinBlock("Measurement Time (ms)", Sampling_Time_Min, Sampling_Time_Max)
        self.maxIndex = spinBlock("Maximum Index", 10, 255)
        self.runExp1 = QPushButton("Run")
        self.stopExp1 = QPushButton("Stop")
        self.save = QPushButton("Save")

        self.runExp1.setEnabled(False)
        self.stopExp1.setEnabled(False)
        self.save.setEnabled(False)
    
    def Tab2_UI(self):
        tab2_layout = QGridLayout()
        tab2_layout.addWidget(self.radio2.RadioUI(), 0, 0, 1, 1)
        tab2_layout.addWidget(self.interval, 0, 1, 1, 1)
        tab2_layout.addWidget(self.totalTime, 0, 2, 1, 1)
        tab2_layout.addWidget(self.maxIndex, 0, 3, 1, 1)
        tab2_layout.addWidget(self.runExp1, 1, 1, 1, 1)
        tab2_layout.addWidget(self.stopExp1, 1, 2, 1, 1)
        tab2_layout.addWidget(self.save, 1, 3, 1, 1)
        self.tab2.setLayout(tab2_layout)

class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.tabWidget = TabSetting()
        self.usbCon = connectBlock("USB Connection")
        self.plot = outputPlot()
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.tabWidget,0,0,1,1)
        mainLayout.addWidget(self.usbCon.layout1(), 0,1,1,1)
        mainLayout.addWidget(self.plot, 1,0,1,2)
        mainLayout.setColumnStretch(0, 5)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 4)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
