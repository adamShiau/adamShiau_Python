import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *

StartVoltage_MIN = 500
StartVoltage_MAX = 1666

VoltageStep_MIN = 200
VoltageStep_MAX = 2000

Scan_Loop_MIN = 1
Scan_Loop_MAX = 2000

Backward_MIN = 0
Backward_MAX = 50

OFFSET_MIN = -3000
OFFSET_MAX = 3000

Run_Loop_MIN = 1
Run_Loop_MAX = 1000

Delay_Time_MIN = 1
Delay_Time_MAX = 1000

Filter_MIN = 1
Filter_MAX = 1000
Filter_Const = 425

DC_Voltage1_MIN = 0
DC_Voltage1_MAX = 1666

DC_Voltage2_MIN = 0
DC_Voltage2_MAX = 4166

Fan_Speed_MIN = 0
Fan_Speed_MAX = 5000

AVG_time_MIN = 1
AVG_time_MAX = 100

Threshold_MIN = -10*1000
Threshold_MAX = 10*1000

Noise_MIN = 1
Noise_MAX = 100

MASS_CENTER_MIN = 0
MASS_CENTER_MAX = 1000
MASS_RANGE_MIN = 0.1
MASS_RANGE_MAX = 100
MASS_RANGE_STEP = 0.1

FONTSIZE = 16

TITLE_TEXT = " Acdemic Sincica GRC Ion Mobility "
LOGO_FILENAME = "set/logo.png"


class Data_Analysis_Group(QGroupBox):
    def __init__(self, parent=None):
        super(Data_Analysis_Group, self).__init__(parent)
        self.setTitle("Data Analysis")
        self.Threshold = spinBlock("Threshold (mV)", Threshold_MIN, Threshold_MAX)
        self.Width = spinBlock("Width (points)", Noise_MIN, Noise_MAX)
        self.LoadBtn = QPushButton("Load Old Data")
        self.CurrBtn = QPushButton("Use Current Data")
        self.AnaBtn = QPushButton("Peak Analysis")
        self.SaveBtn = QPushButton("Save Result")

        self.CurrBtn.setEnabled(False)
        self.AnaBtn.setEnabled(False)
        self.SaveBtn.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.Threshold,0,0,1,1)
        layout.addWidget(self.Width,0,1,1,1)
        layout.addWidget(self.LoadBtn,1,0,1,1)
        layout.addWidget(self.CurrBtn,1,1,1,1)
        layout.addWidget(self.AnaBtn,2,0,1,1)
        layout.addWidget(self.SaveBtn,2,1,1,1)
        self.setLayout(layout)

class Xic_Group(QGroupBox):
    def __init__(self, parent=None):
        super(Xic_Group, self).__init__(parent)
        self.setTitle("Tic / Xic")
        self.xicMassCenter = spinBlock("Xic Mass Center", MASS_CENTER_MIN, MASS_CENTER_MAX)
        self.xicMassRange = spinBlock("Xic Mass Range", MASS_RANGE_MIN, MASS_RANGE_MAX, True, MASS_RANGE_STEP)
        self.xicThreshold = spinBlock("Xic Threshold (mV)", Threshold_MIN, Threshold_MAX)
        self.xicWidth = spinBlock("Xic Width (points)", Noise_MIN, Noise_MAX)

        layout = QGridLayout()
        layout.addWidget(self.xicMassCenter,0,0,1,1)
        layout.addWidget(self.xicMassRange,0,1,1,1)
        layout.addWidget(self.xicThreshold,1,0,1,1)
        layout.addWidget(self.xicWidth,1,1,1,1)
        self.setLayout(layout)

class Data_Sampling_Group(QGroupBox):
    def __init__(self, parent=None):
        super(Data_Sampling_Group, self).__init__(parent)
        self.setTitle("Data Sampling")
        self.frame = QGroupBox("Polarity")
        self.poBtn1 = QRadioButton("Positive", self.frame)
        self.poBtn1.setChecked(True)  # select by default
        self.poBtn2 = QRadioButton("Negative", self.frame)
        self.AVG_time = spinBlock("Average Times", AVG_time_MIN, AVG_time_MAX, False, 1)

        frameLayout = QHBoxLayout()
        frameLayout.addWidget(self.poBtn1)
        frameLayout.addWidget(self.poBtn2)
        self.frame.setLayout(frameLayout)

        layout = QGridLayout()
        layout.addWidget(self.frame,0,0,1,1)
        layout.addWidget(self.AVG_time,0,1,1,1)
        #layout.addWidget(self.frame3,2,0,1,1)
        self.setLayout(layout)


