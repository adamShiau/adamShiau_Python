import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *

StartVoltage_MIN = 1000
StartVoltage_MAX = 1900

VoltageStep_MIN = 200
VoltageStep_MAX = 2000

Scan_Loop_MIN = 1
Scan_Loop_MAX = 2000

Backward_MIN = 0
Backward_MAX = 50

OFFSET_MIN = -3000
OFFSET_MAX = 3000

DC_Voltage1_MIN = 0
DC_Voltage1_MAX = 2000

DC_Voltage2_MIN = 0
DC_Voltage2_MAX = 5000

Fan_Speed_MIN = 0
Fan_Speed_MAX = 5000

MV_Numver_MIN = 50
MV_Numver_MAX = 30000

AVG_time_MIN = 1
AVG_time_MAX = 100

Run_Loop_MIN = 1
Run_Loop_MAX = 1000

INT_CYCLE_MIN = 1
INT_CYCLE_MAX = 500

Threshold_MIN = -10*1000
Threshold_MAX = 10*1000

Noise_MIN = 1
Noise_MAX = 100
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


# class Integrator_Group(QWidget):
#     def __init__(self, parent=None):
#         super(Integrator_Group, self).__init__(parent)
#         self.GroupBox = QGroupBox("Integrator Setting")
#         #self.ResetCycle = spinBlock("Reset Cycle", CYCLE_MIN, CYCLE_MAX, "Reset Time =", "0 (ms)", False)
#         #self.HoldCycle = spinBlock("Hold Cycle", CYCLE_MIN, CYCLE_MAX, "Hold Time =", "0 (ms)", False)
#         #self.IntCycle = spinBlock("Int Cycle (ms)", INT_CYCLE_MIN, INT_CYCLE_MAX, "", "", False)
#         self.vText0 = QLabel("Voltage (V)")
#         self.vStart = QLabel("Start Voltage")
#         self.vth1 = QSpinBox()
#         self.vth2 = QSpinBox()
#         self.vth3 = QSpinBox()
#         self.vStop = QLabel("Stop Voltage")
#         self.gText0 = QLabel("Int Cycle (ms)")
#         self.int_time1 = QDoubleSpinBox()
#         self.int_time2 = QDoubleSpinBox()
#         self.int_time3 = QDoubleSpinBox()
#         self.int_time4 = QDoubleSpinBox()
#         self.int_time1.setDecimals(1)
#         self.int_time2.setDecimals(1)
#         self.int_time3.setDecimals(1)
#         self.int_time4.setDecimals(1)
#         self.int_time1.setRange(INT_CYCLE_MIN, INT_CYCLE_MAX)
#         self.int_time2.setRange(INT_CYCLE_MIN, INT_CYCLE_MAX)
#         self.int_time3.setRange(INT_CYCLE_MIN, INT_CYCLE_MAX)
#         self.int_time4.setRange(INT_CYCLE_MIN, INT_CYCLE_MAX)

#         #self.SubBlockWidget()

#     def SubBlockWidget(self):
#         layout = QGridLayout()
#         layout.addWidget(self.vText0,0,0,1,1)
#         layout.addWidget(self.vStart,1,0,1,1)
#         layout.addWidget(self.vth1,2,0,1,1)
#         layout.addWidget(self.vth2,3,0,1,1)
#         layout.addWidget(self.vth3,4,0,1,1)
#         layout.addWidget(self.vStop,5,0,1,1)
#         layout.addWidget(self.gText0,0,1,1,1)
#         layout.addWidget(self.int_time1,1,1,1,1)
#         layout.addWidget(self.int_time2,2,1,1,1)
#         layout.addWidget(self.int_time3,3,1,1,1)
#         layout.addWidget(self.int_time4,4,1,1,1)
#         #self.setLayout(layout)
#         self.GroupBox.setLayout(layout)
#         self.GroupBox.show()
#         return self.GroupBox


