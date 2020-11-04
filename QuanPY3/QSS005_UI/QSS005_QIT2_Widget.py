import os
import sys
sys.path.append("../")
from py3lib.QuGUIclass import *

# SETTING_FILEPATH = "set"
# SETTING_FILENAME = "set/setting.txt"

# DC parameter
Freq_Min = 0
Freq_Max = 1500
Freq_Step = 0.1
Freq_Decimals = 1

Cdc_Min = 0
Cdc_Max = 50
Cdc_Step = 0.0001
Cdc_Decimals = 4

Crf_Min = 0
Crf_Max = 50
Crf_Step = 0.0001
Crf_Decimals = 4

MASS_MIN = 10
MASS_MAX = 500  
MASS_STEP = 1

Sample_Time_Min = 300 #ms
Sample_Time_Max = 5000 #ms

# TIC parameter
DataPts_Min = 10
DataPts_Max = 16384

Rolling_Min = 1
Rolling_Max = 20

Delay_Time_Min = 50 #ms
Delay_Time_Max = 500 #ms

OFFSET_MIN = -1000 #mV
OFFSET_MAX = 1000  #mV
OFFSET_STEP = 0.01
OFFSET_Decimals = 2

MASS_CENTER_MIN = 0
MASS_CENTER_MAX = 1000

MASS_RANGE_MIN = 0.1
MASS_RANGE_MAX = 1000
MASS_RANGE_STEP = 0.1
MASS_RANGE_Decimals = 1

Threshold_Min = -2
Threshold_Max = 10
Threshold_Step = 0.01
Threshold_Decimals = 2

Width_Min = 1
Width_Max = 100

TITLE_TEXT = "QIT2"

