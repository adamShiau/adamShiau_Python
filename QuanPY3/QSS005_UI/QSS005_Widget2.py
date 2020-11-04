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

# scan parmater
SHOW_IMG = "set/showFig.png"

MS1_CH1_FREQ_MIN = 1  # kHz
MS1_CH1_FREQ_MAX = 1500 # kHz
MS1_SCAN_PERIOD_MIN = 1    # ms
MS1_SCAN_PERIOD_MAX = 1000 # ms
MS1_CH1_TRAPPING_AMP_MIN = 0    # mV
MS1_CH1_TRAPPING_AMP_MAX = 1000 # mV
MS1_CH1_RAMP_MIN = 0    # mV
MS1_CH1_RAMP_MAX = 1000 # mV
MS1_CH1_FINAL_AMP_MIN = 0    # mV
MS1_CH1_FINAL_AMP_MAX = 1000 # mV
MS1_CH1_OFFSET_MIN = -30 #mV
MS1_CH1_OFFSET_MAX = 1000  #mV

TTL_DURATION_MIN = 5    # us
TTL_DURATION_MAX = 1000 # us
DAMPING_DURA_MIN = 0    # us
DAMPING_DURA_MAX = 1000 # us , <= ttl_dura-5
MS1_CH2_CHIRP_AMP_MIN = 10    # mV
MS1_CH2_CHIRP_AMP_MAX = 10000 # mV
ISO_CH2_CHIRP_AMP_MIN = 10    # mV
ISO_CH2_CHIRP_AMP_MAX = 10000 # mV
MS1_CH2_FINAL_FREQ_MIN = 10 # kHz
MS1_CH2_FINAL_FREQ_MAX = 1000 # kHz

MSMS_T1_MIN = 30 #ms
MSMS_T1_MAX = 100 #ms
# MSMS_TIME_MIN = 10 #ms
# MSMS_TIME_MAX = 100 #ms
MSMS_T2_MIN = 50 #ms
MSMS_T2_MAX = 100 #ms
DELAY_TIME_MIN = 10 #ms
DELAY_TIME_MAX = 200 #ms

# CYCLE_MIN = -100
# CYCLE_MAX = 100
# GAIN_P_MIN = 1
# GAIN_P_MAX = 100
# GAIN_N_MIN = 1
# GAIN_N_MAX = 100

# RESET_MIN = 0
# RESET_MAX = 2000
# HOLD_MIN = 0
# HOLD_MAX = 1000
# INT_MIN = 0
# INT_MAX = 2500

# system parameter
LEVEL_MIN = 1
LEVEL_MAX = 10
THRESHOLD_MIN = -10
THRESHOLD_MAX = 10
THRESHOLD_STEP = 0.01
NOISE_WIDTH_MIN = 1
NOISE_WIDTH_MAX = 100

MASS_CENTER_MIN = 0
MASS_CENTER_MAX = 1000
MASS_RANGE_MIN = 0.1
MASS_RANGE_MAX = 100
MASS_RANGE_STEP = 0.1

RF_VOLTAGE_GAIN_MIN = 30
RF_VOLTAGE_GAIN_MAX = 10000
R0_MIN = 0     #mm
R0_MAX = 10    #mm
R0_STEP = 0.01

PEAK_TEXT = "Peak number must largger than 2"
PEAK_MIN = 0
PEAK_MAX = 10000
PEAK_INDEX_MIN = 1
PEAK_INDEX_MAX = 100

RUN_LOOP_MIN = 1
RUN_LOOP_MAX = 500000

TITLE_TEXT = " Acdemic Sincica GRC Mass Spectrometer "

