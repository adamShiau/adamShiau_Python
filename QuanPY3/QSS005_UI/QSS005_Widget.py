import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *

# Preparation setting constant
TAB0_FREQUENCY_MIN = 1    #kHz
TAB0_FREQUENCY_MAX = 1500 #kHz
TAB0_AMP_MIN = 0    #mV
TAB0_AMP_MAX = 1000 #mV
TAB0_OFFSET_MIN = -1000 #mV
TAB0_OFFSET_MAX = 1000  #mV

# constant parmater setting
MS1_CH1_FREQ_MIN = 100  # kHz
MS1_CH1_FREQ_MAX = 2000 # kHz

MS1_CH1_OFFSET_AMP_MIN = -1000 #mV
MS1_CH1_OFFSET_AMP_MAX = 1000  #mV

MS1_CH1_RF_AMP_MIN = 0    # mV
MS1_CH1_RF_AMP_MAX = 1000 # mV

MS1_CH1_RAMP_AMP_MIN = 0    # mV
MS1_CH1_RAMP_AMP_MAX = 1000 # mV

MS1_CH1_FINAL_AMP_MIN = 0    # mV
MS1_CH1_FINAL_AMP_MAX = 1000 # mV

MS1_SCAN_PERIOD_MIN = 1    # ms
MS1_SCAN_PERIOD_MAX = 1000 # ms

MS1_CH2_CHIRP_AMP_MIN = 10    # mV
MS1_CH2_CHIRP_AMP_MAX = 10000 # mV

MS1_CH2_CHIRP_END_FREQ_MIN = 100 # kHz
MS1_CH2_CHIRP_END_FREQ_MAX = 500 # kHz

TTL_DURATION_MIN = 1    # us
TTL_DURATION_MAX = 1000 # us

DAMP_DURATION_MIN = 1    # us
DAMP_DURATION_MAX = 1000 # us

INTERGATION_TIME_MIN = 10  # us
INTERGATION_TIME_MAX = 100 # us

CYCLE_MIN = -100
CYCLE_MAX = 100

GAIN_P_MIN = 1
GAIN_P_MAX = 100

GAIN_N_MIN = 1
GAIN_N_MAX = 100

RESET_MIN = 0
RESET_MAX = 2000

HOLD_MIN = 0
HOLD_MAX = 1000

INT_MIN = 0
INT_MAX = 2500

LEVEL_MIN = 1
LEVEL_MAX = 10

Threshold_MIN = -10
Threshold_MAX = 10

Noise_MIN = 1
Noise_MAX = 100

PEAK_TEXT = "Peak number must largger than 2"

PEAK_MIN = 0
PEAK_MAX = 10000

PEAK_INDEX_MIN = 1
PEAK_INDEX_MAX = 100

RUN_LOOP_MIN = 1
RUN_LOOP_MAX = 500000

TITLE_TEXT = " Acdemic Sincica GRC Mass Spectrometer "