class MassDialog(QDialog):
    def __init__(self, init_data, can_select, parent = None):
        super(MassDialog, self).__init__(parent)
        if (can_select):
            self.setWindowTitle("Modify Optimization Parameter")
        else:
            self.setWindowTitle("Add Mass Table")

        self.select_label = QLabel("Select    ")
        self.cdc_label = QLabel("      Cdc      ")
        self.crf_label = QLabel("      Crf      ")
        self.mass_label = QLabel("     Mass     ")

        self.select1 = QCheckBox("")
        self.select2 = QCheckBox("")
        self.select3 = QCheckBox("")
        self.select4 = QCheckBox("")
        self.select5 = QCheckBox("")
        self.select6 = QCheckBox("")

        self.cdc1 = QLabel("")
        self.cdc2 = QLabel("")
        self.cdc3 = QLabel("")
        self.cdc4 = QLabel("")
        self.cdc5 = QLabel("")
        self.cdc6 = QLabel("")

        self.crf1 = QLabel("")
        self.crf2 = QLabel("")
        self.crf3 = QLabel("")
        self.crf4 = QLabel("")
        self.crf5 = QLabel("")
        self.crf6 = QLabel("")

        self.mass1 = QLabel("")
        self.mass2 = QLabel("")
        self.mass3 = QLabel("")
        self.mass4 = QLabel("")
        self.mass5 = QLabel("")
        self.mass6 = QLabel("")

        self.cdc1.setAlignment(Qt.AlignCenter)
        self.cdc2.setAlignment(Qt.AlignCenter)
        self.cdc3.setAlignment(Qt.AlignCenter)
        self.cdc4.setAlignment(Qt.AlignCenter)
        self.cdc5.setAlignment(Qt.AlignCenter)
        self.cdc6.setAlignment(Qt.AlignCenter)

        self.crf1.setAlignment(Qt.AlignCenter)
        self.crf2.setAlignment(Qt.AlignCenter)
        self.crf3.setAlignment(Qt.AlignCenter)
        self.crf4.setAlignment(Qt.AlignCenter)
        self.crf5.setAlignment(Qt.AlignCenter)
        self.crf6.setAlignment(Qt.AlignCenter)

        self.mass1.setAlignment(Qt.AlignCenter)
        self.mass2.setAlignment(Qt.AlignCenter)
        self.mass3.setAlignment(Qt.AlignCenter)
        self.mass4.setAlignment(Qt.AlignCenter)
        self.mass5.setAlignment(Qt.AlignCenter)
        self.mass6.setAlignment(Qt.AlignCenter)

        self.status = QLabel("")
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.red)
        self.status.setPalette(pe)
        self.OKbtn = QPushButton("OK")
        self.OKbtn.clicked.connect(lambda:self.okButtonPress(can_select))

        self.select1.setEnabled(False)
        self.select2.setEnabled(False)
        self.select3.setEnabled(False)
        self.select4.setEnabled(False)
        self.select5.setEnabled(False)
        self.select6.setEnabled(False)

        self.data = init_data
        self.setData2table(init_data, can_select)
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.select_label, 0, 0, 1, 1)
        layout.addWidget(self.cdc_label, 0, 1, 1, 1)
        layout.addWidget(self.crf_label, 0, 2, 1, 1)
        layout.addWidget(self.mass_label, 0, 3, 1, 1)

        layout.addWidget(self.select1, 1, 0, 1, 1)
        layout.addWidget(self.select2, 2, 0, 1, 1)
        layout.addWidget(self.select3, 3, 0, 1, 1)
        layout.addWidget(self.select4, 4, 0, 1, 1)
        layout.addWidget(self.select5, 5, 0, 1, 1)
        layout.addWidget(self.select6, 6, 0, 1, 1)

        layout.addWidget(self.cdc1, 1, 1, 1, 1)
        layout.addWidget(self.cdc2, 2, 1, 1, 1)
        layout.addWidget(self.cdc3, 3, 1, 1, 1)
        layout.addWidget(self.cdc4, 4, 1, 1, 1)
        layout.addWidget(self.cdc5, 5, 1, 1, 1)
        layout.addWidget(self.cdc6, 6, 1, 1, 1)

        layout.addWidget(self.crf1, 1, 2, 1, 1)
        layout.addWidget(self.crf2, 2, 2, 1, 1)
        layout.addWidget(self.crf3, 3, 2, 1, 1)
        layout.addWidget(self.crf4, 4, 2, 1, 1)
        layout.addWidget(self.crf5, 5, 2, 1, 1)
        layout.addWidget(self.crf6, 6, 2, 1, 1)

        layout.addWidget(self.mass1, 1, 3, 1, 1)
        layout.addWidget(self.mass2, 2, 3, 1, 1)
        layout.addWidget(self.mass3, 3, 3, 1, 1)
        layout.addWidget(self.mass4, 4, 3, 1, 1)
        layout.addWidget(self.mass5, 5, 3, 1, 1)
        layout.addWidget(self.mass6, 6, 3, 1, 1)

        layout.addWidget(self.status, 7, 0, 1, 3)
        layout.addWidget(self.OKbtn, 7, 3, 1, 1)
        self.setLayout(layout)

    def setData2table(self, data, can_select):
        total = len(data)
        # print("total = " + str(total))
        if (total > 0):
            self.cdc1.setText(str(data[0][1]))
            self.crf1.setText(str(data[0][2]))
            self.mass1.setText(str(data[0][3]))
            self.select1.setChecked(data[0][0])
            if (can_select):
                self.select1.setEnabled(True)
        else:
            self.cdc1.setText(" - ")
            self.crf1.setText(" - ")
            self.mass1.setText(" - ")

        if (total > 1):
            self.cdc2.setText(str(data[1][1]))
            self.crf2.setText(str(data[1][2]))
            self.mass2.setText(str(data[1][3]))
            self.select2.setChecked(data[1][0])
            if (can_select):
                self.select2.setEnabled(True)
        else:
            self.cdc2.setText(" - ")
            self.crf2.setText(" - ")
            self.mass2.setText(" - ")

        if (total > 2):
            self.cdc3.setText(str(data[2][1]))
            self.crf3.setText(str(data[2][2]))
            self.mass3.setText(str(data[2][3]))
            self.select3.setChecked(data[2][0])
            if (can_select):
                self.select3.setEnabled(True)
        else:
            self.cdc3.setText(" - ")
            self.crf3.setText(" - ")
            self.mass3.setText(" - ")

        if (total > 3):
            self.cdc4.setText(str(data[3][1]))
            self.crf4.setText(str(data[3][2]))
            self.mass4.setText(str(data[3][3]))
            self.select4.setChecked(data[3][0])
            if (can_select):
                self.select4.setEnabled(True)
        else:
            self.cdc4.setText(" - ")
            self.crf4.setText(" - ")
            self.mass4.setText(" - ")

        if (total > 4):
            self.cdc5.setText(str(data[4][1]))
            self.crf5.setText(str(data[4][2]))
            self.mass5.setText(str(data[4][3]))
            self.select5.setChecked(data[4][0])
            if (can_select):
                self.select5.setEnabled(True)
        else:
            self.cdc5.setText(" - ")
            self.crf5.setText(" - ")
            self.mass5.setText(" - ")

        if (total > 5):
            self.cdc6.setText(str(data[5][1]))
            self.crf6.setText(str(data[5][2]))
            self.mass6.setText(str(data[5][3]))
            self.select6.setChecked(data[5][0])
            if (can_select):
                self.select6.setEnabled(True)
        else:
            self.cdc6.setText(" - ")
            self.crf6.setText(" - ")
            self.mass6.setText(" - ")

    def checkSelect(self):
        selectFlag = False
        total = len(self.data)
        if (total > 0):
            self.data[0][0] = self.select1.isChecked()
        if (total > 1):
            self.data[1][0] = self.select2.isChecked()
        if (total > 2):
            self.data[2][0] = self.select3.isChecked()
        if (total > 3):
            self.data[3][0] = self.select4.isChecked()
        if (total > 4):
            self.data[4][0] = self.select5.isChecked()
        if (total > 5):
            self.data[5][0] = self.select6.isChecked()
        for i in range(0, total):
            selectFlag = selectFlag + self.data[i][0]
        return selectFlag

    def checkDoubleMass(self):
        doubleMass = False
        tempMass = []
        total = len(self.data)
        for i in range(0, total):
            if (self.data[i][0] == True):
                tempLen = len(tempMass)
                for j in range(0, tempLen):
                    if (self.data[i][3] == tempMass[j]):
                        doubleMass = True
                        break
                tempMass.append(self.data[i][3])
                # print(tempMass)
        return doubleMass

    def okButtonPress(self, can_select):
        if (can_select == False):
            self.close()
        else:
            if (self.checkSelect() < 2):
                self.status.setText("At least two data must be selected")
            elif (self.checkDoubleMass()):
                self.status.setText("The same mass data has different parameter")
            else:
                self.status.setText("")
                self.close()

    @staticmethod
    def getParameter(init_data, can_select, parent = None):
        dialog = MassDialog(init_data, can_select, parent)
        result = dialog.exec_()
        # print("widget UI")
        return dialog.data


