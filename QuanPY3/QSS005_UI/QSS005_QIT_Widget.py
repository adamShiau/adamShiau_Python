import os
import sys
sys.path.append("../")
from py3lib.QuGUIclass import *

# SETTING_FILEPATH = "set"
# SETTING_FILENAME = "set/setting.txt"

# Preparation setting constant
WFO_FREQUENCY_MIN = 1    #kHz
WFO_FREQUENCY_MAX = 1500 #kHz
WFO_AMP_MIN = 0    #mV
WFO_AMP_MAX = 1000 #mV
WFO_OFFSET_MIN = -1000 #mV
WFO_OFFSET_MAX = 1000  #mV

WFM_Trigger_Level_Min = -1000 #mv
WFM_Trigger_Level_Max = 1000  #mv

Sample_Time_Min = 300 #ms
Sample_Time_Max = 5000 #ms

Acqu_Time_Min = 3 #s
Acqu_Time_Max = 3600 #s

MASS_MIN = 30   
MASS_MAX = 500  
MASS_STEP = 1

Radius_Min = 0.1
Radius_Max = 100
Radius_Step = 0.1
Radius_Decimals = 1

Freq_Min = 0
Freq_Max = 1500
Freq_Step = 0.1
Freq_Decimals = 1

Rolling_Min = 1
Rolling_Max = 20

DataPts_Min = 10
DataPts_Max = 16384

Threshold_Min = -2
Threshold_Max = 10
Threshold_Step = 0.01

Width_Min = 1
Width_Max = 100

Cdc_Min = 0.0000001
Cdc_Max = 0.1
Cdc_Step = 0.0000001
Cdc_Decimals = 7

Crf_Min = 0.000001
Crf_Max = 10
Crf_Step = 0.000001
Crf_Decimals = 6

TITLE_TEXT = "QIT"


class housingKeeping(QWidget):
    def __init__(self, parent=None):
        super(housingKeeping, self).__init__(parent)
        self.net1 = IPconnectBlock("Major Connection")
        self.net2 = IPconnectBlock("AUX Connection")
        self.FHedit = editBlock("File Header")

        self.HK_UI()

    def HK_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.net1.layout1(),0,0,2,1)
        layout.addWidget(self.net2.layout1(),0,1,2,1)
        layout.addWidget(self.FHedit,2,0,1,2)
        self.setLayout(layout)


class Waveform_Output(QWidget):
    def __init__(self, parent=None):
        super(Waveform_Output, self).__init__(parent)
        self.ch1_freq = spinBlock("Frequency (kHz) <1>", WFO_FREQUENCY_MIN, WFO_FREQUENCY_MAX)
        self.ch1_amp = spinBlock("Amp (mV) <2>", WFO_AMP_MIN, WFO_AMP_MAX)
        self.ch1_offset = spinBlock("Offset (mV) <3>", WFO_OFFSET_MIN, WFO_OFFSET_MAX)
        self.run1_btn = QPushButton("Run")
        self.run1_btn.setEnabled(False)

        self.frame = QGroupBox("ADC input channel")
        self.chBtn1 = QRadioButton("CH 0", self.frame)
        self.chBtn1.setChecked(True)  # select by default
        self.chBtn2 = QRadioButton("CH 1", self.frame)

        self.sample_time = spinBlock("Sample Time (ms)", Sample_Time_Min, Sample_Time_Max)
        self.acqu_time = spinBlock("Total Acquisition Time (s)", Acqu_Time_Min, Acqu_Time_Max)

        self.frame2 = QGroupBox("Polarity")
        self.poBtn1 = QRadioButton("Positive", self.frame2)
        self.poBtn1.setChecked(True)  # select by default
        self.poBtn2 = QRadioButton("Negative", self.frame2)

        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.save_btn = QPushButton("Save")

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        self.wfo_UI()

    def wfo_UI(self):
        frameLayout = QHBoxLayout()
        frameLayout.addWidget(self.chBtn1)
        frameLayout.addWidget(self.chBtn2)
        self.frame.setLayout(frameLayout)

        frameLayout2 = QHBoxLayout()
        frameLayout2.addWidget(self.poBtn1)
        frameLayout2.addWidget(self.poBtn2)
        self.frame2.setLayout(frameLayout2)

        layout = QGridLayout()
        layout.addWidget(self.ch1_freq,0,0,1,2)
        layout.addWidget(self.ch1_amp,0,2,1,2)
        layout.addWidget(self.ch1_offset,0,4,1,2)
        layout.addWidget(self.run1_btn,0,6,1,2)
        layout.addWidget(self.sample_time,0,8,1,2)
        layout.addWidget(self.acqu_time,0,10,1,2)

        layout.addWidget(self.frame,1,0,1,3)
        layout.addWidget(self.frame2,1,3,1,3)

        layout.addWidget(self.start_btn,1,6,1,2)
        layout.addWidget(self.stop_btn,1,8,1,2)
        layout.addWidget(self.save_btn,1,10,1,2)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)

        self.setLayout(layout)