class Ms1Dialog(QDialog):
    def __init__(self, init_data, parent = None):
        super(Ms1Dialog, self).__init__(parent)
        self.setWindowTitle("Set Parameter")

        self.ch1_freq = spinBlock("CH1 Frequency (kHz) <1>", MS1_CH1_FREQ_MIN, MS1_CH1_FREQ_MAX)
        self.do1_period = spinBlock("Scan Period (ms) <2>", MS1_SCAN_PERIOD_MIN, MS1_SCAN_PERIOD_MAX)
        self.ch1_offset_amp = spinBlock("CH1 Offset Amplitude (mV) <13>", MS1_CH1_OFFSET_AMP_MIN, MS1_CH1_OFFSET_AMP_MAX)
        self.ch1_rf_amp = spinBlock("CH1 RF Amplitude (mV) <3>", MS1_CH1_RF_AMP_MIN, MS1_CH1_RF_AMP_MAX)
        self.ch1_ramp_amp = spinBlock("CH1 Ramp Amplitude (mV) <4>", MS1_CH1_RAMP_AMP_MIN, MS1_CH1_RAMP_AMP_MAX)
        self.ch1_final_amp = spinBlock("CH1 Final Amplitude (mV) <5>", MS1_CH1_FINAL_AMP_MIN, MS1_CH1_FINAL_AMP_MAX)
        self.ch2_chirp_amp = spinBlock("CH2 Chirp Amp (mv) <6>", MS1_CH2_CHIRP_AMP_MIN, MS1_CH2_CHIRP_AMP_MAX)
        self.ch2_chirp_end_freq = spinBlock("CH2 Chirp End Frequency (kHz) <8>", MS1_CH2_CHIRP_END_FREQ_MIN, MS1_CH2_CHIRP_END_FREQ_MAX)
        self.ttl_duration = spinBlock("TTL Duration (ms) <10>", TTL_DURATION_MIN, TTL_DURATION_MAX)
        self.damp_duration = spinBlock("Damping Duration (ms) <11>", DAMP_DURATION_MIN, DAMP_DURATION_MAX)
        self.cycle = spinBlock("ADC DC <12>", CYCLE_MIN, CYCLE_MAX)
        self.gain_p = spinBlock("ADC GAIN P", GAIN_P_MIN, GAIN_P_MAX)
        self.gain_n = spinBlock("ADC GAIN N", GAIN_N_MIN, GAIN_N_MAX)
        self.reset = spinBlock("Reset", RESET_MIN, RESET_MAX)
        self.hold = spinBlock("Hold", HOLD_MIN, HOLD_MAX)
        self.int = spinBlock("Int", INT_MIN, INT_MAX)
        self.level = spinBlock("Level", LEVEL_MIN, LEVEL_MAX)
        self.Threshold = spinBlock("Threshold (V)", Threshold_MIN, Threshold_MAX, True, 0.001)
        self.Noise = spinBlock("Width (points)", Noise_MIN, Noise_MAX)
        self.data = init_data

        ch2_freq_list = ["1/2" , "1/3" , "1/4"]
        # self.ch2_freq = QGroupBox("CH2 Freq Ratio <7>")
        # self.ch2_freq_combo = QComboBox()
        # self.ch2_freq_combo.addItems(ch2_freq_list)
        self.ch2_freq = comboBlock("CH2 Freq Ratio <7>", ch2_freq_list)

        self.OKbtn = QPushButton("OK")

        self.ttl_duration.spin.valueChanged.connect(lambda:self.update_damp())
        self.damp_duration.spin.valueChanged.connect(lambda:self.update_ttl())
        self.layout()
        self.connectFunction()
        self.setSpinValue(self.data)

    def layout(self):
        # comboLayout = QVBoxLayout()
        # comboLayout.addWidget(self.ch2_freq_combo)
        # self.ch2_freq.setLayout(comboLayout)

        layout = QGridLayout()
        layout.addWidget(self.ch1_freq,0,0,1,1)   
        layout.addWidget(self.ch1_offset_amp,0,1,1,1) 
        layout.addWidget(self.ch1_rf_amp,0,2,1,1) 
        layout.addWidget(self.ch1_ramp_amp,0,3,1,1)
        layout.addWidget(self.ch1_final_amp,0,4,1,1)

        layout.addWidget(self.do1_period,1,0,1,1)
        layout.addWidget(self.ch2_chirp_amp,1,1,1,1)
        layout.addWidget(self.ch2_chirp_end_freq,1,2,1,1)
        layout.addWidget(self.ch2_freq,1,3,1,1)
        layout.addWidget(self.ttl_duration,1,4,1,1)

        layout.addWidget(self.damp_duration,2,0,1,1)
        layout.addWidget(self.cycle,2,1,1,1)
        layout.addWidget(self.gain_p,2,2,1,1)
        layout.addWidget(self.gain_n,2,3,1,1)
        layout.addWidget(self.level,2,4,1,1)

        layout.addWidget(self.reset,3,0,1,1)
        layout.addWidget(self.hold,3,1,1,1)
        layout.addWidget(self.int,3,2,1,1)
        layout.addWidget(self.Threshold, 3, 3, 1, 1)
        layout.addWidget(self.Noise, 3, 4, 1, 1)

        layout.addWidget(self.OKbtn,4,4,1,1)

        self.setLayout(layout)

    def setSpinValue(self, data):
        self.ch1_freq.spin.setValue(int(data[0]))
        self.do1_period.spin.setValue(int(data[1]))
        self.ch1_rf_amp.spin.setValue(float(data[2]))
        self.ch1_ramp_amp.spin.setValue(float(data[3]))
        self.ch1_final_amp.spin.setValue(int(data[4]))
        self.ch2_chirp_amp.spin.setValue(float(data[5]))
        self.ch2_chirp_end_freq.spin.setValue(int(data[7]))
        self.ttl_duration.spin.setValue(int(data[8]))
        self.damp_duration.spin.setValue(int(data[9]))
        self.cycle.spin.setValue(int(data[10]))
        self.ch1_offset_amp.spin.setValue(int(data[11]))
        self.gain_p.spin.setValue(int(data[12]))
        self.gain_n.spin.setValue(int(data[13]))
        self.reset.spin.setValue(int(data[14]))
        self.hold.spin.setValue(int(data[15]))
        self.int.spin.setValue(int(data[16]))
        self.level.spin.setValue(int(data[17]))
        self.Threshold.spin.setValue(float(data[18]))
        self.Noise.spin.setValue(int(data[19]))

        ms1_ch2_freq = float(data[6])
        if (ms1_ch2_freq == 0.25):
            self.ch2_freq.combo.setCurrentIndex(2)
        elif (ms1_ch2_freq == 0.33333333):
            self.ch2_freq.combo.setCurrentIndex(1)
        else:   #elif (ms1_ch2_freq == 0.5):
            self.ch2_freq.combo.setCurrentIndex(0)

    def getSpinValue(self):
        data = [100, 1, 10.0, 100.0, 0, 10.0, 0.5, 100, 1, 1, 76, 0, 30, 25, 1250, 250, 1250, 1, 0.0, 1]

        ms1_ch2f_ratio = self.ch2_freq.combo.currentIndex()
        if (ms1_ch2f_ratio == 2):
            ms1_ch2_freq = 0.25
        elif (ms1_ch2f_ratio == 1):
            ms1_ch2_freq = 0.33333333
        else:   #elif (ms1_ch2f_ratio) == 0:
            ms1_ch2_freq = 0.5

        data[0] = self.ch1_freq.spin.value()
        data[1] = self.do1_period.spin.value()
        data[2] = float(self.ch1_rf_amp.spin.value())
        data[3] = float(self.ch1_ramp_amp.spin.value())
        data[4] = self.ch1_final_amp.spin.value()
        data[5] = float(self.ch2_chirp_amp.spin.value())
        data[6] = float(ms1_ch2_freq)
        data[7] = self.ch2_chirp_end_freq.spin.value()
        data[8] = self.ttl_duration.spin.value()
        data[9] = self.damp_duration.spin.value()
        data[10] = self.cycle.spin.value()
        data[11] = self.ch1_offset_amp.spin.value()
        data[12] = self.gain_p.spin.value()
        data[13] = self.gain_n.spin.value()
        data[14] = self.reset.spin.value()
        data[15] = self.hold.spin.value()
        data[16] = self.int.spin.value()
        data[17] = self.level.spin.value()
        data[18] = self.Threshold.spin.value()
        data[19] = self.Noise.spin.value()

        return data

    def update_damp(self):
        ttl_value = self.ttl_duration.spin.value()
        #print ttl_value
        #self.damp_duration.coarse.setRange(DAMP_DURATION_MIN, ttl_value)
        self.damp_duration.spin.setRange(DAMP_DURATION_MIN, ttl_value)

    def update_ttl(self):
        damp_value = self.damp_duration.spin.value()
        #print damp_value
        #self.ttl_duration.coarse.setRange(damp_value, TTL_DURATION_MAX)
        self.ttl_duration.spin.setRange(damp_value, TTL_DURATION_MAX)

    def connectFunction(self):
        self.OKbtn.clicked.connect(self.okButtonPress)

    def okButtonPress(self):
        self.data = self.getSpinValue()
        self.close()

    @staticmethod
    def getParameter(init_data, parent = None):
        dialog = Ms1Dialog(init_data, parent)
        result = dialog.exec_()
        return dialog.data


