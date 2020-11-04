import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *


TITLE_TEXT = " NCU FOG Gyro Scope "

MODQ_INDEX = 0
MODR_INDEX = 1
MODQ2_INDEX = 2
MODR2_INDEX = 3
UPPER_BAND_INDEX = 4
LOWER_BAND_INDEX = 5

IGNOR_INDEX = 0
OFFSET_INDEX = 1
THRESHOLD_INDEX = 2
INAGV_INDEX = 3
MVAVG_INDEX = 4 

mod_H_min = 0
mod_H_max = 8191

mod_L_min = -8191
mod_L_max = 0

mod_freq_min = 20
mod_freq_max = 1000000

pi_vth_min = 0
pi_vth_max = 8191

ignor_min = 0
ignor_max = 200

offset_min = -100
offset_max = 100

threshold_min = 0
threshold_max = 500

coeff_min = -1000
coeff_max = 1000

mod_Q_min = 1
mod_Q_max = 1000000

# mod_R_min = 0.0001
# mod_R_max = 1000
# mod_R_step = 0.0001

mod_R_min = 1
mod_R_max = 1000000

upper_band_min = 1
upper_band_max = 100000

lower_band_min = -100000
lower_band_max = -1


class SetKalDialog(QDialog):
    def __init__(self, init_data, parent = None):
        super(SetKalDialog, self).__init__(parent)
        self.setWindowTitle("Kalman Filter")
        self.data = init_data
        self.addItem()
        self.layout()
        self.setValue(self.data)
        self.connectFunction()

    def addItem(self):
        self.modQ = spinBlock("Q", mod_Q_min, mod_Q_max)
        # self.modR = spinBlock("R", mod_R_min, mod_R_max, True, mod_R_step, 4)
        self.modR = spinBlock("R", mod_R_min, mod_R_max)
        self.modQ2 = spinBlock("Q2", mod_Q_min, mod_Q_max)
        self.modR2 = spinBlock("R2", mod_R_min, mod_R_max)
        self.upper_band = spinBlock("Upper Band", upper_band_min, upper_band_max)
        self.lower_band = spinBlock("Lower Band", lower_band_min, lower_band_max)
        self.OKbtn = QPushButton("OK")

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.modQ, 0,0,1,1)
        layout.addWidget(self.modR, 0,1,1,1)
        layout.addWidget(self.modQ2, 1,0,1,1)
        layout.addWidget(self.modR2, 1,1,1,1)
        layout.addWidget(self.upper_band, 2,0,1,1)
        layout.addWidget(self.lower_band, 2,1,1,1)
        layout.addWidget(self.OKbtn, 3,2,1,1)
        self.setLayout(layout)

    def setValue(self, data):
        self.modQ.spin.setValue(int(data[MODQ_INDEX]))
        self.modR.spin.setValue(int(data[MODR_INDEX]))
        self.modQ2.spin.setValue(int(data[MODQ2_INDEX]))
        self.modR2.spin.setValue(int(data[MODR2_INDEX]))
        self.upper_band.spin.setValue(int(data[UPPER_BAND_INDEX]))
        self.lower_band.spin.setValue(int(data[LOWER_BAND_INDEX]))

    def getValue(self):
        self.data[MODQ_INDEX] = self.modQ.spin.value()
        self.data[MODR_INDEX] = self.modR.spin.value()
        self.data[MODQ2_INDEX] = self.modQ2.spin.value()
        self.data[MODR2_INDEX] = self.modR2.spin.value()
        self.data[UPPER_BAND_INDEX] = self.upper_band.spin.value()
        self.data[LOWER_BAND_INDEX] = self.lower_band.spin.value()

    def connectFunction(self):
        self.OKbtn.clicked.connect(self.okButtonPress)

    def okButtonPress(self):
        self.getValue()
        self.close()

    @staticmethod
    def getParameter(init_data, parent = None):
        # print("getParameter")
        # print(init_data)
        dialog2 = SetKalDialog(init_data, parent)
        result = dialog2.exec_()
        return dialog2.data