class Data_Sampling_Group(QGroupBox):
    def __init__(self, parent=None):
        super(Data_Sampling_Group, self).__init__(parent)
        self.setTitle("Data Sampling")
        self.frame = QGroupBox("Channel")
        self.chBtn1 = QRadioButton("CH 0", self.frame)
        self.chBtn1.setChecked(True)  # select by default
        self.chBtn2 = QRadioButton("CH 1", self.frame)

        self.frame2 = QGroupBox("Polarity")
        self.poBtn1 = QRadioButton("Positive", self.frame2)
        self.poBtn1.setChecked(True)  # select by default
        self.poBtn2 = QRadioButton("Negative", self.frame2)

        self.MV_number = spinBlock("ADC Average Points", MV_Numver_MIN, MV_Numver_MAX)
        self.AVG_time = spinBlock("Average Times", AVG_time_MIN, AVG_time_MAX)
        self.int_time = spinBlock("Integrator Times (ms)", INT_CYCLE_MIN, INT_CYCLE_MAX)

        #self.frame3 = QGroupBox("Scan Accumulate")
        #self.acBtn1 = QRadioButton("Yes", self.frame3)
        #self.acBtn2 = QRadioButton("No", self.frame3)
        #self.acBtn2.setChecked(True)  # select by default

        frameLayout1 = QHBoxLayout()
        frameLayout1.addWidget(self.chBtn1)
        frameLayout1.addWidget(self.chBtn2)
        self.frame.setLayout(frameLayout1)

        frameLayout2 = QHBoxLayout()
        frameLayout2.addWidget(self.poBtn1)
        frameLayout2.addWidget(self.poBtn2)
        self.frame2.setLayout(frameLayout2)

        #frameLayout3 = QHBoxLayout()
        #frameLayout3.addWidget(self.acBtn1)
        #frameLayout3.addWidget(self.acBtn2)
        #self.frame3.setLayout(frameLayout3)

        layout = QGridLayout()
        layout.addWidget(self.frame,0,0,1,2)
        layout.addWidget(self.frame2,1,0,1,2)
        layout.addWidget(self.MV_number,2,0,1,1)
        layout.addWidget(self.AVG_time,2,1,1,1)
        layout.addWidget(self.int_time,3,0,1,1)
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
        layout.addWidget(self.DC_Voltage1,0,0,2,1)
        #layout.addWidget(self.V1_Btn,0,1,1,1)
        #layout.addWidget(self.fixed_label1, 0,2,1,1)
        #layout.addWidget(self.fixed_label2,0,3,1,1)
        layout.addWidget(self.DC_Voltage2,0,1,2,1)
        layout.addWidget(self.V2_Btn,0,2,1,2)
        layout.addWidget(self.esi_label1,1,2,1,1)
        layout.addWidget(self.esi_label2,1,3,1,1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 2)
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
        self.text1 = QLabel("Voltage Out = ")
        self.text2 = QLabel("0 (V)")
        self.reset = QPushButton("Turn off all ouput")
        self.reset.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.StartVoltage,0,0,1,2)
        layout.addWidget(self.VoltageStep,0,2,1,2)
        layout.addWidget(self.Loop,1,0,1,2)
        layout.addWidget(self.Back,1,2,1,2)
        layout.addWidget(self.offset,2,0,1,2)
        layout.addWidget(self.Run_loop,2,2,1,2)
        layout.addWidget(self.text1,3,0,1,1)
        layout.addWidget(self.text2,3,1,1,1)
        layout.addWidget(self.reset,3,3,1,1)
        self.setLayout(layout)


class TabPlot(QTabWidget):
    def __init__(self, parent=None):
        super(TabPlot, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.plot1 = outputPlotSize(FONTSIZE)
        self.plot2 = outputPlotSize(FONTSIZE)
        self.addTab(self.tab1,"Single Data")
        self.addTab(self.tab2,"Analysis")
        self.Tab1_UI()
        self.Tab2_UI()

    def Tab1_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot1)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot2)
        self.tab2.setLayout(layout)