class SetPeakDialog(QDialog):
    def __init__(self, peak_num, loggername, parent = None):
        super(SetPeakDialog, self).__init__(parent)
        self.setWindowTitle("Set Peak Mass")
        self.peak1 = checkEditBlock("Peak1 Mass", PEAK_MIN, PEAK_MAX)
        self.peak2 = checkEditBlock("Peak2 Mass", PEAK_MIN, PEAK_MAX)
        self.peak3 = checkEditBlock("Peak3 Mass", PEAK_MIN, PEAK_MAX)
        self.peak4 = checkEditBlock("Peak4 Mass", PEAK_MIN, PEAK_MAX)
        self.peak5 = checkEditBlock("Peak5 Mass", PEAK_MIN, PEAK_MAX)
        self.status = QLabel(PEAK_TEXT)
        self.OKbtn = QPushButton("OK")
        self.setPeak = []
        self.logger = logging.getLogger(loggername)

        self.layout()
        self.connectFunction()
        self.SetPeakEnable(int(peak_num))

    def layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.peak1)
        layout.addWidget(self.peak2)
        layout.addWidget(self.peak3)
        layout.addWidget(self.peak4)
        layout.addWidget(self.peak5)
        layout.addWidget(self.status)
        layout.addWidget(self.OKbtn)
        self.setLayout(layout)

    def connectFunction(self):
        self.OKbtn.clicked.connect(self.okButtonPress)

    def SetPeakEnable(self, peak_num):
        if (peak_num >= 1):
            self.peak1.check.setEnabled(True)
            self.peak1.value.setEnabled(True)
        else:
            self.peak1.check.setEnabled(False)
            self.peak1.value.setEnabled(False)

        if (peak_num >= 2):
            self.peak2.check.setEnabled(True)
            self.peak2.value.setEnabled(True)
        else:
            self.peak2.check.setEnabled(False)
            self.peak2.value.setEnabled(False)

        if (peak_num >= 3):
            self.peak3.check.setEnabled(True)
            self.peak3.value.setEnabled(True)
        else:
            self.peak3.check.setEnabled(False)
            self.peak3.value.setEnabled(False)

        if (peak_num >= 4):
            self.peak4.check.setEnabled(True)
            self.peak4.value.setEnabled(True)
        else:
            self.peak4.check.setEnabled(False)
            self.peak4.value.setEnabled(False)

        if (peak_num >= 5):
            self.peak5.check.setEnabled(True)
            self.peak5.value.setEnabled(True)
        else:
            self.peak5.check.setEnabled(False)
            self.peak5.value.setEnabled(False)

    def SetPeakText(self, color, text):
        pe = QPalette()
        pe.setColor(QPalette.WindowText, color)
        self.status.setPalette(pe)
        self.status.setText(text)
        self.status.show()

    def okButtonPress(self):
        peaknum = 0
        if self.peak1.check.isChecked():
            value = self.peak1.value.text()
            if (value != ""):
                self.setPeak.append([0, float(value)])
                peaknum = peaknum + 1

        if self.peak2.check.isChecked():
            value = self.peak2.value.text()
            if (value != ""):
                self.setPeak.append([1, float(value)])
                peaknum = peaknum + 1

        if self.peak3.check.isChecked():
            value = self.peak3.value.text()
            if (value != ""):
                self.setPeak.append([2, float(value)])
                peaknum = peaknum + 1

        if self.peak4.check.isChecked():
            value = self.peak4.value.text()
            if (value != ""):
                self.setPeak.append([3, float(value)])
                peaknum = peaknum + 1

        if self.peak5.check.isChecked():
            value = self.peak5.value.text()
            if (value != ""):
                self.setPeak.append([4, float(value)])
                peaknum = peaknum + 1

        if (peaknum < 2):
            self.SetPeakText(Qt.red, PEAK_TEXT)
        else:
            self.logger.debug(str(self.setPeak))
            self.close()
           
    @staticmethod
    def getParameter(peak_num, loggername, parent = None):
        dialog = SetPeakDialog(peak_num, loggername, parent)
        result = dialog.exec_()
        return dialog.setPeak