class scanDialog(QDialog):
    def __init__(self, init_data, parent = None):
        super(scanDialog, self).__init__(parent)
        self.setWindowTitle("Scan Parameter")
        self.showFig = QLabel()
        fig = QPixmap(SHOW_IMG)
        self.showFig.setPixmap(fig)
        self.showFig.show()

        self.ch1_freq = spinBlock("CH1 Frequency (kHz)", MS1_CH1_FREQ_MIN, MS1_CH1_FREQ_MAX)
        self.scan_period = spinBlock("Scan Period (ms)", MS1_SCAN_PERIOD_MIN, MS1_SCAN_PERIOD_MAX)
        self.ch1_trapping_amp = spinBlock("CH1 Trapping Amplitude (mV)", MS1_CH1_TRAPPING_AMP_MIN, MS1_CH1_TRAPPING_AMP_MAX)
        self.ch1_ramp = spinBlock("CH1 Ramp Amplitude (mV)", MS1_CH1_RAMP_MIN, MS1_CH1_RAMP_MAX)
        self.ch1_final_amp = spinBlock("CH1 Final Amplitude (mV)", MS1_CH1_FINAL_AMP_MIN, MS1_CH1_FINAL_AMP_MAX)
        self.ch1_offset = spinBlock("CH1 Offset Amplitude (mV)", MS1_CH1_OFFSET_MIN, MS1_CH1_OFFSET_MAX)

        self.ttl_duration = spinBlock("TTL Duration (ms)", TTL_DURATION_MIN, TTL_DURATION_MAX)
        self.damping_dura = spinBlock("Damping Duration (ms)", DAMPING_DURA_MIN, DAMPING_DURA_MAX)

        self.ms1_chirp_amp = spinBlock("MS1 Chirp Amp (mv)", MS1_CH2_CHIRP_AMP_MIN, MS1_CH2_CHIRP_AMP_MAX)
        self.iso_chirp_amp = spinBlock("ISO Chirp Amp (mv)", ISO_CH2_CHIRP_AMP_MIN, ISO_CH2_CHIRP_AMP_MAX)
        ch2_freq_factor_list = ["1/2" , "1/3" , "1/4"]
        self.ch2_freq_factor = comboBlock("CH2 Freq Ratio", ch2_freq_factor_list)
        self.ch2_final_freq = spinBlock("CH2 Chirp End Frequency (kHz)", MS1_CH2_FINAL_FREQ_MIN, MS1_CH2_FINAL_FREQ_MAX)

        self.msms_t1 = spinBlock("MSMS T1 (ms)", MSMS_T1_MIN, MSMS_T1_MAX)
        # self.msms_time = spinBlock("MSMS Time (ms)", MSMS_TIME_MIN, MSMS_TIME_MAX)
        self.msms_t2 = spinBlock("MSMS T2 (ms)", MSMS_T2_MIN, MSMS_T2_MAX)
        self.msms_amp = spinBlock("MSMS Amp (mv)", MS1_CH2_CHIRP_AMP_MIN, MS1_CH2_CHIRP_AMP_MAX)
        self.delay_time = spinBlock("Delay Time (ms)", DELAY_TIME_MIN, DELAY_TIME_MAX)

        self.OKbtn = QPushButton("OK")
        self.data = init_data

        self.ttl_duration.spin.valueChanged.connect(self.update_damp)
        self.damping_dura.spin.valueChanged.connect(self.update_ttl)
        self.layout()
        self.connectFunction()
        self.setSpinValue(self.data)

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.showFig,0,0,1,5)

        layout.addWidget(self.ch1_freq,1,0,1,1)   
        layout.addWidget(self.scan_period,1,1,1,1)
        layout.addWidget(self.ch1_trapping_amp,1,2,1,1) 
        layout.addWidget(self.ch1_ramp,1,3,1,1)
        layout.addWidget(self.ch1_final_amp,1,4,1,1)

        layout.addWidget(self.ch1_offset,2,0,1,1) 
        layout.addWidget(self.ttl_duration,2,1,1,1)
        layout.addWidget(self.damping_dura,2,2,1,1)
        layout.addWidget(self.ms1_chirp_amp,2,3,1,1)
        layout.addWidget(self.iso_chirp_amp,2,4,1,1)

        layout.addWidget(self.ch2_freq_factor,3,0,1,1)
        layout.addWidget(self.ch2_final_freq,3,1,1,1)
        layout.addWidget(self.msms_t1,3,2,1,1)
        # layout.addWidget(self.msms_time,3,2,1,1)
        layout.addWidget(self.msms_t2,3,3,1,1)
        layout.addWidget(self.msms_amp,3,4,1,1)

        layout.addWidget(self.delay_time,4,0,1,1)
        layout.addWidget(self.OKbtn,4,4,1,1)

        self.setLayout(layout)

    def setSpinValue(self, data):
        self.ch1_freq.spin.setValue(int(data[0]))
        self.scan_period.spin.setValue(int(data[1]))
        self.ch1_trapping_amp.spin.setValue(int(data[2]))
        self.ch1_ramp.spin.setValue(int(data[3]))
        self.ch1_final_amp.spin.setValue(int(data[4]))
        self.ch1_offset.spin.setValue(int(data[5]))

        self.ttl_duration.spin.setValue(int(data[6]))
        self.damping_dura.spin.setValue(int(data[7]))

        self.ms1_chirp_amp.spin.setValue(int(data[8]))
        self.iso_chirp_amp.spin.setValue(int(data[15]))
        ms1_ch2_freq_factor = float(data[9])
        if (ms1_ch2_freq_factor == 0.25):
            self.ch2_freq_factor.combo.setCurrentIndex(2)
        elif (ms1_ch2_freq_factor == 0.33333333):
            self.ch2_freq_factor.combo.setCurrentIndex(1)
        else:   #elif (ms1_ch2_freq_factor == 0.5):
            self.ch2_freq_factor.combo.setCurrentIndex(0)
        self.ch2_final_freq.spin.setValue(int(data[10]))

        self.msms_t1.spin.setValue(int(data[11]))
        # self.msms_time.spin.setValue(int(data[12]))
        self.msms_t2.spin.setValue(int(data[12]))
        self.msms_amp.spin.setValue(int(data[13]))
        self.delay_time.spin.setValue(int(data[14]))

    def getSpinValue(self):
        data = [100, 1, 0, 0, 0, 0, 1, 1, 10, 0.5, 100, 30, 50, 10, 10, 10]

        data[0] = self.ch1_freq.spin.value()
        data[1] = self.scan_period.spin.value()
        data[2] = self.ch1_trapping_amp.spin.value()
        data[3] = self.ch1_ramp.spin.value()
        data[4] = self.ch1_final_amp.spin.value()
        data[5] = self.ch1_offset.spin.value()

        data[6] = self.ttl_duration.spin.value()
        data[7] = self.damping_dura.spin.value()

        data[8] = self.ms1_chirp_amp.spin.value()
        data[15] = self.iso_chirp_amp.spin.value()
        ms1_ch2f_ratio = self.ch2_freq_factor.combo.currentIndex()
        if (ms1_ch2f_ratio == 2):
            ms1_ch2_freq_factor = 0.25
        elif (ms1_ch2f_ratio == 1):
            ms1_ch2_freq_factor = 0.33333333
        else:   #elif (ms1_ch2f_ratio) == 0:
            ms1_ch2_freq_factor = 0.5
        data[9] = float(ms1_ch2_freq_factor)
        data[10] = self.ch2_final_freq.spin.value()

        data[11] = self.msms_t1.spin.value()
        # data[12] = self.msms_time.spin.value()
        data[12] = self.msms_t2.spin.value()
        data[13] = self.msms_amp.spin.value()
        data[14] = self.delay_time.spin.value()

        return data

    def update_damp(self):
        ttl_value = self.ttl_duration.spin.value()
        #print ttl_value
        #self.damping_dura.coarse.setRange(DAMPING_DURA_MIN, ttl_value)
        self.damping_dura.spin.setRange(DAMPING_DURA_MIN, ttl_value-5)

    def update_ttl(self):
        damp_value = self.damping_dura.spin.value()
        #print damp_value
        #self.ttl_duration.coarse.setRange(damp_value, TTL_DURATION_MAX)
        self.ttl_duration.spin.setRange(damp_value+5, TTL_DURATION_MAX)

    def connectFunction(self):
        self.OKbtn.clicked.connect(self.okButtonPress)

    def okButtonPress(self):
        self.data = self.getSpinValue()
        self.close()

    @staticmethod
    def getParameter(init_data, parent = None):
        dialog = scanDialog(init_data, parent)
        result = dialog.exec_()
        return dialog.data