class SetSignalDialog(QDialog):
    def __init__(self, init_data, parent = None):
        super(SetSignalDialog, self).__init__(parent)
        self.setWindowTitle("Signal Sampling Parameters")
        self.data = init_data
        self.addItem()
        self.layout()
        self.setValue(self.data)
        self.connectFunction()

    def addItem(self):
        # self.ignor = spinLabelBlock("Init Ignor", "Steps = ", "", ignor_min, ignor_max)
        # self.offset = spinLabelBlock("Signal Offset", "Offset (mV) = ", "", offset_min, offset_max)
        # self.threshold = spinLabelBlock("Step Threshold", "Voltage = ", "", threshold_min, threshold_max)
        self.ignor = spinBlock("Init Ignor", ignor_min, ignor_max)
        self.offset = spinBlock("Signal Offset", offset_min, offset_max)
        self.threshold = spinBlock("Step Threshold", threshold_min, threshold_max)

        inavg_list =["AVG1", "AVG2", "AVG4", "AVG8", "AVG16", "AVG32", "AVG64"]
        # self.inavgLabel = QGroupBox("Input Avg Points")
        # self.inavg = QComboBox()
        # self.inavg.addItems(inavg_list)
        self.inavg = comboBlock("Input Avg Points", inavg_list)

        mvavg_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        # self.mvavgLabel = QGroupBox("Moving Average Setting")
        # self.mvavg = QComboBox()
        # self.mvavg.addItems(mvavg_list)
        self.mvavg = comboBlock("Moving Average Setting", mvavg_list)

        self.OKbtn = QPushButton("OK")

    def layout(self):
        # groupLayout1 = QHBoxLayout()
        # groupLayout1.addWidget(self.inavg)
        # self.inavgLabel.setLayout(groupLayout1)

        # groupLayout2 = QHBoxLayout()
        # groupLayout2.addWidget(self.mvavg)
        # self.mvavgLabel.setLayout(groupLayout2)

        layout = QGridLayout()
        layout.addWidget(self.ignor, 0,0,1,1)
        layout.addWidget(self.offset, 0,1,1,1)
        layout.addWidget(self.threshold, 0,2,1,1)
        # layout.addWidget(self.inavgLabel, 1,0,1,1)
        layout.addWidget(self.inavg, 1,0,1,1)
        # layout.addWidget(self.mvavgLabel, 1,1,1,1)
        layout.addWidget(self.mvavg, 1,1,1,1)
        layout.addWidget(self.OKbtn, 2,2,1,1)
        self.setLayout(layout)

    def setValue(self, data):
        self.ignor.spin.setValue(int(self.data[IGNOR_INDEX]))
        self.offset.spin.setValue(int(self.data[OFFSET_INDEX]))
        self.threshold.spin.setValue(int(self.data[THRESHOLD_INDEX]))
        self.inavg.combo.setCurrentIndex(int(self.data[INAGV_INDEX]))
        self.mvavg.combo.setCurrentIndex(int(self.data[MVAVG_INDEX]))

    def getValue(self):
        self.data[IGNOR_INDEX] = self.ignor.spin.value()
        self.data[OFFSET_INDEX] = self.offset.spin.value()
        self.data[THRESHOLD_INDEX] = self.threshold.spin.value()
        self.data[INAGV_INDEX] = self.inavg.combo.currentIndex()
        self.data[MVAVG_INDEX] = self.mvavg.combo.currentIndex()

    def connectFunction(self):
        self.OKbtn.clicked.connect(self.okButtonPress)

    def okButtonPress(self):
        self.getValue()
        self.close()

    @staticmethod
    def getParameter(init_data, parent = None):
        # print("getParameter")
        # print(init_data)
        dialog = SetSignalDialog(init_data, parent)
        result = dialog.exec_()
        return dialog.data

class setFog(QGroupBox):
    def __init__(self,parent=None):
        super(setFog, self).__init__(parent)
        self.setTitle("Fog Parameters")
        self.modH = spinLabelBlock("Mod H", "Voltage (mV) = ", "", mod_H_min, mod_H_max)
        self.modL = spinLabelBlock("Mod L", "Voltage (mV) = ", "", mod_L_min, mod_L_max)
        self.freq = spinLabelBlock("Mod Freq", "Freq (kHz) = ", "", mod_freq_min, mod_freq_max)
        self.twoPi = spinLabelBlock("2Pi Vth", "Voltage (mV) = ", "", pi_vth_min, pi_vth_max)
        self.frame = QGroupBox("Polarity")
        self.poBtn1 = QRadioButton("Positive", self.frame)
        self.poBtn2 = QRadioButton("Negtive", self.frame)
        self.calib = QGroupBox("Calib. Coeff.")
        self.coeff = QLineEdit()
        self.coeff.setValidator(QDoubleValidator(coeff_min, coeff_max, 10))
        self.setUI()

    def setUI(self):
        frameLayout = QHBoxLayout()
        frameLayout.addWidget(self.poBtn1)
        frameLayout.addWidget(self.poBtn2)
        self.frame.setLayout(frameLayout)

        caliblayout = QHBoxLayout()
        caliblayout.addWidget(self.coeff)
        self.calib.setLayout(caliblayout)

        layout = QGridLayout()
        layout.addWidget(self.modH, 0,0,1,2)
        layout.addWidget(self.modL, 1,0,1,2)
        layout.addWidget(self.freq, 2,0,1,2)
        layout.addWidget(self.twoPi, 3,0,1,2)
        layout.addWidget(self.frame, 4,0,1,1)
        layout.addWidget(self.calib, 4,1,1,1)
        self.setLayout(layout)