class uartBlock(QGroupBox):
    def __init__(self, parent = None):
        super(uartBlock, self).__init__(parent)
        self.setTitle("Gauge")
        self.gaugeTurn = QPushButton("Turn On")
        self.gaugeOut = QLabel("0")
        self.gaugeMeas = QPushButton("Measure")

        pe = QPalette()
        pe.setColor(QPalette.WindowText,Qt.yellow)
        self.gaugeOut.setAutoFillBackground(True)
        pe.setColor(QPalette.Window,Qt.black)
        #pe.setColor(QPalette.Background,Qt.black)
        self.gaugeOut.setPalette(pe)
        self.gaugeOut.setAlignment(Qt.AlignCenter)
        self.gaugeOut.setFont(QFont("", 24, QFont.Bold))
        self.gaugeTurn.setEnabled(False)
        self.gaugeMeas.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.gaugeTurn)
        layout.addWidget(self.gaugeOut)
        layout.addWidget(self.gaugeMeas)
        self.setLayout(layout)


class dacSubBlock(QGroupBox):
    def __init__(self, parent = None):
        super(dacSubBlock, self).__init__(parent)
        self.setTitle("DAC (V)")
        self.dac_combo = QComboBox()
        self.dac_list = ["DAC 1", "DAC 2" , "DAC 3" , "DAC 4" , "DAC 5" , "DAC 6" , "DAC 7" , "DAC 8" , "DAC 9" , "DAC 10"]
        self.dac_combo.addItems(self.dac_list)
        self.text1 = QLabel("output = ")
        self.text2 = QLabel("input x 6 / 5000")
        self.setVolt = QLineEdit()
        self.setVolt.setValidator(QDoubleValidator(0.000, 10.000, 3))
        self.setBtn = QPushButton("Set")
        self.setBtn.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.text1, 0, 0, 1, 1)
        layout.addWidget(self.text2, 0, 1, 1, 1)
        layout.addWidget(self.dac_combo, 1, 0, 1, 2)
        layout.addWidget(self.setVolt, 2, 0, 1, 2)
        layout.addWidget(self.setBtn, 3, 0, 1, 2)
        self.setLayout(layout)