class Signal_Read_Group(QGroupBox):
    def __init__(self, parent=None):
        super(Signal_Read_Group, self).__init__(parent)
        self.setTitle("Signal Read (mV)")
        self.text = QLabel("0")
        pe = QPalette()
        pe.setColor(QPalette.WindowText,Qt.yellow)
        self.text.setAutoFillBackground(True)
        pe.setColor(QPalette.Window,Qt.black)
        self.text.setPalette(pe)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setFont(QFont("",16,QFont.Bold))

        # self.checkbox = QCheckBox("Save Raw File")
        self.SaveDataBtn = QPushButton("Save Signal Data")
        self.SaveDataBtn.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.text,0,0,2,2)
        # layout.addWidget(self.checkbox,0,2,1,1)
        layout.addWidget(self.SaveDataBtn,1,2,1,1)
        self.setLayout(layout)


class Fan_Control_Group(QGroupBox):
    def __init__(self, parent=None):
        super(Fan_Control_Group, self).__init__(parent)
        self.setTitle("Fan Control")
        self.Fan_Speed = spinBlock("Fan Speed Setting (mV)", Fan_Speed_MIN, Fan_Speed_MAX)
        self.fanLabel1 = QLabel("Fan Speed = ")
        self.fanLabel2 = QLabel("0")
        self.FanBtn = QPushButton("Set")
        self.FanBtn.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.Fan_Speed,0,0,1,1)
        layout.addWidget(self.FanBtn,0,1,1,1)
        layout.addWidget(self.fanLabel1,0,2,1,1)
        layout.addWidget(self.fanLabel2,0,3,1,1)
        self.setLayout(layout)


class DC_Voltage_Group(QGroupBox):
    def __init__(self, parent=None):
        super(DC_Voltage_Group, self).__init__(parent)
        self.setTitle("DC Voltage Control")
        self.DC_Voltage1 = spinBlock("Fixed Voltage (V)", DC_Voltage1_MIN, DC_Voltage1_MAX)
        self.DC_Voltage2 = spinBlock("ESI (V)", DC_Voltage2_MIN, DC_Voltage2_MAX)
        # self.V1_Btn = QPushButton("Set Fixed Voltage")
        self.V2_Btn = QPushButton("Set ESI")
        # self.fixed_label1 = QLabel("Fixed DC = ")
        # self.fixed_label2 = QLabel("0")
        self.esi_label1 = QLabel("ESI = ")
        self.esi_label2 = QLabel("0")
        # self.V1_Btn.setEnabled(False)
        self.V2_Btn.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.DC_Voltage1,0,0,1,1)
        #layout.addWidget(self.V1_Btn,0,1,1,1)
        #layout.addWidget(self.fixed_label1, 0,2,1,1)
        #layout.addWidget(self.fixed_label2,0,3,1,1)
        layout.addWidget(self.DC_Voltage2,1,0,1,1)
        layout.addWidget(self.V2_Btn,1,1,1,1)
        layout.addWidget(self.esi_label1,1,2,1,1)
        layout.addWidget(self.esi_label2,1,3,1,1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        self.setLayout(layout)


class HVScan_Group(QGroupBox):
    def __init__(self, parent=None):
        super(HVScan_Group, self).__init__(parent)
        self.setTitle("High Voltage Scan")
        self.StartVoltage = spinBlock("Start Voltage (V)", StartVoltage_MIN, StartVoltage_MAX)
        self.VoltageStep = spinBlock("Voltage Step (mV)", VoltageStep_MIN, VoltageStep_MAX, True, 0.01)
        self.Loop = spinBlock("Total Steps", Scan_Loop_MIN, Scan_Loop_MAX)
        self.Back = spinBlock("Backward points", Backward_MIN, Backward_MAX)
        self.offset = spinBlock("Offset (mV)", OFFSET_MIN, OFFSET_MAX)
        self.Run_loop = spinBlock("Accumulate Loops", Run_Loop_MIN, Run_Loop_MAX)
        self.delay = spinBlock("Time delay (ms)", Delay_Time_MIN, Delay_Time_MAX)
        self.filterFreq = spinBlock("Filter Freq (mHz)", Filter_MIN, Filter_MAX)
        self.checkTic = QCheckBox("Tic / Xic")
        self.checkFilter = QCheckBox("Filter")
        self.text1 = QLabel("Voltage Out = ")
        self.text2 = QLabel("0 (V)")
        self.turnoff = QPushButton("Turn off all output")
        self.turnoff.setEnabled(False)

        self.delay.spin.valueChanged.connect(self.update_filter)

        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.StartVoltage,0,0,1,2)
        layout.addWidget(self.VoltageStep,0,2,1,2)
        layout.addWidget(self.Loop,1,0,1,2)
        layout.addWidget(self.Back,1,2,1,2)
        layout.addWidget(self.offset,2,0,1,2)
        layout.addWidget(self.Run_loop,2,2,1,2)
        layout.addWidget(self.delay,3,0,1,2)
        layout.addWidget(self.filterFreq,3,2,1,2)
        layout.addWidget(self.checkTic,5,0,1,1)
        layout.addWidget(self.checkFilter,5,1,1,1)
        layout.addWidget(self.text1,5,2,1,1)
        layout.addWidget(self.text2,5,3,1,1)
        layout.addWidget(self.turnoff,6,2,1,2)
        self.setLayout(layout)

    def update_filter(self):
        delay_value = float(Filter_Const/self.delay.spin.value())
        if (delay_value < Filter_MAX):
            # print("change filter")
            # print(delay_value)
            self.filterFreq.spin.setRange(Filter_MIN, delay_value)
        else:
            self.filterFreq.spin.setRange(Filter_MIN, Filter_MAX)