class Waveform_Monitor(QWidget):
    def __init__(self, parent=None):
        super(Waveform_Monitor, self).__init__(parent)
        self.trig_src = QGroupBox("Trigger Src <1>")
        self.chBtn1 = QRadioButton("CH 1", self.trig_src)
        self.chBtn1.setChecked(True)  # select by default
        self.chBtn2 = QRadioButton("CH 2", self.trig_src)

        self.sam_num_list = ["4096" , "8192" , "16384"]
        # self.sam_num = QGroupBox("Sample Number <2>")
        # self.sam_num_combo = QComboBox()
        # self.sam_num_combo.addItems(self.sam_num_list)
        self.sam_num = comboBlock("Sample Number <2>", self.sam_num_list)
        self.sam_num.combo.setCurrentIndex(2)

        self.trig_level = spinBlock("Trigger Level (mV) <3>", WFM_Trigger_Level_Min, WFM_Trigger_Level_Max)

        gain_list = ["LV (-1 ~ 1V)" , "HV (-10 ~ 10V)"]
        # self.gain = QGroupBox("Gain <4>")
        # self.gain_combo = QComboBox()
        # self.gain_combo.addItems(gain_list)
        self.gain = comboBlock("Gain <4>", gain_list)
        self.gain.combo.setCurrentIndex(0)

        self.mon_btn = QPushButton("Monitor")
        self.stop_btn = QPushButton("Stop")
        self.mon_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        self.wfm_UI()

    def wfm_UI(self):
        frameLayout = QHBoxLayout()
        frameLayout.addWidget(self.chBtn1)
        frameLayout.addWidget(self.chBtn2)
        self.trig_src.setLayout(frameLayout)

        # comboLayout = QVBoxLayout()
        # comboLayout.addWidget(self.sam_num_combo)
        # self.sam_num.setLayout(comboLayout)

        # gainLayout = QVBoxLayout()
        # gainLayout.addWidget(self.gain_combo)
        # self.gain.setLayout(gainLayout)

        layout = QGridLayout()
        layout.addWidget(self.trig_src,0,0,1,1)
        layout.addWidget(self.sam_num,0,1,1,1)
        layout.addWidget(self.trig_level,0,2,1,1)
        layout.addWidget(self.gain,0,3,1,1)
        layout.addWidget(self.mon_btn,1,2,1,1)
        layout.addWidget(self.stop_btn,1,3,1,1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)

        self.setLayout(layout)