# class Waveform_Output(QGroupBox):
#     def __init__(self, parent=None):
#         super(Waveform_Output, self).__init__(parent)
#         self.wfo_GroupBox = QGroupBox("Preparation")
#         self.ch1_freq = spinBlock("Frequency (kHz) <1>", TAB0_FREQUENCY_MIN, TAB0_FREQUENCY_MAX)
#         self.ch1_amp = spinBlock("Amp (mV) <2>", TAB0_AMP_MIN, TAB0_AMP_MAX)
#         self.ch1_offset = spinBlock("Offset (mV) <3>", TAB0_OFFSET_MIN, TAB0_OFFSET_MAX)
#         self.run1_btn = QPushButton("Run")
#         self.run1_btn.setEnabled(False)

#     def wfo_UI(self):
#         layout = QHBoxLayout()
#         layout.addWidget(self.ch1_freq)
#         layout.addWidget(self.ch1_amp)
#         layout.addWidget(self.ch1_offset)
#         layout.addWidget(self.run1_btn)
#         self.wfo_GroupBox.setLayout(layout)
#         return self.wfo_GroupBox


class housingKeeping(QWidget):
    def __init__(self, parent=None):
        super(housingKeeping, self).__init__(parent)
        self.net = IPconnectBlock("Connection")
        self.FHedit = editBlock("File Header")
        self.uart = uartBlock()
        self.dac = dacSubBlock()
        #self.wfo = Waveform_Output()

        self.HK_UI()

    def HK_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.net.layout1())
        layout.addWidget(self.FHedit)
        layout.addWidget(self.uart)
        #layout.addWidget(self.int_time)
        layout.addWidget(self.dac)
        #layout.addWidget(self.wfo.wfo_UI())
        self.setLayout(layout)