class setGain(QGroupBox):
    def __init__(self,parent=None):
        super(setGain, self).__init__(parent)
        self.setTitle("Gain Setting")
        self.gainBox1 = QGroupBox("1st Gain Setting")
        self.gainBox2 = QGroupBox("2nd Gain Setting")
        self.gain1pwr = QComboBox()
        self.gain2pwr = QComboBox()
        gain_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
        self.gain1pwr.addItems(gain_list)
        self.gain2pwr.addItems(gain_list)

        self.gain1 = QSpinBox()
        self.fst_label = QLabel(" / 2^")
        self.fst_gain_label = QLabel("1st gain =")
        self.fst_gain_out = QLabel("0")

        self.sec_label = QLabel("1 / 2^") 
        self.sec_gain_label = QLabel("2nd gain =")
        self.sec_gain_out = QLabel("0")
        self.setUI()

    def setUI(self):
        GroupLayout1 = QHBoxLayout()
        GroupLayout1.addWidget(self.gain1)
        GroupLayout1.addWidget(self.fst_label)
        GroupLayout1.addWidget(self.gain1pwr)
        GroupLayout1.addWidget(self.fst_gain_label)
        GroupLayout1.addWidget(self.fst_gain_out)
        self.gainBox1.setLayout(GroupLayout1)

        GroupLayout2 = QHBoxLayout()
        GroupLayout2.addWidget(self.sec_label)
        GroupLayout2.addWidget(self.gain2pwr)
        GroupLayout2.addWidget(self.sec_gain_label)
        GroupLayout2.addWidget(self.sec_gain_out)
        self.gainBox2.setLayout(GroupLayout2)

        layout = QVBoxLayout()
        layout.addWidget(self.gainBox1)
        layout.addWidget(self.gainBox2)
        self.setLayout(layout)


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.net = IPconnectBlock("Connection")
        self.usb = connectBlock("USB Connection")
        self.mode = QGroupBox("Feedback Loop mode")
        self.open = QRadioButton("Open", self.mode)
        self.close = QRadioButton("Close", self.mode)
        self.gain = setGain()
        self.fog = setFog()
        self.start = QPushButton("Start")
        self.getData = QPushButton("Get Data")
        self.stop = QPushButton("Stop")
        self.plot  = output2Plot()
        self.main_UI()
        self.enableSSHsetting(False)
        self.start.setEnabled(False)
        self.stop.setEnabled(False)
        self.getData.setEnabled(False)

    def main_UI(self):
        modelayout = QHBoxLayout()
        modelayout.addWidget(self.open)
        modelayout.addWidget(self.close)

        self.mode.setLayout(modelayout)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.plot, 0,0,5,1)
        mainLayout.addWidget(self.net.layout2(), 0,1,1,3)
        mainLayout.addWidget(self.usb.layout1(), 0,4,1,3)
        mainLayout.addWidget(self.mode, 1,1,1,6)
        mainLayout.addWidget(self.gain, 2,1,1,6)
        mainLayout.addWidget(self.fog, 3,1,1,6)
        mainLayout.addWidget(self.start, 4,1,1,2)
        mainLayout.addWidget(self.getData, 4,3,1,2)
        mainLayout.addWidget(self.stop, 4,5,1,2)
        mainLayout.setRowStretch(0, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 3)
        mainLayout.setRowStretch(3, 7)
        mainLayout.setRowStretch(4, 1)
        mainLayout.setColumnStretch(0, 20)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        mainLayout.setColumnStretch(4, 1)
        mainLayout.setColumnStretch(5, 1)
        mainLayout.setColumnStretch(6, 1)
        self.setLayout(mainLayout)

    def enableSSHsetting(self, flag):
        self.open.setEnabled(flag)
        self.close.setEnabled(flag)
        self.gain.gain1.setEnabled(flag)
        self.gain.gain1pwr.setEnabled(flag)
        self.gain.gain2pwr.setEnabled(flag)
        self.fog.modH.spin.setEnabled(flag)
        self.fog.modL.spin.setEnabled(flag)
        self.fog.freq.spin.setEnabled(flag)
        self.fog.twoPi.spin.setEnabled(flag)
        self.fog.poBtn1.setEnabled(flag)
        self.fog.poBtn2.setEnabled(flag)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