class housingKeeping(QWidget):
    def __init__(self, parent=None):
        super(housingKeeping, self).__init__(parent)
        self.net = IPconnectBlock("Major Connection")
        self.FHedit = editBlock("File Header")

        self.HK_UI()

    def HK_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.net.layout1())
        layout.addWidget(self.FHedit)
        self.setLayout(layout)


class DC_Parameter(QWidget):
    def __init__(self, parent=None):
        super(DC_Parameter, self).__init__(parent)
        self.frame = QGroupBox("ADC input channel")
        self.chBtn1 = QRadioButton("CH 0", self.frame)
        self.chBtn1.setChecked(True)  # select by default
        self.chBtn2 = QRadioButton("CH 1", self.frame)

        self.freq = spinBlock("RF Frequency (kHz)", Freq_Min, Freq_Max)
        self.cdc = spinBlock("Cdc", Cdc_Min, Cdc_Max, True, Cdc_Step, Cdc_Decimals)
        self.crf = spinBlock("Crf", Crf_Min, Crf_Max, True, Crf_Step, Crf_Decimals)
        self.mass = spinBlock("Mass", MASS_MIN, MASS_MAX)
        self.sample_time = spinBlock("Sampling Period (ms)", Sample_Time_Min, Sample_Time_Max)

        self.runBtn = QPushButton("Run")
        self.stopBtn = QPushButton("Stop")
        self.addBtn = QPushButton("Add to Table")
        # self.zeroBtn = QPushButton("Zero Calibration")

        self.runBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)
        # self.addBtn.setEnabled(False)
        # self.zeroBtn.setEnabled(False)

        self.DC_Parameter_UI()

    def DC_Parameter_UI(self):
        layout = QGridLayout()
        frameLayout = QHBoxLayout()
        frameLayout.addWidget(self.chBtn1)
        frameLayout.addWidget(self.chBtn2)
        self.frame.setLayout(frameLayout)

        layout.addWidget(self.freq,0,0,1,1)
        layout.addWidget(self.cdc,0,1,1,1)
        layout.addWidget(self.crf,0,2,1,1)
        layout.addWidget(self.mass,0,3,1,1)
        layout.addWidget(self.sample_time,0,4,1,1)

        layout.addWidget(self.frame,1,0,1,1)
        layout.addWidget(self.runBtn,1,2,1,1)
        layout.addWidget(self.stopBtn,1,3,1,1)
        layout.addWidget(self.addBtn,1,4,1,1)
        # layout.addWidget(self.zeroBtn,1,4,1,1)

        self.setLayout(layout)