# class runLoopGroup():
#     def __init__(self, parent=None):
#         self.runGB = QGroupBox("Run Loop")
#         self.runLoop = QSpinBox()
#         self.indexout = QLabel("0")

#     def runLoopWidget(self):
#         layout = QHBoxLayout()
#         layout.addWidget(self.runLoop)
#         layout.addWidget(self.indexout)
#         self.runGB.setLayout(layout)
#         self.runGB.show()
#         return self.runGB


class msTabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(msTabSetting, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.addTab(self.tab1,"Preparation")
        self.addTab(self.tab2,"MS1")
        self.addTab(self.tab3,"Calibration")
        #self.addTab(self.tab4,"Isolation")
        #self.addTab(self.tab5,"MS2")
        
        #tab1 block items
        self.ch1_freq = spinBlock("Frequency (kHz) <1>", TAB0_FREQUENCY_MIN, TAB0_FREQUENCY_MAX)
        self.ch1_amp = spinBlock("Amp (mV) <2>", TAB0_AMP_MIN, TAB0_AMP_MAX)
        self.ch1_offset = spinBlock("Offset (mV) <3>", TAB0_OFFSET_MIN, TAB0_OFFSET_MAX)
        self.run1_btn = QPushButton("Run")
        self.run1_btn.setEnabled(False)

        #tab2 block items
        self.checkNoise = QCheckBox("Noise Filter")
        #self.checkSaveRaw = QCheckBox("Save Raw File")
        self.checkAccu = QCheckBox("Accumulate")
        self.checkNegative = QCheckBox("Negtive Signal")
        self.minMass = spinBlock("Min Mass", 10, 5000)
        self.maxMass = spinBlock("Max Mass",10, 5000)
        self.ms1SetBtn = QPushButton("Set Param")
        #self.ms1Text = QLabel("Run Index")
        #self.ms1Text.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.ms1Index = QLabel("Run Index = 0")
        #self.runLoop = runLoopGroup()
        self.runLoop = spinBlock("Run Loop", RUN_LOOP_MIN, RUN_LOOP_MAX)
        self.ms1RunBtn = QPushButton("Single Run")
        self.ms1RunAllBtn = QPushButton("Run")
        self.ms1StopBtn = QPushButton("Stop")
        self.ms1SaveBtn = QPushButton("Save")
        self.ms1ResetBtn = QPushButton("Reset Index")
        self.ms1RunBtn.setEnabled(False)
        self.ms1RunAllBtn.setEnabled(False)
        self.ms1StopBtn.setEnabled(False)
        self.ms1SaveBtn.setEnabled(False)

        #tab3 block items
        #self.peak = checkSpinBlock("Peak", PEAK_MIN, PEAK_MAX, 0)
        self.currDataBtn = QPushButton("Current Data")
        self.loadDataBtn = QPushButton("Load Data")
        self.Threshold = spinBlock("Threshold (V)", Threshold_MIN, Threshold_MAX, True, 0.01)
        self.Noise = spinBlock("Width (points)", Noise_MIN, Noise_MAX)
        self.caFindBtn = QPushButton("Find Peak")
        self.caSetBtn = QPushButton("Set Peak")
        self.fitBtn = QPushButton("Fitting")
        self.currDataBtn.setEnabled(False)
        self.caFindBtn.setEnabled(False)
        self.caSetBtn.setEnabled(False)
        self.fitBtn.setEnabled(False)

        #tab4 block items
        self.isoFindBtn = QPushButton("Find Peak")
        self.isoSetBtn = QPushButton("Set Peak")
        self.calcuBtn = QPushButton("Calculate Freq.")
        self.startBtn = QPushButton("Start")

        self.Tab1_UI()
        self.Tab2_UI()
        self.Tab3_UI()
        self.Tab4_UI()

    def Tab1_UI(self):
        layout = QHBoxLayout()
        layout.addWidget(self.ch1_freq)
        layout.addWidget(self.ch1_amp)
        layout.addWidget(self.ch1_offset)
        layout.addWidget(self.run1_btn)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.checkNoise, 0, 0, 1, 1)
        layout.addWidget(self.checkNegative, 0, 1, 1, 1)
        layout.addWidget(self.checkAccu, 0, 2, 1, 1 )
        layout.addWidget(self.minMass,0,3,1,1)
        layout.addWidget(self.maxMass,0,4,1,1)
        #layout.addWidget(self.ms1Text, 0, 3, 1, 1)
        layout.addWidget(self.runLoop, 0,5,1,1)
        layout.addWidget(self.ms1Index, 0, 6, 1, 1)
        layout.addWidget(self.ms1SetBtn, 1, 0, 1, 1)
        layout.addWidget(self.ms1RunBtn, 1, 1, 1, 1)
        layout.addWidget(self.ms1RunAllBtn, 1, 2, 1, 1)
        layout.addWidget(self.ms1StopBtn, 1, 3, 1, 1)
        layout.addWidget(self.ms1SaveBtn, 1, 4, 1, 1)
        layout.addWidget(self.ms1ResetBtn, 1, 5, 1, 1)
        self.tab2.setLayout(layout)

    def Tab3_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.Threshold, 0, 0, 1, 1)
        layout.addWidget(self.Noise, 0, 1, 1, 1)
        layout.addWidget(self.currDataBtn, 0, 2, 1, 1)
        layout.addWidget(self.loadDataBtn, 0, 3, 1, 1)
        layout.addWidget(self.caFindBtn, 0, 4, 1, 1)
        layout.addWidget(self.caSetBtn, 0, 5, 1, 1)
        layout.addWidget(self.fitBtn, 0, 6, 1, 1)
        self.tab3.setLayout(layout)

    def Tab4_UI(self):
        layout = QHBoxLayout()
        layout.addWidget(self.isoFindBtn)
        layout.addWidget(self.isoSetBtn)
        layout.addWidget(self.calcuBtn)
        layout.addWidget(self.startBtn)
        self.tab4.setLayout(layout)


class TabPlot(QTabWidget):
    def __init__(self, parent=None):
        super(TabPlot, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.plot1 = output2Plot()
        self.plot2 = output2Plot()
        self.plot1.ax1.set_ylabel("Voltage (V)")
        self.plot1.ax2.set_xlabel("Mass")
        self.plot1.ax2.set_ylabel("Voltage (V)")
        self.plot2.ax1.set_ylabel("Arbiary Uint")
        self.plot2.ax2.set_xlabel("Time (s)")
        self.plot2.ax2.set_ylabel("Arbiary Uint")
        self.addTab(self.tab1,"Mass")
        self.addTab(self.tab2,"TIC")
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


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        #self.plot = output2Plot()
        self.tabPlot = TabPlot()
        self.ms = msTabSetting()
        self.hk = housingKeeping()

        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.ms,0,0,1,1)
        mainLayout.addWidget(self.hk,0,1,2,1)
        #mainLayout.addWidget(self.plot,1,0,1,1)
        mainLayout.addWidget(self.tabPlot,1,0,1,1)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 8)
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