class Mass_Filter(QWidget):
    def __init__(self, parent=None):
        super(Mass_Filter, self).__init__(parent)
        # self.scanGroup = QGroupBox("Scan Mode")
        # self.rfBtn = QRadioButton("RF Mode",self.scanGroup)
        # self.rfBtn.setChecked(True)
        # self.dcBtn = QRadioButton("DC Mode", self.scanGroup)

        self.startMass = spinBlock("Start Mass", MASS_MIN, MASS_MAX)
        self.stopMass = spinBlock("Stop Mass", MASS_MIN, MASS_MAX)
        self.massMin = spinBlock("XIC Min Mass", MASS_MIN, MASS_MAX)
        self.massMax = spinBlock("XIC Max Mass", MASS_MIN, MASS_MAX)

        self.radius = spinBlock("Radius (cm)", Radius_Min, Radius_Max, True, Radius_Step, Radius_Decimals)
        self.freq = spinBlock("RF Frequency (kHz)", Freq_Min, Freq_Max, True, Freq_Step, Freq_Decimals)
        self.rolling = spinBlock("Rolling Avg", Rolling_Min, Rolling_Max)
        self.dataPts = spinBlock("Data Points", DataPts_Min, DataPts_Max)
        self.threshold = spinBlock("Peak Threshold", Threshold_Min, Threshold_Max, True, Threshold_Step)
        self.width = spinBlock("Peak Width", Width_Min, Width_Max)

        self.cdc = spinBlock("Cdc", Cdc_Min, Cdc_Max, True, Cdc_Step, Cdc_Decimals)
        self.crf = spinBlock("Crf", Crf_Min, Crf_Max, True, Crf_Step, Crf_Decimals)

        self.run_index1 = QLabel("Index = ")
        self.run_index1.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.run_index2 = QLabel("0")
        self.run = QPushButton("Run")
        self.stop = QPushButton("Stop")
        self.save = QPushButton("Save File")
        self.run.setEnabled(False)
        self.stop.setEnabled(False)
        self.save.setEnabled(False)
        self.linkFunction()
        self.tic_UI()

    def tic_UI(self):
        # frameLayout = QHBoxLayout()
        # frameLayout.addWidget(self.rfBtn)
        # frameLayout.addWidget(self.dcBtn)
        # self.scanGroup.setLayout(frameLayout)

        layout = QGridLayout()
        # layout.addWidget(self.scanGroup,0,0,1,2)
        layout.addWidget(self.startMass,0,0,1,1)
        layout.addWidget(self.stopMass,0,1,1,1)
        layout.addWidget(self.massMin,0,2,1,1)
        layout.addWidget(self.massMax,0,3,1,1)
        layout.addWidget(self.radius,0,4,1,1)
        layout.addWidget(self.freq,0,5,1,1)

        layout.addWidget(self.rolling,1,0,1,1)
        layout.addWidget(self.dataPts,1,1,1,1)
        layout.addWidget(self.threshold,1,2,1,1)
        layout.addWidget(self.width, 1,3,1,1)
        layout.addWidget(self.cdc,1,4,1,1)
        layout.addWidget(self.crf,1,5,1,1)

        layout.addWidget(self.run_index1,2,0,1,1)
        layout.addWidget(self.run_index2,2,1,1,1)
        layout.addWidget(self.run,2,3,1,1)
        layout.addWidget(self.stop,2,4,1,1)
        layout.addWidget(self.save,2,5,1,1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)

        self.setLayout(layout)

    def linkFunction(self):
        self.startMass.spin.valueChanged.connect(self.adjStartMass)
        self.stopMass.spin.valueChanged.connect(self.adjStopMass)
        self.massMin.spin.valueChanged.connect(self.adjMassMin)
        self.massMax.spin.valueChanged.connect(self.adjMassMax)

    def adjStartMass(self):
        startMass = self.startMass.spin.value()
        #print("start = "+str(self.startMass.spin.value()))
        stopMass = self.stopMass.spin.value()
        massMin = self.massMin.spin.value()
        massMax = self.massMax.spin.value()
        self.stopMass.spin.setRange(startMass+MASS_STEP, MASS_MAX)
        self.massMin.spin.setRange(startMass, massMax-MASS_STEP)
        if (massMin < startMass):
            self.massMax.spin.setRange(startMass+MASS_STEP, stopMass)
        #print("1 stop = "+str(self.stopMass.spin.value()))
        #print("1 min = "+str(self.massMin.spin.value()))
        #print("1 max = "+str(self.massMax.spin.value()))

    def adjStopMass(self):
        stopMass = self.stopMass.spin.value()
        #print("stop = "+str(self.stopMass.spin.value()))
        startMass = self.startMass.spin.value()
        massMin = self.massMin.spin.value()
        massMax = self.massMax.spin.value()
        self.startMass.spin.setRange(MASS_MIN, stopMass-MASS_STEP)
        self.massMax.spin.setRange(massMin+MASS_STEP, stopMass)
        if (massMax > stopMass):
            self.massMin.spin.setRange(startMass, stopMass-MASS_STEP)
        #print("2 start = "+str(self.startMass.spin.value()))
        #print("2 min = "+str(self.massMin.spin.value()))
        #print("2 max = "+str(self.massMax.spin.value()))

    def adjMassMin(self):
        massMin = self.massMin.spin.value()
        #print("min = "+str(self.massMin.spin.value()))
        stopMass = self.stopMass.spin.value()
        self.massMax.spin.setRange(massMin+MASS_STEP, stopMass)
        #print("3 max = "+str(self.massMax.spin.value()))

    def adjMassMax(self):
        massMax = self.massMax.spin.value()
        #print("max = "+str(self.massMax.spin.value()))
        startMass = self.startMass.spin.value()
        self.massMin.spin.setRange(startMass, massMax-MASS_STEP)
        #print("4 min = "+str(self.massMin.spin.value()))


class msTabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(msTabSetting, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.addTab(self.tab1,"Waveform Output")
        self.addTab(self.tab2,"Waveform Monitor")
        self.addTab(self.tab3,"Quadrupole Mass Filter")
        self.wf_out = Waveform_Output()
        self.wf_mon = Waveform_Monitor()
        self.tic = Mass_Filter()
        self.Tab1_UI()
        self.Tab2_UI()
        self.Tab3_UI()

    def Tab1_UI(self):
        tab1_layout = QHBoxLayout()
        tab1_layout.addWidget(self.wf_out)
        self.tab1.setLayout(tab1_layout)

    def Tab2_UI(self):
        tab2_layout = QHBoxLayout()
        tab2_layout.addWidget(self.wf_mon)
        self.tab2.setLayout(tab2_layout)

    def Tab3_UI(self):
        tab3_layout = QHBoxLayout()
        tab3_layout.addWidget(self.tic)
        self.tab3.setLayout(tab3_layout)

class picTabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(picTabSetting, self).__init__(parent)
        self.picTab1 = QWidget()
        self.picTab2 = QWidget()
        self.picTab3 = QWidget()
        self.addTab(self.picTab1, "Preparation")
        self.addTab(self.picTab2, "Waveform Monitor")
        self.addTab(self.picTab3, "TIC Data")
        self.plot = outputPlot()
        self.plot2 = outputPlot()
        self.plot3 = output3Plot()

        self.plot3.ax1.set_xlabel("Time (s)")
        self.plot3.ax2.set_xlabel("m/z")
        self.plot3.ax3.set_xlabel("m/z")

        self.picTab1UI()
        self.picTab2UI()
        self.picTab3UI()

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


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        # self.resize(1024,768)
        # self.move(50,50)
        self.ms = msTabSetting()
        self.hk = housingKeeping()
        self.pic = picTabSetting()

        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.ms,0,0,1,1)
        mainLayout.addWidget(self.hk,0,1,1,1)
        mainLayout.addWidget(self.pic,1,0,1,2)
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