class TabAll(QTabWidget):
    def __init__(self, parent=None):
        super(TabAll, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        # self.tab4 = QWidget()
        # self.tab5 = QWidget()
        self.HVscan = HVScan_Group()
        self.DCset = DC_Voltage_Group()
        self.Fan = Fan_Control_Group()
        self.DataSampling = Data_Sampling_Group()
        # self.Integrator = Integrator_Group()
        self.Analysis = Data_Analysis_Group()
        self.addTab(self.tab1,"Scan")
        # self.addTab(self.tab2,"DC & Fan")
        self.addTab(self.tab2,"Setting")
        # self.addTab(self.tab4,"Integrator")
        self.addTab(self.tab3,"Analysis")

        self.Tab1_UI()
        self.Tab2_UI()
        self.Tab3_UI()
        # self.Tab4_UI()
        # self.Tab5_UI()

        # self.HVscan.StartVoltage.spin.valueChanged.connect(self.VoltageChange)
        # self.HVscan.VoltageStep.spin.valueChanged.connect(self.VoltageChange)
        # self.HVscan.Loop.spin.valueChanged.connect(self.VoltageChange)
        # self.Integrator.vth1.valueChanged.connect(lambda:self.VoltageChange(3))
        # self.Integrator.vth2.valueChanged.connect(lambda:self.VoltageChange(2))

    def Tab1_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.HVscan)
        layout.addWidget(self.DCset)
        self.tab1.setLayout(layout)

    # def Tab2_UI(self):
    #     layout = QVBoxLayout()
    #     layout.addWidget(self.DCset.SubBlockWidget())
    #     layout.addWidget(self.Fan.SubBlockWidget())
    #     self.tab2.setLayout(layout)

    def Tab2_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.Fan)
        layout.addWidget(self.DataSampling)
        self.tab2.setLayout(layout)

    # def Tab4_UI(self):
    #     layout = QVBoxLayout()
    #     layout.addWidget(self.Integrator.SubBlockWidget())
    #     self.tab4.setLayout(layout)

    def Tab3_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.Analysis)
        self.tab3.setLayout(layout)

#Integrator Setting
    # def VoltageChange(self, vth = 4):
    #     if (vth >= 4):
    #         startValue = self.HVscan.StartVoltage.spin.value()
    #         stepValue = float(self.HVscan.VoltageStep.spin.value())/1000.0
    #         loopValue = self.HVscan.Loop.spin.value()
    #         self.stopValue = startValue + stepValue * loopValue

    #         self.Integrator.vStart.setText("Start Voltage = "+ str(startValue))
    #         self.Integrator.vStop.setText("Stop Voltage = "+ str(self.stopValue))

    #         if ((self.stopValue - startValue) < 1):
    #             self.Integrator.vth1.setRange(self.stopValue, self.stopValue-1)
    #         else:
    #             self.Integrator.vth1.setEnabled(True)
    #             self.Integrator.int_time2.setEnabled(True)
    #             self.Integrator.vth1.setRange(startValue+1, self.stopValue-1)

    #     if (vth >= 3):
    #         vth1 = self.Integrator.vth1.value()
    #         if ((self.stopValue - vth1) < 1):
    #             #print("disable vth 1")
    #             self.Integrator.vth1.setEnabled(False)
    #             self.Integrator.int_time2.setEnabled(False)
    #             self.Integrator.vth2.setRange(self.stopValue, self.stopValue-1)
    #         else:
    #             self.Integrator.vth2.setEnabled(True)
    #             self.Integrator.int_time3.setEnabled(True)
    #             self.Integrator.vth2.setRange(vth1+1, self.stopValue-1)

    #     if (vth >= 2):
    #         vth2 = self.Integrator.vth2.value()
    #         if ((self.stopValue - vth2) < 1):
    #             #print("disable vth 2")
    #             self.Integrator.vth2.setEnabled(False)
    #             self.Integrator.int_time3.setEnabled(False)
    #             self.Integrator.vth3.setRange(self.stopValue, self.stopValue-1)
    #         else:
    #             self.Integrator.vth3.setEnabled(True)
    #             self.Integrator.int_time4.setEnabled(True)
    #             self.Integrator.vth3.setRange(vth2+1, self.stopValue-1)

    #     if (vth >= 1):
    #         vth3 = self.Integrator.vth3.value()
    #         if ((self.stopValue - vth3) < 1):
    #             #print("disable vth 3")
    #             self.Integrator.vth3.setEnabled(False)
    #             self.Integrator.int_time4.setEnabled(False)


class mainWidget(QWidget):
#class mainWindow(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        #super (mainWindow, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.net = IPconnectBlock("SSH connection")
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
        mainLayout.addWidget(self.net.layout2(),0,1,1,2)
        mainLayout.addWidget(self.FHedit, 0,3,1,1)
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