class sysDialog(QDialog):
    def __init__(self, init_data, parent = None):
        super(sysDialog, self).__init__(parent)
        self.setWindowTitle("System Parameter")

        self.level = spinBlock("Noise Filter Level", LEVEL_MIN, LEVEL_MAX)
        self.rfVolGain = spinBlock("Rf Voltage Gain", RF_VOLTAGE_GAIN_MIN, RF_VOLTAGE_GAIN_MAX)
        self.threshold = spinBlock("Threshold (V)", THRESHOLD_MIN, THRESHOLD_MAX, True, THRESHOLD_STEP)
        self.noise_width = spinBlock("Width (points)", NOISE_WIDTH_MIN, NOISE_WIDTH_MAX)
        self.xicMassCenter = spinBlock("Xic Mass Center", MASS_CENTER_MIN, MASS_CENTER_MAX)
        self.xicMassRange = spinBlock("Xic Mass Range", MASS_RANGE_MIN, MASS_RANGE_MAX, True, MASS_RANGE_STEP)
        self.isoMassCenter = spinBlock("Isolation Mass Center", MASS_CENTER_MIN, MASS_CENTER_MAX)
        self.isoMassRange = spinBlock("Isolation Mass Range", MASS_RANGE_MIN, MASS_RANGE_MAX, True, MASS_RANGE_STEP)
        self.r0 = spinBlock("R0", R0_MIN, R0_MAX, True, R0_STEP)
        self.z0 = spinBlock("Z0", R0_MIN, R0_MAX, True, R0_STEP)

        #self.cycle = spinBlock("ADC DC <12>", CYCLE_MIN, CYCLE_MAX)
        #self.gain_p = spinBlock("ADC GAIN P", GAIN_P_MIN, GAIN_P_MAX)
        #self.gain_n = spinBlock("ADC GAIN N", GAIN_N_MIN, GAIN_N_MAX)
        #self.reset = spinBlock("Reset", RESET_MIN, RESET_MAX)
        #self.hold = spinBlock("Hold", HOLD_MIN, HOLD_MAX)
        #self.int = spinBlock("Int", INT_MIN, INT_MAX)

        self.OKbtn = QPushButton("OK")
        self.data = init_data

        self.layout()
        self.connectFunction()
        self.setSpinValue(self.data)

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.level,0,0,1,1)
        layout.addWidget(self.rfVolGain,0,1,1,1)

        layout.addWidget(self.threshold,1,0,1,1)
        layout.addWidget(self.noise_width,1,1,1,1)

        layout.addWidget(self.xicMassCenter,2,0,1,1)
        layout.addWidget(self.xicMassRange,2,1,1,1)

        layout.addWidget(self.isoMassCenter,3,0,1,1)
        layout.addWidget(self.isoMassRange,3,1,1,1)

        layout.addWidget(self.r0,4,0,1,1)
        layout.addWidget(self.z0,4,1,1,1)

        #layout.addWidget(self.cycle,2,1,1,1)
        #layout.addWidget(self.gain_p,2,2,1,1)
        #layout.addWidget(self.gain_n,2,3,1,1)
        #layout.addWidget(self.reset,3,0,1,1)
        #layout.addWidget(self.hold,3,1,1,1)
        #layout.addWidget(self.int,3,2,1,1)

        layout.addWidget(self.OKbtn,5,1,1,1)

        self.setLayout(layout)

    def setSpinValue(self, data):
        self.level.spin.setValue(int(data[0]))
        self.threshold.spin.setValue(float(data[1]))
        self.noise_width.spin.setValue(int(data[2]))
        self.xicMassCenter.spin.setValue(int(data[3]))
        self.xicMassRange.spin.setValue(float(data[4]))
        self.isoMassCenter.spin.setValue(int(data[5]))
        self.isoMassRange.spin.setValue(float(data[6]))
        self.rfVolGain.spin.setValue(int(data[7]))
        self.r0.spin.setValue(float(data[8]))
        self.z0.spin.setValue(float(data[9]))


    def getSpinValue(self):
        data = [1, 0.0, 1, 0, 0.1, 0, 0.1, 30, 0.67, 0.52]

        data[0] = self.level.spin.value()
        data[1] = self.threshold.spin.value()
        data[2] = self.noise_width.spin.value()
        data[3] = self.xicMassCenter.spin.value()
        data[4] = self.xicMassRange.spin.value()
        data[5] = self.isoMassCenter.spin.value()
        data[6] = self.isoMassRange.spin.value()
        data[7] = self.rfVolGain.spin.value()
        data[8] = self.r0.spin.value()
        data[9] = self.z0.spin.value()

        return data

    def connectFunction(self):
        self.OKbtn.clicked.connect(self.okButtonPress)

    def okButtonPress(self):
        self.data = self.getSpinValue()
        self.close()

    @staticmethod
    def getParameter(init_data, parent = None):
        dialog = sysDialog(init_data, parent)
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


class msTabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(msTabSetting, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.addTab(self.tab1,"Preparation")
        self.addTab(self.tab2,"MS1")
        self.addTab(self.tab3,"Calibration")

        #tab1 block items
        self.ch1_freq = spinBlock("Frequency (kHz) <1>", TAB0_FREQUENCY_MIN, TAB0_FREQUENCY_MAX)
        self.ch1_amp = spinBlock("Amp (mV) <2>", TAB0_AMP_MIN, TAB0_AMP_MAX)
        self.ch1_offset = spinBlock("Offset (mV) <3>", TAB0_OFFSET_MIN, TAB0_OFFSET_MAX)
        self.run1_btn = QPushButton("Run")

        self.run1_btn.setEnabled(False)

        #tab2 block items
        self.mode = QGroupBox("Running Mode")
        self.ms1  = QRadioButton("MS1")
        self.isolation = QRadioButton("Isolation")
        self.msms = QRadioButton("MS-MS")
        self.ms1.setChecked(True)

        self.checkNoise = QCheckBox("Noise Filter")
        # self.checkAccu = QCheckBox("Accumulate")
        self.checkNegative = QCheckBox("Negative Signal")
        self.checkTic = QCheckBox("Tic / Xic")

        self.scanSetBtn = QPushButton("Scan Param")
        self.sysSetBtn = QPushButton("System Param")

        #self.runLoop = runLoopGroup()
        self.runLoop = spinBlock("Run Loop", RUN_LOOP_MIN, RUN_LOOP_MAX)
        self.ms1RunIndex = QLabel("Run Index = ")
        self.ms1RunIndex.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.ms1Index = QLabel("0")
        self.ms1ResetBtn = QPushButton("Reset Index")

        self.ms1RunBtn = QPushButton("Single Run")
        self.ms1RunAllBtn = QPushButton("Run")
        self.ms1StopBtn = QPushButton("Stop")
        self.ms1SaveBtn = QPushButton("Save")

        self.ms1RunBtn.setEnabled(False)
        self.ms1RunAllBtn.setEnabled(False)
        self.ms1StopBtn.setEnabled(False)
        self.ms1SaveBtn.setEnabled(False)

        #tab3 block items
        #self.peak = checkSpinBlock("Peak", PEAK_MIN, PEAK_MAX, 0)
        self.currDataBtn = QPushButton("Current Data")
        self.loadDataBtn = QPushButton("Load Data")
        self.threshold = spinBlock("Threshold (V)", THRESHOLD_MIN, THRESHOLD_MAX, True, THRESHOLD_STEP)
        self.noise_width = spinBlock("Width (points)", NOISE_WIDTH_MIN, NOISE_WIDTH_MAX)
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
        
    def Tab1_UI(self):
        layout = QHBoxLayout()
        layout.addWidget(self.ch1_freq)
        layout.addWidget(self.ch1_amp)
        layout.addWidget(self.ch1_offset)
        layout.addWidget(self.run1_btn)
        self.tab1.setLayout(layout)

    def Tab2_UI(self):
        modelayout = QHBoxLayout()
        modelayout.addWidget(self.ms1)
        modelayout.addWidget(self.isolation)
        modelayout.addWidget(self.msms)
        self.mode.setLayout(modelayout)

        layout = QGridLayout()
        layout.addWidget(self.mode, 0, 0, 1, 3)
        layout.addWidget(self.checkNoise, 0, 3, 1, 1)
        layout.addWidget(self.checkNegative, 0, 4, 1, 1)
        layout.addWidget(self.checkTic, 0, 5, 1, 1 )
        layout.addWidget(self.scanSetBtn, 0, 6, 1, 1)
        layout.addWidget(self.sysSetBtn, 0, 7, 1, 1)

        layout.addWidget(self.runLoop, 1, 0, 1, 1)
        layout.addWidget(self.ms1RunIndex, 1, 1, 1, 1)
        layout.addWidget(self.ms1Index, 1, 2, 1, 1)
        layout.addWidget(self.ms1ResetBtn, 1, 3, 1, 1)
        layout.addWidget(self.ms1RunBtn, 1, 4, 1, 1)
        layout.addWidget(self.ms1RunAllBtn, 1, 5, 1, 1)
        layout.addWidget(self.ms1StopBtn, 1, 6, 1, 1)
        layout.addWidget(self.ms1SaveBtn, 1, 7, 1, 1)
        self.tab2.setLayout(layout)

    def Tab3_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.threshold, 0, 0, 1, 1)
        layout.addWidget(self.noise_width, 0, 1, 1, 1)
        layout.addWidget(self.currDataBtn, 0, 2, 1, 1)
        layout.addWidget(self.loadDataBtn, 0, 3, 1, 1)
        layout.addWidget(self.caFindBtn, 0, 4, 1, 1)
        layout.addWidget(self.caSetBtn, 0, 5, 1, 1)
        layout.addWidget(self.fitBtn, 0, 6, 1, 1)
        self.tab3.setLayout(layout)


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