class Mass_Filter(QWidget):
    def __init__(self, parent=None):
        super(Mass_Filter, self).__init__(parent)
        self.frame1 = QGroupBox("Polarity")
        self.poBtn1 = QRadioButton("Positive", self.frame1)
        self.poBtn1.setChecked(True)  # select by default
        self.poBtn2 = QRadioButton("Negative", self.frame1)

        self.frame2 = QGroupBox("Cdc Crf")
        self.cBtn1 = QRadioButton("Current", self.frame2)
        self.cBtn1.setChecked(True)  # select by default
        self.cBtn2 = QRadioButton("Optimized", self.frame2)

        self.freq = spinBlock("RF Frequency (kHz)", Freq_Min, Freq_Max, True, Freq_Step, Freq_Decimals)
        self.dataPts = spinBlock("Data Points", DataPts_Min, DataPts_Max)
        self.rolling = spinBlock("Rolling Avg", Rolling_Min, Rolling_Max)
        self.delay = spinBlock("Delay Time (ms)", Delay_Time_Min, Delay_Time_Max)
        self.dcOffset = spinBlock("DC Offset (mV)", OFFSET_MIN, OFFSET_MAX, True, OFFSET_STEP, OFFSET_Decimals)
        self.rfOffset = spinBlock("RF Offset (mV)", OFFSET_MIN, OFFSET_MAX, True, OFFSET_STEP, OFFSET_Decimals)

        self.startMass = spinBlock("Start Mass", MASS_MIN, MASS_MAX)
        self.stopMass = spinBlock("Stop Mass", MASS_MIN, MASS_MAX)
        self.massCenter = spinBlock("Xic Mass Center", MASS_CENTER_MIN, MASS_CENTER_MAX)
        self.massRange = spinBlock("Xic Mass Range", MASS_RANGE_MIN, MASS_RANGE_MAX, True, MASS_RANGE_STEP, MASS_RANGE_Decimals)
        self.cdc = spinBlock("Cdc", Cdc_Min, Cdc_Max, True, Cdc_Step, Cdc_Decimals)
        self.crf = spinBlock("Crf", Crf_Min, Crf_Max, True, Crf_Step, Crf_Decimals)

        self.threshold = spinBlock("Peak Threshold", Threshold_Min, Threshold_Max, True, Threshold_Step, Threshold_Decimals)
        self.width = spinBlock("Peak Width", Width_Min, Width_Max)

        self.run_index1 = QLabel("Index = 0")
        self.run_index1.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        # self.run_index1.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        # self.run_index2 = QLabel("0")

        self.run = QPushButton("Run")
        self.stop = QPushButton("Stop")
        self.zeroBtn = QPushButton("Zero Calibration")
        self.save = QPushButton("Save File")
        self.modify = QPushButton("Modify Optimization Parameter")

        self.run.setEnabled(False)
        self.stop.setEnabled(False)
        self.stop.hide()
        self.zeroBtn.setEnabled(False)
        self.save.setEnabled(False)
        self.modify.setEnabled(False)

        self.linkFunction()
        self.tic_UI()

    def tic_UI(self):
        frameLayout1 = QHBoxLayout()
        frameLayout1.addWidget(self.poBtn1)
        frameLayout1.addWidget(self.poBtn2)
        self.frame1.setLayout(frameLayout1)

        frameLayout2 = QHBoxLayout()
        frameLayout2.addWidget(self.cBtn1)
        frameLayout2.addWidget(self.cBtn2)
        self.frame2.setLayout(frameLayout2)

        layout = QGridLayout()
        layout.addWidget(self.freq,0,0,1,1)
        layout.addWidget(self.dataPts,0,1,1,1)
        layout.addWidget(self.rolling,0,2,1,1)
        layout.addWidget(self.delay,0,3,1,1)
        layout.addWidget(self.dcOffset,0,4,1,1)
        layout.addWidget(self.rfOffset,0,5,1,1)
        layout.addWidget(self.frame1,0,6,1,1)

        layout.addWidget(self.startMass,1,0,1,1)
        layout.addWidget(self.stopMass,1,1,1,1)
        layout.addWidget(self.massCenter,1,2,1,1)
        layout.addWidget(self.massRange,1,3,1,1)
        layout.addWidget(self.cdc,1,4,1,1)
        layout.addWidget(self.crf,1,5,1,1)
        layout.addWidget(self.frame2,1,6,1,1)

        layout.addWidget(self.threshold,2,0,1,1)
        layout.addWidget(self.width,2,1,1,1)
        layout.addWidget(self.run_index1,2,2,1,1)
        # layout.addWidget(self.run_index2,2,1,1,1)
        layout.addWidget(self.run,2,3,1,1)
        layout.addWidget(self.stop,2,3,1,1)
        layout.addWidget(self.zeroBtn,2,4,1,1)
        layout.addWidget(self.save,2,5,1,1)
        layout.addWidget(self.modify,2,6,1,1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)

        self.setLayout(layout)

    def linkFunction(self):
        self.startMass.spin.valueChanged.connect(self.adjStartMass)
        self.stopMass.spin.valueChanged.connect(self.adjStopMass)

    def adjStartMass(self):
        startMass = self.startMass.spin.value()
        #print("start = "+str(self.startMass.spin.value()))
        stopMass = self.stopMass.spin.value()
        self.stopMass.spin.setRange(startMass+MASS_STEP, MASS_MAX)
        #print("1 stop = "+str(self.stopMass.spin.value()))

    def adjStopMass(self):
        stopMass = self.stopMass.spin.value()
        #print("stop = "+str(self.stopMass.spin.value()))
        startMass = self.startMass.spin.value()
        self.startMass.spin.setRange(MASS_MIN, stopMass-MASS_STEP)
        #print("2 start = "+str(self.startMass.spin.value()))


class msTabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(msTabSetting, self).__init__(parent)
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.addTab(self.tab1,"DC Parameter")
        self.addTab(self.tab2,"Quadrupole Mass Filter Scan")
        self.dc = DC_Parameter()
        self.tic = Mass_Filter()
        self.Tab1_UI()
        self.Tab2_UI()

    def Tab1_UI(self):
        tab1_layout = QHBoxLayout()
        tab1_layout.addWidget(self.dc)
        self.tab1.setLayout(tab1_layout)

    def Tab2_UI(self):
        tab2_layout = QHBoxLayout()
        tab2_layout.addWidget(self.tic)
        self.tab2.setLayout(tab2_layout)

class picTabSetting(QTabWidget):
    def __init__(self, parent=None):
        super(picTabSetting, self).__init__(parent)
        self.picTab1 = QWidget()
        self.picTab2 = QWidget()
        self.addTab(self.picTab1, "Preparation")
        self.addTab(self.picTab2, "TIC Data")
        self.plot = outputPlot()
        self.plot2 = output3Plot()

        self.plot2.ax1.set_xlabel("Time (s)")
        self.plot2.ax2.set_xlabel("m/z")
        self.plot2.ax3.set_xlabel("m/z")

        self.picTab1UI()
        self.picTab2UI()

    def picTab1UI(self):
        piclayout = QVBoxLayout()
        piclayout.addWidget(self.plot)
        self.picTab1.setLayout(piclayout)

    def picTab2UI(self):
        piclayout = QVBoxLayout()
        piclayout.addWidget(self.plot2)
        self.picTab2.setLayout(piclayout)


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