class TabPlot(QTabWidget):
    def __init__(self, parent=None):
        super(TabPlot, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.plot1 = outputPlotSize(FONTSIZE)
        self.plot2 = output2Plot()
        self.plot3 = outputPlotSize(FONTSIZE)
        self.plot2.ax1.set_ylabel("Arbiary Uint")
        self.plot2.ax2.set_xlabel("Time (s)")
        self.plot2.ax2.set_ylabel("Arbiary Uint")
        self.addTab(self.tab1,"Single Data")
        self.addTab(self.tab2,"TIC")
        self.addTab(self.tab3,"Analysis")
        self.Tab1_UI()
        self.Tab2_UI()
        self.Tab3_UI()

    def Tab1_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot1)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot2)
        self.tab2.setLayout(layout)

    def Tab3_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot3)
        self.tab3.setLayout(layout)


class TabAll(QTabWidget):
    def __init__(self, parent=None):
        super(TabAll, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.HVscan = HVScan_Group()
        self.DCset = DC_Voltage_Group()
        self.Fan = Fan_Control_Group()
        self.DataSampling = Data_Sampling_Group()
        self.TicXic = Xic_Group()
        self.Analysis = Data_Analysis_Group()
        self.addTab(self.tab1,"Scan")
        self.addTab(self.tab2,"Setting")
        self.addTab(self.tab3,"Analysis")

        self.Tab1_UI()
        self.Tab2_UI()
        self.Tab3_UI()

    def Tab1_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.HVscan)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.DCset)
        layout.addWidget(self.Fan)
        layout.addWidget(self.DataSampling)
        layout.addWidget(self.TicXic)
        self.tab2.setLayout(layout)

    def Tab3_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.Analysis)
        self.tab3.setLayout(layout)

#Integrator Setting
    
class mainWidget(QWidget):
#class mainWindow(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        #super (mainWindow, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.comport = connectBlock("USB Connection")
        #self.plot = output2Plot()
        self.tabPlot = TabPlot()
        self.FHedit = editBlock("File Header")
        self.tabAll = TabAll()
        self.Signal = Signal_Read_Group()
        self.runText = QLabel("Run Index = ")
        self.runText.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.runIndex = QLabel("0")
        #self.resetBtn = QPushButton("Reset Index")
        self.DCmode = QPushButton("DC mode")
        self.startScan = QPushButton("Start Scan")
        self.stop = QPushButton("Stop")

        self.DCmode.setEnabled(False)
        self.startScan.setEnabled(False)
        self.stop.setEnabled(False)

        w = QWidget()
        self.picout = QLabel(w)
        lg = QPixmap(LOGO_FILENAME)
        logo = lg.scaled(500, 90, Qt.KeepAspectRatio)
        self.picout.setPixmap(logo)

        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.tabPlot,0,0,7,1)
        mainLayout.addWidget(self.comport.layout2(),0,1,1,1)
        mainLayout.addWidget(self.FHedit, 0,2,1,2)
        mainLayout.addWidget(self.tabAll,1,1,1,3)
        mainLayout.addWidget(self.Signal,2,1,1,3)
        mainLayout.addWidget(self.runText,3,1,1,1)
        mainLayout.addWidget(self.runIndex,3,2,1,1)
        #mainLayout.addWidget(self.resetBtn,4,3,1,1)
        mainLayout.addWidget(self.DCmode,4,1,1,1)
        mainLayout.addWidget(self.startScan,4,2,1,1)
        mainLayout.addWidget(self.stop,4,3,1,1)
        mainLayout.addWidget(self.picout,5,1,1,3)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 3)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setRowStretch(4, 1)
        mainLayout.setRowStretch(5, 1)
        mainLayout.setRowStretch(6, 1)
        mainLayout.setColumnStretch(0, 8)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        self.setLayout(mainLayout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
